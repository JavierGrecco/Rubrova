# Ficha de integración — CostLedger


**Fuente fijada:** MyCompany 6.2 · commit d21ca6978717b98b6300d90267f9767db7414008  
**Composición:** dentro del cierre actual de RubrovaCustom, según el catálogo estructural.  
**Evidencia:** lectura de fuente estática; no equivale a runtime, conciliación ni aceptación.

**Identificador real:** MODULE CostLedger · **Namespace:** Inventory  
**Fuente:** [CostLedger.lsf](../../../vendor/mycompany/src/main/lsfusion/inventory/ledgers/cost/CostLedger.lsf#L1-L200)  
**Dossier:** [Inventario, reservas y costos](../MYCOMPANY_6_2_INVENTORY_LEDGER_MAP.md) §1.3 y apartados de recepción, despacho, ajuste y pruebas.

## 1. Resumen de 2 minutos

CostLedger es la autoridad de valoración/costo por producto y ubicación. Separa entradas y salidas de costo, calcula cantidades/importes firmados y soporta costo planificado/estándar, AVCO y FIFO. No es el ledger de existencia física.

**REQUIRE directos:** Location, Product, Utils, CostProduct, ItemCost.

**Consumidores directos:** Inventory, AdjustmentCost, ReceiptCost, CostLedgerReport, InventoryValuation, ScrapCost, ShipmentCost, ManufacturingOrderCost y SalesPricelist.

## 2. Modelo de datos

Clases declaradas: CostLedger, InCostLedger y OutCostLedger.

- InCostLedger representa entradas: fecha/hora, ubicación, producto, cantidad e importe informado/calculado.
- OutCostLedger representa salidas: fecha/hora, ubicación, producto, cantidad e importe.
- CostLedger unifica ambas familias mediante propiedades MULTI.
- signedQuantity/signedAmount asignan signo positivo a entradas y negativo a salidas.
- costQuantity, costAmount y costPrice agregan cantidades, importes y costo unitario.
- Cantidad: NUMERIC[16,3]. Importes: NUMERIC[14,2].

## 3. Casos de uso y comunicación

| Caso | Módulo productor/consumidor | Qué verificar |
|---|---|---|
| Recepción | ReceiptCost | Entrada de costo asociada a cantidad recibida y recepción activa |
| Despacho | ShipmentCost | Consumo de costo por ubicación/producto y cantidad efectiva |
| Ajuste | AdjustmentCost | Diferencias y valorización |
| Merma | ScrapCost | Baja física y de costo coherentes |
| Fabricación | ManufacturingOrderCost | Consumo, producto terminado y costo |
| Consulta | CostLedgerReport, InventoryValuation | Conciliación y costo unitario histórico |
| Precio de venta | SalesPricelist | Costo de referencia no equivale a precio ni margen |

El costo planificado de ItemCost y el método de valuación de CostLedger son conceptos relacionados, pero no equivalentes. Seguir CostProduct, categoría y configuración del producto antes de modificar cómo se obtiene un precio.

## 4. Algoritmos y configuración

El cálculo distingue:
- **standardPrice:** valúa entradas/salidas desde el costo del artículo vigente a la fecha.
- **avco:** calcula monto de salida a partir del costo promedio.
- **fifo:** distribuye la cantidad de salida contra capas de entradas y suma cantidad consumida × precio de cada entrada.

La fuente agrupa movimientos por producto y los procesa ordenados por fecha/hora. En las dos ramas de asignación FIFO aparece comentada la condición dateTime(il) <= dateTime(ol). El dossier registra el riesgo de que una salida histórica consuma una entrada posterior. **Es una observación de código que requiere reproducción; no se declara aquí un defecto confirmado.**

El recálculo puede partir de una fecha y limitarse por ubicación/producto. Utiliza NEWSESSION NESTED, marca registros a recalcular, ejecuta calculateCost() y termina con APPLY.

## 5. Riesgos y límites

- No modificar importes de costo para “corregir” un saldo físico.
- No asumir que todas las salidas usan el mismo método.
- No recalcular sin definir fecha inicial, alcance de ubicaciones/productos y efecto histórico.
- No confundir costo del artículo, costo promedio, FIFO, precio de venta o margen.
- Orden de movimientos fuera de secuencia y concurrencia requieren pruebas.
- Permisos efectivos de recálculo deben comprobarse en runtime.

## 6. Pruebas mínimas

1. Costo estándar con cambio de costo planificado.
2. AVCO con varias entradas y salidas parciales.
3. FIFO: entrada 10/04, salida 12/04 y entrada posterior 15/04; la salida del 12/04 no debería consumir la entrada del 15/04.
4. Movimientos fuera de orden y recálculo desde distintas fechas.
5. Varias ubicaciones físicas con una ubicación de costo común.
6. Recepción parcial, despacho parcial, ajuste, merma y fabricación.
7. Conciliación entre cantidad/importe de ledger y valuación/reportes.

**Estado de aceptación:** pendiente. La prueba FIFO es un riesgo abierto que bloquea declarar la valuación aceptada.

## 7. Lecturas siguientes

- [InvLedger](InvLedger.md) para movimiento físico y [ResLedger](ResLedger.md) para reservas/disponible.
- [Datos maestros](../MYCOMPANY_6_2_MASTERDATA_RELATIONSHIPS_MAP.md) §§4–7.
- [Compras](../MYCOMPANY_6_2_PURCHASE_REPLENISHMENT_MAP.md), [ventas](../MYCOMPANY_6_2_SALES_PRICING_LEDGER_MAP.md) y [facturación](../MYCOMPANY_6_2_INVOICING_LEDGER_MAP.md).
- [Seguridad](../../SECURITY_AND_AUDIT.md) y [continuidad operativa](../../OPERATIONAL_RESILIENCE_AND_RECOVERY.md).

**Definición de terminado:** margen, rentabilidad, valuación y recomendaciones no sustituyen este costo transaccional ni escriben sobre el ledger desde analítica.
