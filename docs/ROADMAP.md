# Plan de trabajo

**Revisión:** 20 de noviembre de 2026  
**Dirección prioritaria:** POS y operación comercial → ERP de gestión → contabilidad/fiscalidad → análisis y reportes → perfiles sectoriales y canales → logística avanzada.

## Estado real

Rubrova se encuentra en **Fase 0: selección del núcleo operativo**. Hay visión, alcance, requisitos POS, modelo de dominio, arquitectura, investigación de plataformas, shortlist de código reutilizable y un dataset sintético. Todavía no hay aplicación funcional ni se incorporó código externo.

El validador del dataset tiene 27 pruebas aprobadas y el fixture canónico es válido en CI (20/11/2026). El benchmark separado de demanda mensual con StatsForecast 2.1.1 también terminó correctamente (20/11/2026). Estas ejecuciones validan fixtures y cálculos sintéticos; no instalan ni prueban un POS, ERP, API, integración, backup o flujo real de Rubrova.

La dirección completa está en [Plan maestro de implementación](MASTER_IMPLEMENTATION_PLAN.md). La selección reuse-first está en [Estrategia de reutilización](REUSE_FIRST_IMPLEMENTATION_STRATEGY.md) y la prueba comparativa en [Evaluación de plataformas](PLATFORM_EVALUATION.md). El diseño ejecutable por etapas de demanda, rentabilidad y marcas queda especificado en [Inteligencia de demanda, rentabilidad y marcas](DEMAND_AND_MARGIN_INTELLIGENCE.md).

## Prioridad del producto

El seguimiento de envíos **no es una prioridad de inicio**. Se conserva en el modelo de dominio para que una venta pueda despacharse después y tenga uno o varios envíos, pero los conectores de transportistas se dejan para la última etapa.

| Orden | Resultado | Qué tiene que resolver |
|---:|---|---|
| 1 | POS y venta | Carrito, catálogo, clientes, precios, descuentos, cobro, vuelto, pagos mixtos, caja, devoluciones y ticket |
| 2 | ERP de gestión | Stock, depósitos, compras, proveedores, recepción, costo, clientes, cuentas corrientes y sucursales |
| 3 | Contabilidad y fiscalidad argentina | Libro mayor, cuentas, bancos, impuestos, ARCA, facturas, notas y conciliación |
| 4 | Reportes, control de gestión e inteligencia comercial | Ventas, caja, compras, inventario, rentabilidad por producto/marca/canal/área, preferencias de marcas, tendencias y pronósticos trimestrales/estacionales |
| 5 | Capacidades sectoriales | Recetas, producción, mermas, lotes, vencimientos, mayorista, distribución y servicios B2B |
| 6 | Canales externos | Ecommerce, Mercado Libre, WhatsApp, delivery y pedidos de otras plataformas |
| 7 | Logística avanzada | Transportistas, tarifas, etiquetas, retiro, entrega, tracking y reclamos |

Las dimensiones que afectan costos y reportes (unidad de negocio, canal, sucursal, centro de costo, depósito y proyecto) se incorporan desde el primer modelo. Se posterga el desarrollo sofisticado de BI, no la captura correcta de sus datos.

## Fase 0 — seleccionar la base del POS y la gestión

**Objetivo:** decidir qué aplicación o composición puede resolver el circuito POS + ERP sin comprometer propiedad de datos, operación local, recuperación ni arquitectura.

### Orden de evaluación

1. **ERPNext 16 / Frappe 16:** prueba inicial por la cobertura de POS, inventario, compras, contabilidad, dimensiones y reportes.
2. **MyCompany 6.2 / lsFusion:** prueba inicial por su Retail POS integrado y amplitud de CRM, ventas, compras, inventario, fabricación y facturación.
3. **Tryton 8.0 + tryton-ar 8.0:** candidato prioritario porque existe un conjunto de ocho ramas argentinas alineadas. Se debe probar instalación, tests y homologación antes de elegirlo. Tryton 8.2 queda como actualización posterior con port/revalidación.
4. **Dolibarr 24.0.3:** filtro de menor complejidad para POS/ERP y API.
5. **Posnic 1.9.2:** referencia POS secundaria, no candidato a ERP principal. Revisar licencias y dependencias, localización india, límites offline y compatibilidad de escritorio.

No se comparan por folleto ni por número de módulos. Se ejecuta el mismo circuito: catálogo → carrito editable → venta → pago y vuelto → caja → stock → devolución → reportes → recuperación.

### Tareas pendientes

