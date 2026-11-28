# Perfiles sectoriales

## Principio

Un solo núcleo comercial, capacidades configurables y flujos especializados. Los perfiles no duplican ventas, pagos, inventario, clientes ni auditoría.

Un negocio puede combinar perfiles: supermercado con rotisería, panadería con cafetería o almacén con delivery.

## Kioscos y almacenes

Caja rápida, lector y productos frecuentes; catálogo precargado y alta rápida; fiados; precios y costos; promociones; stock y vencimientos; proveedores; pedidos por WhatsApp; operación local con conexión interrumpida.

## Supermercados y autoservicios

- Varias cajas y turnos.
- Códigos de barras y PLU.
- Productos pesables y etiquetas de balanza.
- Unidades, cajas, packs y fraccionamiento.
- Stock por sucursal, depósito y sector.
- Lotes, vencimientos y FEFO.
- Precios masivos y listas por canal.
- Inventarios y conteos cíclicos.
- Compras y recepción por proveedor.
- Reportes por rubro, marca, góndola, sucursal y caja.
- Permisos y auditoría reforzados.

## Panaderías y pastelerías

- Materias primas y unidades de medida.
- Recetas versionadas.
- Producción por tanda.
- Rendimiento teórico y real.
- Consumo de ingredientes.
- Merma de preparación y cocción.
- Costos por receta, producto y presentación.
- Planificación por día y franja horaria.
- Productos perecederos, lotes y vencimientos.
- Pedidos anticipados y encargos especiales.
- Ventas por peso y unidad.
- Promociones para productos cercanos al final de su vida comercial.

## Rotiserías y comidas preparadas

- Recetas, porciones, ingredientes y adicionales.
- Producción planificada por tanda y horario.
- Preparación y stock de comidas listas.
- Merma, vencimiento y sobrantes.
- Pedidos de mostrador, web, WhatsApp y delivery.
- Comandas y pantalla de cocina.
- Estados de preparación y entrega.
- Tiempos estimados y capacidad de producción.
- Pronóstico de cantidades por día y franja horaria.
- Rentabilidad por plato, porción y combinación.

Diseño funcional detallado: [Elaboración de alimentos, rotisería y trazabilidad](FOOD_PRODUCTION_AND_TRACEABILITY.md). El flujo debe compartir recetas, inventario, lotes, caja y ventas con el comercio minorista; no se implementará como una aplicación paralela.

## Gastronomía, cafeterías y restaurantes

Capacidades opcionales: mesas y sectores, comandas, división de cuenta, mozos, monitor de cocina y barra, reservas, pedidos anticipados, propinas, recetas, ingredientes, stock, delivery y menú QR.

## Reglas compartidas

Todos los perfiles usan catálogo, unidades, precios, descuentos, promociones, inventario, compras, proveedores, caja, pagos, comprobantes, permisos, auditoría, canales y métricas comunes.

## Activación de perfiles

El asistente inicial pregunta por actividades, cajas, sucursales, productos pesables, producción, cocina, canales y hardware. Recomienda una configuración mínima. Las capacidades se pueden habilitar después sin migraciones destructivas.

No ocultar funciones de datos o cumplimiento porque un perfil no las use en su interfaz.
