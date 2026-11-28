# MyCompany 6.2 / lsFusion 6.2 — directorio de integración por módulo

**Objetivo:** que una persona pueda empezar por el nombre exacto del módulo que va a modificar y llegar, en una lectura corta, al documento, entidades, secuencia de uso, dependencias, contratos, efectos y pruebas que debe respetar. Este directorio es el **router obligatorio por módulo**; los dossiers de dominio continúan siendo la explicación funcional profunda y el Manual técnico sigue siendo la fuente de verdad sobre decisiones/evidencia.

**Alcance:** primera versión de navegación integrada para los módulos de mayor impacto transaccional y transversal. No es una declaración de que las 800 fichas individuales estén completas. Los módulos sin una ruta manual específica se resuelven mediante el buscador automático y el mapa de dominio que devuelve.

## 1. Cómo usarlo — ruta de 5 minutos

1. Buscar el **nombre exacto declarado en `MODULE`**, no adivinarlo por el nombre del archivo.
2. Abrir la columna **Primera lectura obligatoria**. Esa sección es el punto de entrada para comprender el circuito.
3. Leer la columna **Seguir con** antes de modificar. Esas dependencias suelen ser necesarias para no romper el dato o ledger dueño.
4. Consultar el archivo LSF indicado, sus `REQUIRE` y sus consumidores directos. El registro estructural detecta composición; no demuestra el comportamiento completo.
5. Antes de programar, abrir la [plantilla obligatoria de ficha de integración](MODULE_INTEGRATION_PASSPORT_TEMPLATE.md). Si el cambio revela una relación, estado, contrato o efecto que no esté en el dossier, completar o ampliar la ficha y actualizar el directorio.

### Consulta automática para cualquiera de los módulos del snapshot

Desde la raíz del repositorio:

```bash
node scripts/platform/module-integration-route.mjs --module InvLedger
node scripts/platform/module-integration-route.mjs --module Receipt
node scripts/platform/module-integration-route.mjs --module NombreExactoDelModulo
```

El comando resuelve los 856 módulos del snapshot (800 MyCompany, 49 lsFusion y 7 extensiones Rubrova). Devuelve: archivo fuente, versión fijada, estado dentro/fuera del cierre de `RubrovaCustom`, namespace, `REQUIRE` directos con sus rutas, consumidores directos con sus rutas, declaraciones estructurales detectadas, ficha individual si existe, dossier de dominio y lecturas transversales. Acepta nombre `MODULE`, basename `.lsf` o ruta exacta. Si el módulo no está en la composición, lo advierte; nunca debe asumirse que puede usarse sin incorporarlo y probarlo.

El [registro estructural completo de módulos](../../.github/workflows/documentation-map.yml) se regenera en CI como artefacto de 30 días. El CLI es la ruta persistente y repetible para consultar cualquier módulo del snapshot sin depender de que una persona conserve ese artefacto.

### 1.1 Cobertura de fichas individuales — estado real

Las **86 entradas manuales** de este directorio son rutas rápidas por módulo con fuente exacta, primera lectura y relaciones. No deben interpretarse como 86 pasaportes individuales completos.

Ya hay **veintidós fichas individuales** con análisis específico:

| Módulo | Pasaporte individual | Qué concentra |
|---|---|---|
| InvLedger | [Ficha InvLedger](modules/InvLedger.md) | Contrato de movimiento físico, saldos, ubicación, aceptación y productores |
| ResLedger | [Ficha ResLedger](modules/ResLedger.md) | Signo de reservas/esperados, disponible, skipAvailable y productores |
| CostLedger | [Ficha CostLedger](modules/CostLedger.md) | Costos estándar, AVCO, FIFO, recálculo y riesgo temporal |
| Receipt | [Ficha Receipt](modules/Receipt.md) | Cabecera/líneas, validaciones y circuito recepción→reserva→movimiento→costo |
| SalesOrder | [Ficha SalesOrder](modules/SalesOrder.md) | Pedido, entidades, estados y documentos derivados |
| Session | [Ficha Session](modules/Session.md) | Apertura/cierre, hooks, POS y asociación de documentos |
| PurchaseOrder | [Ficha PurchaseOrder](modules/PurchaseOrder.md) | Pedido de compra, proveedor, parciales y documentos derivados |
| Invoice | [Ficha Invoice](modules/Invoice.md) | Factura de venta, deuda, cobros y notas de crédito |
| Bill | [Ficha Bill](modules/Bill.md) | Factura proveedor, costos, deuda y pagos |
| Pos | [Ficha Pos](modules/Pos.md) | Caja lógica, empresa, computadora y controladores |
| Product | [Ficha Product](modules/Product.md) | Maestro físico, Item, unidades, variantes, barcode y lotes |
| Partner | [Ficha Partner](modules/Partner.md) | Identidad común y especializaciones legales/comerciales |
| Bom | [Ficha Bom](modules/Bom.md) | Estructura, componentes, subproductos, BOM anidada y operaciones |
| ManufacturingOrder | [Ficha ManufacturingOrder](modules/ManufacturingOrder.md) | Documento, estados, reservas, inventario, lotes y costo |
| WorkCenter | [Ficha WorkCenter](modules/WorkCenter.md) | Maestro de centro y límites de capacidad |
| WorkOrder | [Ficha WorkOrder](modules/WorkOrder.md) | Routing, operaciones, duración y estados |
| Project | [Ficha Project](modules/Project.md) | Contexto de proyecto, estado y documentos relacionados |
| ProjectAssignment | [Ficha ProjectAssignment](modules/ProjectAssignment.md) | Miembros, roles, vigencia y acceso |
| TimeEntry | [Ficha TimeEntry](modules/TimeEntry.md) | Registro común de horas |
| ProjectTimeEntry | [Ficha ProjectTimeEntry](modules/ProjectTimeEntry.md) | Horas por proyecto, filtros y obligatoriedad |
| ProjectManufacturingOrder | [Ficha ProjectManufacturingOrder](modules/ProjectManufacturingOrder.md) | Proyecto asociado a orden de fabricación |
| ProjectManufacturingOrderTimeEntry | [Ficha ProjectManufacturingOrderTimeEntry](modules/ProjectManufacturingOrderTimeEntry.md) | Horas imputadas a la orden y costo laboral |

