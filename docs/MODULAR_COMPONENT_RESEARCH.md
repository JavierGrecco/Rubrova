# Investigación ampliada de plataformas y módulos reutilizables

**Revisión:** 19 de noviembre de 2026  
**Alcance:** uso interno, personal y privado. Podemos considerar GPL/AGPL y proyectos que cubran solo un sistema operativo; la licencia y modo de ejecución se revisan por componente.

Estos candidatos amplían el análisis más allá de POS. Son fuentes de estudio/adaptación, no código incorporado ni módulos aprobados para producción.

## A. Plataformas integrales

### MyCompany / lsFusion — nuevo candidato integral prioritario

- Repositorio: https://github.com/lsfusion-solutions/mycompany
- Release estable inspeccionada: 6.2; commit del tag d21ca6978717b98b6300d90267f9767db7414008.
- Aplicación MyCompany: Apache-2.0. Plataforma lsFusion subyacente: LGPL v3, licencia independiente.
- Alcance observado: ventas y CRM, leads/marketing, pedidos, facturación y pagos, compras, inventario multi-depósito, recepciones/expediciones, fabricación, BOM, centros de trabajo, órdenes de producción, retail POS, proyectos, RR. HH., asistencia y nómina.
- Arquitectura: módulos lsFusion declaran dependencias; la documentación muestra cómo añadir un módulo propio y seleccionar módulos existentes.
- Sistemas: instaladores Windows x64 y Linux, cliente web/navegador y guía Docker. La UI web permite evaluación desde macOS, Windows y Linux sin exigir binario de escritorio universal.
- Valor: candidato integral con módulos seleccionables; puede adelantar ERP, POS, inventario, compras, fabricación, proyectos, RR. HH. y CRM.
- Riesgos: la release estable 6.2 no debe confundirse con la documentación online versión 7.0 ni con master/7.0-SNAPSHOT. Hay ejemplos/configuraciones regionales de otros países; no está demostrado Argentina, ARCA, adquirentes locales ni offline requerido.
- Recomendación: comparar tag 6.2, ejecutar retail/inventario/compra/fabricación y añadir un módulo custom mínimo sin parchear el core.

Fuentes:
- https://github.com/lsfusion-solutions/mycompany
- https://github.com/lsfusion-solutions/mycompany/releases/tag/6.2
- https://mycompany-docs.lsfusion.org/retail/pos/
- https://mycompany-docs.lsfusion.org/administration/development/

### Posnic y ERPNext/Frappe

Se mantienen como candidatos integrales de la evaluación existente. Posnic aporta POS local y ERPNext/Frappe mayor profundidad de ERP/producción/contabilidad. No se eliminan al agregar MyCompany.

- https://github.com/Posnic/POS
- https://github.com/frappe/erpnext
- https://github.com/frappe/frappe

## B. Simple WMS — módulo especializado de almacén

- Repo: https://github.com/q7-technology/simple-wms
- Licencia: MIT.
- Commit inspeccionado: d0b1cbe76ea5dc1ba0ebb68ac444522263cd075f (15/10/2026); no se identificó un release etiquetado.
- Stack: FastAPI/Python 3.12, PostgreSQL, SQLAlchemy, worker, React desktop y scanner PWA.
- Funciones: ledger de stock append-only; recepción, putaway, picking, packing, despacho, transferencias, conteos, reposición y producción; multi-depósito, pallets, cajas, SSCC y scanner PWA.
- Valor: puede adelantar tareas reales de almacén y scanning móvil. El servidor/API no obliga a que el puesto use el mismo OS.
- Límites: delega impresión a un servicio externo; la PWA debe probar su persistencia y reintentos ante cortes. El README advierte que el adaptador SAP no contabiliza todavía devoluciones de entrega: una entrega devuelta y despachada de nuevo puede generar una segunda salida sin la reversión intermedia.
- Encaje: módulo WMS, solo si se define su autoridad sobre stock de depósito y se corrige/prohíbe el flujo SAP defectuoso.

## C. OpenLinker — infraestructura de conectores

