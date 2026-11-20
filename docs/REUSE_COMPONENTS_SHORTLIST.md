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

## 5. Fiscalidad argentina: localización Odoo y SDKs para comparar

### [LaPyme/facturas](https://github.com/LaPyme/facturas)

- Release observada: `facturas@0.28.0`, publicada el 17/11/2026.
- Licencia del paquete: Apache-2.0; Node.js >=22, ESM; estado pre-1.0.
- Facturación electrónica, notas de crédito/débito, consultas de padrón, CLI y documentación en español.
- Estados `authorized`, `rejected`, `indeterminate` y `conflict`, claves idempotentes y recuperación/conciliación del número reservado.

### Odoo — localización oficial argentina y facturación electrónica

Código público de la localización base: [odoo/odoo — addons/l10n_ar, rama 19.0](https://github.com/odoo/odoo/tree/19.0/addons/l10n_ar) y [rama 20.0](https://github.com/odoo/odoo/tree/20.0/addons/l10n_ar).

- El manifiesto público del addon `l10n_ar` declara versión `3.7` y licencia LGPL-3.
- Contiene plan de cuentas y plantillas por responsabilidad fiscal, impuestos/IVA, posiciones fiscales, tipos de documentos, identificaciones, códigos ARCA, monedas y unidades; también contempla CBU y datos fiscales de contacto.
- El manifiesto describe `l10n_ar` como la localización contable base y señala que algunos campos se usan posteriormente por el módulo de factura electrónica. **No debe confundirse con el emisor electrónico WSFE/CAE.**

La [documentación oficial de Odoo 19 para Argentina](https://www.odoo.com/documentation/19.0/es/applications/finance/fiscal_localizations/argentina.html) enumera por separado:
- `l10n_ar`: localización contable base.
- `l10n_ar_reports`: informes de Libro IVA y resumen de IVA.
- `l10n_ar_edi`: facturación electrónica por web service ARCA.
- `l10n_ar_website_sale`: campos fiscales y facturación electrónica en checkout online.
- `l10n_ar_withholding`: retenciones de pago.

**Disponibilidad de código:** en el repositorio público Community `odoo/odoo`, las rutas `addons/l10n_ar_edi` de las ramas 19.0 y 20.0 no existen; sí existe el código de `l10n_ar`. La documentación oficial acredita que el módulo EDI forma parte de la oferta Odoo, pero no demuestra que su código fuente esté disponible en el repositorio Community que estamos inspeccionando. Antes de reutilizarlo hay que obtener el código exacto, conocer su licencia y condiciones de acceso para la edición elegida y verificar si puede operarse en nuestra instalación privada.

### [leonobitech/l10n_ar_arca_edi](https://github.com/leonobitech/l10n_ar_arca_edi) — alternativa comunitaria Odoo 19

- Manifiesto observado: `19.0.1.0.0`, licencia AGPL-3.0 y estado explícito **Beta**.
- Tiene código para WSAA, WSFEv1/CAE, gestión de certificados y entornos de homologación/producción; el repositorio incluye tests para facturas y WSFE.
- Depende de `l10n_ar` y `account_edi`, y de `cryptography`, `zeep` y `lxml`.
- Última actividad observada: 17/03/2026; fijar el commit y revisar el mantenimiento antes de instalar.

**Decisión:** candidato real para una prueba aislada sobre Odoo 19 Community, no módulo aprobado para producción. Contrastar CAE, facturas A/B/C/E, notas de crédito/débito, certificados, errores, numeración concurrente, timeout/estado incierto, retenciones, RG vigentes y homologación. La etiqueta Beta y la antigüedad del último commit obligan a validar normativa y compatibilidad actual antes de confiarle emisión fiscal.

### Estado de OCA Argentina

La rama [OCA/l10n-argentina 19.0](https://github.com/OCA/l10n-argentina/tree/19.0) tiene raíz AGPL-3.0, pero el árbol inspeccionado al 20/11/2026 sólo contiene configuración, workflows, licencia y README: no aparecen carpetas de addons ni manifiestos instalables. Por tanto, **no es una localización lista para instalar** en ese estado. `leonobitech/l10n-argentina` 18.0 también aparece como repositorio de scaffolding sin addons en el árbol revisado.

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

El orden separa herramientas de bajo riesgo que aceleran cualquier plataforma de los servicios completos que podrían añadir una segunda autoridad o una operación innecesaria.

1. **Importación y calidad de datos:** usar OpenRefine para limpieza asistida; probar Frictionless, RapidFuzz, python-stdnum y Pint con el dataset canónico de artículos, clientes, proveedores y CUIT/CBU. La prueba debe detectar duplicados y errores, no fusionar automáticamente.
2. **Fiscalidad argentina:** comparar LaPyme/facturas y arca-sdks en homologación; ejecutar estados inciertos, reintentos con la misma clave, emisión concurrente, respuesta perdida, consulta/recuperación y notas de crédito. Elegir uno; no hacer emisiones dobles.
3. **Hardware de caja:** comparar QZ Tray y pos-toolkit con la misma matriz real de impresoras, cajones, lectores y balanzas; validar firmas, permisos, reconexión y reinicio.
4. **Backups de la plataforma elegida:** si usa PostgreSQL, probar pgBackRest y recuperación PITR a una instancia alternativa; para archivos, comparar restic con Kopia y restaurar muestras verificadas. No esperar al final de la implementación.
5. **Offline:** prototipar PowerSync para catálogos/vistas y tareas no conflictivas; probar pérdida de red, reinicio, reintentos y cambios duplicados. Rechazarlo como solución de stock si no resuelve explícitamente la autoridad y concurrencia.
6. **Canal ecommerce:** después de elegir quién posee catálogo, precio, inventario y ventas, comparar Spree con Saleor en un flujo B2B/online. Probar pedido, cancelación, devolución, webhook duplicado, reservas y conciliación. Llevar sólo uno a prueba profunda.
7. **Documentos:** probar OCRmyPDF + Docling + invoice2data con facturas y remitos anonimizados de varios proveedores. Paperless-ngx es una evaluación separada para archivo documental, permisos y exportación.
8. **Logística:** empezar por el wrapper MiCorreo de Correo Argentino; validar Andreani/OCA contra sus APIs oficiales; sólo entonces evaluar Karrio y el costo de construir conectores argentinos. Vía Cargo queda como tracking externo mientras no exista booking API verificable.
9. **Analítica:** usar DuckDB con exportaciones canónicas Parquet/CSV y conciliar cada métrica contra datos operativos. Comparar Metabase y Superset como aplicaciones BI independientes; elegir como máximo una, con base de lectura y permisos por área.
10. **Automatización e infraestructura común:** Node-RED sólo para integraciones periféricas. Keycloak y OpenTelemetry/Prometheus/Grafana se incorporan cuando haya varias aplicaciones/servicios o necesidad real de SSO/observabilidad. Temporal queda diferido hasta justificar workflows durables complejos.

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

**Valor:** candidato sólido para acelerar tienda online, canal mayorista o marketplace sin construir storefront y checkout desde cero. El storefront oficial está en [spree/storefront](https://github.com/spree/storefront), una aplicación Next.js separada con licencia MIT; el backend Spree conserva BSD-3-Clause. Hay que registrar ambas licencias y versiones como componentes distintos.

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

### Otros repositorios OCA para Odoo

- [OCA/stock-logistics-workflow](https://github.com/OCA/stock-logistics-workflow), rama 19.0: addons de procesos de almacén, transferencias y flujos de stock.
- [OCA/purchase-workflow](https://github.com/OCA/purchase-workflow), rama 19.0: addons de compras, órdenes y flujos de aprobación/proceso.

Ambos repositorios raíz declaran AGPL-3.0, pero cada addon puede declarar LGPL-3 u otra licencia en su `__manifest__.py`. Revisar las dependencias de Odoo y de otros addons; no incorporar repositorios completos ni copiar un módulo sin entender qué modelos y reglas extiende.

**Uso potencial:** aceleradores condicionados a que Odoo gane la comparación. No son servicios independientes y no se pueden portar directamente a Tryton, Frappe u otro ERP.



## 11. Contabilidad y libro mayor

### [Bigcapital](https://github.com/bigcapitalhq/bigcapital)

- Release observada: `v0.25.46` (14/11/2026).
- Licencia declarada en la raíz: AGPL-3.0.
- Aplicación autohospedada con Docker, API y SDK TypeScript; su README la describe como software contable e inventario y permite integrar su API para registrar transacciones en un sistema de doble partida.
- El código revisado incluye módulos para libro mayor, diarios manuales, facturas de venta, bills de proveedores, pagos, conciliación bancaria, reportes, inventario y webhooks.

**Valor:** candidato real para estudiar un libro mayor, cuentas por cobrar/pagar, conciliación y reportes financieros mediante una API ya existente. Puede evitar escribir desde cero una gran parte de contabilidad.

**Límites arquitectónicos y de operación:**
- Es una aplicación integrada: sus módulos comparten el servidor y la base de datos por tenant. No equivale a servicios independientes de ventas, compras, inventario y finanzas.
- Incluye inventario y documentos comerciales, que podrían duplicar datos si la plataforma principal ya tiene esos dominios. Sólo se puede adoptar si Rubrova define una autoridad única y evita registrar la misma operación en dos libros.
- El despliegue de desarrollo declara MariaDB, Redis, ClickHouse, Garage y Gotenberg, además del servidor y la interfaz. La instalación autohospedada necesita medir recursos, backup, restauración y actualización; no tratarla como una biblioteca ligera.
- El servidor `packages/server` aparece con `license: UNLICENSED` en su package manifest aunque el repositorio raíz declara AGPL-3.0. No extraer paquetes internos ni reutilizar código de forma aislada sin aclarar el alcance de la licencia y procedencia.
- No se ha comprobado localización fiscal argentina, ARCA, CUIT, percepciones/retenciones ni exportación contable local.

**Decisión:** candidato para una prueba de contabilidad como aplicación completa o autoridad financiera delimitada, no como microservicios internos. Compararlo contra la contabilidad nativa de Tryton/ERPNext/MyCompany. Nunca mantener Bigcapital y otro ERP como libros mayores paralelos.

**Prueba requerida:** balance de comprobación, mayor, balance general, resultados, flujo de caja, facturas/bills y notas, pagos, cuentas por cobrar/pagar, conciliación bancaria, multimoneda, impuestos, datos por sucursal/área, API, webhooks duplicados, exportación, backup/restore y recuperación tras reinicio. Reconciliar saldos y débitos/créditos contra un conjunto de referencia. Homologar aparte cualquier integración fiscal argentina.

## 12. Analítica y BI local

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

### [Metabase](https://github.com/metabase/metabase)

- Release observada: `v0.65.6` (18/11/2026).
- Código Community Edition fuera del directorio `enterprise/`: AGPL-3.0.
- Código de `enterprise/` y funciones Enterprise: Metabase Commercial License. El software `app-embed.js` tiene un acuerdo de licencia separado.

**Valor:** alternativa de BI con una experiencia de exploración y dashboards más orientada a usuarios de negocio. Puede ser más simple de operar que Superset para consultas y paneles internos.

**Límite de licencia:** para uso como aplicación de BI independiente, revisar y cumplir AGPL-3.0. No asumir que el SDK de embedding se incluye en la licencia comunitaria: el propio repositorio separa sus términos. Para mostrar tableros incrustados dentro de la interfaz Rubrova, verificar el acuerdo específico antes de elegirlo.

**Recomendación:** DuckDB para la primera prueba analítica con datasets exportados; Metabase es una alternativa más simple para BI independiente si su AGPL y licencia de embedding encajan; Superset es una alternativa Apache-2.0 con una operación más técnica. Elegir uno sólo después de una prueba de uso. No adoptar ambos automáticamente como una pila indivisible.

## 13. Identidad, autenticación y observabilidad

| Proyecto | Versión / licencia observada | Uso potencial | Condición |
|---|---|---|---|
| [Keycloak](https://github.com/keycloak/keycloak) | 26.8.2; Apache-2.0 | Identidad central, OIDC/OAuth2, federación de usuarios y autenticación de aplicaciones/servicios. | Diferir si el ERP elegido ya resuelve bien usuarios y permisos. Evaluarlo cuando existan varias aplicaciones independientes o SSO real; su operación agrega infraestructura. |
| [OpenTelemetry Collector](https://github.com/open-telemetry/opentelemetry-collector) | 0.165.0; Apache-2.0 | Recibir y exportar trazas, métricas y logs de servicios. | Candidato transversal cuando haya más de una aplicación o proceso que necesite observabilidad común. |
| [Prometheus](https://github.com/prometheus/prometheus) | 3.16.0; Apache-2.0 | Recolección y consulta de métricas de servicios, equipos y procesos. | Usar para disponibilidad, latencia, colas, sincronización y estado de backups. |
| [Grafana](https://github.com/grafana/grafana) | 13.3.1; AGPL-3.0 | Dashboards operativos y exploración de métricas/logs/trazas. | Revisar la licencia AGPL y usar sólo cuando los paneles operativos justifiquen el servicio adicional. |

**Estrategia:** no instalar Keycloak, Prometheus, Grafana y Collector desde el primer prototipo. Primero comprobar el sistema de identidad y logs nativo de la plataforma. Adoptar una capa común sólo cuando haya varias unidades operativas y métricas que necesitemos correlacionar.

## 14. Backups y restauración

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

## 15. Puertas de aprobación

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


## 15. Forecasting y análisis comercial

El alcance funcional y las pruebas de demanda, rentabilidad y marcas están definidos en [Inteligencia de demanda, rentabilidad y marcas](DEMAND_AND_MARGIN_INTELLIGENCE.md).

| Proyecto | Versión/licencia observada | Qué aporta | Uso propuesto y puerta de entrada |
|---|---|---|---|
| [StatsForecast](https://github.com/Nixtla/statsforecast) | Repositorio Nixtla; Apache-2.0; pyproject.toml observado con versión 2.1.1 | Modelos estadísticos y econométricos de series temporales; baselines, ETS, AutoARIMA, Theta y otros modelos. | Primera biblioteca de pronóstico a probar en un fixture de Rubrova. Fijar release/commit y dependencias; comparar contra naïve, naïve estacional y promedio móvil. |
| [MLForecast](https://github.com/Nixtla/mlforecast) | Apache-2.0; pyproject.toml observado con requires-python >=3.10 y versión 1.1.0 | Feature engineering temporal y modelos de machine learning con variables exógenas/estáticas, validación y predicción probabilística. | Segunda etapa, si hay variables exógenas confiables, historial y mejora medible; comprobar compatibilidad exacta con runtime y modelos elegidos. |
| [HierarchicalForecast](https://github.com/Nixtla/hierarchicalforecast) | Apache-2.0 | Reconciliación de pronósticos de múltiples niveles de agregación. | Posterior a la base de forecast; usar para coherencia SKU/familia/marca/categoría/sucursal/canal/total. |
| [DemandSense](https://github.com/mercer14k/DemandSense) | MIT; 4 commits y 2 estrellas en consulta del 20/11/2026 | Croston-SBA/TSB, demanda intermitente, escenarios, evaluación rolling, intervalos empíricos y API local. | Referencia de funcionalidades y posible inspección puntual. Proyecto todavía pequeño; no usar como núcleo de producción sin pruebas extensas de seguridad, calidad, dependencias y mantenimiento. |
| [DemandOS](https://github.com/RaulMermans/demand-OS) | Sin licencia declarada en el repositorio revisado | Flujo de señales de quiebre, forecasts, backtesting y propuestas de reposición revisadas por personas. | Inspección pública como referencia funcional/arquitectónica; no se presume que el código sea open source. No copiar/modificar sin licencia o permiso explícito; implementar ideas de forma independiente. |

### Rentabilidad y segmentación de marcas

- **Rentabilidad:** no se selecciona una biblioteca financiera genérica como autoridad. Se aprovechan los reportes y el ledger de costos del ERP elegido. ERPNext Stock Ledger/FIFO/Moving Average y Gross Profit son material de referencia funcional; comprobar su comportamiento junto con P&L y el método de valuación. No extraer la fórmula del informe separada del ledger.
- **Primeras y segundas marcas:** implementar el modelo de segmentos configurables con vigencia en Rubrova, comparable por categoría y unidad base. Capturar historial de precios, presentaciones, disponibilidad, promociones, costos y ventas. No se encontró una aplicación open source especializada que reemplace este dominio.
- **ABC/XYZ:** clasifican relevancia y variabilidad de SKU; son análisis complementarios, no etiquetas de primera/segunda marca.
- [Retail Sales & Margin Analysis](https://github.com/EkaterinaA83/Retail-sales-ABC-margin-analysis) aporta un ejemplo de análisis exploratorio de margen/promociones/ABC, pero no muestra un archivo LICENSE visible. Referencia metodológica, no código aprobado.

**Arquitectura de uso:** las bibliotecas de forecasting trabajan en un servicio/pipeline analítico separado sobre snapshots conciliados. DuckDB (MIT) puede soportar consultas locales; Superset (Apache-2.0) es una opción de BI posterior. Ninguna puede escribir en POS, pagos, stock o contabilidad. Metabase y Superset no se instalan juntos por defecto.

**Estado:** investigación documental. No instalar ni fijar dependencias de producción hasta que la plataforma POS/ERP y el runtime estén seleccionados y las pruebas comparativas estén listas.


## 16. Benchmark inicial de demanda mensual

- [StatsForecast 2.1.1](https://github.com/Nixtla/statsforecast) (Apache-2.0; Python >=3.10) es la versión fijada para la primera prueba reproducible. Se comparan AutoETS y AutoTheta en demanda regular, CrostonSBA en demanda intermitente, y cuatro baselines sencillos (último valor, seasonal naive, media de 3 y media de 12 meses).
- El fixture comprende 48 meses sintéticos (2022–2025) y cuatro cortes walk-forward (24, 30, 36 y 42 meses), con horizonte de tres meses. Se registran MAE, WAPE y sesgo.
- No se elige un modelo productivo por el ganador sintético. Debe superar baselines en datos reales comparables y demostrar comportamiento con quiebres de stock, promociones, cambios de precio, productos nuevos y demanda intermitente.
- La comparación se ejecuta en CI con versión fijada; el reporte incluye versión de StatsForecast/Pandas, folds, predicciones y métricas.
