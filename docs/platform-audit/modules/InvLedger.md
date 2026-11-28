# Ficha de integración — InvLedger


**Fuente fijada:** MyCompany 6.2 · commit d21ca6978717b98b6300d90267f9767db7414008  
**Composición:** dentro del cierre actual de RubrovaCustom, según el catálogo estructural.  
**Evidencia:** lectura de fuente estática; no equivale a runtime, conciliación ni aceptación.

**Identificador real:** MODULE InvLedger · **Namespace:** Inventory  
**Fuente:** [InvLedger.lsf](../../../vendor/mycompany/src/main/lsfusion/inventory/ledgers/inv/InvLedger.lsf#L1-L113)  
**Dossier:** [Inventario, reservas y costos](../MYCOMPANY_6_2_INVENTORY_LEDGER_MAP.md) §§1.1, 3, 4 y 8.

## 1. Resumen de 2 minutos

InvLedger es el contrato abstracto del **movimiento físico de inventario**. No es el documento de recepción o despacho ni representa reservas ni costo. Define qué atributos aporta cada movimiento y cómo se calculan ingresos, egresos y saldo físico por producto y ubicación.

**REQUIRE directos:** InventorySettings, Category, Product, Location, Partner, Time.

**Consumidores directos detectados:** Inventory, Adjustment, InvLedgerAPI, InvLedgerItem, InvLedgerLot, ResLedger, ReceiptImport, ReceiptInv, InventoryReport, ProductMoves, Scrap, ScrapInv, ShipmentInv, ShipmentWaiting, ManufacturingOrderBulkCreate, ManufacturingOrderInv, SalesPricelistPrintInventory y SalesPriceReportInventory. Confirmar las rutas exactas con el buscador antes de modificar.

## 2. Responsabilidad y autoridad

- Posee la semántica común del movimiento físico: fecha/hora, número, tipo, producto, cantidad, socio, ubicación origen/destino, activo y aceptación pendiente.
- No posee el flujo completo de recepción, despacho, ajuste, merma o fabricación. Esos módulos producen/extienden los registros concretos.
- No posee el ledger de reservas ni el ledger de costos.
- No crear un saldo editable paralelo ni escribir directamente sobre las tablas físicas de los documentos productores.

## 3. Modelo de datos

La clase principal es ABSTRACT InvLedger. Sus propiedades son abstractas y materializadas; los productores implementan sus valores.

| Propiedad | Semántica |
|---|---|
| type | Tipo de movimiento |
| active | Define si participa en los cálculos |
| notAccepted | Excluye un ingreso pendiente de aceptación |
| dateTime, number | Fecha/hora y número |
| fromLocation, toLocation | Ubicación de origen y destino |
| product, quantity | Producto y cantidad; NUMERIC[16,3] |
| partner | Socio relacionado |

Índices declarados: por producto; por ubicación de origen/producto/fecha; y por ubicación destino/producto/fecha.

## 4. Cálculo del saldo

- **Ingreso:** suma quantity si active, no notAccepted, coincide toLocation y producto.
- **Egreso:** suma quantity si active, coincide fromLocation y producto.
- **Existencia física:** onHand = inQuantity - outQuantity.
- **Jerarquía:** onHandRec agrega los saldos de ubicaciones descendientes.
- **Histórico:** existen variantes temporales con límites distintos: una resta registros con fecha mayor que dt; otra resta registros con fecha mayor o igual. Al cambiar reportes históricos, respetar la frontera inclusiva/exclusiva.
- **Última recepción:** se excluyen movimientos inactivos o pendientes de aceptación.

La restricción positiveOnHand puede impedir un saldo físico negativo. La configuración se hereda por la jerarquía de ubicaciones y se aplica mediante una constraint; no basta con ocultar una acción en la UI.

## 5. Casos de uso y productores

| Caso | Productor/flujo que se debe seguir | Efecto a verificar |
|---|---|---|
| Recepción | Receipt → ReceiptDone → ReceiptInv | Entrada física una sola vez |
| Despacho/venta | Shipment → ShipmentDone → ShipmentInv | Salida física al completar, no al crear el pedido |
| Traslado | Shipment + aceptación en destino | Salida de origen y entrada a destino; pendiente no computa |
| Ajuste/conteo | Adjustment → AdjustmentDone → AdjustmentInv | Diferencia física registrada |
| Merma | Scrap → ScrapInv | Baja física y vínculo con costo/lote si aplica |
| Fabricación | ManufacturingOrderInv | Consumo/entrada según el contrato de la orden |

## 6. Integración y comunicación

- Los productores extienden las propiedades abstractas de InvLedger; esa es la frontera interna de comunicación de lsFusion.
- InvLedgerAPI es un consumidor directo, pero esta ficha no certifica endpoint, autenticación, esquema, filtros ni alcance de escritura. Revisar su fuente y el mapa lsFusion antes de integrarlo externamente.
- REQUIRE no equivale a relación comercial: la relación de negocio se documenta por documento origen, documento derivado y ledger.

## 7. Estados, permisos y riesgos

- active y notAccepted determinan la participación en el saldo; no son sinónimos del estado visual del documento.
- La aceptación de destino depende de permisos de ubicación y la implementa el módulo de aceptación del traslado.
- La restricción de saldo negativo se configura por ubicación y se hereda.
- Editar/cancelar el documento productor debe dejar coherentes los movimientos que generó. No modificar el ledger como sustituto de cancelar o revertir su documento.

## 8. Pruebas mínimas antes de integrar

1. Ingreso y egreso del mismo producto/ubicación.
2. Dos ubicaciones, jerarquía padre/hija y consulta agregada.
3. Traslado con aceptación pendiente y aceptación por usuario con acceso destino.
4. Movimiento cancelado/inactivo y efecto en el saldo.
5. Saldo negativo permitido/prohibido, incluyendo herencia.
6. Consultas históricas justo antes, en y después del instante dt.
7. Cancelación/reversión de productores y conciliación documento↔ledger.

**Estado de aceptación:** pendiente. No hay evidencia aquí de runtime ni conciliación E2E.

## 9. Lecturas siguientes obligatorias

- [ResLedger](ResLedger.md) y [CostLedger](CostLedger.md): ledgers complementarios, no intercambiables.
- [Receipt](Receipt.md) y dossier de inventario §2.
- Dossier de inventario §§3–5 para despacho, ajuste, lotes y costos.
- [Datos maestros](../MYCOMPANY_6_2_MASTERDATA_RELATIONSHIPS_MAP.md) para Product, Location y Partner.
- [Capacidades lsFusion](../LSFUSION_6_2_CAPABILITY_MAP.md) y [guía de integración](../../ENGINEERING_MASTER.md#b-integration).

**Definición de terminado:** no se aprueba una integración que calcule existencias al margen de los productores y de este contrato.