- Repo: https://github.com/openlinker-project/openlinker
- Apache-2.0; v0.20.0, commit 2edefdd3f1a9fdf36c40b28f9076182bc6f50554 (19/11/2026).
- Puertos/capacidades, plugins, conectores de tiendas/marketplaces/carriers, OAuth, mapeo de IDs, webhooks, jobs durables y ADR sobre autoridad de datos.
- Valor: estudiar/adaptar patrones y componentes de integración; no adoptar la aplicación entera.
- Límite: su inventario de conectores observado está orientado en buena parte a Europa/Polonia; no es un adaptador listo para Mercado Libre Argentina o ARCA.

Fuentes:
- https://github.com/openlinker-project/openlinker
- https://github.com/openlinker-project/openlinker/releases/tag/v0.20.0
- https://github.com/openlinker-project/openlinker/tree/v0.20.0/docs/architecture/adrs

## D. OfferKit — promociones, fidelización y gift cards

- Repo: https://github.com/offerkit/offerkit
- MIT para paquetes propios.
- Source commit inspeccionado: 5238376740339815aedec2d5824b5fd223af384f (04/11/2026); release de imagen v0.2.1 (15/10/2026), plataforma linux/amd64.
- Stack: TypeScript, API tipada, PostgreSQL, Redis/BullMQ con fallback a PostgreSQL, dashboard, SDK, CLI y MCP.
- Funciones: motor de descuento/cupón, redenciones stackables atómicas, gift cards con ledger/rollback, loyalty tiers/points/expiry, referidos, segmentos y audit log.
- Valor: motor especializado que puede ahorrar desarrollo de campañas y saldos de beneficios.
- Límites: proyecto joven; verificar versión de source frente a imagen y soporte de plataforma. No debe ser autoridad del total ni de impuestos: Rubrova calcula/congela precio y distribución del descuento y conserva la decisión externa. Probar reversión ante devolución, cancelación y doble webhook.

Fuentes:
- https://github.com/offerkit/offerkit
- https://github.com/offerkit/offerkit/releases/tag/v0.2.1

## E. DuckDB y Apache Superset — inteligencia analítica

- DuckDB: MIT, embebido y multiplataforma. Candidato para consultas analíticas locales, Parquet, proyecciones y prototipos. No reemplaza OLTP ni el ledger.
- Apache Superset: Apache-2.0, BI self-hosted para explorar datos y construir dashboards. Es una plataforma de despliegue más pesada; usar sobre un esquema analítico de solo lectura, no contra el flujo de caja.

Fuentes:
- https://github.com/duckdb/duckdb
- https://duckdb.org/docs/
- https://github.com/apache/superset

## F. Node-RED — automatización periférica

- Repo: https://github.com/node-red/node-red
- Apache-2.0.
- Útil para prototipar notificaciones, tareas programadas, flujos periféricos y conectores.
- No usar como autoridad de venta, pagos, stock, fiscalidad o caja ni en el camino síncrono del checkout.

## G. OpenOMS — condicionado, no aprobado

- Repo: https://github.com/openoms-org/openoms
- LICENSE raíz declara Elastic License 2.0; no tratar como open source aprobado.
- Mantener como referencia de OMS, pero no copiar código ni integrar dependencias sin revisión legal específica y análisis de utilidad para el uso privado.

Fuente: https://github.com/openoms-org/openoms/blob/main/LICENSE

## Prioridad revisada

| Prioridad | Proyecto | Qué evaluar |
|---|---|---|
| Plataforma integral | MyCompany/lsFusion 6.2 | POS, CRM, compras, inventario, producción y composición de módulos |
| Plataforma integral | Posnic 1.9.2 | POS local, caja, stock y recuperación |
| Plataforma integral | ERPNext 16.60.0/Frappe 16 | ERP, compras, fabricación, contabilidad y POS |
| WMS | Simple WMS | Ledger, tareas, scanner PWA, transferencias y devoluciones |
| Conectores | OpenLinker | Ports/adapters, webhooks, mapeo y fulfillment |
| Promociones | OfferKit | Cupones, puntos, gift cards y reversión |
| Analítica | DuckDB + Superset | Read models y dashboards |
| Automatización | Node-RED | Flujos periféricos |
| Condicionado | OpenOMS | Revisar licencia, no incorporar aún |

