# Checkout, caja y terminales de pago

**Revisión:** 19 de noviembre de 2026  
**Estado:** requerimiento funcional definido; integraciones por proveedor pendientes de homologación y prueba con terminal física.

## Objetivo

El cajero debe poder escanear artículos, ver el total actualizado, corregir el carrito antes del cobro, cobrar en efectivo con vuelto exacto o enviar el importe a una terminal integrada. El resultado confirmado vuelve a Rubrova y queda vinculado a la venta.

## Flujo de venta

1. El cajero inicia sesión y toma una caja/turno abierto y autorizado.
2. Escanea un código o busca un producto. El artículo se agrega o incrementa en el carrito con variante, unidad, precio y cantidad.
3. Cada escaneo recalcula subtotal, descuentos, impuestos aplicables y total.
4. Antes de iniciar el cobro, puede editar cantidades o quitar una línea. El sistema recalcula promociones, descuentos, impuestos y total; libera reservas temporales.
5. El producto quitado no forma parte de la venta confirmada ni genera salida de stock, pago o comprobante.
6. El cliente paga con uno o varios medios. Se conserva el importe y estado de cada medio.
7. No se finaliza el pago hasta que la suma cubra el total o exista una modalidad de saldo/fiado autorizada.
8. Rubrova confirma la venta una sola vez y registra los movimientos vinculados de pago, caja e inventario.
9. Se entrega el ticket de venta y, cuando corresponda, se obtiene o vincula el comprobante fiscal.

Una vez enviada una orden a la terminal, el carrito queda congelado. Para cambiarlo, primero se cancela la orden pendiente y se espera confirmación. Si el pago ya fue aprobado, cualquier cambio es devolución/reembolso o nueva operación vinculada, nunca edición silenciosa.

## Efectivo y vuelto exacto

La pantalla muestra total asignado a efectivo, campo grande para ingresar el importe recibido, vuelto calculado automáticamente y faltante cuando no alcanza.

- Vuelto = efectivo recibido − importe asignado a efectivo, si la diferencia es positiva.
- Si el efectivo no alcanza, se muestra cuánto falta; se puede completar con otro medio o ajustar el importe.
- Efectivo neto en caja = efectivo recibido − vuelto.
- Los cálculos se realizan en unidades monetarias menores enteras (centavos), no con coma flotante binaria.
- En pagos mixtos, no se registra el total de la venta como efectivo si parte se cobró por otro medio.

## Terminal bancaria integrada

Rubrova necesita un adaptador por adquirente/proveedor y modelo de terminal. No todos los dispositivos soportan la misma API, impresión, cancelación o modo desconectado.

1. Rubrova congela el checkout y crea un PaymentIntent interno con ID único.
2. El adaptador selecciona la terminal vinculada a la caja/sucursal y transmite importe, moneda y referencia externa única.
3. El cliente opera sobre la terminal; Rubrova no captura ni almacena número completo de tarjeta, banda, PIN ni CVV.
4. El proveedor comunica el resultado por respuesta, consulta y/o webhook autenticado.
5. Rubrova valida firma, referencia, importe, moneda, terminal y estado final. Los webhooks repetidos son idempotentes.
6. Solo un estado final aprobado/confirmado permite marcar ese pago como cobrado. La orden creada o enviada a terminal no es pago aprobado.
7. Si se rechaza o cancela, se vuelve al selector de medios sin cerrar la venta.
8. Si hay timeout o estado desconocido, el pago queda pendiente; se consulta/reconcilia antes de crear otro intento.
9. Una cancelación asíncrona no es final hasta que el proveedor confirme que la terminal no cobró.
10. Los reembolsos se vinculan al pago original.

## Proveedores investigados

| Proveedor | Capacidad documentada | Límites y requisitos | Estado |
|---|---|---|---|
| Mercado Pago Point | Orders API, asignación de terminal, estados, consulta, cancelación, reembolso y webhooks | Access Token en backend; referencia/idempotencia. La terminal Smart puede imprimir acciones personalizadas según versión y configuración. | Primer adaptador a evaluar |
| Getnet Get POS Integrado | Importe enviado desde sistema y resultado devuelto a la caja | API cloud-to-cloud o SDK local USB/Wi-Fi según solución/partner; requiere habilitación y terminal integrada. | Segundo adaptador a evaluar |
| Fiserv / Posnet | POS Integrado “Trx a Trx”: conecta sistema de facturación con medio de captura y transmite transacciones al sistema del comercio en línea | El reglamento Fiserv describe programa y cable; el uso de sistemas/equipos propios está sujeto a certificación y homologación. Se debe solicitar protocolo y modelos compatibles. | Investigar en prioridad |
| Payway / Prisma PayStore Terminals | El portal oficial publica APIs de Terminal Payments, Terminal Refunds, Terminal Reversals y Terminal Settlements; también ofrece terminales integradas y PINpad conectados al sistema de gestión | Requiere revisar catálogo técnico, credenciales, modelo, certificación y disponibilidad para el comercio. Los comprobantes pueden ser digitales y no siempre imprimirse en papel. | Candidato prioritario para prueba técnica |
| Mobbex Smart POS | Plataforma comercial multi-adquirente con API de integración de terminal y conciliación; anuncia compatibilidad con Ingenico, Urovo, Verifone, NexGo y Newland | No es código abierto ni un componente para incorporar sin costo: requiere revisar alta, tarifas, adquirentes, contrato, API y hardware. Puede reducir el número de integraciones directas. | Alternativa comercial a cotizar y comparar |

