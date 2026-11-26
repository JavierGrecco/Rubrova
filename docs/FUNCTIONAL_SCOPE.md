# Alcance funcional

**Estado:** definición funcional; no representa capacidades ya implementadas.

## Propósito

Rubrova es una plataforma integral para administrar, operar y analizar actividades comerciales y de servicios. El POS es una parte del núcleo operativo, no el producto completo.

## Núcleo transversal

- Organización, entidades legales, sucursales, cajas, depósitos, ubicaciones, usuarios, roles y permisos.
- Catálogo de productos y servicios, variantes, códigos, unidades, conversiones, precios, costos y proveedores.
- Clientes personas y empresas, contactos, sedes, domicilios, historial y condiciones comerciales.
- Pedidos, cotizaciones, venta, checkout, facturación, pagos, cuentas corrientes, devoluciones y caja.
- Inventario basado en movimientos, reservas, recepción, transferencias, picking, packing, despacho y devoluciones.
- Compras, abastecimiento, producción, recetas/BOM, mermas, costos y trazabilidad.
- Canales locales y digitales, marketplaces, mensajería, delivery, retiro y logística.
- Integraciones de transportistas y tracking unificado con alta de guía posterior a la venta.
- Exportación/importación contable y administrativa a Tango, Catedral, Bejerman, Xubio, Colppy y perfiles de archivos.
- Fiscalidad argentina, ARCA en homologación, conciliación y recuperación de estados inciertos.
- Auditoría, seguridad, continuidad local, sincronización, backup y restauración.

## Áreas de negocio

Una organización puede tener varias unidades: minorista, comercio electrónico, mayorista/distribución y servicios B2B. Cada una posee reglas y responsables propios y comparte, según configuración, clientes, catálogo, stock, compras, infraestructura y administración.

La asignación económica se realiza por unidad de negocio en la operación y, cuando haga falta, por línea. Canal, sucursal, centro de costo, territorio y proyecto son dimensiones distintas.

## Mayorista y distribución

- Cuentas empresariales, sedes, compradores, condiciones y límites de crédito.
- Mínimos por línea, familia, cantidad, múltiplo de empaque y total de pedido.
- Precios por cliente/segmento/territorio, escalas por volumen, promociones, rebates y vigencias.
- Cotización, pedido confirmado, reserva, entrega parcial, factura y cobro como hechos distintos.
- Retiro por cliente, reparto con flota propia y despacho por transportista.
- Creación de envíos después de la venta; guía y tracking opcionales hasta que el transportista los emita.
- Costos logísticos asociados a pedido, envío y unidad de negocio.

## Servicios B2B

- Catálogo y cotización de servicios, acuerdos y contratos versionados.
- Agenda, calendarios, recurrencia, órdenes de trabajo, técnicos y recursos.
- SLA, fechas comprometidas, alertas, evidencia, aceptación y seguimiento.
- Horas, materiales, viáticos, subcontratos, consumo de bolsa de horas y facturación.
- Rentabilidad por contrato, servicio, cliente y unidad de negocio.

## Áreas de expansión

CRM/fidelización, WMS avanzado, logística/TMS, recursos humanos, proyectos, finanzas y contabilidad avanzada, automatización, dashboards, pronósticos y análisis de contexto externo.

## Perfiles sectoriales

Kioscos y almacenes; supermercados y autoservicios; panaderías y pastelerías; rotiserías y comidas preparadas; restaurantes/cafeterías; comercios especializados; venta mayorista; distribuidoras; y empresas de servicios.

Los perfiles agregan flujos, campos y pantallas sobre el mismo núcleo; no duplican clientes, ventas, pagos, inventario o auditoría.

## Documentos de alcance detallado

- [Mapa integral de capacidades](PRODUCT_CAPABILITY_MAP.md)
- [Áreas de negocio y dimensiones](BUSINESS_LINES_AND_SEGMENTS.md)
- [Mayorista y distribución](WHOLESALE_AND_DISTRIBUTION.md)
- [Servicios B2B y contratos](B2B_SERVICES_AND_CONTRACTS.md)
- [Rentabilidad por área](BUSINESS_UNIT_PROFITABILITY.md)
- [Logística argentina](ARGENTINA_LOGISTICS_INTEGRATION.md)
- [Interoperabilidad contable](ACCOUNTING_INTEROPERABILITY.md)
- [Investigación de necesidades PyME](PYME_NEEDS_AND_PRODUCT_BACKLOG.md)
- [Arquitectura](ARCHITECTURE.md)
- [Roadmap técnico único](ENGINEERING_MASTER.md#roadmap-técnico-único-y-definición-de-terminado)
