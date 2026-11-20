# Requisitos del punto de venta

**Estado:** requisitos de producto para la evaluación y primera entrega; no implica que exista un POS implementado.

## 1. Objetivo

El POS debe ser la puerta más rápida y confiable hacia la operación comercial. No puede depender de que el cajero conozca el ERP ni mostrarle reglas administrativas que no necesita. Al mismo tiempo, cada venta debe quedar correctamente vinculada con catálogo, precios, cliente cuando corresponda, inventario, pagos, caja, auditoría y estado fiscal.

No es una caja aislada que mantenga productos o stock propios: utiliza los servicios maestros del sistema y no inventa una segunda autoridad de inventario o contabilidad.

## 2. Inicio de turno y contexto de la caja

- Identificar operador, dispositivo, sucursal, caja, depósito y unidad de negocio.
- Abrir turno con fondo inicial por medio de pago.
- Mostrar estado de conexión local, disponibilidad de servicios críticos y pendientes de sincronización.
- Recuperar de forma segura una sesión interrumpida sin volver a crear ventas o cobros.
- Restringir operaciones de acuerdo con rol, sucursal, caja, horario y límites de autorización.

## 3. Selección de artículos y carrito

- Buscar por código de barras, SKU, PLU, código alternativo, nombre, marca o descripción.
- Agregar artículos mediante lector, teclado o selección táctil.
- Soportar variantes, presentaciones, packs, cajas, combos y servicios.
- Soportar productos por unidad, peso y otras unidades configuradas; conservar cantidad y precisión.
- Mostrar precio vigente, unidad, disponibilidad y avisos relevantes.
- Permitir cliente opcional en ventas de mostrador y selección de cliente empresarial/cuenta corriente cuando corresponda.
- Mantener el carrito como operación editable: antes de iniciar el cobro se pueden quitar líneas, reducir cantidades o cambiar artículos.
- Recalcular descuentos, promociones, impuestos y total al editar; liberar reservas temporales de líneas retiradas.
- No crear venta confirmada, salida de stock, pago ni documento fiscal por artículos retirados del carrito.

## 4. Precios, descuentos y promociones

- Aplicar listas, escalas, acuerdos, promociones y precios por cliente/canal/sucursal con fecha de vigencia.
- Registrar precio base, precio aplicado, descuento, regla y motivo.
- Permitir descuentos manuales sólo según permisos y límites.
- Separar descuento de línea, carrito, cupón, combo y promoción automática.
- Definir si las reglas se acumulan o excluyen entre sí.
- Congelar una fotografía de precio, impuestos, descuentos y condiciones al confirmar la venta.
- No permitir que un cambio posterior de precio altere una operación histórica.
- Una excepción superior al límite requiere autorización identificable.

## 5. Totales, moneda e impuestos

- Calcular importes con unidades menores enteras y reglas explícitas de redondeo; evitar coma flotante en dinero.
- Desglosar subtotal, descuentos, impuestos, recargos, costo financiero cuando aplique y total.
- Mostrar la moneda y la cotización usada si hay multimoneda.
- No confundir ticket comercial con comprobante fiscal.
- La venta comercial puede quedar registrada mientras la emisión fiscal mantiene su estado separado y visible.
- Un resultado incierto de ARCA se consulta y concilia antes de reintentar; nunca se emite una segunda factura a ciegas.

## 6. Cobro y pagos

- Efectivo exacto, exceso y faltante: calcular vuelto exacto y mostrar cuánto falta.
- Tarjetas, transferencias, QR, billeteras y medios que el proveedor realmente habilite.
- Pagos mixtos y parciales: las asignaciones deben sumar el total y conservar importe, moneda, proveedor y estado de cada componente.
- Diferenciar solicitado, en proceso, aprobado, rechazado, cancelado, pendiente/indeterminado y reembolsado.
- No marcar una venta como pagada por una captura del cliente ni por una pantalla sin confirmación del proveedor.
- Un timeout después de que el cliente pudo haber pagado exige consultar y conciliar antes de otro intento.
- Una devolución o reembolso referencia la venta y el pago originales.
- No guardar PAN completo, CVV ni credenciales de terminal.

