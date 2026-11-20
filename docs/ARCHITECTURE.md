# Arquitectura

## Contexto de reutilización

La plataforma está destinada a uso interno y privado del negocio, sin distribución ni reventa previstas. Por eso, la selección de tecnología debe considerar proyectos GPL y AGPL además de licencias permisivas. No se descarta un proyecto por copyleft: se evalúan su cobertura, capacidad de adaptación, mantenimiento y las condiciones concretas de la licencia. Para AGPL se analiza especialmente si usuarios interactúan remotamente por red con una versión modificada. Si cambia el uso previsto, se revisan las obligaciones antes de distribuir o habilitar acceso a terceros.

La estrategia prioriza aprovechar proyectos completos y módulos maduros cuando su adaptación sea más eficiente que construirlos. Cuando la independencia del producto lo requiera, se incorpora el código fuente completo en vendor/ y se mantiene un fork interno con commits de origen, licencias y pruebas de actualización. Se permite adoptar, extender, modificar o mantener un fork interno si la licencia y el costo de mantenimiento son aceptables. Siempre se conservan licencias, avisos, atribuciones y un registro de origen/versiones.

## Dirección técnica

La dirección es una **plataforma modular con límites explícitos**, que puede combinar un núcleo POS+ERP integrado y servicios Rubrova independientes donde realmente aporten valor. Cada servicio que Rubrova desarrolle o separe tendrá responsabilidad, almacenamiento, contrato, pruebas, despliegue, versión y recuperación propios. No se obliga a que todas las capacidades del negocio sean microservicios desde la primera versión.

La estrategia de implementación es **reuse-first**: antes de construir un dominio propio, se buscan aplicaciones, módulos, plugins, SDK y bibliotecas existentes que resuelvan la necesidad de forma mantenible. Una suite integrada puede conservar juntas POS, ventas, inventario, compras, costos, pagos/caja y contabilidad como núcleo único, sin llamar microservicios a sus módulos. Las capacidades adicionales de Rubrova se conectan mediante APIs/eventos soportados y no duplican autoridades.

### Puerta arquitectónica para reutilizar una aplicación

Para adoptar una aplicación externa hay dos caminos válidos:

1. **Servicio de dominio acotado:** almacenamiento/credenciales propios, API/eventos versionados, despliegue, migraciones, backup, restauración y rollback independientes; invariantes comprobables y ninguna autoridad duplicada.
2. **Núcleo operativo integrado POS+ERP:** puede compartir servidor, base y ciclo de despliegue si eso permite cerrar el circuito comercial/administrativo con una única autoridad coherente. La evaluación debe registrar el acoplamiento, el impacto de actualizaciones, la API disponible, exportación completa, restauración en equipo limpio, permisos, extensibilidad y ruta de salida. No se presenta como microservicios.

**Una API no convierte por sí sola un ERP integrado en microservicios.** La decisión no es fingir que la suite es distribuida, sino medir si la aplicación integrada es la mejor base de operación para el negocio privado y aislar sólo las capacidades de Rubrova que deban evolucionar por separado.

### Candidatos actuales: oportunidades, no decisiones

- **MyCompany/lsFusion 6.2:** módulos ERP/POS y extensiones propias; los módulos de una instalación comparten base de datos. Debe probarse si una capacidad acotada puede operar detrás de un contrato sin mezclar autoridades de ventas, stock y compras.
- **Tryton, serie 7.8:** módulos de negocio, PostgreSQL y POS oficial `sale_point`. Éste registra ventas/devoluciones y pagos; al contabilizar genera movimientos de stock y asientos contables. Sus módulos viven en el mismo servidor/base; hay que demostrar la separación antes de adoptarlo.
- **Dolibarr 24.0.3:** módulos, REST API, hooks y triggers. Aplicación integrada; evaluar si las partes requeridas pueden extraerse o encapsularse como servicio de dominio aislado.
- **ERPNext 16.60.0/Frappe 16:** cobertura ERP y apps extensibles. Un site/bench integra runtime y persistencia; no llamar microservicios a sus apps.
- **Posnic 1.9.2:** candidato POS especializado; comprobar si POS, stock y compras pueden delimitarse y revisar componentes del instalador.
- **uniCenta 5.5.2:** pendiente de acceso verificable al código y revisión de licencia/terceros.

