# MyCompany 6.2 — mapa de inventario, reservas y costos

**Estado: análisis de fuentes parcial; pruebas de runtime y conciliación pendientes.**

Este documento profundiza el dominio de inventario de MyCompany 6.2. No se limita al saldo de stock: separa movimientos físicos, compromisos/reservas y valuación/costo, y sigue la relación entre recepciones, ubicación interna, despachos, transferencias, aceptación, ajustes, lotes y costos.

## 1. Modelo de tres ledgers

El código no maneja el stock como un único número mutable. Hay tres familias de registros que se complementan, pero no deben confundirse.

### 1.1 Ledger de movimientos físicos — InvLedger

El módulo InvLedger concentra movimientos de inventario con tipo, estado activo, aceptación pendiente, fecha/hora, número, ubicación de origen, ubicación de destino, producto, cantidad y socio relacionado.

- Un ingreso se toma de movimientos activos con ubicación destino igual a la ubicación consultada, excluyendo los marcados como notAccepted.
- Un egreso se toma de movimientos activos con ubicación origen igual a la ubicación consultada.
- El saldo físico se calcula como ingresos menos egresos.
- Se calcula por producto y ubicación, con agregación jerárquica de ubicaciones.
- Hay variantes históricas por fecha/hora y límites temporales inclusivos/exclusivos.
- La configuración positiveOnHand de la ubicación puede impedir que el saldo físico quede por debajo de cero; la regla puede heredarse desde la jerarquía de ubicaciones.

**Consecuencia:** un documento en borrador o una reserva no constituye por sí mismo un movimiento físico. El ingreso/egreso real depende del ledger específico que el documento incorpora al completarse y de que el movimiento esté activo.

### 1.2 Ledger de reservas, esperado y disponible — ResLedger

El ledger de reservas representa compromisos y cantidades esperadas:

- Las reservas de egreso se registran como cantidades positivas.
- Las entradas esperadas se pueden representar con cantidades negativas.
- Se separan las cantidades esperadas, reservadas y planificadas.
- El disponible se deriva del saldo físico menos las cantidades planificadas.
- Los movimientos marcados con skipAvailable se muestran en el ámbito de reservas/esperados, pero no modifican el cálculo de disponible.
- La configuración positiveAvailable puede impedir reservar por encima de lo disponible.

En las recepciones, el tipo tiene la opción increaseAvailableStock. Si está desactivada, el ingreso esperado se marca para no intervenir en el disponible. Si está activada, el esperado puede mejorar el disponible según las reglas del ledger. Esto debe distinguirse de la existencia física: un ingreso esperado no es mercadería ya recibida.

En los despachos, las reservas se generan para estados de espera/listo y se liberan al desreservar, cancelar o completar el circuito, según las condiciones del documento.

### 1.3 Ledger de costos — CostLedger

El costo tiene registros y cálculos separados del movimiento físico y de la reserva.

- Hay entradas y salidas de costo; el costo unitario y el importe se asocian a fecha/hora, ubicación de costo y producto.
- Los métodos disponibles son costo planificado/estándar (standardPrice), costo promedio (avco) y FIFO (fifo).
- El método se configura en la categoría y se hereda a los productos; en la fuente revisada, el producto usa FIFO como valor por defecto cuando no hay una definición heredada.
- El costo planificado tiene historial por artículo y fecha de vigencia.
- El recálculo se puede ejecutar a partir de una fecha y limitarse por ubicación/producto.
- CostLocation agrupa ubicaciones físicas bajo la ubicación superior más cercana marcada para calcular costos; si no hay una marcada, llega a la raíz. Por eso dos ubicaciones físicas pueden compartir una misma ubicación de costo.

**Riesgo de fuente prioritario — FIFO y fecha de la recepción:** en CostLedger.lsf, las dos ramas de partición FIFO contienen comentada la condición que restringía las entradas a una fecha/hora menor o igual a la salida que se está valuando. En el código leído, la selección de entradas se sigue ordenando por fecha/hora, pero no se ve activa esa restricción temporal. Es un posible problema al valuar una salida anterior a una recepción posterior, no un defecto confirmado hasta reproducirlo con datos y recálculo. No debe cambiarse la lógica sin entender el algoritmo completo y probarlo.