Los otros módulos siguen teniendo una ruta al dossier de dominio y al CLI, pero no una ficha individual aprobada. Ante una integración que modifique su modelo, estado, API, permisos o efectos, completar el [pasaporte de módulo](MODULE_INTEGRATION_PASSPORT_TEMPLATE.md) y enlazarlo aquí antes de considerar terminado el cambio. La herramienta no inventa casos de uso ni convierte un inventario estructural en documentación funcional.

## 2. Reglas para interpretar la ruta

- **Módulo raíz/compositor:** agrupa `REQUIRE` y composición; no es necesariamente dueño de los datos.
- **Módulo de documento:** define cabecera/líneas, propiedades y validaciones de la operación.
- **Módulo de estado/acción:** agrega una transición o efecto al documento base. No duplicar ni saltar la transición nativa.
- **Módulo de ledger:** registra hechos financieros, físicos, reservas o costos. No escribir sus tablas ni recalcular saldos por fuera del propietario.
- **Módulo de interfaz:** ofrece interacción; no necesariamente posee reglas ni datos.
- **Módulo de API/adaptador:** publica/transforma datos y debe respetar el dueño de origen, permisos, esquema, idempotencia y conciliación.
- **`REQUIRE` no equivale a relación comercial:** seguir por separado el grafo de dependencias de código y las relaciones de documento/ledger.
- **Fuera de `RubrovaCustom`:** módulo identificado, pero no declarado activo en la composición actual. No se usa sólo porque exista en `vendor/`.

### Estados de cobertura

| Estado | Qué permite afirmar |
|---|---|
| **Dossier de fuente parcial** | Hay análisis de fuente en el dossier; sus pendientes siguen abiertos. |
| **Fuentes del dominio leídas** | Se revisaron las fuentes LSF que declara el dossier; runtime y conciliación pueden seguir pendientes. |
| **Ruta documental** | Se sabe dónde investigar, pero no hay ficha funcional propia suficiente. |
| **Fuera de composición** | El módulo está fuera del cierre actual; requiere decisión explícita antes de activarlo. |
| **Runtime verificado / conciliado / aceptado** | Sólo cuando el dossier y la evidencia adjunta lo declaran expresamente para el escenario/configuración concreta. |

Nunca convertir “fuente leída” en “integración aceptada”.

## 3. Directorio rápido por módulo exacto

Los enlaces de fuente apuntan al archivo LSF fijado en el snapshot de MyCompany. La primera lectura indica el apartado que explica el circuito; **seguir con** enumera las dependencias de conocimiento que hacen falta para una integración correcta.

### 3.1 Inventario, recepciones, despachos, reservas y costos

**Dossier primario:** [Mapa de inventario, reservas y costos](MYCOMPANY_6_2_INVENTORY_LEDGER_MAP.md).  
**Cobertura declarada:** análisis de fuentes parcial; pruebas de runtime y conciliación pendientes.