### Efectivo y vuelto

La pantalla solicita el importe recibido del cliente, calcula el vuelto exacto y muestra el faltante cuando el efectivo no alcanza. En un pago mixto, el efectivo que ingresa a caja es el efectivo recibido menos el vuelto; no se registra como efectivo todo el total cobrado por varios medios.

### Terminal bancaria integrada

Cada adquirente y modelo de terminal se conecta mediante un adaptador. El adaptador sólo publica capacidades que se hayan probado: iniciar pago, consultar, cancelar, reembolsar, recibir notificaciones, cerrar lote o imprimir voucher. No se presume que todos los modelos soporten todas las operaciones.

Una vez enviada una orden a la terminal, el importe y carrito quedan congelados mientras procesa. Para modificar la venta se cancela primero la orden pendiente y se espera confirmación. Si el pago ya fue aprobado, el cambio se resuelve mediante devolución/reembolso o una nueva operación vinculada, nunca con edición silenciosa.

## 7. Caja, turnos y movimientos

- Apertura y cierre por operador, dispositivo y caja.
- Fondo inicial por medio de pago.
- Ingresos, retiros, gastos, depósitos y transferencias con concepto, usuario y autorización.
- Arqueo ciego y conteo real por medio de pago.
- Efectivo esperado = fondo inicial + cobros en efectivo − vuelto − retiros/gastos + ingresos autorizados.
- Mostrar diferencia por medio de pago; no compensar diferencias entre efectivo y tarjeta.
- Cierre de turno, cierre de lote externo y liquidación bancaria son hechos distintos.
- Permitir supervisión y re-apertura controlada con auditoría cuando la política lo habilite.

## 8. Confirmación de venta e inventario

- Antes de confirmar, consultar disponibilidad y crear una reserva con idempotencia.
- Inventario conserva el ledger de movimientos y es la autoridad de las cantidades.
- La venta confirmada emite un comando al inventario para convertir la reserva en salida o consumo; el resultado se conserva con su correlación.
- Idempotencia evita repetir la misma venta; CAS/reserva evita que dos ventas distintas consuman la última unidad.
- En sucursal, varias cajas conectadas utilizan el servicio local como autoridad de reservas.
- Si el POS pierde conexión con el coordinador, aplica cuotas exclusivas previamente asignadas o registra la venta como pendiente de conciliación de stock según política; no afirma disponibilidad garantizada.
- Una venta, pago y salida de stock deben conciliarse y poder rastrearse entre servicios.

## 9. Ticket, voucher y comprobante fiscal

Son documentos diferentes:

- **Ticket de venta:** detalle comercial de Rubrova y referencia de la operación.
- **Voucher de terminal:** comprobante del proveedor de pago, si corresponde.
- **Documento fiscal:** factura/ticket fiscal o nota autorizada por ARCA.

Pueden imprimirse en dispositivos distintos. La impresión desde una terminal sólo se habilita para modelos y firmware cuya documentación la soporte. Cada documento conserva su identificador y relación con la venta.

### Política de impresión por medio de pago

- **Efectivo:** ticket comercial en impresora térmica conectada a la caja.
- **Transferencia bancaria:** ticket comercial en impresora de caja cuando el ingreso esté verificado; si queda pendiente, mostrar claramente ese estado.
- **QR y tarjeta:** preferimos que la terminal inteligente vinculada a Rubrova imprima el ticket comercial completo generado por el sistema y el voucher que corresponda. Exige soporte documentado y probado del modelo/firmware. Si solo imprime el voucher bancario, la impresora de caja imprime el ticket detallado.
- La impresora de caja es el mecanismo universal y respaldo para QR/tarjeta.
- Evitar duplicar el ticket comercial cuando se imprime desde la terminal; permitir reimpresión auditada sin duplicar operaciones.
- Factura/comprobante fiscal conserva su propio flujo y no se reemplaza por ticket ni voucher.

## 10. Devoluciones, anulaciones y cambios

