# Continuidad operativa, confiabilidad y recuperación

**Revisión:** 19 de noviembre de 2026  
**Estado:** especificación de arquitectura y aceptación. No representa una implementación ni una garantía de recuperación.

## 1. Objetivo

Rubrova debe proteger los datos y permitir que la operación se recupere de errores humanos, fallos de software, cortes de energía, desconexiones, fallos de hardware, errores de sincronización y actualizaciones defectuosas.

La condición más importante es simple: una venta, cobro o movimiento confirmado no puede desaparecer ni aplicarse dos veces por una falla o un reintento.

## 2. Autoridad transaccional

- Mantener un monolito modular con límites y contratos internos claros.
- Cada dominio tiene una autoridad: ventas, pagos/caja, inventario, fiscalidad, compras, logística y contabilidad externa.
- Confirmar venta, líneas, asignaciones de pago y movimientos internos mediante transacciones coherentes del sistema elegido.
- Publicar eventos por Outbox transaccional; no hacer un commit comercial y luego confiar en que una tarea de interfaz envíe el evento.
- Consumir webhooks y mensajes mediante Inbox duradera, claves idempotentes, deduplicación y registro de payload original.
- Usar identificadores estables de origen, negocio, dispositivo y correlación.
- Los sistemas contables, fiscales, PSP y transportistas conservan su propia autoridad en sus dominios.

La sincronización no debe ejecutar el mismo efecto dos veces. Un lote puede llegar repetido; se conserva el intento y se detecta que su operación ya fue aplicada.

## 3. Topología local y trabajo sin Internet

### Primera etapa: una instalación local

El servidor y la base transaccional deben poder funcionar dentro de la red local y no depender de la conexión a un servicio cloud para registrar ventas, caja o movimientos internos. Los servicios externos se muestran como no disponibles cuando no se pueden alcanzar.

### Varias cajas en una sucursal

Preferir un servicio local de sucursal como autoridad coordinadora de inventario y caja. Los puestos se conectan a él por LAN. Si una terminal pierde comunicación con el nodo local, puede conservar una cola propia de operaciones pendientes, pero debe mostrar claramente el estado y aplicar una política de contingencia.

### Varias sucursales

Cada sucursal puede operar localmente y sincronizar con la administración central. Esto no equivale a mantener varias bases independientes que se fusionan libremente. La autoridad y las reglas de conflicto deben definirse por tipo de dato.

No utilizar "última escritura gana" para ventas, pagos, caja, impuestos o stock. Si varias cajas se desconectan simultáneamente, no pueden conocer las ventas ni reservas de las otras. Para reducir sobreventa, evaluar límites de disponibilidad offline por sucursal/caja, reservas asignadas o una política explícita de venta pendiente de conciliación.

### Restricciones reales

- No simular autorización de ARCA cuando no hubo respuesta.
- No marcar pago integrado como aprobado mientras el resultado sea incierto.
- Una venta offline puede quedar fiscalmente pendiente si el flujo y el tipo de operación lo permiten; se debe mostrar su estado y resolverlo al recuperar conexión.
- La disponibilidad de stock de otras sucursales no se considera actualizada mientras no llegue una sincronización confirmada.

## 4. Estados inciertos y recuperación de operaciones

Cada integración necesita un estado explícito, por ejemplo:
- pendiente de envío;
- enviada, sin confirmación;
- confirmada por el proveedor;
- rechazada;
- agotó reintentos;
- requiere conciliación manual;
- revertida mediante una operación compensatoria.

Caso crítico: una terminal de pago aprueba el cobro, pero la respuesta se pierde. Rubrova no debe iniciar automáticamente un segundo cobro. Primero consulta la operación original mediante su ID o clave externa; si el proveedor no permite resolverla, se deriva a conciliación.

El mismo principio aplica a:
- emisión fiscal luego de timeout;
- alta de guía de transporte;
- importación de pedidos;
- creación de asientos;
- envío de facturas al ERP;
- cancelaciones y devoluciones.

Los reintentos deben tener backoff, límites, jitter cuando corresponda y circuito de interrupción ante fallos repetidos. Las colas de mensajes no procesables deben conservar la causa y permitir replay autorizado.

## 5. Backups y restauración

La política final depende de la plataforma elegida, pero debe incluir:

- Backup automático y cifrado de la base, archivos y documentos.
- Copia local y copia en un medio distinto; al menos una copia fuera del equipo principal.
- Retención diaria/semanal/mensual, con limpieza automática que no borre la última copia válida.
- Registro del resultado de cada backup y alerta cuando falta o está corrupto.
- Exportación/backup consistente de archivos adjuntos, imágenes, etiquetas, documentos y configuración.
- Copia separada y cifrada de secretos/certificados; nunca colocar claves privadas en repositorios, logs o fixtures.
- Prueba de restauración en un entorno aislado, con versión compatible.
- Verificación de integridad, recuento, montos y operación luego de restaurar.

Un backup que nunca se restauró no está demostrado. La aceptación exige restaurar una copia, abrir Rubrova y conciliar operaciones de referencia.

### Objetivos de recuperación

