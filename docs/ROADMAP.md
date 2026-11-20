# Plan de trabajo

**Revisión:** 20 de noviembre de 2026  
**Dirección prioritaria:** POS y operación comercial → ERP de gestión → contabilidad/fiscalidad → análisis y reportes → perfiles sectoriales y canales → logística avanzada.

## Estado real

Rubrova sigue en **Fase 0: piloto integrado POS + ERP**, pero ya superó el primer hito de runtime: MyCompany 6.2 arranca en CI Linux x86_64, carga la extensión Rubrova, permite login, navegación hasta Punto de venta y apertura de un turno sintético. Aún no hay una instalación en el equipo de uso ni una jornada comercial aceptada. Tryton 8.0 + tryton-ar 8.0 permanece como contraste fiscal argentino. El repositorio conserva diseño, investigación, validadores sintéticos y una extensión pequeña sobre MyCompany; no contiene una implementación propia completa de POS/ERP ni código fuente upstream copiado.

El validador del dataset tiene 34 pruebas aprobadas y el fixture canónico es válido en CI (20/11/2026), incluidas reglas sintéticas de identidad de pagos y minimización de datos. El benchmark separado de demanda mensual con StatsForecast 2.1.1 también terminó correctamente. Además, el run [44810418808](https://github.com/JavierGrecco/Rubrova/actions/runs/44810418808) pasó sus cuatro jobs, incluido el runtime real Linux x86_64: MyCompany arrancó, Chromium abrió el POS y se abrió un turno sintético. Esa prueba valida arranque, navegación y estado de sesión, no el circuito de venta completo, pagos, stock, devoluciones o instalación local.

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

## Fase 0 — arrancar el piloto MyCompany 6.2

**Objetivo:** instalar una suite POS + ERP reproducible, extenderla desde fuera de su núcleo y probar el circuito antes de crear módulos equivalentes.

### Orden de ejecución

1. **MyCompany 6.2 / lsFusion:** primer piloto integrado; utilizar Retail POS, sesiones, pagos, devoluciones, inventario, costos, compras y facturación.
2. **Tryton 8.0 + tryton-ar 8.0:** contraste fiscal argentino y alternativa si MyCompany no supera las puertas.
3. **ERPNext 16 / Frappe 16:** reserva; reabrir sólo ante una brecha funcional o técnica medida.
4. **Dolibarr 24.0.3:** filtro corto si las opciones principales no superan las puertas.
5. **Posnic 1.9.2:** referencia POS secundaria, nunca dueño paralelo de ventas o inventario.

El lock de versión, la extensión modular, los scripts de preparación y el detalle de módulos están en [Inicio de implementación](IMPLEMENTATION_START.md).

### Tareas de esta fase

- [x] Fijar MyCompany 6.2 por tag y commit; registrar los hashes oficiales del instalador Windows y del JAR.
- [x] Inspeccionar el código fuente de POS, sesiones, pagos mixtos, efectivo, devoluciones, inventario, costos y compras.
- [x] Crear el punto de entrada RubrovaCustom y el módulo separado RubrovaPOSLocalization, con el glosario es_AR.
- [x] Agregar captions localizados para el primer flujo POS en RubrovaPOSLocalization; validar que los 36 identificadores propios tienen traducción.
- [ ] Cargar los dos módulos Rubrova en MyCompany 6.2 real, confirmar los captions y traducir filtros/mensajes de error heredados.
- [x] Incorporar validación automática del lock, composición de módulos y traducciones; workflow correcto en CI.
- [x] Probar el staging de despliegue Docker en un directorio temporal: copia de los tres archivos, conservación de settings y backups, sin invocar Docker.
- [x] Preparar scripts de despliegue de RubrovaCustom + RubrovaPOSLocalization para Docker, Linux nativo y Windows nativo, con copia previa de settings y módulos existentes.
- [x] Registrar limitación de arquitectura de imagen Docker MyCompany 6.2 en ARM64.
- [ ] Ejecutar la instalación y carga en el equipo anfitrión; la CI no puede sustituir esta prueba.
- [ ] Descargar los artefactos, verificar hashes en la máquina de ejecución e instalar en entorno local aislado.
- [ ] Ejecutar apertura → escaneo → carrito → pagos mixtos/vuelto → venta → stock → devolución → cierre.
- [ ] Probar dos cajas, pagos pendientes/repetidos, caída/reinicio, exportación, backup y restauración.
- [ ] Contrastar con Tryton 8.0 fiscalidad y comprobantes; homologar ARCA antes de producción.

**Criterio de salida:** instalación reproducible, extensión cargada, POS completo en español, permisos, integridad de ventas/pagos/caja/stock, recuperación, exportación y restauración demostradas. Hasta entonces el piloto no se habilita para uso diario.

### Cierre actual de Fase 0 y próximo bloque

- [x] MyCompany 6.2 fijado y ejecutado en CI Linux x86_64.
- [x] Extensión RubrovaCustom + RubrovaPOSLocalization cargada sin modificar módulos upstream.
- [x] Login, navegación Comercio → Punto de venta y renderizado del formulario validados con Chromium.
- [x] Caja sintética seleccionada y turno `SM/000001` abierto en la base descartable de CI.
- [ ] Buscar el producto sintético, añadirlo al recibo y verificar línea, cantidad y precio.
- [ ] Confirmar una venta sintética en efectivo y conciliar recibo, pago, caja e inventario.
- [ ] Probar vuelto/pago mixto, devolución, cierre y conciliación.
- [ ] Completar traducción crítica, permisos, exportación y backup/restauración.

**Dirección inmediata:** no sumar otra suite ERP ni módulos periféricos. Primero completar una venta reproducible de punta a punta sobre MyCompany; sólo incorporar código especializado cuando una brecha concreta esté observada y medida.

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
- [x] Dataset de evaluación y validador automático: 34/34 pruebas de fixture aprobadas en CI (20/11/2026).
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
