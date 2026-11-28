# Ficha de integración — Bill

**Fuente fijada:** MyCompany 6.2 · commit `d21ca6978717b98b6300d90267f9767db7414008`  
**Composición:** incluido en el cierre actual de `RubrovaCustom`, según el catálogo estructural.  
**Evidencia:** revisión estática de fuente; runtime, conciliación y aceptación deben probarse aparte.

**Identificador:** `MODULE Bill` · **Namespace:** `Invoicing`  
**Fuente:** [Bill.lsf](../../../vendor/mycompany/src/main/lsfusion/invoicing/bills/Bill.lsf#L1-L346)  
**Dossier:** [Facturación, deuda, pagos y cuentas](../MYCOMPANY_6_2_INVOICING_LEDGER_MAP.md) §§2.2–2.3, 3, 5 y 7; [compras](../MYCOMPANY_6_2_PURCHASE_REPLENISHMENT_MAP.md) §4.

## 1. Lectura de 2 minutos

`Bill` es la factura de proveedor y sus líneas. Puede mezclar productos y servicios, incluir impuestos/costos/extensiones y extender `IncomingDebt` a través del circuito nativo de Debt. No es el pedido de compra, la recepción física ni el pago al proveedor.

**REQUIRE directos:** InvoicingSettings, TaxItem, BankAccount, FileUtils, MetaTax, PaymentTermsPurchase, DateUtils, ItemPurchase, ItemCost, PartnerPurchase, Company, BarCode, MetaNumerator, Doc, LocationEmployee, BillType, Product, ServiceP.

**Consumidores directos:** BillVehicleService, Invoicing, BillContract, BillCost, BillCurrency, BillFilter, BillItem, BillReady, BillSelection, BillTax, BillUom, BillCustomsDeclaration, BillPrint, ProjectBill, PurchaseBillPricelist, KSeFBill (regional polaco) y SessionInvoice.

## 2. Entidades y validaciones

- Cabecera: clase `Bill`; líneas: `BillLine`.
- Cabecera: tipo, fecha/hora, número, fecha de entrega/ejecución, proveedor, empresa, condiciones/vencimiento, cuentas, referencia del proveedor, representante, nota y detalles.
- Línea: artículo/servicio, cantidad, unidad, precio, impuestos y referencias al documento.
- El socio debe ser proveedor; los artículos deben permitir compra.
- Se admiten Product y Service: no atribuir movimiento físico de inventario a una línea de servicio.
- Cuenta del proveedor y cuenta de empresa validan titularidad; condiciones del proveedor pueden proponer vencimiento.
- La fuente crea defaults del tipo y fecha del documento.

## 3. Interfaz y operación

Declara formularios `bill`, `bills`, `billLines`, navegación, historial de cabecera/líneas, impuestos, estado, conteo de líneas, comentarios, adjuntos y copia en una nueva sesión. `changeUntaxedAmount` permite ajustar importes de línea y recalcula precio según la diferencia; revisar efectos fiscales/precisión antes de extender esa acción.

## 4. Ciclo de vida, deuda y pagos

| Paso | Módulo | Qué hace |
|---|---|---|
| Tipo | BillType | Configuración y defaults |
| Listo | BillReady | Estado que habilita el documento para su ledger |
| Cancelar | BillCanceled | Retira efecto activo según el circuito |
| Costo | BillCost | Integra el costo del documento/servicio según configuración |
| Deuda | BillDebt + Debt | Extiende IncomingDebt por la factura proveedor |
| Pago | OutgoingPayment / Payment | Imputa el pago y reduce saldo pendiente |
| Origen compra/recepción | PurchaseOrderBill / PurchaseOrderBillReceipt | Conserva relación con pedido y recepción |

El mapa de facturación señala que Bill representa IncomingDebt; el nombre incoming/outgoing es terminología de clases y no debe traducirse de forma mecánica como flujo de efectivo. Los pagos parciales se representan mediante imputaciones monetarias. Estado pagado puede derivarse de deuda totalmente imputada, salvo hooks de extensión.

## 5. Comunicación y contratos

- Desde PurchaseOrderBill la factura puede generarse sobre cantidad pedida (`ordered`) o efectivamente recibida (`delivered`). En el segundo caso la factura conserva vínculo con las líneas de recepción consumidas y evita doble facturación.
- BillCost, BillCurrency, BillTax, BillUom y BillContract son extensiones consumidoras; leer antes de tocar el documento.
- KSeFBill es integración regional polaca, no una homologación argentina.
- BillVehicleService la utiliza el dominio de flota; una factura también puede originarse en servicios/gastos.
- No se declara un endpoint externo propio en esta fuente.

## 6. Riesgos y límites

- Producto y servicio tienen efectos distintos; no generar stock por un servicio.
- Costos adicionales, flete, aduana, impuestos y moneda pueden afectar valoración y deuda de formas distintas.
- Una factura proveedor no demuestra que la mercadería fue recibida.
- Cancelar/editar luego de pagos o imputaciones puede afectar deuda.
- No activar KSeF ni módulos regionales como sustituto de normativa argentina.
- Evitar duplicar facturas ante reintentos y conservar links de recepción/pedido.

## 7. Pruebas mínimas

1. Proveedor/empresa/cuenta con titular incorrecto.
2. Producto y servicio; cantidad/unidad y validaciones de compra.
3. Impuestos, moneda, costos adicionales y vencimientos.
4. Facturación ordered vs delivered y facturas parciales.
5. Recepción parcial, factura parcial, notas/correcciones y cancelación.
6. Pago parcial/total y conciliación de Debt/Payment.
7. BillCost, BillCurrency, BillTax y BillUom en datos de prueba.
8. Error/reintento, doble envío y recuperación.
9. Fiscalidad y comprobantes argentinos como gate independiente.

**Aceptación:** lectura de fuente y dossier; runtime y conciliación contable pendientes.

## 8. Lecturas siguientes

- [PurchaseOrder](PurchaseOrder.md), [Invoice](Invoice.md), [Product](Product.md), [Partner](Partner.md).
- [Mapa de facturación](../MYCOMPANY_6_2_INVOICING_LEDGER_MAP.md) §§2–7.
- [Compras](../MYCOMPANY_6_2_PURCHASE_REPLENISHMENT_MAP.md) §§2–4, [inventario](../MYCOMPANY_6_2_INVENTORY_LEDGER_MAP.md), [master data](../MYCOMPANY_6_2_MASTERDATA_RELATIONSHIPS_MAP.md).
- [Interoperabilidad contable](../../ACCOUNTING_INTEROPERABILITY.md), [resiliencia](../../INTEGRATION_RESILIENCE_AND_ERROR_HANDLING.md) y [seguridad](../../SECURITY_POSTURE.md).

**Regla de integración:** conservar el vínculo con pedido/recepción y el ledger de deuda; no convertir Bill en movimiento físico ni en pago.