| Módulo exacto | Fuente LSF | Primera lectura obligatoria | Seguir con / relaciones que no se deben romper |
|---|---|---|---|
| `Inventory` | [Inventory.lsf](../../vendor/mycompany/src/main/lsfusion/inventory/Inventory.lsf) | Dossier §1 y mapa funcional | Es compositor del dominio. Seguir `Receipt`, `Shipment`, `Adjustment`, `Scrap`, `InvLedger`, `ResLedger`, `CostLedger`, `Location`, reportes y master data. |
| `InvLedger` | [InvLedger.lsf](../../vendor/mycompany/src/main/lsfusion/inventory/ledgers/inv/InvLedger.lsf) | [Ficha InvLedger](modules/InvLedger.md) → dossier §1.1 | Distinguir ingreso/egreso físico, ubicación origen/destino, activo, `notAccepted`, corte temporal y agregación. Seguir `ReceiptInv`, `ShipmentInv`, `AdjustmentInv`, `ScrapInv` y aceptación. |
| `ResLedger` | [ResLedger.lsf](../../vendor/mycompany/src/main/lsfusion/inventory/ledgers/res/ResLedger.lsf) | [Ficha ResLedger](modules/ResLedger.md) → dossier §1.2 | Separar reserva positiva, esperado negativo, bruto, planificado, `skipAvailable` y disponible. Seguir `ReceiptRes`, `ShipmentReady`, `ShipmentRes`, ventas y reposición. |
| `CostLedger` | [CostLedger.lsf](../../vendor/mycompany/src/main/lsfusion/inventory/ledgers/cost/CostLedger.lsf) | [Ficha CostLedger](modules/CostLedger.md) → dossier §1.3 | No confundir costo planificado, AVCO, FIFO y movimiento físico. Seguir `ReceiptCost`, `ShipmentCost`, `AdjustmentCost`, `CostLocation`, `CostProduct` e informes; atender el riesgo FIFO anotado en el dossier. |
| `CostLocation` | [CostLocation.lsf](../../vendor/mycompany/src/main/lsfusion/inventory/ledgers/cost/CostLocation.lsf) | Dossier §1.3 | La ubicación de costo puede agrupar ubicaciones físicas; revisar herencia y jerarquía antes de conciliar. |
| `CostProduct` | [CostProduct.lsf](../../vendor/mycompany/src/main/lsfusion/inventory/ledgers/cost/CostProduct.lsf) | Dossier §1.3 | Seguir categoría, producto y `ItemCost`; costo de maestro no equivale necesariamente a valoración real. |
| `Receipt` | [Receipt.lsf](../../vendor/mycompany/src/main/lsfusion/inventory/receipts/Receipt.lsf) | [Ficha Receipt](modules/Receipt.md) → dossier §2.1 | Seguir `ReceiptType`, `ReceiptReady`, `ReceiptDone`, `ReceiptRes`, `ReceiptInv`, `ReceiptCost`, `ReceiptPutAway`, `PurchaseOrderReceipt`, `Bill` y master data. |
| `ReceiptType` | [ReceiptType.lsf](../../vendor/mycompany/src/main/lsfusion/inventory/receipts/ReceiptType.lsf) | Dossier §§2.1–2.5 | La configuración puede alterar numeración, ubicación y comportamiento; revisar `increaseAvailableStock` y `putAway` en los módulos que la consumen. |
| `ReceiptReady` | [ReceiptReady.lsf](../../vendor/mycompany/src/main/lsfusion/inventory/receipts/ReceiptReady.lsf) | Dossier §2.2 | Estado listo y reserva esperada; seguir `ResLedger`, selección, cancelación y cierre. |
| `ReceiptDone` | [ReceiptDone.lsf](../../vendor/mycompany/src/main/lsfusion/inventory/receipts/ReceiptDone.lsf) | Dossier §2.3 | Cantidad real recibida y fecha/hora efectiva; seguir `ReceiptInv`, `ReceiptRes`, `ReceiptCost` y put-away. |
| `ReceiptRes` | [ReceiptRes.lsf](../../vendor/mycompany/src/main/lsfusion/inventory/receipts/ReceiptRes.lsf) | Dossier §2.2 | Esperado con signo negativo y política de disponible; no sumar como stock físico. |
| `ReceiptInv` | [ReceiptInv.lsf](../../vendor/mycompany/src/main/lsfusion/inventory/receipts/ReceiptInv.lsf) | Dossier §2.3 | Movimiento físico efectivo, descontando cantidad ya ubicada internamente; seguir put-away y ledger. |
| `ReceiptCost` | [ReceiptCost.lsf](../../vendor/mycompany/src/main/lsfusion/inventory/receipts/ReceiptCost.lsf) | Dossier §2.5 | Entradas de costo por recepción activa; seguir costos de línea, extensiones abstractas y conciliación con factura. |
| `ReceiptPutAway` | [ReceiptPutAway.lsf](../../vendor/mycompany/src/main/lsfusion/inventory/receipts/ReceiptPutAway.lsf) | Dossier §2.4 | Distribución interna en ubicaciones descendientes; evitar doble conteo entre ubicación principal y destino. |
| `Shipment` | [Shipment.lsf](../../vendor/mycompany/src/main/lsfusion/inventory/shipments/Shipment.lsf) | Dossier §3.1 | Seguir `ShipmentReady`, `ShipmentDone`, `ShipmentRes`, `ShipmentInv`, `ShipmentAcceptance`, picking/lotes, `SalesOrderShipment` y transferencias. |
| `ShipmentReady` | [ShipmentReady.lsf](../../vendor/mycompany/src/main/lsfusion/inventory/shipments/ShipmentReady.lsf) | Dossier §3.2 | Reserva/control de disponibilidad; distinguir cantidad pedida, reservada, preparada y efectivamente despachada. |
| `ShipmentDone` | [ShipmentDone.lsf](../../vendor/mycompany/src/main/lsfusion/inventory/shipments/ShipmentDone.lsf) | Dossier §3.4 | Confirmación del egreso, cantidades efectivas y fecha/hora; seguir `ShipmentInv`, `ShipmentRes` y parciales. |
| `ShipmentRes` | [ShipmentRes.lsf](../../vendor/mycompany/src/main/lsfusion/inventory/shipments/ShipmentRes.lsf) | Dossier §3.2 | Alta/liberación de reserva; conciliar con ResLedger y con pedido fuente. |
| `ShipmentInv` | [ShipmentInv.lsf](../../vendor/mycompany/src/main/lsfusion/inventory/shipments/ShipmentInv.lsf) | Dossier §3.4 | Movimiento físico al completar; revisar origen/destino y recepción espejo de traslados. |
| `ShipmentAcceptance` | [ShipmentAcceptance.lsf](../../vendor/mycompany/src/main/lsfusion/inventory/shipments/acceptance/ShipmentAcceptance.lsf) | Dossier §3.5 | Aceptación en destino según permisos de ubicación; no habilitar un ingreso no aceptado como stock disponible. |
| `Adjustment` | [Adjustment.lsf](../../vendor/mycompany/src/main/lsfusion/inventory/adjustments/Adjustment.lsf) | Dossier §4 | Conteo/diferencia/confirmación; seguir `AdjustmentDone`, `AdjustmentInv`, costo, permisos y trazabilidad. |
| `AdjustmentDone` | [AdjustmentDone.lsf](../../vendor/mycompany/src/main/lsfusion/inventory/adjustments/AdjustmentDone.lsf) | Dossier §4 | Efecto de confirmación sobre ledger; probar diferencias positivas/negativas, cancelación y recálculo. |
| `Scrap` | [Scrap.lsf](../../vendor/mycompany/src/main/lsfusion/inventory/scraps/Scrap.lsf) | Dossier §§1 y 5; mapa funcional, inventario/mermas | Seguir estado, `ScrapInv`, `ScrapCost`, lotes, motivos, permisos y tratamiento de merma; aceptación E2E pendiente. |
| `Location` | [Location.lsf](../../vendor/mycompany/src/main/lsfusion/inventory/locations/Location.lsf) | Dossier §§1.1, 1.3 y 5 | Ubicación física, jerarquía, acceso y ubicación de costo no son sinónimos. Seguir `LocationEmployee`, `LocationProduct`, `CostLocation`, `Partner` y permisos. |
| `ProductSku` | [ProductSku.lsf](../../vendor/mycompany/src/main/lsfusion/inventory/masterdata/ProductSku.lsf) | Dossier de datos maestros §6; inventario §5 | Relaciona SKU/producto con el circuito de inventario; revisar unidades, variantes, código de barras y claves de exportación. |

