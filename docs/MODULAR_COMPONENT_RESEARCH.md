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
