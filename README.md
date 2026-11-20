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
| [Captura de datos y base analítica](docs/DATA_CAPTURE_AND_ANALYTICAL_FOUNDATION.md) | Fechas históricas, áreas/canales, compras, stock, pagos, cajeros, reclamos, exportaciones e IA de lectura |
| [Inteligencia del negocio](docs/BUSINESS_INTELLIGENCE.md) | Métricas, rentabilidad, estacionalidad, tendencias y pronósticos |
| [Perfil 360 e inteligencia por cliente](docs/CUSTOMER_360_AND_INTELLIGENCE.md) | Preferencias, marcas, productos, RFM, retención, CLV y rentabilidad por cliente |
| [Identidad del pagador y conciliación](docs/PAYMENT_IDENTITY_AND_RECONCILIATION.md) | Datos de QR, tarjeta, transferencia y efectivo; integraciones de cobro, privacidad e identidad transversal |
| [Implementación de demanda, rentabilidad y marcas](docs/DEMAND_AND_MARGIN_INTELLIGENCE.md) | Datos fuente, herramientas reutilizables, costos, pronósticos, primeras/segundas marcas y pruebas de aceptación |
| [Benchmark de demanda](scripts/forecasting/benchmark.py) | Comparación reproducible de baselines y StatsForecast sobre datos mensuales sintéticos |
| [Canales e integraciones](docs/CHANNELS_AND_INTEGRATIONS.md) | Omnicanalidad, ARCA, Mercado Libre y pagos |
| [Seguridad y auditoría](docs/SECURITY_AND_AUDIT.md) | Roles, permisos, turnos, autorizaciones y trazabilidad |
| [Perfiles sectoriales](docs/SECTOR_PROFILES.md) | Supermercados, panaderías, rotiserías y gastronomía |
| [Calidad y pruebas](docs/QUALITY_AND_TESTING.md) | Estrategia de pruebas, calidad y control de dependencias |
| [Continuidad y recuperación](docs/OPERATIONAL_RESILIENCE_AND_RECOVERY.md) | Fallos de proceso, idempotencia, CAS, backups, restore y pruebas P27–P48 |
| [Copias de seguridad y recuperación](docs/BACKUP_AND_MIGRATION_STRATEGY.md) | Backup portable sin cifrado de aplicación, checksums, reinstalación de Windows y restauración guiada |
| [Plan maestro de implementación](docs/MASTER_IMPLEMENTATION_PLAN.md) | Orden ejecutivo: POS, ERP, contabilidad, reportes, expansión y logística |
| [Estado real del proyecto](docs/PROJECT_STATUS.md) | Qué funciona, qué está heredado de MyCompany, qué falta y el siguiente bloque de trabajo |
| [Inicio de implementación por bloques](docs/IMPLEMENTATION_START.md) | MyCompany 6.2 como primer piloto, módulos reutilizados, extensión propia y etapas POS + ERP |
| [Instalación del primer piloto](docs/MYCOMPANY_RUNTIME_INSTALL.md) | Preparación de artefactos, instalación aislada y despliegue de la extensión modular Rubrova |
| [Compatibilidad con macOS](docs/MACOS_SUPPORT.md) | Desarrollo desde MacBook, validación Apple Silicon y límites reales del runtime MyCompany |
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
| [Revisión competitiva](docs/COMPETITIVE_MARKET_REVIEW.md) | Comparación con POS/ERP/CRM disponibles en Argentina e internacionales |
| [Evaluación de S-Tech](docs/S_TECH_EVALUATION.md) | Terminales, kioscos, efectivo inteligente, CashFore, CashSchedule y posible integración |
| [Referencias de investigación](docs/RESEARCH.md) | Proyectos estudiados, aprendizajes y fuentes |

## Compatibilidad con macOS

Rubrova contempla macOS como entorno de desarrollo y como equipo cliente del POS web. La preparación de artefactos y el staging de la extensión se validan en CI sobre un runner Apple Silicon. Esto no equivale a certificar el servidor MyCompany en ARM: su imagen de lógica 6.2 está publicada para `linux/amd64`, por lo que el runtime local en Apple Silicon requiere emulación y una prueba real antes de aceptarse. La guía separa lo que ya se valida de lo que todavía falta comprobar: [Compatibilidad con macOS](docs/MACOS_SUPPORT.md).

## Etapa actual y próximos resultados

**Ahora — Fase 0: piloto integrado MyCompany 6.2**

MyCompany 6.2 es el primer piloto de integración, todavía no aprobado para el uso diario. Tryton 8.0 + tryton-ar 8.0 se mantiene como contraste fiscal argentino. ERPNext 16 queda en reserva y sólo se reabre si una brecha concreta justifica la comparación.

- Reutilizar los módulos de Retail POS, sesiones, pagos mixtos, devoluciones, inventario, costos, compras, ventas y facturación.
- Mantener las personalizaciones en un módulo Rubrova separado del código upstream.
- Preparar y validar los artefactos desde Windows, Linux y macOS; desplegar la extensión en Windows/Linux nativo o Docker. CI ya arranca MyCompany 6.2 en Linux x86_64 y ejecuta la extensión Rubrova.
- Verificar con Chromium el login, la navegación Comercio → Punto de venta, el selector de caja y la apertura de un turno sintético. Esta aceptación visual y de sesión ya pasó en CI; no equivale a una jornada de venta aceptada.
- Completar la localización española: los captions críticos del POS se ven en español, pero siguen apareciendo textos heredados en inglés en navegación, filtros y grillas.
- Completar catálogo → búsqueda → carrito → venta → pagos/vuelto → caja → stock → devolución → cierre y conciliación.
- Demostrar exportación, backup/restore, permisos, recuperación, hardware y adaptación fiscal argentina antes del uso real.

El detalle de módulos y bloques está en el [Inicio de implementación](docs/IMPLEMENTATION_START.md). La instalación paso a paso está en la [guía del primer piloto](docs/MYCOMPANY_RUNTIME_INSTALL.md). La [Evaluación de plataformas](docs/PLATFORM_EVALUATION.md) conserva las puertas de aceptación.

**Siguiente resultado:** una jornada de mostrador completa y repetible, conectada a los datos de gestión, con pagos y stock conciliados, devolución auditada, cierre de caja y recuperación probada.

MyCompany 6.2 ya se ejecuta en un entorno efímero de CI Linux x86_64: la extensión carga, Chromium inicia sesión, abre Comercio → Punto de venta, muestra una caja sintética y permite abrir un turno. Esto no es todavía una instalación en tu equipo ni un POS aprobado para uso diario: no se probó añadir un artículo, cobrar, conciliar stock, devolver ni cerrar caja. La localización sigue incompleta. MyCompany se consume como dependencia externa; su código fuente no está copiado al repositorio. El estado detallado, con límites y pruebas, está en [Estado real del proyecto](docs/PROJECT_STATUS.md).

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

**Estado del producto:** Fase 0 avanzada; primer runtime POS probado en CI, circuito comercial todavía incompleto.  
**Estado del software:** MyCompany 6.2 + extensión RubrovaCustom/RubrovaPOSLocalization; login, navegación POS y apertura de turno sintético verificados en CI Linux x86_64. Venta, pago, stock, devolución, cierre, localización completa e instalación local siguen pendientes.
