# Rubrova

Plataforma comercial integral para operar, administrar y hacer crecer negocios de distintos sectores, con un punto de venta completo, gestión omnicanal, funcionamiento resiliente sin conexión e inteligencia basada en los datos reales del negocio.

## Identidad y facilidad de renombrado

La denominación actual es provisoria y se mantiene únicamente en este README y en el nombre del repositorio. Los demás documentos, módulos, paquetes, servicios, tablas, eventos e identificadores internos utilizan nombres funcionales y neutrales. Si decidimos cambiar el nombre, el objetivo es modificar solamente el nombre del repositorio y este README.

La disponibilidad legal de la denominación y de los dominios todavía no está verificada. Antes de convertirla en marca pública habrá que consultar el buscador oficial del INPI, revisar variantes fonéticas y clases pertinentes, y comprobar los dominios.

## Estado actual

<sub>Fase 0 — definición del producto y base arquitectónica.</sub>

El repositorio acaba de inicializarse. En esta etapa estamos consolidando el alcance, las reglas de negocio, los límites entre módulos, las decisiones técnicas y los criterios de calidad. **Todavía no hay una aplicación funcional implementada.** No se deben presentar las capacidades planificadas como funcionalidades disponibles.

El avance se mide por decisiones documentadas, entregables verificables y pruebas ejecutadas, no por cantidad de archivos o commits.

## Qué estamos construyendo

Una plataforma que reúne en un solo lugar:

- **Punto de venta:** caja rápida, catálogo, lector de códigos, descuentos, promociones, medios de pago, devoluciones, cierres y periféricos.
- **Gestión comercial:** productos, variantes, precios, inventario, compras, proveedores, clientes, cuentas corrientes y sucursales.
- **Canales de venta:** local físico, tienda online, WhatsApp, marketplaces, pedidos telefónicos y delivery, con análisis por canal y consolidado.
- **Operación sectorial:** supermercados y autoservicios, kioscos y almacenes, panaderías, rotiserías y gastronomía; perfiles configurables sobre un núcleo común.
- **Administración y control:** usuarios, permisos, turnos, cajas, arqueos, autorizaciones, auditoría y movimientos internos.
- **Inteligencia del negocio:** rentabilidad, demanda, estacionalidad, precios, marcas, categorías, promociones, abastecimiento, tendencias y escenarios.
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
| [Calidad y pruebas](docs/QUALITY_AND_TESTING.md) | Estrategia de pruebas y criterios de aceptación |
| [Plan de trabajo](docs/ROADMAP.md) | Etapas, prioridades y definición de terminado |
| [Forma de trabajo](docs/WORKFLOW.md) | Regla de rama única, commits y documentación |
| [Referencias de investigación](docs/RESEARCH.md) | Proyectos estudiados, aprendizajes y fuentes |

## Etapa actual y próximos resultados

**Ahora — Fase 0: definición y fundamentos**
- Consolidar los requisitos funcionales y operativos.
- Acordar el modelo de dominio y las reglas económicas.
- Definir límites de módulos y contratos.
- Identificar riesgos fiscales, de sincronización, seguridad y hardware.
- Preparar criterios de aceptación antes de implementar.

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
**Estado del software:** sin implementación funcional todavía.
