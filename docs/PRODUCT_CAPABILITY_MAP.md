# Mapa integral de capacidades del producto

**Revisión:** 19 de noviembre de 2026  
**Estado:** alcance funcional consolidado; no implica que las capacidades estén implementadas.

## Qué estamos construyendo

Rubrova es una **plataforma integral de operación, gestión y conocimiento del negocio**. El punto de venta es una puerta de entrada operativa, no la definición ni el límite del producto.

El sistema acompaña el ciclo completo: captar demanda, vender por varios canales, cobrar, preparar y entregar, controlar inventario, comprar, producir, administrar recursos, cumplir obligaciones fiscales y convertir datos confiables en mejores decisiones. Debe servir desde un comercio pequeño con una caja hasta una operación con varios locales, depósitos, equipos, canales y procesos sectoriales.

No queremos una colección de aplicaciones inconexas ni un ERP rígido que obligue a todos a trabajar igual. Queremos un núcleo coherente, módulos especializados y una experiencia sencilla según el rol.

## Mapa de capacidades

| Dominio | Capacidades que deben conservarse |
|---|---|
| Dirección y organización | Negocios, sucursales, cajas, depósitos, ubicaciones, dispositivos, equipos, roles, permisos y configuración por actividad |
| Catálogo y datos maestros | Productos, variantes, marcas, categorías, fabricantes, proveedores, SKU, códigos de barras, PLU, códigos alternativos, atributos, presentaciones, kits, combos, importación y normalización |
| Unidades y precios | Unidad, kg, g, litro, ml, volumen, longitud, fracción, conversiones pack/caja/bulto, listas por canal/sucursal/cliente, vigencia, costo histórico y costo de reposición |
| Venta y atención | POS rápido, scanner, búsqueda, carrito editable, artículos removibles antes del pago, ventas suspendidas/recuperables, clientes, fiado y cuenta corriente |
| Promociones y fidelización | Descuentos por línea/carrito, combos, cupones, precios por cantidad, campañas, tarjetas, puntos, niveles, gift cards, referidos y medición incremental |
| Pagos y tesorería | Efectivo, vuelto, tarjetas, transferencias, QR, billeteras, pagos mixtos/parciales, señas, cuentas, terminal integrada, reembolsos, liquidaciones y conciliación |
| Caja y turnos | Apertura/cierre, fondo inicial, ingresos, retiros, gastos, arqueo ciego, diferencias, autorizaciones, múltiples cajas, operadores y trazabilidad por turno |
| Documentación fiscal | ARCA, facturas, tickets fiscales, notas de crédito/débito, CAE/CAEA, puntos de venta, estados inciertos, conciliación y documentos de marketplaces |
| Pedidos y omnicanalidad | Local, tienda online, WhatsApp, teléfono, Mercado Libre, marketplaces, delivery, reservas, retiro, despacho, entrega, cancelaciones y atribución de canal |
| Inventario y WMS | Multi-sucursal, multi-depósito, ubicaciones, lotes, series, vencimientos/FEFO, reservas, conteos, transferencias, recepción, picking, packing, despacho, devoluciones, pallets y contenedores |
| Compras y abastecimiento | Proveedores, cotizaciones, órdenes, recepción parcial/total, remitos, facturas, costo puesto, plazos, sugerencias, mínimos, stock de seguridad y reposición |
| Producción y manufactura | Recetas/BOM versionadas, rutas, centros de trabajo, órdenes, tandas, consumos, rendimiento, mermas, subproductos, costos y trazabilidad por lote |
| Gastronomía y servicio | Mesas, comandas, cocina/barra, modificadores, adicionales, reservas, división de cuenta, propinas, tiempos de preparación y delivery |
| CRM y clientes | Identidad, historial, saldos, beneficios, segmentos, campañas, referidos, preferencias, consentimiento y reclamos |
| Administración y finanzas | Gastos, cuentas a cobrar/pagar, flujo de fondos, conciliación de liquidaciones y activos; contabilidad general profesional/liquidación impositiva como módulos posteriores |
| Personal y operaciones | Empleados, asistencia, horarios, tareas, responsables, centros de trabajo, proyectos y tiempos |
| Logística y flota | Transportistas, expediciones, rutas/vehículos, seguimiento, entregas fallidas, devoluciones al depósito, comprobantes y costos logísticos |
| Inteligencia del negocio | Ventas netas, margen, contribución, GMROI, ABC/XYZ, rotación, cobertura, demanda, faltantes, compras, precios, elasticidad, estacionalidad, pronósticos, promociones y escenarios |
| Automatización e integración | APIs, webhooks, eventos, conectores, reglas, workflows, tareas programadas, notificaciones, import/export y aprobaciones |
| Plataforma y continuidad | Uso local, sincronización, recuperación, backups/restauración, observabilidad, privacidad, dispositivos y adaptadores por sistema operativo |