Ninguno está aprobado. Una prueba funcional exitosa no basta: deben superarse propiedad del dato, aislamiento, actualización, exportación, recuperación y compatibilidad. Ver [Estrategia reuse-first](REUSE_FIRST_IMPLEMENTATION_STRATEGY.md), [Shortlist de componentes reutilizables](REUSE_COMPONENTS_SHORTLIST.md) y [Evaluación de plataformas](PLATFORM_EVALUATION.md).

### Orden de implementación

1. Filtrar aplicaciones y módulos existentes por función, licencia, madurez, API y aislamiento real.
2. Probar instalaciones acotadas con los mismos escenarios.
3. Comprobar que el módulo candidato se opera, actualiza y restaura como unidad independiente.
4. Reutilizarlo y crear adaptadores cuando supere las puertas.
5. Adoptar la suite como núcleo integrado cuando supere la comparación; construir como servicio propio sólo las brechas que deban aislarse y que la plataforma no cubra.

No se empieza automáticamente por un Gateway, Ventas e Inventario propios. Tampoco se cambia a un monolito propio si falla una suite integrada. Se mantiene el diseño distribuido y se reutiliza todo componente compatible que sostenga esos límites.

## Principios

- Los módulos representan responsabilidades del negocio.
- Cada módulo es dueño de sus reglas y datos.
- Otros módulos usan contratos públicos, no leen tablas internas ajenas.
- No existen dependencias circulares.
- Los eventos describen hechos ocurridos; no sustituyen transacciones necesarias.
- Operaciones financieras y de inventario usan transacciones explícitas.
- Servicios externos quedan detrás de adaptadores.
- La lógica de negocio no depende de una interfaz específica.
- El modo local no depende de que una tarea del navegador siempre esté disponible.
- El código externo no se incorpora sin revisión de licencia, mantenimiento, seguridad y compatibilidad.
- El núcleo de Rubrova se construye desde fuentes versionadas dentro del repositorio; no depende de imágenes, JAR o WAR remotos para iniciar.
- Las dependencias de compilación se fijan y cachean; el runtime productivo se empaqueta y debe operar sin salida a Internet.
- Cada dato transaccional tiene un único sistema responsable; no se ejecutan dos motores de stock o ventas como fuentes de verdad.

## Módulos

| Módulo | Responsabilidad |
|---|---|
| Identidad y acceso | Usuarios, sesiones, roles, permisos |
| Organización | Negocios, sucursales, cajas y ubicaciones |
| Catálogo | Productos, variantes, marcas, categorías y unidades |
| Precios y descuentos | Listas, vigencias, promociones y cupones |
| Ventas POS | Carrito, venta, líneas y tickets |
| Pedidos y canales | Pedidos propios y externos, atribución y entrega |
| Pagos y caja | Cobros, conciliación, caja, turnos y reembolsos |
| Inventario | Existencias, reservas, lotes, movimientos y conteos |
| Compras | Proveedores, cotizaciones, órdenes, recepciones y costos |
| Clientes | Perfil, cuenta corriente, beneficios y consentimiento |
| Producción | Recetas, órdenes, lotes, consumos, rendimientos y mermas |
| Fiscal | Comprobantes, autorizaciones, notas de crédito y conciliación |
| Promociones | Campañas, combos y medición de resultados |
| Inteligencia | Métricas, modelos, pronósticos, alertas y recomendaciones |
| Auditoría | Eventos, autorizaciones y consultas sensibles |
| Integraciones | Adaptadores externos y webhooks |
| Plataforma | Sincronización, notificaciones, archivos, backups y observabilidad |

## Capas por módulo

- Dominio: entidades, valores, reglas e invariantes.
- Aplicación: casos de uso y coordinación.
- Interfaces: API, tareas y entrada desde la interfaz.
- Infraestructura: base de datos, colas, proveedores y dispositivos.
- Pruebas: unitarias, integración, contrato y aceptación.

La estructura debe permitir encontrar responsabilidades sin imponer carpetas innecesarias.

## Datos y persistencia