### 3.2 Ventas, pedidos, precios y despacho

**Dossier primario:** [Mapa de ventas, precios y ledger comercial](MYCOMPANY_6_2_SALES_PRICING_LEDGER_MAP.md).  
**Cobertura declarada:** análisis profundo parcial; pruebas de runtime y conciliación completas pendientes.

| Módulo exacto | Fuente LSF | Primera lectura obligatoria | Seguir con / relaciones que no se deben romper |
|---|---|---|---|
| `Sales` | [Sales.lsf](../../vendor/mycompany/src/main/lsfusion/sales/Sales.lsf) | Dossier §§1–8 | Es compositor comercial. Usar submódulos de pedido, precios, descuentos, ledger, despacho, facturación, compras y fabricación; no atribuirle propiedad individual a la raíz. |
| `SalesOrder` | [SalesOrder.lsf](../../vendor/mycompany/src/main/lsfusion/sales/orders/SalesOrder.lsf) | [Ficha SalesOrder](modules/SalesOrder.md) → dossier §2 | Cabecera/líneas, cliente/empresa, moneda, ubicación, impuestos, descuentos, actividad, condiciones y documento origen. Seguir módulos de estado y downstream. |
| `SalesOrderConfirmed` | [SalesOrderConfirmed.lsf](../../vendor/mycompany/src/main/lsfusion/sales/orders/SalesOrderConfirmed.lsf) | Dossier §2.2 | Confirmación y precondiciones; seguir estado enviado/cancelado/bloqueado, reserva y consecuencias en despacho. |
| `SalesOrderCanceled` | [SalesOrderCanceled.lsf](../../vendor/mycompany/src/main/lsfusion/sales/orders/SalesOrderCanceled.lsf) | Dossier §2.2 | Cancelación y restricciones por documentos derivados; comprobar despacho, factura y fabricación asociada antes de revertir. |
| `SalesOrderShipment` | [SalesOrderShipment.lsf](../../vendor/mycompany/src/main/lsfusion/sales/inventory/shipments/orders/SalesOrderShipment.lsf) | Dossier §2.3 | Pedido→despacho, reservas y entregas parciales. Seguir `Shipment`, `ShipmentReady`, `ShipmentDone`, picking, `ShipmentInv` y ledger comercial. |
| `SalesOrderInvoice` | [SalesOrderInvoice.lsf](../../vendor/mycompany/src/main/lsfusion/sales/invoicing/invoices/orders/SalesOrderInvoice.lsf) | Dossier §2.4 | Pedido→factura; políticas por pedido o despachado y facturación parcial. Seguir `Invoice`, `InvoiceDebt`, deuda y pagos. |
| `SalesOrderManufacturing` | [SalesOrderManufacturing.lsf](../../vendor/mycompany/src/main/lsfusion/sales/manufacturing/orders/SalesOrderManufacturing.lsf) | Dossier §2.6 | Pedido→BOM/orden de fabricación; una orden iniciada restringe cancelaciones/cambios del pedido. Seguir fabricación e inventario. |
| `SalesOrderPurchase` | [SalesOrderPurchase.lsf](../../vendor/mycompany/src/main/lsfusion/sales/purchase/orders/SalesOrderPurchase.lsf) | Dossier §2.5 | Pedido→compra; revisar vínculo de cabecera y líneas, agrupación, proveedor, cantidades parciales y recepción. |
| `SalesPriceType` | [SalesPriceType.lsf](../../vendor/mycompany/src/main/lsfusion/sales/pricelists/pricetypes/SalesPriceType.lsf) | Dossier §3 | Tipo de precio y margen; seguir lista, líneas/valores, fecha de vigencia, producto y cliente. |
| `SalesPricelist` | [SalesPricelist.lsf](../../vendor/mycompany/src/main/lsfusion/sales/pricelists/SalesPricelist.lsf) | Dossier §3 | Cabecera, valores, validez, importación y recálculo; no duplicar el mecanismo nativo de resolución de precios. |

### 3.3 Compras, proveedores y reposición

**Dossier primario:** [Mapa de compras, proveedores y reposición](MYCOMPANY_6_2_PURCHASE_REPLENISHMENT_MAP.md).  
**Cobertura declarada:** lectura profunda parcial; pruebas de runtime y conciliación pendientes.

| Módulo exacto | Fuente LSF | Primera lectura obligatoria | Seguir con / relaciones que no se deben romper |
|---|---|---|---|
| `Purchase` | [Purchase.lsf](../../vendor/mycompany/src/main/lsfusion/purchase/Purchase.lsf) | Dossier §§1–8 | Composición de compra; seguir pedido, precios proveedor, recepción, Bill, reposición e integración con fabricación. |
| `PurchaseOrder` | [PurchaseOrder.lsf](../../vendor/mycompany/src/main/lsfusion/purchase/orders/PurchaseOrder.lsf) | Ficha individual; pedido, proveedor, empresa, parciales y documentos derivados · [Mapa de compras](../MYCOMPANY_6_2_PURCHASE_REPLENISHMENT_MAP.md) §2 | [Ficha PurchaseOrder](modules/PurchaseOrder.md) · Cabecera/líneas, proveedor, empresa, moneda, ubicación, condiciones y costo. Seguir estados y documentos derivados. |
| `PurchaseOrderConfirmed` | [PurchaseOrderConfirmed.lsf](../../vendor/mycompany/src/main/lsfusion/purchase/orders/PurchaseOrderConfirmed.lsf) | Dossier §2 | Confirmación de pedido; seguir recepciones, facturación, reservas y cambios/cancelación. |
| `PurchaseOrderReceipt` | [PurchaseOrderReceipt.lsf](../../vendor/mycompany/src/main/lsfusion/purchase/inventory/receipts/orders/PurchaseOrderReceipt.lsf) | Dossier §3 | Pedido→recepción; seguir Receipt, cantidades recibidas, reservas esperadas, put-away, costo y recepción parcial. |
| `PurchaseOrderBill` | [PurchaseOrderBill.lsf](../../vendor/mycompany/src/main/lsfusion/purchase/invoicing/bills/orders/PurchaseOrderBill.lsf) | Dossier §4 | Pedido→factura proveedor; seguir Bill/BillDebt, política de facturación por pedido/recibido, recepciones y pagos. |
| `PurchaseOrderShipmentAuto` | [PurchaseOrderShipmentAuto.lsf](../../vendor/mycompany/src/main/lsfusion/purchase/inventory/shipments/orders/PurchaseOrderShipmentAuto.lsf) | Dossier §6 | Reposición automática nativa por proveedor/periodo; comparar su ventana, agregados y pack con el planificador Rubrova, sin duplicarlo. |
| `PurchasePricelist` | [PurchasePricelist.lsf](../../vendor/mycompany/src/main/lsfusion/purchase/pricelists/PurchasePricelist.lsf) | Dossier §5 | Precios de proveedor, importaciones, vigencia y aplicación a pedidos/costos. Seguir Master Data y moneda. |

