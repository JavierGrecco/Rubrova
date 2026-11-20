# Investigación y referencias

## Cómo usar este documento

Se estudiaron productos comerciales y proyectos abiertos para identificar soluciones útiles. La investigación no implica que sus funciones hayan sido auditadas. El proyecto está destinado a uso interno y privado, sin distribución ni reventa previstas: por eso se pueden evaluar también proyectos GPL y AGPL, no solo licencias permisivas. Antes de adoptar código, revisar licencia aplicable a la versión exacta, seguridad, mantenimiento, dependencias, avisos y condiciones de uso. La AGPL requiere atención especial si usuarios interactúan remotamente por red con una versión modificada.

Precios y cifras comerciales cambian. Las cifras de adopción publicadas por proveedores son declaraciones propias, salvo verificación independiente.

## POS y comercio minorista

- MiNegocio — https://mi-negocio.app/ — fiados, adaptación al comercio de barrio, importación y aprendizaje desde necesidades reales.
- DonKiosco — https://donkiosco.com.ar/ — catálogo precargado, lector, experiencia móvil y entrada simple.
- Kiosko — https://mikiosko.app/ — conciliación de pagos, compras y costos comparables.
- Cobrando — https://cobrando.app/ — gestión, reportes y automatización documental.
- Pesito — https://www.pesito.com.ar/ — inventario, compras y reposición.
- CajaOS — https://cajaos.com/ — demostración interactiva y gestión POS.

## ERP y arquitectura

- ERPNext — https://docs.frappe.io/erpnext — movimientos de stock, compras, cuentas, fabricación y trazabilidad.
- Apache OFBiz — https://ofbiz.apache.org/ — catálogo, pedidos, promociones, pagos, almacenes y fabricación; evitar reproducir toda su complejidad.
- Posnic — https://github.com/Posnic/POS — arquitectura local y sincronización; revisar AGPL y dependencias antes de reutilizar código.

## Omnicanalidad

- Vendure — https://docs.vendure.io/ — canales, inventario, precios, promociones y pedidos; revisar licencia y modelo comercial.
- Saleor — https://docs.saleor.io/ — variantes, canales, disponibilidad, precios y promociones.
- Shopify — https://help.shopify.com/en/manual/reports-and-analytics — análisis de ventas, inventario, ABC y descuentos.
- Lightspeed — https://retail-support.lightspeedhq.com/hc/en-us/articles/4410640218523-Navigating-Lightspeed-Analytics — rendimiento por producto, marca, categoría y GMROI.

## Gastronomía y sectores

- Fudo — https://fu.do/es-ar/funcionalidades/ — arqueo ciego, multicaja, multiturno, descuentos, recetas, reportes y delivery.
- Maxirest — https://maxirest.com.ar/ — operación local, sincronización central, cocina, auditoría y empleados.
- MIGA — https://migasoftware.com.ar/ — panadería, recetas, producción, stock y merma.
- Odoo 20.0 — https://www.odoo.com/documentation/20.0/ — POS, inventario, compras, fabricación, descuentos, fidelización y hardware; estudiar límites offline y separar Community de Enterprise.

## Abastecimiento y automatización

- Surtivo — https://www.surtivo.com/ — comparar costo por unidad equivalente y normalizar presentaciones.
- Orbi / Alumbra — https://alumbra.io/ — convertir mensajes, audios e imágenes en pedidos estructurados con aprobación.
- Rumbo — https://www.rumbo.chat/ — asistente contextual sobre datos comerciales y recomendaciones supervisadas.

## Estándares y fuentes técnicas

- OWASP ASVS 5.0 — https://owasp.org/www-project-application-security-verification-standard/
- OWASP Logging Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html
- PostgreSQL Row Security — https://www.postgresql.org/docs/current/ddl-rowsecurity.html
- Transactional Outbox — https://learn.microsoft.com/en-us/azure/architecture/databases/guide/transactional-out-box-cosmos
- Star Schema — https://learn.microsoft.com/en-us/power-bi/guidance/star-schema
- IndexedDB — https://developer.mozilla.org/en-US/docs/Web/API/IndexedDB_API
- Background Synchronization — https://developer.mozilla.org/en-US/docs/Web/API/Background_Synchronization_API

