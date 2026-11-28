# Mapa de capacidades de lsFusion 6.2

**Estado: EN CURSO. La puerta de relevamiento de la sección 9.7 sigue ABIERTA.**

Este documento separa la plataforma lsFusion 6.2 del producto MyCompany 6.2. MyCompany está escrito sobre lsFusion, pero sus módulos de negocio no representan por sí solos todas las capacidades del lenguaje, servidor, clientes, APIs y herramientas de administración.

## 1. Fuente y alcance fijados

La fuente de plataforma de Rubrova está fijada en:

- Repositorio: \`lsfusion/platform\`.
- Etiqueta: \`6.2\`.
- Commit: \`dd4dbe5bf9b136e73e18fe25d741253929324350\`.
- Licencia declarada en el lock del proyecto: LGPL-3.0.
- Código Java: 3.330 archivos.
- Módulos LSF propios de la plataforma: 49.
- Documentación incluida: 342 archivos Markdown y 89 imágenes por idioma, inglés y ruso.

La base se distribuye en cuatro módulos Maven: \`api\`, \`desktop-client\`, \`server\` y \`web-client\`. El inventario estructural separa fuentes LSF del servidor y fuentes Java; no deben mezclarse sus conteos.

**Advertencia documental:** algunas páginas de instalación y desarrollo del snapshot incluyen enlaces, ejemplos o nombres de artefactos 6.1 aunque el código fijado sea 6.2. La documentación debe reconciliarse contra la etiqueta 6.2 y el build real antes de transformarse en un procedimiento operativo de Rubrova.

## 1.1 Inventario documental contrastado

El índice automático contiene 684 páginas Markdown y 178 imágenes de lsFusion: 342 páginas y 89 imágenes en inglés, y el mismo conteo en ruso. La comparación de rutas confirma que los 342 nombres de página coinciden entre ambos idiomas.

Hay 33 documentos por idioma que no usan encabezados Markdown estructurados. El indexador conserva su primera línea como título provisional, pero no los considera documentos vacíos: son páginas cortas con texto, tablas o listas. Deben revisarse de manera individual para decidir si son referencias de operadores, introducciones o procedimientos y asociarlos al tema correspondiente.

El catálogo completo por ruta y encabezados se genera con \`scripts/platform/audit-source-docs.mjs\` y se publica como artefacto \`rubrova-source-document-catalog\` de CI. Este índice permite comprobar cobertura y localizar páginas; no sustituye la lectura ni el contraste con el código 6.2.

## 2. Dos modelos que se deben conocer por separado

### 2.1 Modelo lógico

El modelo lógico expresa el dominio y su comportamiento:

- Clases estáticas y dinámicas, clases incorporadas, clasificación, herencia y extensiones.
- Propiedades de datos persistentes y locales, propiedades calculadas, abstractas, agregadas y materializadas.
- Acciones, operadores, expresiones y composición declarativa/imperativa.
- Restricciones y validaciones declarativas.
- Eventos simples y calculados, disparadores por cambios, ciclo de vida de datos y comportamiento local/global.
- Objetos, grupos de objetos, pertenencia, relaciones, agregaciones y jerarquías.
- Espacios de nombres, módulos, dependencias \`REQUIRE\`, extensiones y metaprogramación.

El lenguaje no debe entenderse como una capa de formularios que escribe directamente en tablas. La lógica se declara mediante clases, propiedades, acciones, eventos y restricciones; la plataforma determina su ejecución y representación física.

### 2.2 Modelo físico y de ejecución

El modelo físico determina cómo se desarrolla, carga y ejecuta la lógica:

- Tablas, campos, índices, materializaciones y estructuras físicas derivadas.
- Generación y actualización del esquema de base de datos.
- Motor de ejecución de servidor, sesiones de cambio y transacciones.
- Cliente web, cliente de escritorio y comunicación cliente-servidor.
- Configuración, conexión de base de datos, parámetros de arranque, recursos y despliegue.
- Logs, monitor de procesos, profiler, scheduler y herramientas de mantenimiento.

La definición lógica y su implementación física deben auditarse juntas; una propiedad calculada, una materialización y una tabla persistente no son conceptos equivalentes.

## 3. Lenguaje y lógica de dominio

### 3.1 Clases y objetos

La documentación incluye clases incorporadas y clases definidas por el usuario; herencia, extensión de clases, clasificación con \`IS\`/\`AS\`, identificación de objetos y objetos estáticos. La auditoría debe registrar:

- clase base y clases extendidas;
- compatibilidad de herencia y restricciones de la plataforma;
- clave/ID, unicidad y ciclo de vida;
- referencias entre clases y comportamiento al eliminar;
- pertenencia de propiedades y acciones;
- tablas físicas y estrategias de almacenamiento.

### 3.2 Propiedades

Las familias documentadas incluyen:

- \`DATA\`: propiedades almacenadas, persistentes o locales.
- Propiedades calculadas y composición mediante \`JOIN\`.
- \`ABSTRACT\` y extensiones de propiedades.
- Selección con \`IF\`, \`CASE\`, \`MULTI\`, \`OVERRIDE\` y \`EXCLUSIVE\`.
- Agregación con \`GROUP\`, \`AGGR\`, \`SUM\`, \`MAX\`, \`MIN\` y operaciones relacionadas.
- Conjuntos/estructuras con \`STRUCT\`, \`PARTITION\`, \`UNGROUP\`, recursividad y operadores de objetos.
- Comparación, conversión de tipos, operaciones aritméticas y de texto.
- Índices, propiedades sobre tablas y materializaciones.

La ficha por propiedad debe decir si persiste, cómo se calcula, de qué clases/propiedades depende, cuándo se recalcula, si admite edición, qué índice/materialización la respalda y qué efecto tiene una modificación.

### 3.3 Acciones y operadores

La documentación agrupa operadores dependientes e independientes del contexto. La lista documentada incluye, entre otros:

- Control del flujo: \`IF\`, \`CASE\`, \`FOR\`, \`WHILE\`, \`BREAK\`, \`CONTINUE\`, \`RETURN\`, \`TRY\`.
- Cambios: \`CHANGE\`, \`DELETE\`, \`CHANGECLASS\`, \`APPLY\`, \`CANCEL\`.
- Sesiones y ejecución: \`NEWSESSION\`, \`NESTEDSESSION\`, \`NEWCONNECTION\`, \`NEWEXECUTOR\`, \`NEWTHREAD\`.
- Interacción: \`SHOW\`, \`DIALOG\`, \`INPUT\`, \`REQUEST\`, \`MESSAGE\`, \`ASK\`, \`ACTIVATE\`.
- Entrada/salida: \`IMPORT\`, \`EXPORT\`, \`READ\`, \`WRITE\`, \`PRINT\`, \`EMAIL\`.
- Integración y evaluación: \`EXEC\`, \`EVAL\`, \`EXTERNAL\`, \`INTERNAL\`, \`FORMULA\`.
- Construcción/selección de estructuras y objetos: \`NEW\`, \`SEEK\`, \`EXPAND\`, \`COLLAPSE\`, \`MULTI\`.

No alcanza con listar operadores. Para cada uno que se use en MyCompany/Rubrova hay que documentar parámetros, contexto, permisos, resultado, efectos transaccionales, errores, aislamiento y límites de concurrencia.

### 3.4 Restricciones, eventos y estado

La documentación de plataforma diferencia:
- restricciones declarativas, evaluadas para garantizar reglas de datos;
- eventos sincrónicos y asincrónicos;
- eventos locales a la sesión y globales;
- eventos simples y calculados;
- manejadores que pueden cancelar cambios o ejecutarse en segundo plano;
- operadores de cambio que observan valores previos y cambios dentro de una sesión.

Esta semántica es crítica para entender cuándo se valida un documento, cuándo se recalcula una propiedad, cuándo se dispara un efecto lateral y qué ve cada usuario.

### 3.5 Sesiones y transacciones

Se deben analizar como un subsistema propio:
- sesión de cambios y valores locales;
- aplicar con \`APPLY\`;
- cancelar con \`CANCEL\`;
- \`NEWSESSION\` y \`NESTEDSESSION\`;
- valor previo \`PREV\`;
- operadores \`SET\`, \`CHANGED\` y variantes;
- interacción entre eventos locales/globales y transacciones del motor;
- acciones ejecutadas en hilo, executor, conexión o sesión nueva.

La documentación de eventos explica que un evento global asincrónico puede ejecutarse después de que la sesión haya terminado y que los manejadores pueden agrupar cambios. Eso requiere validar consistencia eventual, no asumir que todos los efectos ocurren de inmediato.

## 4. Formularios, navegación e interfaz

### 4.1 Formularios

Un formulario separa su estructura de sus vistas:

- Objetos y grupos de objetos.
- Propiedades, acciones y grupos de propiedades/acciones.
- Filtros, ordenamientos, relaciones y visibilidad.
- Grupos, pestañas, disposición, anchos, alturas y alineación.
- Eventos y cambios interactivos.
- Vistas interactivas y estáticas.
- Vistas de impresión/reporte y diseños correspondientes.
- Componentes gráficos, pivot, árboles y estructuras visuales.

El formulario no define por sí solo una función de negocio; debe mapearse a la acción y a las propiedades que representa.

### 4.2 Navegador

El navegador agrupa:
- carpetas;
- acciones invocables sin argumentos;
- formularios;
- organización de secciones, orden, visibilidad y ventanas.

Se debe contrastar cada elemento de navegación con permisos, roles, formularios de inicio y contexto del usuario.

### 4.3 Clientes

El repositorio contiene módulos separados para cliente web y cliente de escritorio. La auditoría debe identificar:
- diferencias funcionales y visuales;
- componentes y extensiones JavaScript;
- carga de archivos, impresión, ventanas, diálogos y eventos;
- conectividad y reconexión;
- comportamiento ante pérdida de sesión/red;
- compatibilidad real con navegador y escritorio.

No debe afirmarse que una función funciona en ambos clientes sin probarla.

## 5. Persistencia, SQL y rendimiento

Áreas documentadas:
- clases/propiedades y su representación en tablas;
- nombres de tablas y campos, tablas predeterminadas y completas;
- índices generados y declarados;
- materializaciones y dependencias;
- generación y mantenimiento del esquema;
- fórmulas y operaciones traducidas a SQL;
- conexión a base de datos y parámetros;
- consultas de diagnóstico y operaciones administrativas.

Hay que identificar qué hace el motor automáticamente y qué requiere declaración o intervención. Para cada cálculo grande se debe medir si usa SQL, materialización, índice o ejecución Java y documentar los riesgos de bloqueo, costo y memoria.

## 6. Integración y acceso externo

La documentación separa:
- acceso desde sistemas externos;
- acceso desde el propio sistema hacia servicios externos;
- operadores \`EXTERNAL\`, \`INTERNAL\` y \`FORMULA\`;
- interacción HTTP;
- importación/exportación y formatos externos;
- archivos, correo, JSON y consultas SQL;
- llamadas \`EXEC\`/\`EVAL\` y comunicación cliente-servidor.

La auditoría debe inventariar el contrato de cada API que exponga Rubrova: ruta, método, autenticación, autorización, entrada, salida, idempotencia, límites, errores, trazabilidad y manejo de secretos. Una marca \`@@api\` en fuente no equivale automáticamente a un endpoint seguro o documentado.

## 7. Seguridad, identidad y administración

La plataforma trae capacidades relacionadas con:
- usuarios y autenticación;
- roles, membresías y permisos;
- acceso a elementos de navegación;
- permisos sobre propiedades y acciones;
- configuración de formularios iniciales y comportamiento de interfaz por rol;
- políticas de seguridad;
- configuración del servidor, parámetros del sistema y recursos;
- administración de scheduler y ejecución de tareas;
- logs, historial, eventos de sistema, monitor de procesos y profiler;
- copias de seguridad y restauración.

Los módulos LSF activos de Rubrova que ya fueron identificados incluyen \`Authentication\`, \`Security\`, \`Scheduler\`, \`Backup\`, \`ProcessMonitor\`, \`Service\`, \`System\`, \`SystemEvents\`, \`Reflection\`, \`Eval\`, \`Integration\`, \`Time\`, \`Numerator\` y \`DefaultData\`. El manual de ingeniería documenta la primera lectura de esos módulos y sus riesgos; todavía faltan pruebas negativas por rol y validaciones operativas.

Herramientas de alto impacto como \`Eval\`, reinicio, vacuum, restauración, heap dump, cancelación de procesos o cambios de permisos deben quedar reservadas a perfiles y procedimientos controlados. No se deben exponer como acciones normales de un usuario de negocio.

## 8. Desarrollo, despliegue y operación

La documentación del snapshot incluye:
- desarrollo con IDE y plugin;
- proyectos Maven y estructura de módulos;
- compilación, empaquetado, instalación automática y manual;
- instalación del servidor y cliente web/de escritorio;
- parámetros de inicio y conexión;
- actualizaciones de aplicación y clientes;
- migraciones y cambios de nombres/estructura;
- internacionalización y formatos regionales;
- logs de servidor/cliente;
- scheduler, monitor y profiler;
- mantenimiento de índices, tablas y materializaciones.

**Pendiente importante:** comparar todo procedimiento con el commit exacto de 6.2. Las páginas de instalación del bundle incluyen referencias de descarga y ejemplos 6.1; se debe producir un procedimiento Rubrova comprobado para Java, PostgreSQL, Tomcat, servidor, cliente web y desktop. No se deben ejecutar instrucciones de producción tomadas de documentación genérica sin esa reconciliación.

## 9. Módulos de plataforma fuera de la composición de Rubrova

El cierre estático de \`RubrovaCustom\` incluye 24 módulos LSF de la plataforma. Quedan 25 módulos de plataforma fuera del cierre, que hay que revisar antes de descartarlos o incorporarlos:

| Grupo | Módulos |
|---|---|
| Datos, archivos y utilidades | \`Com\`, \`Document\`, \`Excel\`, \`Historizable\`, \`I18n\`, \`Image\`, \`OpenCV\`, \`Printer\`, \`ProcessUtils\`, \`SQLUtils\`, \`Schedule\`, \`UserEvents\`, \`WebSocket\`, \`Word\` |
| Rendimiento e infraestructura | \`Profiler\`, \`RabbitMQ\` |
| Componentes visuales | \`Carousel\`, \`Chart\`, \`JKanban\` |
| Mensajería | \`Messenger\`, \`Skype\`, \`Slack\`, \`Telegram\`, \`Viber\`, \`Whatsapp\` |

La agrupación anterior es de orientación por nombres y código fuente inicial, no una ficha funcional completa. Hay que revisar cada módulo, sus dependencias Java/externas, configuración, credenciales, licencias, permisos, exposición de red y casos de uso. Algunos son conectores que necesitan un servicio externo; otros sólo cargan una biblioteca de cliente o proveen contratos abstractos.

## 10. Inventario de documentación

El índice completo debe incluir, como mínimo, las 342 páginas Markdown y 89 imágenes de cada idioma de plataforma, además de los 347 documentos Markdown y 113 imágenes de MyCompany. Para cada página debe quedar registrado:
- idioma y ruta;
- título y encabezados;
- dominio/capacidad;
- módulos LSF a los que se refiere;
- estado de lectura y fecha;
- diferencias con la fuente 6.2;
- afirmaciones que necesitan confirmación en fuente o runtime.

El índice por sí solo no es análisis funcional. Sirve para comprobar que no haya documentación sin asignar y para que cada módulo tenga asociado el material que lo explica.

## 11. Estado de evidencia

| Área | Fuente/documentación identificada | Lectura detallada | Prueba en runtime |
|---|---|---|---|
| Lenguaje, clases, propiedades y acciones | Sí | Parcial | Pendiente |
| Eventos, restricciones y sesiones | Sí | Parcial | Pendiente |
| Persistencia, tablas, índices y materializaciones | Sí | Parcial | Pendiente |
| Formularios, vistas y navegación | Sí | Parcial | Pendiente |
| Seguridad y autenticación | Sí | Parcial en módulos activos | Pendiente |
| API, SQL, HTTP, importación y exportación | Sí | Parcial | Pendiente |
| Clientes web/escritorio | Código y páginas identificados | Parcial | Pendiente |
| Desarrollo, instalación y despliegue 6.2 | Sí, con referencias de documentación a revisar | Parcial | Build aprobado; smoke pendiente |
| Operación y diagnóstico | Sí | Parcial en módulos activos | Pendiente |

## 12. Condición de cierre

La plataforma no se considera relevada hasta que:
- las páginas de documentación estén indexadas y asociadas a capacidades;
- cada mecanismo del lenguaje tenga su ficha y ejemplos relevantes;
- los módulos LSF y paquetes Java estén asociados a sus funciones y dependencias;
- se conozca qué módulos están cargados, cuáles son opcionales y cuáles requieren servicios externos;
- la seguridad, las transacciones, los eventos, el cliente y las herramientas operativas tengan pruebas representativas;
- los ejemplos/documentos heredados 6.1 estén reconciliados con la fuente 6.2;
- las integraciones y APIs estén documentadas con contratos y límites;
- se haya verificado el arranque y la operación de los componentes en el runtime de Rubrova.

**Estado actual: incompleto.** Este mapa es una primera clasificación de la superficie disponible. No habilita nuevas funcionalidades ni el avance a otra fase.
