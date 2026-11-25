# Estado real del proyecto Rubrova

**Corte:** 25 de noviembre de 2026  
**Rama:** `main`  
**Última aceptación comercial nativa:** [CI 45548326798](https://github.com/JavierGrecco/Rubrova/actions/runs/45548326798), commit `1f560fbce43d3f9c6512ed2654728cd6250dbe89`. El job macOS ARM64 completó login, apertura de turno, venta en efectivo, factura/pago, conciliación de stock, cierre de turno/caja e incidencia de integración. El job Linux nativo inició el servidor, pero Chromium dejó `PosDashboard` cargando; queda como diagnóstico no bloqueante.  
**Última aceptación funcional Docker completa:** [CI 45503956218](https://github.com/JavierGrecco/Rubrova/actions/runs/45503956218).  
**Estado:** la nueva política de CI hace obligatoria la aceptación Docker/Linux y conserva macOS nativo como puerta obligatoria; el nuevo run [45553489598](https://github.com/JavierGrecco/Rubrova/actions/runs/45553489598) está en curso al momento de este corte. No hay aceptación en un Mac físico ni autorización para uso diario.

## Resumen ejecutivo

Rubrova contiene los árboles completos y fijados de lsFusion 6.2 y MyCompany 6.2 en `vendor/`. Su reactor Maven compila servidor, cliente GWT y lógica MyCompany desde las fuentes propias. El desarrollo local prioriza el runtime nativo (Java 21, PostgreSQL 18 y Tomcat 9), especialmente en macOS. CI exige tanto la aceptación nativa macOS ARM64 como la aceptación funcional Docker/Linux; Linux nativo sin Docker queda como diagnóstico no bloqueante.

La aceptación Docker [45503956218](https://github.com/JavierGrecco/Rubrova/actions/runs/45503956218) completó con Chromium una venta sintética de ARS 1.250, factura/pago, stock reducido de 10 a 9, caja conciliada y turno `CLOSED`; también comprobó reinicio y escenarios HTTP simulados. Después, la aceptación nativa macOS ARM64 [45548326798](https://github.com/JavierGrecco/Rubrova/actions/runs/45548326798) completó venta, pago, stock y cierre en el runner Apple Silicon. La segunda evidencia confirma el runtime nativo, pero no reemplaza la prueba en un Mac de usuario. El nuevo job Docker/Linux automático debe confirmar otra vez el empaquetado y el ciclo POS.

Todos los datos utilizados fueron sintéticos y quedaron en una base temporal de CI que se destruye al terminar. Esta aprobación demuestra el primer recorrido venta → cobro → stock → cierre básico; no habilita aún el uso diario ni significa que el POS/ERP esté terminado.

## Qué está probado

| Capacidad | Estado | Evidencia y alcance |
|---|---|---|
| Fuentes originales lsFusion 6.2 + MyCompany 6.2 | Aprobado | Snapshots fijados en el lock y completos en `vendor/` |
| Compilación del fork Rubrova | Aprobado en CI | Reactor Maven, servidor, cliente GWT y lógica MyCompany compilados desde fuentes propias |
| Imágenes propias del runtime Docker | Construcción previa aprobada; nueva aceptación obligatoria en CI | Artefactos compilados desde fuentes Rubrova e incorporados a imágenes propias; el job Docker/Linux ahora es automático y obligatorio |
| Arranque, RMI y cliente web | Aprobado en macOS ARM64 CI y Docker histórico | En `45548326798` macOS inició PostgreSQL, servidor, RMI, Tomcat y cliente web; el diagnóstico Linux nativo es la única ruta que no renderizó el POS |
| Login y navegación al POS | Aprobado en macOS ARM64 CI y Docker histórico | Chromium llegó a Comercio → Punto de venta y el POS abrió turno en el runtime nativo macOS; Linux nativo separado queda en diagnóstico |
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
| Runtime durante una caída de Internet | No aceptado | Linux nativo bloquea la salida externa, pero el navegador queda cargando en `PosDashboard`; macOS nativo pasó el recorrido comercial con conectividad normal, no una prueba offline. Investigar dependencias de navegador antes de aprobar este escenario |
| Instalación inicial y paquete completo sin Internet | Pendiente | La prueba de runtime aislado no demuestra todavía que el instalador, los artefactos, las imágenes base y las dependencias puedan instalarse en una PC limpia sin conexión |
| Ejecución local nativa sin Docker | Aceptación comercial básica en macOS ARM64 CI; prueba en equipo real pendiente | Supervisor Python, instancia PostgreSQL propia, servidor `BusinessLogicsBootstrap` y cliente Tomcat. El recorrido de venta, pago, stock y cierre pasó en el runner Apple Silicon; falta repetir en un Mac de usuario y ampliar la cobertura. Linux nativo es un diagnóstico no bloqueante |
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

1. **Confirmar Docker/Linux en la nueva CI:** exigir que el job automático complete la venta sintética, pagos, stock, caja, cierre y pruebas de integraciones con las imágenes Rubrova.
2. **Verificar el runtime nativo en el Mac de usuario:** repetir el recorrido que ya pasó en CI con PostgreSQL 18 y Java 21 ARM64, revisar persistencia, logs y estabilidad.
3. **Completar la cobertura del POS:** arqueo contado, diferencias, ingresos/retiros, vuelto, pagos mixtos, tarjeta, devoluciones y cancelaciones.
4. **Investigar Linux nativo sin bloquear el producto:** reproducir el `PosDashboard` que queda cargando bajo bloqueo de salida externa y localizar la dependencia de navegador; no cambiar reglas comerciales para compensar el entorno CI.
5. **Persistencia y recuperación:** reiniciar servidor y cliente sin borrar PostgreSQL; probar backup/restore y rollback sobre copias.
6. **Instalación offline y Windows:** paquete completo en PC limpia sin Internet; validar instalación, procesos, permisos y rutas en Windows x64.
7. **ERP y localización:** continuar compras, inventario, proveedores, reportes y experiencia visual sobre módulos originales, adaptando con extensiones propias.
8. **Fiscalidad e integraciones externas:** ARCA, medios electrónicos, marketplaces y logística sólo después de tener idempotencia, Outbox, circuit breaker, auditoría y conciliación probadas.

La evidencia `45503956218` demuestra el recorrido comercial básico en Docker y `45548326798` demuestra ese recorrido en el runtime nativo macOS ARM64 de CI. Ninguna de las dos ejecuciones declara terminado el producto ni autoriza producción. La aceptación completa requiere devoluciones y reintegros conciliados, arqueo y movimientos de caja, vuelto, pagos mixtos/tarjeta, persistencia tras reiniciar el runtime nativo, restauración desde backup y comportamiento seguro ante fallos externos.

## Política transversal de errores

Se mantiene la política de [Resiliencia de integraciones y tratamiento de errores](INTEGRATION_RESILIENCE_AND_ERROR_HANDLING.md). El motor lsFusion ofrece `timeoutHttp()`, `HEADERSTO` y `TRY/CATCH`, pero esos mecanismos no sustituyen una política completa. El helper GET y el registro de incidencias se probaron contra un proveedor simulado; faltan Outbox, circuit breaker y ampliar los escenarios de escritura más allá de GET. Los conectores de producción permanecen deshabilitados hasta superar esas puertas.

Los logs SQL de arranque se interpretan en el diagnóstico técnico actualizado: las dos consultas iniciales de `dumb` pertenecen a la detección de base vacía; el conflicto serializable de `Time.currentDate` se recuperó y el valor quedó persistido. Los timeouts de consultas siguen observándose y deben medirse para mejorar el arranque, sin aumentar límites indiscriminadamente.

La prueba de venta usa `RubrovaCISalesFixture` sólo en CI: prepara ARS, caja, depósito y stock sintético. La venta aceptada no se valida con el precio de la búsqueda, sino con el importe de la factura, pago asociado, caja y ledger de inventario realmente persistidos.
