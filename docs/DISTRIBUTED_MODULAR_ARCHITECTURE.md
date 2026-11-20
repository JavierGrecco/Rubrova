# Arquitectura modular distribuida

**Revisión:** 20 de noviembre de 2026  
**Estado:** decisión de arquitectura objetivo y reglas obligatorias para la evaluación. No implica que los servicios estén implementados ni desplegados.

## 1. Decisión de arquitectura

Rubrova se diseñará como una **plataforma de servicios de dominio independientes**, no como un monolito. Cada servicio tendrá responsabilidad acotada, datos propios, contrato público, ciclo de pruebas, despliegue, versionado y rollback independientes.

Los servicios podrán ejecutarse juntos en un mismo equipo local cuando la instalación sea pequeña, pero seguirán siendo procesos o unidades de despliegue separados. Compartir hardware no significa compartir código interno, tablas, credenciales ni ciclo de vida.

La arquitectura combinará:
- servicios independientes, alineados con capacidades del negocio;
- un gateway local de APIs para aplicaciones y dispositivos;
- comunicación síncrona para operaciones que necesitan respuesta inmediata;
- mensajería durable y eventos para procesos asíncronos;
- un nodo de operación local por sucursal para mantener caja e inventario disponibles sin depender de Internet;
- integraciones externas aisladas en adaptadores reemplazables;
- observabilidad, seguridad y gestión de versiones comunes.

No adoptaremos Kubernetes, Kafka ni una malla de servicios por anticipado. La independencia de los servicios es una decisión de diseño; la infraestructura se elige después de medir el despliegue real. Para una instalación local privada, una plataforma de procesos o contenedores más sencilla puede ser más confiable y fácil de mantener que un clúster sobredimensionado.

## 1.1 Reutilización primero sin perder independencia

La preferencia por servicios independientes no obliga a desarrollar todo desde cero. Cada nuevo servicio debe partir de una búsqueda de código disponible y una prueba de reutilización. Pero no cualquier aplicación modular satisface el objetivo de arquitectura.

Para adoptar una aplicación existente como servicio Rubrova, debe demostrar: límite de dominio acotado y dueño único de sus datos; persistencia/credenciales aislables; API/eventos públicos y versionados; ciclo propio de despliegue, migración, backup, restauración y rollback; actualización independiente; y pruebas de permisos, concurrencia, idempotencia y recuperación.

**Los módulos dentro de un mismo ERP no se convierten automáticamente en servicios independientes.** Si comparten runtime, base y migraciones, se evalúa el producto como aplicación integrada. Sólo se puede aceptar completo si sus responsabilidades forman un límite de dominio deliberado y no absorben datos que la arquitectura asigna a otros servicios. De lo contrario, se reutilizan módulos o bibliotecas separables y el resto queda como referencia técnica.

Ver [Estrategia reuse-first](REUSE_FIRST_IMPLEMENTATION_STRATEGY.md) y [Shortlist de componentes reutilizables](REUSE_COMPONENTS_SHORTLIST.md).

## 2. Qué aprendemos de las empresas y plataformas líderes

Las fuentes públicas no revelan todos los sistemas internos de estas empresas. Tomamos sus guías y casos documentados como evidencia técnica puntual, sin asumir que Rubrova deba copiar su infraestructura completa.

### Apple

- Apple recomienda modularizar código en paquetes reutilizables, separar networking/utilidades y controlar qué interfaces se exponen. Los paquetes permiten tests y dependencias explícitas. Esto respalda módulos con contratos pequeños, no un conjunto de carpetas que acceden libremente a cualquier cosa.
- Swift Concurrency usa actores para aislar estado mutable y evitar data races; es una referencia útil para nuestros procesos concurrentes: cada agregado crítico debe tener un mecanismo explícito de serialización o control de concurrencia.
- Las Human Interface Guidelines priorizan feedback claro y recuperación sencilla de errores. En Rubrova, la aplicación debe explicar qué se confirmó, qué está pendiente y cómo corregirlo, sin trasladar complejidad interna al operador.

Fuentes:
- https://developer.apple.com/documentation/xcode/organizing-your-code-with-local-packages
- https://developer.apple.com/documentation/swift/concurrency
- https://developer.apple.com/design/human-interface-guidelines/feedback
- https://developer.apple.com/design/human-interface-guidelines/design-principles

