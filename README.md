# Rubrova

Plataforma comercial integral para operar, administrar y hacer crecer negocios de distintos sectores, con un punto de venta completo, gestión omnicanal, funcionamiento resiliente sin conexión e inteligencia basada en los datos reales del negocio.

## Identidad y facilidad de renombrado

La denominación actual es provisoria y se mantiene únicamente en este README y en el nombre del repositorio. Los demás documentos, módulos, paquetes, servicios, tablas, eventos e identificadores internos utilizan nombres funcionales y neutrales. Si decidimos cambiar el nombre, el objetivo es modificar solamente el nombre del repositorio y este README.

La disponibilidad legal de la denominación y de los dominios todavía no está verificada. Antes de convertirla en marca pública habrá que consultar el buscador oficial del INPI, revisar variantes fonéticas y clases pertinentes, y comprobar los dominios.

## Probar el proyecto localmente

**El camino principal para desarrollar y usar Rubrova localmente es el runtime nativo, sin Docker.** En macOS Apple Silicon, Java 21, PostgreSQL 18 y Tomcat 9 ejecutan el servidor y el cliente en el propio equipo. Docker no es requisito para trabajar localmente. En CI, la aceptación principal y obligatoria es el runtime nativo macOS ARM64. También se ejecuta el POS nativo en Linux sin Docker; Docker/Linux se conserva como diagnóstico suplementario no bloqueante mientras se investiga un problema de acceso HTTP del cliente.

Ya existe un primer supervisor en `scripts/platform/run-local-native-preview.py`. Puede preparar una base aislada, iniciar el servidor, esperar el fin de la inicialización y luego iniciar el cliente web. El prototipo requiere artefactos compilados y Java 21, las herramientas nativas de PostgreSQL 18, Python 3 y Tomcat 9.0.124. Si Tomcat no está en caché, la primera preparación lo descarga y verifica; por eso todavía no es un instalador offline ni una entrega lista para una PC limpia.

Desde la raíz del repositorio, después de preparar Java 21 y PostgreSQL 18:

```bash
python3 scripts/platform/runtime-config.py init
mvn -B -ntp -f build/rubrova/pom.xml -Passemble -DskipTests package
mvn -B -ntp -f vendor/platform/pom.xml -pl server,web-client -am -DskipTests package
python3 scripts/platform/run-local-native-preview.py doctor
python3 scripts/platform/run-local-native-preview.py --no-open start
```

El comando de inicio abre el POS en `http://127.0.0.1:8080`; se detiene con Ctrl+C y conserva la base local. Se puede usar `--offline` antes de `doctor` o `start` para impedir descargas: sólo funcionará cuando Tomcat y los artefactos ya estén disponibles en caché. En macOS, si PostgreSQL 18 está en Postgres.app, indicá su carpeta bin mediante `RUBROVA_POSTGRES_BIN=/Applications/Postgres.app/Contents/Versions/18/bin`.

En macOS también podés hacer doble clic en `Iniciar Rubrova.command`, en la raíz del repositorio. Comprueba Java 21 y PostgreSQL 18, prepara la configuración, recompila si faltan artefactos o cambió la revisión, ejecuta el diagnóstico y abre el POS en el navegador. No instala dependencias del sistema por su cuenta; la primera preparación puede necesitar Maven e Internet para Tomcat.

Para abrir una **demostración con una caja, un artículo y 10 unidades de stock**, usá `Iniciar Rubrova - Demo.command`. Este modo tiene una base de datos, una configuración y puertos separados del runtime normal; no agrega datos de muestra a tu base principal y no incorpora endpoints ni simuladores de CI. La venta de muestra es persistente dentro de esa base de demostración.

En la ejecución CI más reciente `45641728845` (código `774387cae1876a2220091dea79c3df5a93023bd5`), el build completo, las validaciones, Windows y los recorridos POS nativos macOS ARM64 y Linux x86_64 pasaron. macOS se probó con conectividad externa habilitada; Linux completó el mismo ciclo con salida externa bloqueada. También pasaron las pruebas unitarias de configuración y ensamblado del modo Demo. El diagnóstico Docker/Linux continúa separado y no bloquea esta ruta; en la ejecución anterior el cliente Docker devolvió HTTP `000` tras cargar 717/717 módulos. Son pruebas de CI, no una instalación en tu Mac ni una autorización de producción.

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
11. Un proveedor externo puede fallar sin detener el POS/ERP local: todo conector tiene timeout, límites de reintentos, idempotencia, estado incierto y pruebas de fallo.

## Cómo leer la documentación

