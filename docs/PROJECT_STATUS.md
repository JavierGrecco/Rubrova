# Estado real del proyecto Rubrova

**Corte:** 24 de noviembre de 2026  
**Rama:** `main`  
**Última ejecución nativa completa:** [CI 45537346986](https://github.com/JavierGrecco/Rubrova/actions/runs/45537346986), commit `a0f11eca75e75b9355ea0dbb6be0f4c4ce799ab7`. Compilación, validaciones y Windows pasaron. En Linux x86_64 y macOS ARM64 PostgreSQL y lsFusion/MyCompany iniciaron correctamente y completaron `onFinallyStarted`; ambos smoke fallaron después porque Tomcat devolvió HTTP 404 en `/login`. Tomcat desplegó el directorio `ROOT`, pero no se observó el mapeo del servlet `LSFWeb`. La revisión de `web.xml` detectó que el supervisor reescribía el descriptor Java EE con `ElementTree` sin conservar el namespace por defecto; esta revisión agrega la preservación del namespace y una prueba que exige las rutas `/login` y `/main`. Su efecto todavía debe confirmarse en una nueva ejecución de CI. 
**Última aceptación funcional completa:** [CI 45503956218](https://github.com/JavierGrecco/Rubrova/actions/runs/45503956218)  
**Commit funcional aceptado:** `e23acfc7bb3387ebd184b1aeed9e80c8994593c5`  
**Transición a runtime nativo:** Linux x86_64 ya tiene el smoke nativo; esta revisión incorpora también un smoke automático en macOS ARM64 usando `macos-26` y PostgreSQL 18 ARM64. La primera ejecución de ese nuevo job todavía debe aportar evidencia. No hay todavía un resultado de venta nativa ni una aceptación de uso diario en Mac/Windows.

## Resumen ejecutivo

Rubrova contiene los árboles completos y fijados de lsFusion 6.2 y MyCompany 6.2 en `vendor/`. Su reactor Maven compila servidor, cliente GWT y lógica MyCompany desde las fuentes propias. La decisión de ejecución cambió: el camino principal de desarrollo y CI será nativo (Java 21, PostgreSQL 18 y Tomcat 9); Docker queda como comprobación secundaria y manual.

La aceptación funcional completa más reciente [45503956218](https://github.com/JavierGrecco/Rubrova/actions/runs/45503956218) completó con Chromium una venta sintética de ARS 1.250: factura y pago en efectivo persistidos, stock reducido de 10 a 9, caja conciliada y turno `CLOSED`. También comprobó reinicio de servidor/cliente sin borrar PostgreSQL y ocho resultados de integración simulados. **Esa aceptación corresponde al smoke Docker histórico**, no al nuevo runtime nativo. La lógica comercial ya se probó; ahora hay que repetirla en el entorno que será el principal.

Todos los datos utilizados fueron sintéticos y quedaron en una base temporal de CI que se destruye al terminar. Esta aprobación demuestra el primer recorrido venta → cobro → stock → cierre básico; no habilita aún el uso diario ni significa que el POS/ERP esté terminado.

## Qué está probado

| Capacidad | Estado | Evidencia y alcance |
|---|---|---|
| Fuentes originales lsFusion 6.2 + MyCompany 6.2 | Aprobado | Snapshots fijados en el lock y completos en `vendor/` |
| Compilación del fork Rubrova | Aprobado en CI | Reactor Maven, servidor, cliente GWT y lógica MyCompany compilados desde fuentes propias |
| Imágenes propias del runtime Docker | Aprobado en CI | Artefactos compilados desde fuentes Rubrova e incorporados a imágenes propias; validación Docker pasa a ser secundaria |
| Arranque, RMI y cliente web | Aprobado en smoke Docker histórico; nativo pendiente | El smoke nativo actual inicia lsFusion y completa `onStarted`, pero Tomcat devuelve 404 en `/login`; no se acepta aún el cliente web nativo |
| Login y navegación al POS | Aprobado en smoke Docker histórico; nativo pendiente | Chromium llegó a Comercio → Punto de venta en la aceptación Docker; la ruta nativa actual sigue bloqueada por el 404 web |
| Apertura de turno | Aprobado en CI | Turno sintético `SM/000001` |
| Búsqueda y selección de artículo | Aprobado en CI | Un único producto sintético; una línea de recibo, cantidad 1 y precio ARS 1.250 |
| Confirmación del cobro en efectivo | Aprobado en CI | Se confirma el diálogo nativo de MyCompany mediante `PROPERTY(overFormOk)` |
| Factura y pago | Aprobado en CI | Una factura, una factura pagada, un pago entrante; importe y pago aplicado ARS 1.250 |
| Caja y turno | Aprobado en CI | Efectivo pagado en el turno ARS 1.250; saldo de la cuenta de caja ARS 1.250 |
| Movimiento de stock | Aprobado en CI | Ledger de inventario: entrada 10, salida 1, existencia 9 |
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
| Runtime durante una caída de Internet | En validación nativa | El workflow nuevo bloquea la salida externa y comprueba que el servidor y la UI sigan respondiendo por loopback; falta que la ejecución completa termine correctamente |
| Instalación inicial y paquete completo sin Internet | Pendiente | La prueba de runtime aislado no demuestra todavía que el instalador, los artefactos, las imágenes base y las dependencias puedan instalarse en una PC limpia sin conexión |
| Ejecución local nativa sin Docker | Prototipo implementado; aceptación pendiente | Supervisor Python, instancia PostgreSQL propia, servidor `BusinessLogicsBootstrap` y cliente Tomcat. CI ejecuta smoke de arranque en Linux x86_64 y, desde esta revisión, también en macOS ARM64; aún falta aceptar venta, pagos, stock, cierre y reinicio en ambos runtimes |
| Configuración siempre disponible | En desarrollo inicial | Existe el esquema y el gestor CLI para `native-local`, `docker-local` y `remote-online`; falta el panel visual independiente y su integración con la administración del POS |
| Backup, restauración y rollback | Pendiente | No se acepta producción sin restauración real sobre una copia |
| Windows y macOS ARM64 | Parcial | Windows: PowerShell pasa análisis sintáctico. macOS ARM64: job nativo automático agregado sobre runner Apple Silicon `macos-26`; primera ejecución pendiente. No equivale todavía a aceptación en un Mac de usuario ni a venta nativa |
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

1. **Aceptar el runtime nativo en Linux y Apple Silicon:** lograr que ambos smoke automáticos completen login, menú y persistencia inicial; a continuación reutilizar el fixture comercial para venta, cobro, stock, cierre y reinicio con PostgreSQL local.
2. **Completar la aceptación comercial en nativo:** mover los fixtures sintéticos al harness compartido y repetir venta, pagos, caja, stock, cierre, reinicio y conciliación.
3. **Completar caja y pagos:** arqueo contado, diferencias, ingresos/retiros, vuelto, pagos mixtos, tarjeta y cancelación.
4. **Persistencia y recuperación:** reiniciar servidor y cliente sin borrar PostgreSQL y repetir consultas de factura, pago, turno y ledger. Probar además backup/restore y rollback sobre copias.
5. **Prueba del camino HTTP de navegador:** `EXTERNAL HTTP CLIENT` real desde Chromium, con timeout, CORS, abort, fallo de red y recuperación.
6. **Instalación offline y plataformas:** paquete completo en PC limpia sin Internet; después validación real en Windows y macOS ARM64.
7. **ERP y localización:** continuar compras, inventario, proveedores, reportes y experiencia visual sobre módulos originales, adaptando con extensiones propias.
8. **Fiscalidad e integraciones externas:** ARCA, medios electrónicos, marketplaces y logística sólo después de tener idempotencia, Outbox, circuit breaker, auditoría y conciliación probadas.

La aceptación funcional 45503956218 demuestra el primer recorrido comercial integrado —venta, pago, salida de stock y cierre básico— en el runtime Docker construido desde fuentes Rubrova. No demuestra todavía el mismo recorrido en el runtime nativo, no declara terminado el producto ni autoriza producción. La aceptación completa requiere devoluciones y reintegros conciliados, arqueo y movimientos de caja, casos de pago restantes, persistencia después de reiniciar, restauración desde backup y comportamiento seguro ante fallos externos.

## Política transversal de errores

Se mantiene la política de [Resiliencia de integraciones y tratamiento de errores](INTEGRATION_RESILIENCE_AND_ERROR_HANDLING.md). El motor lsFusion ofrece `timeoutHttp()`, `HEADERSTO` y `TRY/CATCH`, pero esos mecanismos no sustituyen una política completa. El helper GET y el registro de incidencias se probaron contra un proveedor simulado; faltan Outbox, circuit breaker y ampliar los escenarios de escritura más allá de GET. Los conectores de producción permanecen deshabilitados hasta superar esas puertas.

Los logs SQL de arranque se interpretan en el diagnóstico técnico actualizado: las dos consultas iniciales de `dumb` pertenecen a la detección de base vacía; el conflicto serializable de `Time.currentDate` se recuperó y el valor quedó persistido. Los timeouts de consultas siguen observándose y deben medirse para mejorar el arranque, sin aumentar límites indiscriminadamente.

La prueba de venta usa `RubrovaCISalesFixture` sólo en CI: prepara ARS, caja, depósito y stock sintético. La venta aceptada no se valida con el precio de la búsqueda, sino con el importe de la factura, pago asociado, caja y ledger de inventario realmente persistidos.