### 3.4 Facturación, deuda, pagos y cuentas

**Dossier primario:** [Mapa de facturación, deuda, pagos y cuentas](MYCOMPANY_6_2_INVOICING_LEDGER_MAP.md).  
**Cobertura declarada:** lectura profunda de ledgers, documentos/pagos e impuestos; pruebas de runtime y conciliación contable pendientes.

| Módulo exacto | Fuente LSF | Primera lectura obligatoria | Seguir con / relaciones que no se deben romper |
|---|---|---|---|
| `Invoicing` | [Invoicing.lsf](../../vendor/mycompany/src/main/lsfusion/invoicing/Invoicing.lsf) | Dossier §§1–8 | Composición financiera; seguir Invoice, Bill, Debt, Payment, IncomingPayment, OutgoingPayment, impuestos, cuentas y calendario. |
| `Invoice` | [Invoice.lsf](../../vendor/mycompany/src/main/lsfusion/invoicing/invoices/Invoice.lsf) | Ficha individual; factura de venta, deuda, cobros y notas de crédito · [Mapa de facturación](../MYCOMPANY_6_2_INVOICING_LEDGER_MAP.md) §§2–3 | [Ficha Invoice](modules/Invoice.md) · Factura de venta, impuestos y líneas; seguir estados, InvoiceDebt, crédito/devolución, cobros y ledger comercial. |
| `Bill` | [Bill.lsf](../../vendor/mycompany/src/main/lsfusion/invoicing/bills/Bill.lsf) | Ficha individual; factura proveedor, costo, deuda y pagos · [Mapa de facturación](../MYCOMPANY_6_2_INVOICING_LEDGER_MAP.md) §§2–5 | [Ficha Bill](modules/Bill.md) · Factura proveedor; seguir recepción/compra, costo de línea, deuda saliente, pagos, impuestos y correcciones. |
| `Debt` | [Debt.lsf](../../vendor/mycompany/src/main/lsfusion/invoicing/ledgers/Debt.lsf) | Dossier §3 | Ledger de deudas, imputaciones parciales, socio/empresa, moneda y saldo; seguir Invoice/Bill y pagos. |
| `Payment` | [Payment.lsf](../../vendor/mycompany/src/main/lsfusion/invoicing/ledgers/Payment.lsf) | Dossier §§4–5 | Movimientos de cuentas y conciliación; distinguir caja/banco, cobro/pago y sesión POS. |
| `IncomingPayment` | [IncomingPayment.lsf](../../vendor/mycompany/src/main/lsfusion/invoicing/payments/incoming/IncomingPayment.lsf) | Dossier §5.1 | Cobro y aplicación a deuda; seguir Payment, InvoiceDebt, SessionPayment y medios de pago. |
| `OutgoingPayment` | [OutgoingPayment.lsf](../../vendor/mycompany/src/main/lsfusion/invoicing/payments/outgoing/OutgoingPayment.lsf) | Dossier §5.2 | Pago/salida y aplicación a deuda; seguir BillDebt, reintegros y SessionPayment. |

### 3.5 Retail, POS, turnos y medios de pago

**Dossier primario:** [Mapa de retail, POS, sesiones y devoluciones](MYCOMPANY_6_2_RETAIL_POS_SESSIONS_MAP.md).  
**Cobertura declarada:** las 30 fuentes LSF retail fueron leídas; aceptación runtime, hardware/fiscal y conciliación de caja pendientes.

