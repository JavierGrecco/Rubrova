# Copias de seguridad y recuperación de Rubrova

**Revisión:** 20 de noviembre de 2026  
**Estado:** requisito de producto y diseño de recuperación. No representa una función implementada ni una copia de seguridad actualmente operativa.

## 1. Objetivo para el negocio

El dueño debe poder recuperar Rubrova sin depender de la computadora original. Si Windows se reinstala, el disco falla o se reemplaza el equipo, debe ser posible instalar Rubrova en otra PC, seleccionar una copia, ingresar la clave de recuperación y continuar con el negocio conservando sus operaciones e historial.

No alcanza con copiar una carpeta de instalación ni con guardar solamente la base de datos. El respaldo debe permitir recuperar la información de negocio, los documentos y la configuración necesaria para volver a operar.

La recuperación debe poder realizarla una persona autorizada desde una interfaz guiada, sin abrir una consola, editar bases de datos ni reconstruir carpetas manualmente.

## 2. Dos tipos de respaldo complementarios

### 2.1 Copia de recuperación completa

Paquete portable de Rubrova, con formato identificable (propuesta: .rubrova-backup), cifrado y verificable. Incluye los datos necesarios para reconstruir el estado en una instalación compatible, sin depender de la ruta original ni del disco anterior.

Debe contener:
- manifiesto con organización, sucursales, áreas, fecha de corte, zona horaria, moneda, versión de Rubrova, versiones de módulos, versiones de esquema y requisitos mínimos;
- datos de catálogo, clientes, proveedores, marcas, categorías, listas y vigencias;
- ventas, líneas, pedidos, devoluciones, pagos, caja, compras, recepciones, movimientos y reservas de inventario;
- costos históricos y de reposición, valuación, cuentas corrientes, gastos, asientos y conciliaciones;
- documentos fiscales y comerciales, facturas/remitos de compra, adjuntos, imágenes, contratos y archivos del negocio;
- auditoría, referencias externas, claves idempotentes, correlation IDs y estados pendientes;
- eventos/outbox/inbox, cursores de sincronización y posiciones necesarias para reconstrucción coherente;
- configuración funcional, plantillas, reglas, perfiles por sucursal y configuración de periféricos, sin secretos en texto claro;
- checksums por componente, checksum del manifiesto y resultado de consistencia.

El paquete puede incorporar también un snapshot nativo del motor de base de datos para acelerar una restauración exacta. Ese snapshot es un acelerador, no el único formato disponible: los datos propios deben poder exportarse a un formato lógico documentado para no quedar atados a un motor o proveedor.

### 2.2 Copia incremental y recuperación a un punto

El mecanismo nativo de la base elegida debe aprovechar journal/WAL, logs transaccionales, snapshots incrementales o la función equivalente que realmente soporte. Debe permitir recuperar una secuencia coherente de operaciones hasta un corte conocido, no una mezcla de archivos copiados mientras cambian.

Cada copia registra:
- ID, fecha y hora UTC, punto de corte y rango de transacciones/logs;
- versión de aplicación, esquema y formato;
- componentes y servicios incluidos;
- checksum, tamaño, cifrado y clave de recuperación referenciada;
- ubicación, retención, estado de verificación y última restauración probada.

La captura establece una barrera consistente: el corte del ledger, los archivos, los eventos y los offsets deben corresponder al mismo estado. Si un componente no pudo incluirse, el respaldo se marca incompleto y no se ofrece como una copia válida de recuperación total.

## 3. Frecuencia, destinos y retención

La configuración será visible y editable. La política inicial a probar es:

- proteger cada operación confirmada en el registro durable del motor transaccional;
- mantener puntos locales incrementales según la capacidad del motor y del disco;
- cuando el usuario configure un NAS o destino remoto cifrado siempre disponible, enviar puntos incrementales con una meta inicial de hasta 15 minutos entre puntos recuperables fuera del equipo;
- sin NAS ni destino remoto, generar copia diaria en un disco externo y mostrar que el RPO real queda limitado a la última copia completada; recomendar rotar dos discos externos y desconectarlos tras cada respaldo;
- generar una copia completa diaria cuando haya destino disponible;
- conservar puntos horarios recientes y copias diarias durante 30 días;
- conservar 12 cierres mensuales, sujeto al espacio disponible;
- generar una copia antes de actualizar Rubrova o migrar el esquema;
- ofrecer una segunda ubicación externa/cifrada opcional (NAS o almacenamiento remoto) sin exigir una cuenta cloud para usar Rubrova.

