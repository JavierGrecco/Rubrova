# Estado real del proyecto Rubrova

**Corte:** 26 de noviembre de 2026  
**Rama canónica:** `main`  
**Candidato de integración:** [PR #10](https://github.com/JavierGrecco/Rubrova/pull/10), rama `integration/replenishment-mainline-preflight`, basada directamente en `main` (`699eb834`), sin commits por detrás. El [PR #8](https://github.com/JavierGrecco/Rubrova/pull/8) fue cerrado sin fusionar y reemplazado para no arrastrar 118 commits divergentes.

## Estado de la última validación

- **Prevalidación de plataforma compartida:** aprobada en el PR #10, SHA `9b9083c35570675a1bb7055fd86d235bf9ab4fde`, run [45735930978](https://github.com/JavierGrecco/Rubrova/actions/runs/45735930978). Pasaron 30/30 pruebas Node, 34/34 validaciones de evaluación, 10 + 5 + 18 pruebas Python, chequeos de shell, listener y despliegue.
- **Windows:** validación sintáctica aprobada en el mismo run.
- **Prevalidación de reposición:** aprobada en [45735930945](https://github.com/JavierGrecco/Rubrova/actions/runs/45735930945), invocando el mismo `local-preflight.sh --replenishment` usado localmente.
- **Compilación completa:** en ejecución en el job `build-fork` del run [45735930978](https://github.com/JavierGrecco/Rubrova/actions/runs/45735930978). Todavía no se declara aprobada.
- **Runtime nativo macOS ARM64:** pendiente de la compilación. La última ejecución completada de una revisión anterior inició PostgreSQL, servidor, RMI y Tomcat; el navegador autenticó correctamente, pero la acción `/exec/Rubrova.rubrovaExportReplenishmentSource` falló con HTTP 500 `Set operation is incorrect`. El nuevo smoke incorpora sondas independientes para inventario, compromisos y recepciones, antes de probar la exportación consolidada.
- **Linux nativo y Docker/Linux:** ahora se reservan para ejecución manual (`workflow_dispatch`), para conservar sus diagnósticos sin sumar sus tiempos a cada PR. El smoke nativo macOS ARM64 sigue siendo obligatorio.
- **Datos reales:** no se ha conciliado todavía una exportación tomada de una base MyCompany local. Las fixtures son sintéticas.
- **PR y ramas:** PR #10 deriva de `main` y está en borrador. PR #8 se cerró sin fusionar; no debe reabrirse ni mezclarse con la rama nueva.


## Resumen de madurez

La última aceptación funcional completa del POS base sigue siendo el [CI 45637101959](https://github.com/JavierGrecco/Rubrova/actions/runs/45637101959), sobre una revisión anterior. Validó con datos sintéticos login, apertura de turno, venta en efectivo, factura/pago, stock y cierre básico en runners de CI. No constituye una jornada real, una instalación productiva ni una aceptación del nuevo puente de reposición.

El repositorio contiene los árboles completos y fijados de lsFusion 6.2 y MyCompany 6.2 en `vendor/`. Su reactor compila el servidor, el cliente GWT y la lógica MyCompany desde las fuentes propias. El camino de desarrollo local prioriza Java 21, PostgreSQL 18 y Tomcat 9 sin Docker, con una vista previa supervisada y datos aislados.

El candidato de integración incorpora el módulo autenticado de exportación nativa y su puente Python. Las pruebas rápidas cubren conversión y conciliación con fixtures, pero sólo el servidor real puede demostrar que las consultas lsFusion 6.2 son finitas y correctas. La exportación consolidada ya falló con `Set operation is incorrect`; hasta que el smoke macOS ARM64 pruebe los cuatro endpoints y las cifras concilien con una base real, la integración no se considera aceptada.

## Resumen ejecutivo

Rubrova está en **Fase 0: piloto integrado POS + ERP**. El núcleo MyCompany/lsFusion está compilado desde las fuentes fijadas y el primer circuito POS básico fue probado en CI con una base sintética. El foco inmediato es cerrar la exportación nativa de reposición y demostrar que el runtime puede utilizarse localmente en el MacBook Air del usuario.

La exportación nueva es de solo lectura. Separa existencia física, disponible nativo, reservas, compromisos por línea de venta y recepciones previstas. El adaptador Python valida las conciliaciones, exige políticas explícitas por producto/ubicación y rechaza escenarios que el planificador todavía no modela. No ejecuta `fillAuto`, ni crea, modifica o confirma órdenes de compra.

El último fallo de runtime identificado no es de compilación ni de arranque: el servidor y el cliente cargan y el login funciona; la acción consolidada devuelve HTTP 500 por una operación de conjuntos incorrecta. Se retiraron conversiones de tipo sobre los índices de línea y se reforzó la comprobación estática; la corrección necesita una nueva ejecución del smoke nativo.

La capa de pagos presenciales tiene arquitectura y entidades iniciales de configuración/trazabilidad, pero no existe todavía un conector homologado ni cobros reales. Tryton 8.0 + tryton-ar 8.0 se conserva como referencia fiscal argentina, no como segundo núcleo operativo.

## Qué está probado

| Capacidad | Estado | Evidencia y alcance |
|---|---|---|
| Fuentes originales lsFusion 6.2 + MyCompany 6.2 | Aprobado | Snapshots fijados en el lock y completos en `vendor/` |
| Compilación del fork Rubrova | Aprobado en CI | Reactor Maven, servidor, cliente GWT y lógica MyCompany compilados desde fuentes propias |
| Imágenes propias del runtime Docker | Construcción y smoke aprobados en CI | Artefactos compilados desde fuentes Rubrova; el diagnóstico Docker/Linux completó el ciclo funcional en `45637101959` |
| Arranque, RMI y cliente web | Aprobado en macOS ARM64 y Linux nativo CI; Docker histórico aprobado | En `45641728845`, macOS y Linux nativo iniciaron PostgreSQL, servidor, RMI, Tomcat y cliente web. Docker/Linux sigue como diagnóstico suplementario no bloqueante |
| Login y navegación al POS | Aprobado en macOS ARM64 y Linux nativo CI; Docker histórico aprobado | Chromium abrió Comercio → Punto de venta y ejecutó el recorrido de venta tanto en macOS ARM64 como en Linux x86_64 sin Docker |
| API nativa autenticada de reposición | En validación | El servidor y el login cargaron en macOS ARM64 y Linux; la acción devolvió HTTP 500 `Set operation is incorrect`. Se eliminaron las conversiones de índices y el nuevo smoke está en curso. No se declara aceptada hasta verificar el JSON y conciliarlo con datos reales |
| Apertura de turno | Aprobado en Docker y macOS ARM64 CI | Turno sintético `SM/000001` en Docker y turno de prueba de Rubrova en macOS nativo |
| Búsqueda y selección de artículo | Aprobado en Docker y macOS ARM64 CI | Un producto sintético; línea de recibo, cantidad 1 y precio ARS 1.250 |
| Confirmación del cobro en efectivo | Aprobado en Docker y macOS ARM64 CI | Se confirma el diálogo nativo de MyCompany mediante `PROPERTY(overFormOk)` |
| Factura y pago | Aprobado en Docker y macOS ARM64 CI | Una factura, una factura pagada y un pago entrante; importe aplicado ARS 1.250 |
| Caja y turno | Aprobado en Docker y macOS ARM64 CI | Efectivo pagado y conciliado; cierre básico de turno y caja |
| Movimiento de stock | Aprobado en Docker y macOS ARM64 CI | Ledger de inventario conciliado; en el fixture Docker, entrada 10, salida 1, existencia 9 |
| Resiliencia HTTP GET | Aprobado en escenarios CI | Timeout, clasificación de 408/429/503 y errores definitivos, persistencia de incidencias y recuperación del proveedor simulado |
| `HEADERSTO` / `Retry-After` | Aprobado en escenario CI | El 429 devuelve y persiste `Retry-After: 2` con el mecanismo nativo de lsFusion |
| Configuración y trazabilidad de terminales | Base inicial incorporada; validación CI pendiente | Cuentas de proveedor, equipos, asignación a caja/medio, intenciones, intentos, eventos, reintegros y líneas de liquidación con claves idempotentes únicas. No procesa tarjetas ni ejecuta cobros reales |
| Adaptadores físicos y cloud-to-cloud | Pendiente | Falta seleccionar un proveedor/modelo, conseguir SDK/API y credenciales de sandbox y homologar la operación con terminal real |
| Timeout de `EXTERNAL HTTP CLIENT` desde navegador | Pendiente | Falta una prueba real en Chromium con endpoint lento/CORS, abort, error de red y recuperación |
| Cierre básico después de venta en efectivo exacto | Aprobado en CI | Turno `SM/000001` quedó `CLOSED`; venta/neta y saldo de caja ARS 1.250 conciliados. Faltan arqueo contado, diferencias, ingresos y retiros |
| Devolución y reintegro | Pendiente | Falta comprobar Bill, OutgoingPayment, medio original y movimiento inverso de stock |
| Vuelto, pagos mixtos y tarjeta | Pendiente | El primer circuito aceptado sólo cubre efectivo exacto, sin vuelto |
| Reinicio conservando datos | Aprobado en CI | En `45503956218` se reiniciaron servidor y cliente sin borrar PostgreSQL y se volvieron a conciliar factura, pago, caja, stock y turno cerrado |
| Traducción completa | En curso / parcial | Se corrigieron captions de POS y caja y se añadió el bundle de acceso español; la revisión integrada debe superar el smoke visual antes de aceptarse |
| Runtime durante una caída de Internet | Parcial | Linux x86_64 nativo completó en CI `45637101959` el ciclo POS con salida externa bloqueada, incluyendo pago, stock, cierre y recuperación de integraciones. macOS ARM64 pasó el recorrido con conectividad habilitada; falta repetir el navegador Mac con egress bloqueado y completar una instalación offline limpia |
| Instalación inicial y paquete completo sin Internet | Pendiente | La prueba de runtime aislado no demuestra todavía que el instalador, los artefactos, las imágenes base y las dependencias puedan instalarse en una PC limpia sin conexión |
| Ejecución local nativa sin Docker | Aceptación comercial básica en macOS ARM64 y Linux x86_64 CI; prueba en equipo real pendiente | Supervisor Python, instancia PostgreSQL propia, servidor `BusinessLogicsBootstrap` y cliente Tomcat. El recorrido de venta, pago, stock, cierre y fallos de integración pasó en ambos runners nativos; falta repetir en tu Mac y ampliar la cobertura |
| Configuración siempre disponible | En desarrollo inicial | Existe el esquema y el gestor CLI para `native-local`, `docker-local` y `remote-online`; falta el panel visual independiente y su integración con la administración del POS |
| Backup, restauración y rollback | Pendiente | No se acepta producción sin restauración real sobre una copia |
| Windows y macOS ARM64 | Parcial | macOS ARM64: venta y cierre básicos aprobados en runner `macos-26`; prueba en Mac físico y periféricos pendientes. Windows: sólo validación sintáctica hasta ahora; falta runtime y aceptación funcional |
| ARCA, terminales/adquirentes, marketplaces y logística | Pendiente | La arquitectura y la base de configuración de terminales están documentadas; no hay adaptador bancario productivo ni homologación física. Ningún conector comercial se habilita hasta superar idempotencia, Outbox, circuit breaker, fallos simulados y conciliación |

## Terminales de pago

La responsabilidad del cobro bancario permanece en la terminal y en el proveedor (PSP/adquirente). Rubrova contempla tres modalidades: terminal autónoma con registro manual, integración local por SDK/puente e integración cloud-to-cloud. Se incorporó una base de configuración y trazabilidad, pero no un adaptador real ni una autorización de cobro. La liquidación bancaria se concilia por separado del pago confirmado. Véase [Arquitectura de terminales de pago y conciliación](PAYMENT_TERMINAL_INTEGRATION_ARCHITECTURE.md).

## Modos de ejecución y control local

El contrato está en `platform/runtime-config.schema.json`; `scripts/platform/runtime-config.py` permite crear, validar y gestionar los destinos `native-local`, `docker-local` y `remote-online`. El prototipo nativo inicia y supervisa PostgreSQL, lsFusion y Tomcat, pero aún no cambia de destino ni migra datos de negocio. El panel visual independiente sigue pendiente. Ver [Modos de ejecución y control local](RUNTIME_MODES_AND_LOCAL_CONTROL.md).

## Código y propiedad de fuentes

- `vendor/platform/`: snapshot del motor lsFusion 6.2 (servidor, API, cliente web/desktop y build).
- `vendor/mycompany/`: snapshot completo de MyCompany 6.2 (POS y ERP).
- `extensions/lsfusion/`: módulos y localización propios de Rubrova.
- `patches/lsfusion/`: modificaciones directas al motor, sólo cuando una extensión no alcanza.
- `build/rubrova/pom.xml`: reactor Maven que compone las fuentes del motor y de MyCompany.

Los commits de origen y licencias están fijados en `platform/source-lock.json` y en los avisos de los árboles vendorizados. MyCompany usa Apache-2.0 y lsFusion LGPL-3.0. Los módulos de pago, factura y despacho usados en el primer circuito se conservaron del snapshot original; la prueba prepara datos sintéticos y mide los resultados, no reimplementa esos procesos.

## Arquitectura objetivo para una PC local

El runtime productivo será local: servidor propio, aplicación MyCompany adaptada, cliente web servido desde el mismo equipo y PostgreSQL persistente. El primer runtime construido desde fuentes Rubrova ya se ejecutó con éxito en CI. Aún falta empaquetar todas las dependencias y demostrar una instalación limpia sin Internet.

El núcleo POS/ERP debe continuar operando sin conexión externa. ARCA, adquirentes/QR, marketplaces, mensajería y transportistas son integraciones remotas: cuando no estén disponibles, deben quedar pendientes o informar indisponibilidad sin bloquear catálogo, caja local, ventas permitidas, compras, stock ni informes.

## Protección de producción

No se actualizará automáticamente ningún componente. Cada versión candidata debe superar comparación con su origen, reaplicación de cambios Rubrova, compilación, regresión funcional, migración probada sobre una copia de base, backup/restore y prueba offline. Se mantendrá el último paquete estable y una ruta de recuperación. Nunca probaremos una migración sobre la única base productiva.

## Próximo orden de implementación

1. **Completar la aceptación de la demostración aislada:** el launcher crea una base, configuración y puertos separados; verificar con Chromium el turno y el artículo de muestra en el segundo arranque nativo.
2. **Verificar el runtime nativo en el Mac de usuario:** repetir el recorrido que ya pasó en CI con PostgreSQL 18 y Java 21 ARM64, revisar persistencia, logs y estabilidad.
3. **Completar la cobertura del POS:** arqueo contado, diferencias, ingresos/retiros, vuelto, pagos mixtos, tarjeta, devoluciones y cancelaciones.
4. **Cerrar la verificación offline en macOS:** repetir el smoke del POS con egress bloqueado en un runner Apple Silicon y después en el Mac de usuario. Linux nativo ya completó este recorrido sin Docker en `45637101959`.
5. **Persistencia y recuperación:** reiniciar servidor y cliente sin borrar PostgreSQL; probar backup/restore y rollback sobre copias.
6. **Instalación offline y Windows:** paquete completo en PC limpia sin Internet; validar instalación, procesos, permisos y rutas en Windows x64.
7. **ERP y localización:** continuar compras, inventario, proveedores, reportes y experiencia visual sobre módulos originales, adaptando con extensiones propias.
8. **Fiscalidad e integraciones externas:** ARCA, medios electrónicos, marketplaces y logística sólo después de tener idempotencia, Outbox, circuit breaker, auditoría y conciliación probadas.

La evidencia `45503956218` demuestra el recorrido comercial básico en Docker histórico; `45637101959` demuestra ese recorrido en Docker/Linux, macOS ARM64 y Linux nativo. Linux nativo también lo completó con la salida externa bloqueada. Ninguna ejecución declara terminado el producto ni autoriza producción.

## Política transversal de errores

Se mantiene la política de [Resiliencia de integraciones y tratamiento de errores](INTEGRATION_RESILIENCE_AND_ERROR_HANDLING.md). El motor lsFusion ofrece `timeoutHttp()`, `HEADERSTO` y `TRY/CATCH`, pero esos mecanismos no sustituyen una política completa. El helper GET y el registro de incidencias se probaron contra un proveedor simulado; faltan Outbox, circuit breaker y ampliar los escenarios de escritura más allá de GET. Los conectores de producción permanecen deshabilitados hasta superar esas puertas.

Los logs SQL de arranque se interpretan en el diagnóstico técnico actualizado: las dos consultas iniciales de `dumb` pertenecen a la detección de base vacía; el conflicto serializable de `Time.currentDate` se recuperó y el valor quedó persistido. Los timeouts de consultas siguen observándose y deben medirse para mejorar el arranque, sin aumentar límites indiscriminadamente.

La prueba de venta usa `RubrovaCISalesFixture` sólo en CI: prepara ARS, caja, depósito y stock sintético. La venta aceptada no se valida con el precio de la búsqueda, sino con el importe de la factura, pago asociado, caja y ledger de inventario realmente persistidos.