La regresión mínima debe incluir: ingreso del 10 de abril, egreso del 12 de abril, segundo ingreso del 15 de abril; costo FIFO del egreso del 12 no debería consumirse de un ingreso del 15. Repetir luego de registrar movimientos fuera de orden y recalcular el costo desde distintas fechas.

## 2. Recepción: esperado → recepción efectiva → ubicación interna

### 2.1 Documento de recepción

Receipt tiene tipo, fecha programada, número, ubicación, proveedor, referencia del proveedor, nota y líneas con artículo y cantidad inicial. El artículo debe permitir compra; se controlan cantidades no negativas y máximos configurados para el tipo. Existe también una recepción inmediata no planificada.

La recepción tiene historial, archivos, comentarios, acceso por ubicación y copia de documentos. Estos elementos de soporte deben mapearse junto con los datos operativos; no son sólo campos visuales.

### 2.2 Reserva de recepción

ReceiptRes crea el registro de esperado cuando la línea tiene cantidad inicial positiva, la recepción está lista y todavía no está completada. El ingreso esperado se representa como una reserva negativa. La opción increaseAvailableStock del tipo controla si ese esperado participa del cálculo de disponible.

### 2.3 Recepción efectiva

ReceiptDone registra la cantidad recibida y la fecha/hora de ejecución. ReceiptInv lleva al ledger físico la cantidad completada que aún no fue distribuida mediante ubicación interna. La recepción cancelada deja de aportar un movimiento activo al saldo.

### 2.4 Ubicación interna (put-away)

El módulo ReceiptPutAway permite dividir lo recibido entre la ubicación principal del documento y ubicaciones hijas:

- Sólo se puede elegir una ubicación descendiente de la ubicación de la recepción.
- La cantidad ubicada se acumula por línea y no puede superar la cantidad recibida.
- El proceso se habilita para tipos configurados con putAway, una vez que la recepción está lista o completada.
- ReceiptPutAwayLedger genera el movimiento hacia la ubicación hija.
- ledgerDone acumula lo ya ubicado; ReceiptInv descuenta esa parte del ingreso que permanece en la ubicación principal.

La intención del diseño es evitar doble conteo: la misma cantidad recibida debe estar una sola vez en el saldo, ya sea en la ubicación principal o en una ubicación hija. Hay que verificarlo con movimientos parciales, varias ubicaciones, eliminación/reversión de líneas de ubicación interna y cancelación de recepción.

### 2.5 Costo de recepción

ReceiptCost genera una entrada al ledger de costo por cantidad recibida y recepción activa. El tipo puede habilitar el ingreso manual del costo por línea. Cuando no hay costo de línea, la fuente incorpora el mecanismo abstracto de costo del artículo u otras extensiones; se debe seguir su resolución completa antes de asumir cuál es el valor final. El documento acumula el importe de costo de sus líneas.

## 3. Despacho: reserva → preparación → egreso → aceptación

### 3.1 Documento y tipo de despacho

Shipment tiene tipo, fecha programada, número, ubicación origen, posible ubicación destino, cliente, dirección de entrega, referencia, nota y líneas de producto/cantidad. Los artículos deben poder venderse. Un tipo puede ser un traslado; en ese caso exige ubicación destino y no permite que origen y destino sean iguales.

### 3.2 Espera y reserva

ShipmentReady trabaja con estados de espera/listo. Al controlar disponibilidad, calcula cuánto se puede reservar por línea, sin reservar valores negativos. El documento queda listo cuando todas sus líneas tienen reservada la cantidad demandada.

Se puede desreservar. La acción de despacho parcial crea otro documento con las cantidades que quedaron sin reservar y permite continuar el circuito por separado. Es necesario comprobar en runtime cómo quedan relacionados ambos documentos, qué sucede con referencias y lotes, y cómo se comportan los permisos y las cancelaciones.

### 3.3 Preparación y picking

Hay módulos específicos de picking y tareas. La auditoría debe diferenciar:
- cantidad pedida en el despacho;
- cantidad reservada;
- cantidad seleccionada/preparada;
- cantidad efectivamente despachada.

La existencia de una tarea de picking no demuestra por sí sola que la reserva esté completa o que se haya efectuado el movimiento físico.

### 3.4 Despacho efectivo