La regla de integración está en [Composición de módulos y contratos](MODULE_COMPOSITION.md). No integrar varios sistemas como fuentes de verdad paralelas.


## H. Alternativa comercial de terminales: Mobbex Smart POS

- Fuente: https://www.mobbex.com/smart-pos/
- El proveedor describe Smart POS multi-adquirente para Payway, Fiserv, Global Processing y Getnet, terminales Ingenico, Urovo, Verifone, NexGo y Newland, integración por API desde el software de caja y conciliación automática.
- No es un proyecto de código abierto ni un módulo para copiar. Es una vía comercial alternativa a implementar una integración directa con cada adquirente.
- Puede reducir el número de adaptadores, pero crea dependencia operativa y comercial de un proveedor. Solicitar tarifas, disponibilidad local, documentación de API, pruebas, política de reversos, cierres de lote, impresiones, conectividad y terminales compatibles antes de evaluarlo.
- Compararlo contra las integraciones directas de Mercado Pago Point, Getnet, Fiserv/Posnet y Payway; no asumir que soporta todos los modelos ni que elimina certificaciones.

Fuentes de terminales:
- Mercado Pago Point: https://www.mercadopago.com.ar/developers/es/docs/mp-point/payment-processing
- Getnet POS integrado: https://www.getnet.net/ar/ayuda/terminales-getpos/get-pos-integrado
- Fiserv/Posnet: https://www.fiserv.com.ar/content/dam/firstdata/ar/es/pdf/Reglamento_de_Comerciantes_13-04-26.pdf
- Payway PayStore Terminals: https://developers.payway.com.ar/catalog?category=Pagos
- Mobbex Smart POS: https://www.mobbex.com/smart-pos/


## I. Dolibarr ERP/CRM 24.0.3 — candidato integral para áreas comerciales y servicios

- Repositorio: https://github.com/Dolibarr/dolibarr
- Release: 24.0.3, publicada el 11/11/2026; commit del tag 5c6c7ff6a5112413b1c27221c8d11750afad56f8.
- Licencia declarada: GPL-3.0.
- Stack: aplicación web PHP, módulos activables y extensiones; admite despliegues genéricos en distintos sistemas/hosting.
- Cobertura documentada en la distribución: terceros/contactos, productos y servicios, stock/depósitos, códigos de barras, lotes/series, variantes, BOM y manufacturing orders, propuestas, pedidos, contratos/suscripciones, intervenciones, tickets, envíos, facturas/créditos, pagos, POS, contabilidad, proyectos y agenda.
- **Por qué es relevante:** reúne venta de productos, prestación de servicios, contratos, agenda y envíos. El módulo de Shipping parte de un pedido, sigue cantidades despachadas y pendientes, genera packing slips y evidencia de entrega. Interventions representa órdenes de servicio/mantenimiento.
- **Límites a verificar:** no asumir que los módulos estándar cubren las escalas mayoristas, reglas multiárea o rentabilidad por unidad que queremos. Hay que probar la atribución de ingresos/costos, clientes con varias relaciones comerciales, acuerdos de suministro y localización argentina. La modularidad de Dolibarr no implica que cada módulo pueda extraerse a otro runtime.
- **Recomendación:** nuevo candidato de alta relevancia funcional para inspección comparativa. Antes de incorporarlo al laboratorio formal, realizar una prueba de código/funcional de dimensiones de área, shipment lifecycle, contratos/intervenciones, márgenes y actualización de módulos. No declararlo compatible con Rubrova todavía.

Fuentes:
- https://github.com/Dolibarr/dolibarr/releases/tag/24.0.3
- https://github.com/Dolibarr/dolibarr/tree/24.0
- https://wiki.dolibarr.org/index.php/User_documentation
- https://wiki.dolibarr.org/index.php/Module_Shipments
- https://wiki.dolibarr.org/index.php?title=Module_Interventions_En
- https://www.dolibarr.org/presentation-shipments.php

## J. OCA Field Service 19.0 — módulos de servicio para ecosistema Odoo

