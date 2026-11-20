# Shortlist de componentes reutilizables

**Revisión:** 20 de noviembre de 2026  
**Estado:** investigación documental y de repositorios. Ninguno de estos componentes está integrado ni aprobado para producción.

## Objetivo

Esta lista complementa la evaluación de ERP/POS. Busca piezas concretas que puedan incorporarse dentro de un servicio Rubrova o funcionar como una aplicación de dominio separada, sin reconstruir desde cero tareas técnicas ya resueltas.

La selección prioriza código fuente accesible, licencia identificable, mantenimiento observable, función acotada y operación local. La existencia de un README, una API o una demo no equivale a compatibilidad probada.

**Regla arquitectónica:** una biblioteca se integra dentro del servicio que la necesita; una aplicación se evalúa como unidad de dominio aislada. Ninguna pieza puede crear una segunda autoridad para ventas, pagos, caja, inventario, fiscalidad o contabilidad.

## 1. Calidad e importación de datos

| Proyecto | Versión / licencia observada | Qué aporta | Límite y uso propuesto |
|---|---|---|---|
| [OpenRefine](https://github.com/OpenRefine/OpenRefine) | 3.10.1; BSD-3-Clause | Limpieza local de datos, filtros, agrupamiento de valores similares, reconciliación y transformaciones reversibles. | Herramienta asistida para preparar migraciones y revisar catálogos grandes; no es el importador transaccional ni fusiona registros sin aprobación. |
| [Frictionless](https://github.com/frictionlessdata/frictionless-py) | 5.21.0; MIT | Leer, describir y validar CSV, XLS, JSON y otros formatos; detectar errores por fila/campo y transformar tablas. | Biblioteca/CLI para validación estructural; las reglas comerciales y contables siguen siendo propias del dominio. |
| [RapidFuzz](https://github.com/rapidfuzz/RapidFuzz) | 3.14.6; MIT | Comparación aproximada de cadenas y métricas como Levenshtein/Jaro-Winkler, con implementaciones optimizadas. | Sugiere coincidencias entre nombres, marcas, SKU y proveedores. Una similitud no demuestra que dos entidades sean la misma. |
| [python-stdnum](https://github.com/arthurdejong/python-stdnum) | 2.2; LGPL-2.1 | Parseo y validación de identificadores; incluye formatos argentinos CUIT, CBU y DNI. | Valida estructura y dígitos cuando corresponda. No consulta el padrón ARCA ni confirma vigencia o titularidad bancaria. |
| [Pint](https://github.com/hgrecco/pint) | 0.26; BSD | Unidades dimensionales y conversiones entre unidades explícitamente identificadas. | Útil para kg/g, litros/ml, metros/unidades. No debe inferir una unidad ausente ni convertir valores ambiguos por intuición. |
| [libpostal](https://github.com/openvenues/libpostal) | MIT; biblioteca C | Análisis y normalización de direcciones internacionales mediante NLP y datos abiertos. | Candidato posterior para direcciones de clientes/envíos. Exige probar calles, alturas, barrios, localidades y códigos postales argentinos; no es geocodificador ni validación postal oficial. |

**Flujo recomendado de importación:** conservar el archivo original y su hash; detectar formato, codificación y esquema; mostrar vista previa con errores; sugerir equivalencias con RapidFuzz/OpenRefine sin fusionar automáticamente; validar CUIT/CBU/DNI y unidades sólo cuando estén explícitas; ejecutar reglas de dominio; generar un lote idempotente con filas aceptadas, rechazadas y pendientes.

**Prioridad: muy alta.** OpenRefine puede usarse primero para preparar datos de prueba. Frictionless, RapidFuzz, python-stdnum y Pint se prueban como bibliotecas dentro del servicio importador que finalmente se elija.

## 2. Facturas, documentos y archivo

| Proyecto | Versión / licencia observada | Qué aporta | Límite y uso propuesto |
|---|---|---|---|
| [OCRmyPDF](https://github.com/ocrmypdf/OCRmyPDF) | 17.14.2; MPL-2.0 | Añade una capa de texto OCR a PDF escaneados y los vuelve buscables. | Preprocesamiento; no interpreta por sí solo CUIT, importes ni conceptos. |
| [Docling](https://github.com/docling-project/docling) | 2.151.1; MIT | Analiza estructura documental y tablas de PDF y otros formatos ofimáticos con salida estructurada. | Candidato para documentos complejos; medir memoria, tiempo y precisión con muestras anonimizadas. |
| [invoice2data](https://github.com/invoice-x/invoice2data) | 1.0.1; MIT | Extrae campos de facturas PDF mediante plantillas configurables por proveedor y genera datos estructurados. | Útil para proveedores y diseños conocidos si preparamos plantillas argentinas; requiere pruebas por proveedor y revisión humana. |
| [Paperless-ngx](https://github.com/paperless-ngx/paperless-ngx) | 3.5.1; GPL-3.0 | Archivo documental autohospedado, OCR, clasificación, búsqueda, ingestión desde carpetas/correo y API. | Posible servicio separado para conservar/localizar originales. No es autoridad del estado de una factura ni del asiento contable. |

**Pipeline recomendado:** guardar el original inmutable con hash; aplicar OCR sólo cuando haga falta; extraer estructura/tablas con Docling o invoice2data; conservar valor original, valor propuesto, evidencia y confianza; contrastar CUIT, número, fecha, moneda e importes; pedir revisión humana antes de generar cuenta a pagar, pago, recepción o asiento; archivar el original en un servicio documental independiente.

**Prioridad: media-alta.** Empezar por facturas de proveedores recurrentes y remitos. No hacer OCR indiscriminadamente ni automatizar pagos.

## 3. Logística y transporte multioperador

### Karrio — candidato para reutilizar el motor multi-carrier

Repositorio: [karrioapi/karrio](https://github.com/karrioapi/karrio)  
Documentación: https://karrio.io/docs  
Licencia: el archivo raíz declara LGPL-3.0 para contenido fuera de `ee/`; el directorio Enterprise tiene licencia separada y los terceros conservan sus propias licencias. La API de GitHub marca la licencia global como NOASSERTION, por lo que se deben revisar los archivos/paquetes realmente incorporados.

Karrio aporta una API autohospedada para cotización, etiquetas, conexiones con transportistas y tracking. El repositorio incluye conectores comunitarios para DHL, FedEx, UPS, USPS, Canada Post, DPD y otros.

**Hallazgo argentino:** al inspeccionar el árbol de conectores de la rama principal el 20/11/2026 no encontré conectores para Andreani, Correo Argentino PAQ.AR, OCA e-Pak ni Vía Cargo. No es una integración argentina lista para activar.

**Uso potencial:** reutilizar el modelo normalizado, servidor y SDK, y desarrollar adaptadores argentinos sólo después de obtener documentación oficial, credenciales de QA y pruebas de cotización, etiqueta, tracking, cancelación, errores y webhooks. El pedido y el inventario conservan sus autoridades fuera de Karrio.

| Proyecto | Versión / licencia observada | Evaluación |
|---|---|---|
| [OpenBoxes](https://github.com/openboxes/openboxes) | EPL-1.0; activo en noviembre de 2026 | WMS orientado a cadenas sanitarias. Aporta ideas de recepción, movimientos, lotes y despacho; no asumir que cubra retail, pesables o POS. |
| [Simple WMS](https://github.com/q7-technology/simple-wms) | MIT; creado en septiembre de 2026, sin release publicada; último push 15/10/2026 | Ledger append-only, tareas de depósito, scanner PWA, SSCC y API. Referencia prometedora pero de madurez pública baja; no autoridad de stock. |
| [Open TMS](https://github.com/phrogdriver/open_tms) | MIT; sin release estable, última actividad observada en julio de 2026 | Proyecto temprano para transporte; referencia de dominio, no base productiva. |

**Prioridad:** Karrio media-alta si hay APIs argentinas y QA disponibles; OpenBoxes como referencia WMS; Simple WMS y Open TMS en vigilancia.

## 4. Hardware, impresión y pagos

### QZ Tray — puente local de dispositivos

Repositorio: [qzind/tray](https://github.com/qzind/tray)  
Release observada: `v2.3.0` (11/09/2026).  
Licencia del código fuente según `LICENSE.txt`: LGPL-2.1; ejemplos de API public domain y componentes de terceros con licencias propias.

QZ Tray conecta aplicaciones web con impresoras y dispositivos locales; documenta ESC/POS, USB, serie, HID, sockets y archivos. Ofrece paquetes para Windows, macOS y Linux.

**Condición:** imprimir silenciosamente requiere firmar las solicitudes; la documentación contempla adquirir un certificado de QZ o implementar una autoridad raíz propia. Esto exige proteger y distribuir correctamente las claves. Compararlo en laboratorio con [pos-toolkit](https://github.com/narisolutions/pos-toolkit). Probar impresoras, cajón, balanza y lector concretos.

### Mercado Pago — SDK oficial

Repositorio: [mercadopago/sdk-nodejs](https://github.com/mercadopago/sdk-nodejs)  
Versión observada: 3.6.2 (11/11/2026). Licencia MIT; Node.js >=18.

SDK oficial para consumir APIs de Mercado Pago desde Node.js/TypeScript. **Límite:** no demuestra por sí mismo la integración con un terminal Point físico. Emparejamiento, estados presenciales, voucher, timeouts y webhooks requieren prueba con API/dispositivo concretos. Todo cobro necesita referencia idempotente y estado incierto recuperable.

## 5. Fiscalidad argentina: dos SDK para comparar

### [LaPyme/facturas](https://github.com/LaPyme/facturas)

- Release observada: `facturas@0.28.0`, publicada el 17/11/2026.
- Licencia del paquete: Apache-2.0; Node.js >=22, ESM; estado pre-1.0.
- Facturación electrónica, notas de crédito/débito, consultas de padrón, CLI y documentación en español.
- Estados `authorized`, `rejected`, `indeterminate` y `conflict`, claves idempotentes y recuperación/conciliación del número reservado.

### [ramiidv/arca-sdks](https://github.com/ramiidv/arca-sdks)

- Monorepo TypeScript MIT.
- Paquetes observados el 19/11/2026: `@ramiidv/arca-facturacion@7.1.0`, `@ramiidv/arca-common@0.10.2`, `@ramiidv/arca-padron@0.9.3` y `@ramiidv/arca-sire@0.7.4`.
- Node.js >=22.12, ESM; incluye pruebas unitarias, integración y homologación.

**Decisión:** no integrar ambos SDK como emisores simultáneos. Compararlos en homologación bajo el mismo contrato y elegir uno. Probar emisión, notas de crédito, concurrencia, respuesta perdida, estado incierto, recuperación y certificados. Rubrova conserva idempotencia de negocio, evidencia y conciliación; nunca reintentar una factura ciegamente.

## 6. Automatización y procesos durables

| Proyecto | Versión / licencia observada | Uso posible | Decisión |
|---|---|---|---|
| [Node-RED](https://github.com/node-red/node-red) | 5.0.10 (17/11/2026); Apache-2.0 | Automatizaciones visuales, dispositivos, webhooks y flujos periféricos. | Candidato para integraciones no transaccionales; sin acceso directo a ledgers ni autoridad para confirmar cobros/stock. |
| [Temporal](https://github.com/temporalio/temporal) | 1.32.2 (02/11/2026); MIT | Workflows durables, reintentos, esperas, compensaciones y recuperación. | Potente, pero añade servidor y operación. Diferir hasta que existan procesos largos entre servicios que lo justifiquen. |

## 7. Orden recomendado de pruebas

1. **Importación/calidad:** OpenRefine para limpieza asistida; Frictionless, RapidFuzz y python-stdnum con el dataset de artículos, clientes, proveedores y CUIT/CBU; Pint sólo para unidades explícitas.
2. **Fiscalidad:** comparar LaPyme/facturas y arca-sdks en homologación, con énfasis en estados inciertos, claves estables, recuperación y concurrencia.
3. **Hardware:** comparar QZ Tray y pos-toolkit con la misma matriz de impresoras, cajones, lectores y balanzas; medir instalación, firma y reinicio del puente.
4. **Documentos:** probar OCRmyPDF + Docling + invoice2data con facturas/remitos anonimizados. Paperless-ngx se evalúa aparte como archivo.
5. **Envíos:** evaluar Karrio sólo después de confirmar APIs y obtener credenciales QA de Andreani, Correo Argentino y OCA. Presupuestar conectores faltantes.
6. **Automatización:** Node-RED para procesos periféricos si ahorra trabajo; Temporal sólo con necesidad demostrada.

## 8. Sincronización y experiencia offline

### [PowerSync](https://github.com/powersync-ja/powersync-service)

- Release del servicio observada: `v1.29.1` (18/11/2026).
- Licencia del servicio y SDK JavaScript: Apache-2.0.
- Mantiene una base SQLite local en el dispositivo y sincroniza con un backend; documenta soporte para PostgreSQL y otros motores, con SDKs para web, móvil, escritorio y entornos headless.

**Valor para Rubrova:** puede evitar desarrollar desde cero el almacenamiento y la replicación de catálogos, vistas, tareas de picking, listas de precios o información de clientes en puestos y dispositivos que deban seguir consultando datos durante una desconexión.

**Límite crítico:** sincronizar cambios no equivale a resolver reglas transaccionales concurrentes. PowerSync no debe decidir quién consume la última unidad de stock ni confirmar offline una operación que necesita conocer el estado de otros puestos. Los comandos de venta, pago y movimiento deben llegar a su autoridad de dominio con clave idempotente, control de versión/CAS y resultado explícito; cuando no pueda validarse la operación, queda pendiente o usa una cuota local exclusiva previamente asignada.

**Recomendación:** prioridad media-alta para prototipar lectura offline y tareas no conflictivas. No adoptar como solución única de inventario offline.

## 9. Ecommerce y canales online

### [Spree](https://github.com/spree/spree)

- Release observada: `v6.0.5` (16/11/2026).
- Licencia: BSD-3-Clause.
- Plataforma headless con REST API, SDK TypeScript, panel administrativo y storefront Next.js. La documentación del proyecto describe catálogos por canal, listas de precios/volumen, grupos de clientes, empresas y casos B2B/mayoristas y marketplaces.

**Valor:** candidato sólido para acelerar tienda online, canal mayorista o marketplace sin construir storefront y checkout desde cero.

**Límite:** Spree conserva modelos propios de catálogos, órdenes, pagos y stock. Rubrova tendría que definir una sola autoridad para cada dato: por ejemplo, Spree puede gestionar carrito y checkout, pero las existencias vendibles, los costos y la disponibilidad real deben consultarse/reservarse contra el servicio o plataforma que Rubrova haya designado. Los pedidos externos se importan idempotentemente y se concilian.

### [Saleor](https://github.com/saleor/saleor)

- Release observada: `3.23.50` (17/11/2026).
- Licencia: BSD-3-Clause.
- Plataforma headless/API-only con GraphQL; maneja canales, monedas, precios, stock y webhooks, y se extiende mediante apps.

**Valor:** alternativa especialmente interesante si se prefiere una API GraphQL y una separación estricta entre backend de comercio y storefront.

**Decisión:** no probar Spree y Saleor en profundidad al mismo tiempo. Empezar por Spree por su encaje B2B/mayorista; mantener Saleor como alternativa si la evaluación favorece GraphQL o una experiencia más API-centric. Ninguno reemplaza el ERP ni el POS local.

## 10. Inventario técnico y fabricación

### [InvenTree](https://github.com/inventree/InvenTree)

- Licencia: MIT.
- Sistema de inventario de partes/componentes construido sobre Python/Django, con interfaz web, REST API y sistema de plugins.
- Su enfoque destaca trazabilidad de partes, ubicaciones, lotes/seriales y listas de materiales (BOM).

**Encaje:** puede ser útil para fabricación, armado, repuestos, componentes y depósitos técnicos; es menos adecuado como POS minorista o maestro universal de precios/ventas.

**Límite:** si se adopta como autoridad independiente de inventario de componentes, hay que delimitar qué artículos/depósitos posee. No debe coexistir con otro sistema que contabilice las mismas existencias. Evaluar sincronización de recepciones, consumos de producción, unidades de medida, mermas, costos, API, exportación y backup/restore.

### [OCA/manufacture](https://github.com/OCA/manufacture)

- Rama de referencia: `19.0`.
- El repositorio reúne addons de fabricación para Odoo. Un ejemplo inspeccionado es `mrp_multi_level` versión `19.0.1.0.5`, que agrega planificación multinivel y declara LGPL-3.0 en su manifiesto.
- El repositorio raíz declara AGPL-3.0, pero cada addon puede declarar una licencia diferente.

**Encaje:** biblioteca de módulos para extender fabricación, BOM y planificación si Odoo termina siendo la plataforma elegida. No es una aplicación independiente ni se puede trasladar directamente a Tryton, Frappe u otro ERP.

**Regla:** verificar el manifiesto y dependencias de cada addon individual. No asumir que toda la colección tiene la licencia del primer módulo inspeccionado.

## 11. Analítica y BI local

### [DuckDB](https://github.com/duckdb/duckdb)

- Release observada: `v2.0.0` (21/10/2026).
- Licencia: MIT.
- Motor analítico in-process: se ejecuta dentro del proceso, sin un servidor independiente, y consulta CSV, Parquet, JSON, Excel y otros datos locales/remotos.

**Valor:** adecuado para preparar reportes, consolidar datos por área de negocio, calcular rotación, márgenes, ABC/XYZ, GMROI y comparar períodos sobre datasets analíticos. Puede reducir la necesidad de desplegar un motor de base adicional sólo para informes.

**Límite:** no usarlo como base OLTP de ventas/stock ni como sustituto de la base transaccional de un ERP. Su función es analítica, con datos derivados y conciliados.

### [Apache Superset](https://github.com/apache/superset)

- Release observada: `6.1.0` (13/05/2026).
- Licencia: Apache-2.0.
- Aplicación de BI web para explorar datos, crear gráficos, dashboards y consultas sobre fuentes compatibles.

**Valor:** tablero de gestión, dashboards por negocio/sucursal/canal, inventario, ventas, compras y rentabilidad.

**Límite:** agrega servicios y operación, y los dashboards deben consultar un repositorio/modelo analítico de sólo lectura. No dar permisos de escritura a bases transaccionales ni exponer datos sensibles entre áreas.

**Recomendación:** DuckDB para la primera prueba analítica con datasets exportados; Superset sólo cuando la necesidad de paneles multiusuario justifique una aplicación BI dedicada. No adoptar ambos automáticamente como una pila indivisible.

## 12. Identidad, autenticación y observabilidad

| Proyecto | Versión / licencia observada | Uso potencial | Condición |
|---|---|---|---|
| [Keycloak](https://github.com/keycloak/keycloak) | 26.8.2; Apache-2.0 | Identidad central, OIDC/OAuth2, federación de usuarios y autenticación de aplicaciones/servicios. | Diferir si el ERP elegido ya resuelve bien usuarios y permisos. Evaluarlo cuando existan varias aplicaciones independientes o SSO real; su operación agrega infraestructura. |
| [OpenTelemetry Collector](https://github.com/open-telemetry/opentelemetry-collector) | 0.165.0; Apache-2.0 | Recibir y exportar trazas, métricas y logs de servicios. | Candidato transversal cuando haya más de una aplicación o proceso que necesite observabilidad común. |
| [Prometheus](https://github.com/prometheus/prometheus) | 3.16.0; Apache-2.0 | Recolección y consulta de métricas de servicios, equipos y procesos. | Usar para disponibilidad, latencia, colas, sincronización y estado de backups. |
| [Grafana](https://github.com/grafana/grafana) | 13.3.1; AGPL-3.0 | Dashboards operativos y exploración de métricas/logs/trazas. | Revisar la licencia AGPL y usar sólo cuando los paneles operativos justifiquen el servicio adicional. |

**Estrategia:** no instalar Keycloak, Prometheus, Grafana y Collector desde el primer prototipo. Primero comprobar el sistema de identidad y logs nativo de la plataforma. Adoptar una capa común sólo cuando haya varias unidades operativas y métricas que necesitemos correlacionar.

## 13. Backups y restauración

### [pgBackRest](https://github.com/pgbackrest/pgbackrest)

- Release observada: `2.60.1` (16/11/2026).
- Licencia: MIT.
- Solución específica para PostgreSQL: backups completos/diferenciales/incrementales, archivo WAL, múltiples repositorios, retención, checksums y verificación en restauración.

**Uso:** candidato prioritario si los servicios elegidos utilizan PostgreSQL. Permite diseñar recuperación a un momento concreto (PITR) con sus respaldos y WAL; probarla en un servidor alternativo y no sobre la única instancia activa.

### [restic](https://github.com/restic/restic)

- Release observada: `0.20.0` (19/11/2026).
- Licencia: BSD-2-Clause.
- Backup/restauración multiplataforma para Windows, macOS y Linux, con repositorios cifrados y destinos locales, SFTP y almacenamiento compatible con S3, entre otros.

**Uso:** respaldar adjuntos, documentos, archivos de configuración exportables y otros ficheros. Para bases de datos activas, generar primero un backup consistente con la herramienta propia del motor; no copiar en caliente el directorio de datos esperando que restic lo convierta en un respaldo consistente.

### Alternativa: [Kopia](https://github.com/kopia/kopia)

- Release observada: `0.23.1` (16/06/2026).
- Licencia: Apache-2.0.
- Herramienta de backup de archivos con CLI y GUI, snapshots, cifrado, compresión y deduplicación.

Puede ser más cómoda para operación asistida con GUI; comparar con restic, no acumular ambas herramientas sin necesidad.

**Decisión recomendada:** elegir una herramienta de backup de archivos (restic o Kopia) y, si usamos PostgreSQL, pgBackRest para la base. El catálogo de Rubrova debe registrar cada backup, su hash, alcance, versión de esquema, retención, ubicación, prueba de restauración y manifiesto multi-servicio. Nunca considerar que un snapshot de VM sustituye un backup verificado de datos.

## 14. Puertas de aprobación

- Fijar release, commit y hash de artefactos.
- Revisar licencia raíz, subdirectorios/paquetes, dependencias y recursos.
- Comprobar actividad, responsables, seguridad y ruta de actualización.
- Probar Windows/macOS y hardware exacto cuando corresponda.
- Verificar APIs, permisos, exportación, backup, restauración y sustitución.
- Definir autoridad del dato y bloquear SQL cruzado.
- Medir esfuerzo de integración y mantenimiento; registrar parches propios.
- Someter cobros y fiscalidad a sandbox/homologación y conciliar estados inciertos.
- Conservar originales, hashes, logs y resultados de pruebas como evidencia.

## Estado real

- Se verificaron metadatos, releases, licencias declaradas y áreas del código de los repositorios enlazados al 20/11/2026.
- La inspección documental no equivale a una prueba funcional instalada.
- No se incorporó código externo a Rubrova.
- Ninguna biblioteca, SDK, WMS, TMS, archivo documental o plataforma fiscal de esta lista está aprobada para producción.
- El stack/lenguaje de servicios propios sigue abierto hasta que las pruebas justifiquen una decisión.
- Los proyectos de sincronización, ecommerce, BI, identidad, observabilidad y backup añadidos en esta revisión están documentados como candidatos; no se instalaron ni se eligieron.

Esta lista se complementa con el [Catálogo de código reutilizable](CODE_REUSE_CATALOG.md), la [Estrategia reuse-first](REUSE_FIRST_IMPLEMENTATION_STRATEGY.md) y la [Evaluación de plataformas](PLATFORM_EVALUATION.md).
