# MyCompany 6.2 — mapa funcional de CRM y gestión de leads

**Estado: 24 fuentes LSF inventariadas; ciclo del lead, estados, Kanban, llamadas/correos, marketing y conversión a documentos revisados. Pruebas de runtime e integraciones externas pendientes.**

## 1. Inventario de módulos

| Área | Módulos |
|---|---|
| Raíz/configuración | `CRM`, `CRMSettings` |
| Lead y ciclo de vida | `Lead`, `LeadInitial`, `LeadStatus`, `LeadType`, `LeadPriority`, `LeadTag`, `LeadLost` |
| Datos relacionados | `LeadCustomer`, `LeadPartner`, `LeadItem` |
| Comunicaciones | `LeadCall`, `LeadEmail` |
| Marketing | `LeadMarketing`, `Campaign`, `Medium`, `Source`, `MarketingInitial` |
| Tablero y reportes | `LeadKanban`, `LeadReport`, `LeadReportMarketing` |
| Conversión a documentos | `LeadSalesOrder`, `LeadInvoice` |

El módulo raíz `CRM` compone leads, estados/tipos, llamadas, correos, clientes, artículos, Kanban, informes, marketing y creación de pedidos/facturas.

## 2. Modelo del lead

Fuente: `crm/leads/Lead.lsf`.

El lead guarda:
- ID y fecha/hora de creación;
- nombre y descripción enriquecida;
- cliente/socio asociado;
- responsable comercial (empleado);
- tipo y estado;
- prioridad y etiquetas;
- fecha de cierre prevista;
- ingreso esperado y probabilidad;
- teléfono, correo, dirección, ciudad, provincia/estado, código postal;
- persona de contacto, nombre de entidad legal, puesto y sitio web.

Al crear el lead:
- se completa fecha/hora;
- se propone responsable desde el usuario actual si es empleado;
- se propone tipo predeterminado;
- se asigna primer estado aplicable;
- se conserva el historial, archivos, comentarios y actividades mediante macros comunes.

La búsqueda de leads puede localizarse por teléfono/correo. Los datos pueden estar parcialmente completos; convertirlos a socio exige revisar duplicados y calidad.

## 3. Tipos, estados y workflow

### 3.1 Estados

`LeadStatus` define nombre, ID, orden y marca de cierre. Los estados abiertos y cerrados se diferencian mediante esa marca. El orden controla el orden visual y la secuencia del tablero.

### 3.2 Tipos de lead

`LeadType` mantiene nombre/ID y una matriz de estados permitidos. Si un tipo no declara una matriz propia, la fuente permite usar la lista general. Si se cambia el tipo de un lead y el estado actual deja de ser permitido, el código vuelve al primer estado válido. La restricción impide guardar una transición no permitida.

### 3.3 Perdido

`LeadLost` configura:
- estado que representa lead perdido;
- motivos de pérdida;
- acción para marcarlo como perdido y registrar el motivo.

Se puede cerrar un lead por otros estados además de perdido. Debe conservarse el motivo y la historia de cambios.

### 3.4 Prioridades y etiquetas

`LeadPriority` usa una prioridad con color semántico; `LeadTag` permite tags con color. Se usan en formularios, listados y Kanban.

**Pendiente:** probar transiciones no válidas, cambios de tipo, estados cerrados, usuario sin permiso, motivos obligatorios, reapertura y reasignación.

## 4. Kanban y seguimiento

Fuente: `crm/leads/LeadKanban.lsf`.

El Kanban:
- genera columnas a partir de los estados no cerrados permitidos para el filtro/tipo;
- muestra leads con nombre, estado, tipo, cliente, ingreso esperado, prioridad, tags, responsable y fecha prevista;
- permite cambiar el estado entre opciones válidas;
- permite ordenar las tarjetas por usuario (el orden se guarda por usuario);
- incorpora búsqueda y filtros del listado de leads;
- utiliza recursos web propios para la interacción visual.

El estado visual no sustituye a las reglas del documento; el cambio se valida en LSF contra la matriz de estados del tipo.

**Pendiente:** concurrencia entre usuarios, arrastrar tarjetas cuando cambian permisos/estado, orden personalizado, actualización en tiempo real, accesibilidad, navegación móvil y consistencia del tablero con los filtros del listado.

## 5. Cliente y artículos relacionados

- `LeadCustomer` permite crear una entidad legal desde el lead copiando nombre, teléfono, correo y otros datos básicos; luego enlaza el socio al lead.
- `LeadPartner` permite crear un lead desde la ficha de un socio y lista los leads asociados.
- `LeadItem` enlaza un artículo/servicio con el lead y puede proponer el nombre del lead desde el artículo si está vacío.

La conversión a socio debe revisar duplicados por CUIT, nombre, correo, teléfono y razón social. El importador o creador no demuestra por sí mismo la validez fiscal argentina de esa entidad.

## 6. Llamadas y correo

### 6.1 Llamadas

`LeadCall` utiliza el modelo común `Call`:
- puede localizar el lead abierto que coincida con el teléfono entrante;
- vincula la llamada con el socio/lead;
- permite crear lead desde llamada sin vincular o asociar llamada a un lead;
- copia teléfono, responsable y datos de contexto;
- muestra una bandeja de llamadas por procesar del empleado actual;
- permite marcar llamada ignorada o lista, solicitar grabación si el proveedor lo admite y abrir el lead asociado.

El módulo `Call` es un contrato común con puntos abstractos; la telefonía concreta depende de un proveedor (por ejemplo, Zadarma/Mango en regionalizaciones). La documentación de MyCompany describe Zadarma con API key/secret, webhook, PBX, internos, eventos de llamada y grabaciones.

