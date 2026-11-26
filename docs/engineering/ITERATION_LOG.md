# Registro de iteraciones e investigaciones

Registro cronológico de hechos y resultados. No reemplaza a los commits ni a los logs originales: los enlaza y conserva la explicación necesaria para no repetir diagnósticos.

## 2026-11-25 — REP-001 — Primeras sondas nativas de reposición

- **Pull request:** [#8](https://github.com/JavierGrecco/Rubrova/pull/8).
- **Run:** [45727626334](https://github.com/JavierGrecco/Rubrova/actions/runs/45727626334).
- **Resultado:** en Linux x86_64 y macOS ARM64 arrancaron PostgreSQL, el servidor lsFusion y Tomcat; el login y la navegación funcionaron.
- **Hecho observado:** las sondas de inventario, compromisos y recepciones devolvieron HTTP 200 y JSON parseable. El inspector rechazó `outgoingCommitments` porque no era una lista. El access log mostró respuestas de 12 bytes para la sonda de compromisos.
- **Interpretación:** el transporte y la autenticación no eran suficientes para demostrar el contrato. La estructura del JSON no contenía la colección esperada.
- **Decisión/cambio:** añadir conteos nativos independientes a las colecciones y comprobar raíz, tipo, filas y conteo. El consumidor sólo interpreta ausencia como lista vacía si el conteo confirma cero.
- **Estado:** regla incorporada al módulo, adaptador, inspector y fixtures; aceptación nativa pendiente.

## 2026-11-25 — REP-002 — Incompatibilidad de sintaxis entre lsFusion 6.2 y 7.x

- **Pull request:** [#8](https://github.com/JavierGrecco/Rubrova/pull/8).
- **Run:** [45730502272](https://github.com/JavierGrecco/Rubrova/actions/runs/45730502272).
- **Commit probado:** `b189e2c7d526d5b9eebcf39590d845016ed8f742`.
- **Hecho observado:** build de lsFusion/MyCompany y publicación de artefactos completaron. En el arranque nativo Linux y macOS, el parser reportó `RubrovaReplenishmentExport:11:12 mismatched input 'JSON' expecting ';'` en `RETURN JSON FROM`, seguido por errores en cascada en las columnas del mismo bloque. El contenedor Docker presentó la misma causa de inicio; no fue un problema exclusivo de arquitectura ARM.
- **Interpretación confirmada por fuente:** el proyecto está fijado a lsFusion 6.2. Su documentación define `RETURN` sin expresión y documenta los resultados de API v6 mediante propiedades de resultado. El patrón de endpoints existentes de Rubrova utiliza `EXPORT JSON FROM`. La forma `RETURN JSON FROM` consultada pertenece a documentación 7.x.
- **Corrección aplicada:** reemplazar `RETURN JSON FROM` por `EXPORT JSON FROM` en los cuatro endpoints y cambiar la prueba estática para impedir que se vuelva a introducir sintaxis 7.x en módulos 6.2.
- **Advertencia metodológica:** la recomendación anterior de reemplazar `EXPORT` por `RETURN JSON FROM` fue incorrecta para la versión fijada. Se conserva aquí para evitar repetirla.
- **Resultado esperado:** el servidor debe poder parsear y cargar el módulo; después se debe validar el cuerpo HTTP y la estructura de las tres colecciones.
- **Estado al actualizar este registro:** corrección subida a la rama del PR; aún no hay un run de aceptación sobre el nuevo SHA.

## 2026-11-25 — REP-003 — Fijación de sintaxis y protección del contrato

- **Cambios:**
  - `extensions/lsfusion/RubrovaReplenishmentExport.lsf`: volver al patrón `EXPORT JSON FROM`.
  - `scripts/platform/validate-mycompany-extension.test.mjs`: exigir ese patrón para las cuatro acciones API y rechazar `RETURN JSON FROM`.
  - Se conservan los conteos independientes y la política de colecciones ausentes.
- **Commits:** `e8e20e8c28e1e1f2479d07604668030603598c1f` y `c99c9941836571a7465066eefda31179dd6a26c5`.
- **Validación:** pendiente de la ejecución de CI sobre el SHA resultante.

## Plantilla de nuevo registro

Copiar el formato de [RECORD_TEMPLATE.md](RECORD_TEMPLATE.md). Registrar también las hipótesis descartadas y las limitaciones que siguen abiertas.

## 2026-11-25 — REP-004 — Regresión del matcher estático y verificación de endpoints

- **Workflow afectado:** [45732148752](https://github.com/JavierGrecco/Rubrova/actions/runs/45732148752).
- **Hecho observado:** el job de validación estática falló antes de compilar; `assert.equal(replenishmentApiActions.length, 4)` recibió cero acciones.
- **Causa raíz:** la expresión regular del test se escribió con escapes duplicados. El archivo fuente tenía cuatro acciones; el matcher no las reconocía por un defecto del test.
- **Corrección:** se fijó el patrón de captura y se comprobó contra el contenido real de `RubrovaReplenishmentExport.lsf`: cuatro acciones detectadas, las cuatro empiezan con `EXPORT JSON FROM` y ninguna con `RETURN JSON FROM`.
- **Commit correctivo:** `073a22915b34baf0816a456d2b815bb355726be8`.
- **Estado:** el matcher quedó corregido y verificado contra los archivos recuperados del branch; todavía falta una ejecución de CI que confirme el test en GitHub Actions.

## 2026-11-26 — REP-005 — Verificación de la regresión, mapa de relaciones y divergencia con main

- **Cambios documentales:** se añadió [DOMAIN_RELATIONSHIPS.md](DOMAIN_RELATIONSHIPS.md), con el recorrido entre módulos, matriz de propiedad, relaciones navegadas de inventario, venta, ledger de despachos y recepciones; también se añadió ADR-0004 para la identidad compuesta de líneas de venta.
- **Hecho observado:** la rama feature define `sourceLineId` como número comercial de orden + índice de línea, mientras que la versión actual de `main` todavía tiene una descripción antigua basada en `Sales.OrderLine.id`. La extracción de esta rama agrupa por el objeto `Sales.OrderLine` y serializa una clave compuesta; el contrato debe conservar esa distinción.
- **Verificación estática local del contenido recuperado:** cuatro acciones API detectadas; todas utilizan `EXPORT JSON FROM`; ninguna utiliza `RETURN JSON FROM`; los tres contadores aparecen en la exportación y en su sonda; adaptador e inspector validan conteo y longitud; fixture JSON válido; están presentes las tres pruebas nuevas de colecciones vacías/conteos.
- **Límite de esa verificación:** es una comprobación del contenido del branch; no sustituye Node, Python, el parser de lsFusion ni el runtime real de CI.
- **Estado de CI:** el último workflow de plataforma visible sigue siendo [45732148752](https://github.com/JavierGrecco/Rubrova/actions/runs/45732148752), que falló por un matcher estático defectuoso antes de compilar. El matcher se simplificó luego a verificaciones inequívocas, pero todavía no hay una ejecución registrada sobre el SHA actual.
- **Divergencia de ramas:** el PR #8 continúa apuntando al SHA base anterior `bab975fd...`; `main` avanzó 21 commits documentales y GitHub informa `mergeable_state=dirty`. Antes de fusionar hay que incorporar los cambios de `main` y reconciliar, como mínimo, README, Calidad y pruebas, soporte macOS, instalación MyCompany y el documento de stock proyectado; no se debe resolver sobrescribiendo documentación sin revisión.
- **Criterio de cierre:** validar el test estático en CI; compilar y cargar lógica en Linux/macOS; verificar la respuesta autenticada y las colecciones; después sincronizar con `main` y volver a ejecutar los gates del SHA final.


## 2026-11-25 — REP-006 — Prevalidación compartida y reducción del ciclo CI

- **Hechos de duración:** en [45637101959](https://github.com/JavierGrecco/Rubrova/actions/runs/45637101959) el workflow tardó 31m32s: el build del fork duró 401s, el diagnóstico Docker/Linux 1.005s y el smoke nativo macOS 417s. En [45723325906](https://github.com/JavierGrecco/Rubrova/actions/runs/45723325906), el build duró 363s, Docker/Linux 226s y el smoke macOS 294s.
- **Diagnóstico:** Docker/Linux era un job no bloqueante y no era el entorno local prioritario; su coste puede superar el de todos los tests rápidos juntos. No aporta evidencia superior a la ruta nativa cuando la aceptación prioritaria es macOS ARM64.
- **Cambio:** se añadió `scripts/platform/local-preflight.sh` con modos `--platform`, `--replenishment` y `--all`. Los workflows llaman a las mismas rutinas para evitar que la validación local difiera de CI.
- **Cambio CI:** el build completo y el smoke nativo macOS ARM64 permanecen automáticos. Los jobs Linux nativo y Docker/Linux quedan bajo ejecución manual. Se añade concurrencia a nivel workflow para cancelar una corrida antigua al llegar un commit nuevo al mismo PR.
- **Integración de ramas:** se creó `integration/replenishment-mainline-preflight` desde `main` (base `699eb8343706acd9631ca83150eb54ba8fba71e3`) para reconstruir un PR corto y evitar arrastrar los 118 commits divergentes del PR #8.
- **Límite de validación:** esta entrada registra la decisión y la implementación del preflight/workflows; hasta que el nuevo PR ejecute Actions, no se marca la nueva capa como aprobada. El script rápido tampoco carga lsFusion ni consulta una base MyCompany.
- **Próximo criterio de cierre:** nueva ejecución de CI para el commit integrado; build + smoke macOS ARM64 + respuesta JSON válida de las cuatro acciones y conteos conciliados; después probar el runtime en el MacBook local.


## 2026-11-26 — REP-007 — Primera ejecución del preflight unificado

- **PR:** [#10](https://github.com/JavierGrecco/Rubrova/pull/10).
- **Run:** [45735337191](https://github.com/JavierGrecco/Rubrova/actions/runs/45735337191), SHA `5ac3c75f`.
- **Hecho observado:** el workflow ejecutó el nuevo preflight. En la suite Node pasaron 28 de 29 pruebas; falló una aserción de concurrencia en `validate-mycompany-extension.test.mjs`, que esperaba cuatro apariciones globales de `cancel-in-progress: true`.
- **Causa:** el nuevo `concurrency` a nivel workflow añadió una quinta regla global, mientras que los cuatro controles por job siguen siendo correctos. La aserción existente contaba ambos niveles como si fueran una sola política.
- **Corrección:** distinguir en el test la regla global por PR de las cuatro reglas por job; añadir una regresión que verifica que Linux/Docker son manuales y que el smoke macOS ARM64 permanece automático; comprobar que ambos workflows invocan el mismo preflight local.
- **Alcance del fallo:** no llegó a la compilación Maven ni al smoke de runtime porque el job `validate` es una dependencia previa. Windows pasó y el workflow del planificador terminó en verde.
- **Estado:** corrección subida al branch; la segunda ejecución sobre el nuevo SHA debe confirmar el arreglo.


## 2026-11-26 — REP-008 — Preflight unificado aprobado en la nueva rama principal

- **PR:** [#10](https://github.com/JavierGrecco/Rubrova/pull/10), SHA probado `9b9083c35570675a1bb7055fd86d235bf9ab4fde`.
- **Preflight de plataforma:** [run 45735930978](https://github.com/JavierGrecco/Rubrova/actions/runs/45735930978), job `Prevalidación local compartida`: aprobado.
- **Resultados:** 30/30 tests Node de la extensión; 34/34 tests Node de evaluación; 10 tests de configuración Python, 5 de URL/runtime nativo y 18 de supervisor nativo; pruebas de listener y despliegue aprobadas. La validación sintáctica de Windows también pasó.
- **Preflight de reposición:** [run 45735930945](https://github.com/JavierGrecco/Rubrova/actions/runs/45735930945): aprobado, usando `local-preflight.sh --replenishment`.
- **Corrección de iteración:** las ejecuciones iniciales del PR #10 descubrieron (a) una aserción que mezclaba concurrencia global y por job, y (b) que el workflow de reposición conservaba sus pasos anteriores. Ambos casos se corrigieron y se añadieron pruebas estáticas para que no vuelva a producirse la divergencia.
- **Concurrencia:** al llegar el SHA corregido, la corrida anterior fue cancelada; no se debe tomar como fallo funcional de código.
- **Estado:** primera capa de validación rápida aprobada en GitHub. La compilación completa del fork continúa; el smoke macOS ARM64 y la API nativa siguen pendientes.

## 2026-11-26 — REP-011 — Conflicto de concurrencia al persistir el idioma del usuario

- **PR:** #10.
- **Evidencia:** [run 45741635022](https://github.com/JavierGrecco/Rubrova/actions/runs/45741635022), log PostgreSQL y `server-console.log`.
- **Síntoma:** dos transacciones del usuario admin (`CustomUser.key0=786`) intentaron actualizar `Authentication_clientLanguage_CustomUser` con `en` al mismo tiempo. PostgreSQL devolvió `could not serialize access due to concurrent update`; el log de lsFusion registró `SQLConflictException: UPDATE_CONFLICT` para el mismo `UPDATE Authentication_customUser`.
- **Alcance:** el servidor terminó su inicio y la UI alcanzó `UI_LOGIN_STATUS=authenticated:admin`; por tanto, el conflicto no fue la causa inmediata del fallo de esa corrida, que se detuvo por una reserva de salida igual a cero. Se registra como fallo concurrente independiente.
- **Causa localizada:** `RemoteConnection.initConnectionContext()` crea una sesión por conexión RMI y `saveUserContext()` escribe los cinco datos de locale/formato en la fila compartida de `CustomUser`. El cliente web puede inicializar varias conexiones para el mismo usuario en paralelo.
- **Corrección:** bloqueo por stripe derivado del login, adquirido antes de `getExecSession()`. La creación de conexiones del mismo usuario queda serializada; los demás usuarios conservan concurrencia.
- **Regresión:** el preflight comprueba estáticamente el orden bloqueo→sesión; el smoke nativo busca el conflicto específico en los logs y debe imprimir `RUBROVA_AUTH_USER_CONTEXT_SERIALIZATION=passed`.
- **Estado:** fix subido; compilación y smoke nativo de un SHA nuevo pendientes.