Aplicar el principio 3-2-1 cuando la operación lo permita: tres copias, dos medios distintos y una copia fuera del equipo. Una copia en otra carpeta del mismo disco no protege contra la rotura de ese disco.

Los objetivos de RPO y RTO se muestran como metas a medir en equipos reales. No se promete recuperar operaciones posteriores a la última copia segura fuera del equipo. Rubrova debe mostrar claramente fecha/hora del último respaldo externo válido y advertir cuando su antigüedad supere la política configurada.

## 4. Cifrado y recuperación de claves

- Cifrar los paquetes y copias fuera del equipo con una clave que no dependa exclusivamente del Windows instalado.
- Ofrecer una clave/frase de recuperación o archivo de recuperación exportable, con advertencia para guardarlo en un lugar distinto del backup.
- No guardar la clave dentro del mismo archivo cifrado ni confiar únicamente en Windows Credential Manager/DPAPI, porque puede perderse al reinstalar Windows o cambiar el equipo.
- Permitir proteger copias con contraseña robusta y derivación de clave adecuada; la implementación debe usar bibliotecas criptográficas mantenidas y parámetros versionados.
- Guardar tokens, claves de terminal, certificados privados ARCA y credenciales de proveedores en un almacén secreto separado, cifrado y de acceso restringido.
- Los secretos se pueden respaldar en un archivo/paquete de recuperación independiente, también cifrado, o volver a vincular manualmente tras la recuperación.
- Nunca guardar secretos en Git, logs, fixtures, manifiestos legibles ni backups sin cifrar.
- Explicar que perder tanto la clave de recuperación como su copia protegida puede hacer imposible descifrar los respaldos.

## 5. Recuperar en una PC nueva o después de reinstalar Windows

El flujo debe ser guiado:

1. Instalar Windows y descargar/instalar una versión compatible de Rubrova.
2. Conectar el disco externo, NAS o ubicación donde se encuentre el respaldo.
3. Abrir “Recuperar Rubrova” y seleccionar el paquete/punto deseado.
4. Ingresar la clave de recuperación o desbloquear el almacén cifrado.
5. Verificar manifiesto, checksums, integridad, versión, espacio y compatibilidad antes de tocar datos existentes.
6. Restaurar primero en una instancia/directorio aislado, nunca sobre la única copia disponible.
7. Aplicar sólo las migraciones de esquema soportadas y ejecutar verificaciones de saldos, conteos, relaciones y ledgers.
8. Conciliar pagos, terminales, ARCA, webhooks y otros efectos externos que puedan haber ocurrido después del corte. Una restauración local no cancela un pago aprobado ni una factura autorizada; consultar al proveedor antes de reintentar.
9. Mostrar un resumen de lo recuperado, fecha exacta del último dato, pendientes, advertencias y dispositivos que necesitan volver a vincularse.
10. Autorizar la activación de la instalación restaurada y conservar intactos el paquete y el equipo/disco anterior hasta terminar la verificación.

La restauración debe funcionar aunque la nueva computadora tenga otro nombre, usuario de Windows, letra de disco, ruta de instalación o número de serie. Los identificadores del negocio no pueden depender de la identidad física del equipo.

## 6. Cambio de equipo y continuidad de dispositivos

La copia incluye perfiles de impresoras, lectores, balanzas, cajas y terminales, pero no debe fingir que la vinculación física se transfiere sola. Al iniciar en otro equipo, un asistente vuelve a detectar y probar los periféricos y solicita autorización para asociarlos.

Los secretos y certificados se recuperan mediante el almacén cifrado independiente o se vuelven a registrar. La restauración no debe activar dos cajas con la misma identidad de dispositivo ni duplicar una terminal.

