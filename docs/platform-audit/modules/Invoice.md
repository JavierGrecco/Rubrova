# Ficha de integración — Invoice

**Fuente fijada:** MyCompany 6.2 · commit `d21ca6978717b98b6300d90267f9767db7414008`  
**Composición:** incluido en el cierre actual de `RubrovaCustom`, según el catálogo estructural.  
**Evidencia:** revisión estática de fuente; runtime, conciliación y aceptación deben probarse aparte.

**Identificador:** `MODULE Invoice` · **Namespace:** `Invoicing`  
**Fuente:** [Invoice.lsf](../../../vendor/mycompany/src/main/lsfusion/invoicing/invoices/Invoice.lsf#L1-L383)  
**Dossier:** [Facturación, deuda, pagos y cuentas](../MYCOMPANY_6_2_INVOICING_LEDGER_MAP.md) §§2.1–2.3, 3, 5 y 7.

## 1. Lectura de 2 minutos

`Invoice` define la factura de venta y sus líneas. Su estado, datos fiscales/comerciales y relación con `Debt` determinan cuándo participa en saldos y cuándo queda pendiente/cancelada/pagada. No es lo mismo que un cobro, un pago, una sesión de caja o un comprobante fiscal argentino homologado.

**REQUIRE directos:** InvoicingSettings, TaxItem, BankAccount, FileUtils, MetaTax, PaymentTermsSales, DateUtils, Department, ItemSales, PartnerSales, Company, Employee, BarCode, MetaNumerator, Doc, InvoiceType, Product.

**Consumidores directos:** Invoicing, InvoiceContract, InvoiceCurrency, InvoiceFilter, InvoiceItem, InvoicePack, InvoiceReady, InvoiceSelection, InvoiceTax, InvoiceUom, ProjectInvoice, KSeFInvoice (regional polaco), DiscountCardInvoice, PosDashboardDiscountCard y SalesPricelistInvoice.

## 2. Entidades y datos dueños

- Cabecera: clase `Invoice`; líneas: `InvoiceLine`.
- Cabecera: tipo, fecha/hora, número, fechas de entrega/ejecución, cliente, empresa, condiciones/vencimiento, cuentas, dirección, departamento, representante y detalles.
- Líneas: artículo, unidad, cantidad, precio, descuento e impuestos.
- El cliente debe cumplir `isCustomer`; el artículo debe cumplir `canBeSold`.
- La empresa es obligatoria y se inicializa desde `defaultCompany()`.
- La cuenta del cliente debe pertenecer a ese cliente; la cuenta de empresa debe pertenecer a la empresa seleccionada.
- Condiciones de pago del cliente pueden inicializar la fecha de vencimiento.
- El artículo determina unidad y puede proponer precio predeterminado. La línea hereda estado y datos de la factura.

## 3. Interfaz y operaciones

El módulo declara formularios `invoice`, `invoices` e `invoiceLines`, navegación de facturas, historial, datos y formulario fiscal, formulario de estado, conteo de líneas, comentarios y archivos. La factura ofrece acción `copy` que crea una nueva factura y copia cabecera/líneas; no es una reversión de la original.

La fuente utiliza macros de documento, estado, impuestos, descuentos, historia y objetos asociados. Revisar la expansión/contrato de esas macros antes de extender el documento.

## 4. Ciclo de vida y relación con deuda/pago

| Tema | Módulo relacionado | Efecto |
|---|---|---|
| Tipo | InvoiceType | Configuración y defaults documentales |
| Preparar/listar | InvoiceReady | Marca documento listo y lo hace elegible para ledgers según circuito |
| Cancelar | InvoiceCanceled | Retira el efecto activo del documento cuando corresponde |
| Deuda | InvoiceDebt + Debt | La factura de venta extiende OutgoingDebt en el modelo nativo |
| Cobro | IncomingPayment / Payment | Aplica importes al saldo; puede haber parcialidad |
| Nota de crédito/devolución | CreditNote y módulos relacionados | Documento correctivo separado y efecto de deuda/stock según caso |
| Sesión POS | SessionInvoice / SessionPayment | Asocia factura y cobros al turno |

El mapa de facturación explica que el ledger de deuda define la actividad desde el estado listo y que la cancelación desactiva el documento. El estado pagado puede derivarse de la imputación total, salvo puntos de extensión como `skipSetDone`. No implementar “pagada” como un booleano aislado ni confundir total bruto del pago con el monto imputado a esta factura.

## 5. Comunicación e integraciones

- La factura conserva relación con SalesOrder cuando se crea desde pedido; pueden existir varias facturas parciales contra un origen.
- POS crea facturas y las asocia a SessionInvoice; cobros se registran por Payment/IncomingPayment.
- `KSeFInvoice` es consumidor regional polaco; no implica compatibilidad fiscal argentina ni debe activarse como tal.
- La fuente de Invoice no declara aquí una API externa; no inferir endpoints desde módulos consumidores.
- Autoridad de deuda, movimientos bancarios/caja y stock reside en módulos ledgers/documentos correspondientes, no en la pantalla de factura.

## 6. Riesgos

- emitir o duplicar factura ante reintento;
- cambiar cliente/empresa/cuenta luego de generar pagos o contratos;
- cambiar líneas/precio/impuestos luego de imputaciones;
- confundir factura, nota de crédito, despacho y cobro;
- asumir que estado visual determina integridad fiscal;
- usar KSeF o una configuración regional como sustituto de integración ARCA.
- pérdida de referencia a pedido/líneas o a recepción cuando la factura es derivada.

## 7. Pruebas mínimas

1. Cliente no cliente, empresa y cuenta con titular incorrecto: rechazo.
2. Artículo no vendible, servicio/producto, UoM y conversión.
3. Impuestos incluidos/separados, descuentos, moneda y fecha de cotización.
4. Borrador→listo→cancelado/pagado, edición permitida y efecto de cada transición sobre Debt.
5. Cobro parcial, múltiples cobros, pago aplicado a varias deudas y saldo residual.
6. Nota de crédito y devolución; conciliación de cantidades/importe.
7. Asociación POS/session y sesión cerrada.
8. Reintento/timeout y duplicación, documentos derivados y restore.
9. Localización argentina y comprobante fiscal/homologación, como gate separado.

**Aceptación:** fuentes revisadas por el dossier; runtime, conciliación fiscal y E2E pendientes.

## 8. Lecturas siguientes

- [Bill](Bill.md), [PurchaseOrder](PurchaseOrder.md), [SalesOrder](SalesOrder.md), [Session](Session.md).
- [Mapa de facturación](../MYCOMPANY_6_2_INVOICING_LEDGER_MAP.md) §§2–7.
- [Ventas](../MYCOMPANY_6_2_SALES_PRICING_LEDGER_MAP.md), [Retail/POS](../MYCOMPANY_6_2_RETAIL_POS_SESSIONS_MAP.md), [Master Data](../MYCOMPANY_6_2_MASTERDATA_RELATIONSHIPS_MAP.md).
- [Interoperabilidad contable](../../ACCOUNTING_INTEROPERABILITY.md), [pagos/terminales](../../PAYMENT_TERMINAL_INTEGRATION_ARCHITECTURE.md), [seguridad](../../SECURITY_POSTURE.md).

**Regla de integración:** un cobro sólo modifica la deuda en la medida en que queda aplicado; no alterar Debt ni reportar una factura como pagada desde un flujo paralelo.