| Documento | Qué explica |
|---|---|
| [Visión y objetivos](docs/PRODUCT_VISION.md) | Problema, usuarios, propuesta de valor y principios |
| [Alcance funcional](docs/FUNCTIONAL_SCOPE.md) | Capacidades del producto y límites del alcance |
| [Requisitos del POS](docs/POS_REQUIREMENTS.md) | Venta, caja, descuentos, pagos, hardware y operación diaria |
| [Arquitectura](docs/ARCHITECTURE.md) | Estructura técnica, módulos, datos y decisiones de plataforma |
| [Arquitectura modular distribuida](docs/DISTRIBUTED_MODULAR_ARCHITECTURE.md) | Servicios independientes, APIs/eventos, idempotencia, CAS y operación local |
| [Modos de ejecución y control local](docs/RUNTIME_MODES_AND_LOCAL_CONTROL.md) | Ejecución nativa sin Docker, Docker local, conexión remota, supervisor y cambio seguro de destino |
| [Modelo de dominio](docs/DOMAIN_MODEL.md) | Entidades, movimientos, estados y relaciones |
| [Captura de datos y base analítica](docs/DATA_CAPTURE_AND_ANALYTICAL_FOUNDATION.md) | Fechas históricas, áreas/canales, compras, stock, pagos, cajeros, reclamos, exportaciones e IA de lectura |
| [Inteligencia del negocio](docs/BUSINESS_INTELLIGENCE.md) | Métricas, rentabilidad, estacionalidad, tendencias y pronósticos |
| [Perfil 360 e inteligencia por cliente](docs/CUSTOMER_360_AND_INTELLIGENCE.md) | Preferencias, marcas, productos, RFM, retención, CLV y rentabilidad por cliente |
| [Identidad del pagador y conciliación](docs/PAYMENT_IDENTITY_AND_RECONCILIATION.md) | Datos de QR, tarjeta, transferencia y efectivo; integraciones de cobro, privacidad e identidad transversal |
| [Arquitectura de terminales de pago](docs/PAYMENT_TERMINAL_INTEGRATION_ARCHITECTURE.md) | Terminal autónoma e integrada, adaptadores, entidades, estados, idempotencia, webhooks y conciliación |
| [Implementación de demanda, rentabilidad y marcas](docs/DEMAND_AND_MARGIN_INTELLIGENCE.md) | Datos fuente, herramientas reutilizables, costos, pronósticos, primeras/segundas marcas y pruebas de aceptación |
| [Benchmark de demanda](scripts/forecasting/benchmark.py) | Comparación reproducible de baselines y StatsForecast sobre datos mensuales sintéticos |
| [Canales e integraciones](docs/CHANNELS_AND_INTEGRATIONS.md) | Omnicanalidad, ARCA, Mercado Libre y pagos |
| [Seguridad y auditoría](docs/SECURITY_AND_AUDIT.md) | Roles, permisos, turnos, autorizaciones y trazabilidad |
| [Perfiles sectoriales](docs/SECTOR_PROFILES.md) | Supermercados, panaderías, rotiserías y gastronomía |
| [Calidad y pruebas](docs/QUALITY_AND_TESTING.md) | Estrategia de pruebas, calidad y control de dependencias |
| [Continuidad y recuperación](docs/OPERATIONAL_RESILIENCE_AND_RECOVERY.md) | Fallos de proceso, idempotencia, CAS, backups, restore y pruebas P27–P55 |
| [Resiliencia de integraciones y errores](docs/INTEGRATION_RESILIENCE_AND_ERROR_HANDLING.md) | Timeouts, reintentos seguros, circuit breaker, Outbox, mensajes en español y simulación de fallos para cada proveedor |
| [Herramientas y componentes adicionales](docs/TOOLING_AND_REUSE_RESEARCH_2026_11.md) | Evaluación de librerías de resiliencia, pruebas de fallos, ARCA, conectores y módulos reutilizables |
| [Copias de seguridad y recuperación](docs/BACKUP_AND_MIGRATION_STRATEGY.md) | Backup portable sin cifrado de aplicación, checksums, reinstalación de Windows y restauración guiada |
| [Plan maestro de implementación](docs/MASTER_IMPLEMENTATION_PLAN.md) | Orden ejecutivo: POS, ERP, contabilidad, reportes, expansión y logística |
| [Estado real del proyecto](docs/PROJECT_STATUS.md) | Qué funciona, qué falta y el siguiente bloque de trabajo |
| [Propiedad del código y operación offline](docs/SOURCE_OWNERSHIP_AND_OFFLINE_RUNTIME.md) | Fork controlado de MyCompany/lsFusion, compilación reproducible, operación local, cambios y actualizaciones seguras |
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