- Repositorio: https://github.com/OCA/field-service
- Rama inspeccionada: 19.0; el catálogo publica addons versión 19.0.
- Licencia del repositorio: AGPL-3.0; cada addon se verifica individualmente en __manifest__.py.
- Addons relevantes: fieldservice, fieldservice_agreement, fieldservice_calendar, fieldservice_recurring, fieldservice_timesheet, fieldservice_expense, fieldservice_vehicle, fieldservice_stock, fieldservice_crm, fieldservice_project y fieldservice_portal.
- Hallazgo: fieldservice_agreement declara AGPL-3, depende de fieldservice y agreement, y aparece en estado Beta. fieldservice_recurring aporta órdenes recurrentes; calendar y timesheet conectan programación y tiempo.
- Valor: referencia concreta para órdenes de trabajo, acuerdos, técnicos, recurrencias, agenda, stock, gastos y vehículos.
- Límite: está integrado al ORM de Odoo. No es una biblioteca independiente que se pueda copiar sin su runtime. El español argentino disponible en algunos archivos i18n no implica localización argentina completa.
- Recomendación: usarlo como fuente de patrones y candidato de adopción/fork si se evaluara Odoo como base; no prometer integración directa con otra plataforma sin estudiar dependencias.

Fuentes:
- https://github.com/OCA/field-service/tree/19.0
- https://github.com/OCA/field-service/blob/19.0/fieldservice_agreement/__manifest__.py

## K. OpenFieldPro — FSM self-hosted orientado a servicios

- Repositorio: https://github.com/niko4244/openfieldpro
- Rama principal declarada: ofp-monorepo; commit inspeccionado 25ba62297ba4b6890656017dd425117de166b94a (22/08/2026).
- Licencia: AGPL-3.0-only.
- Stack: monorepo TypeScript, Fastify/API, Next.js web, PostgreSQL y app Expo para técnicos.
- Funciones observadas: CRM, clientes y propiedades, agenda día/semana/mes, dispatcher board, órdenes de trabajo, estimaciones, facturas, pagos, service plans, reporting, documentos, notificaciones, plugin registry, API tokens, webhooks y app móvil.
- Estado declarado por el README: release-candidate hardening; exige pruebas de dispositivos y evidencia de backup/restore antes de release.
- Valor: referencia concreta para el flujo de servicios desde oportunidad hasta pago, agenda/dispatch, trabajo técnico y cierre/facturación.
- Límite: proyecto joven y vertical; no reemplaza mayorista, stock, compras, POS ni contabilidad integral. Revisar datos y reglas de facturación antes de reutilizar.
- Recomendación: extraer conceptos, contratos y pruebas; evaluar código de agenda/dispatch/work order como módulo solo si su esquema puede aislarse. No adoptar la aplicación completa como base.

Fuentes:
- https://github.com/niko4244/openfieldpro
- https://github.com/niko4244/openfieldpro/tree/ofp-monorepo
- https://github.com/niko4244/openfieldpro/blob/ofp-monorepo/LICENSE

## L. Open TMS — transporte y tracking posterior al pedido

- Repositorio: https://github.com/DominicFinn/open_tms
- Rama: main; README indica desarrollo activo y que todavía no existe release estable.
- Licencia: README y metadata de GitHub indican MIT, pero la inspección del árbol/endpoint no encontró un archivo raíz LICENSE. **Licencia pendiente de verificación antes de incorporar código.**
- Stack: TypeScript, React, Fastify, Prisma y PostgreSQL; backend CQRS/event-driven.
- Funciones observadas: clientes, carriers, órdenes, facilities/depósitos, lanes/rutas, shipment lifecycle, tracking, eventos, referencias de carrier, consolidación, shipment share links, customer portal, API, webhooks, EDI, carrier integrations, IoT y SLA.
- Particularmente relevante: permite crear un shipment desde una orden o varias; dividir una orden grande en varios envíos; consolidar envíos compatibles; mantener la orden separada del shipment; asociar carrier y tracking después; mantener timeline de eventos e idempotencia de webhooks.
- Valor: fuente cercana al caso de distribución interprovincial y carga posterior del número de guía.
- Riesgos: proyecto en desarrollo sin release; stack y dominio orientados a 3PL/logística compleja; revisar seguridad, transiciones, integridad de cantidades, permisos multiempresa, licencia real y madurez antes de portar.
- Recomendación: candidato prioritario para inspección de Shipment/Tracking y patrones de integración; no usarlo como autoridad de ventas, pagos o inventario comercial.

