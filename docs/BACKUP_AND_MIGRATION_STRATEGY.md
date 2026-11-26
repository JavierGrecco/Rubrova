# Copias de seguridad y recuperación de Rubrova

**Revisión:** 26 de noviembre de 2026  
**Estado:** primer incremento técnico implementado para backup lógico PostgreSQL nativo. No es todavía el paquete portable completo ni una recuperación de negocio certificada.

## 1. Objetivo para el negocio

El dueño debe poder recuperar Rubrova sin depender de la computadora original. Si Windows se reinstala, el disco falla o se reemplaza el equipo, debe ser posible instalar Rubrova en otra PC, seleccionar una copia y continuar con el negocio conservando sus operaciones e historial.

No alcanza con copiar una carpeta de instalación ni con guardar solamente la base de datos. El respaldo debe permitir recuperar la información de negocio, los documentos y la configuración necesaria para volver a operar.

La recuperación debe poder realizarla una persona autorizada desde una interfaz guiada, sin abrir una consola, editar bases de datos ni reconstruir carpetas manualmente.

## 2. Dos tipos de respaldo complementarios

### 2.1 Copia de recuperación completa

Paquete portable de Rubrova, con formato identificable (propuesta: .rubrova-backup), verificable y sin cifrado propio de Rubrova. Incluye los datos necesarios para reconstruir el estado en una instalación compatible, sin depender de la ruta original ni del disco anterior.

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
- checksums, tamaño, destino y estado de integridad; no hay clave de backup de aplicación;
- ubicación, retención, estado de verificación y última restauración probada.

La captura establece una barrera consistente: el corte del ledger, los archivos, los eventos y los offsets deben corresponder al mismo estado. Si un componente no pudo incluirse, el respaldo se marca incompleto y no se ofrece como una copia válida de recuperación total.

## 3. Frecuencia, destinos y retención

La política inicial se centra en discos locales y externos; no exige NAS, nube ni cuentas de terceros.

- Proteger cada operación confirmada mediante la persistencia durable del motor transaccional.
- Mantener puntos locales incrementales cuando el motor seleccionado lo soporte de forma consistente.
- Crear una copia completa automática al menos una vez al día.
- Cuando un disco externo esté conectado, copiar el respaldo a ese medio y verificar checksums y consistencia antes de declarar la copia correcta.
- Rotar dos discos externos identificados: conectar uno para generar y verificar la copia; luego desconectarlo y guardar el otro en una ubicación física distinta, preferentemente fuera del establecimiento. Alternarlos regularmente. No dejar ambos discos conectados permanentemente.
- Conservar 30 copias diarias y 12 cierres mensuales como política inicial, sujeta a capacidad y prueba de restauración.
- Crear un punto de recuperación previo a cada actualización o migración de esquema.
- Mostrar fecha/hora de última copia local y externa válida. Si el disco externo no está conectado o el último backup está atrasado, mostrarlo como riesgo, no como "protegido".

El RPO de pérdida de datos frente a un daño del equipo principal queda limitado a la fecha del último respaldo externo verificado. Una copia interna en otro directorio o partición del mismo disco no protege contra la falla de ese disco. Los backups conectados pueden recibir corrupción o malware junto con los datos activos; por eso la copia externa se desconecta después de cada ejecución.

## 4. Política inicial: backup sin cifrado a nivel de aplicación

Para la primera versión, **Rubrova no cifrará el paquete de respaldo**. El paquete portable será legible por una instalación compatible y no requerirá contraseña, frase secreta, keychain, TPM ni clave generada por el sistema anterior. Esto reduce el código, el riesgo de perder claves y la complejidad de recuperar después de una reinstalación.

La decisión se apoya en el escenario operativo actual: copias en discos locales y externos bajo control físico del negocio. No significa que un disco externo sea invulnerable. Si se pierde o roba, un respaldo sin cifrado puede ser leído por quien tenga el dispositivo; esa exposición se acepta explícitamente en la política inicial y se reduce con estas medidas:

- Mantener el equipo y los discos en lugares con acceso físico restringido; guardar los discos externos bajo llave.
- Rotar al menos dos discos externos, identificados y registrados; desconectar el disco después de cada copia.
- Conservar al menos una copia fuera del equipo principal y, para acercarse a la regla 3-2-1, fuera del mismo establecimiento. Un incendio, robo o daño físico en el local puede afectar a todos los discos guardados allí.
- No dejar todos los respaldos conectados durante la operación: ransomware, malware o un error administrativo pueden alcanzar las unidades conectadas.
- Mantener puntos históricos y no sobrescribir siempre la misma copia; probar restauraciones y guardar una versión anterior limpia.
- Registrar quién crea, restaura, exporta y elimina respaldos, y proteger esas acciones con roles.
- No incluir contraseñas, tokens, claves privadas, certificados ARCA ni secretos de terminal/proveedores en el paquete legible. Esas credenciales se vuelven a vincular o se gestionan aparte mediante el almacén del sistema operativo y un procedimiento separado.

