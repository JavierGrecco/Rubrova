# MyCompany 6.2 — mapa de facturación, deuda, pagos y cuentas

**Estado: lectura de fuentes en profundidad para ledgers, facturas/pagos y cálculo de impuestos; pruebas de runtime y conciliación contable pendientes.**

Este documento sigue los objetos desde facturas y facturas de proveedor hasta deudas, imputaciones, pagos, cuentas y calendario. El propósito es no desarrollar un segundo circuito si el modelo nativo ya lo resuelve.

## 1. Alcance de fuentes

El dominio \`invoicing\` contiene **134 módulos LSF**. Su estructura se divide en:

| Subdominio | Archivos LSF | Función |
|---|---:|---|
| Núcleo y configuración | 2 | Composición y parámetros |
| Cuentas, bancos y cajas | 5 | Cuentas abstractas, bancos, cuentas bancarias y cuentas de caja |
| Facturas de proveedor (\`Bill\`) | 18 | Cabecera, líneas, tipos, filtros, estado, impuestos, moneda, deuda, impresión y costos |
| Correcciones y notas de compra | 2 | Corrección de factura de proveedor y efecto sobre deuda |
| Declaraciones aduaneras | 3 | Documentos y datos aduaneros asociados a facturas de compra |
| Pagos aplicados a facturas de proveedor | 3 | Asociación de pagos y contratos |
| Impresión de facturas de proveedor | 2 | Plantillas e impresión de factura/recepción |
| Devoluciones a proveedor | 4 | Devolución, contrato, unidades y datos iniciales |
| Recepciones vinculadas a facturas | 9 | Recepción, costos, lotes y filtros |
| Despachos vinculados a facturas | 7 | Envíos, lotes, devoluciones y filtros |
| Facturas de venta (\`Invoice\`) | 18 | Cabecera, líneas, tipos, filtros, estado, impuestos, moneda, deuda e impresión |
| Anticipos y correcciones de venta | 4 | Anticipos, correcciones y efecto sobre deuda |
| Notas de crédito | 4 | Nota de crédito y relaciones con contratos/lotes |
| Pagos aplicados a facturas de venta | 3 | Asociación de pagos y contratos |
| Impresión de facturas de venta | 5 | Factura, contrato, deuda, despacho y unidades |
| Ledgers de deuda y pagos | 4 | Deuda abstracta, pagos y relaciones por socio/contrato |
| Cuentas analíticas | 2 | Clasificación y carga/importación |
| Pagos entrantes | 12 | Cobros, tipos, estados, moneda, deuda, ledger, imputación, impresión y filtros |
| Pagos salientes | 13 | Pagos, tipos, estados, moneda, deuda, ledger, imputación, impresión y filtros |
| Reportes y calendario | 3 | Informes de facturas, facturas de proveedor y calendario de vencimientos |
| Impuestos | 5 | Grupos, tasas, reglas por artículo y cálculos |
| Condiciones de pago | 3 | Plazos genéricos, de cliente y de proveedor |

Los conteos son archivos/módulos y no funciones. La ficha estructural individual queda en el registro automático del proyecto; este documento explica los circuitos que se pudieron seguir en fuente.

## 2. Modelo de documento y estado

### 2.1 Factura de venta — \`Invoice\`

Fuente principal: \`invoicing/invoices/Invoice.lsf\`.

- Cabecera con tipo, fecha/hora, número, cliente, empresa propia, representante, condiciones y fecha de vencimiento, cuentas y datos de entrega.
- La fecha se inicializa con la fecha/hora actual al crear el documento.
- El cliente y la empresa se inicializan desde valores predeterminados o el tipo documental.
- El cliente debe cumplir la clasificación de socio como cliente.
- Las condiciones de pago del cliente pueden proponer la fecha de vencimiento: fecha del documento más los días configurados.
- La cuenta del cliente debe pertenecer al mismo cliente; la cuenta propia debe pertenecer a la empresa seleccionada.
- Las líneas validan que el artículo pueda venderse, toman unidad/precio predeterminados y heredan la moneda de la cabecera.

### 2.2 Factura de proveedor

**Pasaporte de integración:** [SupplierBillLifecycle](modules/SupplierBillLifecycle.md), con el enlace al pedido, las dos rutas de recepción, deuda, pago saliente, costo, moneda y cuentas.
 — \`Bill\`

Fuente principal: \`invoicing/bills/Bill.lsf\`.

- Cabecera equivalente para proveedor y empresa propia.
- El proveedor debe cumplir la clasificación de socio como proveedor.
- Las condiciones de pago del proveedor pueden proponer la fecha de vencimiento.
- La cuenta del proveedor y la cuenta propia se validan contra sus titulares.
- Las líneas validan que el artículo pueda comprarse y pueden tomar costo/precio predeterminado a la fecha del documento.
- La factura de proveedor permite combinar productos y servicios y cuenta con extensiones para costos adicionales, impuestos, lotes, recepciones e importes aduaneros.

### 2.3 Estados que afectan los ledgers

Las fuentes separan al menos borrador, listo/para pagar, pagado/terminado y cancelado. Los nombres que aparecen en cada formulario pueden variar por tipo de documento.

- \`InvoiceReady\` / \`BillReady\`: marcan el documento como listo.
- \`InvoiceCanceled\` / \`BillCanceled\`: un documento listo deja de estar activo cuando se cancela.
- \`InvoiceDone\` / \`BillDone\`: permiten marcar el documento como pagado.
- La integración con el ledger de deuda define \`active\` a partir del estado listo y que el documento no esté cancelado.
- \`InvoiceDebt\` / \`BillDebt\` pueden activar el estado pagado cuando el importe de deuda coincide con el total imputado, salvo que el punto abstracto \`skipSetDone\` lo impida.

**Consecuencia:** borrador, cancelado, listo y pagado no son etiquetas visuales intercambiables. Cada estado afecta si el hecho participa en los saldos/ledgers.

**Pendiente:** reproducir todos los cambios de estado, sus eventos y el efecto de edición, cancelación, reactivación y cambio de importes sobre la deuda.

## 3. Ledger de deuda

**Lectura complementaria:** [SupplierBillLifecycle](modules/SupplierBillLifecycle.md) §§6–8 explica cómo Bill y OutgoingPayment se extienden como IncomingDebt/OutgoingDebt y cómo se enlazan con Payment.

Fuente: \`invoicing/ledgers/Debt.lsf\`.

La clase \`Debt\` es abstracta. Los documentos y pagos la extienden como deuda entrante o saliente.

Cada deuda expone:
- estado activo;
- tipo, número y fecha;
- fecha de vencimiento;
- socio y empresa;
- contrato;
- moneda de origen e importe de origen;
- moneda de cálculo, tipo de cambio e importe calculado;
- importe pagado, saldo pendiente y contraparte asociada.

### 3.1 Orientación de deuda

- \`Invoice\` extiende \`OutgoingDebt\`: representa el saldo que surge de la factura de venta.
- \`Bill\` extiende \`IncomingDebt\`: representa el saldo que surge de la factura de proveedor.
- \`IncomingPayment\` y \`OutgoingPayment\` también se integran en esas clases abstractas para permitir imputar cobros y pagos.

Las palabras *incoming* y *outgoing* son nombres de clases del modelo; para entender el sentido económico hay que seguir la relación concreta. No se deben traducir mecánicamente como “entra dinero” o “sale dinero”.

### 3.2 Imputación entre deudas

El ledger mantiene \`paid(IncomingDebt, OutgoingDebt)\`: importe imputado entre una deuda entrante y una saliente.

Reglas visibles en fuente:

- La imputación requiere que ambos objetos correspondan al mismo socio y a la misma empresa.
- Un punto abstracto \`skipMatched\` puede excluir determinadas combinaciones.
- Sólo se puede imputar cuando ambos objetos están activos y los dos saldos pendientes son positivos.
- La imputación manual acumula el menor saldo disponible, no debe superar el saldo de ninguna de las dos partes.
- El total pagado de cada deuda suma imputaciones hacia contrapartes activas.
- El saldo pendiente es importe menos monto imputado.
- Hay restricciones que impiden imputar por encima del total positivo, salvo que un punto abstracto \`skipCheckLeft\` exceptúe el caso.

No es un único booleano “pagado”: la relación contiene montos, permite imputaciones parciales y puede vincular una deuda con varias contrapartes.

### 3.3 Conversión de moneda

El ledger guarda importe/moneda de origen y calcula un importe materializado en una moneda de trabajo. Usa cotización con fecha asociada a la deuda. Hay una opción global \`skipConvertingDebtToDefaultCurrency\` que evita la conversión a la moneda predeterminada.

Los módulos de factura y factura de proveedor fijan moneda por tipo documental o documento y determinan fecha de cotización a partir de la fecha del documento.

**Pendiente:** verificar fecha exacta de cotización, moneda predeterminada, tipos de cambio faltantes, redondeo, diferencias de cambio y comportamiento cuando se modifica la fecha del documento luego de imputar pagos.

## 4. Ledger de movimientos de caja/banco

Fuente: \`invoicing/ledgers/Payment.lsf\`.

La clase abstracta \`Payment\` registra:
- estado activo, tipo y fecha/hora;
- número;
- socio y empresa;
- cuenta del socio y cuenta propia;
- importe firmado, nota y referencia.

### 4.1 Cuentas

La clase \`Account\` es abstracta y tiene:
- titular (socio/empresa);
- moneda;
- responsable;
- nota;
- condición \`allowNegative\`;
- cuenta predeterminada por titular.

Las cuentas concretas se extienden como cuentas bancarias y cajas.

### 4.2 Saldo

El saldo de una cuenta es la suma de importes firmados de pagos activos donde esa cuenta es la cuenta propia:

- \`IncomingPaymentLedger\` agrega el importe de un cobro como positivo.
- \`OutgoingPaymentLedger\` agrega el importe de un pago como negativo.
- El sistema impide que una cuenta quede negativa, salvo que \`allowNegative\` esté habilitado.
- \`balanceA(account, date)\` calcula el saldo histórico restando del saldo actual los movimientos activos posteriores a la fecha.

La fuente contiene también el saldo consolidado de caja por empresa.

**Pendiente:** conciliación con extractos bancarios, transferencias internas, comisiones, retenciones, depósitos/retiros del POS, múltiples monedas, saldos históricos, cambios de estado y cuentas negativas autorizadas.

## 5. Pagos entrantes y salientes

### 5.1 Cobro — \`IncomingPayment\`

- Tiene tipo, fecha/hora, número, socio, empresa, cuenta del socio, cuenta propia e importe.
- La cuenta del socio debe pertenecer al socio del cobro; la cuenta propia debe pertenecer a la empresa.
- El tipo define si se permite usar una cuenta bancaria o caja.
- Un pago puede ser interno entre empresas; en ese caso las reglas exigen que el socio represente una empresa.
- Su integración con deuda lo extiende como \`IncomingDebt\`.
- Participa del ledger de movimientos con signo positivo.
- La regla de activación observada es: pago terminado y no cancelado.

### 5.2 Pago — \`OutgoingPayment\`

- Tiene estructura equivalente, pero con cuentas y sentido de pago.
- Participa del ledger de movimientos con signo negativo.
- La regla de activación observada contempla los estados listo o terminado, salvo cancelación.
- El tipo también controla qué clases de cuenta se aceptan.

### 5.3 Registro de pago desde factura

En la factura de venta, \`InvoicePayment\` agrega una acción \`Register Payment\` que:
- crea un \`IncomingPayment\`;
- toma tipo de pago configurado en el tipo de factura;
- copia cliente, empresa y cuentas;
- lo marca como terminado;
- propone el importe pendiente de la factura;
- imputa el saldo disponible;
- permite ajustar el monto dentro del diálogo y aplicar.

En la factura de proveedor, \`BillPayment\` crea un \`OutgoingPayment\`:
- toma tipo de pago configurado en el tipo de factura de proveedor;
- copia proveedor, empresa, cuentas y moneda;
- lo marca como listo;
- propone el remanente por pagar;
- imputa el saldo disponible;
- permite ajustar el monto dentro del diálogo.

### 5.4 Asociación automática por referencia

Las fuentes \`IncomingPaymentDebt\` y \`OutgoingPaymentDebt\` observan cambios de referencia, socio y estado activo. Si la referencia contiene el número de una deuda compatible y \`canBePaid\` se cumple, imputan automáticamente el saldo pendiente.

**Importante:** esta regla por coincidencia textual de referencia necesita pruebas de unicidad y de falsos positivos. No se debe asumir que equivale a una conciliación bancaria.

## 6. Condiciones de pago y calendario

### 6.1 Condiciones de pago

La clase \`PaymentTerm\` guarda nombre y cantidad de días.

- \`PaymentTermsSales\` permite asignar condiciones de pago a clientes.
- \`PaymentTermsPurchase\` permite asignarlas a proveedores.
- Factura y factura de proveedor pueden completar automáticamente fecha de vencimiento a partir de fecha del documento y días de la condición, salvo que el usuario ya haya modificado la fecha.

### 6.2 Calendario de vencimientos

Fuente: \`invoicing/reporting/PaymentCalendar.lsf\`.

- Filtra por empresa y rango de fechas.
- Agrupa por tipo de deuda o por socio/tipo.
- Muestra saldo anterior al intervalo y variación de deuda en cada fecha.
- Puede abrir el detalle de deudas por vencimiento.
- Calcula \`forecastCash\` como saldo actual de caja más la suma firmada de deudas activas con vencimiento hasta la fecha.
- Incluye una vista de línea para la proyección de caja.

**Pendiente:** validar el signo económico de cada tipo de deuda en escenarios de cobro/pago, documentos cancelados, pagos parciales, moneda, transferencias internas, pagos posteriores y fecha de corte.

## 7. Impuestos

Fuentes: \`taxes/TaxGroup.lsf\`, \`Tax.lsf\`, \`TaxItem.lsf\`, \`MetaTax.lsf\`, \`invoices/InvoiceTax.lsf\`, \`bills/BillTax.lsf\`.

### 7.1 Catálogo y configuración

- \`TaxGroup\` define grupos de impuestos.
- \`Tax\` define nombre, grupo y porcentaje numérico.
- La macro \`defineTax\` agrega selección de impuestos para artículos, categorías, socios o tipos de documentos según el consumidor.
- Para artículos, las reglas pueden copiar impuestos predeterminados desde la categoría, respetando el nivel más específico de la jerarquía.
- En facturas de venta, el tipo de factura puede determinar los impuestos de sus líneas.
- En facturas de proveedor, la regla usa impuestos de compra configurados para el proveedor y puede recurrir al artículo según el caso.

### 7.2 Cálculo

La macro \`defineTaxCalc\`:
- calcula base de renglón como cantidad por precio;
- selecciona tasas por grupo;
- impide seleccionar dos impuestos del mismo grupo en una línea;
- calcula el importe de impuesto por tasa;
- agrega impuesto al total si el precio no lo incluye;
- permite extraer el componente del impuesto si el precio sí lo incluye;
- consolida base, impuestos y total por línea y documento;
- no permite quitar un impuesto que ya está involucrado en un cálculo, salvo que el flujo lo resuelva.

La fórmula observada para el componente tributario usa la tasa sobre la base; cuando el precio incluye impuesto, divide por cien más la tasa para extraer el componente.

### 7.3 Límite local

Este modelo es configurable y genérico. No demuestra:
- tipos de comprobante argentinos;
- IVA discriminado y tratamiento por condición frente a ARCA;
- CAE, puntos de venta, numeración fiscal ni contingencia;
- percepciones/retenciones nacionales, provinciales o municipales;
- impuestos internos;
- RG/Padrones y validación actualizada de CUIT;
- integración de factura electrónica ni homologación.

La adecuación argentina requiere un análisis independiente de módulos regionales, APIs, certificados, proveedores y obligaciones normativas.

## 8. Correcciones, anticipos, notas de crédito y devoluciones

El dominio incluye:
- \`InvoiceCorrection\` / \`BillCorrection\` para vincular correcciones a facturas originales;
- \`InvoiceAdvance\` para anticipos de venta;
- \`CreditNote\` y \`Refund\` para notas de crédito/devoluciones;
- extensiones de deuda \`InvoiceCorrectionDebt\` y \`BillCorrectionDebt\`;
- vínculos con movimientos de inventario para devoluciones y recepciones;
- tipos, contratos, lotes, unidades e impresión asociados.

Algunos módulos relevantes están fuera del cierre actual de \`RubrovaCustom\`; por eso el inventario debe marcarlos como disponibles en la fuente pero no necesariamente cargados.

**Pendiente:** seguir cada tipo de corrección y anticipo, qué documento revierte o ajusta, la relación con inventario, saldo, pagos e impuestos, y qué sucede al cancelar una corrección que ya tiene imputaciones.

## 9. Riesgos y pruebas de aceptación necesarias

| Tema | Escenarios mínimos |
|---|---|
| Deuda parcial | 1 factura contra varios pagos, 1 pago contra varias facturas, remanente y reimputación |
| Sobreimputación | Intentar pagar más que la deuda, editar importe luego de imputar y cancelar contrapartida |
| Estados | Borrador, listo, terminado, cancelado, reactivo y cambio de estado con deuda/pago aplicado |
| Autocoincidencia | Referencia exacta, parcial, duplicada, con prefijo/sufijo, mismo número en otro socio/empresa |
| Monedas | Misma moneda, moneda extranjera, cotización faltante, cambio de fecha, diferencia y redondeo |
| Cuentas | Titular incorrecto, cuenta bancaria no permitida, caja no permitida, saldo negativo habilitado/no habilitado |
| Impuestos | Precio con impuesto incluido/excluido, dos tasas de distinto grupo, dos del mismo grupo, cambio de artículo/tipo/proveedor |
| Correcciones | Nota de crédito total/parcial, anticipo aplicado parcialmente, corrección encadenada y cancelación |
| Calendario | Vencimientos antes/dentro/después del período, pagos posteriores, saldo inicial, proyección y varios socios |
| Reportes | Conciliar factura, deuda, pagos, ledger de cuenta, saldo y calendario |

## 10. Estado

La lectura de las fuentes identificó el modelo abstracto de deuda, la relación de imputaciones, el ledger de movimientos de caja/banco, las facturas de venta y proveedor, los estados, pagos desde documentos, pagos automáticos por referencia, términos, calendario e impuestos configurables.

**No se declara conciliado ni aceptado:** faltan pruebas del runtime de Rubrova, ejercicios con varias monedas, conciliación de cuentas, impuestos argentinos y escenarios completos de corrección/devolución.