## Fuentes argentinas y reguladoras

- ARCA — Webservices de factura electrónica: https://www.arca.gob.ar/ws/documentacion/ws-factura-electronica.asp
- ARCA — Tipos de comprobantes: https://www.arca.gob.ar/facturacion/comprobantes/tipos.asp
- ARCA — Emisión y autorización: https://www.arca.gob.ar/fe/emision-autorizacion/comprobantes.asp
- Mercado Libre Developers: https://developers.mercadolibre.com.ar/
- Mercado Pago Developers: https://www.mercadopago.com.ar/developers/es
- INDEC: https://www.indec.gob.ar/
- BCRA — REM: https://www.bcra.gob.ar/PublicacionesEstadisticas/Relevamiento_de_Expectativas_de_Mercado.asp
- Servicio Meteorológico Nacional: https://www.smn.gob.ar/
- SEPA — Precios Claros: https://www.argentina.gob.ar/economia/comercio/preciosclaros

## Criterios de adopción

1. Documentación oficial del proveedor o regulador tiene prioridad.
2. Los proyectos se estudian tanto para aprender como para reutilizar código, módulos o soluciones completas; no se presume equivalencia funcional.
3. Cifras comerciales se identifican como declaraciones del proveedor.
4. Disponibilidad, licencia, versión y mantenimiento se revisan antes de adoptar código o servicios.
5. Las decisiones importantes quedan registradas con alternativas y consecuencias.


### POS, descuentos y hardware

- Odoo 19 — descuentos por línea y globales, programas de lealtad, cupones, promociones automáticas, Buy X Get Y y listas de precios: https://www.odoo.com/documentation/19.0/applications/sales/point_of_sale/pricing.html.
- Fudo — descuentos fijos/porcentuales, multicaja, turnos, arqueo ciego, cierres parciales y reportes: https://fu.do/es/funcionalidades/.
- Square — matriz de compatibilidad de lectores de códigos: https://squareup.com/us/en/compatibility/accessories/barcode-scanners.
- Square — conexión y prueba de cajones de dinero USB o asociados a impresoras: https://api.squareup.com/help/us/en/article/8354-connect-a-cash-drawer-to-your-point-of-sale.
- Square — impresoras para tickets, comandas, pedidos, anulaciones y etiquetas: https://squareup.com/help/us/en/article/8246-connect-a-printer-to-square.

Estos ejemplos ayudan a definir una matriz propia de hardware compatible. No se copiarán listas de compatibilidad de otros proveedores como si fueran pruebas de nuestros adaptadores.

### Calidad, seguridad, accesibilidad y normativa

- ISO/IEC 25010:2023 — modelo de calidad del producto: https://www.iso.org/standard/78176.html.
- W3C WCAG 2.2 — recomendación vigente para accesibilidad web: https://www.w3.org/TR/wcag/.
- OWASP ASVS 5.0 — requisitos de seguridad verificables: https://asvs.owasp.org/.
- NIST SSDF SP 800-218 — v1.1 final; Rev. 1 / v1.2 seguía como borrador en la consulta del 19/11/2026: https://csrc.nist.gov/Projects/ssdf/publications.
- PCI Security Standards Council — biblioteca oficial; PCI DSS v4.0.1: https://www.pcisecuritystandards.org/es/document_library/.
- Argentina — Ley 25.326 de protección de datos personales: https://www.argentina.gob.ar/normativa/nacional/ley-25326-64790/actualizacion.
- Argentina — texto actualizado de RG 1415, con modificaciones de 2025 y 2026: https://www.argentina.gob.ar/normativa/nacional/resoluci%C3%B3n-1415-2003-81316/actualizacion.
- INPI — buscador oficial de marcas: https://portaltramites.inpi.gov.ar/marcasconsultas/busqueda.