### Samsung

Samsung documentó que Samsung Account evolucionó a una arquitectura de más de 70 microservicios. Para actualizar EKS sin interrumpir el servicio utilizó dos clústeres: el existente continuaba atendiendo tráfico mientras el nuevo validaba compatibilidad; después se podía cambiar el tráfico y volver al anterior si surgían problemas.

La lección para Rubrova no es operar dos clústeres enormes, sino desplegar versiones nuevas en paralelo, probar compatibilidad y mantener una ruta de retorno al último release estable.

One UI también publica principios útiles para la experiencia: foco en la tarea, interacción natural, legibilidad y adaptación al dispositivo. Son criterios de interfaz, no una especificación de arquitectura de backend.

Fuentes:
- https://developer.samsung.com/sdp/blog/en/2024/08/23/the-secret-behind-non-disruptive-cloud-infrastructure-upgrade
- https://developer.samsung.com/one-ui/index.html

### Xiaomi

Xiaomi publicó openvela, una plataforma modular para AIoT con capas de kernel y servicios, mecanismos IPC y RPC para comunicar componentes y sistemas diferentes, además de herramientas de diagnóstico y emulación. Su integración abierta de Xiaomi Home también documenta mensajería publish/subscribe mediante MQTT y operación local a través de un hub, además del camino cloud.

La lección útil es separar capacidades y usar contratos de comunicación entre procesos, con un modo local que no depende de consultar continuamente la nube. No asumimos que la arquitectura de un sistema operativo IoT sea directamente equivalente a un ERP.

Fuentes:
- https://doc.openvela.com/document?id=198&language=en&version=trunk
- https://github.com/open-vela/docs
- https://github.com/Xiaomi/ha_xiaomi_home

### Google, Microsoft y AWS

- Google Android recomienda modularización con alta cohesión y bajo acoplamiento, interfaces pequeñas y límites de responsabilidad. Advierte contra módulos demasiado pequeños, cuyo costo de coordinación supera el beneficio.
- Microsoft recomienda servicios por dominios, almacenamiento privado por servicio, APIs de negocio, mensajería asíncrona, observabilidad y evitar compartir esquemas de base de datos. También documenta idempotencia, transactional outbox, sagas y compensaciones.
- AWS explica que las operaciones con efectos secundarios no son seguras para reintentar salvo que tengan un contrato idempotente explícito.

Fuentes:
- https://developer.android.com/topic/modularization
- https://learn.microsoft.com/en-us/azure/architecture/guide/architecture-styles/microservices
- https://learn.microsoft.com/en-us/azure/architecture/patterns/saga
- https://learn.microsoft.com/en-us/azure/architecture/patterns/idempotent-consumer
- https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/transactional-outbox-pattern
- https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/

## 3. Límites de dominio y servicios objetivo

Los límites se definen por reglas y propiedad del dato, no por la cantidad de tablas o pantallas.

| Servicio | Autoridad y responsabilidad |
|---|---|
| Identidad y organización | Usuarios, permisos, entidades legales, sucursales, dispositivos y políticas |
| Catálogo y precios | Artículos, variantes, unidades, listas, reglas de precio y vigencias |
| Clientes y proveedores | Maestros, direcciones, condiciones comerciales y cuentas externas |
| Pedidos y ventas | Cotización, pedido, carrito confirmado, venta, devolución y estado comercial |
| Inventario y almacenes | Libro de movimientos, reservas, disponibilidad, ubicaciones, lotes y conteos |
| Pagos y caja | Intentos de cobro, resultados, medios, turnos, arqueos, reembolsos y liquidaciones |
| Compras y abastecimiento | Proveedores, órdenes, recepciones, costos de compra y reposición |
| Fiscal | Comprobantes, autorización ARCA, notas de crédito/débito y estados inciertos |
| Logística y fulfillment | Preparación, bultos, guías, transportistas, reparto y tracking |
| Producción y servicios | Recetas/BOM, órdenes de producción, contratos, SLA y órdenes de trabajo |
| Integraciones | Adaptadores, webhooks, import/export y bandejas Inbox/Outbox |
| Inteligencia | Modelos de lectura, métricas y pronósticos; nunca escribe ledgers operativos |
| Documentos | Archivos originales, OCR, versiones derivadas y evidencias |
| Plataforma y operaciones | Gateway, configuración, mensajería, backups, telemetría y despliegues |

