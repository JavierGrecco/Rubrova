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
