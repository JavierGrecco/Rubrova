# Estado real del proyecto Rubrova

**Corte:** 22 de noviembre de 2026  
**Rama:** `main`  
**Última aceptación funcional:** [CI #172](https://github.com/JavierGrecco/Rubrova/actions/runs/44982716337)  
**Commit probado:** `3d1cfbf1038e25608768c1561349390708dca6ec`

## Resumen ejecutivo

Rubrova ya compila desde sus propias fuentes vendorizadas de lsFusion 6.2 y MyCompany 6.2, construye las imágenes propias del runtime y las ejecuta en un entorno CI Linux x86_64 descartable. La ejecución #172 completó una venta minorista real dentro de esa base temporal: el POS creó una sola factura por ARS 1.250, registró un único ingreso de efectivo, dejó la factura pagada, sumó ARS 1.250 al turno y a la cuenta de caja, y descontó una unidad del inventario (10 iniciales, 1 salida, 9 disponibles).

La aceptación no se basa sólo en el mensaje visual. Chromium confirmó el diálogo de cobro y el test consultó las entidades y ledgers persistidos. Los datos del cliente, caja, producto, ubicación, ajuste inicial, venta y pago son sintéticos y se destruyen al terminar el CI. No se modificaron datos comerciales de una instalación real.

Esta aprobación cierra el primer circuito comercial del POS. No significa que el POS/ERP completo esté terminado: faltan probar cierre de turno, devoluciones, vuelto, pagos mixtos/tarjeta, persistencia después de reiniciar, instalación offline, backup/restore y ejecución real en Windows y macOS.

## Qué está probado

| Capacidad | Estado | Evidencia y alcance |
|---|---|---|
| Fuentes originales lsFusion 6.2 + MyCompany 6.2 | Aprobado | Snapshots fijados en el lock y completos en `vendor/` |
| Compilación del fork Rubrova | Aprobado en CI | Reactor Maven, servidor, cliente GWT y lógica MyCompany compilados desde fuentes propias |
| Imágenes propias del runtime | Aprobado en CI | Servidor, lógica y cliente construidos y utilizados por el smoke |
| Arranque, RMI y cliente web | Aprobado en CI | PostgreSQL 18, lógica, RMI 7652, Tomcat y acceso Chromium |
| Login y navegación al POS | Aprobado en CI | Chromium llega a Comercio → Punto de venta |
| Apertura de turno | Aprobado en CI | Turno sintético `SM/000001` |
| Búsqueda y selección de artículo | Aprobado en CI | Un único producto sintético; una línea de recibo, cantidad 1 y precio ARS 1.250 |
| Confirmación del cobro en efectivo | Aprobado en CI | Se confirma el diálogo nativo de MyCompany mediante `PROPERTY(overFormOk)` |
| Factura y pago | Aprobado en CI | Una factura, una factura pagada, un pago entrante; importe y pago aplicado ARS 1.250 |
| Caja y turno | Aprobado en CI | Efectivo pagado en el turno ARS 1.250; saldo de la cuenta de caja ARS 1.250 |
| Movimiento de stock | Aprobado en CI | Ledger de inventario: entrada 10, salida 1, existencia 9 |
| Resiliencia HTTP GET | Aprobado en escenarios CI | Timeout, clasificación de 408/429/503 y errores definitivos, persistencia de incidencias y recuperación del proveedor simulado |
| `HEADERSTO` / `Retry-After` | Aprobado en escenario CI | El 429 devuelve y persiste `Retry-After: 2` con el mecanismo nativo de lsFusion |
| Timeout de `EXTERNAL HTTP CLIENT` desde navegador | Pendiente | Falta una prueba real en Chromium con endpoint lento/CORS, abort, error de red y recuperación |
| Cierre y arqueo de turno | Pendiente | Falta conciliar apertura, ventas, devoluciones, ingresos/retiros y saldo final |
| Devolución y reintegro | Pendiente | Falta comprobar Bill, OutgoingPayment, medio original y movimiento inverso de stock |
| Vuelto, pagos mixtos y tarjeta | Pendiente | El primer circuito aceptado sólo cubre efectivo exacto, sin vuelto |
| Reinicio conservando datos | Pendiente | Falta reiniciar servidor/cliente conservando PostgreSQL y volver a conciliar factura, pago, caja y stock |
| Traducción completa | Parcial | POS inicial localizado; aún quedan textos heredados en inglés |
| Instalación local sin Internet | Pendiente | CI construye imágenes propias, pero no demuestra todavía paquete completo offline ni ausencia de descargas en una PC limpia |
| Backup, restauración y rollback | Pendiente | No se acepta producción sin restauración real sobre una copia |
| Windows y macOS ARM64 | Parcial | PowerShell pasa análisis sintáctico; macOS ARM64 no se ejecutó en #172 y no hay aceptación runtime nativa en esas plataformas |
| ARCA, adquirentes, marketplaces y logística | Pendiente | Ningún conector comercial se habilita hasta superar idempotencia, Outbox, circuit breaker, fallos simulados y conciliación |

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

1. **Cerrar el turno de caja:** partir de la venta aceptada y verificar cierre, importes esperados, diferencias, movimientos y saldo final.
2. **Devolución y reintegro:** usar el circuito original de MyCompany, relacionar Bill con la factura, verificar el medio y monto efectivamente abonados, el OutgoingPayment y la reversión correspondiente de stock.
3. **Completar los casos de pago:** vuelto, pagos parciales/mixtos, tarjeta y cancelación, con conciliación exacta por medio.
4. **Persistencia y recuperación:** reiniciar servidor y cliente sin borrar PostgreSQL y repetir consultas de factura, pago, turno y ledger. Probar además backup/restore y rollback sobre copias.
5. **Prueba del camino HTTP de navegador:** `EXTERNAL HTTP CLIENT` real desde Chromium, con timeout, CORS, abort, fallo de red y recuperación.
6. **Instalación offline y plataformas:** paquete completo en PC limpia sin Internet; después validación real en Windows y macOS ARM64.
7. **ERP y localización:** continuar compras, inventario, proveedores, reportes y experiencia visual sobre módulos originales, adaptando con extensiones propias.
8. **Fiscalidad e integraciones externas:** ARCA, medios electrónicos, marketplaces y logística sólo después de tener idempotencia, Outbox, circuit breaker, auditoría y conciliación probadas.

La aceptación #172 demuestra el primer ciclo comercial local —venta, pago y salida de stock— en el runtime propio de Rubrova. No declara terminado el producto ni autoriza producción. La aceptación completa requiere operación local estable, cierre y devolución conciliados, persistencia después de reiniciar, restauración desde backup y comportamiento seguro ante fallos externos.

## Política transversal de errores

Se mantiene la política de [Resiliencia de integraciones y tratamiento de errores](INTEGRATION_RESILIENCE_AND_ERROR_HANDLING.md). El motor lsFusion ofrece `timeoutHttp()`, `HEADERSTO` y `TRY/CATCH`, pero esos mecanismos no sustituyen una política completa. El helper GET y el registro de incidencias se probaron contra un proveedor simulado; faltan Outbox, circuit breaker y ampliar los escenarios de escritura más allá de GET. Los conectores de producción permanecen deshabilitados hasta superar esas puertas.

Los logs SQL de arranque se interpretan en el diagnóstico técnico actualizado: las dos consultas iniciales de `dumb` pertenecen a la detección de base vacía; el conflicto serializable de `Time.currentDate` se recuperó y el valor quedó persistido. Los timeouts de consultas siguen observándose y deben medirse para mejorar el arranque, sin aumentar límites indiscriminadamente.

La prueba de venta usa `RubrovaCISalesFixture` sólo en CI: prepara ARS, caja, depósito y stock sintético. La venta aceptada no se valida con el precio de la búsqueda, sino con el importe de la factura, pago asociado, caja y ledger de inventario realmente persistidos.
