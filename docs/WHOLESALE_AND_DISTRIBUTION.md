# Venta mayorista y distribución B2B

**Revisión:** 19 de noviembre de 2026  
**Estado:** alcance funcional definido; reglas y cifras reales se configurarán por área, cliente, producto, territorio y contrato.

## Objetivo

El área mayorista/distribuidora necesita un circuito distinto del mostrador minorista. Debe atender compradores empresariales, negociar condiciones, aplicar mínimos y escalas, gestionar crédito, preparar pedidos grandes, dividir entregas y seguir despachos hasta el retiro o la entrega final.

El sistema no debe forzar al mayorista a simular una venta minorista con cantidades grandes. Debe poder operar con vendedores, listas acordadas, pedidos recurrentes, depósitos, picking, entregas parciales y conciliación logística.

## 1. Cuenta B2B y condiciones del comprador

Una cuenta empresarial debe contemplar:
- razón social, CUIT, condición fiscal y domicilios;
- organización matriz, sucursales y establecimientos de entrega;
- compradores y contactos autorizados, teléfonos y correos;
- territorio, vendedor responsable y zona de reparto;
- listas de precio, acuerdos, descuentos, vigencia y moneda;
- condiciones de pago, plazo, límite de crédito y exposición abierta;
- requisitos de compra, horarios, documentación de recepción;
- condiciones de retiro o transporte preferidas;
- historial de cotizaciones, pedidos, devoluciones, pagos y reclamos.

Una misma cuenta puede comprar en diferentes áreas y canales. Las condiciones especiales son relaciones cuenta-área, no clientes duplicados.

## 2. Mínimos de compra y unidades comerciales

El motor debe soportar mínimos en varios niveles:

| Regla | Ejemplo |
|---|---|
| Mínimo por SKU | Comprar al menos 6 unidades de un artículo |
| Múltiplo de empaque | Vender cajas de 12, no 13 unidades |
| Mínimo por variante | Un color/tamaño solo se vende en bultos de 4 |
| Mínimo por familia | Combinar 24 unidades entre artículos de una familia |
| Mínimo del pedido | Total mayorista de al menos ARS 50.000 |
| Mínimo por zona/ruta | Pedido mínimo para justificar un reparto local |
| Mínimo por contrato | Entrega programada con volumen comprometido |
| Mínimo por período | Compra acumulada mensual o trimestral |

Las cantidades de compra y de stock pueden usar unidades distintas. El sistema debe registrar factor de conversión (unidad, pack, caja, bulto, kg, litro), precisión, redondeo y código logístico. Una caja de 12 no puede interpretarse como 12 cajas ni duplicar stock.

Cuando no se alcanza un mínimo, cada política debe ser explícita:
- impedir confirmar;
- sugerir completar el mínimo;
- aplicar precio minorista/otra lista;
- cobrar recargo de pedido pequeño;
- permitir excepción con autorización y motivo.

No se debe cambiar el precio o el mínimo silenciosamente.

## 3. Listas y escalas por volumen

Se necesitan:
- lista minorista, mayorista, distribuidor, revendedor, institucional y por contrato;
- precios específicos por cliente, grupo, territorio, canal, moneda y vigencia;
- escalas por cantidad, valor del pedido, combinación de productos o volumen acumulado;
- precio por empaque y por unidad alternativa;
- descuentos por línea, familia, cesta o campaña;
- acuerdos especiales por cliente y excepciones autorizadas;
- promociones acumulativas/no acumulativas con prioridad explícita;
- bonificaciones en unidades y notas de crédito/rebate posterior.

Ejemplo ilustrativo de una escala:
- 1 a 11 unidades: precio base;
- 12 a 23: precio mayorista nivel 1;
- 24 o más: precio nivel 2.

La escala puede ser por línea, por grupo de artículos o por cesta. El sistema tiene que indicar qué regla aplicó, qué umbral alcanzó y cuál fue el ahorro. Si varias reglas coinciden, la precedencia y la combinación deben estar definidas y probadas.

### Precedencia comercial sugerida

1. Condición contractual vigente del cliente y producto.
2. Precio individual negociado por cliente.
3. Lista del grupo/segmento de cliente.
4. Lista del área y canal.
5. Lista general.

Las promociones se evalúan después de identificar elegibilidad y respetan su política de stacking. Toda cotización/pedido conserva la fotografía del precio, lista, regla, versión, vigencia, descuento, impuestos y usuario que autorizó una excepción. Un cambio de lista no reescribe pedidos ya aceptados.

## 4. Cotización, pedido y crédito

Flujo sugerido:
1. Consulta/solicitud del comprador.
2. Cotización con cantidades, precios, mínimos, disponibilidad y vigencia.
3. Revisión comercial y autorización de excepción si corresponde.
4. Pedido confirmado con dirección, modalidad y fecha deseada.
5. Validación de crédito, deuda vencida, límite y pagos anticipados.
6. Reserva/compromiso de stock según política.
7. Preparación y fulfillment.
8. Facturación según el momento fiscal configurado para la operación.
9. Cobro, cuenta corriente y conciliación.

Un pedido puede estar confirmado sin estar facturado, despachado o cobrado. Son estados distintos. La orden comercial no debe provocar movimientos contables o de stock antes del evento configurado.

## 5. Venta y despacho son objetos diferentes

Este punto es central para el escenario de distribución:

