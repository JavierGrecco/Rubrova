# Pasaporte de integración — pedido, factura de proveedor, deuda y pago

**Grupo funcional:** PurchaseOrderBill / Bill / OutgoingPayment lifecycle  
**Fuente fijada:** MyCompany 6.2 · commit d21ca6978717b98b6300d90267f9767db7414008  
**Plataforma:** lsFusion 6.2 · commit dd4dbe5bf9b136e73e18fe25d741253929324350  
**Composición:** módulos de Purchase, Invoicing e InvoicingInventory cargados por MyCompany; los módulos de valuación de recepción se inicializan explícitamente después de Purchase.  
**Evidencia:** lectura estática de fuentes y dependencias. La conciliación runtime de factura, deuda, pago, moneda y costo de factura sigue pendiente; no se declara aceptado ni fiscalmente homologado.

Este pasaporte reúne una única secuencia documental/financiera. Complementa [PurchaseOrder](PurchaseOrder.md), [Bill](Bill.md), [ReceiptLifecycle](ReceiptLifecycle.md), el [mapa de compras](../MYCOMPANY_6_2_PURCHASE_REPLENISHMENT_MAP.md) y el [mapa de facturación, deuda, pagos y cuentas](../MYCOMPANY_6_2_INVOICING_LEDGER_MAP.md).

## 0. Resumen de integración — lectura de 2 minutos

| Pregunta | Respuesta |
|---|---|
| Alcance de este grupo | 37 módulos MyCompany que conectan pedido, factura de proveedor, recepción originada en factura, deuda, pago y cuentas |
| Dueños de datos | Purchase es dueño de Order/OrderLine; Invoicing es dueño de Bill/BillLine y OutgoingPayment; Debt y Payment son modelos abstractos transversales |
| Política de facturación | ordered: cantidad pedida menos facturada; delivered: cantidad recibida en recepciones activas que aún no fue facturada |
| Pago | Bill extiende IncomingDebt; OutgoingPayment extiende OutgoingDebt; el importe se imputa mediante paid(IncomingDebt, OutgoingDebt) |
| Movimiento de cuenta | OutgoingPaymentLedger extiende Payment y aporta importe firmado negativo mientras el pago está activo |
| Segundo camino de recepción | BillReceipt permite crear una Receipt inmediata/Done desde líneas de producto de una factura de proveedor |
| Costo | BillReceiptCost proporciona una implementación alternativa del costo de ReceiptLine; BillReceiptCostService añade distribución de servicios |
| APIs | Este grupo no declara un endpoint HTTP propio. La comunicación es interna lsFusion mediante REQUIRE, extensiones, WHEN, acciones y relaciones documentales |
| Riesgo clave | No confundir cantidad pedida/facturada/recibida/pagada, estado Done, deuda imputada y movimiento de caja/banco |
| Decisión reuse-first | Usar Bill, PurchaseOrderBill, BillDebt, Debt, OutgoingPayment y Payment. No crear factura, deuda o pago paralelo en Rubrova |
| Aceptación actual | Fuentes revisadas; runtime E2E de facturas de proveedor, pagos y conciliación de cuentas pendiente |

## 1. Módulos del circuito y fronteras

### 1.1 Pedido de compra → factura de proveedor

