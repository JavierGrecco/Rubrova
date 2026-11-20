# Continuidad operativa, confiabilidad y recuperación

**Revisión:** 20 de noviembre de 2026  
**Estado:** especificación de arquitectura y aceptación. No representa una implementación ni una garantía de recuperación.

## 1. Objetivo y alcance de las pruebas

Rubrova debe recuperarse de fallos de software, cierre inesperado de aplicaciones, caída de un servicio, desconexiones, errores de sincronización, fallos de hardware y actualizaciones defectuosas.

**No es necesario ni se solicitará apagar físicamente el equipo, desenchufarlo ni provocar un corte eléctrico real.** La prueba de fallo abrupto consiste en terminar de forma controlada el proceso de Rubrova o de un servicio en puntos previamente definidos, reiniciar únicamente ese proceso y comprobar la recuperación. También se simulan timeouts, pérdida de red, respuestas demoradas, respuestas duplicadas, errores 5xx, caída/reinicio del broker y pérdida de conexión a la base.

La condición principal es: una operación confirmada no desaparece ni produce efectos duplicados. Si no llegó a confirmarse, la interfaz debe poder determinar su estado o dejarla claramente como incierta; nunca debe inventar que se completó.

La arquitectura objetivo son servicios de dominio independientes con datos y despliegues propios, conectados mediante APIs, eventos y un nodo local de sucursal. El diseño completo está en [Arquitectura modular distribuida](DISTRIBUTED_MODULAR_ARCHITECTURE.md).

## 2. Idempotencia en todos los caminos

La idempotencia es obligatoria para comandos HTTP, webhooks, eventos, importaciones, tareas programadas, operaciones de caja, pagos, inventario, fiscalidad y reintentos entre servicios.

Cada operación lógica lleva una clave estable desde el origen hasta todos sus reintentos. El servicio receptor registra esa clave con una restricción única en su propia base de datos, un hash de la solicitud y el resultado. La comprobación y el registro deben ser atómicos; no se acepta un patrón de consultar primero y registrar después porque dos ejecuciones simultáneas podrían pasar la comprobación.

Reglas:
- Misma clave + mismo contenido: devolver el resultado original sin repetir efectos.
- Misma clave + contenido diferente: responder conflicto, registrar la anomalía y no procesar.
- Claves diferentes: son operaciones diferentes; la idempotencia no las convierte en una sola.
- Eventos de proveedores: deduplicar por proveedor, cuenta y event_id estable.
- Webhook repetido: guardar evidencia del intento y responder correctamente sin repetir el cobro, movimiento o notificación.
- Entrega fuera de orden: validar versión/secuencia del agregado y conservar el payload original.
- Consumidor de eventos: debe ser idempotente aunque el broker o el proveedor ya tengan deduplicación.
- Efecto externo incierto: consultar la autoridad externa antes de iniciar una nueva operación.

No se promete exactly-once en el transporte. Se diseña entrega al menos una vez y un solo efecto de negocio mediante Outbox/Inbox durables, claves idempotentes, restricciones únicas y conciliación.

## 3. Servicios independientes y consistencia distribuida

Cada servicio mantiene su almacenamiento privado. La comunicación entre servicios usa contratos versionados; no se comparten tablas ni se hacen escrituras SQL cruzadas.

Una transacción local se confirma dentro del servicio dueño del dato. Cuando el proceso necesita completar acciones en varios servicios, se usa una Saga durable con pasos, reintentos y compensaciones explícitas. Ejemplo: pedido → reserva de inventario → intento de pago → confirmación de venta → movimiento de salida → documento fiscal.

Si un paso falla:
- reintentar sólo operaciones idempotentes y recuperables;
- liberar una reserva cuando todavía no existe una venta confirmada;
- consultar un pago incierto antes de volver a cobrar;
- conciliar un comprobante o una guía que pudo haberse creado;
- aplicar reembolso, nota de crédito o ajuste cuando la operación externa ya ocurrió.

Una Saga no borra la historia. Cada compensación es una operación de negocio auditable y también debe ser idempotente.

## 4. Stock, simultaneidad y operación offline

Idempotencia resuelve la repetición de una misma operación. **No resuelve la competencia entre dos ventas diferentes que intentan consumir la misma unidad.**

El servicio de Inventario mantiene un ledger append-only, reservas y una versión por artículo/ubicación. La venta solicita una reserva/consumo atómico. El servicio valida cantidad disponible y versión esperada mediante compare-and-swap (CAS). Si otra venta modificó primero el agregado, la segunda recibe conflicto, vuelve a leer y ofrece alternativa, menor cantidad, backorder o intervención.