Fuente:
- https://github.com/DominicFinn/open_tms

## Prioridad de investigación por nuevos escenarios

| Dominio | Candidato | Próxima inspección |
|---|---|---|
| ERP + contratos + envíos + POS | Dolibarr 24.0.3 | Áreas, margen, contratos, intervenciones y envío parcial |
| Wholesale/B2B pricing | ERPNext y Dolibarr | Mínimos, tiers, cliente/contrato, UOM y crédito |
| Servicios de campo | OCA Field Service / OpenFieldPro | Acuerdos, SLA, agenda, recurrencias, costo real y aceptación |
| TMS/distribución | Open TMS / Simple WMS | Pedido a uno/múltiples envíos, tracking posterior, handoff y costo |
| Rentabilidad multiárea | ERPNext / Dolibarr | Dimensiones y P&L por unidad con costos compartidos |

Las referencias se analizan por módulo y versión; no se integran como fuentes de verdad paralelas.


### Inspección de código de Dolibarr 24.0.3: matiz multiárea importante

En el tag 24.0 se inspeccionaron las clases de envío, contrato, intervención, proyecto, categorías y margen:

- `Expedition` es un objeto separado del pedido/venta y contiene `tracking_number`, `tracking_url`, almacén y líneas de expedición. Esto confirma que puede modelarse un despacho y asignar su guía al envío sin que la venta tenga que contenerla.
- `Contrat` posee tercero/cliente y líneas contractuales. `Fichinter` (intervención) puede vincularse con cliente, proyecto y contrato; contiene fechas/duración y líneas propias. Es una base real para estudiar cumplimiento de servicios.
- El proyecto incluye presupuesto, cliente y configuración de tareas/tiempo facturable.
- El módulo de márgenes tiene vistas para margen de producto, cliente y agente comercial. Esto no demuestra por sí solo un P&L completo por unidad de negocio ni un modelo de costos compartidos.
- El campo `entity` que aparece en varios objetos representa el contexto de entidad de Dolibarr/multiempresa; no debe interpretarse como unidad de negocio o centro de beneficio.
- Las categorías pueden etiquetar distintos tipos de objetos, pero no equivalen automáticamente a dimensiones de contabilidad analítica.

**Conclusión revisada:** Dolibarr contiene código reutilizable especialmente interesante para shipment, contratos e intervenciones. Sigue siendo un candidato integral de inspección, pero su adaptación multiárea y el resultado de gestión por unidad probablemente requieran modelado/extensión adicional. Antes de elevarlo a cuarto candidato formal hay que demostrar asignación de BU en líneas, ledger de costos, consolidación y actualización sin romper módulos.


## S. invoice2data — extracción asistida de facturas PDF

- Repositorio: https://github.com/invoice-x/invoice2data
- Versión/metadata inspeccionada: 1.0.1; Python >=3.10; licencia declarada MIT en pyproject.toml.
- Extrae campos de facturas mediante plantillas configurables y parsers de PDF/texto/tablas; tiene extras opcionales para OCR engines, PDF parsers y modelos de extracción.
- Valor para Rubrova: acelerar la carga de facturas de proveedores, CUIT, fechas, número, moneda, total e ítems cuando la estructura del proveedor es conocida.
- Límite: la extracción basada en plantillas es frágil ante formatos nuevos y no valida la autenticidad fiscal ni reemplaza la revisión. Un PDF escaneado necesita OCR previo; un campo extraído no equivale a un asiento ni a una factura verificada.
- Recomendación: ejecutar como proceso aislado de ingestión; devolver campos propuestos, nivel de confianza, página/fragmento de origen y errores para revisión humana. Guardar el original y su checksum. No escribir automáticamente en cuentas a pagar sin aprobar.
- Prueba: facturas reales anonimizadas de varios proveedores, formatos de texto y escaneados, cambios de plantilla, importes con coma/punto, IVA/percepciones y detección de duplicados.

Fuentes:
- https://github.com/invoice-x/invoice2data
- https://invoice2data.readthedocs.io/