| Módulo exacto | Fuente LSF | Primera lectura obligatoria | Seguir con / relaciones que no se deben romper |
|---|---|---|---|
| `Retail` | [Retail.lsf](../../vendor/mycompany/src/main/lsfusion/retail/Retail.lsf) | Dossier §§1–12 | Composición retail; revisar parámetros, POS, sesión, dashboard, métodos, devoluciones, facturas y extensiones Rubrova. |
| `Pos` | [Pos.lsf](../../vendor/mycompany/src/main/lsfusion/retail/pos/Pos.lsf) | Ficha individual; caja lógica, empresa, computadora, controladores y Session · [Mapa Retail/POS](../MYCOMPANY_6_2_RETAIL_POS_SESSIONS_MAP.md) §§2–3 | [Ficha Pos](modules/Pos.md) · Caja lógica, empresa, computadora y driver; seguir PosPaymentMethod, PaymentMethod, usuario y sesión. |
| `PosPaymentMethod` | [PosPaymentMethod.lsf](../../vendor/mycompany/src/main/lsfusion/retail/pos/PosPaymentMethod.lsf) | Dossier §2 | Habilitación por caja y cuenta vinculada; revisar titularidad empresa, Payment y caja central. |
| `PaymentMethod` | [PaymentMethod.lsf](../../vendor/mycompany/src/main/lsfusion/retail/payments/PaymentMethod.lsf) | Dossier §4 | Método de cobro entrante y tipo de pago saliente para devoluciones; seguir cuentas, cobros y terminales. |
| `Session` | [Session.lsf](../../vendor/mycompany/src/main/lsfusion/retail/sessions/Session.lsf) | [Ficha Session](modules/Session.md) → dossier §3 | Turno, apertura/cierre, único turno abierto por POS y hooks before/after; seguir facturas, pagos, retiros y cierre. |
| `SessionInvoice` | [SessionInvoice.lsf](../../vendor/mycompany/src/main/lsfusion/retail/sessions/SessionInvoice.lsf) | Dossier §3 | Relación sesión↔factura/nota y totales netos; seguir Invoice/CreditNote y estados. |
| `SessionPayment` | [SessionPayment.lsf](../../vendor/mycompany/src/main/lsfusion/retail/sessions/SessionPayment.lsf) | Dossier §4 | Importes por medio de pago; seguir IncomingPayment, OutgoingPayment, InvoiceDebt y BillDebt. |
| `SessionShipment` | [SessionShipment.lsf](../../vendor/mycompany/src/main/lsfusion/retail/sessions/SessionShipment.lsf) | Dossier §3 | Relación de despacho con sesión; seguir inventario, factura y logística. |
| `PosDashboard` | [PosDashboard.lsf](../../vendor/mycompany/src/main/lsfusion/retail/pos/dashboard/PosDashboard.lsf) | Dossier §6 | Pantalla de venta y contexto POS/sesión; seguir búsqueda, líneas, precio, reserva, factura y permisos. |
| `PosDashboardPayment` | [PosDashboardPayment.lsf](../../vendor/mycompany/src/main/lsfusion/retail/pos/dashboard/PosDashboardPayment.lsf) | Dossier §4 | Cobro mixto y vuelto; seguir métodos, terminal, IncomingPayment, cuenta, sesión y conciliación. |
| `PosDashboardReturn` | [PosDashboardReturn.lsf](../../vendor/mycompany/src/main/lsfusion/retail/pos/dashboard/return/PosDashboardReturn.lsf) | Dossier §8 | Devolución/crédito y reintegro; seguir CreditNote, stock disposition, OutgoingPayment, límites Rubrova y sesión. |

### 3.6 Datos maestros y entidades transversales

**Dossier primario:** [Mapa de datos maestros y relaciones transversales](MYCOMPANY_6_2_MASTERDATA_RELATIONSHIPS_MAP.md).  
**Cobertura declarada:** 84 módulos inventariados y fuentes principales leídas; pruebas runtime, extensiones y adecuación argentina pendientes.

| Módulo exacto | Fuente LSF | Primera lectura obligatoria | Seguir con / relaciones que no se deben romper |
|---|---|---|---|
| `MasterDataP` | [MasterData.lsf](../../vendor/mycompany/src/main/lsfusion/masterdata/MasterData.lsf) | Dossier §1 | La fuente declara `MODULE MasterDataP`; seguir entidades compartidas y composición, no inferir el nombre del módulo desde el archivo. |
| `Item` | [Item.lsf](../../vendor/mycompany/src/main/lsfusion/masterdata/items/Item.lsf) | Dossier §§4–6 | Artículo abstracto, categoría y unidad; seguir Product/Service, atributos, variantes, barcode, UOM, packs y costos. |
| `Product` | [Product.lsf](../../vendor/mycompany/src/main/lsfusion/masterdata/items/products/Product.lsf) | Ficha individual; Item, unidad, atributos, variantes, lote y SKU · [Datos maestros](../MYCOMPANY_6_2_MASTERDATA_RELATIONSHIPS_MAP.md) §§4–7 | [Ficha Product](modules/Product.md) · Producto físico; seguir Item, ItemSales/Purchase, ProductLot, ProductSku, Inventario, facturación y BOM. |
| `Partner` | [Partner.lsf](../../vendor/mycompany/src/main/lsfusion/masterdata/partners/Partner.lsf) | Ficha individual; identidad, especializaciones y roles cliente/proveedor · [Datos maestros](../MYCOMPANY_6_2_MASTERDATA_RELATIONSHIPS_MAP.md) §§2–3 | [Ficha Partner](modules/Partner.md) · Identidad común; distinguir LegalEntity, Company, Individual, cliente/proveedor, contactos y duplicados. |
| `Company` | [Company.lsf](../../vendor/mycompany/src/main/lsfusion/masterdata/partners/Company.lsf) | Dossier §3 | Empresa propia y titular de cuentas/documentos; seguir permisos, POS, facturas, compras y pagos. |
| `Employee` | [Employee.lsf](../../vendor/mycompany/src/main/lsfusion/masterdata/partners/employees/Employee.lsf) | Dossier §3 | Empleado y vínculo con usuario/roles; seguir HR, CRM, Fleet, ubicación y seguridad. |
| `ProductSku` | [ProductSku.lsf](../../vendor/mycompany/src/main/lsfusion/inventory/masterdata/ProductSku.lsf) | Dossier §6; inventario §5 | SKU y productos, claves de importación/exportación y usos en compromisos/reservas. |

### 3.7 Fabricación y órdenes de trabajo

**Ruta actual:** [Mapa funcional general](MYCOMPANY_6_2_FUNCTIONAL_MAP.md), dominio Manufacturing; [Ventas](MYCOMPANY_6_2_SALES_PRICING_LEDGER_MAP.md) §2.6; [Compras](MYCOMPANY_6_2_PURCHASE_REPLENISHMENT_MAP.md) §7; [Inventario](MYCOMPANY_6_2_INVENTORY_LEDGER_MAP.md) §§1–5.