La tecnología de persistencia depende de la plataforma que supere la prueba:

- Si se reutiliza Posnic, su MongoDB/Mongoose debe permanecer dentro del único servicio que se le asigne; si sus modelos mezclan ventas, compras y stock de manera inseparable, no cumple la puerta de adopción como servicio independiente.
- Si se reutiliza Tryton, su PostgreSQL y los módulos oficiales deben quedar dentro del límite de servicio que se demuestre aislable. `sale_point` genera movimientos de stock y asientos contables, por lo que la prueba debe resolver quién posee inventario y contabilidad.
- Si se reutiliza Dolibarr, su base y migraciones no pueden compartirse con otros servicios Rubrova; la REST API no sustituye la prueba de aislamiento de datos.
- Si se reutiliza ERPNext, su persistencia MariaDB se acepta sólo dentro del límite de aplicación/servicio demostrado; PostgreSQL no se considera equivalente ni se fuerza durante esta ronda.
- Cada servicio mantiene su almacenamiento privado, migraciones y credenciales. PostgreSQL es candidato para servicios transaccionales; SQLite puede ser útil para persistencia local de puestos/edge, según las pruebas. La decisión concreta se toma por servicio y no habilita consultas SQL cruzadas.
- Historial de movimientos para caja, pagos, inventario y cuentas corrientes.
- Fotografía de valores relevantes al momento de la venta.
- Identificadores globales para operaciones originadas sin conexión.
- Migraciones y esquemas versionados.
- Consultas analíticas separadas lógicamente del flujo de caja.

No se elige una base de datos global para toda la plataforma. Cada servicio posee su almacenamiento, credenciales, migraciones y estrategia de backup/restore. La consistencia entre servicios se obtiene mediante contratos, eventos, Sagas y conciliación, no mediante escrituras cruzadas.
## Aislamiento de negocios

Toda entidad operativa pertenece a un negocio y, cuando corresponde, a sucursal o ubicación. El servidor valida el contexto del negocio; nunca confía en identificadores del cliente sin comprobar permisos. Se evaluará Row-Level Security como defensa adicional. Las pruebas deben intentar acceder a datos de otro negocio desde cada ruta.

## Operación sin conexión

- Persistir localmente antes de confirmar al usuario que la operación quedó guardada.
- Cola duradera de operaciones pendientes.
- UUID, dispositivo, negocio, secuencia local y versión de esquema.
- Envío repetible con idempotencia del servidor.
- Bandeja de entrada para deduplicar eventos.
- Reintentos con backoff y estado visible.
- Conflictos explícitos para stock, precios y datos maestros.
- Reconciliación y estado fiscal separado.
- Recuperación tras cierre, reinicio, pérdida de proceso y corte durante sincronización.

Las cajas de una sucursal deben coordinar las reservas con el servicio local de Inventario por LAN. Si un puesto pierde esa conexión, sólo puede vender stock cubierto por cuotas exclusivas preasignadas o registrar la operación como pendiente de conciliación bajo una política explícita. Idempotencia evita repetir la misma venta; CAS/reservas evita que dos ventas distintas consuman la misma unidad. No usar "último cambio gana" para dinero, ventas o stock. Ver [Arquitectura modular distribuida](DISTRIBUTED_MODULAR_ARCHITECTURE.md).

No prometer offline total: ARCA, pagos externos y datos de otros dispositivos pueden requerir conexión. El offline POS debe ser probado incluso después de cerrar y volver a abrir la aplicación; mantener una pestaña abierta no alcanza.

## Eventos y sincronización

Usar Outbox/Inbox cuando una transacción deba producir un mensaje confiable. Cada evento incluye id, tipo, versión, fecha, negocio, origen y correlación. No incluir secretos ni datos personales innecesarios.

La cola de sincronización no reemplaza el registro transaccional. Una venta, su pago y su movimiento de inventario deben confirmarse de forma coherente antes de notificarse o replicarse. Los reintentos son idempotentes y la recuperación debe poder reconstruirse desde datos duraderos.

Si se adopta una plataforma integral, primero se prueba su mecanismo de eventos y sincronización nativo. No se agrega PowerSync, Redis u otro servicio por anticipado: solo después de medir una necesidad concreta y demostrar que no crea una segunda autoridad de datos.