## Perfiles sectoriales

Kioscos y almacenes; supermercados y autoservicios; panaderías y pastelerías; rotiserías y comidas preparadas; restaurantes, cafeterías y gastronomía; comercios especializados y venta mayorista.

Un negocio puede combinar perfiles. Los perfiles agregan flujos, campos y pantallas; no duplican catálogo, ventas, pagos, caja, stock ni auditoría.

## Capas de alcance

**Núcleo transversal:** organización, identidad, catálogo, unidades, precios, checkout/venta, pagos, caja, inventario, auditoría, fiscalidad e integración.

**Módulos de expansión:** CRM/fidelización, compras avanzadas, WMS, producción, logística, personal, contabilidad, automatización y analítica avanzada.

**Servicios externos:** ARCA, adquirentes/terminales, Mercado Pago, Mercado Libre, mensajería, transportistas y fuentes económicas/climáticas.

Que algo sea posterior en el roadmap no significa que se haya perdido del diseño. La implementación se secuencia para conservar integridad y evitar construir todas las áreas a la vez.

## Criterios de coherencia

- Una venta, un cobro, una reserva de stock y un comprobante fiscal son hechos relacionados, pero distintos.
- Cada área tiene un módulo responsable de sus datos y reglas.
- Los módulos se conectan por contratos explícitos, no por tablas compartidas.
- Los canales convergen en el mismo modelo de pedidos y ventas, sin doble conteo.
- No se finge que ARCA o un adquirente aprobaron algo sin confirmación.
- Los indicadores muestran fuentes y distinguen observación de estimación.
- El dueño ve la visión global; el cajero ve una interfaz mínima y rápida.
- Los módulos externos se pueden adoptar o sustituir sin cederles la definición del negocio.

## Documentos fuente

[Visión](PRODUCT_VISION.md) · [Alcance funcional](FUNCTIONAL_SCOPE.md) · [Modelo de dominio](DOMAIN_MODEL.md) · [POS](POS_REQUIREMENTS.md) · [Perfiles](SECTOR_PROFILES.md) · [Canales](CHANNELS_AND_INTEGRATIONS.md) · [Inteligencia](BUSINESS_INTELLIGENCE.md) · [Seguridad](SECURITY_AND_AUDIT.md) · [Arquitectura](ARCHITECTURE.md) · [Roadmap](ROADMAP.md).

Este mapa es la referencia de cobertura: una investigación o comparación de POS no debe reducir el proyecto a una caja registradora.


## Unidades de negocio y operaciones empresariales

El alcance incluye la gestión de varias áreas dentro de una organización: venta minorista, venta online, mayorista/distribución y servicios B2B. Cada área puede tener su catálogo habilitado, listas, reglas, responsables, contratos, presupuestos y estado de resultados, sin duplicar los maestros compartidos.

Las dimensiones deben distinguir entidad legal, unidad de negocio/centro de beneficio, centro de costo, canal, sucursal, depósito, territorio, cliente, proyecto y contrato. Un canal no define el área: una venta mayorista por WhatsApp sigue perteneciendo a la unidad mayorista.

La venta mayorista contempla clientes empresa, mínimos y múltiplos de empaque, precios escalonados, acuerdos, crédito, pedidos parciales, retiro, reparto propio y transporte externo con guía incorporada después de la venta.

Los servicios empresariales contemplan contratos versionados, SLA, calendarios, recurrencias, órdenes de trabajo, técnicos/recursos, evidencia, aceptación, consumo y facturación.

La rentabilidad debe poder consultarse por área y de forma consolidada, con ingresos netos, costo de mercadería/prestación, costos variables de servir, gastos directos y costos compartidos asignados por reglas explícitas. Las áreas no se fuerzan a ser sistemas separados.

Documentos de detalle:
- [Áreas de negocio y dimensiones](BUSINESS_LINES_AND_SEGMENTS.md)
- [Mayorista y distribución](WHOLESALE_AND_DISTRIBUTION.md)
- [Servicios B2B y contratos](B2B_SERVICES_AND_CONTRACTS.md)
- [Rentabilidad por área](BUSINESS_UNIT_PROFITABILITY.md)
