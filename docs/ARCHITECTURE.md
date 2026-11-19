# Arquitectura

## Contexto de reutilización

La plataforma está destinada a uso interno y privado del negocio, sin distribución ni reventa previstas. Por eso, la selección de tecnología debe considerar proyectos GPL y AGPL además de licencias permisivas. No se descarta un proyecto por copyleft: se evalúan su cobertura, capacidad de adaptación, mantenimiento y las condiciones concretas de la licencia. Para AGPL se analiza especialmente si usuarios interactúan remotamente por red con una versión modificada. Si cambia el uso previsto, se revisan las obligaciones antes de distribuir o habilitar acceso a terceros.

La estrategia prioriza aprovechar proyectos completos y módulos maduros cuando su adaptación sea más eficiente que construirlos. Se permite adoptar, extender, modificar o mantener un fork interno si la licencia y el costo de mantenimiento son aceptables. Siempre se conservan licencias, avisos, atribuciones y un registro de origen/versiones.

## Dirección técnica

La dirección sigue siendo un **monolito modular con límites claros**, una base transaccional central y capacidad local para operar durante interrupciones de conectividad. No se dividirá en microservicios sin una necesidad medida.

La estructura del negocio y las invariantes son propias. Los frameworks y módulos externos se evalúan como herramientas reemplazables: no deben decidir qué significa una venta, un pago, un movimiento de caja o un movimiento de inventario.

## Plataformas bajo evaluación

No hay framework ni base de datos aprobados todavía. La ronda de prueba compara tres candidatos integrales, sin ejecutarlos juntos ni crear varias fuentes de verdad:

- **MyCompany/lsFusion 6.2:** aplicación ERP/POS modular con CRM, ventas, compras, inventario multi-depósito, producción, facturación, proyectos y RR. HH. La aplicación MyCompany declara Apache-2.0; la plataforma lsFusion tiene licencia LGPL-3.0 independiente. Su cliente web permite evaluar desde navegador en los tres sistemas de escritorio, aunque la release no ofrece cliente macOS nativo. La localización argentina, los adquirentes, ARCA y el offline aún no están demostrados.
- **Posnic 1.9.2:** POS de escritorio Electron/Node con API local y MongoDB/Mongoose. Es el candidato más directo para validar caja, ventas, inventario y operación local. Su código es AGPL-3.0-only; el paquete revisado incorpora MongoDB SSPL-1.0 y amCharts 4 comercial. La edición self-hosted permite varios clientes sobre una base común, pero no sincroniza varias bases independientes entre cajas o sucursales. La evidencia offline publicada es limitada y no demuestra recuperación ante pérdida de energía o cierre forzado. La release 1.9.2 no incluye instalador macOS; para evaluar desde Mac se utilizará una VM Ubuntu Desktop con el AppImage Linux verificado.
- **ERPNext 16.60.0 + Frappe Framework 16:** candidato de mayor cobertura administrativa: inventario, compras, producción, costos y contabilidad. ERPNext es GPL-3.0 y Frappe Framework es MIT. El POS y el modo offline de esta versión deben comprobarse en la instalación concreta; no se presume recuperación duradera por documentación de versiones anteriores.

Las referencias exactas y el protocolo común están en [Evaluación de plataformas](PLATFORM_EVALUATION.md). Los pasos de instalación y las restricciones de sistema operativo están en [Laboratorio de evaluación](PLATFORM_LAB_SETUP.md). MyCompany se fija al tag 6.2 y a los hashes de su instalador/JAR; no mezclarlo con la documentación online 7.0. Posnic se prueba desde el tag `v1.9.2`; la rama `main` se revisa aparte porque contiene commits posteriores y `develop` estaba divergida. ERPNext se prueba mediante la imagen `frappe/erpnext:v16.60.0` desde `frappe_docker/pwd.yml` fijado al commit `ef24ebc0a411b6237694765f0b51d8f8f8dd13ce`; registrar la versión efectiva de Frappe con `bench version`.

**Alternativa de salida:** si ninguna opción supera los controles de integridad, operación local, recuperación y costo de adaptación, construir un monolito modular propio. En ese caso TypeScript y PostgreSQL son candidatos, no decisiones irrevocables. Los componentes especializados se integrarán detrás de contratos explícitos y nunca mantendrán un segundo libro de ventas, pagos o stock.
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