### Varias cajas conectadas en la sucursal

Un nodo local de sucursal aloja el servicio de Inventario y coordina las reservas para las cajas conectadas por LAN. Los puestos no editan saldos locales independientes.

### Una caja aislada del nodo local

Sólo se permiten dos políticas explícitas:
1. Cuotas exclusivas preasignadas por el nodo local antes de perder conexión. Cada terminal puede consumir únicamente su cuota, que no se comparte con las demás.
2. Contingencia con venta local pendiente de conciliación y aviso visible de que el stock no está confirmado. Se pueden bloquear artículos de alto valor, escasos o sujetos a control.

Sin comunicación y sin cuotas exclusivas, dos cajas no conocen los movimientos mutuos. No existe una clave idempotente capaz de garantizar que ambas no vendan la misma última unidad. No se aplicará “última escritura gana” a inventario, caja, pagos o impuestos.

### Varias sucursales

Cada sucursal conserva su ledger local. El stock centralizado es una proyección con marca de última sincronización, no una disponibilidad garantizada durante una partición. Los traslados recorren estados explícitos: solicitado, reservado, despachado, en tránsito, recibido y conciliado.

## 5. Backups y catálogo de puntos de recuperación

Los backups deben ser automáticos, verificables, cifrados y estar registrados como recursos administrables. Deben cubrir las bases de cada servicio, archivos/documentos, configuración necesaria, el estado durable de mensajería y los datos que permiten correlacionar operaciones.

Cada backup tendrá un registro de catálogo con:
- ID único del backup y fecha/hora UTC;
- servicio, instancia, organización/ámbito y almacenamiento cubierto;
- versión de la aplicación, imagen/build y versión de esquema;
- tipo: completo, incremental, snapshot o punto-en-tiempo;
- rango de WAL/logs/eventos cuando aplique;
- manifiesto de servicios y offsets del broker para recuperar un punto coherente entre servicios;
- tamaño, checksum, cifrado y referencia a la clave (nunca la clave en el catálogo);
- ubicación, copia secundaria, política de retención y fecha de expiración;
- estado: solicitado, ejecutando, correcto, fallido, verificado o restauración probada;
- último test de restauración, resultado y duración;
- persona/proceso que lo generó y correlación de la operación.

La política incluirá copias automáticas, una segunda copia en otro medio y una copia fuera del equipo principal cuando la política de privacidad y operación lo permita. Los secretos y certificados se respaldan aparte, cifrados y con control de acceso estricto. Nunca se incluyen en Git, logs o fixtures.

Cada backup verifica su checksum y consistencia. La restauración completa se ensaya periódicamente en un entorno aislado y después de cambios importantes de plataforma o esquema. Un backup que nunca fue restaurado no se considera probado.

### Restauración y rollback de datos

No se sobrescribe directamente la única base activa. La recuperación recomendada es:
1. Elegir el punto de recuperación desde el catálogo, con fecha, servicio, versión y cobertura visibles.
2. Restaurar a una instancia/directorio separado, conservando intactos el estado actual y los backups.
3. Validar checksum, esquema, conteos, saldos, ledger, relaciones y manifiesto de eventos/offsets entre servicios.
4. Conciliar las operaciones confirmadas después del punto elegido; reproducir eventos legítimos sólo con claves idempotentes o generar compensaciones cuando corresponda.
5. Probar flujos críticos en la instancia restaurada y mostrar el impacto esperado.
6. Autorizar el cambio de destino/cutover y conservar el punto anterior hasta cerrar la verificación.

Las plataformas administradas suelen restaurar a una nueva instancia para evitar sobreescribir la original; Rubrova seguirá el mismo principio, adaptado a la tecnología local que finalmente se elija.

Un restore a un punto anterior puede borrar del estado reconstruido ventas legítimas posteriores. Por eso no se ofrece como un botón de “deshacer todo” sin conciliación. El sistema debe mostrar qué operaciones entran en la ventana de recuperación.

## 6. Rollback de código, releases y migraciones

Git y los backups resuelven problemas diferentes.

### Código fuente y versiones

- Cada release estable registra commit, tag, artefacto inmutable, versión de cada servicio, digest, SBOM, dependencias y migraciones compatibles.
- Si un cambio ya llegó a main, se revierte mediante un commit de corrección o git revert, que registra un nuevo commit inverso y conserva la historia.
- No se utiliza git reset --hard ni force-push para borrar commits compartidos de main. reset puede servir para trabajo local aún no publicado, pero no es el mecanismo de rollback de una historia compartida.
- Mantener el último artefacto estable de cada servicio permite volver a desplegar sólo el servicio afectado.
- Usar feature flags para desactivar una capacidad problemática sin retirar todo el release.
- En servicios críticos, desplegar una nueva versión en paralelo, ejecutar smoke/contract tests y desplazar el tráfico gradualmente o mediante blue-green. Mantener la versión anterior disponible hasta completar la validación.

