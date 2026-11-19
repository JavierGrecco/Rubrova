# Modelo de dominio

## Objetivo

Definir conceptos compartidos para que ventas, inventario, caja, facturación e inteligencia no calculen realidades distintas.

## Organización y ubicación

- Business: negocio propietario de los datos.
- Branch: sucursal.
- Location: depósito, salón, cocina, góndola u otra ubicación.
- Register: caja o terminal.
- Device: dispositivo que origina operaciones.
- User: persona con acceso individual.
- Shift: turno de un usuario o caja.

## Catálogo

- Product y Variant: artículo y presentación.
- SKU, Barcode y PLU: identificadores internos y externos.
- Brand, Category y UnitOfMeasure: marca, clasificación y unidad.
- SupplierProduct: relación con proveedor, código externo, presentación y costo.
- PriceList y PriceRecord: lista y precio con vigencia, moneda, canal y contexto.

Proveedor, marca y categoría son relaciones distintas, no una sola jerarquía. Una marca puede tener muchas categorías y un proveedor distribuir distintas marcas.

## Ventas y pedidos

- Order: intención comercial originada en un canal.
- Sale: operación confirmada.
- SaleLine: artículo, cantidad, unidad, precio y fotografía de valores.
- DiscountApplication: regla e importe del descuento.
- Promotion y CouponRedemption: campaña y uso.
- Return y Cancellation: devolución o anulación vinculada al original.
- Fulfillment: preparación, retiro, envío y entrega.

Un pedido externo no se convierte en una segunda venta si representa la misma operación. Debe tener clave externa única e idempotencia.

## Pagos, caja y cuentas

- PaymentIntent, Payment y PaymentAllocation.
- Refund vinculado a un pago.
- CashMovement y CashSession.
- CustomerAccountEntry y SupplierAccountEntry.

No confundir pago pendiente con acreditado ni saldo de cuenta con efectivo en caja.

## Inventario y compras

- InventoryBalance: saldo calculado/materializado por producto, ubicación, lote y estado.
- InventoryMovement: entrada, salida, reserva, liberación, transferencia, ajuste o reversión.
- StockReservation.
- PurchaseOrder, GoodsReceipt y SupplierInvoice.
- StockCount, InventoryAdjustment y Lot.

El saldo no es el único registro: los movimientos permiten reconstruir cómo se llegó a él.

## Producción

- Recipe y RecipeVersion.
- ProductionOrder y ProductionBatch.
- IngredientConsumption y ProductionOutput.
- WasteMovement y FinishedGoodsMovement.

Conservar la versión de receta o costo de referencia utilizada cuando corresponda.

## Fiscalidad

- FiscalDocument: factura, ticket, nota de crédito/débito u otro comprobante.
- FiscalIssuer: sistema que emitió el documento.
- FiscalAuthorization: CAE, CAEA u otra autorización.
- FiscalReference y FiscalReconciliation.

Debe existir unicidad por obligación fiscal y referencia de operación. Un documento externo se vincula; no se vuelve a emitir automáticamente.

## Auditoría

AuditEvent, Approval, ReasonCode, ActorContext y EvidenceReference permiten registrar acción, autorización, responsable y evidencia.

## Movimientos no comerciales

Clasificaciones: consumo propio, personal, muestra, degustación, compensación, donación, uso de producción, rotura, vencimiento o devolución a proveedor.

Cada movimiento conserva cantidad, costo de referencia, responsable, autorización, motivo y tratamiento documental/fiscal correspondiente. Puede tener vista restringida, pero sigue disponible para auditoría y control. No se admite una categoría para ocultar ventas o eliminar rastros.

## Reglas de consistencia

- Importes con precisión decimal y moneda explícita.
- Cantidad siempre asociada a unidad.
- Fechas con contexto de zona horaria.
- Correcciones relacionadas con el original.
- Idempotencia para operaciones externas.
- Cambios de precio, costo, unidad o clasificación no reescriben operaciones pasadas.
- Estados comerciales, de pago, inventario y fiscales independientes y correlacionables.
