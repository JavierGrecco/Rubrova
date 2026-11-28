# MyCompany 6.2 — mapa de utilidades compartidas

**Estado: lectura de fuentes inicial completada para los 21 módulos; pruebas de runtime y validación de cada integración pendientes.**

Este documento describe los 21 módulos de \`vendor/mycompany/src/main/lsfusion/utils\`. Son una capa transversal que MyCompany reutiliza en distintas áreas. No se deben tratar como funciones de negocio aisladas ni copiar su lógica en Rubrova antes de revisar sus contratos.

## 1. Inventario de módulos y dependencias

| Módulo | Dependencias \`REQUIRE\` | Responsabilidad identificada |
|---|---|---|
| \`Audio\` | \`SystemEvents\` | Reproducción de audio remoto o local desde formularios |
| \`BarCodeReader\` | \`SystemEvents\` | Lectura de códigos con cámara y cliente web |
| \`Call\` | \`Employee\`, \`Utils\` | Modelo común de llamadas y puntos de extensión para telefonía |
| \`Color\` | \`Utils\` | Paleta de colores compartida con valores RGB |
| \`Comments\` | \`SystemEvents\`, \`DateUtils\` | Comentarios enriquecidos asociados a objetos, historial y archivos |
| \`Crypto\` | \`SQLUtils\`, \`FileUtils\` | Operaciones criptográficas de apoyo y llamadas a \`pgcrypto\` |
| \`DateUtils\` | \`Time\`, \`Utils\` | Fórmulas, períodos, filtros y dimensiones de fecha/hora |
| \`Doc\` | \`SystemEvents\`, \`Authentication\`, \`Time\`, \`BarCode\`, \`Icon\`, \`ItemAttribute\`, \`ObjectUtils\` | Macros reutilizables para documentos, estados, relaciones, búsqueda, historial y descuentos |
| \`DocTemplate\` | \`MasterData\`, \`Utils\` | Plantillas de documentos por formato y tipo documental |
| \`Documentation\` | \`MarkdownViewer\` | Acceso a manuales según el idioma del usuario |
| \`EmailTemplate\` | \`MasterDataSettings\`, \`Email\` | Plantillas de correo y acciones para enviar mensajes desde objetos |
| \`EmailUtils\` | \`Employee\`, \`Comments\` | Cuenta de correo por usuario, notificaciones, bandeja y asociación de correos a objetos |
| \`FileUtils\` | Sin \`REQUIRE\` declarado | Adjuntos, metadatos, apertura, descarga y vista previa de archivos |
| \`GeoUtils\` | \`SystemEvents\` | Obtención de ubicación geográfica desde el navegador |
| \`Initial\` | \`DefaultData\`, \`SystemEvents\` | Inicialización de datos una sola vez, con puntos de exclusión |
| \`Input\` | \`SystemEvents\` | Filtros por nombre, expresiones de teléfono/correo y teclados en pantalla |
| \`MarkdownViewer\` | \`SystemEvents\` | Visualización de Markdown, imágenes locales y navegación por historial |
| \`MetaNumerator\` | \`Numerator\`, \`MasterDataSettings\` | Metacódigo para numeración automática de clases y documentos |
| \`NumericUtils\` | Sin \`REQUIRE\` declarado | Normalización de escala numérica con SQL |
| \`ObjectUtils\` | Sin \`REQUIRE\` declarado | Historial de objetos, plantillas de propiedades y sincronización de propiedades |
| \`Selection\` | Sin \`REQUIRE\` declarado | Selección múltiple y acciones masivas sobre formularios |

La dependencia \`REQUIRE\` declara composición entre módulos, no un contrato completo. Hay que leer también las propiedades/acciones abstractas que otros módulos completan con \`+=\` o \`ACTION+\`, y las macros que generan código adicional.

## 2. Fichas funcionales

### 2.1 Audio

**Fuente:** \`utils/Audio.lsf\`, \`resources/web/utils/audio.js\`.

- Incluye un formulario de reproducción para una referencia remota (texto/URL) y otro para un archivo local \`RAWFILE\`.
- Los dos formularios utilizan el componente web personalizado \`playRecord\`.
- Carga \`audio.js\` al iniciar el cliente web.

**No significa:** que exista grabación de audio, telefonía o almacenamiento de llamadas. Es un reproductor.

**Pendiente:** formatos admitidos, tamaño máximo, autenticación de URL remota, compatibilidad de navegador, controles de reproducción, descarga de archivos y comportamiento sin conexión.

### 2.2 BarCodeReader

**Fuente:** \`utils/BarCodeReader.lsf\`, \`resources/web/utils/barcodereader.js\`, \`resources/web/utils/html5-qrcode.js\`.

- Carga las bibliotecas web de lectura de códigos.
- Expone opciones configurables en JSON; los valores iniciales detectados son \`fps = 5\` y \`photo = 1\`.
- El componente devuelve texto decodificado y, cuando está habilitado, una captura codificada en Base64 que se transforma en imagen local.
- La acción \`readBarcode()\` recibe el JSON del cliente y carga el texto/captura en propiedades locales.

**Límite:** el módulo no decide qué hacer con el código leído. La búsqueda de producto, selección de lote, movimiento de inventario o emisión de comprobante los implementan otros módulos.

**Pendiente:** formatos soportados, permisos de cámara, HTTPS, dispositivos, lectura de códigos dañados, concurrencia y tratamiento de imágenes/privacidad.

### 2.3 Call

**Fuente:** \`utils/Call.lsf\`.

- Declara \`Call\` y una tabla propia.
- Guarda identificador, fecha/hora de inicio, sentido entrante/saliente, llamante, destinatario, nombre del contacto, duración, resultado y si quedó grabada.
- Expone puntos abstractos: \`callAvailable\`, \`call\`, \`start\`, \`end\` y \`requestRecord\`.

**Interpretación:** es un contrato común para que los conectores de telefonía completen el comportamiento. No integra por sí solo una central telefónica.

**Pendiente:** idempotencia de eventos, correlación del identificador del proveedor, estados, grabaciones, retención, permisos y conectores concretos. Los módulos Zadarma/Mango regionales se estudian por separado.

### 2.4 Color

**Fuente:** \`utils/Color.lsf\`.

- Define colores semánticos: primario, secundario, éxito, información, advertencia, peligro, claro y oscuro; cada uno tiene variante sutil.
- Expone nombre, ID y valor RGB materializado.
- Provee un formulario de consulta de la paleta.

**Límite:** no es un sistema completo de temas ni una paleta editable por usuario; los valores RGB están definidos en el módulo.

**Pendiente:** contraste WCAG, consistencia con temas de Rubrova y pruebas en los clientes web/escritorio.

### 2.5 Comments

**Fuente:** \`utils/Comments.lsf\`, \`resources/web/utils/comments.js\`, \`comments.css\`.

- La macro \`defineObjectComments\` crea una clase de comentario vinculada al objeto de negocio, fecha/hora, usuario, texto enriquecido y conteo/último comentario.
- Los comentarios se muestran en un componente web \`comments\`; hay acciones para agregar, editar y eliminar.
- Incluye puntos abstractos \`header\` y \`footer\` para mostrar información adicional.
- \`defineObjectCommentsHistory\` agrega al comentario los cambios del historial del objeto.
- \`defineObjectCommentsFiles\` agrega enlaces a archivos adjuntos del comentario.
- \`defineObjectCommentsCreate\` crea el comentario contenedor cuando se registra el primer evento/archivo asociado.

**Pendiente:** permisos por objeto, edición/borrado, auditoría de eliminaciones, sanitización de HTML enriquecido, XSS, adjuntos, notificaciones, retención y acceso a archivos. La seguridad del comentario no debe inferirse del permiso de la ficha principal.

### 2.6 Crypto

**Fuentes:** \`utils/Crypto.lsf\` y cinco clases Java en \`src/main/java/mycompany/utils/crypto\`.

- Al iniciar intenta crear la extensión PostgreSQL \`pgcrypto\` si no existe.
- Expone propiedades locales para resultados cifrados, CSR, clave privada, XML firmado, clave AES e IV.
- Calcula hash SHA-256 en Base64 mediante SQL.
- La capa Java implementa:
  - generación de clave AES de 256 bits e IV aleatorio de 16 bytes;
  - cifrado AES/CBC con relleno PKCS5 (equivalente a PKCS#7 para el tamaño de bloque AES);
  - cifrado RSA-OAEP con MGF1 y certificado X.509;
  - generación de par de claves EC \`secp256r1\` y CSR firmado con SHA256withECDSA;
  - firma XML XAdES enveloped con digest SHA-256, canonicalización exclusiva, datos del certificado y hora de firma.

**Advertencias de seguridad que deben verificarse antes de usar en producción:**

- AES-CBC por sí solo no autentica el contenido. Debe existir un mecanismo externo de integridad/autenticación o evaluarse otro modo autenticado; no hay que asumir que el módulo lo resuelve.
- Revisar codificación de bytes, parámetros OAEP exactos, longitud de clave, IV, formato de serialización y manejo de errores.
- Revisar ciclo de vida de claves privadas: dónde se guardan, cifrado en reposo, permisos, backups, rotación, revocación y exposición en logs/propiedades.
- Revisar el endurecimiento del parser XML y la prevención de XXE/entidades externas en la firma.
- Verificar certificados, cadena de confianza, validación de vigencia y algoritmos permitidos.
- El nombre XAdES no demuestra compatibilidad con un estándar fiscal argentino ni con ARCA.

**Pendiente:** inspección completa de las cinco clases, pruebas criptográficas independientes con vectores conocidos, pruebas de interoperabilidad, análisis de dependencias BouncyCastle/JDK y revisión de seguridad especializada.

### 2.7 DateUtils

**Fuente:** \`utils/DateUtils.lsf\`.

- Convierte duraciones entre timestamps en unidades legibles y localizables.
- Calcula duración de fechas y textos como hoy, hace X días o dentro de X días.
- Maneja intervalos inclusivos de fechas, desplazamiento al mes anterior/siguiente y períodos diarios/semanales/mensuales/anuales.
- Aporta macros para filtros por rango de fechas, agregaciones por día de semana, semana, mes, año, minuto y hora, y su presentación en formularios.
- Usa fórmulas SQL para calcular partes de tiempo; hay funciones que dependen del reloj de PostgreSQL (\`LOCALTIMESTAMP\`).

**Pendiente:** zonas horarias, UTC/local, horario de verano, límites de mes/año, años bisiestos, precisión, cambio de día durante sesiones largas y coherencia entre JVM y PostgreSQL.

### 2.8 Doc

**Fuente:** \`utils/Doc.lsf\` (620 líneas).

Es una biblioteca de metacódigo para construir documentos de negocio de forma homogénea. Entre las macros identificadas:

- formularios de lista/detalle y objetos relacionados;
- estados, contenedores y acciones para cambiar estados;
- búsqueda de documentos y selección de líneas;
- historial de documentos y líneas;
- relaciones documento-origen/destino y relaciones entre líneas;
- descuentos y filtros por propiedades;
- conteo de renglones y reglas de producto/servicio en una sola línea;
- componentes auxiliares para presentación, etiquetas y cabeceras;
- registro de fuentes de actividad/comentarios.

**Importancia:** las macros expanden código en los módulos consumidores. El conteo de propiedades/formularios visible antes de expandirlas no representa todo lo que termina compilado. No hay que recrear formularios documentales a mano sin revisar qué macros ya aplican.

**Pendiente:** ficha de cada macro con entradas, declaraciones generadas, supuestos sobre clases/propiedades, orden de expansión, comportamiento cuando falta una extensión y efectos en rendimiento.

### 2.9 DocTemplate

**Fuente:** \`utils/DocTemplate.lsf\`.

- Define formatos PDF, DOCX, XLSX, RTF y HTML, además de una opción \`Printer\` sin vista previa.
- La macro \`defineDocTemplate\` crea clases de plantillas, nombre, nombre de recurso, archivo subido, formato, nombre de exportación y acciones para abrir, cargar y restablecer el archivo.
- \`defineDocTemplateType\` relaciona plantillas con tipos documentales.
- \`defineDocTemplateTypeForm\` agrega una acción de impresión al documento: selecciona una plantilla por tipo o pide que se elija; compone dinámicamente la acción de impresión y exportación.

**Pendiente:** motor real de renderizado por formato, plantillas de muestra, variables disponibles, seguridad de archivos, rutas/recursos, nombres de salida, fuentes, concurrencia y formatos regionales. El inventario de 30 JRXML es una capa de reportes/impresión adicional y debe conciliarse con estas plantillas.

### 2.10 Documentation

**Fuente:** \`utils/Documentation.lsf\`.

- Agrega al navegador una acción para abrir documentación del usuario.
- Busca \`docs/<idioma del usuario>/overview.md\`.
- Si ese recurso no existe, el visor vuelve al idioma inglés.

**Estado de idioma:** MyCompany upstream trae documentos en inglés, polaco y ruso; no hay carpeta es_AR. En esa composición, un usuario argentino puede terminar viendo documentación en inglés hasta que Rubrova entregue su propia documentación en español argentino.

### 2.11 EmailTemplate

**Fuente:** \`utils/EmailTemplate.lsf\`.

- Permite mantener plantillas con nombre, asunto y cuerpo enriquecido.
- Define una acción común \`writeMessage\` que crea un correo, abre el formulario de composición y ejecuta \`send\`.
- Las macros asocian plantillas a un objeto: filtran cuáles se pueden usar, procesan variables \`{{...}}\` a partir de propiedades del objeto y rellenan destinatario/asunto/cuerpo.
- Si no hay plantilla aplicable, abre el cliente de correo mediante \`mailto:\` como alternativa.

**Pendiente:** transporte SMTP real, remitente y cuenta, adjuntos, variables sin resolver, HTML seguro, codificación, errores, reintentos, auditoría y política de envío.

### 2.12 EmailUtils

**Fuente:** \`utils/EmailUtils.lsf\`.

- Asocia una cuenta de correo con el empleado.
- Define macros para avisos por correo cuando se agrega un comentario a un objeto y el destinatario optó por recibirlos.
- Permite vincular correos entrantes con objetos de negocio.
- Una bandeja puede listar correos, remitente, asunto, fechas, mensaje y adjuntos; los marca como listos, ignorados o ya procesados.
- Las macros \`create\` y \`attach\` crean un objeto de negocio o asocian el correo a uno existente, trasladan los adjuntos y completan el objeto mediante una acción abstracta \`fill\`.

**Límite:** el código de esta utilidad no demuestra por sí solo cómo se conecta al servidor de correo, sincroniza carpetas ni implementa autenticación. Eso depende del módulo \`Email\`, sus cuentas y su configuración.

**Pendiente:** IMAP/SMTP, OAuth, deduplicación, correlación de conversaciones, adjuntos maliciosos, privacidad, retención, permisos y tratamiento de correos reenviados.

### 2.13 FileUtils

**Fuente:** \`utils/FileUtils.lsf\`.

- Ofrece fórmulas para tamaño en bytes y extracción de segmentos de archivos.
- La macro \`defineObjectFiles\` agrega una clase de adjunto relacionada con cualquier clase de negocio y guarda archivo, nombre, extensión, descripción, fecha/hora, usuario y orden.
- Permite subir, abrir, descargar y enumerar archivos, incluso los tres primeros como accesos directos.
- La macro \`defineObjectFilesForm\` agrega grilla de archivos, carga desde JSON/Base64 y vista previa.
- Muestra imágenes JPG/JPEG/PNG/BMP y PDF; para DOC/DOCX intenta convertir con \`wordToPdf\`.

**Pendiente:** límites de tamaño, validación de extensión y MIME, antivirus, protección de rutas, archivos ejecutables, almacenamiento y backup, conversión DOC/DOCX, acceso directo a URL, registro de descargas y permisos por objeto.

### 2.14 GeoUtils

**Fuente:** \`utils/GeoUtils.lsf\`, \`resources/web/utils/geoutils.js\`.

- Obtiene ubicación mediante API de geolocalización del navegador.
- Devuelve timestamp, latitud, longitud y errores del navegador.
- Los valores de esta utilidad son locales a la sesión; los módulos de negocio deciden si los persisten.
- Opciones por defecto detectadas: alta precisión, timeout de 5 segundos, antigüedad máxima 0 y caché indicada de 60.
- Provee una macro para insertar el bloque de geolocalización en formularios.

**Pendiente:** consentimiento, permisos del navegador, HTTPS, exactitud real, falsificación de ubicación, retención, acceso a coordenadas, cumplimiento de privacidad y comportamiento sin GPS.

### 2.15 Initial

**Fuente:** \`utils/Initial.lsf\`.

- Mantiene una marca \`initialized\`.
- En el evento de inicio ejecuta la carga inicial cuando no se completó y no se activa el punto abstracto \`skipInitial\`.
- Depende de \`DefaultData\` para la infraestructura de carga y \`SystemEvents\` para el evento de inicio.

**Pendiente:** qué implementaciones de \`loadDefaultData\` existen, orden de carga, idempotencia, rollback, ejecución simultánea, diferencias entre base nueva y actualización y forma de marcar la inicialización como terminada.

### 2.16 Input

**Fuente:** \`utils/Input.lsf\`.

- Define un diálogo de ingreso de cantidad.
- Mantiene expresiones configurables para validar teléfonos y correos; asigna valores iniciales al primer inicio.
- Incluye macros para filtros por nombre, teclados numéricos y teclados decimales en formularios.
- Permite fijar cantidades, aumentar/disminuir, limpiar el valor y, en una variante, ejecutar el cambio dentro de una sesión nueva con \`APPLY\`.
- Los valores de teclado se almacenan localmente durante la interacción.

**Pendiente:** precisión/escala, separador decimal regional, teclado físico y móvil, negativos, límites de cantidad y consistencia entre la variante que aplica cambios y la que edita en la sesión actual.

### 2.17 MarkdownViewer

**Fuente:** \`utils/MarkdownViewer.lsf\`, \`resources/web/utils/markdownviewer.js\`, \`markdownviewer.css\`.

- Carga una página Markdown desde los recursos del producto.
- Lee también imágenes relacionadas con la carpeta \`images/\` y las embebe como Data URI Base64 para evitar rutas relativas que el cliente web no puede resolver.
- Mantiene historial local de páginas con acciones atrás/adelante.
- El componente web devuelve la ruta elegida y el servidor actualiza el contenido.
- Al abrir el visor, carga las bibliotecas \`marked@18.3.0\` y \`marked-gfm-heading-id@4.1.4\) desde jsDelivr mediante \`INTERNAL CLIENT WAIT\`.

**Riesgo operativo:** el comentario del módulo aclara que el visor se abre bajo demanda para no bloquear el POS al inicio. Sin embargo, necesita conectividad al CDN en el momento de abrirlo, salvo que Rubrova empaquete localmente esas bibliotecas. Hay que decidir y probar el modo sin conexión.

**Pendiente:** sanitización XSS, enlaces externos, archivos de imagen de gran tamaño, caché, CDN/versión fijada, fallback offline, accesibilidad y compatibilidad web.

### 2.18 MetaNumerator

**Fuente:** \`utils/MetaNumerator.lsf\`.

- Ofrece macros para agregar numerador automático a una clase o a un tipo documental.
- Permite definir serie, valor mínimo/máximo y longitud de cadena, asigna el número al crear el objeto y avanza el numerador en la sesión.
- Otra macro agrega un identificador único de clase con longitud configurable y propiedad indexada.
- Incorpora selector/configuración del numerador a opciones de MyCompany.

**Pendiente:** concurrencia multiusuario, bloqueo y unicidad, huecos por cancelación, copia de documentos, anulaciones, reinicio de serie, año fiscal, sucursal/punto de venta y requisitos legales de numeración.

### 2.19 NumericUtils

**Fuente:** \`utils/NumericUtils.lsf\`.

- Expone una fórmula SQL \`trimScale\` basada en PostgreSQL \`trim_scale\`, que quita escala decimal innecesaria de un valor numérico al presentarlo/normalizarlo.

**Pendiente:** compatibilidad de versión PostgreSQL, diferencia entre formato y precisión contable, impacto en redondeos e interoperabilidad con otros motores.

### 2.20 ObjectUtils

**Fuente:** \`utils/ObjectUtils.lsf\`.

- Agrega una opción global para desactivar el registro de historial.
- La macro \`defineHistoryObject\` crea una clase de historial con objeto, fecha/hora, usuario, equipo, tipo y descripción; expone autor/fecha de creación y última modificación.
- \`defineHistoryProperty\` registra los cambios de una propiedad, con valor anterior y nuevo, salvo que se desactive el historial o se elimine el objeto en el mismo evento.
- \`defineHistoryForm\` agrega un panel con historial a una ficha.
- \`definePropertyObject\`, \`definePropertyValue\` y \`processPropertyTemplate\` ofrecen un mecanismo de reemplazo de marcadores \`{{...}}\` por propiedades del objeto; pueden formar listas HTML resumidas.
- \`defineHistoryModify\` genera eventos para alta y baja.
- \`defineSychronizeProperty\` (nombre tal como aparece en fuente) sincroniza cambios entre una propiedad del objeto y otra de su clase.

**Riesgos:** el interruptor global puede dejar operaciones sin historial; no se debe asumir que es una auditoría inmutable. Deben validarse quién lo puede cambiar, el contexto de ejecución, integridad del historial y tratamiento de cambios masivos.

### 2.21 Selection

**Fuente:** \`utils/Selection.lsf\`.

- Agrega selección por fila con estado local anidado.
- Inserta controles para seleccionar, invertir la selección, limpiar la selección y filtrar por seleccionados.
- Macros adicionales permiten copiar objetos seleccionados (pidiendo fecha/hora y usando \`clone\`), borrar seleccionados en una sesión nueva con confirmación, o ejecutar una acción sobre todos los seleccionados.
- La selección se limita al filtro/objeto que define el formulario.

**Pendiente:** permisos por acción y objeto, volumen de registros, conflictos concurrentes, restricciones de borrado, límites del lote, resultado parcial y posibilidad de revertir.

## 3. Integración entre utilidades y dominios

| Utilidad | Consumidores identificados o candidatos directos | Relación |
|---|---|---|
| \`Doc\` | Compras, ventas, facturas, movimientos de inventario, fabricación y otros documentos | Estandariza formularios, estados, historial y relaciones mediante metacódigo |
| \`DocTemplate\` | Impresión de documentos por tipo | Resuelve selección/configuración de plantillas y ejecución dinámica de impresión |
| \`MetaNumerator\` | Pedidos, facturas, recepciones, despachos, ajustes, órdenes de fabricación, recibos | Genera números/series en los documentos que invocan las macros |
| \`ObjectUtils\` | Datos maestros y fichas que habilitan historial | Historial de cambios y sustitución de marcadores por valores del objeto |
| \`Comments\` | CRM, proyectos, documentos y objetos que agregan las macros | Comentarios con historial y adjuntos |
| \`FileUtils\` | Socios, vehículos, productos, documentos, postulaciones, comentarios | Adjuntos comunes con acceso y vista previa |
| \`EmailTemplate\` / \`EmailUtils\` | CRM, RR. HH., socios y documentos | Correo saliente con plantillas y asociación de entrantes a objetos |
| \`DateUtils\` | Reportes, documentos y formularios que agregan filtros/agrupaciones | Filtros por fecha y dimensiones temporales |
| \`GeoUtils\` | Asistencia, ubicación y posibles formularios de seguimiento | Captura del navegador; cada módulo decide persistencia y uso |
| \`BarCodeReader\` | POS, productos, inventario y picking | Entrega el código leído; cada módulo implementa la búsqueda/operación |
| \`Call\` | CRM y conectores telefónicos regionales | Modelo y hooks abstractos para telefonía |
| \`Selection\` | Listados de datos maestros y documentos que usan selección masiva | Acciones por lote sobre filas elegidas |
| \`Input\` | POS, carga móvil y formularios táctiles | Teclado, filtros y datos numéricos de entrada |
| \`MarkdownViewer\` / \`Documentation\` | Ayuda y manuales de usuario | Visualización de recursos Markdown e imágenes |
| \`Crypto\` | Integraciones regionales como KSeF; otros usos a confirmar | CSR, cifrado, hash y firma XML; depende de claves/certificados y revisión de seguridad |

Esta tabla vincula consumidores observados y candidatos. La dependencia técnica real de cada módulo se confirma con \`REQUIRE\`, llamadas, \`+=\`, \`ACTION+\` y metacódigo; no se debe inferir sólo por afinidad de nombres.

## 4. Inventario de recursos que complementan las utilidades

Además de los 21 módulos LSF, el snapshot MyCompany contiene recursos web específicos para varias utilidades:

- \`audio.js\`
- \`barcodereader.js\` y \`html5-qrcode.js\`
- \`comments.js\` y \`comments.css\)
- \`geoutils.js\`
- \`markdownviewer.js\` y \`markdownviewer.css\)
- \`dragula.js\` y \`dragula.css\) (recurso común de arrastre/soltar; mapear consumidores)
- hojas/scripts de Kanban de CRM/proyectos y calendario de turnos
- scripts regionales Zadarma, Wazzup y CryptoPro

Las extensiones Java de Crypto se detallan en el módulo \`Crypto\`. Los recursos web y las clases Java deben auditarse junto con el módulo LSF que los carga; un archivo presente en el repo no está automáticamente habilitado en la aplicación.

## 5. Matriz de verificación pendiente

| Área | Qué falta demostrar |
|---|---|
| Documentos y plantillas | Renderizado real por formato, selección por tipo, nombres, fuentes, imágenes, impresión y permisos |
| Historial y comentarios | Cobertura de altas/cambios/bajas, usuario/equipo, desactivación global, sanitización, permisos y archivos |
| Archivos | Validación MIME/tamaño, antivirus, preview, conversión DOCX, descarga autenticada y backups |
| Correo | SMTP/IMAP, cuentas, OAuth, plantillas, adjuntos, duplicados, errores y trazabilidad |
| Telefonía/llamadas | Conectores específicos, estados, grabaciones, webhooks, correlación e idempotencia |
| Geolocalización | Consentimiento, exactitud, seguridad, persistencia, retención y permisos |
| Código de barras | Cámara, navegadores, HTTPS, formatos, desempeño y vínculo con producto/lote |
| Numeración | concurrencia, huecos, cancelaciones, reset, sucursales y requisitos fiscales |
| Criptografía | vectores de prueba, interoperabilidad, llaves/certificados, XML hardening, modo autenticado y revisión externa |
| Visor documental | sanitización, CDN, offline, imágenes y accesibilidad |
| Selección masiva | permisos, lotes grandes, errores parciales, reversión y concurrencia |
| Fechas y números | zona horaria, precisión, redondeo, PostgreSQL y formatos regionales |

## 6. Estado

Las 21 fuentes de utilidades fueron identificadas y sus contratos principales se leyeron a nivel de código. Esta clasificación no representa todavía aceptación en runtime. La puerta 9.7 continúa ABIERTA hasta que las utilidades relevantes se carguen, se prueben, se concilien con sus consumidores y queden documentadas las excepciones.