ShipmentDone permite completar despachos listos o despachos inmediatos en borrador. Si no se ingresaron cantidades efectivas, puede pedir completar con las cantidades reservadas. La cantidad despachada no puede superar la demanda inicial, salvo que el tipo habilite explícitamente doNotCheckDone. Al confirmar registra fecha/hora de ejecución.

ShipmentInv traslada al ledger físico la cantidad completada aún no contabilizada. Para una salida, descuenta de la ubicación de origen; en un traslado puede registrar también el destino.

### 3.5 Aceptación en la ubicación destino

El traslado puede requerir aceptación cuando el usuario que lo inicia no tiene acceso a la ubicación destino:

- Al cambiar el destino, la fuente marca acceptanceConfirmation cuando el usuario no tiene permiso sobre la ubicación nueva.
- El documento puede quedar completado, pero el ingreso destino permanece marcado notAccepted.
- ShipmentAcceptanceInv conecta esa confirmación con el ledger y excluye el ingreso no aceptado del saldo físico destino.
- La acción accept sólo aparece para un usuario que tiene acceso a la ubicación destino.
- Una vez aceptado, el movimiento deja de estar marcado notAccepted y pasa a contar en el saldo destino.

Esto es un mecanismo de control entre depósitos/usuarios, no una simple confirmación visual. Debe probarse con dos perfiles, uno con acceso sólo al origen y otro sólo al destino, incluyendo rechazo, cancelación, destino cambiado y reintentos.

### 3.6 Costo de un traslado

ShipmentCost genera una salida de costo de la ubicación de costo origen y una entrada de costo en la ubicación de costo destino, pero sólo cuando ambas ubicaciones pertenecen a grupos de costo diferentes. El importe de entrada deriva del costo de salida. Si las ubicaciones físicas comparten la misma CostLocation, no se genera ese traspaso de costo.

## 4. Ajuste: teórico → conteo físico → diferencia → ledger

Adjustment registra el artículo, ubicación y cantidad teórica y real. La ubicación de cada línea debe quedar dentro de la ubicación padre del documento.

- En el estado en progreso se puede completar el conteo real; según la configuración, puede copiarse la cantidad teórica como valor inicial o acumularse el conteo manual.
- La diferencia se calcula como cantidad real menos cantidad teórica.
- Al marcar el ajuste como completado se generan movimientos de inventario por la diferencia. Una diferencia positiva ingresa; una negativa egresa.
- Sólo las líneas con diferencia generan el movimiento normal, aunque hay una opción para crear ajustes de entrada manuales.
- Los ajustes cancelados dejan de aportar movimientos activos.
- Hay módulos específicos para costos y lotes; el costo puede requerir un precio manual para ajustes de entrada y el conteo puede desglosarse por lote.

**Pendiente:** comprobar qué sucede con cambios retroactivos de la cantidad teórica, inventario negativo, edición posterior, ajustes con lote, múltiples unidades, costo, diferencias por redondeo y cancelación luego de completar.

## 5. Lotes, series, códigos y ubicaciones

- ProductLot hereda de la categoría si un producto trabaja con lotes, números de serie, numerador y prefijo.
- ReceiptLot permite registrar cantidades iniciales/recibidas por lote y, mediante el flujo de código de barras, puede crear un lote si no existe.
- ShipmentLot separa las cantidades por lote y las relaciona con el despacho efectivo.
- InvLedgerLot calcula ingresos, egresos y saldo por lote y ubicación, con historia temporal y consultas de movimientos.
- Hay ubicaciones preferidas por producto dentro de una ubicación jerárquica; el destino sugerido debe seguir perteneciendo a la jerarquía correspondiente.
- Los paquetes y conversiones de unidad también afectan cantidades y picking; faltan pruebas conjuntas con lotes y reservas.

GTIN, SKU, código de barras y número de lote no se deben tratar como equivalentes. El módulo ProductGtin está fuera del cierre base de Rubrova y debe analizarse por separado antes de decidir activarlo.

## 6. Matriz de escenarios pendientes de ejecución