- [ ] Fijar tags/commits y dependencias actuales de ERPNext 16, MyCompany 6.2, Tryton 8.0 + ocho módulos tryton-ar 8.0 y Dolibarr 24.0.3.
- [ ] Ejecutar filtro documental, de licencia, instalación, API, exportación, backup y restauración en una instancia limpia y en un equipo distinto.
- [ ] Probar ERPNext y MyCompany con el flujo POS completo y jornada simulada.
- [ ] Instalar Tryton 8.0 con las ocho ramas tryton-ar fijadas en el [lock reproducible](TRYTON_ARGENTINA_8_0_LOCK.md), ejecutar tests y homologar WSFE/WSFEX; dejar Tryton 8.2 como upgrade posterior sujeto a port y revalidación.
- [ ] Ejecutar filtro corto de Dolibarr y decidir si entra en la comparación profunda.
- [ ] Mantener Posnic como comparador POS sólo si aporta una ventaja medible frente al POS incluido en los ERP.
- [ ] Llevar como máximo dos candidatos a la prueba profunda P01–P67.
- [ ] Decidir qué responsabilidades pueden quedar en una aplicación de dominio externa y qué dominios requieren servicios Rubrova independientes.
- [ ] Documentar decisión, evidencia, riesgos, licencias, costo de adaptación y camino de actualización.

**Criterio de salida:** candidato/composición elegida con pruebas reproducibles; autoridades de venta, pago, caja, stock, contabilidad y fiscalidad definidas; no se construyen módulos propios sobre una plataforma aún no seleccionada.

## Fase 1 — primera entrega: POS con gestión mínima real

**Objetivo:** tener un circuito comercial que se pueda usar y auditar, no una pantalla de demostración.

Alcance:

- Organización, sucursal, usuarios, roles, dispositivos, caja y depósito básicos.
- Catálogo, variantes, códigos de barras, unidades, productos pesables, precios y clientes.
- Capturar desde el inicio marca, fabricante y segmento comercial configurable por categoría (primera/líder, segunda, económica, propia, alternativa/genérica), con vigencia desde/hasta, motivo, responsable e historial; no inferir el segmento sólo por precio.
- Capturar unidad base y comparable, contenido neto, equivalencias de pack/caja/bulto y precios/costos históricos con vigencias. La venta conserva el precio, costo de referencia, marca, segmento y presentación aplicados en ese momento.
- Registrar disponibilidad y existencia por producto/ubicación, reservas, tránsito, períodos sin stock, productos no vendibles, horarios, cambios de surtido, promociones y demanda no satisfecha cuando se pueda observar; son datos obligatorios para corregir la demanda censurada.
- Carrito editable antes del cobro; descuentos, promociones e impuestos recalculables.
- Efectivo, vuelto, medios mixtos y registro del resultado de cada pago.
- Apertura, movimientos, arqueo y cierre de caja.
- Venta, ticket propio, cancelación y devolución parcial/total.
- Reservas y movimientos de stock con una autoridad única y ledger trazable.
- Documento fiscal separado del ticket, con estados visibles.
- Lector e impresora mediante adaptadores; terminal de pago real sólo tras pruebas de sandbox/homologación.
- Panel operativo con ventas netas, devoluciones, medios de pago, diferencia de caja y productos vendidos.
- Persistencia local, idempotencia, audit trail, backup automático, portable y verificable, restauración guiada en Windows limpio y reinicio del proceso. La copia externa debe poder continuar en otro equipo.

**Criterio de salida:** una jornada repetible sin pérdida ni duplicación; ventas, pagos, caja, stock y documento fiscal conciliados; recuperación demostrada.

## Fase 2 — ERP administrativo

**Objetivo:** administrar el negocio de punta a punta detrás de la caja.

Alcance:

- Clientes/empresas, proveedores, contactos, condiciones y listas de precios.
- Cuenta corriente, crédito, vencimientos, saldos y límites con aprobación.
- Compras, órdenes, recepción parcial/total, devoluciones a proveedor y costos accesorios.
- Depósitos, transferencias, conteos, ajustes autorizados, reservas, lotes y vencimientos según el rubro.
- Ledger de inventario valorizado con método documentado (FIFO/promedio móvil u otro soportado por el núcleo elegido), costo de cada recepción, descuentos/bonificaciones, flete y costos puestos; distinguir costo histórico, costo vendido y costo de reposición.
- Costos variables atribuibles (comisiones de medios de pago/canales, embalaje, preparación y entrega) y gastos directos/compartidos con reglas de asignación versionadas; nunca publicar rentabilidad firme con costos ausentes.
- Importación masiva, normalización y validación de datos.
- Sucursales y varias áreas de negocio; captura de unidad de negocio y centro de costo por línea cuando corresponda.
- Documentos, adjuntos, historial y auditoría.

