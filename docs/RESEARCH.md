# Investigación y referencias

## Cómo usar este documento

Se estudiaron productos comerciales y proyectos abiertos para identificar soluciones útiles. La investigación no implica que sus funciones hayan sido auditadas ni que su código pueda reutilizarse. Antes de adoptar código, revisar licencia, seguridad, mantenimiento y compatibilidad.

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
- Odoo — https://www.odoo.com/documentation/ — POS, ecommerce, promociones, restaurantes e inventario; estudiar límites offline.

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
2. Los proyectos se estudian para aprender diseño y operación; no se presume equivalencia funcional.
3. Cifras comerciales se identifican como declaraciones del proveedor.
4. Disponibilidad, licencia, versión y mantenimiento se revisan antes de adoptar código o servicios.
5. Las decisiones importantes quedan registradas con alternativas y consecuencias.