## T. OCRmyPDF — OCR local y archivado documental

- Repositorio: https://github.com/ocrmypdf/OCRmyPDF
- Licencia: Mozilla Public License 2.0.
- La documentación indica soporte para Linux, Windows, macOS y FreeBSD; agrega una capa de texto OCR a PDFs escaneados, corrige inclinación, optimiza y puede generar PDF/A.
- Valor: digitalizar facturas, remitos, órdenes, recibos, contratos y constancias de entrega manteniendo la imagen y haciendo buscable el contenido. Encaja con el requisito multiplataforma y puede ejecutarse en el equipo o servidor local.
- Límite: OCR solo reconoce texto; no clasifica ni valida documento fiscal, proveedor, CUIT, importe o CAE. Depende de Tesseract y binarios/lenguajes adicionales; registrar la licencia de cada dependencia distribuida.
- Recomendación: combinarlo con invoice2data o extractor propio. El original permanece inmutable; OCR produce una versión derivada con checksum, idioma y versión del motor. Se requiere revisión humana para valores económicos y fiscales.

Fuentes:
- https://github.com/ocrmypdf/OCRmyPDF
- https://ocrmypdf.readthedocs.io/en/latest/

## U. skforecast — pronóstico de demanda y reposición

- Repositorio: https://github.com/skforecast/skforecast
- Licencia: BSD-3-Clause.
- Biblioteca Python que unifica modelos estadísticos, regresores machine learning y modelos foundation; permite entrenar, predecir, hacer backtesting, pronóstico probabilístico, ajustar parámetros, crear features de calendario y explicar variables.
- Valor: construir pronósticos por SKU, familia, sucursal o canal y simular reposición. Puede usar eventos, estacionalidad, promociones y ventas históricas cuando haya suficiente cobertura.
- Límite: no es un motor de inventario ni conoce por sí solo lead time, mínimos, cajas, roturas de stock, demanda censurada por faltantes ni compras comprometidas. Los modelos foundation pueden añadir dependencias/descargas y no se deben usar para datos privados sin estudiar el flujo.
- Recomendación: extraer patrones y evaluar la biblioteca en un servicio analítico opcional (Python), manteniendo el núcleo transaccional independiente. Comparar siempre contra baseline ingenuo/estacional y evaluar backtesting temporal; medir WAPE/MAE/bias y cobertura de intervalos. No pedirle que cambie compras o precios automáticamente.
- Criterio: solo activar pronóstico para series con historial y calidad suficientes; para demanda intermitente o SKUs nuevos mostrar reglas simples y nivel de confianza bajo.

Fuentes:
- https://github.com/skforecast/skforecast
- https://skforecast.org/latest/

## V. Polars — procesamiento analítico de alto rendimiento

- Repositorio: https://github.com/pola-rs/polars
- Licencia: MIT.
- Motor de consultas/DataFrames escrito en Rust con API Python, Rust, Node.js y SQL; soporta ejecución perezosa, optimización y spill a disco.
- Valor: procesar importaciones grandes, exportaciones contables, conciliaciones y datasets analíticos sin cargar todos los registros en memoria.
- Límite: es una herramienta de procesamiento, no una base OLTP ni un ledger; no usar DataFrame para sustituir las restricciones transaccionales de PostgreSQL.
- Recomendación: candidato de rendimiento para pipelines de lectura/transformación analítica, con pruebas de memoria, precisión decimal, redondeo, zonas horarias y tipos antes de adoptarlo.

Fuente:
- https://github.com/pola-rs/polars

## W. Bigcapital — contabilidad de doble partida como referencia de código

