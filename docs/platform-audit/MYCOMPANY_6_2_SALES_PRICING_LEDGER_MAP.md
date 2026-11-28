# MyCompany 6.2 — mapa de ventas, precios, descuentos y ledger comercial

**Estado: análisis profundo parcial; pruebas de runtime y conciliación completas pendientes.**

El dominio \`sales\` tiene 92 módulos LSF. El alcance va desde el pedido de venta hasta despacho, facturación, cobro, compra/fabricación disparada por demanda, lista de precios, descuentos, márgenes y reportes.

## 1. Inventario del dominio

| Área | Módulos LSF |
|---|---:|
| Núcleo y configuración | 2 |
| Pedidos, estados, tipos, selección, búsqueda, impresión, correo, API y móvil | 19 |
| Listas de precios y valores | 9 |
| Tipos de precio | 3 |
| Impresión de listas de precios | 4 |
| Descuentos y condiciones | 6 |
| Reportes | 6 |
| Despachos y picking vinculados a pedidos | 6 |
| Facturación ligada al pedido y su ledger | 5 |
| Ledger comercial y cuentas | 5 |
| Integración con facturación de proveedor | 3 |
| Integración con compras | 3 |
| Integración con fabricación | 2 |
| Descuentos por ubicación y cuentas tributarias | 1 o más extensiones transversales |

El inventario de 92 archivos incluye extensiones repartidas en subcarpetas de inventario, facturación, compras, fabricación y reportes. El registro estructural automático contiene el nombre y la ruta de cada archivo; el presente mapa explica el funcionamiento que ya se pudo seguir en fuente.

## 2. Pedido de venta

Fuentes principales:
- \`sales/orders/SalesOrder.lsf\`
- \`SalesOrderConfirmed.lsf\`
- \`SalesOrderSent.lsf\`
- \`SalesOrderCanceled.lsf\`
- \`SalesOrderLocked.lsf\`
- \`SalesOrderType.lsf\`
- \`SalesOrderPartner.lsf\`
- \`SalesOrderItem.lsf\`
- \`SalesOrderPricelist.lsf\`
- \`SalesOrderTax.lsf\`
- \`SalesOrderDiscount.lsf\`
- \`SalesOrderDebt.lsf\`

### 2.1 Datos y validaciones

El pedido registra tipo, cliente, empresa, fecha, fecha prevista de entrega, ubicación, dirección de entrega, representante, moneda, condiciones de pago, líneas, cantidades, precios y descuentos.

- El tipo puede proponer cliente/empresa, moneda, depósito y otras opciones.
- El socio debe poder actuar como cliente.
- La cuenta del cliente y la cuenta propia deben pertenecer a sus titulares.
- El artículo de cada línea debe estar habilitado para venta.
- Al seleccionar artículo se completan unidad de medida y precio predeterminado si no se modificaron manualmente.
- El tipo/cliente puede determinar el tipo de precio y la configuración de impuestos incluidos o separados.
- La ubicación debe ser utilizable y no estar marcada como de uso interno cuando la regla lo prohíbe.

### 2.2 Estados y acciones

El código separa borrador, enviado, confirmado, bloqueado y cancelado mediante módulos de extensión. El flujo visible incluye envío por correo, confirmación, bloqueo, cancelación, copia, búsqueda y selección múltiple.

El estado confirmado habilita el circuito de cumplimiento. El pedido no es todavía un despacho, una factura ni un cobro: esas entidades nacen en módulos conectados y mantienen referencias al pedido o sus líneas.

### 2.3 Pedido → despacho

Fuentes:
- \`sales/inventory/shipments/orders/SalesOrderShipment.lsf\`
- \`SalesOrderShipmentInitial.lsf\`
- \`SalesOrderShipmentStatus.lsf\`
- \`SalesOrderShipmentPickingTask.lsf\`
- \`SalesOrderShipmentCost.lsf\`

Al confirmar un pedido, si el tipo dispone de tipo de despacho y ubicación, se puede crear un despacho de reserva. El modelo distingue:
- cantidad pedida;
- cantidad que se pretende despachar;
- cantidad reservada;
- cantidad efectivamente despachada.

Se puede ejecutar el pedido mediante varios despachos parciales. La reserva no equivale a una salida física de stock; el movimiento definitivo se produce cuando el despacho se completa/realiza. Los controles impiden exceder la cantidad pedida y, según el tipo, bloquear un pedido con despachos activos o cantidades pendientes.

El módulo de picking agrega tareas/selección de artículos y cantidades para preparar el despacho. Se debe probar la operación con varios depósitos, lotes y ubicaciones, no sólo con un producto simple.

### 2.4 Pedido → factura

Fuentes:
- \`sales/invoicing/invoices/orders/SalesOrderInvoice.lsf\`
- \`SalesOrderInvoiceInitial.lsf\`
- \`SalesOrderInvoiceShipment.lsf\`
- \`SalesOrderInvoiceShipmentInitial.lsf\`
- \`SalesOrderInvoiceStatus.lsf\`

El tipo de pedido define la política de facturación:
- por cantidades pedidas;
- o por cantidades despachadas.

Se controla cuánto se facturó, cuánto se pagó y cuánto queda pendiente por línea. Es posible crear facturas parciales. La configuración del tipo determina si el pedido se puede bloquear con cantidades sin facturar o sin pagar.

### 2.5 Pedido → compras

Fuentes:
- \`sales/purchase/orders/SalesOrderPurchase.lsf\`
- \`SalesOrderPurchaseAdd.lsf\`
- \`sales/purchase/pricelists/SalesPricelistPurchase.lsf\`

El pedido de venta puede vincular órdenes de compra generadas para atender la demanda. El vínculo existe tanto a nivel de cabecera como de líneas y permite mostrar cantidades y referencias cruzadas.

**Pendiente:** estudiar cuándo se sugiere/crea una compra, agrupación por proveedor, SKU/unidades, compras parciales, reserva de mercadería recibida y conciliación de la cantidad finalmente entregada al cliente.

### 2.6 Pedido → fabricación

Fuentes:
- \`sales/manufacturing/orders/SalesOrderManufacturing.lsf\`
- \`SalesOrderManufacturingReport.lsf\`

El tipo de pedido puede asociarse a un tipo de orden de fabricación. Se puede elegir BOM por línea y crear órdenes de fabricación asociadas a ese pedido. Una opción \`autoCreateManufacturingOrder\` genera órdenes al confirmar el pedido y actualiza cantidad/producto/BOM cuando corresponde.

Hay restricciones explícitas: si la orden de fabricación asociada ya empezó, no se permite cancelar el pedido ni cambiar las cantidades, el artículo o la BOM de la línea. Tampoco se puede eliminar la línea que originó la fabricación.

**Conclusión:** la venta puede ser origen de una cadena de abastecimiento y producción. No hay que modelarla como un documento comercial aislado.

## 3. Tipos de precio y listas de precios

Fuentes principales:
- \`sales/pricelists/pricetypes/SalesPriceType.lsf\`
- \`SalesPriceTypeMarkup.lsf\`
- \`sales/pricelists/SalesPricelist.lsf\`
- \`SalesPricelistValue.lsf\`
- \`SalesPricelistChange.lsf\`
- \`SalesPricelistAPI.lsf\`
- \`SalesPricelistType.lsf\`
- \`SalesPricelistItem.lsf\`
- \`SalesPricelistInitial.lsf\`

### 3.1 Tipo de precio

Cada \`PriceType\` guarda:
- nombre e ID;
- moneda;
- si el precio incluye impuestos;
- asignación de tipo de precio predeterminado a un cliente.

El tipo de precio de un pedido se propone desde el cliente o tipo documental. Una regla controla la compatibilidad entre \`taxIncluded\` del tipo de pedido y del tipo de precio.

### 3.2 Lista y líneas

Una lista de precios:
- tiene tipo, número, fecha de inicio/fin y estado;
- define qué tipos de precio permite modificar (\`editIn\`);
- contiene líneas por artículo;
- puede almacenar costo, margen y precio por tipo de precio;
- puede adjuntar archivos y comentarios;
- se puede copiar, editar, marcar terminada e imprimir.

La fuente calcula el precio teniendo en cuenta costo histórico a la fecha de la lista, tipo de precio base, moneda y cotización, margen y coeficiente para compatibilizar impuestos incluidos/separados.

Hay controles para que no se elimine un tipo de precio cuando ya existen precios asociados y para limpiar valores cuando se desactiva la edición de ese tipo.

### 3.3 Validez temporal

\`SalesPricelistValue\` busca la última línea de una lista terminada cuyo intervalo de vigencia contiene la fecha solicitada. También obtiene precio anterior, fecha de inicio y referencia de lista.

Esto permite comparar una lista con la anterior y seleccionar el precio aplicable según fecha del pedido/documento.

### 3.4 Recálculo de precios

\`SalesPricelistChange\` incluye, al menos, tres operaciones:
- fijar márgenes tomando el precio de listas anteriores;
- fijar márgenes a partir de los márgenes definidos en tipos de precio/categorías/artículos;
- modificar precios a partir de precios anteriores con un porcentaje indicado.

Cuando se selecciona un artículo o se habilita un tipo de precio, se puede heredar el margen del artículo/categoría y calcular el precio.

### 3.5 API de precios

\`SalesPricelistAPI.lsf\` declara \`getPrices(type, time)\` con marca \`@@api\`. Busca el tipo de precio y exporta JSON con ID de artículo y precio vigente para la fecha pedida. Si no encuentra el tipo de precio, lanza una excepción.

**Pendiente:** contrato HTTP completo, autenticación/autorización, paginación, artículos sin ID, moneda, impuestos incluidos, vigencia horaria, duplicados, control de cambios e idempotencia. La marca \`@@api\` no sustituye la ficha de seguridad del endpoint.

## 4. Descuentos

Fuentes principales:
- \`sales/discounts/SalesDiscount.lsf\`
- \`SalesDiscountLine.lsf\`
- \`SalesDiscountItem.lsf\`
- \`SalesDiscountAttribute.lsf\`
- \`SalesDiscountPartner.lsf\`
- \`sales/inventory/discounts/SalesDiscountLocation.lsf\`
- \`SalesDiscountInvoice.lsf\`
- \`SalesDiscountInvoiceLedger.lsf\`
- \`SalesDiscountBillLedger.lsf\)

Un descuento contiene:
- fechas de inicio/fin;
- selección de categorías y artículos;
- tipos de precio aplicables;
- porcentaje o precio específico por tipo de precio;
- marca manual;
- umbral de importe de compra;
- cantidad mínima por línea;
- importe acumulado vendido al cliente;
- importe vendido al cliente durante el mes anterior;
- extensiones por atributos del artículo, etiquetas del socio y ubicación.

La macro de líneas de descuento calcula las coincidencias según artículo/categoría, fecha, tipo de precio, cantidad, importe, acumulado del cliente y acumulado del mes anterior. El cálculo de precio resultante puede venir de:
- aplicar el porcentaje de descuento al precio de la línea;
- o tomar el precio de una lista de precios elegida para el descuento.

Existe selección manual. Para descuentos automáticos el módulo elige una coincidencia según el precio resultante; la fuente usa un orden descendente y toma el último registro, por lo que debe verificarse con casos de empate y precios iguales.

Las reglas cambian ante modificaciones de cantidad, fecha, cliente, artículo, precio, tipo y ubicación, salvo que se desactive el recálculo o el descuento sea manual. Se incorpora un recálculo explícito para volver a procesar líneas.

**Pendiente:** reglas de acumulación y prioridad, descuentos superpuestos, empates, impuestos incluidos, artículos con variantes, devoluciones, actualización retroactiva de listas, promociones por cliente y auditoría de cambios. El mapa debe diferenciar descuentos de ventas, ajustes de factura y descuentos comerciales por línea.

## 5. Ledger comercial y márgenes

Fuentes:
- \`sales/ledgers/SalesLedger.lsf\`
- \`SalesLedgerAccount.lsf\`
- \`SalesLedgerPartner.lsf\`
- \`SalesLedgerAccountInvoice.lsf\`
- \`SalesLedgerInvoice.lsf\`
- \`sales/invoicing/bills/ledgers/SalesLedgerBill.lsf\`
- \`SalesLedgerBillReceipt.lsf\`
- \`sales/invoicing/inventory/shipments/SalesLedgerInvoiceShipment.lsf\`

La clase abstracta \`SalesLedger\` normaliza cada movimiento comercial con:
- tipo, fecha/hora, número, ubicación;
- artículo, cliente, cantidad y precio;
- costo calculado;
- importe sin impuestos, impuestos e importe total;
- marca para excluir el movimiento de ciertos acumulados.

El costo por defecto se calcula como cantidad por costo del artículo a la fecha del movimiento. Los módulos específicos agregan costos de movimientos físicos/despachos cuando corresponde.

El margen se calcula como importe sin impuestos menos costo; el porcentaje se calcula sobre el costo. Esa definición debe validarse contra el criterio de negocio esperado, porque no es lo mismo margen sobre costo que margen sobre venta.

### 5.1 Ledger desde facturas

\`SalesLedgerInvoice\` agrega líneas de facturas activas al ledger. Copia fecha, tipo, número, artículo, cliente, cantidad, precio, base, impuesto y total.

### 5.2 Cuentas comerciales

\`SalesAccount\` separa cuentas de ingreso, costo y cuentas personalizadas. \`SalesLedgerAccountInvoice\` asigna montos a cuentas por línea y permite desglose por cuenta en la factura; también registra componentes tributarios.

### 5.3 Ventas acumuladas por cliente

\`SalesLedgerPartner\` calcula:
- ventas iniciales declaradas manualmente;
- ventas acumuladas del cliente a partir del ledger;
- ventas totales con inicial;
- ventas por período mensual;
- ventas del mes anterior;
- valores previos de esos acumulados para evaluar reglas de descuento.

Estos acumulados se usan en descuentos por ventas históricas, por lo que cambios retroactivos en ledger, notas de crédito o exclusiones pueden repercutir en promociones.

**Pendiente:** comprobar conciliación factura ↔ ledger ↔ costo ↔ cuenta ↔ reporte, correcciones/devoluciones, múltiples monedas, impuestos, costo promedio/FIFO, cambios de fecha, exclusiones y consistencia del porcentaje de margen.

## 6. Reportes identificados

Los 6 módulos de \`sales/reports\` incluyen informes de:
- pedidos;
- ledger comercial;
- cuentas comerciales;
- descuentos;
- precios;
- resumen de ventas.

También hay reportes específicos de inventario y despachos en subcarpetas. Cada uno debe quedar vinculado a sus fuentes, filtros, agrupaciones, fórmula y población de documentos.

## 7. API, móvil y conectores

- \`SalesOrderAPI\` importa pedidos y líneas desde JSON mediante una acción expuesta con \`@@api\`; el código incluye borrado de pedidos en borrador según número de referencia.
- \`SalesPricelistAPI\` exporta precios vigentes por tipo y fecha.
- \`SalesOrderMobile\` / \`SalesOrderMobileSearch\` aportan formularios de trabajo móvil.
- \`SalesOrderGeo\` agrega datos de ubicación.
- \`SalesOrderEmail\` agrega correo/impresión al pedido.

Estos endpoints y capacidades requieren contratos separados: autenticación, permisos, límites, formato, errores, duplicados, consistencia y protección de datos.

## 8. Matriz de conciliación y pruebas

| Circuito | Pruebas necesarias |
|---|---|
| Pedido → despacho | Reserva, entrega parcial, varios depósitos, lotes, picking, falta de stock, cancelación |
| Pedido → factura | Política pedido/despacho, facturas parciales, pagos parciales, nota de crédito y reversión |
| Pedido → compra | Sugerencia, agrupación proveedor, recepción parcial y entrega al cliente |
| Pedido → fabricación | Creación manual/automática, BOM, cambio de cantidad, restricciones tras iniciar producción |
| Precio | Precio vigente, listas superpuestas, tipo/moneda/impuestos, cambio de precio y copia |
| Descuento | Manual/automático, umbrales, acumulado mensual, atributos, tags, ubicación y empate |
| Ledger | Facturas activas, cancelación, notas de crédito, costo histórico y ubicación |
| Reportes | Reconciliación de importe, base, impuesto, costo, margen y ventas por cliente |
| API | Importación repetida, referencia duplicada, autorización, error parcial y actualización |

## 9. Estado

La lectura de fuente ya identifica cómo se conectan pedidos, despachos, facturas, compras, fabricación, listas de precios, descuentos, API y ledger de ventas. Aún falta la prueba en runtime de esos recorridos y la conciliación de importes con inventario, facturación, costos y cuentas.

**El dominio de ventas no está cerrado:** la ficha de los módulos restantes, reportes y excepciones debe completarse antes de declarar cubiertos los 92 archivos.