Rubrova ya ejecutó en CI el runtime nativo sobre un runner Apple Silicon `macos-26`, con Java 21 ARM64 y PostgreSQL 18 ARM64. En `45641728845` el POS completó venta, pago, stock y cierre. Linux x86_64 nativo completó el mismo recorrido con salida externa bloqueada. Falta repetirlo en tu Mac y validar periféricos. Docker/Linux se conserva como diagnóstico automático no bloqueante.

## Etapa actual y próximos resultados

**Ahora — Fase 0: piloto integrado MyCompany 6.2**

MyCompany 6.2 es el primer piloto de integración, todavía no aprobado para el uso diario. Tryton 8.0 + tryton-ar 8.0 se mantiene como contraste fiscal argentino. ERPNext 16 queda en reserva y sólo se reabre si una brecha concreta justifica la comparación.

- Reutilizar los módulos de Retail POS, sesiones, pagos mixtos, devoluciones, inventario, costos, compras, ventas y facturación.
- Mantener las personalizaciones en un módulo Rubrova separado del código upstream.
- Preparar y validar los artefactos desde las fuentes vendorizadas. El desarrollo local prioriza PostgreSQL + Java + Tomcat nativos en macOS. CI exige la aceptación nativa macOS; Linux nativo y Docker/Linux se conservan como diagnósticos automáticos no bloqueantes.
- La aceptación funcional [CI 45503956218](https://github.com/JavierGrecco/Rubrova/actions/runs/45503956218) probó en Docker una venta de ARS 1.250 en efectivo, factura/pago persistidos, stock (10 → 9), caja, cierre `CLOSED` y resiliencia HTTP. Luego, [CI 45548326798](https://github.com/JavierGrecco/Rubrova/actions/runs/45548326798) repitió el recorrido comercial básico en el runtime nativo macOS ARM64. Son dos evidencias distintas y ninguna habilita por sí sola el uso diario.
- En `45641728845`, el smoke nativo macOS ARM64 completó el recorrido comercial básico con conectividad externa habilitada, y Linux x86_64 completó el mismo recorrido con la salida externa bloqueada. También pasaron las pruebas unitarias del modo Demo, que comprueban que su configuración y datos quedan separados del runtime normal. El diagnóstico Docker/Linux se conserva como advertencia no bloqueante.
- El POS sigue en aceptación: faltan devoluciones/reintegros, vuelto, pagos mixtos y tarjeta, movimientos y arqueo de caja, permisos por perfil, backup/restore, periféricos y pruebas fiscales argentinas.
- La localización aún es parcial. La navegación general y varios formularios heredados requieren revisión. El JAR de MyCompany 6.2 ya se ejecuta nativamente en Java ARM64; que la imagen Docker oficial publique `linux/amd64` sólo afecta al camino Docker en Apple Silicon, no al runtime nativo.

El detalle de módulos y bloques está en el [Inicio de implementación](docs/IMPLEMENTATION_START.md). La instalación paso a paso está en la [guía del primer piloto](docs/MYCOMPANY_RUNTIME_INSTALL.md). La [Evaluación de plataformas](docs/PLATFORM_EVALUATION.md) conserva las puertas de aceptación.

**Siguiente resultado:** una jornada de mostrador completa y repetible, conectada a los datos de gestión, con pagos y stock conciliados, devolución auditada, cierre de caja y recuperación probada.

MyCompany 6.2 y lsFusion 6.2 ya están vendorizados y Rubrova construye sus propios artefactos. El smoke actual de CI prueba una venta y cierre sintéticos, además de conciliación de stock y efectivo; la instalación anfitriona, los circuitos aún pendientes y la aceptación operativa siguen abiertos. El estado detallado está en [Estado real del proyecto](docs/PROJECT_STATUS.md) y la estrategia completa en [Propiedad del código y operación offline](docs/SOURCE_OWNERSHIP_AND_OFFLINE_RUNTIME.md).

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

**Estado del producto:** piloto MyCompany 6.2 en evolución; el ciclo comercial básico pasó en Docker y en el runtime nativo macOS ARM64 de CI. No está aprobado para uso diario.  
**Estado del software:** fuentes lsFusion/MyCompany fijadas y vendorizadas, extensiones propias, supervisor nativo y aceptación comercial básica en CI sobre macOS ARM64 y Linux x86_64 sin Docker. Siguen pendientes la prueba en un Mac físico, el instalador offline, el panel de control, Windows nativo y los circuitos comerciales restantes; el cliente Docker/Linux tiene un diagnóstico HTTP pendiente.