- Repositorio: https://github.com/bigcapitalhq/bigcapital
- Licencia del repositorio: AGPL-3.0.
- README describe una aplicación self-hosted de accounting + inventory, estados financieros y reportes; ofrece API para integrar transacciones de un sistema externo en contabilidad de doble partida.
- Valor: estudiar modelo de cuentas, journal entries, documentos, saldos, cuentas por cobrar/pagar, estados financieros e integración headless. Puede ayudar a comparar la construcción de un ledger propio frente a un motor contable existente.
- Límite: no se comprobó localización argentina, ARCA, IVA/percepciones/retenciones, libros/regímenes argentinos, multiárea con eliminación de costos internos ni integración con Tango/Catedral. Tampoco es un módulo pequeño; es otra aplicación con autoridad financiera.
- Recomendación: referencia de arquitectura/contratos y posible laboratorio separado, no añadirlo como segundo libro contable en Rubrova. AGPL-3.0 y sus obligaciones deben revisarse si se adapta o integra código; el uso privado no equivale a exención automática de licencias.
- Prueba documental siguiente: identificar modelos/servicios de journal, accounts, billing, inventory, API de creación de transacciones, reversión y conciliación; comparar con el modelo canónico de ACCOUNTING_INTEROPERABILITY.md.

Fuente:
- https://github.com/bigcapitalhq/bigcapital
- https://docs.bigcapital.app/api-reference


## M. InvenTree — inventario, trazabilidad y extensión por plugins

- Repositorio: https://github.com/inventree/InvenTree
- Rama inspeccionada: master; licencia del repositorio: MIT.
- Stack: Python/Django, Django REST Framework, PostgreSQL/MySQL/MariaDB/SQLite, Redis y frontend React.
- El README define un sistema de control de stock y partes de bajo nivel, con backend de base de datos, interfaz web, API REST, módulo Python y plugin interface.
- Valor para Rubrova: modelo de partes/SKU, stock por ubicación, trazabilidad, API, extensiones, datos y operaciones de depósito. Es una fuente técnica atractiva para revisar modelos de inventario, seriales/lotes, unidades, barcode y plugins.
- Riesgo: es una aplicación completa con su propio modelo de stock. Integrarlo como servicio externo sin designar un único ledger duplicaría existencias y movimientos.
- Recomendación: inspeccionar migraciones, modelos, endpoints, plugin API, conteo y movimientos; reutilizar patrones o componentes independientes, no incorporar toda la aplicación como segunda autoridad de inventario.

Fuente: https://github.com/inventree/InvenTree

## N. OpenBoxes — WMS y gestión de supply chain

- Repositorio: https://github.com/openboxes/openboxes
- Rama inspeccionada: develop; README declara EPL-1.0.
- Propósito: WMS/inventario de propósito general, surgido para cadenas de abastecimiento con restricciones de recursos. El proyecto destaca eficiencia, flexibilidad, accesibilidad y soporte a cadenas de suministro complejas.
- Valor: recepción, inventario, ubicaciones, transferencias y operación de almacenes. Tiene guías de usuario, instalación, comunidad y demo.
- Límite: aplicación completa con su propia persistencia y flujo de stock; no es un paquete de funciones independiente. Su origen en health supply chain implica estudiar bien los modelos y no asumir encaje directo con retail argentino.
- Recomendación: utilizarlo como referencia para workflows de recepción, movimientos, conteos, transferencia y trazabilidad. No crear una segunda fuente de verdad de stock en Rubrova.

Fuentes:
- https://github.com/openboxes/openboxes
- https://docs.openboxes.com/en/latest/

## O. OpenWMS.org — ejecución avanzada de almacenes y material flow control

- Repositorio: https://github.com/openwms/org.openwms
- Rama inspeccionada: master; el README requiere JDK 25 y describe Java 25/Spring Boot 4.1, RabbitMQ y componentes distribuidos.
- Licencias: el root tiene Apache-2.0 y la tabla del proyecto distingue explícitamente módulos públicos Apache-2.0, privados GPLv3 y componentes privados/preview. Cada repo/módulo se licencia por separado.
- Propósito: WMS extensible más Material Flow Control (MFC) para almacenes automáticos y manuales. La arquitectura orquesta servicios de inventario, movimientos, tareas, picking, transporte y drivers cercanos a sensores/PLC.
- Valor: arquitectura de composición de servicios, ownership por componente, APIs de negocio, eventos, dispositivos y movimiento físico.
- Riesgo: infraestructura distribuida considerable, Java 25/Spring, módulos privados y control de hardware con tiempos de respuesta exigentes. Es mucho más complejo que el depósito típico de una pyme.
- Recomendación: no adoptarlo como base. Guardar como referencia de segunda etapa si Rubrova administra depósitos automatizados, transportadores, sensores o varias instalaciones grandes. Solo evaluar repositorios Apache públicos, nunca asumir que el catálogo completo comparte la licencia root.

