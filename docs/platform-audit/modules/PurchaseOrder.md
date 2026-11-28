# Ficha de integración — PurchaseOrder

**Fuente fijada:** MyCompany 6.2 · commit `d21ca6978717b98b6300d90267f9767db7414008`  
**Composición:** incluido en el cierre actual de `RubrovaCustom`, según el catálogo estructural.  
**Evidencia:** revisión estática de fuente; runtime, conciliación y aceptación deben probarse aparte.

**Identificador:** `MODULE PurchaseOrder` · **Namespace:** `Purchase`  
**Fuente:** [PurchaseOrder.lsf](../../../vendor/mycompany/src/main/lsfusion/purchase/orders/PurchaseOrder.lsf#L1-L341)  
**Dossier primario:** [Compras, proveedores y reposición](../MYCOMPANY_6_2_PURCHASE_REPLENISHMENT_MAP.md) §§1–4 y 8.

## 1. Lectura de 2 minutos

`PurchaseOrder` es el documento de origen del circuito de aprovisionamiento. Mantiene proveedor, empresa compradora, moneda, ubicación, condiciones de pago, fecha prevista y líneas con artículo/unidad/cantidad/precio. Su confirmación puede habilitar recepción, facturación y fabricación, según el tipo y configuración. **El pedido no es stock recibido ni deuda/factura contabilizada.**

**REQUIRE directos:** Time, MetaNumerator, Employee, Company, Currency, FileUtils, Icon, Comments, Activity, MetaTax, TaxItem, BarCode, PurchaseOrderType, PurchaseSettings, PartnerPurchase, ItemSales, ItemCost, PaymentTermsPurchase, Doc, DateUtils, DebtPartner, LocationEmployee.

**Consumidores directos:** ProjectPurchaseOrder, Purchase, PurchaseOrderReceipt, PurchaseOrderShipment, PurchaseOrderBill, PurchaseOrderManufacturing, PurchaseOrderCanceled, PurchaseOrderDebt, PurchaseOrderEmail, PurchaseOrderFilter, PurchaseOrderItem, PurchaseOrderPack, PurchaseOrderPartner, PurchaseOrderSelection, PurchaseOrderSent, PurchaseOrderUom, PurchaseOrderPrint y PurchaseOrderReport.

## 2. Entidades, responsabilidad y validaciones

- Cabecera: clase `Order`; líneas: `OrderLine`.
- La cabecera conserva tipo, fecha/hora, número, proveedor, condiciones de pago, vencimiento, fecha programada, empresa propia, ubicación, moneda, representante, referencia del proveedor, nota y detalles.
- La línea pertenece a una cabecera y contiene artículo, unidad derivada, cantidad, precio y cálculo fiscal/comercial.
- El socio debe cumplir `isVendor`; el artículo debe cumplir `canBePurchased`.
- La ubicación no puede ser de uso interno cuando la constraint lo prohíbe.
- El proveedor puede proponer condiciones de pago; el tipo puede proponer defaults de moneda y ubicación.
- La unidad y los paquetes pueden incorporar conversiones; no comparar cantidades sin normalizarlas a su unidad de referencia.
- La empresa y las cuentas asociadas deben respetar su titularidad en los módulos de deuda/pago.

No crear otra entidad “orden de compra” para un canal externo: evaluar primero los hooks, extensiones y referencias de PurchaseOrder.

## 3. Interfaz y uso

Fuentes declaran formularios `order`, `orders` y `orderLines`, navegación `orders`, historial de cabecera/línea, impuestos, estado, conteo de líneas, acceso por ubicación, actividad, comentarios y adjuntos. `copy` aplica el contexto actual y genera una nueva sesión/documento con cabecera y líneas copiadas; no reutiliza el ID.

El módulo contiene una anotación `@@api`; identificar la declaración exacta en la fuente antes de consumirla como API externa. No asumir autenticación, esquema ni idempotencia a partir del inventario de declaraciones.

## 4. Casos de uso y circuito

| Paso | Módulo relacionado | Resultado que debe conservarse |
|---|---|---|
| Crear/editar | PurchaseOrder + PurchaseOrderType | Proveedor, empresa, moneda, ubicación, líneas y condiciones |
| Enviar | PurchaseOrderSent / PurchaseOrderEmail | Estado de envío, plantilla y destinatario |
| Confirmar | PurchaseOrderConfirmed | Transición y elegibilidad para documentos derivados |
| Recibir | PurchaseOrderReceipt → Receipt | Referencia pedido/línea, cantidades parciales y coeficientes de unidad |
| Facturar proveedor | PurchaseOrderBill → Bill | Política ordered/delivered y referencia a líneas de recepción |
| Abastecer/fabricar | PurchaseOrderManufacturing | Artículos y cantidades vinculadas a órdenes de fabricación |
| Cancelar/bloquear | PurchaseOrderCanceled y estados | No permitir romper operaciones downstream activas |
| Deuda e informe | PurchaseOrderDebt / PurchaseOrderReport | Pendientes y cantidades conciliables |

En política de facturación `ordered`, se factura contra cantidad pedida menos cantidad ya facturada. En `delivered`, la factura se construye desde recepciones activas, cantidades efectivamente recibidas y todavía no facturadas; se conserva la relación con la recepción para no facturar dos veces una misma cantidad.

## 5. Comunicación y contratos

Las fronteras internas están repartidas entre extensiones del documento base y módulos de cumplimiento. Las relaciones clave son:
- Pedido ↔ recepción y líneas de recepción.
- Pedido ↔ factura de proveedor y línea de recepción consumida.
- Pedido ↔ órdenes de fabricación y demanda.
- Pedido ↔ deuda/condiciones de pago.
- Pedido ↔ proveedor/empresa/ubicación/artículo.

No inferir que un `REQUIRE` significa que todos los flujos estén activos. Comprobar política del tipo, estados y composición de cada módulo consumidor.

## 6. Estados, efectos y riesgos

La confirmación habilita procesos downstream; envío, cancelación y bloqueo tienen módulos separados. Antes de modificar/cancelar un pedido, verificar recepciones, facturas, pagos, despachos y órdenes de fabricación originadas. Una orden de fabricación iniciada puede restringir cambios en el documento origen.

Riesgos:
- duplicar recepción o facturación al reintentar una acción;
- confundir cantidad pedida con recibida/facturada/pagada;
- perder conversión de unidad o paquete;
- cancelar cabecera sin evaluar documentos dependientes;
- asumir que precio/costo del pedido equivale al costo final del ledger.

## 7. Pruebas mínimas

1. Proveedor y artículo válidos/no válidos, empresas y ubicaciones.
2. Moneda, condiciones, unidad, pack y conversiones.
3. Confirmación/envío/cancelación/bloqueo con permisos.
4. Varias recepciones parciales contra un pedido.
5. Facturación ordered vs delivered, con facturas parciales y sin doble consumo de recepción.
6. Diferencias de precio/cantidad, impuestos, moneda y costos de recepción.
7. Pedido a fabricación y restricciones tras inicio de producción.
8. Reintentos, concurrencia y reversión; conciliación pedido↔recepción↔Bill↔pago.

**Aceptación:** pendiente de runtime y conciliación E2E.

## 8. Lecturas siguientes

- [Receipt](Receipt.md), [Bill](Bill.md), [Product](Product.md) y [Partner](Partner.md).
- [Mapa de compras](../MYCOMPANY_6_2_PURCHASE_REPLENISHMENT_MAP.md) §§2–8.
- [Inventario](../MYCOMPANY_6_2_INVENTORY_LEDGER_MAP.md), [facturación](../MYCOMPANY_6_2_INVOICING_LEDGER_MAP.md) y [datos maestros](../MYCOMPANY_6_2_MASTERDATA_RELATIONSHIPS_MAP.md).
- [Resiliencia](../../INTEGRATION_RESILIENCE_AND_ERROR_HANDLING.md), [seguridad](../../SECURITY_POSTURE.md) y [guía de integración](../../ENGINEERING_MASTER.md#b-integration).

**Regla de integración:** conservar la identidad del pedido y sus líneas a lo largo de recepciones, facturas y fabricación; no reemplazar esas relaciones por un estado o saldo agregado.