**Criterio de salida:** ventas, recepciones, compras, costo y disponibilidad coinciden; toda diferencia tiene origen, responsable y tratamiento.

## Fase 3 — contabilidad, fiscalidad y administración argentina

**Objetivo:** convertir los hechos comerciales en resultados contables/fiscales confiables.

Alcance:

- Libro mayor, plan de cuentas, diarios, períodos, cierres y asientos.
- Cuentas por cobrar/pagar, bancos, conciliación, medios de pago, liquidaciones y comisiones.
- Impuestos, tipos documentales, puntos de venta, numeración y reglas argentinas.
- ARCA en homologación; emisión, consulta, estados inciertos, nota de crédito/débito y recuperación.
- CUIT, condición fiscal, retenciones/percepciones aplicables.
- Exportación e importación idempotente para el estudio o sistema contable usado (Tango, Catedral, Bejerman, Xubio, Colppy u otro).
- Conciliación desde la venta hasta el pago, el movimiento de stock, el comprobante y el asiento.

Bigcapital sólo se prueba si la contabilidad de la plataforma elegida no alcanza. No se mantienen libros mayores paralelos.

**Criterio de salida:** débitos/créditos, saldos, impuestos, ventas y documentos conciliados; ARCA homologado antes de cualquier habilitación productiva.

## Fase 4 — reportes y control de gestión

### Capacidades obligatorias de inteligencia comercial

- Seguimiento diario, semanal, mensual, trimestral y por estación del hemisferio sur.
- Detección temprana de productos emergentes, acelerados, desacelerados, estancados y en caída.
- Pronóstico por SKU/familia, marca, categoría, sucursal, canal y área, con horizonte explícito.
- Comparación interanual equivalente y ajuste por días sin stock, promociones, cambios de precio y surtido.
- Alertas y recomendaciones de compra/reposición antes de cada trimestre y estación, considerando lead time, stock de seguridad y presupuesto.
- Rentabilidad absoluta y porcentual por producto/marca/categoría/cliente; distinguir facturación de contribución real.
- Perfil 360 por cliente/empresa: productos, categorías, marcas/segmentos, preferencias de canal, recurrencia, RFM, retención, CLV y contribución, con ventas anónimas preservadas.
- Recomendaciones por cliente (recompra, sustitución, complementos y recuperación) sólo con evidencia suficiente, permiso de contacto cuando corresponda y aprobación humana.
- Segmentación configurable de primeras marcas, segundas, económicas, propias y alternativas; medir participación por unidades, tickets, facturación y ganancia.
- Detección de sustitución y cambios de preferencia entre marcas, controlando faltantes y diferencias de presentación/precio por unidad.
- Simulación de precio, promoción, surtido y compra; toda ejecución requiere aprobación.
- Medición posterior del pronóstico frente al resultado real, con error y sesgo por horizonte/segmento.


**Objetivo:** transformar datos correctos en decisiones sin inventar costos o conclusiones.

Orden de construcción:

1. Cierre diario: ventas netas, tickets, ticket promedio, descuentos, devoluciones, pagos y caja.
2. Ventas: artículo, variante, marca, categoría, cajero, cliente, sucursal, canal y área.
3. Inventario: disponible, reservado, en tránsito, rotación, cobertura, quiebres, excedentes, antigüedad y vencimientos.
4. Costos y margen: costo vendido, margen bruto, contribución neta de comisiones, embalaje y logística, precio de reposición y GMROI.
5. Compras y proveedores: cumplimiento, plazos, costos, diferencias y propuesta de reposición.
6. Finanzas: cuentas por cobrar/pagar, mora, caja, bancos, flujo y estados contables.
7. Rentabilidad por área y consolidado: minorista, ecommerce, mayorista/distribución y servicios.
8. Perfil 360 por cliente: RFM, retención, marcas/productos preferidos, contribución y acciones sugeridas; exportar datos fuente y explicar cada segmento.