Fuentes:
- https://github.com/openwms/org.openwms
- https://wiki.openwms.cloud/projects/openwms/wiki/00-dot-02-business-services

## P. Automatización y workflows: Activepieces, Temporal, Kestra y n8n

### Activepieces
- Repositorio: https://github.com/activepieces/activepieces
- MIT para el core fuera de packages/ee y rutas enterprise especificadas en la licencia.
- Builder visual de automatizaciones e integraciones; útil para tareas de back-office, alertas y sincronización periférica.
- No permitir que sus flujos modifiquen directamente el ledger sin pasar por APIs idempotentes y permisos de Rubrova.

### Temporal
- Repositorio: https://github.com/temporalio/temporal
- MIT.
- Motor de durable execution para workflows largos que sobreviven reinicios, con historial y reintentos. Encaja conceptualmente en emisión fiscal, integración logística, importación de lotes y conciliaciones.
- Requiere backend/worker/DB y competencias operativas; puede ser excesivo al inicio. Primero definir workflow y pruebas; decidir después si hace falta el motor.

### Kestra
- Repositorio: https://github.com/kestra-io/kestra
- Apache-2.0.
- Orquestación declarativa de flujos de datos, infraestructura y operaciones.
- Puede servir para pipelines, conciliaciones y tareas programadas, pero no es el motor transaccional de una venta.

### n8n
- Repositorio: https://github.com/n8n-io/n8n
- Sustainable Use License, source-available; no OSI open source. La licencia del README/archivo también excluye ramas distintas de master y separa carpetas .ee.
- Es útil como referencia y puede contemplarse para determinados workflows internos si se revisa la licencia vigente; no incorporarlo como código abierto ni como núcleo de Rubrova.

**Conclusión:** usar APIs/adaptadores de Rubrova para operaciones de negocio. Una herramienta de automatización externa puede coordinar tareas periféricas, pero no sustituye estados durables, permisos, audit trail ni idempotencia del dominio.

Fuentes:
- https://github.com/activepieces/activepieces
- https://github.com/temporalio/temporal
- https://github.com/kestra-io/kestra
- https://github.com/n8n-io/n8n

## Q. Paperless-ngx — archivo documental OCR

- Repositorio: https://github.com/paperless-ngx/paperless-ngx
- Rama inspeccionada: dev; licencia GPL-3.0.
- Sistema self-hosted de archivo y búsqueda de documentos, con OCR y metadatos.
- Valor: referencia para capturar facturas de proveedores, remitos, constancias de entrega, contratos y comprobantes; indexar y vincularlos a los objetos de Rubrova.
- Límite: no reemplaza compras, cuentas a pagar, impuestos ni contabilización. Si se usa como servicio separado, Rubrova mantiene la referencia documental y el vínculo de negocio; no se crea un segundo registro contable.
- Recomendación: evaluar ingestión desde carpetas/email/escáner y extracción asistida, manteniendo original inmutable, checksum, permisos y revisión humana.

Fuente: https://github.com/paperless-ngx/paperless-ngx

## R. Analítica tabular: DuckDB, Polars y Apache Superset

La separación recomendada es:
- PostgreSQL/ERP como OLTP transaccional y autoridad de los registros.
- DuckDB para consultas analíticas locales y procesamiento por lotes.
- Polars para preparación/transformación de datasets cuando se requiera alto rendimiento.
- Superset para dashboards de solo lectura sobre vistas y datasets analíticos.
- Ninguna de estas herramientas recibe permisos para escribir ventas, caja, pagos, movimientos de inventario o libros contables.
- Las métricas deben tener definiciones versionadas, filtros explícitos, fuente, fecha de actualización y conciliación con los datos de origen.

Fuentes:
- https://github.com/duckdb/duckdb
- https://github.com/pola-rs/polars
- https://github.com/apache/superset

Las referencias son candidatas de código, patrones o servicios de soporte; ninguna está incorporada ni ejecutada en Rubrova. La decisión de integración exige revisión de licencias, dependencias, versión, seguridad, ownership de datos y pruebas locales.
