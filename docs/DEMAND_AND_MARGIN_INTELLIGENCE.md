# Inteligencia de demanda, rentabilidad y marcas

**Revisión:** 25 de noviembre de 2026  
**Estado:** diseño funcional y selección preliminar de herramientas; ninguna biblioteca de forecasting o BI está instalada ni aprobada para producción.

Este documento es la referencia de implementación para que las capacidades de demanda, rentabilidad y preferencia entre marcas no se pierdan entre las fases del POS, ERP y analítica. Complementa el [Plan de trabajo](ROADMAP.md), el [Plan maestro](MASTER_IMPLEMENTATION_PLAN.md), la [Inteligencia del negocio](BUSINESS_INTELLIGENCE.md) y el [Catálogo de código reutilizable](CODE_REUSE_CATALOG.md).

## 1. Principios y límites

1. La base transaccional elegida conserva la autoridad sobre ventas, pagos, caja, compras, inventario, costos y contabilidad.
2. El módulo analítico lee hechos y ledgers conciliados mediante consultas, exportaciones o read models versionados. No modifica ventas, stock, pagos, precios ni asientos.
3. El cálculo económico debe poder rastrearse hasta la venta, devolución, recepción, movimiento de stock, comisión, gasto y regla de asignación que lo originó.
4. Una predicción es una estimación con horizonte, cobertura y error medido; no es un dato observado ni una orden de compra.
5. La clasificación de marca representa una decisión comercial mantenida por el negocio. No se deduce solamente del precio ni se confunde con la clasificación ABC.
6. Toda recomendación de compra, precio, promoción, sustitución o liquidación requiere revisión y aprobación explícita.
7. Las bibliotecas se integran detrás de interfaces/adaptadores. El ERP elegido puede resolver ya algunas funciones y debe ser probado antes de duplicarlas.

## 2. Datos que se deben capturar desde el POS y el ERP

La inteligencia futura depende de la calidad del registro inicial. No se posterga la captura de estas dimensiones aunque los tableros avanzados lleguen en una fase posterior.

### 2.1 Producto, marca y presentación

- Identidad estable del producto, SKU, variante, categoría y subcategoría.
- Marca/fabricante y segmento comercial configurable por categoría: primera/líder, segunda, económica, propia, alternativa o genérica.
- Clasificación con vigencia desde/hasta, motivo, usuario y auditoría; conservar historial de cambios y permitir reclasificar sin alterar informes históricos.
- Unidad base y unidad comparable (kg, g, litro, ml, unidad, metro, etc.), contenido neto y equivalencia de pack/caja/bulto.
- Presentación, tamaño, precio y costo históricos con fechas efectivas.
- Proveedor, referencia de compra, lote y datos de vencimiento cuando corresponda.

La categoría define el contexto competitivo. Una marca puede ser primera en una categoría y alternativa en otra. No asumir que "más cara" equivale a "primera marca".

### 2.2 Hechos comerciales y disponibilidad

Cada línea de venta debe conservar producto/variante, cantidad en unidad base, precio aplicado, descuentos, impuestos, promoción, fecha/hora, caja, sucursal, canal, unidad de negocio, cliente cuando corresponda, y vínculo con devolución/anulación. Se guardan los valores relevantes al momento de la operación para no recalcular ventas históricas con el precio o nombre actuales.

Además se registran, por producto y ubicación y con granularidad operativa suficiente:

- Existencia, disponible, reservado, en tránsito y no vendible.
- Intervalos sin stock/quiebre, inventario contado y ajustes.
- Producto activo/inactivo, altas/bajas y cambios de surtido.
- Horarios de apertura/cierre y cierres extraordinarios cuando afecten la exposición.
- Promociones, precio regular/promocional, canal, vigencia y condiciones.
- Demanda no satisfecha o ventas perdidas cuando pueda registrarse con evidencia.

La ausencia de ventas durante un faltante no se interpreta como ausencia de demanda. Los cambios de precio, inflación, empaque, mix, horario, canal y surtido se distinguen del crecimiento real de unidades.

#### Períodos con quiebres: ajuste conservador de demanda censurada

El registro debe separar días de apertura, días con existencia vendible y días sin stock por SKU y ubicación. Las ventas observadas durante un faltante son demanda censurada: no deben interpretarse como la demanda total ni como una pérdida automática de preferencia.

Como primer control reproducible, Rubrova incorpora un estimador sencillo para evaluar períodos con disponibilidad suficiente:

