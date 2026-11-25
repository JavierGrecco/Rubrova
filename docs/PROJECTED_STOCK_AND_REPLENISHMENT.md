# Stock proyectado y planificación conservadora de reposición

**Revisión:** 25 de noviembre de 2026  
**Estado:** planificador sintético + importador de snapshots + primera API nativa `@@api` de sólo lectura. La API ya exporta hechos de MyCompany 6.2; todavía falta conciliar el resultado con una base real y unirlo con pronóstico y políticas externas. No genera ni confirma órdenes de compra.

Este documento registra la primera regla temporal de reposición de Rubrova. Complementa [Inteligencia de demanda, rentabilidad y marcas](DEMAND_AND_MARGIN_INTELLIGENCE.md) y el [Plan de trabajo](ROADMAP.md). La plataforma operativa sigue siendo MyCompany 6.2 / lsFusion 6.2; este experimento no reemplaza sus ledgers ni su flujo de compras.

## 1. Qué encontramos en MyCompany 6.2

Antes de proponer otro módulo se revisaron las fuentes vendorizadas de inventario y compras:

- `InvLedger.lsf` calcula existencias físicas a partir de entradas y salidas activas, no aceptadas según corresponda (`onHand = inQuantity - outQuantity`).
- `ResLedger.lsf` separa cantidades reservadas positivas y esperadas negativas. El disponible se calcula como existencia menos reservas que participan en `planned`.
- `ShipmentRes.lsf` representa reservas asociadas a líneas de salida pendientes; `ShipmentWaiting.lsf` expone la demanda que aún espera despacho. Para pedidos de venta, `SalesOrderShipment.lsf` aporta el agregado más seguro: `toShip(OrderLine) = max(shippedQuantity - done, 0)`, donde `done` suma lo efectivamente despachado en envíos activos.
- `ReceiptRes.lsf` representa recepciones previstas como cantidades negativas. La propiedad `skipAvailable` permite que una recepción esperada no aumente `available` salvo que el tipo de recepción esté configurado para ello. Por eso no debemos asumir que todo lo que está en una orden de compra ya forma parte del stock disponible.
- `PurchaseOrderShipmentAuto.lsf` ya tiene una rutina de auto pedido: compara disponibilidad previa, envíos pendientes y demanda despachada dentro del período configurado al proveedor; redondea por `purchasePackRatio` y `fillAuto` crea líneas de pedido.

Es importante no duplicar ese mecanismo. El algoritmo existente sirve como punto de comparación, pero no implementa la misma proyección diaria propuesta aquí: su ventana y sus agregados son distintos, la inclusión de recepciones depende de la configuración y el redondeo por pack no equivale por sí solo a un MOQ. Antes de conectarlo con datos reales hay que probar en MyCompany una cesta donde convivan pedidos esperando despacho, reservas parciales, recepciones confirmadas y recepciones vencidas.

## 2. Contrato de datos del experimento

El código está en [plan_replenishment.py](../scripts/replenishment/plan_replenishment.py) y el fixture en [replenishment-planning.json](fixtures/replenishment-planning.json). Las cantidades se expresan en milésimas de unidad (`milli-units`): 1000 equivale a una unidad, igual que la precisión de tres decimales usada por los ledgers de MyCompany.

Cada SKU y ubicación necesita:

- Existencia física actual.
- Pronóstico diario no comprometido, con cobertura y períodos elegibles.
- Lead time del proveedor y período de revisión.
- Stock de seguridad configurado.
- Cantidad mínima de pedido y múltiplo de compra.
- Compromisos de salida abiertos, con fecha, cantidad restante y porción reservada.
- Recepciones de proveedor con fecha prevista y estado.

### 2.1 Reservas y compromisos: regla anti doble conteo

`outgoing.quantityMilli` representa la cantidad todavía pendiente de cumplir, neta de lo que ya se despachó. `outgoing.reservedMilli` es una parte de esa misma cantidad, no una salida adicional.

El cálculo muestra:

`availableNow = onHand - sum(reservedMilli)`

Pero la proyección descuenta una sola vez la cantidad completa del compromiso abierto:

`projectedStock = onHand - outgoingCommitments - forecastDemand + confirmedIncoming`

No hace `onHand - reserved - outgoingCommitments`, porque eso duplicaría la parte reservada. El pronóstico diario recibido por el planificador también debe excluir los compromisos de salida ya listados.