Dos cajas aisladas no conocen los movimientos mutuos. El inventario local debe coordinarse desde un servicio de sucursal; las cuotas offline son exclusivas y acotadas. Sin comunicación ni preasignación no es posible garantizar que ambas no vendan la última unidad. Los detalles de CAS, ledger, reservas y contingencia están en [Arquitectura modular distribuida](DISTRIBUTED_MODULAR_ARCHITECTURE.md).
## Hardware

La interfaz POS se comunica con una capa de dispositivos independiente. Los protocolos y controladores de impresoras, lectores, balanzas, cajones, pantallas y terminales se aíslan detrás de adaptadores. Se prioriza una pasarela local cuando sea necesaria para acceso USB, serie o red y para mantener la caja desacoplada de los servicios externos.

No se afirma compatibilidad por marca genérica: cada modelo, conexión y sistema operativo se registra en una matriz de pruebas físicas.

## Observabilidad

Logs estructurados, correlación por operación, métricas de latencia y sincronización, trazas de flujos, alertas de fallos fiscales y de pago, estado visible para operaciones pendientes, backups automáticos y pruebas de restauración.

## Decisiones y validaciones pendientes

- [x] Dirección de servicios independientes por dominio, contratos de comunicación y propiedad única del dato.
- [x] Estrategia de reutilización compatible con uso interno privado, con control de licencias por componente.
- [x] Ronda integral de tres candidatos: MyCompany/lsFusion 6.2, Posnic 1.9.2 y ERPNext 16.60.0/Frappe 16.
- [x] Protocolo común de aceptación y datos sintéticos documentados.
- [ ] Instalar y ejecutar MyCompany/lsFusion 6.2 en entorno local aislado y probar un módulo custom.
- [ ] Instalar y ejecutar Posnic en entorno local aislado.
- [ ] Instalar y ejecutar ERPNext/Frappe en entorno local aislado.
- [ ] Completar P01–P26 del protocolo y registrar evidencia.
- [ ] Validar límites y despliegue independiente de los servicios; decidir qué plataforma o componente externo puede cubrir cada dominio sin fusionar las autoridades de datos.
- [ ] Confirmar una solución fiscal argentina con pruebas de homologación.
- [ ] Cerrar interfaz, persistencia local y eventual servicio local según los resultados.
- [ ] Validar hardware con modelos físicos concretos.
- [ ] Establecer backup, restauración y observabilidad para la plataforma elegida.

Ninguna validación pendiente se considera implementada por estar escrita en este documento.
## Candidatos de reutilización priorizados (19/11/2026)

La evaluación integral compara MyCompany/lsFusion por su extensibilidad modular, Posnic por su cercanía a una caja local y ERPNext/Frappe por su amplitud administrativa, productiva y contable. Ninguno está aprobado: la recuperación offline, la localización argentina y el esfuerzo de adaptación todavía deben demostrarse.

Componentes especializados que pueden acelerar el producto sin convertirse en otra fuente de verdad:

- **Hardware y tickets:** pos-toolkit (Apache-2.0) contiene un plugin Rust/Tauri v2 para ESC/POS, cajón, scanners seriales y balanzas HID, además de un constructor TypeScript de tickets. No es universal para navegador y `register-core` figura como planificado.
- **Pruebas de hardware:** emupos y ESCPost (Apache-2.0) para simulación, diagnóstico y render de tickets; la simulación no sustituye la prueba física.
- **Fiscalidad:** arca-sdks / `@ramiidv/arca-facturacion` 7.1.0 (MIT, Node >=22.12) como candidato para WSAA/WSFE/WSFEX/CAEA, sujeto a homologación y control propio de idempotencia y estados inciertos.
- **Offline:** evaluar primero el mecanismo nativo de la plataforma. PowerSync Open Edition (Apache-2.0) y Dexie (Apache-2.0) quedan como alternativas: PowerSync para sincronización SQLite/PostgreSQL según edición; Dexie para IndexedDB, no para sincronización distribuida completa.

NexoPOS sigue bloqueado hasta aclarar la discrepancia entre su archivo LICENSE y composer.json. Odoo Community 20 y Medusa v2 se conservan como investigación histórica, no como finalistas activos.