Primero usar los reportes nativos del ERP y validar su costo/ledger contra movimientos. Para proyecciones, probar StatsForecast como primera biblioteca de modelos estadísticos; MLForecast queda condicionado a datos exógenos e historial suficientes, y HierarchicalForecast para una etapa posterior cuando haya que reconciliar SKU/familia/marca/categoría/sucursal/canal. DemandSense se inspecciona como referencia MIT de demanda intermitente, backtesting y escenarios, pero su madurez es baja; DemandOS queda como referencia para inspección: la ausencia de licencia no concede permiso para copiar o modificar su código; reproducir ideas de forma independiente o pedir autorización. Para el análisis local, probar DuckDB sobre snapshots/Parquet canónicos y elegir como máximo una herramienta BI posterior (Metabase o Superset) si existe una necesidad multiusuario. La comparación de primera/segunda marca se implementa con reglas y métricas propias de Rubrova: no se sustituye por ABC ni por notebooks exploratorios. Ninguna herramienta analítica escribe en ventas, pagos, inventario o contabilidad. El detalle de licencias, decisiones y pruebas está en [Inteligencia de demanda, rentabilidad y marcas](DEMAND_AND_MARGIN_INTELLIGENCE.md).

**Criterio de salida:** las métricas cuadran con los movimientos originales, muestran fórmula/fuente/filtros/actualización y declaran costos o datos faltantes. Los reportes no bloquean la caja. La inteligencia comercial demuestra backtesting, análisis ajustado por disponibilidad, tableros de rentabilidad y participación de marcas, y perfil 360 reproducible por cliente; las recomendaciones declaran confianza y no ejecutan compras/precios automáticamente.

## Fase 5 — perfiles sectoriales y capacidades de expansión

- Gastronomía, panadería y rotisería: recetas, BOM, rendimiento, merma, tandas de producción, comandas, cocina, pesables y vencimientos.
- Mayorista/distribución: mínimos, múltiplos, escalas, listas por cliente, crédito, entregas parciales y costo de servir.
- Servicios B2B: contratos, recurrencias, agenda, SLA, órdenes de trabajo, técnicos, horas, materiales, viáticos y rentabilidad.
- Varias áreas: permisos, recursos y resultados separados; consolidado sin ingresos internos ficticios.

**Criterio de salida:** perfiles que reutilizan los mismos maestros y servicios, sin duplicar clientes, ventas, inventario ni reglas contables.

## Fase 6 — canales e integraciones comerciales

- Ecommerce, pedidos por WhatsApp, Mercado Libre, delivery y otros canales reales.
- Integrar un canal por vez; probar pedidos, cancelaciones, pagos, comisiones y devoluciones.
- Webhooks firmados, idempotencia, estados externos, conciliación y prevención de doble factura/sobreventa.
- Spree o Saleor sólo como posible canal ecommerce, nunca como ERP/POS paralelo.
- PowerSync sólo si una prueba demuestra valor para lecturas/tareas offline; no coordina la última unidad de stock.

**Criterio de salida:** cada pedido externo se reconcilia con venta, pago, inventario y fiscalidad sin duplicados.

## Fase 7 — logística avanzada

El modelo de fulfillment y la posibilidad de agregar una guía después de vender existen desde el diseño inicial. La construcción de integraciones se posterga:

1. Retiro por cliente y entrega/reparto propio.
2. Carga manual de operador, guía, paquete y eventos.
3. Andreani, Correo Argentino PAQ.AR y OCA con credenciales de QA.
4. Vía Cargo como tracking externo mientras no haya API de booking verificada.
5. Agregadores, cotización, etiquetas, manifiestos, reclamos y analítica logística.
6. Kangu sólo si se confirma operación argentina.

**Criterio de salida:** los transportistas no controlan venta, pago ni stock maestro; cada envío conserva su vínculo con el pedido y su trazabilidad.

## Calidad transversal y definición de terminado

Todas las fases deben pasar las pruebas que correspondan:

- POS: rapidez, accesibilidad, teclado, lector, pantalla táctil, carrito editable, devoluciones y permisos.
- Integridad: idempotencia, CAS para stock, caja reconciliada y ausencia de doble emisión.
- Resiliencia: corte de red, terminación abrupta del proceso, reintentos, broker caído, restore y rollback.
- Seguridad: permisos en servidor, aislamiento por negocio/sucursal, gestión de secretos y auditoría.
- Datos: importación validada, fórmulas trazables, moneda/redondeos y costo explícito.
- Operación: instalación local, actualización, documentación en español y recuperación guiada por una persona autorizada después de reinstalar Windows o cambiar la PC.
- Reutilización: versión/commit, licencia por archivo/dependencia, avisos, pruebas y costo de mantenimiento.

Ninguna capacidad se marca terminada porque exista una pantalla, documentación o demo. Se requiere evidencia reproducible.

## Entregables de investigación ya completados