Los identificadores de eventos deben ser únicos dentro de cada lista. Si se repite un ID de recepción o salida, el planificador falla en lugar de sumar dos veces el mismo documento.

### 2.2 Qué suministro se considera

Sólo entran al cálculo las recepciones con estado `confirmed` o `in_transit`, fecha no vencida y entrega dentro del horizonte. Se excluyen los borradores, documentos meramente enviados sin confirmación, anulados, ya recibidos (porque su cantidad debe estar reflejada en la existencia física), vencidos y posteriores al horizonte.

Los compromisos de salida con estado `waiting`, `ready` o `confirmed` se consideran firmes. Los borradores, anulados y ya despachados no se vuelven a descontar. Las salidas posteriores al horizonte no alteran la existencia proyectada de ese período, aunque su parte reservada reduce el disponible inmediato.

## 3. Regla temporal y decisión

El horizonte total es:

`coverageDays = supplierLeadTimeDays + reviewPeriodDays`

Para cada día se descuenta primero la demanda no comprometida y los compromisos de salida; luego se suma la recepción prevista de ese día. Este orden conservador se usa porque el fixture no contiene horas de entrega y despacho.

Al final del período se compara la existencia proyectada con el stock de seguridad:

`reorderGap = max(safetyStock - projectedEndBeforeOrder, 0)`

La sugerencia se redondea hacia arriba respetando el mayor entre el faltante y el MOQ, y luego el múltiplo del proveedor. El pedido sugerido se supone recibido al final del lead time. Por eso se calcula aparte el mínimo intradía anterior a esa fecha: si cae por debajo de cero, el estado pasa a `EXPEDITE_REQUIRED`. Emitir un pedido normal no resolvería un quiebre que ocurriría antes de su llegada.

Estados posibles:

| Estado | Significado |
|---|---|
| `NO_ORDER_NEEDED` | La proyección termina al menos en el stock de seguridad. |
| `ORDER_RECOMMENDED` | La proyección queda por debajo del stock de seguridad y el cálculo puede sugerir cantidad. |
| `EXPEDITE_REQUIRED` | Hay un faltante previsto antes de la llegada de un pedido nuevo; hace falta acelerar, transferir o resolver la causa. |
| `SUPPRESSED` | El historial de demanda no cumple los mínimos de elegibilidad/cobertura. No se sugiere cantidad. |
| `DATA_REVIEW` | Las reservas abiertas superan la existencia física; primero hay que conciliar datos. |

La primera barrera exige al menos 12 períodos elegibles y un porcentaje de cobertura no menor al 50%. Es un umbral operativo conservador para no convertir un pronóstico sin evidencia suficiente en una compra sugerida. No declara que un producto tenga estacionalidad ni que el pronóstico sea preciso.

## 4. Escenarios y pruebas

El fixture contiene seis escenarios sintéticos:

1. Reposición con compromiso de salida, recepción confirmada, MOQ y múltiplo.
2. Caso con cobertura suficiente sin necesidad de compra.
3. Quiebre previsto antes de la llegada del nuevo pedido.
4. Pronóstico con historia/cobertura insuficiente.
5. Reservas superiores a la existencia física.
6. Exclusión de recepciones no confirmadas, canceladas y vencidas.

La suite prueba también IDs duplicados, cantidades inválidas, reservas mayores que su propia línea, compromisos fuera del horizonte, y el caso en que el pronóstico diario es cero pero la historia sí es suficiente. CI valida sintaxis, pruebas unitarias y resultado determinista de los seis escenarios.

## 5. Límites deliberados

- El fixture es 100% sintético; no representa el surtido ni las ventas de una tienda.
- La demanda diaria se distribuye uniformemente. Todavía no hay calendario de apertura, fines de semana, estacionalidad, promociones, cambios de precio, sustitución ni demanda perdida observada.
- El planificador no calcula el stock de seguridad estadístico: lo recibe como política explícita.
- No selecciona proveedor, no estima costos puestos, presupuesto, moneda, financiación, flete ni restricciones de capacidad.
- No hace transferencias entre depósitos ni sustituye productos.
- El planificador no consulta directamente la base de datos MyCompany. La API nativa exporta hechos operativos autenticados a JSON; la normalización y conciliación con pronóstico/políticas siguen siendo etapas separadas.
- No crea, edita, confirma ni envía órdenes de compra y no cambia ventas, reservas, stock o contabilidad.

## 6. Próxima puerta antes de integración

