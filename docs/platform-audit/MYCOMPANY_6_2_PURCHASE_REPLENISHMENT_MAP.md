# MyCompany 6.2 — mapa de compras, proveedores y reposición

**Estado: lectura profunda parcial de pedidos, recepción, facturación vinculada, listas de precios y reposición automática; pruebas de runtime y conciliación pendientes.**

El dominio \`purchase\` contiene 49 módulos LSF y se integra con Inventario, Facturación, Fabricación y Datos maestros.

## 1. Inventario estructural

| Subdominio | Cantidad de módulos | Alcance |
|---|---:|---|
| Raíz y configuración | 2 | Composición y parámetros de compra |
| Pedidos de compra | 19 | Cabecera, líneas, tipo, estados, filtros, búsqueda, selección, correo, impresión, unidades, paquetes y deuda |
| Listas de precios de proveedor | 9 | Cabecera, líneas, tipo de importación, búsqueda, filtros, estado, valores e importación |
| Impresión de listas de precios | 2 | Plantillas/formatos de listas |
| Listas de precio de facturas de proveedor | 2 | Precio relacionado con facturas de proveedor y unidades |
| Recepciones ligadas al pedido | 4 | Creación de recepción, costo, estado y datos iniciales |
| Facturación de proveedor ligada al pedido | 7 | Crear factura, controlar estado, unidades, política de facturación, facturas/recepciones y datos iniciales |
| Fabricación ligada al pedido | 3 | Crear orden de fabricación, precio/lista y creación automática |
| Reportes | 1 | Reporte de pedidos |
| Despachos/abastecimiento automático | 1 | Cálculo de reposición por proveedor/periodo |

La suma por carpeta debe leerse junto con el inventario automático de módulos: algunas extensiones están ubicadas en subcarpetas compartidas de inventario/facturación y el producto se compone mediante \`REQUIRE\`.

## 2. Pedido de compra

Fuentes principales:
- \`purchase/orders/PurchaseOrder.lsf\`
- \`PurchaseOrderConfirmed.lsf\`
- \`PurchaseOrderSent.lsf\`
- \`PurchaseOrderCanceled.lsf\`
- \`PurchaseOrderLocked.lsf\`
- \`PurchaseOrderPartner.lsf\`
- \`PurchaseOrderItem.lsf\`
- \`PurchaseOrderType.lsf\`
- \`PurchaseOrderDebt.lsf\`

La cabecera incluye tipo, fecha, número, proveedor, empresa compradora, moneda, depósito/ubicación, condiciones de pago y datos logísticos. Los renglones incluyen artículo, unidad, cantidad, precio e importes.

Reglas identificadas:
- el proveedor debe estar clasificado como proveedor;
- la fecha y empresa se inicializan por defecto;
- las condiciones de pago pueden proponerse desde el proveedor;
- la cuenta del proveedor/empresa se valida contra su titular cuando se usa;
- el artículo debe poder comprarse;
- al cambiar artículo se puede proponer precio/costo predeterminado;
- se controlan conversiones de unidad y paquetes;
- se puede enviar al proveedor por correo e imprimir;
- hay estados para envío, confirmación, bloqueo y cancelación.

La confirmación es el punto que habilita circuitos de recepción, facturación y fabricación según tipo y configuración.

## 3. Pedido → recepción → inventario

Fuentes:
- \`purchase/inventory/receipts/orders/PurchaseOrderReceipt.lsf\`
- \`PurchaseOrderReceiptCost.lsf\`
- \`PurchaseOrderReceiptInitial.lsf\`
- \`PurchaseOrderReceiptStatus.lsf\`

La recepción mantiene relación con pedido y línea original. El sistema:
- calcula cantidad a recibir y convierte unidades mediante el coeficiente SKU;
- crea/actualiza una recepción de reserva cuando el pedido está confirmado y tiene ubicación/tipo de recepción;
- crea líneas de recepción vinculadas a las líneas del pedido;
- guarda la demanda inicial de recepción y controla lo efectivamente recibido;
- impide exceder la cantidad del pedido;
- permite recepciones parciales y, por tanto, varias recepciones para cubrir un pedido;
- según el tipo de pedido, impide bloquearlo si hay recepciones activas o si no está totalmente recibido;
- la extensión de costo copia el precio del pedido a la recepción y lo prorratea por coeficiente de unidad.

**Distinción:** la recepción prevista/reservada no es el mismo hecho que la mercadería efectivamente recibida. Debe comprobarse qué estado impacta stock, lote, costo y contabilidad.

**Pendiente:** recepción con diferencias, faltantes, sobrantes, sustituciones, lote/serie, ubicación, costos adicionales, recepción parcial, rechazo y reversión.

## 4. Pedido → factura de proveedor

**Pasaporte de integración relacionado:** [SupplierBillLifecycle](modules/SupplierBillLifecycle.md), que amplía este mapa con Bill, BillReceipt, deuda, pago, cuenta y la precedencia de costos.

Fuentes:
- \`purchase/invoicing/bills/orders/PurchaseOrderBill.lsf\`
- \`PurchaseOrderBillStatus.lsf\`
- \`PurchaseOrderBillInitial.lsf\`
- \`PurchaseOrderBillUom.lsf\`
- \`PurchaseOrderBillReceipt.lsf\`
- \`PurchaseOrderBillReceiptInitial.lsf\)

El tipo de pedido define:
- tipo de factura de proveedor;
- política de facturación;
- si se prohíbe bloquear el pedido con cantidades sin pagar.

La fuente distingue dos políticas explícitas:

1. **Cantidad pedida (\`ordered\`):** calcula lo que queda por facturar según cantidad del pedido menos cantidad ya facturada.
2. **Cantidad recibida (\`delivered\`):** toma las líneas de recepción activas, con cantidad efectivamente recibida y todavía no facturada; crea líneas de factura vinculadas a la recepción y al pedido.

La factura conserva la relación con el origen. Se muestran cantidades facturadas y pagadas por línea y se impide superar el límite del pedido. La política \`delivered\` registra qué línea de factura consumió la línea de recepción, evitando volver a facturar esa misma recepción.

La deuda, los pagos y los saldos se resuelven por las clases del dominio \`Invoicing\`; consultar [MYCOMPANY_6_2_INVOICING_LEDGER_MAP.md](MYCOMPANY_6_2_INVOICING_LEDGER_MAP.md).

**Pendiente:** factura parcial, diferencia de precio, diferencia de cantidad, impuestos, moneda, recepción no facturada, factura sin recepción, cancelación, devolución y corrección. El pago/deuda/ledger de cuenta y el costo de recepción originado en factura se analizan en el pasaporte SupplierBillLifecycle; no se consideran aceptados por la revisión estática.

## 5. Listas de precios de proveedor

Fuentes:
- \`purchase/pricelists/PurchasePricelist.lsf\`
- \`PurchasePricelistValue.lsf\`
- \`PurchasePricelistImport.lsf\`
- \`PurchasePricelistImportGenerate.lsf\`
- \`PurchasePricelistDone.lsf\`
- \`PurchasePricelistFilter.lsf\`
- \`PurchasePricelistItem.lsf\`
- \`PurchasePricelistPartner.lsf\`

Una lista de proveedor guarda:
- proveedor;
- fecha inicial/final y estado;
- líneas por artículo;
- nombre y referencia del artículo según proveedor;
- precio;
- archivos y comentarios;
- búsquedas y filtros por artículo/precio.

El selector de precio para un artículo busca la última lista terminada del proveedor dentro de la vigencia correspondiente. Hay una variante que busca el último precio de cualquier proveedor; otra propiedad usa el costo del artículo como alternativa cuando no hay precio de lista.

### 5.1 Importación de listas

- Se pueden configurar tipos de importación y asignarlos a proveedores.
- El tipo guarda un script; la macro construye un JSON de importación que indica tipo \`action\`.
- El generador permite indicar columnas para ID, código de barras, nombre, unidad y precio; también fila de inicio y si se usa la referencia como ID.
- La acción ejecuta el script configurado mediante \`EVAL ACTION\` con el objeto de lista de precios.

**Riesgo de seguridad:** el script de importación es código ejecutable. Se debe limitar quién lo crea/edita/ejecuta, validar su contenido, restringir recursos y datos accesibles y registrar resultado/errores. No debe ser un campo editable por cualquier usuario de compras.

**Pendiente:** formatos reales de proveedores, CSV/XLSX/PDF, codificación, separador decimal, IVA, moneda, SKU/GTIN, artículos duplicados, líneas inválidas, idempotencia y rollback.

## 6. Reposición automática por proveedor

Fuente: \`purchase/inventory/shipments/orders/PurchaseOrderShipmentAuto.lsf\`.

La extensión agrega al proveedor un período de compra. Al cambiar el proveedor del pedido calcula el intervalo desde/hasta que se analiza. El módulo calcula previsión periódica y cantidad sugerida de pedido; luego crea líneas para los artículos cuya previsión indique necesidad.

**Relación con fabricación:**
- \`PurchaseOrderManufacturingAuto.lsf\` calcula consumo periódico de materiales en órdenes de fabricación activas;
- considera depósito/ubicación de materiales y estructura de ubicaciones;
- incorpora consumo previsto y pendiente para el período de reposición.

La cantidad sugerida se calcula en el módulo base combinando previsión, espera/demanda y datos de períodos. Hay que seguir todas las propiedades abstractas y extensiones que contribuyen a esa fórmula antes de tratarla como una regla de reabastecimiento completa.

**Pendiente:** stock disponible/reservado, órdenes abiertas, pedidos en tránsito, mínimo/múltiplo, lead time, calendario de proveedor, consumo estacional, demanda comercial, unidades, MOQ, pack, seguridad de stock, parámetros por depósito y redondeo.

## 7. Pedido de compra → fabricación

Fuentes:
- \`purchase/manufacturing/orders/PurchaseOrderManufacturing.lsf\`
- \`PurchaseOrderManufacturingAuto.lsf\`
- \`PurchaseOrderManufacturingPricelist.lsf\`

El pedido puede estar relacionado con líneas de consumo de órdenes de fabricación. La relación permite identificar qué materiales y cantidades se compraron para qué orden de fabricación. Se valida que el artículo de la línea de compra coincida con el material consumido de la orden.

El circuito puede generar compras a partir de necesidades de fabricación y debe preservar la referencia entre pedido, línea, consumo y producción.

**Pendiente:** agrupación por proveedor, múltiples órdenes de fabricación, proveedor alternativo, compra parcial, cambios en BOM, replanificación, sobrecompra y cierre de órdenes ya empezadas.

## 8. Integración con inventario, deuda y costo

El dominio de compras trabaja con módulos de inventario para las recepciones y módulos de facturación para las facturas de proveedor. La estructura incorpora:
- cantidad ordenada/recibida/facturada/pagada;
- precio y costo por línea;
- movimiento físico de recepción;
- lote/serie y costo de recepción cuando están activados;
- deuda con el proveedor y pagos salientes;
- calendario de vencimientos y saldo de cuentas.

No se debe asumir que el total de una factura equivale al costo de stock. El costo puede incluir costos adicionales, servicios, impuestos y ajustes que pertenecen a módulos distintos.

## 9. Pruebas necesarias

| Circuito | Escenarios mínimos |
|---|---|
| Pedido | Borrador, enviado, confirmado, bloqueado, cancelado, copia y cambio de proveedor |
| Recepción | Total, parcial, varias recepciones, exceso, faltante, devolución, lote/ubicación |
| Facturación por pedido | Política \`ordered\`, parciales y bloqueo |
| Facturación por recibido | Política \`delivered\`, varias recepciones y no doble facturación |
| Precio proveedor | Lista vigente, vencida, lista futura, ausencia y proveedor alternativo |
| Importación | Columnas cambiadas, fila inicial, referencia/ID, duplicados, filas inválidas y script malformado |
| Reposición | Demanda/forecast, ventas, compras abiertas, consumo de fabricación, depósitos y múltiplos |
| Costos | Precio de compra, coeficiente SKU, gastos adicionales y conciliación con costo de inventario |
| Cuenta y deuda | Factura, pago parcial, nota de crédito, vencimiento y moneda |

## 10. Estado

Las fuentes revisadas permiten identificar el pedido de compra, la reserva/recepción, las políticas de facturación por pedido o recibido, las listas de precios de proveedor, la importación configurable, la reposición automática y las relaciones con fabricación.

**El dominio no está cerrado:** quedan por leer y probar individualmente las extensiones, todos los estados y filtros, reportes, integraciones, excepciones de compra y la conciliación completa con inventario, deuda y costos.