\[
\widehat{D}=U_{\mathrm{obs}}\times\frac{D_{\mathrm{abiertos}}}{D_{\mathrm{disponibles}}}
\]

Donde los días disponibles son días de apertura menos días sin stock. La regla inicial sólo calcula una estimación cuando hay al menos 10 días disponibles y la disponibilidad representa al menos el 50% de los días abiertos. Los períodos por debajo de esos límites se marcan como insuficientes y no se extrapolan. La estimación se etiqueta como tal y jamás modifica ventas, inventario, caja ni contabilidad.

El nuevo fixture [stockout-censored-demand.json](fixtures/stockout-censored-demand.json) contiene 36 meses sintéticos y una verdad latente conocida sólo para puntuar el experimento. El benchmark compara ventas observadas y estimación ajustada sobre exactamente los mismos períodos elegibles. Este control valida la implementación de la fórmula y su comportamiento ante faltantes; **no demuestra precisión con datos reales ni sustituye un pronóstico temporal**. Supone que la tasa de demanda de los días disponibles representa los días agotados, supuesto que puede fallar ante promociones, estacionalidad intramensual, sustitución o quiebres concentrados en fines de semana.

La capacidad futura debe mejorar esta primera regla con granularidad diaria/horaria, demanda no satisfecha registrada, sustitución entre SKU, precio, promociones, calendario y backtesting sobre períodos reales conciliados. Los datos sintéticos nunca se mezclan con entrenamiento productivo.