El primer corte de implementación debe comenzar por identidad/organización, catálogo/precios, ventas/checkout, inventario y pagos/caja. Los restantes servicios se habilitan según el flujo completo que se esté construyendo.

## 4. Comunicación entre servicios

### Síncrona

Usar HTTP/JSON con APIs versionadas como contrato público inicial. gRPC puede evaluarse para comunicaciones internas de alto volumen o contratos tipados donde el beneficio sea medible. Los clientes no deben invocar directamente todos los servicios: usan un gateway local que aplica autenticación, autorización, rate limits, correlación y routing.

### Asíncrona

Usar un broker durable para eventos y trabajos que no necesitan bloquear la interacción del usuario. Cada servicio publica y consume eventos mediante Outbox/Inbox transaccionales. La entrega se considera at least once: puede haber duplicados, por lo que cada consumidor debe ser idempotente.

El broker no reemplaza las bases propias. Si el broker se cae, el evento pendiente permanece en la Outbox del servicio emisor y se publica al recuperarse.

### Contratos

Cada contrato debe definir:
- nombre, propósito, propietario y versión;
- request/response o esquema del evento;
- autenticación, autorización y permisos;
- claves de idempotencia y semántica de reintento;
- errores tipados y códigos recuperables/no recuperables;
- timeout, límites, orden requerido y garantías;
- compatibilidad hacia atrás y política de deprecación;
- tests de contrato del proveedor y consumidor.

Los cambios deben ser compatibles durante la ventana en que conviven versiones. Primero se agregan campos/capacidades opcionales; se migra a los consumidores; sólo después se retiran los campos antiguos.

## 5. Propiedad y aislamiento de datos

Cada servicio escribe exclusivamente en su propio almacenamiento. Otros servicios consultan su API o consumen eventos; nunca leen sus tablas ni hacen SQL directo.

Para despliegues pequeños, dos servicios podrían compartir una instancia física de PostgreSQL, pero deben tener bases/esquemas, roles y credenciales separados, migraciones independientes y prohibición técnica de escrituras entre esquemas. La separación física se adopta cuando la carga, seguridad o recuperación lo requieran.

Cada dato tiene una única autoridad. Las vistas o proyecciones replicadas son de solo lectura y se actualizan por eventos. Las operaciones que necesitan consistencia inmediata se resuelven en el servicio dueño del agregado.

## 6. Idempotencia: contrato obligatorio

Idempotencia no es sólo una comprobación en memoria ni una opción del broker. Se aplica a comandos de API, webhooks, eventos, importaciones, trabajos programados, pagos, facturas, movimientos de stock y reintentos entre servicios.

### Clave de operación

Cada comando lógico recibe una idempotency_key estable, generada en el origen y conservada durante todos los reintentos. La clave se guarda con:
- organización, servicio y operación;
- identificador de origen/dispositivo;
- hash de la solicitud normalizada;
- estado in_progress, completed, failed_retryable o needs_reconciliation;
- respuesta/resultado original;
- fecha, correlación y vencimiento de retención.

Debe existir una restricción única en almacenamiento para impedir que dos consumidores reclamen la misma operación simultáneamente. La comprobación y el registro se hacen atómicamente, no mediante un SELECT seguido por un INSERT separado.

Si llega la misma clave y el mismo contenido, se devuelve el resultado ya registrado. Si llega la misma clave con contenido diferente, se rechaza como conflicto y se audita; nunca se trata como una nueva operación.

### Webhooks y eventos repetidos