### Mercado Pago Point: estados relevantes

- created: la orden existe, pero la terminal todavía no la obtuvo.
- at_terminal: la terminal obtuvo la orden; aún no significa cobrado.
- action_required: se requiere revisar/confirmar el resultado en la terminal; aún no se acredita.
- processed con el detalle de transacción acreditada: pago completado y acreditado.
- failed, canceled o expired: pago no completado.
- refunded o partially_refunded: reembolso total o parcial.
- at_terminal con status_detail cancellation_requested: la solicitud de cancelación fue aceptada, pero es asíncrona. Una respuesta HTTP 202 no confirma que la terminal haya cancelado; hay que esperar el webhook final y conciliar.

Las notificaciones incluyen procesamiento, cancelación, reembolso, acción requerida, error y expiración. Rubrova valida la firma, registra el evento de forma idempotente y consulta el estado cuando necesita recuperarse.

Para nuevas integraciones se sigue Orders API, no la API heredada Payment Intents si la documentación vigente indica migración.

## Tres documentos diferentes

1. **Ticket de venta de Rubrova:** artículos, cantidades, descuentos, impuestos y medios de pago.
2. **Voucher de la terminal:** comprobante del adquirente con resultado de la transacción.
3. **Comprobante fiscal:** factura, ticket fiscal o nota emitida por ARCA o por el emisor autorizado del canal.

Mercado Pago documenta acciones de impresión de contenido personalizado en terminales compatibles y permite consultar el estado de la acción. La función, el papel y el formato exacto deben confirmarse en el modelo/firmware disponible. Payway informa que ciertos comprobantes de tarjeta pueden enviarse por email y no imprimirse en papel. Esto no significa que cualquier Point, Posnet, Getnet o Payway imprima el ticket detallado de Rubrova o una factura fiscal.

## Desconexión y fallos

- Sin terminal conectada, la venta no se marca como cobrada con tarjeta.
- Se puede ofrecer otro medio habilitado, dejar el carrito pendiente o abandonar la operación.
- Si la terminal acepta pero la respuesta se pierde, el estado queda pendiente; consultar al proveedor antes de repetir.
- Si existe modo autónomo/desconectado, registrar como pago externo pendiente de conciliación con evidencia; nunca inventar autorización.
- No reutilizar la misma orden para otro cliente ni duplicar pagos por reintentos.

## Compatibilidad por sistema operativo

La lógica de checkout y pagos vive en contratos neutrales. La comunicación física se implementa mediante adaptadores:

- USB/serie/red local/SDK nativo: puente local para Windows, Linux y macOS según soporte real del fabricante.
- API cloud-to-cloud y webhooks: adaptador de servidor, independiente del OS del puesto si hay conexión.
- Impresoras ESC/POS, cajón, scanner y balanza: capacidades distintas del terminal bancario.
- Si un SDK solo existe para Windows o Android, se puede integrar detrás del contrato y desarrollar otro adaptador más adelante.
- La matriz registra proveedor, modelo, firmware, OS del puente, conexión, API y pruebas.

## Pruebas de aceptación

- Escanear uno o varios artículos y ver total actualizado.
- Quitar una línea antes de pagar; recalcular descuentos/impuestos y no registrar stock para el artículo retirado.
- Ingresar efectivo exacto, mayor y menor; vuelto/faltante correctos al centavo.
- Pagar en efectivo más tarjeta y conciliar caja.
- Simular aprobación, rechazo, cancelación, expiración, acción requerida, webhook repetido y timeout.
- Impedir cambios silenciosos del carrito mientras la terminal procesa.
- Reconciliar un pago posiblemente aprobado sin crear otro.
- Comprobar por separado voucher terminal, ticket de venta y comprobante fiscal.
- Reembolsar total/parcial y comprobar efectos.
- Probar cada terminal/modelo/OS, no solo un emulador.

## Fuentes primarias

- Mercado Pago Point — procesamiento: https://www.mercadopago.com.ar/developers/es/docs/mp-point/payment-processing
- Mercado Pago Point — webhooks: https://www.mercadopago.com.ar/developers/es/docs/mp-point/notifications
- Mercado Pago Point — estados: https://www.mercadopago.com.ar/developers/es/docs/mp-point/resources/status-order-transaction
- Mercado Pago Point — impresión: https://www.mercadopago.com.ar/developers/es/docs/mp-point/configure-printings
- Getnet — POS Integrado: https://www.getnet.net/ar/ayuda/terminales-getpos/get-pos-integrado
- Getnet — solución: https://www.getnet.net/ar/nuestras-soluciones/cobros-presenciales/pos-integrado
- Fiserv — Reglamento de Comerciantes 13/04/2026: https://www.fiserv.com.ar/content/dam/firstdata/ar/es/pdf/Reglamento_de_Comerciantes_13-04-26.pdf
- Payway — catálogo de APIs: https://developers.payway.com.ar/catalog?category=Pagos
- Payway — terminales/PINpad: https://www.payway.com.ar/terminales-punto-venta
- Mobbex — Smart POS multi-adquirente: https://www.mobbex.com/smart-pos/

La habilitación comercial, modelos, firmware y certificación deben confirmarse con cada adquirente antes de producción.