El nombre de producto no se considera legalmente disponible hasta realizar búsqueda de denominaciones idénticas y similares, variantes fonéticas, titulares y clases pertinentes. La consulta web no sustituye el análisis del INPI ni asesoramiento especializado.


## Proyectos abiertos y reutilización de código

El catálogo de repositorios, módulos, licencias y condiciones está en [Catálogo de código reutilizable](CODE_REUSE_CATALOG.md). La evaluación técnica y el guion común están en [Evaluación de plataformas](PLATFORM_EVALUATION.md).

### Estado actualizado — 19/11/2026

La ronda integral compara **MyCompany/lsFusion 6.2**, **Posnic 1.9.2** y **ERPNext 16.60.0 + Frappe Framework 16**. MyCompany se agregó por su cobertura de ERP/POS y su mecanismo de módulos. Odoo Community 20 y Medusa v2 quedan como referencias históricas fuera de la comparación activa; NexoPOS no se aprueba mientras siga la discrepancia entre su LICENSE raíz GPLv3 y composer.json MIT.

**Posnic** aporta POS local, ventas, inventario, compras y caja. La prueba debe fijarse en el tag `v1.9.2`: la rama `main` consultada tenía seis commits posteriores y `develop` estaba divergida. Su self-hosted comparte una base en LAN, pero no sincroniza varias bases independientes; esa función se ofrece mediante Cloud. La evidencia offline publicada es limitada. El código es AGPL-3.0-only, mientras que el instalador revisado incluye MongoDB SSPL-1.0 y amCharts 4 comercial. Sus campos GST/India requieren adaptación para Argentina.

**ERPNext/Frappe** aporta mayor profundidad en inventario, compras, costos, fabricación y contabilidad. ERPNext es GPL-3.0 y Frappe Framework MIT. ERPNext v16.60.0 debe probarse con Frappe Framework 16 fijado; no presumir recuperación offline ni soporte PostgreSQL equivalente.

**Componentes especializados:**
- pos-toolkit: Apache-2.0; plugin Tauri/Rust para hardware y paquete TypeScript para tickets. `register-core` está planificado.
- emupos y ESCPost: Apache-2.0; simulación y diagnóstico de periféricos.
- arca-sdks: `@ramiidv/arca-facturacion` 7.1.0, MIT, Node >=22.12; candidato de homologación, no garantía de cumplimiento por sí solo.
- PowerSync Open Edition: Apache-2.0, separada de Enterprise/Cloud.
- Dexie.js: Apache-2.0, IndexedDB y no sincronización distribuida completa.

La evaluación sigue sin ejecución local. El laboratorio fija MyCompany 6.2 con instalador/JAR verificados por SHA-256; Posnic 1.9.2 se prueba en Windows/Linux compatible (no tiene instalador macOS en esa release; en Mac se usa VM); ERPNext se levanta con el demo oficial Frappe Docker, fijado al commit `ef24ebc0a411b6237694765f0b51d8f8f8dd13ce` y a la imagen `frappe/erpnext:v16.60.0`. El dataset tiene validador Node.js y CI con 27 pruebas aprobadas el 20/11/2026. El benchmark mensual de demanda regular/intermitente con StatsForecast 2.1.1 también pasó CI; ambos usan datos sintéticos. Esas pruebas validan el dataset y sus invariantes sintéticas, no la instalación ni el comportamiento funcional de los candidatos. No se incorporó código externo; la ejecución local de MyCompany, Posnic y ERPNext y los escenarios funcionales P01–P26 siguen pendientes.

Fuentes de código y licencias:
- Posnic: https://github.com/Posnic/POS/releases/tag/v1.9.2 y https://github.com/Posnic/POS
- ERPNext: https://github.com/frappe/erpnext/releases/tag/v16.60.0
- Frappe Framework: https://github.com/frappe/frappe/tree/version-16
- pos-toolkit: https://github.com/narisolutions/pos-toolkit
- arca-sdks: https://github.com/ramiidv/arca-sdks
- PowerSync: https://github.com/powersync-ja/powersync-js
- Dexie.js: https://github.com/dexie/Dexie.js