| Área | Escenario positivo | Excepciones y conciliaciones obligatorias |
|---|---|---|
| Stock físico | Recepción y despacho simple | Cancelación, cantidades parciales, fechas retroactivas, inventario negativo y unidades |
| Reservas | Reserva completa y liberación | Dos usuarios compitiendo, reserva parcial, expected, cambio de tipo y cancelación |
| Recepción | Recepción total/parcial | Duplicación, sobre-recepción, proveedor/empresa, referencia, borrador y reintento |
| Ubicación interna | Una recepción dividida en dos ubicaciones hijas | Ubicación no descendiente, sobre-ubicación, reversión, cancelación y doble conteo |
| Despacho | Reserva, picking y egreso | Picking incompleto, despacho parcial, over-ship, desreservar, cancelación y faltantes |
| Traslado | Salida origen y entrada destino | Aceptación pendiente, usuario sin permiso, traslado entre ubicaciones con mismo/diferente costo |
| Ajustes | Conteo con faltante y sobrante | Lote, costo, redondeo, ajustes repetidos, cancelación y movimientos retroactivos |
| Lotes | Recepción y despacho de varios lotes | Lote inválido, duplicado, serie única, cantidad por lote y saldo negativo |
| Costos | Estándar, promedio y FIFO | Recepciones posteriores, movimientos fuera de orden, recálculo, devolución y traslado |
| Histórico | Consulta de stock a una fecha/hora | Límites inclusivos/exclusivos, misma marca temporal y reconstrucción luego de cancelar |

Para aceptar un escenario hay que conciliar simultáneamente: documento origen, documento resultante, cantidades por línea, ledger físico, ledger de reserva, ledger de costo, saldo por ubicación/producto/lote, historial, reportes y permisos. Una pantalla que muestre el saldo esperado no alcanza.

## 7. Riesgos que bloquean una conclusión funcional

1. **FIFO:** falta reproducir la selección de entradas posteriores a la fecha de la salida y evaluar recálculo retroactivo.
2. **Traslados pendientes de aceptación:** falta probar que el saldo destino no aumente antes de aceptar y que el origen se descuente una sola vez.
3. **Ubicación interna:** falta probar el reparto entre ubicación padre e hijas ante cambios y cancelaciones.
4. **Reservas esperadas:** falta verificar las opciones de tipo que incluyen/excluyen ingresos esperados del disponible y su interacción con pedidos de compra.
5. **CostLocation:** falta verificar qué sucede al mover mercadería entre ubicaciones dentro y fuera del mismo grupo de costo.
6. **Lotes y unidades:** falta conciliar unidades alternativas, paquetes, series, códigos y movimientos físicos/costos.
7. **Recálculo histórico:** falta verificar consistencia ante operaciones ingresadas fuera de orden y cancelaciones.

No se propone corregir nada de esto a ciegas. Primero hay que construir escenarios reproducibles, registrar el resultado de la fuente 6.2 y distinguir defecto, comportamiento intencional o límite documentado.

## 8. Fuentes LSF revisadas y trazabilidad

Las referencias son SHA de blob de los archivos del snapshot MyCompany 6.2 incluido en Rubrova. Sirven para identificar exactamente la fuente leída; no equivalen a una prueba de ejecución.

