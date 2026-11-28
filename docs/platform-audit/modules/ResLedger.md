# Ficha de integración — ResLedger


**Fuente fijada:** MyCompany 6.2 · commit d21ca6978717b98b6300d90267f9767db7414008  
**Composición:** dentro del cierre actual de RubrovaCustom, según el catálogo estructural.  
**Evidencia:** lectura de fuente estática; no equivale a runtime, conciliación ni aceptación.

**Identificador real:** MODULE ResLedger · **Namespace:** Inventory  
**Fuente:** [ResLedger.lsf](../../../vendor/mycompany/src/main/lsfusion/inventory/ledgers/res/ResLedger.lsf#L1-L85)  
**Dossier:** [Inventario, reservas y costos](../MYCOMPANY_6_2_INVENTORY_LEDGER_MAP.md) §§1.2, 2.2, 3.2 y 8.

## 1. Resumen de 2 minutos

ResLedger registra **reservas, entradas esperadas y cantidades planificadas** y calcula el disponible como saldo físico menos planificación. Requiere InvLedger; no reemplaza el movimiento físico.

**REQUIRE directo:** InvLedger.

**Consumidores directos:** Inventory, ResLedgerItem, Receipt, ReceiptReady, InventoryReport, ScrapSearch, Shipment, ShipmentReady, ShipmentRes, ManufacturingOrderReady, ManufacturingOrderRes, PurchaseOrderSearch y SalesOrderSearch.

## 2. Responsabilidad y autoridad

- Posee la semántica común de cantidades reservadas y esperadas por producto/ubicación.
- Consume el saldo físico de InvLedger para calcular el disponible.
- No completa una recepción o despacho ni crea un movimiento físico.
- Pedido, recepción esperada, reserva, cantidad preparada y saldo físico son hechos diferentes.

## 3. Modelo de datos y signo

La clase ResLedger declara propiedades abstractas materializadas: dateTime, number, type, location, product, reserved, partner y skipAvailable.

- reserved > 0 representa cantidad reservada.
- reserved < 0 representa cantidad esperada; expected suma su valor absoluto.
- reserved(Location, Product) agrega sólo valores positivos.
- planned suma reserved cuando skipAvailable no está activo.
- available = onHand - planned.
- Hay agregaciones por ubicación padre que incluyen descendientes.

**No invertir el signo** al integrar una entrada esperada. No sumar la expectativa como inventario físico.

## 4. Casos de uso

| Caso | Productor | Efecto |
|---|---|---|
| Recepción planificada | Receipt / ReceiptReady / ReceiptRes | Esperado negativo; el tipo puede excluirlo del disponible |
| Despacho en espera/listo | ShipmentReady / ShipmentRes | Reserva positiva, según disponibilidad |
| Liberar/cancelar reserva | Acciones del documento productor | La reserva deja de afectar disponible |
| Fabricación | ManufacturingOrderReady / ManufacturingOrderRes | Consumo/abastecimiento reservado según configuración |
| Consulta | Inventory, búsquedas/reportes de compras y ventas | Expone disponible y esperado sin confundirlos con físico |

## 5. Comunicación y contrato

ResLedger depende directamente de InvLedger y utiliza onHand/onHandRec para calcular disponible. Los productores extienden las propiedades abstractas del ledger. No se identifica aquí un endpoint externo propio.

La configuración positiveAvailable puede impedir que el disponible sea negativo. Se hereda por jerarquía de ubicaciones. La validación es una constraint del servidor; no reemplazarla por una validación sólo visual.

## 6. Riesgos de integración

- skipAvailable no significa “no existe”: la fila puede seguir representando una reserva/esperado aunque no afecte disponible.
- La expectativa puede ser visible aunque no mejore disponible.
- Una reserva cancelada o liberada debe retirarse sin generar movimiento físico inverso.
- No dejar la misma cantidad reservada después de completar y volver a reservarla por un documento derivado sin una transición explícita.
- Picking/preparación no es automáticamente igual a reservado ni despachado.

## 7. Pruebas mínimas

1. Reserva positiva reduce disponible.
2. Reserva negativa aparece como esperado y no aumenta onHand.
3. skipAvailable no altera disponible y conserva su clasificación.
4. Liberar, cancelar y completar documentos transforma/libera reservas correctamente.
5. Restricción de disponible negativo con herencia de ubicación.
6. Agregación padre/hijo.
7. Conciliación pedido↔reserva↔despacho↔ledger físico.

**Estado de aceptación:** pendiente de pruebas runtime y conciliación.

## 8. Lecturas siguientes

- [InvLedger](InvLedger.md): saldo físico consumido por este ledger.
- [Receipt](Receipt.md) y [mapa de inventario](../MYCOMPANY_6_2_INVENTORY_LEDGER_MAP.md) §§2–3.
- [Ventas](../MYCOMPANY_6_2_SALES_PRICING_LEDGER_MAP.md) §2 y [compras](../MYCOMPANY_6_2_PURCHASE_REPLENISHMENT_MAP.md) §2.
- [Datos maestros](../MYCOMPANY_6_2_MASTERDATA_RELATIONSHIPS_MAP.md) para producto y ubicación.
- [Capacidades lsFusion](../LSFUSION_6_2_CAPABILITY_MAP.md) para restricciones y propiedades abstractas.

**Definición de terminado:** ninguna integración deriva el disponible directamente de cantidades de pedidos sin respetar ResLedger.
