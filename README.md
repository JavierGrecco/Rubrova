# Rubrova

Plataforma comercial integral para operar, administrar y hacer crecer negocios de distintos sectores, con un punto de venta completo, gestión omnicanal, funcionamiento resiliente sin conexión e inteligencia basada en los datos reales del negocio.

## Identidad y facilidad de renombrado

La denominación actual es provisoria y se mantiene únicamente en este README y en el nombre del repositorio. Los demás documentos, módulos, paquetes, servicios, tablas, eventos e identificadores internos utilizan nombres funcionales y neutrales. Si decidimos cambiar el nombre, el objetivo es modificar solamente el nombre del repositorio y este README.

La disponibilidad legal de la denominación y de los dominios todavía no está verificada. Antes de convertirla en marca pública habrá que consultar el buscador oficial del INPI, revisar variantes fonéticas y clases pertinentes, y comprobar los dominios.

## Qué estamos construyendo

Una plataforma que reúne en un solo lugar:

- **Punto de venta y checkout:** escaneo rápido, edición del carrito antes de pagar, efectivo y vuelto exacto, pagos mixtos, integración con terminales, devoluciones y cierres.
- **ERP y gestión comercial:** catálogo, precios, inventario/WMS, compras, proveedores, producción, CRM, clientes, cuentas corrientes y sucursales.
- **Múltiples áreas de negocio:** minorista, online, mayorista/distribución y servicios B2B, con reglas, recursos y rentabilidad propios sobre datos compartidos.
- **Canales de venta:** local físico, tienda online, WhatsApp, marketplaces, pedidos telefónicos y delivery, con análisis por canal y consolidado.
- **Operación sectorial:** supermercados y autoservicios, kioscos y almacenes, panaderías, rotiserías y gastronomía; perfiles configurables sobre un núcleo común.
- **Mayorista y servicios empresariales:** mínimos y escalas por volumen, crédito, contratos de suministro, SLA, agendas, órdenes de trabajo, logística y seguimiento.
- **Administración y control:** usuarios, permisos, turnos, cajas, arqueos, autorizaciones, auditoría y movimientos internos.
- **Inteligencia y automatización:** rentabilidad, demanda, estacionalidad, precios, marcas, categorías, promociones, abastecimiento, pronósticos, escenarios, workflows y alertas.
- **Integraciones:** ARCA, Mercado Pago, marketplaces, mensajería y hardware comercial.
- **Continuidad operativa:** registro local, sincronización confiable, recuperación y trazabilidad ante cortes de conexión.

## Principios que no vamos a negociar

1. La caja debe ser rápida, clara y confiable. La complejidad se resuelve dentro de módulos bien delimitados, no se traslada al comerciante.
2. Cada operación confirmada debe conservar su historia. Las correcciones se registran mediante anulaciones o movimientos compensatorios, nunca mediante borrado silencioso.
3. Ventas, pagos, inventario y comprobantes fiscales son conceptos relacionados, pero tienen estados y ciclos de vida diferentes.
4. Una venta se registra una sola vez y se factura una sola vez por la obligación fiscal correspondiente, aunque intervengan varios sistemas.
5. Los descuentos, promociones, devoluciones, gastos y salidas internas se registran explícitamente y pueden auditarse.
6. La inteligencia explica sus cálculos, fuentes, supuestos y nivel de confianza. No inventa datos ni presenta estimaciones como hechos.
7. Los reportes globales y por canal comparten definiciones consistentes y permiten llegar desde el indicador hasta la operación que lo originó.
8. La seguridad, la privacidad, la accesibilidad y la calidad se diseñan desde el inicio.
9. La documentación usa lenguaje simple, directo y humano. Cada módulo debe explicar qué hace, qué no hace y cómo se prueba.
10. El repositorio mantiene una sola rama viva: `main`. No se crean ramas de trabajo paralelas.

## Cómo leer la documentación