- Validar firma, cuenta/proveedor y estructura antes de procesar.
- Deduplicar por identidad estable del proveedor, normalmente provider + account_id + event_id.
- Persistir el payload original y su hash.
- Registrar la recepción en Inbox con restricción única.
- Procesar el efecto de negocio y marcar el evento como aplicado de forma transaccional cuando ambos pertenezcan al mismo almacenamiento.
- Si interviene otro servicio o efecto externo, registrar estado intermedio y propagar la misma clave lógica al siguiente servicio.
- Si el evento ya fue aplicado, devolver una respuesta de éxito al emisor sin repetir el efecto.
- Si llega fuera de orden, conservarlo y validar aggregate_version/secuencia antes de actualizar proyecciones.
- Si el proveedor no ofrece un ID estable, usar un fingerprint de negocio documentado como último recurso y enviar casos ambiguos a conciliación.

La deduplicación del broker por sí sola no alcanza: el consumidor debe proteger sus propios efectos y cualquier llamada posterior.

## 7. Stock y concurrencia: idempotencia más control de versión

Una clave idempotente detiene la repetición de la misma venta. No impide que dos ventas distintas, con claves diferentes, intenten consumir la última unidad. Para eso se necesita coordinación o control de concurrencia.

### Modelo de inventario

El servicio de Inventario mantiene un ledger append-only de movimientos y calcula, por artículo/ubicación:
- on_hand: cantidad física registrada;
- reserved: cantidad reservada para pedidos;
- available: cantidad disponible para vender;
- in_transit, damaged y quarantined: estados separados.

No se actualiza el saldo con sobrescrituras silenciosas. Una operación de venta solicita una reserva o consumo atómico al servicio propietario.

### Control optimista de concurrencia (CAS)

Cada agregado de stock mantiene version. Una operación envía cantidad, ubicación y expected_version o expected_available. El servicio confirma sólo si la versión/saldo todavía coincide y la cantidad disponible alcanza. El cambio de saldo, movimiento de ledger, reserva y registro idempotente se guardan en una transacción local.

Si otra venta cambió primero el stock, la segunda recibe un conflicto de concurrencia; vuelve a leer, recalcula y ofrece alternativas: menor cantidad, otro depósito, backorder o intervención. No se descarta el cambio ni se impone “último cambio gana”.

Este enfoque coincide con la estrategia pública de Shopify: ajustes incrementales con ID idempotente y cambios de cantidad absoluta protegidos mediante compare-and-swap. La propia documentación advierte que omitir el control puede producir cantidades inexactas.

Fuentes:
- https://shopify.dev/docs/api/admin-graphql/latest/mutations/inventoryAdjustQuantities
- https://shopify.dev/docs/api/admin-graphql/latest/mutations/inventorySetQuantities
- https://learn.microsoft.com/en-us/azure/architecture/guide/design-principles/minimize-coordination

### Operación local en una sucursal

Para varias cajas conectadas a la misma sucursal, un servicio local de Inventario/Edge es el coordinador y autoridad de las reservas. Las cajas envían comandos; no editan sus propias copias del saldo.

Si un puesto pierde la conexión con ese coordinador, no puede afirmar que el último artículo sigue disponible. Para permitir venta offline sin conexión entre cajas existen dos políticas válidas:

1. **Cuotas preasignadas:** mientras están conectadas, el coordinador entrega a cada caja una reserva exclusiva y limitada de cantidades/identificadores. Cada cuota sólo puede gastarse una vez. Evita competencia sobre la misma unidad a costa de inmovilizar stock en terminales.
2. **Modo de contingencia:** se permite registrar una venta local con estado pending_inventory_reconciliation y se advierte que el stock no está confirmado. La política puede bloquear artículos escasos, de alto valor o regulados. Al reconectar, el servicio concilia y genera una incidencia si hubo sobreventa.

No hay una técnica de idempotencia que permita que dos equipos aislados consuman con certeza la misma última unidad. Si no pueden comunicarse ni tienen cuotas exclusivas, no conocen los movimientos del otro. Debe elegirse explícitamente entre disponibilidad, reserva previa o posible sobreventa controlada.

### Varias sucursales

Cada sucursal conserva su propio ledger local. La disponibilidad de otra sucursal es una proyección con fecha de sincronización, no una cantidad actual garantizada. Los traslados son operaciones con estados requested, reserved, dispatched, in_transit, received y reconciled; no se agregan simultáneamente al stock de origen y destino.

## 8. Operaciones que cruzan servicios: Sagas