| Módulo | Fuente | Responsabilidad |
|---|---|---|
| PurchaseOrderBill | [PurchaseOrderBill.lsf](../../../vendor/mycompany/src/main/lsfusion/purchase/invoicing/bills/orders/PurchaseOrderBill.lsf#L1-L152) | Relación Order↔Bill, política ordered/delivered, cantidades billed/paid y creación de factura |
| PurchaseOrderBillInitial | [PurchaseOrderBillInitial.lsf](../../../vendor/mycompany/src/main/lsfusion/purchase/invoicing/bills/orders/PurchaseOrderBillInitial.lsf) | Asigna el tipo de factura bill al tipo de pedido estándar cuyo ID es order |
| PurchaseOrderBillReceipt | [PurchaseOrderBillReceipt.lsf](../../../vendor/mycompany/src/main/lsfusion/purchase/invoicing/bills/orders/PurchaseOrderBillReceipt.lsf#L1-L38) | Construye líneas de Bill desde ReceiptLine activas y todavía no facturadas |
| PurchaseOrderBillReceiptInitial | [PurchaseOrderBillReceiptInitial.lsf](../../../vendor/mycompany/src/main/lsfusion/purchase/invoicing/bills/orders/PurchaseOrderBillReceiptInitial.lsf) | Inicializa la política delivered para los tipos de pedido |
| PurchaseOrderBillStatus | [PurchaseOrderBillStatus.lsf](../../../vendor/mycompany/src/main/lsfusion/purchase/invoicing/bills/orders/PurchaseOrderBillStatus.lsf) | Resume estados de las facturas relacionadas al pedido, excluyendo canceladas |
| PurchaseOrderBillUom | [PurchaseOrderBillUom.lsf](../../../vendor/mycompany/src/main/lsfusion/purchase/invoicing/bills/orders/PurchaseOrderBillUom.lsf) | Copia unidad de proveedor a factura y conserva cantidades/precios por unidad de socio |

### 1.2 Documento Bill, estados, deuda y extensiones

| Módulo | Fuente | Responsabilidad |
|---|---|---|
| Bill | [Bill.lsf](../../../vendor/mycompany/src/main/lsfusion/invoicing/bills/Bill.lsf#L1-L346) | Factura de proveedor, cabecera, líneas, proveedor/empresa, cuentas, fecha de vencimiento, artículos/servicios, impuestos, archivos e historial |
| BillType | [BillType.lsf](../../../vendor/mycompany/src/main/lsfusion/invoicing/bills/BillType.lsf) | Numerador, proveedor/artículo por defecto y política de precio con impuestos incluidos |
| BillInitial | [BillInitial.lsf](../../../vendor/mycompany/src/main/lsfusion/invoicing/bills/BillInitial.lsf) | Datos iniciales del tipo de factura |
| BillSelection | [BillSelection.lsf](../../../vendor/mycompany/src/main/lsfusion/invoicing/bills/BillSelection.lsf) | Acciones/listado y selección documental |
| BillReady | [BillReady.lsf](../../../vendor/mycompany/src/main/lsfusion/invoicing/bills/BillReady.lsf) | Estado Ready / To pay, que habilita el efecto activo |
| BillCanceled | [BillCanceled.lsf](../../../vendor/mycompany/src/main/lsfusion/invoicing/bills/BillCanceled.lsf) | Cancelación; active(Bill) queda ready AND NOT canceled |
| BillDone | [BillDone.lsf](../../../vendor/mycompany/src/main/lsfusion/invoicing/bills/BillDone.lsf) | Estado Paid y acción markAsDone |
| BillDebt | [BillDebt.lsf](../../../vendor/mycompany/src/main/lsfusion/invoicing/bills/BillDebt.lsf#L1-L71) | Extiende Bill como IncomingDebt, aporta saldo y auto-actualiza Done al cubrirse el importe |
| BillCost | [BillCost.lsf](../../../vendor/mycompany/src/main/lsfusion/invoicing/bills/BillCost.lsf#L1-L98) | Distribución de costos de servicios hacia líneas de producto |
| BillServiceCost | [BillServiceCost.lsf](../../../vendor/mycompany/src/main/lsfusion/invoicing/bills/BillServiceCost.lsf) | Define objetivos/productos y bases para repartir costos de líneas de servicio |
| BillCurrency | [BillCurrency.lsf](../../../vendor/mycompany/src/main/lsfusion/invoicing/bills/BillCurrency.lsf) | Moneda del tipo/documento y cotización según fecha |
| BillTax | [BillTax.lsf](../../../vendor/mycompany/src/main/lsfusion/invoicing/bills/BillTax.lsf) | Impuestos de compra según proveedor/artículo |
| BillUom | [BillUom.lsf](../../../vendor/mycompany/src/main/lsfusion/invoicing/bills/BillUom.lsf) | Unidad de proveedor, cantidad y precio expresados en unidad alternativa |
| BillPayment | [BillPayment.lsf](../../../vendor/mycompany/src/main/lsfusion/invoicing/bills/payments/BillPayment.lsf#L1-L65) | Acción Register Payment que crea OutgoingPayment y propone la deuda pendiente |

### 1.3 Bill → Receipt y costo de recepción

| Módulo | Fuente | Responsabilidad |
|---|---|---|
| BillReceipt | [BillReceipt.lsf](../../../vendor/mycompany/src/main/lsfusion/invoicing/inventory/receipts/BillReceipt.lsf#L1-L141) | Relaciona Bill con Receipt, permite crear recepción inmediata/Done desde productos de la factura y soporta autoCreateReceipt |
| BillReceiptInitial | [BillReceiptInitial.lsf](../../../vendor/mycompany/src/main/lsfusion/invoicing/inventory/receipts/BillReceiptInitial.lsf) | Asigna receiptType receipt al tipo Bill cuyo ID es bill |
| BillReceiptCost | [BillReceiptCost.lsf](../../../vendor/mycompany/src/main/lsfusion/invoicing/inventory/receipts/BillReceiptCost.lsf#L1-L10) | Calcula costo desde precio de BillLine, cantidad recibida, tipo de cambio y extraCost |
| BillReceiptCostService | [BillReceiptCostService.lsf](../../../vendor/mycompany/src/main/lsfusion/invoicing/inventory/receipts/BillReceiptCostService.lsf#L1-L14) | Incorpora a extraCost los servicios distribuidos a productos |

### 1.4 Pago saliente y movimiento de cuenta

| Módulo | Fuente | Responsabilidad |
|---|---|---|
| OutgoingPayment | [OutgoingPayment.lsf](../../../vendor/mycompany/src/main/lsfusion/invoicing/payments/outgoing/OutgoingPayment.lsf#L1-L172) | Documento de pago, socio, empresa, cuentas, importe, referencia y nota |
| OutgoingPaymentType | [OutgoingPaymentType.lsf](../../../vendor/mycompany/src/main/lsfusion/invoicing/payments/outgoing/OutgoingPaymentType.lsf) | Tipos de pago, numerador y cuentas permitidas (banco/caja/intercompany) |
| OutgoingPaymentInitial | [OutgoingPaymentInitial.lsf](../../../vendor/mycompany/src/main/lsfusion/invoicing/payments/outgoing/OutgoingPaymentInitial.lsf) | Tipos iniciales de pago a proveedor por banco/caja y reintegros a clientes |
| OutgoingPaymentReady | [OutgoingPaymentReady.lsf](../../../vendor/mycompany/src/main/lsfusion/invoicing/payments/outgoing/OutgoingPaymentReady.lsf) | Estado To pay |
| OutgoingPaymentDone | [OutgoingPaymentDone.lsf](../../../vendor/mycompany/src/main/lsfusion/invoicing/payments/outgoing/OutgoingPaymentDone.lsf) | Estado Done y acción Mark as Done |
| OutgoingPaymentCanceled | [OutgoingPaymentCanceled.lsf](../../../vendor/mycompany/src/main/lsfusion/invoicing/payments/outgoing/OutgoingPaymentCanceled.lsf) | Cancela y retira el efecto activo |
| OutgoingPaymentDebt | [OutgoingPaymentDebt.lsf](../../../vendor/mycompany/src/main/lsfusion/invoicing/payments/outgoing/OutgoingPaymentDebt.lsf#L1-L75) | Extiende OutgoingPayment como OutgoingDebt, permite imputar a IncomingDebt y busca referencias automáticamente |
| OutgoingPaymentLedger | [OutgoingPaymentLedger.lsf](../../../vendor/mycompany/src/main/lsfusion/invoicing/payments/outgoing/OutgoingPaymentLedger.lsf) | Extiende Payment; registra salida con signo negativo |
| OutgoingPaymentCurrency | [OutgoingPaymentCurrency.lsf](../../../vendor/mycompany/src/main/lsfusion/invoicing/payments/outgoing/OutgoingPaymentCurrency.lsf) | Moneda por tipo/cuenta propia y cotización por fecha |
| OutgoingPaymentContract | [OutgoingPaymentContract.lsf](../../../vendor/mycompany/src/main/lsfusion/invoicing/payments/outgoing/OutgoingPaymentContract.lsf) | Contrato en el pago y relación con la deuda |

### 1.5 Modelos transversales

| Módulo | Fuente | Responsabilidad |
|---|---|---|
| Debt | [Debt.lsf](../../../vendor/mycompany/src/main/lsfusion/invoicing/ledgers/Debt.lsf#L1-L106) | IncomingDebt/OutgoingDebt, imputaciones, saldos, conversión y vencimientos |
| Payment | [Payment.lsf](../../../vendor/mycompany/src/main/lsfusion/invoicing/ledgers/Payment.lsf#L1-L102) | Movimientos firmados por cuenta, balance histórico y restricción de saldo negativo |
| PurchaseOrderDebt | [PurchaseOrderDebt.lsf](../../../vendor/mycompany/src/main/lsfusion/purchase/orders/PurchaseOrderDebt.lsf) | Muestra deuda total y vencida del proveedor en el pedido; no es una deuda propia del pedido |

**Cobertura exacta:** 37 módulos agrupados; no equivale a 37 fichas individuales. Entre las dependencias relevantes que no se deben ignorar están PurchaseOrder/Confirmed/Locked, PurchaseOrderReceipt, ReceiptCanceled/ReceiptCost, CreditNote, ShipmentReceipt, ProductSku, BillContract, Contract, Currency/ExchangeRate, Account, BankAccount, CashAccount, Partner, Company, PaymentTermsPurchase, TaxItem y MetaTax.

## 2. Autoridad de datos y qué no debe duplicarse

| Dato | Dueño | Fuente de verdad |
|---|---|---|
| Pedido y cantidad contratada | Purchase | Order / OrderLine |
| Recepción y cantidad físicamente recibida | Inventory | Receipt / ReceiptLine |
| Factura del proveedor | Invoicing | Bill / BillLine |
| Relación línea de factura↔pedido | PurchaseOrderBill | orderLine(BillLine) |
| Relación línea de factura↔recepción | PurchaseOrderBillReceipt / BillReceipt | billLine(ReceiptLine) y relación documental |
| Deuda del proveedor | Invoicing | Bill como IncomingDebt |
| Pago | Invoicing | OutgoingPayment como OutgoingDebt y Payment |
| Imputación | Invoicing | paid(IncomingDebt, OutgoingDebt) |
| Saldo de cuenta bancaria/caja | Invoicing | Payment.balance(Account) |
| Costo de inventario recibido | Inventory | ReceiptCostLedger y cost(ReceiptLine) |

No es dueño de la factura fiscal argentina, la presentación contable definitiva, el extracto bancario ni la confirmación del banco. Tampoco reemplaza las reglas de inventario de Receipt/ReceiptInv ni los ledgers de costo.

## 3. Dos políticas diferentes de facturación desde pedido

### 3.1 Ordered — cantidad pedida

PurchaseOrderBill calcula:

- billed(OrderLine): suma de cantidades de BillLine cuyo Bill está Ready y no cancelado;
- toBillOrdered(OrderLine): max(cantidad del pedido menos billed, 0);
- createBill crea una Bill Ready, copia proveedor, empresa, referencia, nota, moneda y condiciones; crea líneas ligadas a OrderLine y propone cantidad/precio.

La opción ordered factura contra el pedido sin exigir que la cantidad haya pasado por una Receipt. La fuente también cae a esta ruta cuando no hay política configurada o cuando la línea no es Product.

### 3.2 Delivered — cantidad recibida

PurchaseOrderBillReceipt calcula la cantidad pendiente a facturar a partir de ReceiptLine:

- toma sólo recepciones activas;
- toma cantidad efectivamente recibida (done);
- excluye líneas que ya tienen billLine;
- crea BillLine por la cantidad efectivamente recibida;
- enlaza la línea de factura con OrderLine y marca qué ReceiptLine fue consumida por esa factura.

El campo toBillShipped tiene ese nombre en la fuente, pero en este flujo representa cantidad recibida, no cantidad enviada al cliente.

**Riesgo de cancelación de factura — fuente revisada, runtime pendiente.** La macro `defineDocLineRelation(bill, receipt, ...)` crea `billLine = DATA BillLine (ReceiptLine)`, una referencia persistente entre líneas. `BillCanceled.cancel` sólo marca `canceled(Bill)` en una nueva sesión y no borra ese vínculo. A su vez, `PurchaseOrderBillReceipt.toBillShipped` exige `NOT billLine(ReceiptLine)`, pero no comprueba si la factura relacionada continúa activa. `PurchaseOrderBill.billed` sí excluye las facturas canceladas. La fuente muestra así una asimetría: una Bill cancelada deja de contar como facturada para el pedido, pero su ReceiptLine podría continuar excluida de la ruta `delivered` para crear una factura sustituta. No declarar defecto hasta probarlo en runtime.


PurchaseOrderBillReceiptInitial inicializa InvoicingPolicy.delivered para los tipos de pedido. PurchaseOrderBillInitial asigna el tipo de factura bill al tipo de pedido de ID order. Son datos iniciales; revisar configuración efectiva antes de crear otros tipos de pedido.

### 3.3 “Paid” por línea no es un importe pagado

PurchaseOrderBill distingue:
- billed(OrderLine): suma la cantidad de líneas en Bill Ready no canceladas;
- paid(OrderLine): suma la cantidad de líneas en Bill Done no canceladas.

Por tanto, el indicador paid en el pedido se calcula por cantidad/documento Done, no como suma monetaria de Debt. La restricción forbidLockNotFullyPaid se basa en esa cantidad por línea. BillDebt puede marcar Bill Done cuando la deuda queda totalmente imputada, pero existe también la propiedad/acción BillDone; no asumir que cualquier Bill Done demuestra una transferencia bancaria conciliada.

## 4. Dos caminos de recepción que deben mantenerse separados

### 4.1 Pedido → recepción existente → factura

Con política delivered, PurchaseOrderBillReceipt crea la factura a partir de ReceiptLine activas y marca billLine(ReceiptLine). Es la ruta que conserva la trazabilidad de la recepción ya ingresada.

### 4.2 Factura → recepción inmediata

BillReceipt permite que una factura Ready genere una Receipt inmediata y Done:
- usa el tipo de recepción configurado en BillType y la ubicación de la factura;
- crea ReceiptLine por cada línea Product;
- fija done(ReceiptLine) desde cantidad de BillLine convertida a SKU;
- liga la ReceiptLine a BillLine;
- puede crear manualmente con createReceipt o automáticamente si autoCreateReceipt(BillType) está habilitado.

La acción manual aparece cuando no hay líneas de recepción relacionadas. La automatización se dispara al establecer Ready o al cambiar el conteo de líneas de producto. Al cancelar Bill, la fuente cancela una Receipt ligada si countBill(Receipt) = 1; cambios de proveedor/cantidad/artículo también pueden actualizar esa recepción.

**Riesgo de configuración que exige prueba:** no combinar sin control el camino delivered (que reutiliza recepciones de pedido) con autoCreateReceipt (que puede generar una Receipt nueva desde Bill). La acción manual tiene un filtro por countReceiptLine, pero el trigger automático debe probarse expresamente en la composición real para descartar una segunda recepción o movimiento de stock.

## 5. De dónde sale el costo de la recepción

ReceiptCost declara cost(ReceiptLine) como ABSTRACT CASE. MyCompany incorpora al menos dos productores relevantes:
- PurchaseOrderReceiptCost: costo basado en precio de OrderLine, cantidad Done y coeficiente SKU;
- BillReceiptCost: costo basado en precio de BillLine, cantidad Done, rate1 de la factura y coeficiente SKU, más extraCost.

La raíz MyCompany requiere Purchase antes de BillReceiptCost y BillReceiptCostService; el propio comentario del módulo indica que éstos deben inicializarse después de Purchase. La documentación de lsFusion 6.x explica que ABSTRACT CASE es OVERRIDE por defecto, que FIRST añade implementaciones al comienzo de la lista y que la última implementación añadida queda seleccionada si varias coinciden. Ver [ABSTRACT operator — lsFusion 6.x](https://docs.lsfusion.org/v6/ABSTRACT_operator/) y la [composición MyCompany](../../../vendor/mycompany/src/main/lsfusion/MyCompany.lsf#L1-L15).

**Inferencia de fuente que debe confirmarse en runtime:** cuando una ReceiptLine está ligada a OrderLine y BillLine, la implementación BillReceiptCost, cargada después de Purchase, debería prevalecer sobre PurchaseOrderReceiptCost en lugar de sumar ambos costos. No tratarlo como un resultado medido hasta ejecutar un caso con precios diferentes.

BillCost y BillServiceCost permiten distribuir líneas de servicio entre líneas de producto usando bases amount, cost, salesPrice, weight, volume o quantity. BillReceiptCostService lleva esa distribución a extraCost de la recepción. La suma distribuida no puede superar el importe sin impuestos de la línea de servicio.

## 6. Deuda, imputación y estado

BillDebt extiende Bill como IncomingDebt y proyecta proveedor, empresa, contrato, moneda, importe de origen y vencimiento. OutgoingPaymentDebt extiende OutgoingPayment como OutgoingDebt.

Debt mantiene paid(IncomingDebt, OutgoingDebt) y calcula left como importe menos imputaciones:
- ambos documentos deben estar activos;
- socio y empresa deben coincidir;
- ambos saldos deben ser positivos;
- skipMatched puede excluir una pareja;
- las acciones de imputación agregan como máximo el menor saldo disponible;
- el ledger impide que el saldo pendiente positivo se vuelva negativo salvo skipCheckLeft.

El nombre de las clases IncomingDebt/OutgoingDebt es técnico. Bill (deuda con proveedor) hereda IncomingDebt y OutgoingPayment hereda OutgoingDebt. No traducir literalmente “incoming/outgoing” como entrada/salida de efectivo.

BillDebt marca done(Bill) cuando amount[Debt](Bill) = paid(Bill), salvo skipSetDone; si deja de cumplirse, revierte done. Esta condición se refiere al importe de deuda totalmente imputado. BillDone también declara estado Paid/Done; verificar permisos y posibles acciones manuales antes de usar el flag como evidencia de liquidación.

## 7. Pago saliente y saldo de cuenta

BillPayment.registerPayment:
1. exige que la factura esté Ready;
2. crea OutgoingPayment en estado Ready;
3. copia tipo de pago configurado en BillType, proveedor, empresa, cuentas y moneda;
4. propone el saldo pendiente;
5. imputa el saldo disponible;
6. abre el diálogo para ajustar importe e imputación.

OutgoingPaymentCanceled define active(payment) como (ready OR done) AND NOT canceled. OutgoingPaymentLedger extiende Payment y registra signedAmount = -amount. Payment.balance suma movimientos activos por companyAccount y no permite saldo negativo si la cuenta no admite allowNegative.

**Consecuencia de fuente:** un OutgoingPayment Ready ya participa del ledger Payment y de la lógica de deuda, aunque su estado siga siendo To pay. BillPayment lo crea Ready, no Done. Debe distinguirse saldo comprometido/propuesto de pago efectivamente ejecutado en reportes y conciliación bancaria. La fuente por sí sola no demuestra cuándo el dinero salió del banco.

OutgoingPaymentType restringe cuentas bancarias/caja y puede marcar pagos intercompany. OutgoingPaymentInitial crea tipos de pago a proveedor bancarios y en efectivo, además de tipos para reintegro a clientes; no considerar todos los tipos como pagos a proveedor.

### 7.1 Secuencia comprobada en fuente MyCompany 6.2 — `BillPayment.registerPayment`

El código fijado de MyCompany 6.2 precisa el comportamiento que debe conservar Rubrova:

1. `BillPaymentInitial` asigna `outgoingPaymentType('vendorbank')` al tipo Bill cuyo ID es `bill`; el tipo `vendorcash` existe, pero no es el predeterminado. No asumir que cualquier CashAccount es compatible con la acción estándar.
2. `registerPayment(Bill)` sólo se expone cuando el documento está Ready. La acción aplica el documento actual y, en una sesión nueva, crea `OutgoingPayment`, lo pone Ready, ejecuta `fill(p,b)` y los eventos locales.
3. `fill(p,b)` copia el tipo de pago desde BillType, proveedor, cuenta del proveedor, empresa, cuenta de la empresa y moneda. Las cuentas deben pertenecer a sus titulares y respetar el tipo bancario/de caja permitido.
4. La acción propone `sourceLeft(b)` como importe y aplica `paid(b,p) <- left(b,p)`. Luego abre el formulario nativo `outgoingPayment` en un diálogo para que el usuario ajuste el importe. Si reduce el importe, la propia acción limita la imputación a `amount[Debt](p)`.
5. `OutgoingPaymentCanceled.active` considera activos tanto Ready como Done, excepto cancelados; `OutgoingPaymentLedger` incorpora el pago al `Payment` con `signedAmount = -amount`. Por ello, el saldo de la cuenta disminuye al registrar un pago Ready, no sólo al marcarlo Done.
6. `OutgoingPaymentDone.markAsDone` cambia el estado a Done en otra sesión, pero no crea un segundo movimiento: el pago sigue siendo un único Payment activo.
7. `BillDebt` marca Bill Done/Paid cuando el importe de deuda queda totalmente imputado y revierte ese estado cuando deja de cumplirse. **Es posible, por diseño de fuente, que Bill ya figure Paid mientras el último OutgoingPayment continúa Ready**. No confundir deuda cubierta/imputada con confirmación externa del banco.
8. `Payment.balance(Account)` suma sólo Payment activos y un constraint impide saldo negativo si `allowNegative(account)` no está habilitado. Un pago que no pueda cubrirse con la cuenta de empresa debe fallar, no crear un saldo artificial.
9. En paralelo, `OutgoingPaymentDebt` puede autoimputar por coincidencia de substring entre `reference(payment)` y `number(IncomingDebt)`. Esa heurística no es conciliación bancaria ni debe usarse como sustituto de la imputación explícita que realiza `BillPayment`.

**Fuentes upstream fijadas al SHA MyCompany 6.2 `d21ca6978717b98b6300d90267f9767db7414008`:** [BillPayment](https://github.com/lsfusion-solutions/mycompany/blob/d21ca6978717b98b6300d90267f9767db7414008/src/main/lsfusion/invoicing/bills/payments/BillPayment.lsf), [BillPaymentInitial](https://github.com/lsfusion-solutions/mycompany/blob/d21ca6978717b98b6300d90267f9767db7414008/src/main/lsfusion/invoicing/bills/payments/BillPaymentInitial.lsf), [OutgoingPayment](https://github.com/lsfusion-solutions/mycompany/blob/d21ca6978717b98b6300d90267f9767db7414008/src/main/lsfusion/invoicing/payments/outgoing/OutgoingPayment.lsf), [OutgoingPaymentCanceled](https://github.com/lsfusion-solutions/mycompany/blob/d21ca6978717b98b6300d90267f9767db7414008/src/main/lsfusion/invoicing/payments/outgoing/OutgoingPaymentCanceled.lsf), [OutgoingPaymentDone](https://github.com/lsfusion-solutions/mycompany/blob/d21ca6978717b98b6300d90267f9767db7414008/src/main/lsfusion/invoicing/payments/outgoing/OutgoingPaymentDone.lsf), [OutgoingPaymentDebt](https://github.com/lsfusion-solutions/mycompany/blob/d21ca6978717b98b6300d90267f9767db7414008/src/main/lsfusion/invoicing/payments/outgoing/OutgoingPaymentDebt.lsf), [OutgoingPaymentLedger](https://github.com/lsfusion-solutions/mycompany/blob/d21ca6978717b98b6300d90267f9767db7414008/src/main/lsfusion/invoicing/payments/outgoing/OutgoingPaymentLedger.lsf), [BillDebt](https://github.com/lsfusion-solutions/mycompany/blob/d21ca6978717b98b6300d90267f9767db7414008/src/main/lsfusion/invoicing/bills/BillDebt.lsf), [Debt](https://github.com/lsfusion-solutions/mycompany/blob/d21ca6978717b98b6300d90267f9767db7414008/src/main/lsfusion/invoicing/ledgers/Debt.lsf), [Payment](https://github.com/lsfusion-solutions/mycompany/blob/d21ca6978717b98b6300d90267f9767db7414008/src/main/lsfusion/invoicing/ledgers/Payment.lsf), [Account](https://github.com/lsfusion-solutions/mycompany/blob/d21ca6978717b98b6300d90267f9767db7414008/src/main/lsfusion/invoicing/accounts/Account.lsf), [CashAccount](https://github.com/lsfusion-solutions/mycompany/blob/d21ca6978717b98b6300d90267f9767db7414008/src/main/lsfusion/invoicing/accounts/cash/CashAccount.lsf).

**Contrato de fixture futura:** la aceptación debe pulsar la acción real `registerPayment` y trabajar con sus diálogos; no basta con insertar OutgoingPayment directamente. Crear cuentas sintéticas independientes de tipo permitido, asignarlas explícitamente a Bill/proveedor y empresa, y sembrar un saldo de apertura positivo mediante el flujo nativo. Medir antes/después el importe de la factura, `paid(Bill)`, `left(Bill)`, estado Bill, estado de cada OutgoingPayment y `Payment.balance(Account)`. En la secuencia 40 + 60 sobre una deuda de 100, el primer pago debe dejar 60 pendientes; el segundo completa la imputación y puede marcar Bill Paid aun estando Ready; pasar el segundo pago a Done no debe descontar dos veces; cancelarlo debe retirar su movimiento e imputación y hacer reaparecer la deuda, siempre que el contrato funcional permita esa cancelación. Repetir la lectura tras reinicio sin volver a ejecutar acciones.

**Estado:** lectura estática exacta de la versión fijada; la secuencia anterior es un plan de aceptación, no resultado runtime. Debe probarse primero la ruta UI nativa porque `registerPayment` abre `DIALOG`.

## 8. Coincidencia automática por referencia

OutgoingPaymentDebt observa cambios de reference, partner y active. Si la referencia contiene el número de una IncomingDebt y canBePaid se cumple, asigna el saldo pendiente automáticamente.

Es una coincidencia de texto por substring, no una conciliación bancaria ni un identificador único. Debe probarse con números que se solapan, referencias con prefijo/sufijo, dos facturas del mismo proveedor, números iguales en empresas distintas y pago que se activa/cancela. No habilitar autoimputación irrestricta sin controlar falsos positivos.

## 9. Moneda, impuestos y condiciones

- BillCurrency fija moneda por BillType/Bill y calcula rate1 por fecha del documento.
- OutgoingPaymentCurrency propone moneda desde cuenta propia o tipo de pago y calcula cotización por fecha.
- Debt conserva moneda e importe de origen y proyecta importe en moneda de cálculo con tipo de cambio fechado.
- BillTax usa reglas de impuesto de compra del proveedor y/o artículo.
- BillType controla taxIncluded, defaults, numerador y tipo de comprobante interno.
- PaymentTermsPurchase propone condiciones y vencimiento según fecha del documento.
- BillUom/PurchaseOrderBillUom mantienen unidades/precios de proveedor; comparar cantidades sólo tras normalizar SKU y unidad.

El modelo de impuestos es genérico. No acredita por sí mismo CAE, ARCA, puntos de venta, numeración fiscal argentina, percepciones/retenciones, padrones ni contingencia. Esas obligaciones requieren un proyecto separado de adecuación local.

## 10. Seguridad y validaciones encontradas

En fuente:
- Bill exige socio clasificado como proveedor;
- BillLine exige artículo apto para compra;
- cuenta del proveedor debe pertenecer al socio;
- cuenta propia debe pertenecer a la empresa;
- BillReceipt impide usar una ubicación marcada internalUse y aplica acceso por ubicación;
- OutgoingPayment valida titular de cuenta del socio/empresa y permite bancos/cajas según OutgoingPaymentType;
- interpay exige que el socio sea una Company.

Pendiente de runtime:
- usuario que intenta crear, modificar, marcar Ready/Done o cancelar factura sin acceso;
- usuario sin acceso a ubicación de recepción;
- cuenta bancaria/caja de titular incorrecto y tipo no permitido;
- doble clic/reintento de Register Payment;
- acceso a las acciones y APIs desde servidor, no sólo visibilidad en formulario;
- cancelación de factura cuando ya existe pago imputado.

## 11. Matriz de pruebas para aceptar el circuito

| Prueba | Resultado exigido |
|---|---|
| Ordered vs delivered | La factura nunca supera el saldo facturable bajo la política seleccionada |
| Parciales sucesivos | Pedido 3, recibos 2+1; facturas parciales sin volver a tomar ReceiptLine ya facturada |
| Factura sin recepción | Sólo ocurre bajo política ordered o flujo expresamente configurado |
| Factura crea Receipt | Receipt inmediata/Done y stock/costo conciliados una sola vez |
| autoCreateReceipt | Sin duplicar la ruta PurchaseOrderBillReceipt delivered |
| Cancelar Bill con Receipt ligada | Se cancela el documento vinculado según el contrato nativo; sin dejar stock/costo activo residual |
| Precio pedido distinto de factura | Comprobar qué implementación cost(ReceiptLine) prevalece y que costo no se duplique |
| Servicio/flete | Distribución por bases y extraCost de recepción reconciliados |
| Pago parcial por acción nativa | Factura 100; botón Register Payment 40; left 60; segundo 60; left 0 |
| Listo vs terminado | Pago Ready descuenta una vez del Payment ledger; cambiar a Done no duplica movimiento |
| Estado derivado de Bill | Bill pasa a Paid al cubrirse toda la deuda aunque el OutgoingPayment correspondiente siga Ready |
| Cancelación de pago | El OutgoingPayment cancelado deja de ser activo, su imputación se retira y el saldo/deuda se recalculan |
| Cuenta y permisos | Cuenta propia del titular correcto, tipo vendorbank/vendorcash permitido, fondos suficientes y rechazo si saldo negativo no autorizado |
| Un pago a varias facturas | Imputación limitada al saldo de cada factura y al monto del pago |
| Sobrepago | Constraint impide sobreimputar deuda ni crear saldo negativo no autorizado |
| Reference substring | No se imputa una factura homónima/solapada por falso positivo |
| Ready vs Done | Reportar por separado saldo de cuenta afectado por Ready y estado de documento Done; no llamarlo conciliación bancaria |
| Moneda | Tipo de cambio fechado, redondeo y edición de fecha después de imputar |
| Cancelar Bill delivered y reemitirla | La ReceiptLine vuelve a quedar facturable o la política define otro camino explícito; no debe quedar una recepción activa imposible de facturar | 
| Cancelar factura/pago | Deuda, imputaciones y cuenta se recalculan sin dejar contrapartidas activas incorrectas |
| Fiscalidad | Comprobantes e impuestos argentinos homologados por separado |

## 12. Decisión reuse-first

| Necesidad | Usar | No desarrollar en paralelo |
|---|---|---|
| Facturar pedido | PurchaseOrderBill ordered/delivered | Otra regla de facturación por cantidad |
| Recibir desde factura | BillReceipt cuando el flujo lo exige | Segundo documento de recepción propio |
| Valuar recepción | ReceiptCost + productores nativos de costo | Ledger de costo Rubrova paralelo |
| Deuda proveedor | BillDebt + Debt | Saldo de proveedor duplicado |
| Pago proveedor | BillPayment + OutgoingPayment | Nuevo documento de pago |
| Imputación parcial | Debt.paid(IncomingDebt, OutgoingDebt) | Conciliación monetaria propia |
| Saldo de cuenta | Payment + Account | Caja/banco paralelo |
| Costos de servicios | BillCost/BillServiceCost y BillReceiptCostService | Reparto propio sin comparar la base nativa |

**No escribir SQL sobre Bill, Receipt, Debt, Payment o sus ledgers.** No alterar el precio de una recepción directamente para compensar diferencias; corregir el documento/relación origen y probar el recálculo nativo.

## 13. Estado y próximos pasos

**Estado actual:** fuente de 37 módulos relevada y relaciones/fórmulas documentadas. La asimetría potencial al cancelar una factura delivered (§3.2) tiene una fixture CI; el run #617 compiló/empaquetó la plataforma completa, pero el smoke nativo abortó durante la carga de datos por superar el límite `vendorReference varchar(30)`. Se corrigió la referencia y se agregó un guard de longitud en `main` (REP-062); todavía no se ha medido la secuencia Bill delivered/cancel en runtime. No existe aún una aceptación E2E completa de pedido→factura→recepción→costo→deuda→pago→saldo de cuenta. #613 acepta sólo Receipt/stock/put-away/costo, no factura, deuda ni pago.

Siguiente bloque de evidencia:
1. Reejecutar CI sobre la referencia corregida y obtener el diagnóstico medido de Bill delivered/cancel; repetir lectura persistida después del reinicio.
2. Según el resultado, corregir con un parche estrecho sólo si se confirma el defecto, preservando el historial documental.
3. Después de resolver ese bloque, implementar una prueba UI para `BillPayment.registerPayment` con pagos parciales y totales, tipo de cuenta permitido y fondos suficientes. Medir Ready/Done/Cancel, imputación de deuda y balance sin duplicar movimientos.
4. Probar la coincidencia automática por substring de referencia por separado; no mezclarla con la aceptación explícita de BillPayment.
5. Conciliar después del reinicio OrderLine, BillLine, ReceiptLine, Debt, Payment y saldo de cuenta.

## 14. Lecturas relacionadas

- [ReceiptLifecycle](ReceiptLifecycle.md), [PurchaseOrder](PurchaseOrder.md), [Bill](Bill.md).
- [Mapa de compras y reposición](../MYCOMPANY_6_2_PURCHASE_REPLENISHMENT_MAP.md).
- [Mapa de facturación, deuda, pagos y cuentas](../MYCOMPANY_6_2_INVOICING_LEDGER_MAP.md).
- [Inventory ledgers](../MYCOMPANY_6_2_INVENTORY_LEDGER_MAP.md).
- [MyCompany root composition](../../../vendor/mycompany/src/main/lsfusion/MyCompany.lsf).
- [lsFusion ABSTRACT CASE 6.x](https://docs.lsfusion.org/v6/ABSTRACT_operator/).

**Definición de terminado:** quien modifique una factura o pago puede identificar el módulo dueño, el vínculo documental con pedido/recepción, la deuda imputada, el movimiento de cuenta, la regla de costo/currency que se aplica y la prueba que debe volver a pasar.