Definir RPO (cuánto dato se puede perder como máximo) y RTO (cuánto se puede tardar en volver a operar) según la actividad y el costo de respaldo. Se deben medir en pruebas; no presentar un objetivo teórico como una garantía.

## 6. Actualizaciones y cambios de esquema

- Fijar versiones y hashes de cada release y dependencia de producción.
- Generar backup automático antes de migraciones.
- Ejecutar migraciones sobre una copia y comprobar tiempo, integridad y compatibilidad.
- Usar migraciones versionadas, repetibles de forma segura y con reporte.
- No intentar "deshacer" una migración de base compleja con SQL inverso improvisado; ante una actualización fallida, restaurar backup verificado o aplicar una corrección forward controlada.
- Mantener un plan de recuperación de versión y verificar qué datos se escribieron durante la ventana.
- Nunca actualizar simultáneamente todos los puestos si el cliente y el servidor requieren compatibilidad de versiones.

## 7. Observabilidad operativa

El panel de salud debe explicar, en lenguaje claro:

- estado local del servidor y base de datos;
- última copia correcta y última restauración ensayada;
- espacio disponible;
- integraciones conectadas, degradadas o sin credenciales;
- operaciones pendientes de sincronizar;
- operaciones dudosas y conciliaciones requeridas;
- eventos rechazados y próximos reintentos;
- comprobantes fiscales pendientes;
- pagos cuya autorización necesita consulta;
- pedidos externos sin importar o conciliar;
- envíos sin guía o tracking atrasado.

Cada error debe incluir fecha, módulo, operación de referencia, impacto, siguiente acción y si se puede reintentar sin riesgo.

Los logs deben estar estructurados y correlacionados, pero no deben incluir certificados, tokens, contraseñas, datos completos de tarjetas ni información personal innecesaria.

## 8. Seguridad y trazabilidad

- Roles y permisos comprobados en servidor para toda operación sensible.
- Separación de funciones para descuentos, anulaciones, ajustes de stock, cierre de caja y aprobación de lotes contables.
- Auditoría append-only de acciones relevantes: actor, fecha, dispositivo, motivo, objeto, valores anteriores/nuevos y correlación.
- Correcciones monetarias e inventario mediante reversión o movimiento compensatorio.
- Sesiones, secretos, backups y archivos protegidos.
- Aislamiento verificable por organización, sucursal y ubicación.
- Análisis de dependencias, secretos y vulnerabilidades en CI; SBOM y licencias versionadas.

## 9. Pruebas de aceptación adicionales

Estas pruebas amplían P01–P26; no reemplazan el protocolo existente.

| ID | Escenario | Resultado exigido |
|---|---|---|
| P27 | Cortar energía o matar el proceso antes, durante y después de confirmar una venta | Recuperar exactamente el estado confirmado o indicar que no se confirmó; sin duplicados |
| P28 | Perder respuesta de una terminal después de que el pago pudo aprobarse | Consultar la misma operación antes de crear otra |
| P29 | Recibir dos veces el mismo webhook, fuera de orden | Un único efecto; historial original conservado |
| P30 | Restaurar una copia en un equipo limpio | Aplicación operativa y totales de referencia conciliados |
| P31 | Migración de versión con fallo intermedio | Restaurar o corregir con procedimiento documentado, sin corrupción |
| P32 | Dos cajas offline con ventas simultáneas del último artículo | Conflicto explícito; sin "última escritura gana" ni pérdida de historia |
| P33 | Caída de ARCA, ERP o carrier | La operación local conserva su estado y la cola permite recuperación segura |
| P34 | Disco casi lleno, backup fallido o secreto expirado | Alerta previa al impacto y bloqueo/contingencia segura donde corresponda |
| P35 | Reejecutar un lote de importación/exportación | No duplicar registros, asientos, comprobantes ni movimientos |
| P36 | Intentar acceder a datos de otra sucursal u organización | Denegación en servidor y evento de auditoría |

## 10. Indicadores de confiabilidad

- Cantidad y antigüedad de operaciones pendientes.
- Operaciones inciertas sin conciliar.
- Ventas sin comprobante cuando corresponde.
- Pagos sin aplicar y liquidaciones con diferencias.
- Eventos externos duplicados detectados.
- Tiempo de recuperación de una integración.
- Último backup correcto y antigüedad de la última restauración probada.
- Diferencias entre stock contable y conteo físico.
- Duración y tasa de fallos de sincronización.
- Cambios de versión fallidos y tiempo de recuperación.

## 11. Criterio de salida

La continuidad está aprobada sólo cuando se demuestra con pruebas repetibles que:
1. las operaciones confirmadas sobreviven a cierre y reinicio;
2. los reintentos no duplican efectos;
3. los estados inciertos son identificables y conciliables;
4. el backup puede restaurarse;
5. una actualización fallida tiene un procedimiento de recuperación;
6. la falta de conexión no oculta tareas o comprobantes pendientes;
7. el usuario sabe qué está funcionando, qué está degradado y qué requiere intervención.

El diseño sigue siendo un monolito modular con una única autoridad por dominio. No se agrega una cola, motor de workflow o servicio distribuido sólo por moda: primero se mide la necesidad y se demuestra su beneficio.