La decisión y los criterios de prueba están en [Evaluación de plataformas](PLATFORM_EVALUATION.md). Ninguno de los candidatos se considera incorporado o probado en Rubrova.

## Composición de módulos de terceros

La arquitectura permite reutilizar módulos, adaptadores y servicios de proyectos diferentes. Se define cómo incorporarlos en [Composición de módulos y contratos](MODULE_COMPOSITION.md).

Reglas obligatorias:
- Cada agregado y cada ledger tienen un único módulo responsable.
- Los módulos externos se integran por puertos/capacidades y adaptadores; no comparten tablas ni hacen escrituras SQL directas entre sí.
- Las APIs y eventos se versionan, autentican, correlacionan y prueban.
- Los webhooks y mensajes se procesan de manera idempotente; los estados inciertos se concilian con el sistema autoritativo.
- Las operaciones distribuidas usan procesos durables y compensaciones explícitas cuando no existe una transacción común.
- La integración debe poder sustituirse sin reescribir reglas comerciales.
- La licencia, el commit, las dependencias, los avisos y las pruebas de cada componente quedan inventariados.

## Compatibilidad multiplataforma

Windows, Linux y macOS son objetivos del producto. No obligan a que todos los componentes compartan el mismo binario:

| Capa | Estrategia |
|---|---|
| Dominio, casos de uso y contratos | Neutral respecto del OS |
| Interfaz web/PWA | Navegador en Windows, Linux y macOS; móvil/handheld según capacidad |
| API y módulos de servidor | Contenedores/runtime compatible, independiente del sistema del puesto |
| Integraciones cloud y webhooks | Adaptador de servidor |
| Hardware USB/serie/Bluetooth | Puente local con implementaciones por OS y modelo |
| Paquete nativo | Solo cuando la experiencia o el acceso a dispositivo lo exijan |

Un componente valioso de Linux, Android o Windows no se descarta por sí solo. Se incorpora detrás de una capacidad estable y se crean adaptadores para los sistemas faltantes. La matriz de compatibilidad registra qué está probado de verdad.

La selección de plataformas integrales y la investigación de módulos son decisiones distintas: MyCompany, Posnic y ERPNext se comparan como posibles bases; Simple WMS, OpenLinker, OfferKit y las herramientas analíticas se estudian como módulos/adaptadores.


## Modelo multiárea y dimensiones de responsabilidad

Rubrova separa entidad legal, unidad de negocio/centro de beneficio, centro de costo, canal, sucursal, depósito, territorio, cliente, proyecto y contrato. Una venta mayorista originada por WhatsApp no se transforma en una venta del área digital solo por el canal. Las dimensiones no se sustituyen unas a otras.

Cada documento tiene una dimensión principal por defecto y cada línea puede conservar su propia unidad de negocio y asignación económica. Los recursos y maestros pueden compartirse con políticas de disponibilidad, permisos y costo de uso.

Ver [Áreas de negocio y dimensiones](BUSINESS_LINES_AND_SEGMENTS.md) y [Rentabilidad por área](BUSINESS_UNIT_PROFITABILITY.md).

## Separación de pedido, venta, fulfillment y despacho

El pedido es el compromiso comercial; la venta/factura es el hecho económico/fiscal; el fulfillment es la preparación; el envío es el movimiento físico; el tracking es una referencia externa que puede conocerse después.

Un pedido puede dividirse en entregas parciales, y un envío puede consolidar pedidos compatibles. El número de guía/seguimiento es opcional hasta que el operador lo emite; se añade después como una actualización auditada. Las entregas propias, retiro en depósito y handoff a transporte externo son modalidades diferentes.

Ver [Mayorista y distribución](WHOLESALE_AND_DISTRIBUTION.md).

## Servicios y compromisos B2B

Los servicios son líneas de catálogo con unidad de cobro y costo. Los contratos versionados originan obligaciones, calendarios, visitas y órdenes de trabajo. Las órdenes conservan SLA, tareas, responsable, recursos, horas, materiales, evidencia y aceptación. Un contrato puede estar vinculado a ventas mayoristas y a servicios, sin replicar el cliente.