### 4.1 Protección opcional del disco, no del formato Rubrova

Cuando el disco salga del establecimiento o contenga datos de clientes especialmente delicados, el usuario podrá proteger **el volumen completo** mediante la función de cifrado del sistema operativo (por ejemplo, BitLocker To Go en ediciones de Windows que lo admitan o un volumen externo cifrado compatible con macOS). Esa protección es opcional y queda fuera del formato .rubrova-backup: Rubrova no implementa una segunda capa de cifrado ni administra claves criptográficas propias en esta etapa.

En Windows, la disponibilidad de BitLocker To Go depende de la edición instalada (Pro, Enterprise o Education; no está disponible en Windows Home mediante la función BitLocker estándar). En macOS, la Utilidad de Discos permite crear volúmenes externos cifrados, pero normalmente exige formatear primero el dispositivo. Si se elige cifrar el disco, guardar la clave de recuperación en otro lugar y comprobar que se puede desbloquear en otra PC compatible antes de depender de él. Un disco cifrado sin su clave también puede quedar inaccesible; el cifrado del volumen no elimina el requisito de probar recuperación.

### 4.2 Integridad del paquete

La ausencia de cifrado no elimina la validación. Cada copia tendrá:
- manifiesto con versión del formato, aplicación/esquema, fecha de corte, componentes y tamaño;
- SHA-256 por archivo/fragmento y checksum del manifiesto para detectar corrupción accidental;
- verificación de relaciones, conteos, saldos, ledgers y documentos incluidos;
- resultado de consistencia y estado de última restauración probada.

Los checksums detectan daños y cambios accidentales; por sí solos no autentican quién creó el archivo ni resisten a un atacante que pueda reemplazar el paquete y recalcularlos. En la política inicial esa limitación se compensa con acceso físico y permisos; una firma autenticada se podrá estudiar después si aparece un requisito concreto.

### 4.3 Separar el backup de los secretos

El backup de negocio conserva configuración y referencias, pero omite secretos reutilizables. Después de restaurar, Rubrova presenta una lista de servicios que necesitan reautenticación o reemisión de credenciales. Los certificados privados y tokens no se copian en texto claro junto con ventas/clientes.

No usar DPAPI, Keychain, TPM ni el usuario de Windows como requisito para leer el backup de negocio. Pueden proteger secretos locales o volúmenes, pero no deben condicionar la apertura del paquete portable.

### 4.4 Cuándo reconsiderar el cifrado del paquete

Reevaluar cifrado a nivel de aplicación si los respaldos empiezan a viajar fuera de ubicaciones controladas, si se alojan en almacenamiento de terceros, si hay acceso de varias organizaciones/personas no confiables o si el análisis de riesgo exige confidencialidad criptográfica del archivo. En ese caso debe ser una opción explícita y probada de extremo a extremo, no una obligación que impida restaurar los backups existentes sin claves.

## 5. Recuperar en una PC nueva o después de reinstalar Windows

El flujo debe ser guiado:

1. Instalar Windows y descargar/instalar una versión compatible de Rubrova.
2. Conectar el disco externo, NAS o ubicación donde se encuentre el respaldo.
3. Abrir “Recuperar Rubrova” y seleccionar el paquete/punto deseado.
4. Si el sistema operativo solicita desbloquear el disco externo, hacerlo con su método habitual; el paquete Rubrova no pide una clave adicional.
5. Verificar manifiesto, checksums, integridad, versión, espacio y compatibilidad antes de tocar datos existentes.
6. Restaurar primero en una instancia/directorio aislado, nunca sobre la única copia disponible.
7. Aplicar sólo las migraciones de esquema soportadas y ejecutar verificaciones de saldos, conteos, relaciones y ledgers.
8. Conciliar pagos, terminales, ARCA, webhooks y otros efectos externos que puedan haber ocurrido después del corte. Una restauración local no cancela un pago aprobado ni una factura autorizada; consultar al proveedor antes de reintentar.
9. Mostrar un resumen de lo recuperado, fecha exacta del último dato, pendientes, advertencias y dispositivos que necesitan volver a vincularse.
10. Autorizar la activación de la instalación restaurada y conservar intactos el paquete y el equipo/disco anterior hasta terminar la verificación.

La restauración debe funcionar aunque la nueva computadora tenga otro nombre, usuario de Windows, letra de disco, ruta de instalación o número de serie. Los identificadores del negocio no pueden depender de la identidad física del equipo.