- Devolución total o parcial con referencia a venta y líneas originales.
- Motivo, operador, autorización, cantidades, estado del producto y destino físico.
- Distinguir devolución comercial, reintegro de dinero, reposición de stock y nota de crédito fiscal.
- No borrar ventas ni pagos confirmados: registrar movimientos compensatorios.
- Permitir cambio por otro artículo como operación vinculada y auditable.
- Una devolución de un producto usado, dañado o vencido no regresa automáticamente a stock disponible.

## 11. Offline y recuperación

- El funcionamiento local no depende de Internet para operaciones que puedan resolverse con datos y autoridades locales.
- Los servicios externos (terminal, ARCA, ecommerce) informan su estado y dejan los procesos pendientes cuando no se puede confirmar.
- Cada comando posee una clave idempotente estable; el mismo comando repetido devuelve el resultado anterior.
- Los eventos externos se deduplican por identidad del proveedor, cuenta y evento.
- La interfaz diferencia guardado local, venta confirmada, stock pendiente, pago pendiente y comprobante fiscal pendiente.
- Reiniciar o cerrar abruptamente el proceso POS no pierde ni duplica operaciones confirmadas.
- La sincronización reenvía sólo lo que falta; los conflictos quedan visibles y conciliables.

## 12. Informes disponibles para el operador y supervisor

Desde la primera entrega deben existir informes operativos simples:

- Ventas por turno, caja, operador y período.
- Total neto, descuentos, devoluciones, tickets y ticket promedio.
- Cobros por medio de pago y efectivo esperado.
- Diferencia de caja y movimientos manuales.
- Artículos/cantidades vendidos y consulta de stock.
- Ventas pendientes de pago, de conciliación fiscal o de conciliación de stock.

Los análisis de margen, rentabilidad por área, rotación y pronósticos se amplían cuando compras, costos y contabilidad estén conciliados.

## 13. Experiencia, rendimiento y accesibilidad

- La tarea habitual de escanear, revisar y cobrar debe requerir pocos pasos.
- El foco vuelve al campo de escaneo después de agregar un artículo.
- Los controles principales son utilizables con teclado, lector y pantalla táctil.
- El carrito, el total y el estado de cobro permanecen claros y visibles.
- Mensajes concretos: qué ocurrió, qué quedó confirmado y qué acción puede tomar el operador.
- No mostrar al cajero menús administrativos, herramientas de integración ni complejidad de servicios.
- Medir tiempo de búsqueda, escaneo, recálculo, persistencia y confirmación en el equipo objetivo; establecer umbrales de aceptación con los resultados del laboratorio y no con estimaciones no probadas.
- Cumplir WCAG 2.2 AA en componentes web aplicables: contraste, foco, etiquetas, tamaño de objetivos y navegación por teclado.

## 14. Escenarios mínimos de aceptación

1. Venta en efectivo exacto y con vuelto.
2. Venta con dos medios de pago y vuelto correcto.
3. Retirar una línea del carrito antes del pago sin crear salida ni cobro.
4. Producto por peso, variante y pack con redondeo correcto.
5. Precio/promoción vigente y descuento manual con autorización.
6. Cliente de mostrador y cliente con cuenta corriente.
7. Apertura, arqueo ciego, diferencia y cierre de caja.
8. Pago en terminal aprobado, rechazado, cancelado y con respuesta incierta.
9. Webhook y comando de pago repetidos sin duplicar efectos.
10. Dos cajas intentando vender la última unidad: una reserva y la otra recibe conflicto/alternativa.
11. Desconexión, reinicio abrupto y reintento sin pérdida ni duplicado.
12. Devolución parcial, reintegro, stock en cuarentena y nota de crédito vinculada.
13. ARCA no disponible: estado fiscal pendiente y recuperación sin doble emisión.
14. Restaurar backup y repetir consulta de venta, pago, caja e inventario.
15. El cajero no puede ejecutar una operación administrativa no autorizada.

Ver [Checkout y terminales](CHECKOUT_AND_PAYMENT_TERMINALS.md), [Plan maestro de implementación](MASTER_IMPLEMENTATION_PLAN.md) y [Calidad y pruebas](QUALITY_AND_TESTING.md) para el flujo completo y las pruebas transversales.