| Módulo/archivo | SHA de blob | Líneas |
|---|---|---:|
| inventory/ledgers/inv/InvLedger.lsf | b88ddc727087292bd886c5575b09f5ceaba18d89 | Revisado |
| inventory/ledgers/res/ResLedger.lsf | 45ab3e6f01721ad3057ef845dcdd859b2352875f | Revisado |
| inventory/ledgers/cost/CostLedger.lsf | a43fdc7faba64455cb7a36cab8a5eb9942faa98d | Revisado |
| inventory/ledgers/cost/CostProduct.lsf | b233f23cbc1c8c9f8ea008fc9322889a1f3c0288 | 38 |
| inventory/ledgers/cost/CostLocation.lsf | 2145541e43dfa7ddd200cf09de1765f5c0a6c064 | 24 |
| masterdata/items/ItemCost.lsf | 9f7e42ddfa09418b7dc9f4bba601ff43ab62b8f3 | 70 |
| masterdata/items/products/ProductLot.lsf | 2e4c427b42cd809db41e97d9052da2f53be27f22 | 23 |
| inventory/ledgers/inv/InvLedgerLot.lsf | 4495f9bee6f3665933e166cd9b20bfff69be911c | 146 |
| inventory/receipts/Receipt.lsf | d7249c8de5a630d274e21c98899f2d4df4e53222 | 253 |
| inventory/receipts/ReceiptDone.lsf | 322df12b3fe609510d64e83708381d182b4a1515 | 87 |
| inventory/receipts/ReceiptCanceled.lsf | fc7028f79975519809c9e290316eb39e38c829fd | 47 |
| inventory/receipts/ReceiptPutAway.lsf | 1b49d9751b3504faefb07df907fae9c03f054dbf | 143 |
| inventory/receipts/ReceiptInv.lsf | 6c4fab05144612ef06a502d9934a7b9a48b5a35c | 25 |
| inventory/receipts/ReceiptCost.lsf | a529318beaecf70de32fa04ae66db7d931c9d542 | 40 |
| inventory/receipts/ReceiptRes.lsf | 806dbfe4500b9aa1eaaacf41d89e63cfc64d8955 | 28 |
| inventory/receipts/lot/ReceiptLot.lsf | 0fddef54db545bc9308aab730b20e582666c4575 | 33 |
| inventory/shipments/Shipment.lsf | 281a2ab37e4f610eecbfb612ce543a8a16c5dfd8 | 290 |
| inventory/shipments/ShipmentReady.lsf | 20041e8ab40c263e1e6ec370a64b2f0ee2941505 | 112 |
| inventory/shipments/ShipmentDone.lsf | b77c7c98705fa428c33851cd1b41b1f9b7118cda | 96 |
| inventory/shipments/ShipmentInv.lsf | 0f9e1a82d60334e2819e4b6ca84278c719deee2a | 26 |
| inventory/shipments/ShipmentCost.lsf | c6a1eb93ba194811d2eed644b266d86326a1d92b | 48 |
| inventory/shipments/ShipmentRes.lsf | acf478e7db88fbf7f44b96f3794999716f639183 | 25 |
| inventory/shipments/acceptance/ShipmentAcceptance.lsf | 3836502d72b1d402b52f74596bfb0c148c77fd44 | 58 |
| inventory/shipments/acceptance/ShipmentAcceptanceInv.lsf | f431465f8d975bca49e769bdac7ff982221f740a | 7 |
| inventory/shipments/lot/ShipmentLot.lsf | f9013237d9aa9fa4e5eab89f2e3efb56de29b0cf | 25 |
| inventory/adjustments/Adjustment.lsf | 17381a62bd67f09f952058dd2212634132dc5073 | 210 |
| inventory/adjustments/AdjustmentInProgress.lsf | 0f325301576558b33bdc6f3484dfb00d1ce25416 | 68 |
| inventory/adjustments/AdjustmentDone.lsf | e8f98ab43ec199143b0b87193daedce06cfcf98a | 84 |
| inventory/adjustments/AdjustmentCanceled.lsf | ffcfc18e2fa44926f840c015bf91434c2107cec6 | 45 |
| inventory/adjustments/AdjustmentInv.lsf | eeb72dac9609fe3170f126e31db9f49d645c43e6 | 18 |
| inventory/adjustments/AdjustmentCost.lsf | cc855e86063d11bc12ee7539eb0c5217dbaf132a | 70 |
| inventory/adjustments/AdjustmentLot.lsf | 3718ba7a7d537e34a6865c968626bfd73130db48 | 72 |

**Cobertura del dominio:** estos archivos corresponden a una selección importante de módulos de inventario, pero el árbol completo contiene 112 archivos LSF en el dominio. Falta identificar y analizar los módulos restantes de depósitos, ubicaciones, empaques, movimientos, búsquedas, reportes, costos, inventario móvil, lotes y utilidades. Por lo tanto, el dominio de inventario sigue siendo parcial.

## 9. Estado final de esta revisión

- Modelo de tres ledgers: **identificado en fuente**.
- Recepción, ubicación interna y movimiento físico: **analizado parcialmente en fuente**.
- Despacho, reserva, movimiento y aceptación: **analizado parcialmente en fuente**.
- Ajustes, lotes y costos: **analizado parcialmente en fuente**.
- FIFO y fecha de entradas: **riesgo de fuente identificado; reproducción pendiente**.
- Arranque, formularios, permisos, reportes y conciliación de punta a punta: **pendientes de runtime**.

**No se considera terminado el relevamiento de inventario ni cerrado el relevamiento global de MyCompany 6.2.**