Git revert no restaura una base de datos, un pago, un comprobante fiscal ni un envío. Sólo revierte cambios de código/configuración incluidos en el commit.

Fuentes:
- https://git-scm.com/docs/git-revert
- https://git-scm.com/docs/git-reset
- https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/safe-deployments

### Migraciones compatibles

Cada servicio versiona su esquema de forma independiente. Para reducir el riesgo:
1. Agregar columnas/tablas/campos de manera compatible.
2. Desplegar código que pueda leer el esquema anterior y el nuevo.
3. Migrar datos con lotes controlados y métricas.
4. Cambiar lecturas/escrituras a la nueva estructura.
5. Retirar compatibilidad antigua sólo cuando no queden instancias anteriores.

Este patrón expand-contract evita que un rollback de código encuentre una base incompatible. Si una migración destructiva ya ocurrió, no se improvisa una migración inversa: se restaura una copia verificada o se hace una corrección forward con datos conciliados.

### Efectos externos irreversibles

Restaurar una base no cancela un cobro aprobado, una factura autorizada por ARCA, un envío aceptado o una notificación recibida. Esos casos se resuelven con consultas y operaciones compensatorias válidas en el proveedor correspondiente.

## 7. Actualizaciones y cambios de esquema

- Fijar versiones y hashes de cada release y dependencia de producción.
- Generar un punto de recuperación antes de migraciones.
- Probar la actualización y rollback en una copia restaurada.
- Mantener compatibilidad entre versiones de API durante el despliegue gradual.
- Migrar cada servicio independientemente.
- Verificar qué eventos se publicaron y procesaron durante la ventana.
- No eliminar la versión anterior ni los backups hasta cerrar la validación.

## 8. Observabilidad operativa

El panel debe explicar en lenguaje claro:
- estado, versión y salud de cada servicio;
- gateway y broker local;
- última copia correcta, integridad y última restauración probada;
- espacio disponible;
- operaciones Outbox/Inbox pendientes y su antigüedad;
- webhooks duplicados y eventos fuera de orden;
- claves idempotentes en curso o con resultado incierto;
- conflictos CAS, reservas vencidas y conciliaciones de stock;
- Sagas en curso y compensaciones pendientes;
- pagos que requieren consulta;
- comprobantes fiscales pendientes;
- pedidos externos no conciliados;
- envíos sin guía o tracking atrasado.

Cada error incluye fecha, servicio, operación de referencia, impacto, acción siguiente y si se puede reintentar sin riesgo. Logs y trazas se correlacionan de extremo a extremo, sin tokens, contraseñas, certificados ni datos completos de tarjetas.

## 9. Seguridad y trazabilidad

- Roles y permisos comprobados en el servicio dueño del dato.
- Autenticación servicio-a-servicio y credenciales rotables.
- Separación de funciones para descuentos, anulaciones, ajustes de stock, cierre de caja y aprobación de lotes.
- Auditoría append-only de acciones relevantes: actor, fecha, dispositivo, motivo, objeto, valores previos/nuevos y correlación.
- Correcciones monetarias e inventario mediante reversión o movimiento compensatorio.
- Aislamiento por organización, sucursal y ubicación.
- Análisis de dependencias, secretos y vulnerabilidades en CI; SBOM y licencias versionadas.

## 10. Pruebas de aceptación adicionales

Estas pruebas amplían P01–P26; no reemplazan el protocolo existente.