- **Pedido:** compromiso comercial, cantidades y condiciones aceptadas.
- **Venta/factura:** documento económico/fiscal emitido según reglas y momento aplicables.
- **Fulfillment:** tarea de preparar y cumplir el pedido.
- **Despacho/envío:** movimiento físico de mercancía, que puede crearse después de la venta.
- **Guía/tracking del transportista:** referencia externa, muchas veces desconocida al momento de cobrar/facturar.

No se obliga a conocer el número de guía cuando se registra la venta. La operación puede quedar con entrega pendiente y asociar el transportista y su referencia posteriormente.

Un pedido puede dividirse en varias entregas parciales. Una entrega puede contener líneas de más de un pedido cuando la consolidación sea válida. Cada envío conserva su propia identidad y trazabilidad.

## 6. Tres modalidades de entrega

### A. Retiro por el comprador

- Seleccionar retiro en sucursal/depósito.
- Definir ventana o turno, persona autorizada y documentación.
- Preparar y marcar listo para retirar.
- Registrar entrega con código/PIN, firma, nombre/identidad del receptor y fecha.
- Cerrar el fulfillment y liberar el pedido pendiente.

### B. Reparto local propio

- Seleccionar zona, ruta, fecha y ventana.
- Asignar vehículo, chofer y ayudante si corresponde.
- Generar paradas y secuencia; consolidar pedidos compatibles.
- Registrar salida, intentos, entrega, evidencia y firma.
- Capturar combustible, peajes, horas, kilometraje y costo de reparto.
- Gestionar entrega parcial, dirección incorrecta, rechazo o reprogramación.

### C. Despacho a una logística para otra provincia

- Registrar el transportista, sucursal/agencia de destino y servicio elegido.
- Crear el despacho cuando se prepara la mercadería.
- Entregar al operador y registrar quién recibe, fecha, bultos, peso/volumen y documentación de handoff.
- Cargar después la guía, número de seguimiento o ID que el transportista emite.
- Consultar o recibir eventos de tracking; si no hay integración, permitir carga manual auditada.
- Registrar flete, seguro, adicionales, cobro al remitente/destinatario y comprobantes.
- Asociar incidencias, daños, extravíos, entregas fallidas y reclamos.

El dato de tracking debe ser opcional en el pedido/venta y obligatorio solo para los estados del despacho que realmente lo requieren. Se conserva la fecha de asignación para medir cuánto tardó el operador en emitirlo.

## 7. Modelo de estados del despacho

Estados de referencia:
- pending_fulfillment;
- picking;
- packed;
- ready_for_pickup / ready_for_carrier;
- awaiting_carrier_reference;
- carrier_booked;
- handed_over;
- in_transit;
- out_for_delivery;
- delivered;
- delivery_exception;
- returned_to_origin;
- cancelled.

No todos los transportistas ni las modalidades usan todos los estados. El adaptador normaliza los eventos externos sin inventar un avance. El historial es append-only para auditoría; el estado actual es una proyección del historial y las correcciones se agregan como nuevos eventos.

## 8. Costos de distribución y rentabilidad

Por pedido/envío se deben separar:
- costo de mercadería;
- preparación/picking/packing;
- embalaje;
- flete del tercero;
- reparto propio (horas, combustible, peajes, vehículo);
- seguro y adicionales;
- comisión del vendedor;
- comisión de cobro;
- devoluciones, reintentos y daños.

El costo de transporte se puede distribuir a las líneas por peso, volumen, cantidad, valor o regla contractual. Se registra el método y la base usada. No se reparte arbitrariamente ni se pierde el costo en una cuenta general.

## 9. Aceptación mayorista

- Cliente empresa con varios contactos y direcciones.
- Lista específica por cliente y vigencia.
- Mínimo por SKU, empaque, familia y pedido.
- Escalas por cantidad, cesta y período acumulado.
- Conflicto de reglas/stacking y excepción autorizada.
- Pedido a crédito y validación de límite.
- Confirmar venta antes de conocer el tracking.
- Registrar retiro por comprador, reparto propio y carrier interprovincial.
- Crear dos despachos parciales desde un pedido.
- Asociar guía externa después de la venta y reconstruir su historial.
- Conciliar cantidades, stock, facturas, cobros, flete y costo de servir el pedido.

## Referencias técnicas investigadas

ERPNext documenta listas de precio, precios por UOM, mínimos, múltiplos de empaque y precios por cliente; también reglas por cantidad/importe y promociones con slabs. Sus Sales Orders admiten entregas y facturas parciales mediante documentos posteriores. Ver:
- https://docs.frappe.io/erpnext/item-price
- https://docs.frappe.io/erpnext/price-lists
- https://docs.frappe.io/erpnext/pricing-rule
- https://docs.frappe.io/erpnext/promotional-scheme
- https://docs.frappe.io/erpnext/sales-order
- https://docs.frappe.io/erpnext/delivery-note

Dolibarr permite crear envíos desde pedidos, mantener cantidades pendientes, packing slips y pruebas de entrega:
- https://wiki.dolibarr.org/index.php/Module_Shipments

Open TMS contiene patrones de conversión de órdenes a uno o varios envíos, consolidación, eventos de tracking y handoff a transportistas. Está en desarrollo activo y requiere revisión de licencia/estabilidad antes de reutilizarlo:
- https://github.com/DominicFinn/open_tms
