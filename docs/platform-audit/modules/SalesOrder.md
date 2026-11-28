# Ficha de integración — SalesOrder


**Fuente fijada:** MyCompany 6.2 · commit d21ca6978717b98b6300d90267f9767db7414008  
**Composición:** dentro del cierre actual de RubrovaCustom, según el catálogo estructural.  
**Evidencia:** lectura de fuente estática; no equivale a runtime, conciliación ni aceptación.

**Identificador real:** MODULE SalesOrder · **Namespace:** Sales  
**Fuente:** [SalesOrder.lsf](../../../vendor/mycompany/src/main/lsfusion/sales/orders/SalesOrder.lsf#L1-L395)  
**Dossier:** [Ventas, precios, descuentos y ledger comercial](../MYCOMPANY_6_2_SALES_PRICING_LEDGER_MAP.md) §2; [datos maestros](../MYCOMPANY_6_2_MASTERDATA_RELATIONSHIPS_MAP.md).

## 1. Resumen de 2 minutos

SalesOrder define el pedido comercial y sus líneas. Es el documento de origen de circuitos posteriores: despacho/reserva, facturación, compras, fabricación, deuda y reportes. Un pedido confirmado no equivale a stock despachado, factura emitida ni pago cobrado.

**REQUIRE directos:** Time, MetaNumerator, Employee, Company, DateUtils, FileUtils, Comments, Activity, MetaTax, TaxItem, BarCode, LocationEmployee, Department, SalesSettings, PartnerSales, ItemSales, SalesOrderType, PaymentTermsSales, ServiceP, Doc.

**Consumidores directos principales:** ProjectSalesOrder, Sales, SalesOrderShipment, SalesOrderManufacturing, SalesOrderAPI, SalesOrderCanceled, SalesOrderConfirmed, SalesOrderDebt, SalesOrderEmail, SalesOrderFilter, SalesOrderGeo, SalesOrderItem, SalesOrderPack, SalesOrderPartner, SalesOrderSearch, SalesOrderSelection, SalesOrderSent, SalesOrderTax, SalesOrderPrint, SalesPricelistSearch y SalesOrderReport.

## 2. Responsabilidad y datos

Clase cabecera: Order. Clase de línea: OrderLine.

**Cabecera:** tipo, fecha/hora, numerador, cliente, vigencia, condiciones de pago, vencimiento calculado, empresa, fecha programada, dirección de entrega, ubicación, moneda, representante, referencia del cliente, nota y detalles.

**Línea:** pedido propietario, artículo, descripción, unidad derivada, cantidad, precio, impuestos y valores de línea. El artículo puede ser producto físico o servicio y debe poder venderse (canBeSold).

Reglas observadas:
- El socio debe tener rol de cliente (isCustomer).
- Empresa y algunos defaults se proponen automáticamente.
- Las condiciones de pago pueden heredarse del cliente.
- La dirección de entrega puede derivarse del departamento o dirección del cliente.
- La ubicación no puede ser de uso interno cuando la regla lo prohíbe.
- Tipo/cliente/artículo participan de la resolución de precio e impuestos.

## 3. Interfaz y uso

Formularios: order, orders y orderLines; la navegación incorpora orders. El formulario permite administrar cabecera, líneas, impuestos y totales; integra historia, documentos, estados, permisos de ubicación, actividad, comentarios y archivos.

La acción copy crea un nuevo pedido y copia datos comerciales y líneas; no reutiliza el ID original. El helper showOrder(LONG id) tiene anotación @@api; revisar publicación, permisos y contrato real antes de tratarlo como API externa estable.

## 4. Casos de uso y documentos derivados

| Caso | Módulo siguiente | Qué debe preservarse |
|---|---|---|
| Crear/editar pedido | SalesOrder + tipos/estado | Cabecera, líneas, unidad, precio, moneda e impuestos |
| Confirmar | SalesOrderConfirmed | Validaciones y restricciones posteriores |
| Enviar/cancelar/bloquear | SalesOrderSent, SalesOrderCanceled y estados relacionados | Estado y permisos; comprobar documentos derivados |
| Preparar/despachar | SalesOrderShipment → Shipment | Pedido, cantidad pedida, reservada, preparada y despachada |
| Facturar | SalesOrderInvoice → Invoice | Política por cantidad pedida o despachada; facturas parciales |
| Comprar para cumplir | SalesOrderPurchase | Vínculo pedido/orden de compra en cabecera y líneas |
| Fabricar para cumplir | SalesOrderManufacturing | BOM y orden asociada; cambios/cancelación limitados tras inicio |

## 5. Contratos y comunicación

- Los submódulos consumen/extienden las clases y propiedades del pedido; no duplicar cabecera ni líneas.
- La fuente declara @@api para showOrder y existe consumidor SalesOrderAPI; esta ficha no certifica autenticación, esquema, endpoints ni idempotencia.
- Doc, MetaTax, TaxItem, PartnerSales, ItemSales, PaymentTermsSales y LocationEmployee participan del contrato. Revisar sus reglas antes de sobreescribir propiedades.
- Documentos derivados deben conservar referencias al pedido/líneas para parcialidad y conciliación.

## 6. Estados, transacciones y riesgos

Estados y acciones se distribuyen entre confirmación, envío, cancelación y bloqueo. No asumir que borrar/cancelar un pedido es seguro si generó despacho, factura, compra u orden de fabricación.

El módulo usa macros de estado documental, impuestos, descuentos, historial y objetos relacionados. La expansión de macros no se incluye en el conteo estático; revisar sus definiciones antes de extenderlas.

## 7. Pruebas mínimas

1. Cliente válido/inválido, empresa y ubicación permitida/no permitida.
2. Producto/servicio vendible, unidad y conversión.
3. Precio por lista, descuentos e impuestos incluidos/separados.
4. Confirmar, enviar, bloquear, cancelar y editar en cada estado permitido.
5. Varios despachos y facturas parciales.
6. Compra o fabricación derivada y restricciones tras inicio de producción.
7. API showOrder/SalesOrderAPI: autenticación, permisos, IDs inválidos, empresa y contrato.
8. Conciliación pedido↔despacho↔factura↔cobro y cancelaciones.

**Estado de aceptación:** análisis de fuente detallado; runtime, API y conciliación E2E pendientes.

## 8. Lecturas siguientes

- [Mapa de ventas](../MYCOMPANY_6_2_SALES_PRICING_LEDGER_MAP.md) §§2–7.
- [Inventario](../MYCOMPANY_6_2_INVENTORY_LEDGER_MAP.md), [facturación](../MYCOMPANY_6_2_INVOICING_LEDGER_MAP.md) y [compras](../MYCOMPANY_6_2_PURCHASE_REPLENISHMENT_MAP.md).
- [Datos maestros](../MYCOMPANY_6_2_MASTERDATA_RELATIONSHIPS_MAP.md) para Partner, Company, Item, unidad, Department y Employee.
- [Capacidades lsFusion](../LSFUSION_6_2_CAPABILITY_MAP.md), [seguridad](../../SECURITY_POSTURE.md) y [resiliencia](../../INTEGRATION_RESILIENCE_AND_ERROR_HANDLING.md).

**Definición de terminado:** ninguna integración convierte el pedido directamente en una alteración de stock o deuda fuera de los documentos derivados y sus estados nativos.
