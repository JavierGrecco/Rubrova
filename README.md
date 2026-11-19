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
| [Modelo de dominio](docs/DOMAIN_MODEL.md) | Entidades, movimientos, estados y relaciones |
| [Inteligencia del negocio](docs/BUSINESS_INTELLIGENCE.md) | Métricas, rentabilidad, estacionalidad, tendencias y pronósticos |
| [Canales e integraciones](docs/CHANNELS_AND_INTEGRATIONS.md) | Omnicanalidad, ARCA, Mercado Libre y pagos |
| [Seguridad y auditoría](docs/SECURITY_AND_AUDIT.md) | Roles, permisos, turnos, autorizaciones y trazabilidad |
| [Perfiles sectoriales](docs/SECTOR_PROFILES.md) | Supermercados, panaderías, rotiserías y gastronomía |
| [Calidad y pruebas](docs/QUALITY_AND_TESTING.md) | Estrategia de pruebas, calidad y control de dependencias |
| [Plan de trabajo](docs/ROADMAP.md) | Etapas, prioridades y definición de terminado |
| [Forma de trabajo](docs/WORKFLOW.md) | Regla de rama única, commits y documentación |
| [Estrategia de reutilización de código abierto](docs/OPEN_SOURCE_STRATEGY.md) | Proyectos reutilizables, licencias, riesgos y prueba de compatibilidad |
| [Catálogo de código reutilizable](docs/CODE_REUSE_CATALOG.md) | Inventario de proyectos, módulos y componentes candidatos |
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

**Ahora — Fase 0: preservar el alcance integral y elegir una base con pruebas reales**
- Consolidar reglas comerciales, dominio y contratos.
- Mantener el mapa integral: no reducir el proyecto a POS; comparar ERP modular, WMS, canales, producción, promociones y analítica.
- Ampliar la comparación integral a MyCompany/lsFusion 6.2, además de Posnic 1.9.2 y ERPNext 16.60.0.
- Evaluar módulos especializados como Simple WMS, OpenLinker, OfferKit, DuckDB/Superset y Node-RED detrás de contratos.
- Validar automáticamente la aritmética y consistencia del dataset de prueba mediante GitHub Actions (última ejecución: 21/21 pruebas aprobadas).
- Comparar las tres plataformas integrales con P01–P19 y los escenarios multiárea P20–P26.
- Mantener el modelo de rentabilidad con eliminación de cargos internos entre áreas y distinguir transferencias gerenciales de operaciones intercompany reales.
- Probar funcionamiento local, cierre forzado, recuperación, caja, inventario y backup.
- Medir cuánto código podemos reutilizar sin modificar núcleos de forma invasiva.
- Verificar la adaptación argentina y la viabilidad de ARCA en homologación.
- Revisar las licencias de cada componente y dependencia del paquete concreto.
- Elegir una sola fuente de verdad o confirmar el monolito modular propio.

El proyecto y sus dominios están en [Mapa integral de capacidades](docs/PRODUCT_CAPABILITY_MAP.md). La estructura multiárea está en [Áreas de negocio y dimensiones](docs/BUSINESS_LINES_AND_SEGMENTS.md). Los procesos mayoristas están en [Mayorista y distribución](docs/WHOLESALE_AND_DISTRIBUTION.md), los servicios en [Servicios B2B y contratos](docs/B2B_SERVICES_AND_CONTRACTS.md) y la medición económica en [Rentabilidad por área](docs/BUSINESS_UNIT_PROFITABILITY.md). Ninguna plataforma o módulo está aprobado por aparecer en el catálogo.
**Siguiente — Fase 1: núcleo transaccional**
- Catálogo, precios y unidades de medida.
- Carrito y venta POS.
- Descuentos y promociones con trazabilidad.
- Pagos mixtos y movimientos de caja.
- Inventario basado en movimientos.
- Usuarios, turnos y auditoría.
- Pruebas automatizadas de los flujos críticos.

Las etapas posteriores incorporarán sincronización offline, compras, canales, fiscalidad, perfiles sectoriales e inteligencia avanzada según el orden documentado en el roadmap.

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