1. Ejecutar la API nativa `Rubrova.rubrovaExportReplenishmentSource` contra una base local MyCompany 6.2 y guardar un snapshot real sin modificar documentos.
2. Demostrar con datos de prueba que una reserva parcial no se cuenta también como demanda pendiente independiente.
3. Conciliar cada recepción prevista con su estado, fecha y cantidad restante; no contar dos veces lo ya recibido.
4. Comparar en paralelo la sugerencia de este experimento con `PurchaseOrderShipmentAuto` por SKU/proveedor/ubicación, documentando diferencias.
5. Incorporar demanda diaria ajustada por disponibilidad sólo cuando su historia y cobertura sean suficientes.
6. Recién después diseñar una vista de planificación con explicación de cada componente. Las compras seguirán requiriendo confirmación humana explícita.

## 8. API nativa de fuente MyCompany 6.2

Se agregó [RubrovaReplenishmentExport.lsf](../extensions/lsfusion/RubrovaReplenishmentExport.lsf), requerido por `RubrovaCustom`. Publica la acción `Rubrova.rubrovaExportReplenishmentSource` con marcador `@@api`. La ruta de ejecución es `/exec/Rubrova.rubrovaExportReplenishmentSource`.

La API está diseñada para ejecutarse con una sesión autenticada. En la configuración de lsFusion, mantener `enableAPI=0`: en ese modo no se habilita la ejecución arbitraria de código y sólo se aceptan acciones marcadas `@@api` por usuarios autorizados. No habilitar `enableAPI=2` para esta integración. El consumidor local debe usar la sesión autorizada y no exponer el endpoint a Internet.

La respuesta es un documento `mycompany-replenishment-source-export`, diferente del snapshot normalizado que consume el planificador. Contiene tres colecciones independientes:

| Colección | Contenido |
|---|---|
| `inventory` | Una fila por producto/ubicación con movimientos o reservas: entradas/salidas físicas, `onHand`, `grossReserved`, `plannedNetReservation`, `expectedInbound` y `available` nativo. |
| `outgoingCommitments` | Una fila por línea de pedido confirmada: `Sales.toShip(OrderLine)`, reserva efectiva agregada desde `ShipmentResLedger.lineReserved`, documento, ubicación y fecha. |
| `receipts` | Filas de `ReceiptResLedger` listas, no realizadas y vinculadas a órdenes de compra confirmadas; incluye remanente, fecha e indicador `increaseAvailableStock`. |

Las cantidades se exportan en la unidad del SKU, conservando tres decimales de MyCompany; no se convierten silenciosamente a milésimas ni se agregan ubicaciones jerárquicas. El disponible sale directamente de `Inventory.available(Location, Product)`; `plannedNetReservation` conserva el saldo firmado que participa en ese cálculo. La colección de recepciones conserva `increaseAvailableStock` incluso cuando es verdadero: la etapa normalizadora debe aplicar la política y, por ahora, el importador existente continúa bloqueando ese caso.

**Límite deliberado:** esta primera API no inventa pronóstico diario, períodos elegibles, lead time, stock de seguridad, MOQ ni múltiplos. Esos datos no salen de los ledgers y deben provenir de la capa de planificación/configuración. Por eso la respuesta nativa todavía no se puede pasar directamente a `import_mycompany_snapshot.py`, cuyo contrato exige además `planningInputs` normalizados.

El test de runtime autenticado comprueba el esquema, la unicidad de identidades, la restricción de reservas por línea y la identidad `available = onHand - plannedNetReservation`. Es una comprobación contra la instancia efímera de CI; no reemplaza la conciliación pendiente contra una base MyCompany local con datos reales.

