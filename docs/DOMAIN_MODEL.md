undefined

## Checkout editable y terminales de pago

- Cart y CartRevision: carrito de trabajo y revisiones previas a confirmar la venta.
- CartLine y CartLineRemoved: línea activa y retiro/cambio previo al pago; una línea retirada no produce SaleLine ni InventoryMovement.
- CheckoutSession: congelación del carrito al iniciar el pago y correlación de los medios.
- PaymentIntent: obligación de cobro por importe y moneda, interna o externa.
- PaymentAttempt: intento individual con proveedor, terminal, idempotency key, referencia externa y estado.
- PaymentAllocation: distribución del total entre efectivo, terminal, transferencia, QR o cuenta.
- TerminalOrder: orden del proveedor y sus estados externos; se vincula con PaymentAttempt.
- PaymentReceiptReference: referencia del voucher de la terminal, distinta del ticket de venta y del FiscalDocument.
- CashTender y CashChange: efectivo recibido y vuelto entregado, con su impacto neto en CashMovement.
- FiscalDocument permanece separado: una terminal que imprime un voucher no se convierte por ello en emisor fiscal.

## Módulos externos y autoridad

Cada agregado tiene un módulo propietario. Los sistemas especializados reciben comandos y publican resultados por contrato; no escriben tablas de otros módulos. La referencia al módulo, proveedor, versión de esquema, evento y correlación se conserva para auditoría y conciliación.