**Pendiente:** deduplicación de webhooks, correlación de llamadas, llamadas sin identificador, registros repetidos, fallos de PBX, permisos de grabación, privacidad y retención.

### 6.2 Correo

`LeadEmail` amplía las utilidades de EmailTemplate/EmailUtils:
- compone asunto y cuerpo con datos del lead;
- genera link a la ficha del lead;
- permite enviar plantillas filtradas por tipo/estado;
- registra mensajes entrantes y permite asociarlos a un lead existente o crear uno;
- puede enviar notificaciones sobre comentarios al responsable comercial.

La cuenta de correo y el transporte dependen del subsistema Email y su configuración. No asumir que IMAP/SMTP/OAuth están listos por el solo hecho de tener el formulario.

**Pendiente:** autenticación, sincronización, adjuntos maliciosos, HTML, duplicados, privacidad y trazabilidad.

## 7. Marketing y atribución

`LeadMarketing` agrega al lead:
- campaña;
- medio;
- origen/fuente.

`Campaign`, `Medium` y `Source` son catálogos separados. `MarketingInitial` carga datos predeterminados cuando corresponde. Los reportes pueden agrupar leads, ingresos previstos y estados por campaña/medio/origen.

**Límite:** estos campos permiten atribución manual/configurable; no prueban por sí solos integración con Google Ads, Meta Ads, analítica web o formularios externos. Esa captura debe buscarse en APIs o conectores específicos.

## 8. Conversión a pedido o factura

### 8.1 Pedido de venta

`LeadSalesOrder`:
- configura un tipo de pedido para la operación de CRM;
- crea un pedido y lo enlaza con el lead;
- copia el cliente y datos comerciales;
- puede generar líneas desde el artículo y el ingreso esperado;
- permite abrir el pedido y regresar al lead;
- muestra en el lead todos los pedidos vinculados.

El pedido luego sigue el circuito nativo de ventas: estados, stock, despacho, impuestos, facturación, deuda y cobro.

### 8.2 Factura

`LeadInvoice`:
- configura tipo de factura para la operación de CRM;
- crea una factura enlazada al lead;
- copia el cliente y datos previstos;
- muestra facturas asociadas al lead.

La factura luego sigue el modelo general de facturación, deuda, pagos e impuestos. No es correcto considerar que el lead se transforma en una factura final sin ejecutar y validar esos procesos.

### 8.3 Trazabilidad

La relación bidireccional lead ↔ pedido/factura permite:
- abrir el lead desde el documento;
- consultar documentos creados desde el lead;
- mantener la procedencia comercial.

**Pendiente:** conversiones múltiples, crear pedido y factura sobre el mismo lead, importe esperado, artículos sin precio, datos fiscales faltantes, cambio de cliente, cancelar documento, duplicados e idempotencia.

## 9. Informes

`LeadReport` es un pivot con:
- ID, nombre, estado, fecha de alta;
- probabilidad y cierre previsto;
- cliente y responsable;
- prioridad/tags;
- teléfono/correo;
- descripción y datos de contacto;
- importe esperado.

`LeadReportMarketing` agrega campaña, medio y origen. El manual describe filtros por intervalo de fecha y agrupaciones por fecha de creación, fecha de cierre prevista, responsable, estado y campaña.

El importe esperado es un pronóstico comercial, no ingreso contable ni facturación real.

## 10. Seguridad, calidad de datos y adecuación local

- Permisos deben revisarse sobre lectura/edición de lead, información de contacto, llamadas, grabaciones, correos y conversiones.
- Los datos personales y la ubicación/contactos requieren política de privacidad, retención y acceso.
- Debe impedirse que un usuario vea leads de otros equipos cuando la política de negocio requiera segmentación; el responsable comercial no debe confundirse automáticamente con permiso de seguridad.
- La entidad legal creada desde un lead no demuestra CUIT, condición fiscal, domicilio fiscal, IIBB ni validación ARCA.
- Los reportes de pronóstico necesitan distinguir ingreso previsto, pedido confirmado, factura emitida y dinero cobrado.

## 11. Pruebas obligatorias

| Escenario | Qué demostrar |
|---|---|
| Alta y edición | Defaults, responsable, datos opcionales, historial y permisos |
| Tipos/estados | Matriz de transiciones, cerrado, perdido, reapertura y cambio de tipo |
| Kanban | Arrastrar entre estados válidos/no válidos, orden por usuario y concurrencia |
| Cliente | Crear entidad desde lead, duplicados, titularidad y datos faltantes |
| Llamadas | Llamada entrante/saliente, webhook duplicado, vincular/crear/ignorar y grabación |
| Correo | Enviar, recibir, adjuntar, asociar, crear lead y fallos de cuenta |
| Marketing | Campaña/medio/origen y atribución de informes |
| Pedido/factura | Conversión repetida, artículo, precio, importe, cliente, cancelación y enlace |
| Reportes | Conciliar cantidad de leads, estados, ingresos previstos y documentos reales |

## 12. Estado

Las 24 fuentes CRM están inventariadas. El primer análisis de código identificó el ciclo del lead, estados por tipo, Kanban, datos de contacto, responsable, etiquetas/prioridades, llamadas, correo, marketing, reportes y conversión a pedido/factura.

**No está cerrado:** faltan pruebas de runtime, conectores externos, permisos detallados, APIs, integraciones de marketing y conciliación entre pronóstico, pedidos, facturas y cobros. La puerta general sigue ABIERTA.