No se intentará simular una transacción ACID que cubra varios servicios y proveedores externos. Los flujos largos usarán una Saga orquestada o coreografiada con estados durables, timeout, reintentos y acciones compensatorias idempotentes.

Ejemplo simplificado de checkout:
1. Ventas crea el pedido con ID y clave estables.
2. Inventario reserva las cantidades.
3. Pagos inicia el cobro o registra el medio elegido.
4. Ventas confirma la venta cuando se cumplen las condiciones.
5. Inventario convierte la reserva en movimiento de salida.
6. Fiscal solicita el comprobante según el estado fiscal permitido.
7. Si un paso falla, la Saga libera la reserva o compensa el efecto que corresponda.
8. Si un pago o comprobante quedó incierto, no ejecuta otro: consulta y concilia primero.

Una compensación no es borrar el pasado. Puede ser liberar una reserva, anular una autorización, emitir un reembolso, una nota de crédito o un movimiento de ajuste. Los efectos externos legalmente emitidos no se revierten por restaurar una base de datos.

## 9. Topología de despliegue

### Modo local

Un instalador configura un **nodo local de sucursal** con gateway, servicios de dominio, broker durable, almacenamiento, monitor y puente de hardware. Los puestos de caja se conectan por LAN. No se requiere Internet para los procesos locales críticos.

Los servicios se ejecutan como unidades independientes y se reinician sin tener que reiniciar todo el producto. Un servicio no disponible debe degradar sólo las capacidades que dependen de él; el estado se informa claramente.

### Administración central y varias sucursales

La central recibe eventos de cada nodo, mantiene vistas consolidadas y coordina datos maestros, reportes y procesos que requieren conexión. Los nodos locales siguen trabajando cuando el enlace WAN está caído, usando políticas de stock, precios y permisos previamente sincronizadas.

### Tecnologías de infraestructura

- API Gateway: evaluar Envoy, Traefik o gateway integrado según pruebas de Windows/macOS/Linux.
- Mensajería durable: comparar NATS JetStream y RabbitMQ en carga real, persistencia local, backup, operación y actualización.
- Observabilidad: OpenTelemetry para trazas, métricas y logs correlacionados.
- Contenedores/servicios: elegir el mecanismo más simple que permita versionar, aislar, iniciar y detener cada servicio en los tres sistemas operativos objetivo.
- Base de datos: seleccionar por servicio según el resultado de la evaluación de plataformas; no usar una base global compartida como interfaz entre ellos.

No se adopta ningún candidato de infraestructura hasta ejecutar pruebas locales y registrar versiones, consumo de recursos, recuperación y costo de mantenimiento.

## 10. Observabilidad y gobierno técnico

Cada interacción recibe correlation_id de extremo a extremo. Cada comando lleva idempotency_key; cada evento tiene event_id, aggregate_id y aggregate_version. Las trazas permiten reconstruir el camino desde el POS hasta stock, pago, fiscalidad y logística.

Panel técnico-operativo:
- servicio, versión y estado;
- latencia y errores por endpoint;
- cola Outbox/Inbox, edad y reintentos;
- eventos duplicados detectados;
- conflictos CAS y reservas vencidas;
- Sagas en curso o compensaciones pendientes;
- dependencias degradadas;
- última copia y última restauración validada.

Todos los servicios comparten estándares de logs, métricas, seguridad, contratos, versionado y despliegue. El número de lenguajes se mantiene reducido; la independencia no justifica diversidad tecnológica innecesaria.

## 11. Puertas de aceptación arquitectónica

Antes de aprobar un servicio:
- su base/namespace y credenciales están aislados;
- otro servicio no puede alterar sus datos;
- el contrato tiene versión y tests de consumidor/proveedor;
- requests repetidos y concurrentes producen un único efecto;
- se recupera de broker, red o dependencia caída;
- su despliegue y rollback no exigen actualizar todos los servicios;
- el esquema tolera al menos la versión anterior del consumidor durante la migración;
- las métricas/trazas permiten encontrar una operación;
- backup y restauración se prueban para su almacenamiento;
- los estados inciertos y compensaciones están documentados.

La arquitectura debe ser modular de verdad: un módulo que comparte tablas, despliegue inseparable o ciclos de vida con todos los demás es una dependencia acoplada, no un servicio independiente.
