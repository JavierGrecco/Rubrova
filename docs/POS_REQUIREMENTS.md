undefined

## Checkout detallado y eliminación de artículos antes del cobro

El carrito es una operación editable, no una venta confirmada. Cada escaneo agrega o incrementa una línea y recalcula el total. Antes de iniciar el cobro, el cajero puede quitar productos o reducir cantidades. El sistema recalcula promociones, descuentos, impuestos y total, libera reservas temporales y no genera salida de stock, pago ni comprobante por los artículos retirados.

Una vez que se envió una orden a una terminal, el importe y el carrito quedan congelados mientras la terminal procesa. Para cambiar el carrito hay que cancelar primero la orden pendiente y esperar confirmación. Si el cobro ya fue aprobado, el cambio se gestiona como devolución/reembolso o nueva venta vinculada, nunca como edición silenciosa.

## Cobro en efectivo y vuelto

La pantalla solicita el importe recibido del cliente, calcula el vuelto exacto y muestra también el faltante cuando el efectivo no alcanza. Se calculan importes con unidades monetarias menores enteras para evitar errores de coma flotante. En pago mixto, el efectivo que ingresa a caja es el importe recibido menos el vuelto; no se registra todo el total como efectivo si parte se cobró por otro medio.

## Terminal bancaria integrada

El checkout debe poder crear una solicitud en la terminal asignada a la caja, transmitir el importe exacto, detectar la respuesta aprobada/rechazada/cancelada y registrar el resultado en el pago correspondiente. Se implementa un adaptador por proveedor y modelo de dispositivo. La selección de tarjeta en pantalla no es aprobación: solo el estado final confirmado por proveedor permite completar ese tramo del pago.

Un timeout, webhook repetido o cancelación asíncrona debe resolverse por consulta y conciliación, no con un cobro nuevo a ciegas. La pantalla debe informar cuando un pago queda pendiente de confirmación.

## Ticket de venta, voucher y factura

El ticket detallado de Rubrova, el voucher de la terminal y la factura fiscal son documentos diferentes. Pueden imprimirse en dispositivos distintos. La impresión desde una terminal solo se habilita para modelos y firmware que documenten esa función; no se presume que todos los adquirentes impriman el ticket de Rubrova o un comprobante fiscal.

Ver [Checkout y terminales](CHECKOUT_AND_PAYMENT_TERMINALS.md) para el flujo, capacidades investigadas de Mercado Pago Point/Getnet/Fiserv Posnet/Payway y escenarios de aceptación.