Referencias funcionales para contraste: [Odoo — reglas de reabastecimiento](https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/inventory/warehouses_storage/replenishment/reordering_rules.html) y [ERPNext — cantidad proyectada](https://docs.frappe.io/erpnext/projected-quantity).

## 7. Adaptador de snapshots MyCompany 6.2

Se agregó [import_mycompany_snapshot.py](../scripts/replenishment/import_mycompany_snapshot.py), con un ejemplo sintético en [mycompany-replenishment-snapshot.json](fixtures/mycompany-replenishment-snapshot.json). El adaptador convierte una extracción JSON en entradas del planificador y devuelve un reporte por producto/ubicación. No conoce credenciales, no tiene cliente PostgreSQL/RMI/HTTP y no abre una sesión lsFusion: sólo lee el archivo entregado por el operador.

El contrato de entrada exige MyCompany 6.2 y una declaración explícita de semántica para impedir que una columna con nombre parecido se interprete como otra magnitud:

| Campo del snapshot | Origen/semántica requerida |
|---|---|
| inventory.onHandMilli | InvLedger.onHand para una ubicación exacta, no un agregado jerárquico |
| outgoingCommitments.sourceLineId | ID de Sales.OrderLine; identidad única del compromiso |
| outgoingCommitments.sourceDocumentId | ID de Sales.Order |
| outgoingCommitments.openQuantityMilli | Sales.toShip(OrderLine) de un pedido confirmado, neto de las cantidades ya despachadas |
| outgoingCommitments.lineReservedMilli | Suma de ShipmentResLedger.lineReserved por OrderLine, es decir, reserva efectiva después de ledgerReserved |
| outgoingCommitments.scheduledDate | Sales.Order.scheduledDateTime |
| outgoingCommitments.relatedShipmentCount | Cantidad de documentos Shipment vinculados a la línea; metadato para auditar parciales, no cantidad a sumar |
| receipts.expectedQuantityMilli | Cantidad aún pendiente de recepción representada por ReceiptResLedger |
| receipts.scheduledDate | Receipt.scheduledDateTime |
| planningInputs.nativeAutoOrderQtyMilli | Valor leído de PurchaseOrderShipmentAuto.toOrderPeriodic, si se exporta |

**Despachos y parciales.** La unidad de exportación es una línea de pedido de venta, no cada `ShipmentLine`. En `SalesOrderShipment.lsf`, `done(OrderLine)` agrega las cantidades despachadas de envíos activos y `toShip(OrderLine)` calcula la cantidad aún pendiente. Además, `ShipmentReady.shipPartially` crea una línea residual en otro documento, mientras `SalesOrderShipment.overShipPartially` conserva el vínculo con la misma `OrderLine`. Por lo tanto, exportar cada documento como una demanda independiente puede duplicar la obligación de entrega. La extracción nativa debe emitir una sola fila por `Sales.OrderLine.id`, con `openQuantityMilli = Sales.toShip(OrderLine)` y `lineReservedMilli` como suma de `ShipmentResLedger.lineReserved` asociada a esa línea. `relatedShipmentCount` sólo ayuda a auditar cuántos documentos participan; no se suma como cantidad. El adaptador rechaza IDs de líneas de pedido duplicados y reservas superiores al remanente.

**Compras y recepciones.** PurchaseOrderReceipt crea/actualiza una Receipt en estado ready para una orden confirmada, copia scheduledDateTime y establece la cantidad de cada línea en toReceive, que descuenta lo ya recibido. El adaptador incluye sólo líneas ready vinculadas a una orden confirmada y una vez por purchaseOrderLineId. Una Receipt done ya debe estar reflejada en onHand y se excluye; las órdenes en draft/sent/cancelled también se excluyen. Las recepciones cuyo tipo usa increaseAvailableStock=true se rechazan en esta versión, porque MyCompany puede incorporarlas al available antes de la recepción física y el planificador aún no reproduce esa política. No se oculta esa diferencia ni se aproxima con una cifra.

**Comparación contra la rutina nativa.** El campo nativeAutoOrderQtyMilli es opcional y representa una lectura de toOrderPeriodic tomada desde MyCompany en el mismo contexto de proveedor, ubicación y fecha. El adaptador calcula la diferencia contra la cantidad sugerida por Rubrova cuando el planificador tiene historia suficiente. No invoca fillAuto ni crea líneas de orden. La comparación sólo será válida con valores capturados del runtime; los números de la fixture son ilustrativos.

La CI compila ambos módulos, ejecuta las pruebas del adaptador y corre el CLI contra el snapshot de ejemplo. Las pruebas cubren reservas parciales, despacho residual, recepción confirmada, recepción ya hecha, borrador, orden enviada, IDs duplicados, líneas de compra duplicadas, semántica incompatible y el caso increaseAvailableStock.

**Límite actual:** el archivo de ejemplo es sintético. El contrato ya consolida compromisos por línea de pedido usando las propiedades nativas identificadas, pero todavía no existe una exportación real desde MyCompany ni se ha conciliado una muestra tomada de su base. Por tanto, esta entrega valida el contrato de intercambio y sus protecciones, no afirma que el snapshot ya pueda extraerse del runtime productivo. El siguiente paso es implementar el endpoint/reporte nativo de sólo lectura y contrastar sus cantidades contra las propiedades originales, antes de usar el planificador en una decisión comercial.
