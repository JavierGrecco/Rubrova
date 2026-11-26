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

## 2026-11-26 — REP-012 — Error de parseo lsFusion en fixture de reposición

- **PR:** [#10](https://github.com/JavierGrecco/Rubrova/pull/10), rama de integración existente.
- **Evidencia:** [run 45744747100](https://github.com/JavierGrecco/Rubrova/actions/runs/45744747100), job macOS ARM64.
- **Síntoma:** el proveedor simulado y PostgreSQL iniciaron, pero el supervisor terminó durante el arranque del servidor. `stderr.log` señaló `RubrovaCIReplenishmentFixture:71:61 — WHERE clause is forbidden with GroupingType`.
- **Causa raíz:** `rubrovaCIOutgoingOrder() = GROUP MAX Sales.Order o WHERE ...` usa una cláusula no admitida por ese tipo de agrupación en lsFusion 6.2.
- **Corrección:** se reemplazó `WHERE` por `IF`, siguiendo la sintaxis de agrupación ya usada por `RubrovaCISalesFixture.lsf` y otros módulos del repositorio.
- **Regresión:** se añadió al preflight una aserción positiva para `GROUP MAX ... IF` y otra negativa para `GROUP MAX ... WHERE`.
- **Alcance:** esta corrección resuelve el error de parseo identificado; no se declara validada hasta que el servidor arranque y el smoke macOS pase las sondas y la exportación.


## 2026-11-26 — REP-013 — Consolidación main y aceptación nativa integrada

- **Commit canónico:** [`f545c907`](https://github.com/JavierGrecco/Rubrova/commit/f545c907b12a9eed4cf5e532edd3434babb64139).
- **Estado del repositorio:** una única rama visible (`main`) y cero pull requests abiertos. La exportación nativa de reposición y el runtime quedaron integrados; no continuar desarrollando ramas paralelas para el mismo alcance.
- **Validación:** [run 45847755524](https://github.com/JavierGrecco/Rubrova/actions/runs/45847755524), concluido con `success`; [planificador run 45847755643](https://github.com/JavierGrecco/Rubrova/actions/runs/45847755643), concluido con `success`.
- **Hechos observados en macOS ARM64:** login autenticado; sondas de inventario, compromisos y recepciones HTTP 200; exportación con conteos y filas verificables; venta sintética ARS 1.250; pago exacto en efectivo; stock 10 → 9; turno `CLOSED`; persistencia después del reinicio; Demo aislada aprobada.
- **Límites:** egress externo habilitado (`RUBROVA_NATIVE_OFFLINE_ACCEPTANCE=not_tested`); Linux nativo y Docker/Linux `skipped`; los datos son sintéticos y todavía no hay aceptación en el Mac físico ni jornada productiva.

## 2026-11-26 — REP-014 — Primer respaldo lógico PostgreSQL nativo

- **Motivo:** el supervisor ya conservaba la base entre reinicios, pero aún no existía un paquete comprobable ni una restauración protegida.
- **Implementación:** `scripts/platform/native-postgres-backup.py` crea un paquete de base PostgreSQL en formato custom, con manifiesto y SHA-256; verifica el paquete y restaura sólo a una base nueva, nunca sobre `rubrova_dev`.
- **Seguridad:** comprueba que el servidor sea PostgreSQL 18 y que el directorio de datos y puerto correspondan al clúster privado de Rubrova; sólo conecta a loopback; no exporta secretos; ante un fallo intenta retirar únicamente la base nueva incompleta.
- **Pruebas añadidas:** corrupción de dump/manifiesto, entradas extra, directorio de datos ajeno, confirmación explícita, base ya existente y limpieza de una restauración fallida.
- **Aceptación:** preflight y smoke nativo macOS ARM64 aprobados en [run 45855055565](https://github.com/JavierGrecco/Rubrova/actions/runs/45855055565). El log confirma creación, SHA-256, verificación y restauración a `rubrova_restore_ci`; se emitió `RUBROVA_NATIVE_POSTGRES_BACKUP_RESTORE=passed`.
- **Límite:** protege PostgreSQL, no adjuntos, documentos, configuración del SO ni credenciales. La aceptación local en Mac físico/Windows y el paquete completo siguen pendientes.


## 2026-11-26 — REP-015 — Aceptación nativa integrada y restauración PostgreSQL

- **Commit probado:** `ac758d01e8fb1ef2bfdd65900a23281c9aab3c3a`.
- **Workflow:** [45855055565](https://github.com/JavierGrecco/Rubrova/actions/runs/45855055565), terminado con `success`.
- **Build:** preflight compartido, validación sintáctica Windows y compilación completa del servidor, cliente GWT y lógica MyCompany aprobados.
- **Smoke macOS ARM64:** login, API autenticada de reposición sobre fixtures, venta ARS 1.250, efectivo exacto, factura/pago, stock 10 → 9, cierre de turno, reinicio/persistencia y Demo aislada aprobados.
- **Backup/restore:** paquete PostgreSQL creado y verificado por SHA-256 y `pg_restore --list`; restauración a `rubrova_restore_ci`; la base original `rubrova_dev` no se sobrescribió.
- **Límites:** egress estuvo habilitado (`offline acceptance not tested`); Linux/Docker fueron `skipped`; Windows sólo comprobó sintaxis; aún no hay prueba en Mac físico, base comercial real, periféricos ni jornada real.
- **Siguiente iteración:** proteger devolución parcial/total y reintegro contra sobredevolución; luego movimientos y arqueo físico, utilizando los ledgers originales de MyCompany sin duplicarlos.


## 2026-11-26 — REP-016 — Investigación de contratos lsFusion/MyCompany y parser de booleanos

- **Repositorio:** https://github.com/JavierGrecco/Rubrova
- **Documentación consolidada:** commit ef008fe0f3bf6bad5bf27aa1440c8acb760cf0fb; guía docs/engineering/LSFUSION_MYCOMPANY_INTEGRATION_GUIDE.md, índice de ingeniería y contrato general.
- **Fuentes fijadas:** lsFusion 6.2 commit dd4dbe5bf9b136e73e18fe25d741253929324350; MyCompany 6.2 commit d21ca6978717b98b6300d90267f9767db7414008.
- **Alcance investigado:** modelo de módulos y dependencias; REQUIRE/NAMESPACE; propiedades declarativas y DATA; acciones; hooks abstractos; constraints; formularios; eventos; APPLY/CANCEL/NEWSESSION/NESTEDSESSION; Action API y EXTERNAL; POS, facturas, notas de crédito, cobros/reintegros, sesiones, caja, despachos, recepciones, ledger físico y reservas.
- **Hechos observados:** runtime LSF integrado, no conjunto de microservicios; el POS conecta Session/Invoice/IncomingPayment/Shipment/InvLedger y la devolución conecta Bill/BillLine/OutgoingPayment/Receipt/InvLedger. onHand y available son magnitudes distintas. La fórmula active(...) varía según el documento. Los agregados vacíos pueden retornar NULL y no deben compararse como cero sin normalización explícita.
- **Riesgo de negocio descubierto:** el formulario nativo de reintegro limita cada nota frente a lo cobrado originalmente por medio de pago, pero no resta los reintegros de devoluciones anteriores; la validación acumulativa es una brecha a proteger en Rubrova.
- **Hecho observado de CI:** run 45870077864, SHA 698cba2db3567f07478dede2950b07b6e4a265f5: preflight, validación Windows y compilación pasaron; el arranque macOS ARM64 falló al inicializar la lógica con RubrovaCISalesFixture:206:83 use NULL instead of FALSE. El parser llegó a procesar 719 de 722 módulos; no fue un fallo de PostgreSQL ni de compilación.
- **Corrección aplicada:** commit 26a60fd1f88fd2b355b8a72baafbd9688ed5ff53 de la rama del PR #13 cambia los dos campos de diagnóstico a enteros 1/0 y actualiza las aserciones estáticas. Evita usar FALSE, que no es el literal de falso aceptado por el lenguaje/versión.
- **Validación posterior:** run 45872444450, SHA 26a60fd1f88fd2b355b8a72baafbd9688ed5ff53: prevalidación y Windows aprobados; compilación Maven completa en curso al registrar esta iteración; smoke nativo aún no ha comenzado. No se declara corregido hasta que el parser cargue los módulos y el escenario E2E pase.
- **Pendientes de investigación:** Compras/abastecimiento; pedidos mayoristas y canales; fiscalidad ARCA; lotes/costos/producción; CRM/cuenta corriente; autorizaciones/auditoría; instalación local Mac físico y Windows; periféricos, desconexión de red y backup completo.


## 2026-11-26 — REP-017 — Flujos de compras, ventas mayoristas y analítica comercial

- **Base:** MyCompany 6.2 vendorizado en Rubrova, revisión fijada en platform/mycompany-6.2.lock.json.
- **Documentación:** se amplió docs/engineering/LSFUSION_MYCOMPANY_INTEGRATION_GUIDE.md (secciones 6.7–6.11) en commit 5484d1beece3bcc5ec6c40b9c569b1890e1dbf9c.
- **Compras:** Purchase.Order confirmado puede generar Receipt ready con ReceiptLine/initialDemand. ReceiptResLedger representa la entrada esperada como reserva firmada; increaseAvailableStock condiciona su efecto en available. ReceiptInvLedger sólo incorpora la cantidad efectivamente completada al inventario físico. PurchaseOrderReceipt limita recibido a la cantidad pedida.
- **Facturación proveedor:** PurchaseOrderBill soporta cantidad pedida no facturada; PurchaseOrderBillReceipt añade facturación por cantidad recibida y evita reutilizar ReceiptLine ya vinculadas. BillDebt y OutgoingPaymentDebt conectan obligaciones y pagos; BillPayment.registerPayment crea OutgoingPayment.
- **Ventas mayoristas:** SalesOrderShipment crea/reutiliza Shipment waiting para el remanente, ejecuta precheckAvailability y registra reservas antes de la salida física. Los despachos parciales se concilian por Sales.OrderLine; una constraint evita sobre-despacho. ShipmentInvLedger registra la salida física final.
- **Facturación de venta:** SalesOrderInvoice permite la política ordered; SalesOrderInvoiceShipment añade delivered y factura sólo ShipmentLine completadas, activas y aún no facturadas, preservando los enlaces de línea.
- **Relación venta-compra:** SalesOrderPurchase enlaza líneas de Sales.OrderLine con Purchase.OrderLine para trazabilidad. No se interpreta como compra automática ni como reserva física sin evidencia adicional.
- **Analítica:** SalesLedger agrega hechos por producto, cliente, ubicación y tiempo, con cantidad, importe, costo y margen; SalesLedgerInvoice aporta ventas positivas y SalesLedgerBill aporta notas de crédito negativas. La política exacta de costo/retroactividad requiere una investigación específica antes de usar el margen en decisiones productivas.
- **Reglas incorporadas:** pedido, recepción/despacho, factura y pago son etapas distintas; las cantidades y los importes deben conciliarse por separado; los ledgers nativos siguen siendo la fuente de verdad.
- **Límites pendientes:** políticas de valoración de stock, lotes y costos ajustados; impuestos/ARCA; compras automáticas, MOQ/múltiplos y proveedor preferente; stock de seguridad, plazo de entrega y abastecimiento multi-sucursal; seguridad/roles y escenarios con datos reales.


## 2026-11-26 — REP-018 — Del modelo de terminales al estado real de integración

- **Fuentes inspeccionadas:** extensions/lsfusion/RubrovaPaymentTerminals.lsf, extensions/lsfusion/RubrovaIntegrationResilience.lsf, scripts/platform/fixtures/RubrovaCIIntegrationFixture.lsf, docs/MYCOMPANY_RUNTIME_INSTALL.md.
- **Hecho observado:** PaymentTerminals define persistencia y formularios para cuenta de proveedor, terminal, asignación POS/medio, intención, intento, evento, reintegro y liquidación. Contiene claves de idempotencia y una bandera de firma verificada, y deliberadamente no guarda el cuerpo HTTP entero.
- **Límite probado por inspección:** no hay acciones de cobro real ni EXTERNAL HTTP POST en el código LSF del módulo; no hay receptor de webhook ni bridge local implementado. El propio documento de instalación califica el módulo como configuración/trazabilidad y dice que aún no ejecuta cobros reales.
- **Resiliencia actual:** rubrovaHttpGet clasifica respuestas 429, 408/425, 5xx, 401, 403, 409 y fallo de conexión/timeout, establece timeout entre 1 y 30.000 ms y persiste una incidencia separada. No realiza reintentos automáticos ni implementa métodos HTTP de escritura.
- **Decisión:** la integración electrónica queda clasificada como modelo preparado, no operativa. Los intentos e intenciones no son el movimiento contable. El cobro confirmado debe registrarse como IncomingPayment; el reintegro confirmado debe conciliarse con Bill y OutgoingPayment; las liquidaciones separan bruto, comisión, retenciones y neto.
- **Pruebas requeridas:** doble envío, timeout con resultado remoto desconocido, consulta de estado, webhook duplicado/tardío/firma inválida, reinicio, reintegro y conciliación con liquidación; pruebas con bridge y hardware real.