| Módulo exacto | Fuente LSF | Primera lectura obligatoria | Seguir con / estado |
|---|---|---|---|
| `Manufacturing` | [Manufacturing.lsf](../../vendor/mycompany/src/main/lsfusion/manufacturing/Manufacturing.lsf) | [Guía obligatoria Fabricación + Proyectos](MYCOMPANY_6_2_MANUFACTURING_PROJECTS_INTEGRATION.md) | Compositor del dominio; revisar sus 41 fuentes LSF por separado. La guía E2E es de proceso, no un pasaporte exhaustivo de todo el compositor. |
| `Bom` | [Bom.lsf](../../vendor/mycompany/src/main/lsfusion/manufacturing/bom/Bom.lsf) | [Ficha Bom](modules/Bom.md) + guía Fabricación/Proyectos | Estructura, cantidades base, subproductos, operaciones y BOM anidada. |
| `ManufacturingOrder` | [ManufacturingOrder.lsf](../../vendor/mycompany/src/main/lsfusion/manufacturing/orders/ManufacturingOrder.lsf) | [Ficha ManufacturingOrder](modules/ManufacturingOrder.md) + guía Fabricación/Proyectos | Documento central; revisar estado real, reservas, inventario, costos, lotes y vínculo de proyecto. |
| `WorkCenter` | [WorkCenter.lsf](../../vendor/mycompany/src/main/lsfusion/manufacturing/workOrders/WorkCenter.lsf) | [Ficha WorkCenter](modules/WorkCenter.md) + guía Fabricación/Proyectos | Maestro nativo; no demuestra capacidad finita ni calendario. |
| `WorkOrder` | [WorkOrder.lsf](../../vendor/mycompany/src/main/lsfusion/manufacturing/workOrders/WorkOrder.lsf) | [Ficha WorkOrder](modules/WorkOrder.md) + guía Fabricación/Proyectos | Operación derivada de BOM; revisar regeneración, estado y duración estimada. |

**No crear recetas, consumos, órdenes, mermas o costos paralelos** sin cerrar el análisis nativo de BOM, ManufacturingOrder, WorkOrder, sus reservas y ledgers.

### 3.8 Proyectos, asignaciones, partes de horas y órdenes de fabricación

**Ruta obligatoria:** [guía Fabricación + Proyectos](MYCOMPANY_6_2_MANUFACTURING_PROJECTS_INTEGRATION.md) y [mapa de Proyectos](MYCOMPANY_6_2_PROJECT_MANAGEMENT_INTEGRATIONS_MAP.md). Esta integración conecta documentos nativos, no una API interna.

| Módulo exacto | Fuente LSF | Primera lectura obligatoria | Seguir con / estado |
|---|---|---|---|
| `Project` | [Project.lsf](../../vendor/mycompany/src/main/lsfusion/projectManagement/projects/Project.lsf) | [Ficha Project](modules/Project.md) | Contexto de trabajo y documentos; seguir asignaciones, ventas, compras, fabricación, tiempos y reportes. |
| `ProjectAssignment` | [ProjectAssignment.lsf](../../vendor/mycompany/src/main/lsfusion/projectManagement/projects/ProjectAssignment.lsf) | [Ficha ProjectAssignment](modules/ProjectAssignment.md) | Roles, fechas de vigencia y filtros de acceso; probar usuario global/sin asignaciones. |
| `TimeEntry` | [TimeEntry.lsf](../../vendor/mycompany/src/main/lsfusion/projectManagement/timeEntries/TimeEntry.lsf) | [Ficha TimeEntry](modules/TimeEntry.md) | Registro base de horas; seguir Project, Task, nómina y timesheets. |
| `ProjectTimeEntry` | [ProjectTimeEntry.lsf](../../vendor/mycompany/src/main/lsfusion/projectManagement/projects/timeentries/ProjectTimeEntry.lsf) | [Ficha ProjectTimeEntry](modules/ProjectTimeEntry.md) | Proyecto por parte, projectRequired y filtros de acceso. |
| `ProjectManufacturingOrder` | [ProjectManufacturingOrder.lsf](../../vendor/mycompany/src/main/lsfusion/projectManagement/manufacturing/orders/ProjectManufacturingOrder.lsf) | [Ficha ProjectManufacturingOrder](modules/ProjectManufacturingOrder.md) | Vínculo Project↔ManufacturingOrder y creación desde proyecto. |
| `ProjectManufacturingOrderTimeEntry` | [ProjectManufacturingOrderTimeEntry.lsf](../../vendor/mycompany/src/main/lsfusion/projectManagement/manufacturing/orders/ProjectManufacturingOrderTimeEntry.lsf) | [Ficha ProjectManufacturingOrderTimeEntry](modules/ProjectManufacturingOrderTimeEntry.md) | Asociación TimeEntry↔ManufacturingOrder y coherencia de proyecto. |

**No crear project ledger, worklog, receta, orden ni costo paralelos.** Usar los formularios y ledgers nativos; respetar permisos y el punto de extensión `fill`.

### 3.9 CRM, RR. HH. y flota

Estas áreas tienen dossiers específicos y una ruta de integración, pero su análisis funcional no es exhaustivo. No habilitan uso productivo sin completar formularios, estados, permisos, APIs y pruebas.