| Documento | Qué explica |
|---|---|
| [Visión y objetivos](docs/PRODUCT_VISION.md) | Problema, usuarios, propuesta de valor y principios |
| [Alcance funcional](docs/FUNCTIONAL_SCOPE.md) | Capacidades del producto y límites del alcance |
| [Requisitos del POS](docs/POS_REQUIREMENTS.md) | Venta, caja, descuentos, pagos, hardware y operación diaria |
| [Arquitectura](docs/ARCHITECTURE.md) | Estructura técnica, módulos, datos y decisiones de plataforma |
| [Arquitectura modular distribuida](docs/DISTRIBUTED_MODULAR_ARCHITECTURE.md) | Servicios independientes, APIs/eventos, idempotencia, CAS y operación local |
| [Modelo de dominio](docs/DOMAIN_MODEL.md) | Entidades, movimientos, estados y relaciones |
| [Inteligencia del negocio](docs/BUSINESS_INTELLIGENCE.md) | Métricas, rentabilidad, estacionalidad, tendencias y pronósticos |
| [Implementación de demanda, rentabilidad y marcas](docs/DEMAND_AND_MARGIN_INTELLIGENCE.md) | Datos fuente, herramientas reutilizables, costos, pronósticos, primeras/segundas marcas y pruebas de aceptación |
| [Canales e integraciones](docs/CHANNELS_AND_INTEGRATIONS.md) | Omnicanalidad, ARCA, Mercado Libre y pagos |
| [Seguridad y auditoría](docs/SECURITY_AND_AUDIT.md) | Roles, permisos, turnos, autorizaciones y trazabilidad |
| [Perfiles sectoriales](docs/SECTOR_PROFILES.md) | Supermercados, panaderías, rotiserías y gastronomía |
| [Calidad y pruebas](docs/QUALITY_AND_TESTING.md) | Estrategia de pruebas, calidad y control de dependencias |
| [Continuidad y recuperación](docs/OPERATIONAL_RESILIENCE_AND_RECOVERY.md) | Fallos de proceso, idempotencia, CAS, backups, restore y pruebas P27–P44 |
| [Plan maestro de implementación](docs/MASTER_IMPLEMENTATION_PLAN.md) | Orden ejecutivo: POS, ERP, contabilidad, reportes, expansión y logística |
| [Conjunto Tryton 8.0 Argentina](docs/TRYTON_ARGENTINA_8_0_LOCK.md) | Ocho módulos locales fijados por commit, dependencias, licencias y plan de prueba |
| [Plan de trabajo](docs/ROADMAP.md) | Etapas, prioridades y definición de terminado |
| [Forma de trabajo](docs/WORKFLOW.md) | Regla de rama única, commits y documentación |
| [Estrategia reuse-first](docs/REUSE_FIRST_IMPLEMENTATION_STRATEGY.md) | Decisión vigente: reutilizar primero, selección de plataformas, puertas y plan de evaluación |
| [Shortlist de componentes reutilizables](docs/REUSE_COMPONENTS_SHORTLIST.md) | Bibliotecas, SDK y aplicaciones para datos, ARCA, hardware, documentos, logística y automatización |
| [Estrategia de reutilización de código abierto](docs/OPEN_SOURCE_STRATEGY.md) | Proyectos reutilizables, licencias, riesgos y prueba de compatibilidad |
| [Catálogo de código reutilizable](docs/CODE_REUSE_CATALOG.md) | Inventario de proyectos, módulos y componentes candidatos |
| [Logística argentina](docs/ARGENTINA_LOGISTICS_INTEGRATION.md) | Andreani, PAQ.AR, OCA, Vía Cargo, agregadores y tracking unificado |
| [Interoperabilidad contable](docs/ACCOUNTING_INTEROPERABILITY.md) | Tango, Catedral, Bejerman, Xubio, Colppy y reportes de gestión |
| [Necesidades PyME y backlog](docs/PYME_NEEDS_AND_PRODUCT_BACKLOG.md) | Evidencia de pymes argentinas y mejoras priorizadas para Rubrova |
| [Investigación de mercado y oportunidades](docs/MARKET_RESEARCH_AND_ADDITIONAL_OPPORTUNITIES.md) | Evidencia de adopción digital, problemas relatados y proyectos adicionales |
| [Mapa integral de capacidades](docs/PRODUCT_CAPABILITY_MAP.md) | Cobertura completa: ERP, POS, canales, WMS, producción, finanzas e inteligencia |
| [Áreas de negocio y dimensiones](docs/BUSINESS_LINES_AND_SEGMENTS.md) | Varias actividades, clientes y recursos compartidos con resultados separados |
| [Mayorista y distribución](docs/WHOLESALE_AND_DISTRIBUTION.md) | B2B, mínimos, escalas, crédito, retiros, reparto y envíos posteriores |
| [Servicios B2B y contratos](docs/B2B_SERVICES_AND_CONTRACTS.md) | Contratos, SLA, agendas, órdenes de trabajo y cumplimiento |
| [Rentabilidad por área](docs/BUSINESS_UNIT_PROFITABILITY.md) | Costos directos/compartidos y resultados por unidad y consolidados |
| [Checkout y terminales](docs/CHECKOUT_AND_PAYMENT_TERMINALS.md) | Carrito, vuelto, pagos integrados, terminales y comprobantes |
| [Composición de módulos](docs/MODULE_COMPOSITION.md) | Contratos, propiedad de datos, adaptadores y compatibilidad multiplataforma |
| [Investigación de módulos ampliados](docs/MODULAR_COMPONENT_RESEARCH.md) | WMS, ERP, conectores, promociones, BI y automatización |
| [Evaluación de plataformas](docs/PLATFORM_EVALUATION.md) | Prueba reproducible de las plataformas integrales con escenarios comunes |
| [Laboratorio de evaluación](docs/PLATFORM_LAB_SETUP.md) | Instalación aislada, versiones fijadas y registro de evidencias |
| [Referencias de investigación](docs/RESEARCH.md) | Proyectos estudiados, aprendizajes y fuentes |