- Si se adopta Posnic, evaluar su MongoDB/Mongoose como base transaccional única y medir el costo de conservar o migrar sus modelos.
- Si se adopta ERPNext, aceptar y probar su persistencia MariaDB como parte del framework; PostgreSQL no se considera equivalente ni se fuerza durante esta ronda.
- Si construimos el monolito propio, PostgreSQL es el candidato para el registro central. La persistencia local se decidirá con pruebas, comparando SQLite y almacenamiento de navegador según el empaquetado elegido.
- Historial de movimientos para caja, pagos, inventario y cuentas corrientes.
- Fotografía de valores relevantes al momento de la venta.
- Identificadores globales para operaciones originadas sin conexión.
- Migraciones y esquemas versionados.
- Consultas analíticas separadas lógicamente del flujo de caja.

No se elige una base de datos por preferencia aislada: debe acompañar a una única plataforma transaccional y permitir backup, restauración y auditoría demostrables.
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

Dos dispositivos desconectados no pueden conocer cambios mutuos. Para varias cajas offline se evaluará un servicio local de sucursal o concentrador LAN. No usar "último cambio gana" para conflictos financieros o de stock.

No prometer offline total: ARCA, pagos externos y datos de otros dispositivos pueden requerir conexión. El offline POS debe ser probado incluso después de cerrar y volver a abrir la aplicación; mantener una pestaña abierta no alcanza.

## Eventos y sincronización

Usar Outbox/Inbox cuando una transacción deba producir un mensaje confiable. Cada evento incluye id, tipo, versión, fecha, negocio, origen y correlación. No incluir secretos ni datos personales innecesarios.

La cola de sincronización no reemplaza el registro transaccional. Una venta, su pago y su movimiento de inventario deben confirmarse de forma coherente antes de notificarse o replicarse. Los reintentos son idempotentes y la recuperación debe poder reconstruirse desde datos duraderos.

Si se adopta una plataforma integral, primero se prueba su mecanismo de eventos y sincronización nativo. No se agrega PowerSync, Redis u otro servicio por anticipado: solo después de medir una necesidad concreta y demostrar que no crea una segunda autoridad de datos.

Dos cajas aisladas no conocen los cambios mutuos. No usar "último cambio gana" para dinero, ventas, caja o stock. Si más adelante necesitamos varias cajas independientes sin internet, se evaluará un concentrador local de sucursal y un protocolo de conciliación explícito.
## Hardware

La interfaz POS se comunica con una capa de dispositivos independiente. Los protocolos y controladores de impresoras, lectores, balanzas, cajones, pantallas y terminales se aíslan detrás de adaptadores. Se prioriza una pasarela local cuando sea necesaria para acceso USB, serie o red y para mantener la caja desacoplada de los servicios externos.

No se afirma compatibilidad por marca genérica: cada modelo, conexión y sistema operativo se registra en una matriz de pruebas físicas.

## Observabilidad

Logs estructurados, correlación por operación, métricas de latencia y sincronización, trazas de flujos, alertas de fallos fiscales y de pago, estado visible para operaciones pendientes, backups automáticos y pruebas de restauración.

## Decisiones y validaciones pendientes

- [x] Dirección de monolito modular y propiedad de datos por módulo.
- [x] Estrategia de reutilización compatible con uso interno privado, con control de licencias por componente.
- [x] Ronda integral de tres candidatos: MyCompany/lsFusion 6.2, Posnic 1.9.2 y ERPNext 16.60.0/Frappe 16.
- [x] Protocolo común de aceptación y datos sintéticos documentados.
- [ ] Instalar y ejecutar MyCompany/lsFusion 6.2 en entorno local aislado y probar un módulo custom.
- [ ] Instalar y ejecutar Posnic en entorno local aislado.
- [ ] Instalar y ejecutar ERPNext/Frappe en entorno local aislado.
- [ ] Completar P01–P19 del protocolo y registrar evidencia.
- [ ] Elegir una plataforma o aprobar el monolito modular propio.
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