- [x] Catálogo de código reutilizable y estrategia reuse-first.
- [x] Requisitos POS, checkout, efectivo, vuelto, pagos mixtos y terminales.
- [x] Modelo de dominio que separa venta, pago, stock, comprobante y envío.
- [x] Arquitectura de servicios de dominio, APIs/eventos, ownership, idempotencia, CAS, Outbox/Inbox y recuperación.
- [x] Dataset de evaluación y validador automático: 27/27 pruebas de fixture aprobadas en CI (20/11/2026).
- [x] Benchmark mensual de demanda regular e intermitente con StatsForecast 2.1.1 y baselines; CI aprobado sobre 48 meses sintéticos por serie (20/11/2026).
- [x] Investigación de ERPNext, MyCompany/lsFusion, Tryton, Dolibarr y Posnic.
- [x] Revisión de la localización argentina Odoo y de tryton-ar; se encontraron ocho ramas coordinadas 8.0 con manifiestos y tests; instalación y homologación pendientes.
- [x] Shortlist de componentes para fiscalidad, importación, hardware, analítica, producción, ecommerce, backup y logística.
- [x] Requisitos de reportes, métricas y rentabilidad por área.
- [x] Diseño detallado de demanda, pronósticos, rentabilidad y análisis de primeras/segundas marcas con herramientas y licencias candidatas registradas.
- [x] Especificación de captura temporal para canales, formatos, compras, recepción, disponibilidad, pagos, caja, cajeros, promociones, reclamos y devoluciones.
- [x] Matriz de exportación portable e investigación de DuckDB, Parquet/Arrow, Polars, dbt Core, Evidence, Superset y Metabase.
- [x] Diseño de identidad de pagos por canal, conciliación y límites de uso de datos de pagador; shortlist de SDK/API de Mercado Pago, Payway, Getnet, MODO y Fiserv.
- [x] Evaluación de S-Tech como proveedor potencial de terminales, efectivo inteligente y autoservicio.

## Próximos pasos concretos

1. Ejecutar el filtro comparativo POS + ERPNext 16 y MyCompany 6.2 con el mismo dataset y circuito.
2. Ejecutar Tryton 8.0 en paralelo con las ramas argentinas 8.0; instalar el conjunto, ejecutar tests y homologar. Tryton 8.2 se evalúa como actualización posterior.
3. Pasar Dolibarr 24.0.3 por el filtro corto y llevar como máximo dos finalistas a P01–P67.
4. Resolver las puertas de licencia, API, localización argentina, exportación, backup/restore y límite de dominio. P49 añade la comprobación de historial comercial; P50–P57 validan temporalidad, caja, promociones, reclamos y exportaciones; P58–P60 validan el perfil 360; P61–P67 validan identidad de pagos, conciliación, privacidad, PCI e integraciones.
5. Elegir la base del primer circuito y recién entonces implementar/adaptar las brechas concretas.
6. Ampliar el benchmark con quiebres de stock censurados, promociones, cambios de precio, productos nuevos y más horizontes; preparar una entrada de datos reales una vez elegida la plataforma POS/ERP. Evaluar MLForecast y HierarchicalForecast sólo después de medir la mejora frente a baselines.

El requisito de copia portable y recuperación en PC nueva está en [Copias de seguridad y recuperación](BACKUP_AND_MIGRATION_STRATEGY.md). El backup de aplicación será portable y sin cifrado propio; se valida mediante checksums, reconciliación y restauración en PC nueva. El cifrado del disco completo puede habilitarse opcionalmente desde el sistema operativo.

La captura desde el primer día, los escenarios P50–P57 y la capa de BI/exportación se especifican en [Captura de datos y base analítica](DATA_CAPTURE_AND_ANALYTICAL_FOUNDATION.md). El Perfil 360 y las pruebas P58–P60 quedan en [Perfil 360 e inteligencia por cliente](CUSTOMER_360_AND_INTELLIGENCE.md). La comparación de alternativas de mercado se documenta en [Revisión competitiva](COMPETITIVE_MARKET_REVIEW.md). La arquitectura de pagos está en [Identidad del pagador y conciliación](PAYMENT_IDENTITY_AND_RECONCILIATION.md); S-Tech queda como proveedor complementario a evaluar en [S-Tech para Rubrova](S_TECH_EVALUATION.md), no como núcleo POS+ERP.

La [investigación logística argentina](ARGENTINA_LOGISTICS_INTEGRATION.md) se conserva, pero no desplaza estos pasos ni condiciona el inicio del producto.