## Etapa actual y próximos resultados

**Ahora — Fase 0: elegir el núcleo POS + ERP**

Rubrova debe comenzar por la operación del negocio. El seguimiento de envíos se mantiene en el diseño para no limitar futuras capacidades, pero sus integraciones se dejan para una etapa posterior.

- Evaluar el circuito completo POS + gestión: catálogo, carrito editable, ventas, pagos, vuelto, caja, stock, devoluciones, compras y reportes básicos.
- Probar ERPNext 16, MyCompany 6.2 y Tryton 8.0 con el conjunto argentino tryton-ar 8.0; filtrar Dolibarr 24.0.3 como alternativa de menor complejidad. Tryton 8.2 queda como actualización posterior.
- Mantener Posnic 1.9.2 como referencia POS secundaria, no como plataforma de gestión principal.
- Aplicar el mismo dataset sintético y las puertas de instalación, licencia, API, exportación, backup, restauración, arquitectura y localización argentina.
- Llevar como máximo dos finalistas a la prueba profunda. No elegir por cantidad de módulos ni por una demostración.
- Capturar desde el inicio unidad de negocio, sucursal, canal, centro de costo y depósito para que los reportes posteriores sean correctos.
- Mantener una autoridad única por dominio y construir/integrar servicios con APIs/eventos; no compartir tablas privadas entre aplicaciones.

El orden completo y los criterios de salida están en el [Plan maestro de implementación](docs/MASTER_IMPLEMENTATION_PLAN.md). La [Evaluación de plataformas](docs/PLATFORM_EVALUATION.md) contiene el protocolo comparativo.

**Siguiente — primera entrega funcional**

Un circuito de mostrador completo: producto → carrito → venta → pago y vuelto → caja → stock → ticket/documento separado → devolución → cierre y conciliación. Debe sobrevivir reintentos, desconexión y reinicio del proceso sin pérdidas ni duplicados.

Después se completa la gestión administrativa y contable, se construyen reportes de rentabilidad con costos validados, se amplían perfiles sectoriales y canales digitales, y por último se incorporan conectores avanzados de transportistas y tracking.

Todavía no se ha elegido una plataforma ni se ha incorporado código externo. No existe una aplicación funcional de Rubrova; el estado real y las pruebas pendientes se registran en el plan maestro y el roadmap.

## Forma de trabajo

- La única rama viva es `main`.
- No se crean ramas de funcionalidades, experimentos o releases.
- Los cambios se preparan y revisan en una copia de trabajo basada en `main`; se ejecutan las validaciones correspondientes y luego se integran mediante commits pequeños y comprensibles en `main`.
- No se deja trabajo pendiente en ramas alternativas ni se acumulan cambios sin integrar.
- Cada entrega actualiza el estado, las pruebas y la documentación afectada.
- No se declara una capacidad terminada sin evidencia verificable.

Ver [Forma de trabajo](docs/WORKFLOW.md).

## Criterio de calidad

El objetivo no es implementar muchas pantallas. Es entregar operaciones correctas, rápidas, comprensibles y recuperables. Para cada capacidad importante deben existir reglas explícitas, pruebas de éxito y error, permisos, trazabilidad, impacto en inventario y dinero, y tratamiento ante falta de conexión.

## Referencias y cumplimiento

Las integraciones fiscales y de pago se implementarán contra documentación oficial vigente y se probarán en entornos de homologación antes de habilitarse en producción. Los requisitos de seguridad se tomarán como una base verificable, incluyendo OWASP ASVS. Las referencias estudiadas están reunidas en [Investigación](docs/RESEARCH.md).

---

**Estado del producto:** definición y arquitectura en preparación.  
**Estado del software:** sin implementación funcional ni código externo incorporado.
