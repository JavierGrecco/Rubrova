# Requisitos del punto de venta

## Objetivo

La caja debe permitir atender con rapidez y registrar correctamente venta, descuentos, pagos, stock y responsabilidad del operador. El flujo frecuente debe funcionar con teclado, pantalla táctil y lector de códigos.

## Flujo de venta

1. El operador inicia sesión y abre o toma una caja/turno autorizado.
2. Escanea, busca o selecciona artículos.
3. El sistema valida estado, precio, unidad, disponibilidad y reglas vigentes.
4. El operador modifica cantidades, agrega cliente o aplica descuentos permitidos.
5. El sistema calcula subtotales, descuentos, impuestos y total.
6. El cliente elige uno o más medios de pago.
7. El sistema confirma el cobro o registra saldo pendiente según la modalidad.
8. Se confirma la venta y se generan movimientos relacionados.
9. Se emite o vincula el comprobante fiscal según la configuración del canal.
10. Se entrega o envía ticket y la operación queda disponible para consulta y auditoría.

Una venta no se considera cobrada porque el operador seleccionó un medio de pago. El estado debe reflejar la confirmación real del proveedor cuando aplique.

## Descuentos y promociones

### Tipos admitidos

- Porcentaje o importe fijo sobre una línea.
- Porcentaje o importe fijo sobre el carrito.
- Precio especial por cantidad.
- Segunda unidad o unidad adicional con descuento.
- Combos y paquetes.
- Precio por lista, grupo de cliente o volumen.
- Cupón o código promocional.
- Descuento por día, horario, sucursal o canal.
- Beneficio de fidelización.
- Descuento autorizado por supervisor.
- Liquidación por vencimiento o discontinuación, con motivo específico.

### Registro obligatorio

Cada descuento conserva:
- Precio base utilizado.
- Importe o porcentaje aplicado.
- Línea o conjunto de líneas afectadas.
- Regla, promoción o cupón que lo originó.
- Canal, sucursal y vigencia.
- Usuario que lo aplicó y quién lo autorizó, si corresponde.
- Motivo, si fue manual o excepcional.
- Importe final y asignación proporcional a las líneas.
- Impacto en margen y documentación fiscal.

El descuento no sobrescribe el precio de lista ni borra la condición original. La venta conserva una fotografía de precios y reglas vigentes al confirmarse.

### Reglas y controles

- Definir prioridad y compatibilidad entre promociones.
- Impedir acumulaciones no permitidas.
- Configurar límites por rol, importe y porcentaje.
- Permitir mínimo de margen configurable, con excepción explícita y auditada.
- Impedir totales negativos o descuentos superiores a la base elegible.
- Definir redondeos de manera consistente.
- Calcular impuestos sobre la base neta según normativa y comprobante.
- Permitir descuentos diferentes por canal sin alterar otros canales.
- Distribuir descuentos de carrito entre líneas para devoluciones y análisis.
- Revertir proporcionalmente descuentos y beneficios cuando se devuelven artículos.
- Identificar promociones financiadas por el comercio o por un proveedor.

### Reportes de descuentos

Importe y porcentaje descontado; descuentos por usuario, sucursal, caja y canal; descuentos por producto, marca y categoría; motivos y excepciones; uso de cupones; ganancia antes/después del descuento; impacto en margen y contribución; comparación de campañas.

## Carrito y atención

- Búsqueda instantánea y lectura de códigos.
- Modificación de cantidades y unidades.
- Suspender y recuperar ventas sin perder contenido.
- Agregar o cambiar cliente según permisos.
- Identificar productos sin precio o código.
- Mostrar stock disponible sin bloquear indebidamente la venta.
- Mostrar promociones aplicables y ahorro total.
- Venta rápida de artículos frecuentes.
- División de cuenta y cobro parcial cuando el perfil lo necesite.

## Pagos

- Efectivo, tarjetas, transferencia, QR, billeteras, cuenta corriente y medios configurables.
- Pagos mixtos, entrega de efectivo y vuelto.
- Pagos parciales, señas y saldos.
- Consulta de autorización y estado con proveedores.
- Reembolsos vinculados al pago original.
- Conciliación entre venta, operación de pago y acreditación.
- Nunca almacenar datos completos de tarjeta ni CVV; usar terminales, SDK o proveedores habilitados.

## Caja, turnos y cierres

Fondo inicial, operador, ingresos, retiros, gastos, devoluciones, arqueo ciego opcional, efectivo esperado/contado, totales por medio de pago, diferencia explicada, reapertura excepcional autorizada, varias cajas y turnos.

## Devoluciones, cambios y anulaciones

Buscar operación original; devolver todo o parte; registrar estado y destino de mercadería; reingresar stock solo si corresponde; reembolsar al medio original cuando la plataforma lo permita; registrar alternativa autorizada; emitir nota de crédito cuando aplique; conservar registros relacionados; prevenir reembolsos duplicados.

## Hardware

Definir matriz probada para PC, terminal táctil, tablet y teléfono; lectores USB/Bluetooth tipo teclado; impresoras térmicas y de etiquetas; cajones de dinero; balanzas y códigos de peso; terminales de pago; pantallas de cocina. La compatibilidad no se afirma sin probar modelo, sistema operativo, conexión, protocolo y versión.

## Rendimiento y experiencia

La pantalla de venta no espera informes pesados. Escanear es directo. La confirmación indica si quedó guardada. Los errores proponen el siguiente paso. Teclado, lector y pantalla táctil deben ser utilizables. Los perfiles no ven opciones administrativas innecesarias.

## Criterios de aceptación mínimos

- Venta en efectivo con vuelto correcto.
- Venta con medios mixtos.
- Descuento por línea y carrito.
- Descuentos incompatibles no se acumulan.
- Excepción solicita autorización y queda registrada.
- Devolución revierte correctamente stock, importe y descuento.
- Reintentar no duplica venta ni cobro.
- El cierre concilia movimientos del turno.
- Un corte no elimina una venta confirmada localmente.
- Informe de descuentos coincide con líneas de venta.
- Ticket y comprobante reflejan importes coherentes.