| Módulo exacto | Fuente LSF | Primera lectura obligatoria | Seguir con / estado |
|---|---|---|---|
| `CRM` | [CRM.lsf](../../vendor/mycompany/src/main/lsfusion/crm/CRM.lsf) | [CRM y leads](MYCOMPANY_6_2_CRM_LEADS_MAP.md) | Composición CRM; seguir Master Data, Sales y utilidades de comunicación. |
| `Lead` | [Lead.lsf](../../vendor/mycompany/src/main/lsfusion/crm/leads/Lead.lsf) | CRM y leads §2 | Lead, estado/tipo/prioridad, actividad y socio; seguir conversión a SalesOrder/Invoice y comunicaciones. |
| `HumanResources` | [HumanResources.lsf](../../vendor/mycompany/src/main/lsfusion/humanResources/HumanResources.lsf) | [HR, asistencia y payroll](MYCOMPANY_6_2_HR_ATTENDANCE_PAYROLL_MAP.md) | Composición HR; seguir empleados, asistencia, reclutamiento, nómina y pagos. |
| `Attendance` | [Attendance.lsf](../../vendor/mycompany/src/main/lsfusion/humanResources/attendance/Attendance.lsf) | HR, asistencia y payroll §4 | Asistencia y empleado; seguir AttendanceMobile/Kiosk, GeoUtils, permisos y reglas laborales. |
| `Fleet` | [Fleet.lsf](../../vendor/mycompany/src/main/lsfusion/fleet/Fleet.lsf) | [Flota y costos](MYCOMPANY_6_2_FLEET_VEHICLE_COSTS_MAP.md) | Composición de vehículos/servicios y gastos; seguir Master Data, Bills y Project Management. |
| `Vehicle` | [Vehicle.lsf](../../vendor/mycompany/src/main/lsfusion/fleet/vehicles/Vehicle.lsf) | Flota y costos §2 | Vehículo, modelo, combustible, categoría y archivos; ficha E2E de mantenimiento pendiente. |
| `ProjectManagement` | [ProjectManagement.lsf](../../vendor/mycompany/src/main/lsfusion/projectManagement/ProjectManagement.lsf) | [Proyectos e integraciones](MYCOMPANY_6_2_PROJECT_MANAGEMENT_INTEGRATIONS_MAP.md) | Composición; seguir proyectos, tareas, HR, compras, ventas, fabricación y facturación. |
| `Task` | [Task.lsf](../../vendor/mycompany/src/main/lsfusion/projectManagement/tasks/Task.lsf) | Proyectos e integraciones §3 | Tarea y workflow; seguir estados, dependencias, asignaciones, tiempos, notificaciones y permisos. |

## 4. Rutas transversales obligatorias

La primera lectura del módulo no sustituye estas dependencias cuando el cambio las toca:

| Cuando el cambio toca... | Leer además | Razón |
|---|---|---|
| Producto, socio, empresa, empleado, unidad, barcode, variante, pack | [Datos maestros](MYCOMPANY_6_2_MASTERDATA_RELATIONSHIPS_MAP.md) | Evitar crear un maestro o clave paralela; conservar identidad/ratios. |
| Documentos, líneas, historial, numeradores, archivos, correo, geo, criptografía | [Utilidades compartidas](MYCOMPANY_6_2_UTILITY_MODULES.md) | Reutilizar macros y mecanismos nativos; validar permisos, configuración y dependencias. |
| Sesión, APPLY/CANCEL, hooks, eventos, formularios, API o transacciones | [Capacidades lsFusion](LSFUSION_6_2_CAPABILITY_MAP.md) + [Guía de integración](../ENGINEERING_MASTER.md#b-integration) | Comprender contrato de lenguaje/runtime y fronteras de sesión. |
| API, terminal, proveedor, webhook, transporte | [Contratos históricos](../ENGINEERING_MASTER.md#c-contracts) + [Resiliencia de integraciones](../INTEGRATION_RESILIENCE_AND_ERROR_HANDLING.md) | Esquema, autenticación, idempotencia, timeout, error, recuperación y conciliación. |
| Roles, ubicaciones, secretos, `@@api`, administración | [Postura de seguridad](../SECURITY_POSTURE.md) + [Seguridad y auditoría](../SECURITY_AND_AUDIT.md) | Autorización real, mínimo privilegio, auditoría y exposición de datos. |
| Backup, migración, cambios de esquema o restauración | [Backup y migraciones](../BACKUP_AND_MIGRATION_STRATEGY.md) + [Continuidad operativa](../OPERATIONAL_RESILIENCE_AND_RECOVERY.md) | Compatibilidad, recuperación y verificación de datos. |
| Rentabilidad, costo, forecast o reportes | [Fundación analítica](../DATA_CAPTURE_AND_ANALYTICAL_FOUNDATION.md) + [Demanda y margen](../DEMAND_AND_MARGIN_INTELLIGENCE.md) | No alterar ledger transaccional ni confundir dato observado con estimación. |
| Fiscalidad argentina, facturación electrónica o comprobantes | [Interoperabilidad contable](../ACCOUNTING_INTEROPERABILITY.md) | MyCompany 6.2 no equivale a integración fiscal argentina homologada. |

## 5. Módulos que no aparecen en las tablas anteriores

No significa que sean irrelevantes. Para cualquier nombre del inventario:
1. ejecutar `node scripts/platform/module-integration-route.mjs --module NombreExacto`;
2. seguir el dossier principal que devuelve según el dominio del archivo;
3. si no hay ruta manual suficiente, registrar un pendiente y completar la ficha de integración;
4. si está fuera del cierre de `RubrovaCustom`, evaluar dependencias, licencia, configuración, seguridad y prueba de carga antes de proponer activarlo.

Los módulos regionales, los 16 módulos no regionales fuera del cierre y los 25 módulos de plataforma lsFusion fuera de la composición conservan su condición de candidatos no activados. Ver el [mapa funcional de MyCompany](MYCOMPANY_6_2_FUNCTIONAL_MAP.md), el [mapa regional](MYCOMPANY_6_2_REGIONAL_MODULES.md) y el [mapa de capacidades lsFusion](LSFUSION_6_2_CAPABILITY_MAP.md).

## 6. Condición de cierre por módulo

Un módulo no se declara listo para integración sólo porque figure en el registro, tenga REQUIRE resuelto o compile. La ficha debe demostrar:
- quién es dueño de las entidades y qué API/acción constituye su contrato;
- qué caso de uso produce el documento y qué estados lo gobiernan;
- qué ledgers y otros módulos consumen sus hechos;
- cómo se comportan parciales, cancelaciones, reintentos, permisos y concurrencia;
- cómo se concilia el resultado y qué evidencia repetible existe;
- qué se puede extender sin parchear ni duplicar al upstream.

Hasta contar con esa evidencia, el estado debe permanecer explícitamente parcial o pendiente.