| ID | Escenario | Resultado exigido |
|---|---|---|
| P27 | Terminar abruptamente el proceso POS o un servicio en puntos controlados durante una venta, sin apagar físicamente el equipo | Recuperar el último estado confirmado o identificar la operación como no confirmada/incierta; sin perder ni duplicar efectos |
| P28 | Perder la respuesta de una terminal después de que el pago pudo aprobarse | Consultar la misma operación antes de iniciar otro cobro |
| P29 | Recibir dos veces el mismo webhook, incluso en paralelo y fuera de orden | Una sola aplicación del evento; payload e intentos conservados |
| P30 | Restaurar el manifiesto completo de servicios en un equipo/entorno limpio | Aplicación operativa y saldos/ledgers conciliados |
| P31 | Fallar una migración intermedia y volver al release anterior | Compatibilidad, restore o corrección forward sin corrupción |
| P32 | Dos cajas intentan vender simultáneamente la última unidad con conexión al nodo local | CAS/reserva permite un solo consumo; la otra recibe conflicto y opciones |
| P33 | Caída de ARCA, ERP o carrier | Operación local conserva su estado; Outbox y conciliación recuperan el proceso |
| P34 | Disco casi lleno, backup fallido o secreto expirado | Alerta antes del impacto y contingencia segura |
| P35 | Reejecutar un lote de importación/exportación | No duplicar registros, asientos, comprobantes ni movimientos |
| P36 | Intentar acceder a datos de otra sucursal u organización | Denegación en el servicio dueño del dato y auditoría |
| P37 | Enviar simultáneamente el mismo comando con la misma clave idempotente | Una sola ejecución; las demás reciben el resultado registrado |
| P38 | Reutilizar la misma clave idempotente con un contenido distinto | Conflicto auditable; ningún segundo efecto |
| P39 | Recibir el mismo event_id en dos consumidores concurrentes | Una sola aplicación de negocio protegida por restricción única |
| P40 | Actualizar stock con expected_version obsoleto | Rechazo CAS, lectura nueva y resolución explícita; sin sobrescritura |
| P41 | Aislar una caja del servicio local de Inventario | Sólo consume cuota exclusiva o registra venta pendiente según política; no afirma stock global confirmado |
| P42 | Desplegar versión nueva de un servicio y provocar un error de salud | Retorno a la versión estable de ese servicio sin reescribir main ni actualizar innecesariamente los demás |
| P43 | Caída del broker después del commit del servicio emisor pero antes de publicar | Outbox conserva el evento y lo publica una vez recuperado; consumidores idempotentes |
| P44 | Fallar un paso intermedio de una Saga de checkout | Reintentos/compensaciones idempotentes y estado final conciliable |

## 11. Indicadores de confiabilidad

- Cantidad y antigüedad de comandos/eventos pendientes.
- Operaciones inciertas sin conciliar.
- Duplicados detectados por proveedor/servicio.
- Tasa de conflictos CAS y reservas vencidas.
- Tiempo de recuperación de un servicio o integración.
- Último backup correcto, último checksum verificado y antigüedad de la última restauración probada.
- Desvíos entre stock físico, reservado y disponible.
- Duración y tasa de fallos de sincronización.
- Rollbacks de servicio y migraciones fallidas.
- Tiempo medido de restauración (RTO) y punto de datos recuperable (RPO).

## 12. Fuentes técnicas de referencia

- Git: [git revert](https://git-scm.com/docs/git-revert) y [git reset](https://git-scm.com/docs/git-reset), para distinguir reversión con historial de reescritura de estado local.
- AWS RDS: [recuperación a un punto en el tiempo](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_PIT.html).
- Google Cloud SQL: [restauración y point-in-time recovery](https://cloud.google.com/sql/docs/postgres/backup-recovery/restore).
- Microsoft: [Idempotent Consumer](https://learn.microsoft.com/en-us/azure/architecture/patterns/idempotent-consumer), [Saga](https://learn.microsoft.com/en-us/azure/architecture/patterns/saga), [Outbox](https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/transactional-outbox-pattern) y [safe deployments](https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/safe-deployments).
- Shopify: [inventoryAdjustQuantities](https://shopify.dev/docs/api/admin-graphql/latest/mutations/inventoryAdjustQuantities) e [inventorySetQuantities con compare-and-swap](https://shopify.dev/docs/api/admin-graphql/latest/mutations/inventorySetQuantities).

## 13. Criterio de salida

La continuidad está aprobada sólo cuando se demuestra con pruebas repetibles que:
1. las operaciones confirmadas sobreviven a la terminación y reinicio del proceso;
2. los reintentos no duplican efectos;
3. una clave repetida con otro contenido se rechaza;
4. dos ventas concurrentes no consumen la misma unidad sin autorización;
5. los estados inciertos son identificables y conciliables;
6. los backups tienen registro, checksum y restauración probada;
7. cada servicio puede desplegarse o revertirse sin actualización global innecesaria;
8. los efectos externos se compensan correctamente, no se borran localmente;
9. la falta de conexión no oculta tareas o comprobantes pendientes;
10. el operador sabe qué está funcionando, qué está degradado y qué requiere intervención.

La meta es que Rubrova pueda continuar operando, aislar un fallo, recuperar el servicio afectado y conservar evidencia de cada acción. La recuperación no debe depender de borrar historia ni de que el usuario manipule bases de datos manualmente.