Ver [Servicios B2B y contratos](B2B_SERVICES_AND_CONTRACTS.md).

## Resultado por área y consolidación

Los hechos económicos llevan dimensiones de unidad de negocio, centro de costo, canal, sucursal, cliente, producto, proyecto o contrato según corresponda. Los costos directos se imputan donde suceden; los compartidos permanecen visibles y pueden distribuirse mediante reglas versionadas. La vista consolidada elimina la duplicación de las asignaciones y reconcilia con el libro contable.


## Logística e interoperabilidad con sistemas externos

El dominio logístico posee Shipment, HandlingUnit, CarrierBooking, TrackingReference y TrackingEvent. No pertenece al POS ni al adaptador de un transportista. Los pedidos y ventas pueden existir antes de la guía; el módulo de logística recibe una solicitud de fulfillment, prepara uno o varios envíos y asocia la referencia externa cuando está disponible.

Los transportistas y agregadores se conectan por adaptadores bajo un contrato común de capacidades. El adaptador conserva códigos y payloads originales, normaliza eventos sin borrar el origen y procesa webhooks con idempotencia. Los agregadores de tracking (por ejemplo, AfterShip/17TRACK) son proveedores de visibilidad; no se consideran automáticamente operadores de contratación, creación de guías o etiquetas.

La integración contable usa un paquete canónico y perfiles por destino. Rubrova genera lotes de exportación balanceados, revisables e idempotentes; el ERP contable designado conserva el libro legal y/o los comprobantes que le correspondan. Nunca se sincroniza el mismo documento a dos emisores ni se mantienen dos ledgers editables sin una autoridad definida.

Referencias:
- [Logística argentina y seguimiento unificado](ARGENTINA_LOGISTICS_INTEGRATION.md)
- [Interoperabilidad contable y administrativa](ACCOUNTING_INTEROPERABILITY.md)
- [Investigación de mercado y oportunidades](MARKET_RESEARCH_AND_ADDITIONAL_OPPORTUNITIES.md)
- [Continuidad operativa y recuperación](OPERATIONAL_RESILIENCE_AND_RECOVERY.md)

## Ingestión documental y automatización

Facturas, remitos, contratos y constancias ingresan a una bandeja de documentos. El archivo original se conserva inmutable con checksum; OCR y extracción de campos generan datos derivados con versión, evidencia de origen y confianza. La revisión humana precede la generación de cuentas a pagar, comprobantes o asientos.

OCRmyPDF/invoice2data y Paperless-ngx son candidatos de procesamiento/archivo, no autoridades contables. Las automatizaciones y motores de workflow ejecutan pasos periféricos por APIs; no escriben directamente sobre tablas del ledger, ventas, stock o pagos.

## Analítica y pronóstico

El OLTP sigue siendo autoridad transaccional. DuckDB/Polars y los modelos de forecasting se utilizan en lecturas, snapshots y pipelines analíticos separados. Los reportes guardan definición, versión, fecha, cobertura y fuente; las predicciones se comparan con baselines mediante backtesting temporal. Ningún forecast confirma compras, modifica precios ni descuenta stock sin una decisión autorizada.

El asistente puede sugerir, explicar y preparar simulaciones, pero las decisiones que cambian dinero, stock, impuestos o compromisos requieren validación de reglas y permisos.


## Propiedad de fuentes y ejecución local

La base inicial es un fork controlado de MyCompany 6.2 y lsFusion 6.2, versionados en vendor/mycompany/ y vendor/platform/. Los módulos de Rubrova permanecen separados en extensions/lsfusion/; los cambios directos del motor se documentan como parches bajo patches/lsfusion/. El agregador Maven build/rubrova/pom.xml compone el motor y la solución desde el mismo repositorio.

El funcionamiento del POS/ERP principal es local en una PC. Ningún recurso estático, JAR, WAR, imagen Docker o base de datos se descarga durante el arranque. Las integraciones fiscales, de pagos, tiendas y transportistas son adaptadores remotos opcionales y sus fallos no detienen la operatoria local permitida. Ver [Propiedad del código y operación offline](SOURCE_OWNERSHIP_AND_OFFLINE_RUNTIME.md).
