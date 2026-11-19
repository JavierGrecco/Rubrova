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

La comparación de licencias, arquitectura, alcance y posibilidad de adaptación está desarrollada en [Estrategia de reutilización de código abierto](OPEN_SOURCE_STRATEGY.md).

Resumen de la revisión del 19/11/2026:

- **Medusa:** núcleo MIT con materiales Enterprise separados; primer candidato para probar módulos de comercio reutilizables.
- **Odoo Community 20.0:** los manifiestos públicos de POS, inventario, compras, fabricación, contabilidad base, fidelización y `l10n_ar` declaran LGPL-3. Es finalista por cobertura funcional, pero el offline del POS no garantiza recuperación tras cierre del navegador. La disponibilidad y licencia de `l10n_ar_edi` y `l10n_ar_reports` no se confirmaron en el repositorio Community.
- **Frappe / ERPNext:** Frappe es MIT, ERPNext es GPLv3; no confundir las dos licencias.
- **Apache OFBiz:** Apache 2.0; suite ERP muy completa, pero con costo de adaptación elevado.
- **Saleor:** BSD 3-Clause; referencia de comercio electrónico, no una base POS completa.
- **Vendure, uniCenta y NexoPOS:** GPLv3 por defecto; no incorporar su núcleo sin una decisión explícita sobre copyleft.
- **OSPOS:** su archivo LICENSE agrega una exigencia de atribución visible en cada pantalla; no encaja con una interfaz completamente rebrandeada.
- **TastyIgniter:** MIT; referencia o posible fuente acotada para flujos gastronómicos.

- **ARCA externo para Odoo:** `leonobitech/l10n_ar_arca_edi` declara AGPL-3, Odoo 19 y estado Beta en su manifiesto; estudiar su protocolo y pruebas, no incorporarlo al producto sin una decisión expresa sobre AGPL.
- **OCA `l10n-argentina`:** repositorio raíz AGPL-3; la licencia de cada módulo se determina por su propio manifiesto. La rama 19.0 revisada no presentaba módulos listos para integrar.

Fuentes de código y documentación Odoo 20:
- Soporte de versiones: https://www.odoo.com/documentation/20.0/es/administration/supported_versions.html
- POS offline: https://www.odoo.com/documentation/20.0/es_419/applications/sales/point_of_sale/use.html
- Descuentos y promociones: https://www.odoo.com/documentation/20.0/es_419/applications/sales/point_of_sale/extra/pricing.html
- Localización argentina y ARCA: https://www.odoo.com/documentation/20.0/es_419/applications/finance/fiscal_localizations/argentina.html
- Código público LGPL-3 del POS y `l10n_ar`: https://github.com/odoo/odoo/blob/20.0/addons/point_of_sale/__manifest__.py y https://github.com/odoo/odoo/blob/20.0/addons/l10n_ar/__manifest__.py

La consulta de código abierto no equivale a una auditoría de seguridad ni a la aprobación de una dependencia. No se incorporó código externo en esta etapa.


## Criterio actualizado: uso privado interno

La plataforma se construye para uso propio del negocio. No se prevé distribuir copias, revender el software ni ofrecerlo a terceros como servicio. En este escenario, la GPL permite modificar y utilizar internamente el programa sin publicar las modificaciones ni entregar el código a terceros, según la FAQ oficial de GNU. La AGPL añade una obligación específica para versiones modificadas con las que usuarios interactúan remotamente a través de una red: debe ofrecerse el código fuente correspondiente a esos usuarios.

Por lo tanto:
- No limitar la búsqueda a MIT/BSD/Apache. Incluir GPL, AGPL, LGPL y licencias duales.
- Considerar proyectos completos como ERPNext, Odoo, Vendure, uniCenta, NexoPOS y módulos OCA si su cobertura ahorra trabajo.
- Comparar adopción completa, fork, extensión y extracción de módulos; elegir la vía que minimice tiempo y mantenimiento.
- Conservar licencias, copyright, avisos NOTICE y atribuciones aplicables, y registrar los cambios.
- Revalidar el análisis si se habilita acceso remoto a terceros, se distribuye una copia, se contrata a otra entidad para operar el sistema o cambia el alcance del proyecto.

Fuentes:
- GNU GPL FAQ: https://www.gnu.org/licenses/gpl-faq.es.html
- GNU AGPLv3, sección 13: https://www.gnu.org/licenses/agpl-3.0.html
- Frappe, separación de licencias entre Framework y ERPNext: https://docs.frappe.io/legal/others/license-and-trademark

Este criterio es una guía técnica general, no asesoramiento jurídico sobre un caso concreto.

## Catálogo de código reutilizable

La revisión detallada de repositorios, manifiestos, licencias, cobertura y límites está en [Catálogo de código reutilizable](CODE_REUSE_CATALOG.md).

Hallazgos principales verificados el 19/11/2026:
- Posnic: código propio AGPL-3.0-only; paquetes con MongoDB SSPL-1.0; operación local/offline documentada con límites y evidencia acotada.
- ERPNext GPL-3.0 y Frappe MIT.
- NexoPOS presenta discrepancia: LICENSE GPLv3 frente a composer.json MIT. Bloqueado hasta aclaración.
- pos-toolkit y emupos y ESCPost: Apache-2.0; hardware, simulación y diagnóstico.
- arca-sdks: monorepo activo; paquete de facturación MIT; el repo anterior fue archivado.
- PowerSync Open Edition: Apache-2.0; separar funciones open source de Enterprise/Cloud.
- Dexie.js: Apache-2.0 para IndexedDB, no sync completo.
- TastyIgniter MIT; DearPOS Apache-2.0 y ElitaleRestro AGPLv3 como referencias sectoriales con límites.

No se clonó ni ejecutó código de estos proyectos en esta fase.