## 7. Exportación portable y salida del sistema

Además del backup nativo, el dueño debe poder exportar sus datos en formatos utilizables:
- datos tabulares estructurados (CSV/JSON y Parquet cuando corresponda);
- documentos originales y adjuntos en su estructura lógica;
- catálogo de IDs, relaciones, monedas, unidades, zona horaria y diccionario de datos;
- manifiesto, checksums y reporte de validación;
- historial de versiones y cambios de esquema.

La exportación portable sirve para migrar de motor o plataforma. No reemplaza el paquete de recuperación rápida ni debe perder relaciones entre venta, pago, stock, factura y documento de origen.

## 8. Seguridad y auditoría

Registrar quién solicitó, creó, verificó, descargó, restauró o eliminó una copia; cuándo, desde qué instalación y con qué resultado. Proteger el catálogo para que una persona sin permiso no pueda descargar o borrar respaldos.

Las copias deben estar cifradas en reposo y durante la transferencia. La eliminación respeta la retención configurada y deja auditoría. Probar restauraciones en un equipo/instancia aislada, sin contactar terminales, ARCA ni otros servicios externos hasta completar la conciliación.

## 9. Pruebas obligatorias

- Copia completa de todas las áreas y restauración exacta en la misma versión.
- Restauración en una instalación Windows limpia con ruta, usuario y disco distintos.
- Restauración en una PC de reemplazo a partir únicamente de un disco externo.
- Recuperación con el paquete lógico cuando el snapshot nativo del motor no es compatible.
- Verificación de ventas, pagos, caja, stock, costos, cuentas, comprobantes, adjuntos, auditoría y analítica después del restore.
- Restauración de copia cifrada usando la clave externa; fallo claro ante clave incorrecta o perdida.
- Corrupción/truncamiento de archivo, checksum incorrecto, archivo faltante y cadena incremental incompleta: rechazo seguro y conservación de originales.
- Equipo desconectado antes de la siguiente copia externa: advertir el RPO real y no declarar backup protegido.
- Migración desde una versión soportada a otra: comprobar esquema, saldos, eventos y adjuntos.
- Re-vinculación de impresora, scanner, balanza y terminal sin duplicar identidades ni cobros.
- Restauración seguida de consulta de estado de pagos y documentos fiscales inciertos antes de reintentar.

La prueba sólo pasa si la operación puede continuar y los ledgers concilian. Un ZIP que se abre o una base que arranca no bastan.

## 10. Criterios de aceptación

- El dueño puede crear y verificar un backup desde la interfaz sin comandos.
- Una copia almacenada fuera de la PC permite recuperar Rubrova en un equipo limpio.
- El sistema informa último corte recuperable, integridad, cobertura, tamaño y última restauración probada.
- Los archivos y transacciones restaurados conservan IDs, vínculos, fechas, zona horaria, moneda, estados y auditoría.
- Ningún pago, venta, stock o comprobante se duplica al restaurar/reconciliar.
- Un backup incompleto, corrupto o sin clave no reemplaza datos válidos.
- La exportación portable permite leer los datos sin ejecutar la aplicación.
- El proceso puede realizarse con una guía en español y sin depender de herramientas de desarrollo.

## 11. Estado y dependencias

- [x] Requisito de recuperar la operación en instalación limpia documentado.
- [x] Separación de backup completo, incremental, exportación portable y secretos.
- [x] Flujo previsto para reinstalar Windows o reemplazar la computadora.
- [ ] Elegir motor POS/ERP y comprobar su soporte real de snapshot/WAL/exportación.
- [ ] Definir formato y esquema versionado del paquete portable.
- [ ] Implementar programación, catálogo, cifrado, verificación y retención.
- [ ] Implementar asistente de restauración y re-vinculación de periféricos.
- [ ] Probar restauración Windows limpia, PC de reemplazo y recuperación de secretos.

**Estado real:** el diseño ya es un requisito de Rubrova; la creación automática y la restauración guiada todavía no están implementadas.