Como referencias de diseño:
- [Odoo — reglas de reabastecimiento](https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/inventory/warehouses_storage/replenishment/reordering_rules.html): mínimos/máximos, horizonte y plazos de proveedor.
- [ERPNext — cantidad proyectada](https://docs.frappe.io/erpnext/projected-quantity): integra existencias, entradas previstas, pedidos y reservas.



#### Planificación temporal de stock y reposición (experimento separado)

Para conectar demanda con compras sin automatizar transacciones, se abrió un planificador de solo lectura. Estudia existencia física, reservas, compromisos de salida abiertos, recepciones confirmadas, lead time, período de revisión, demanda diaria elegible, stock de seguridad, MOQ y múltiplo de compra. Las reservas son parte de los compromisos de salida: se descuentan para calcular disponible inmediato, pero no se suman como una segunda demanda en la proyección. Las recepciones borrador, enviadas sin confirmación, canceladas, recibidas, vencidas o fuera del horizonte se excluyen.

El cálculo proyecta cada día hasta `lead time + período de revisión`, descuenta demanda no comprometida y salidas firmes antes de sumar las recepciones del día, y marca por separado un faltante anterior a la llegada del nuevo pedido. Si no hay al menos 12 períodos elegibles y un 50% de cobertura, suprime la sugerencia. El resultado es una cantidad propuesta redondeada por MOQ/múltiplo, nunca una orden de compra.

La especificación, el código y los seis escenarios sintéticos están en [Stock proyectado y planificación conservadora de reposición](PROJECTED_STOCK_AND_REPLENISHMENT.md), [plan_replenishment.py](../scripts/replenishment/plan_replenishment.py) y [fixture](fixtures/replenishment-planning.json). El prototipo aún debe conciliarse contra los ledgers reales de MyCompany y compararse con `PurchaseOrderShipmentAuto`; no está conectado a la base, no modifica existencias y no autoriza compras.

### 2.3 Costos y gastos

Se conservan las recepciones y costos de proveedor por fecha, cantidades, descuentos, bonificaciones, flete, seguro, impuestos no recuperables y demás costos atribuibles. También se registran comisiones de adquirentes/billeteras, costos variables de canal, embalaje, preparación, entrega y otros gastos que puedan vincularse de forma consistente.

La base debe distinguir costo histórico/contable, costo de mercadería vendida, costo de reposición y costo estimado. No se publica rentabilidad como dato firme si falta un costo válido: se muestra cobertura y faltantes.

## 3. Inteligencia de demanda y pronósticos

El fixture mensual y el comparador reproducible baselines/StatsForecast están en [historial sintético](fixtures/demand-monthly-history.json) y [benchmark](../scripts/forecasting/benchmark.py). La ejecución usa StatsForecast 2.1.1 fijado y backtesting walk-forward con horizonte de tres meses; sus resultados son evidencia técnica sobre datos sintéticos, no selección de producción.

### 3.1 Qué debe responder

Para SKU, familia, marca, categoría, sucursal, canal y unidad de negocio:

- Evolución diaria, semanal, mensual, trimestral y por estación del hemisferio sur; trimestres calendario y estaciones se muestran por separado.
- Productos emergentes, acelerados, creciendo sostenidamente, desacelerados, estancados y en caída.
- Cambios de unidades, tickets, ventas netas, margen, contribución y participación.
- Comparación contra período anterior y mismo período comparable del año anterior.
- Próxima demanda esperada por horizonte, con rango/intervalo, baseline, nivel de confianza y evidencia.
- Riesgo de quiebre, exceso, vencimiento e inmovilización de capital.
- Sugerencias de compra y reposición basadas en demanda prevista, disponibilidad, reservas, tránsito, lead time, mínimo/múltiplo, stock de seguridad, proveedor y presupuesto.

Las subas nominales en pesos no prueban por sí mismas un crecimiento de demanda. El sistema debe observar unidades comparables y mostrar separadamente el efecto precio, inflación, presentación y composición.

### 3.2 Estrategia de modelos

No se adopta un único algoritmo para todos los artículos. El pipeline debe comparar baselines sencillos y modelos especializados, con selección por comportamiento de la serie:

1. **Base obligatoria:** último valor, promedio móvil, naïve estacional y métodos sencillos de suavizado. Deben ser difíciles de superar y siempre figurar como referencia.
2. **Demanda regular:** evaluar StatsForecast para métodos estadísticos y econométricos (por ejemplo, ETS, AutoARIMA, Theta y modelos estacionales).
3. **Variables explicativas:** evaluar MLForecast cuando haya historial y calidad suficientes para incorporar precio, promociones, calendario, día de semana, canal y variables externas válidas.
4. **Demanda intermitente:** evaluar métodos Croston-SBA y TSB; no forzar métodos regulares en productos con muchos ceros.
5. **Agregación coherente:** evaluar HierarchicalForecast cuando haga falta reconciliar pronósticos de productos con familia, marca, categoría, sucursal, canal y total.
6. **Nuevos artículos o historial insuficiente:** usar reglas de lanzamiento, analogías validadas o baseline conservador; informar explícitamente que no hay historia suficiente para un pronóstico confiable.

La biblioteca es un motor de cálculo, no la definición de demanda. El servicio propio prepara datos, filtra períodos no comparables, selecciona modelos, persiste resultados y expone explicaciones y trazabilidad.

### 3.3 Evaluación de pronósticos

Cada corrida guarda: corte de datos, ventana de entrenamiento, horizonte, segmento, features, método, versión/commit de biblioteca, parámetros, baseline, predicción puntual, intervalos, fecha de cálculo y resultado real posterior.

Se ejecuta backtesting temporal con ventanas móviles y períodos de prueba no usados para elegir el modelo. Informar al menos WAPE, MAE, MASE cuando proceda, RMSE y sesgo; evaluar cobertura de intervalos cuando existan. Los resultados se desglosan por horizonte, categoría, tipo de demanda y nivel de agregación. Registrar drift, fallos de datos y fecha de revisión.

Como guía de madurez:
- Menos de 12 meses comparables: análisis preliminar; no afirmar estacionalidad anual recurrente.
- 12 a 24 meses: hipótesis iniciales sujetas a variación y backtesting.
- 24 a 36 meses comparables: mejor base para recurrencias, sin prometer precisión.
- Cambios importantes de precios, surtido, ubicación, horario o canal pueden romper la comparabilidad aunque exista historia larga.

Los intervalos se calibran con resultados medidos. No se confunden bandas heurísticas con intervalos probabilísticos calibrados.

### 3.4 Primera ejecución reproducible (fixture sintético)

La primera ejecución de GitHub Actions con StatsForecast 2.1.1 finalizó correctamente el 20/11/2026. El fixture contiene dos series de 48 meses, con cuatro cortes walk-forward y horizonte de tres meses.

- **Serie regular:** AutoETS obtuvo WAPE 0,0069; AutoTheta 0,0538; el baseline de último valor 0,0580. En este patrón sintético, AutoETS capturó bien la tendencia y estacionalidad.
- **Serie intermitente:** CrostonSBA obtuvo WAPE 1,360; el naive estacional obtuvo 1,417. El error sigue siendo alto (WAPE mayor a 1), por lo que el resultado demuestra dificultad real de la serie, no una predicción lista para compras.

Este resultado sólo demuestra que el experimento es ejecutable y reproducible. No representa ventas de Rubrova ni permite elegir un modelo productivo. La próxima comparación debe incluir datos reales ya conciliados, stockouts censurados, promociones, variaciones de precio y más horizontes.

## 4. Rentabilidad y costos

### 4.1 Autoridad del costo

El inventario valorizado y el libro contable del núcleo ERP son las fuentes de verdad. Antes de desarrollar un cálculo propio hay que probar qué método y reportes provee la plataforma elegida.

ERPNext es una referencia útil para estudiar su Stock Ledger y los métodos FIFO/promedio móvil. Su documentación explica cómo los movimientos de recepción/salida actualizan valorización y costo vendido, y por qué el informe Gross Profit no coincide necesariamente con el estado de resultados: trabajan desde fuentes y alcances distintos. No tratar su informe como una biblioteca aislada ni copiar fórmulas sin el ledger subyacente.

- [ERPNext: FIFO y Moving Average](https://docs.frappe.io/erpnext/fifo-and-moving-average)
- [ERPNext: por qué Gross Profit difiere de P&L](https://docs.frappe.io/erpnext/gross-profit-report-differences)
- [ERPNext fuente](https://github.com/frappe/erpnext)

La adopción de ERPNext como plataforma completa y cualquier extracción/adaptación de código requieren revisar su licencia, dependencias y obligaciones aplicables. No duplicar ledgers de costo entre ERPNext y Rubrova.

### 4.2 Métricas obligatorias

- Ventas netas, unidades, descuentos, bonificaciones y devoluciones.
- Costo de mercadería vendida por el método de valuación vigente.
- Ganancia bruta absoluta y margen bruto porcentual.
- Costo de reposición y margen de reposición separados del margen histórico realizado.
- Contribución después de comisiones de pago, costos variables, embalaje, preparación, canal y logística atribuible.
- Resultado después de costos directos; mostrar separadamente gastos compartidos asignados y no asignados.
- Inventario promedio y capital inmovilizado, rotación, cobertura, antigüedad y GMROI.
- Rentabilidad por SKU/variante, marca, categoría, proveedor, canal, sucursal y unidad de negocio.

El tablero identifica los cuatro cuadrantes: alta venta/alta rentabilidad, alta venta/baja rentabilidad, baja venta/alta rentabilidad y baja venta/baja rentabilidad. También detecta erosión de margen, promociones que venden más pero contribuyen menos, crecimiento rentable y exceso de capital inmovilizado.

GMROI se calcula con el período y método de valuación explícitos: ganancia bruta del período / inventario promedio valorizado a costo. No intercambiar margen porcentual, markup, ganancia absoluta y resultado operativo.

### 4.3 Costos compartidos y consolidación

Los costos directos se asignan donde se generan. Los compartidos se muestran inicialmente sin distribuir o se asignan con reglas versionadas, justificadas y visibles (por ejemplo, superficie, horas, pedidos, uso o ventas cuando sea adecuado). La vista consolidada elimina duplicaciones y concilia con contabilidad. Se distinguen devengado, facturado y cobrado.

## 5. Primeras, segundas y otras marcas

No se ha identificado un paquete open source especializado que resuelva esta clasificación comercial y su evolución con suficiente contexto. La lógica de segmento, vigencia, comparabilidad y sustitución se construye en el modelo de Rubrova.

La clasificación es independiente de ABC:
- **Segmento de marca:** posición comercial definida por categoría (primera/líder, segunda, económica, propia, alternativa/genérica).
- **ABC:** importancia relativa de un producto según una variable y período (ventas, unidades, contribución, inversión u otra).
- **XYZ:** variabilidad/estabilidad de la demanda.

El análisis compara participación por unidades, tickets, ventas netas, ganancia y contribución; evolución trimestral/estacional; precio normalizado por kg/litro/unidad; promociones; disponibilidad; margen; proveedor; sucursal, canal y área. Debe detectar productos que ganan unidades cuando otro pierde participación y distinguir sustitución probable de un simple faltante o cambio de precio.

Se pueden tomar como referencia metodológica notebooks de análisis retail/ABC, pero no incorporarlos como dependencia productiva sin licencia y pruebas. En particular, [Retail Sales & Margin Analysis](https://github.com/EkaterinaA83/Retail-sales-ABC-margin-analysis) es un notebook exploratorio sin archivo LICENSE visible en la revisión; sirve para estudiar agregaciones ABC y márgenes, no para copiar su código. ABC no reemplaza el análisis de primera y segunda marca.

La inferencia causal se evita: correlación entre una suba de precio y una baja de ventas no demuestra por sí sola que una haya causado la otra. Mostrar evidencia, muestra, supuestos y explicaciones alternativas.

## 6. Herramientas y decisión de reutilización

| Proyecto | Licencia observada | Función para Rubrova | Decisión actual |
|---|---|---|---|
| [StatsForecast](https://github.com/Nixtla/statsforecast) | Apache-2.0 | Modelos estadísticos y econométricos de series temporales | Primera biblioteca a probar en un fixture reproducible; no instalar hasta validar el entorno del servicio |
| [MLForecast](https://github.com/Nixtla/mlforecast) | Apache-2.0 | Features temporales y ML con variables exógenas/estáticas | Segunda etapa; sólo si añade precisión demostrada frente a baselines/StatsForecast |
| [HierarchicalForecast](https://github.com/Nixtla/hierarchicalforecast) | Apache-2.0 | Reconciliar pronósticos en jerarquías de producto/marca/categoría/local/canal | Etapa posterior; exige jerarquía estable y backtesting |
| [DemandSense](https://github.com/mercer14k/DemandSense) | MIT | Referencia ejecutable de demanda intermitente, comparación de modelos, intervalos empíricos, rolling backtests y escenarios | Inspeccionar selectivamente; repositorio pequeño (4 commits y 2 estrellas en la consulta), no base de producción |
| [DemandOS](https://github.com/RaulMermans/demand-OS) | Sin licencia declarada en el repositorio revisado | Referencia funcional de riesgo de faltantes, features, backtesting y recomendaciones revisadas por humanos | Se puede inspeccionar públicamente como referencia; la ausencia de licencia no concede permiso de reutilización. No copiar/modificar código sin licencia o autorización explícita del titular; reproducir las ideas de forma independiente. |
| [DuckDB](https://github.com/duckdb/duckdb) | MIT | Motor analítico local para snapshots/Parquet y consultas | Primera opción a probar para read models si los reportes nativos no alcanzan |
| [Apache Superset](https://github.com/apache/superset) | Apache-2.0 | Exploración y dashboards BI self-hosted | Alternativa futura, sólo si se justifica una aplicación BI multiusuario |
| [ERPNext](https://github.com/frappe/erpnext) | GPL-3.0 en el repositorio principal revisado | Referencia de Stock Ledger, valuación y reportes de utilidad bruta | Evaluar como plataforma; no extraerlo como biblioteca aislada |
| [Retail Sales & Margin Analysis](https://github.com/EkaterinaA83/Retail-sales-ABC-margin-analysis) | No se observó LICENSE | Ejemplo de notebook para ABC, promociones y margen | Referencia metodológica solamente |

Las licencias se vuelven a comprobar en el commit/tag exacto que se evalúe, junto con licencias de dependencias, datos, modelos y artefactos. Conservar avisos, atribución, SBOM/manifiesto y cambios según corresponda. MIT y Apache-2.0 permiten uso privado y modificación bajo sus condiciones de avisos; la ausencia de licencia no concede esos permisos. Una aplicación GPL/AGPL exige analizar el modo de uso y cualquier distribución.

## 7. Arquitectura de implementación

- Mantener la base OLTP del ERP/POS como autoridad.
- Publicar read models canónicos y snapshots con fecha de corte, esquema y linaje.
- Usar DuckDB y/o Polars para preparar/analisar snapshots si el volumen lo justifica; no ejecutar consultas pesadas en el camino de cobro.
- Ejecutar los modelos de forecasting detrás de una interfaz estable del servicio analítico; empaquetar las bibliotecas con versiones fijadas y dependencias auditadas.
- El dashboard nativo del ERP es la primera opción. Si no cubre la necesidad, evaluar una sola herramienta externa (Metabase o Superset) con permisos por área y acceso de solo lectura.
- Persistir ejecuciones, resultados y versiones; poder reproducir una predicción y explicar un indicador.
- No requerir IA externa. Las explicaciones pueden ser determinísticas y basadas en datos; un modelo local opcional nunca reemplaza las reglas matemáticas o financieras.

## 8. Secuencia obligatoria

1. **Fase 0 — selección POS/ERP:** comparar reportes, costos, ledger, valuación, dimensiones analíticas, exportación y API de las plataformas. Confirmar si el ERP seleccionado ya resuelve estos problemas.
2. **Fase 1 — POS y datos maestros:** capturar marcas/segmentos con vigencia, unidades comparables, precios, promociones, áreas/canales y disponibilidad/faltantes desde el primer día.
3. **Fase 2 — compras e inventario:** implementar recepción, costos accesorios, método FIFO/promedio cuando corresponda, ledger valorizado y trazabilidad de costo.
4. **Fase 3 — contabilidad y liquidaciones:** conciliar ventas, compras, COGS, bancos, medios de pago, comisiones, retenciones, gastos y asientos.
5. **Fase 4A — BI descriptivo y rentabilidad:** cierre diario, ventas, costos, márgenes, contribución, GMROI y resultados por producto/marca/área.
6. **Fase 4B — preferencias de marcas:** participación, precio comparable, tendencias, sustitución y efecto de faltantes/promociones.
7. **Fase 4C — pronóstico:** baselines y StatsForecast; después MLForecast y métodos intermitentes cuando se justifique; reconciliación jerárquica después de validar los agregados.
8. **Fases posteriores:** simulación avanzada de promociones/precios/compras y alertas, manteniendo aprobación humana.

No se retrasa la selección del POS/ERP por querer instalar una pila analítica desde el inicio. Sí se exige conservar los datos necesarios y probar costos desde las primeras operaciones.

## 9. Criterios de aceptación

La capacidad no se considera terminada hasta demostrar en dataset sintético y después con operación real controlada:

- Comparar una misma categoría en trimestre calendario y estación, sin confundir ambos períodos.
- Detectar crecimiento real en unidades aunque la facturación nominal crezca por precio; mostrar ambos indicadores.
- Simular una caída de ventas causada por un quiebre de stock y comprobar que no se presenta como pérdida de preferencia.
- Comparar demanda regular e intermitente y seleccionar un baseline/modelo con backtesting sin fuga temporal.
- Medir error y sesgo por horizonte, producto y categoría; mostrar insuficiencia de historial e intervalos sin calibrar.
- Reconciliar forecast por SKU con familia/categoría/total sin duplicar ni perder unidades.
- Simular primeras y segundas marcas con diferentes tamaños, precios, promociones y margen; comparar por unidad normalizada.
- Detectar una sustitución probable sólo cuando los datos de disponibilidad y evolución la respaldan; mostrar alternativas.
- Simular recepción a dos costos distintos y verificar costo vendido, inventario final y margen bajo el método de valuación establecido.
- Mostrar margen bruto, contribución y resultado operativo como conceptos separados y reconciliables.
- Comprobar que las consultas analíticas no bloquean ni escriben en el POS/ledger.
- Reproducir una ejecución a partir de sus datos, versión y parámetros, y navegar cada indicador hasta su origen.

## 10. Estado y siguientes acciones

- [x] Requisitos funcionales de demanda, estacionalidad, rentabilidad y segmentación de marcas documentados.
- [x] Candidatos principales de forecasting, BI y referencia ERP registrados con papel y licencia observada.
- [x] Límites de DemandSense, DemandOS y notebooks exploratorios documentados.
- [ ] Revisar versiones fijadas, dependencias y compatibilidad del stack elegido.
- [ ] Comparar los métodos de stock valuation y rentabilidad de los finalistas POS/ERP.
- [x] Añadir un fixture sintético separado de quiebres de stock y un ajuste conservador de demanda censurada, con cobertura, umbrales, exclusiones y métricas reproducibles.
- [ ] Ampliar el dataset con marcas, presentaciones, promociones, cambios de precio y costos históricos; incorporar escenarios de quiebres más complejos.
- [x] Preparar benchmark reproducible StatsForecast frente a baselines sobre 48 meses sintéticos y demanda regular/intermitente; CI registra MAE, WAPE y sesgo en backtesting walk-forward.
- [x] Ejecutar y revisar la primera corrida CI del benchmark (20/11/2026); resultados sintéticos registrados, sin selección productiva.
- [ ] Comparar estabilidad y coste en datos reales conciliados antes de aprobar cualquier motor productivo.
- [ ] Evaluar MLForecast y HierarchicalForecast sólo después de obtener una línea base útil.
- [ ] Probar el modelo de datos de segmentos de marca y métricas de sustitución con casos controlados.
- [ ] Aprobar dependencias, licencias, versiones y pruebas antes de incorporarlas.

**Estado real:** existe un experimento ejecutable separado para ajustar demanda censurada con una regla de disponibilidad y fixture 100% sintético. No está conectado al POS ni a compras, no usa datos reales y no autoriza decisiones automáticas. Ninguna biblioteca nueva de forecasting o BI fue añadida ni se declaró terminada una capacidad productiva.