Este resumen es una guía de investigación, no asesoramiento jurídico ni auditoría de seguridad.

## Investigación ampliada de módulos — 19/11/2026

- **MyCompany/lsFusion 6.2:** MyCompany Apache-2.0, runtime lsFusion LGPL v3; POS, CRM, compras, inventario, fabricación, proyectos y RR. HH. Nuevo candidato integral. https://github.com/lsfusion-solutions/mycompany
- **Simple WMS:** MIT; FastAPI/PostgreSQL, stock ledger append-only, tareas de almacén, scanner PWA y transferencias. Candidato WMS. https://github.com/q7-technology/simple-wms
- **OpenLinker v0.20.0:** Apache-2.0; arquitectura hexagonal, ports/adapters, conectores, OAuth, webhooks y fulfillment. Referencia para integración. https://github.com/openlinker-project/openlinker
- **OfferKit:** MIT; cupones, redenciones atómicas, gift cards, loyalty, referidos y segmentos. Candidato de promociones. https://github.com/offerkit/offerkit
- **DuckDB:** MIT; motor analítico embebido y multiplataforma, no OLTP. https://github.com/duckdb/duckdb
- **Apache Superset:** Apache-2.0; BI self-hosted de solo lectura. https://github.com/apache/superset
- **Node-RED:** Apache-2.0; automatización periférica, no fuente transaccional. https://github.com/node-red/node-red
- **OpenOMS:** Elastic License 2.0, no aprobado como open source. https://github.com/openoms-org/openoms

Ver [Investigación ampliada de módulos](MODULAR_COMPONENT_RESEARCH.md) y [Composición de módulos](MODULE_COMPOSITION.md).

### Terminales locales de pago

Mercado Pago Point documenta Orders API, estados, webhooks, cancelaciones asíncronas e impresión de contenido personalizado en terminales compatibles. Getnet documenta soluciones POS Integrado con API/SDK según habilitación; Fiserv/Posnet ofrece una modalidad Trx a Trx cuya integración necesita protocolo y homologación; Payway mantiene documentación de desarrolladores que requiere acceso técnico adicional.

La especificación y la matriz de capacidades están en [Checkout y terminales](CHECKOUT_AND_PAYMENT_TERMINALS.md). Estos hallazgos son documentales; no se ha realizado homologación física con un adquirente.


### Integraciones logísticas, contables y nuevas necesidades PyME — 19/11/2026

- **Transportistas:** se documentaron las APIs directas de Andreani, PAQ.AR y OCA e-Pak; tracking de Vía Cargo mediante AfterShip/17TRACK; Envíopack como agregador comercial con webhooks; Kangu queda pendiente de demostrar disponibilidad argentina.
- **Administración/contabilidad:** Tango/Axoft mantiene APIs y archivos con alcances distintos; Catedral se considera inicialmente mediante importación/exportación; Bejerman, Xubio y Colppy ofrecen APIs sujetas a plan y permisos. Se define un paquete canónico de exportación y conciliación.
- **Proyectos de inventario y documentos:** InvenTree, OpenBoxes, OpenWMS, Paperless-ngx, OCRmyPDF e invoice2data; se revisan licencias y ownership para no duplicar inventario o libros.
- **Analítica y workflows:** Temporal, Activepieces, Kestra, skforecast y Polars, con n8n separado por su licencia source-available. La automatización y el forecasting no toman decisiones contables/stock sin aprobación.
- **Necesidades de PyME:** pérdida de pedidos por fallos de sincronización, offline, códigos/ubicaciones de inventario, márgenes reales, cobro tardío, caja y migración asistida. La evidencia, sus límites y el backlog están documentados.

Documentación:
- [Logística argentina y seguimiento unificado](ARGENTINA_LOGISTICS_INTEGRATION.md)
- [Interoperabilidad contable y administrativa](ACCOUNTING_INTEROPERABILITY.md)
- [Necesidades PyME y backlog](PYME_NEEDS_AND_PRODUCT_BACKLOG.md)
- [Investigación ampliada de módulos](MODULAR_COMPONENT_RESEARCH.md)