## 6. Cambio de equipo y continuidad de dispositivos

La copia incluye perfiles de impresoras, lectores, balanzas, cajas y terminales, pero no debe fingir que la vinculación física se transfiere sola. Al iniciar en otro equipo, un asistente vuelve a detectar y probar los periféricos y solicita autorización para asociarlos.

Los secretos y certificados se vuelven a vincular o se recuperan mediante el mecanismo separado del sistema operativo; nunca desde el paquete legible. La restauración no debe activar dos cajas con la misma identidad de dispositivo ni duplicar una terminal.

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

El acceso a las copias se protege físicamente y con permisos; el cifrado del disco completo queda opcional a cargo del sistema operativo. La eliminación respeta la retención configurada y deja auditoría. Probar restauraciones en un equipo/instancia aislada, sin contactar terminales, ARCA ni otros servicios externos hasta completar la conciliación.

## 9. Pruebas obligatorias

- Copia completa de todas las áreas y restauración exacta en la misma versión.
- Restauración en una instalación Windows limpia con ruta, usuario y disco distintos.
- Restauración en una PC de reemplazo a partir únicamente de un disco externo.
- Recuperación con el paquete lógico cuando el snapshot nativo del motor no es compatible.
- Verificación de ventas, pagos, caja, stock, costos, cuentas, comprobantes, adjuntos, auditoría y analítica después del restore.
- Restauración del paquete sin claves de aplicación, en PC nueva y desde disco externo.
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

### Incremento técnico inicial

Se incorpora `scripts/platform/native-postgres-backup.py` para el runtime `native-local`:

- `create`: genera un paquete `.rubrova-db-backup` con un volcado PostgreSQL en formato custom, manifiesto, tamaño y SHA-256.
- `verify`: valida las entradas del paquete, el checksum del manifiesto y del volcado, y que `pg_restore --list` pueda leerlo.
- `restore`: verifica primero el paquete y restaura sólo en una base nueva indicada explícitamente. Rechaza nombres reservados y bases existentes. Si falla una restauración, intenta eliminar únicamente la base parcial que creó; no cambia el destino activo de Rubrova.
- La herramienta comprueba que el servidor PostgreSQL 18 pertenece al directorio privado de datos configurado y limita la conexión a loopback. No almacena ni empaqueta contraseñas.
- La prueba nativa de CI crea, verifica y restaura el respaldo dentro del mismo clúster aislado, usando una base de destino separada.

Comandos desde la raíz del repositorio:

```bash
python3 scripts/platform/native-postgres-backup.py create --output /ruta/segura/rubrova-db.rubrova-db-backup
python3 scripts/platform/native-postgres-backup.py verify /ruta/segura/rubrova-db.rubrova-db-backup
python3 scripts/platform/native-postgres-backup.py restore /ruta/segura/rubrova-db.rubrova-db-backup --target-database rubrova_restore_test --confirm-new-database
```

El comando `restore` no sustituye la base activa ni actualiza `runtime-config.json`; restaura a una base nueva para validación o recuperación asistida. El primer paquete declara de forma visible que su alcance es **sólo PostgreSQL**. No contiene archivos adjuntos, imágenes, documentos externos, secretos ni binarios. Los checksums detectan corrupción accidental, no autentican el origen del archivo.

### Lista de implementación

- [x] Requisito de recuperar la operación en instalación limpia documentado.
- [x] Separación de backup completo, incremental, exportación portable y secretos.
- [x] Flujo previsto para reinstalar Windows o reemplazar la computadora.
- [x] Primera herramienta de backup lógico PostgreSQL con manifiesto y SHA-256.
- [x] Verificación estructural mediante checksum y `pg_restore --list`.
- [x] Restauración protegida que sólo crea una base nueva, con limpieza ante fallo.
- [ ] Superar la suite automatizada y el smoke real de PostgreSQL del nuevo SHA.
- [ ] Validar en el Mac físico y en Windows las rutas reales y recuperación de datos.
- [ ] Incorporar adjuntos, documentos, configuración funcional y exportación portable.
- [ ] Implementar programación, catálogo, retención y copia verificada a disco externo.
- [ ] Implementar asistente visual en español y re-vinculación de periféricos.
- [ ] Probar restauración Windows limpia y PC de reemplazo desde un disco externo.

**Decisión vigente:** el backup de Rubrova no tendrá cifrado a nivel de aplicación en la primera versión. La protección opcional del disco se delega al sistema operativo.

**Estado real:** ya existe una primera copia lógica de PostgreSQL; la recuperación completa del negocio sigue sin estar implementada ni aceptada.
