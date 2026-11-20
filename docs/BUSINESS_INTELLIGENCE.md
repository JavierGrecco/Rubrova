# Inteligencia del negocio

## Propósito

Transformar operaciones confiables en información útil. El módulo debe responder qué está pasando, por qué podría pasar, qué puede ocurrir y qué alternativas conviene evaluar.

Los informes globales, por sucursal y canal usan definiciones comunes y permiten rastrear cada indicador hasta sus datos fuente.

La selección técnica, los contratos de datos, el orden de implementación y los criterios de aceptación de pronósticos, rentabilidad y marcas se mantienen en [Inteligencia de demanda, rentabilidad y marcas](DEMAND_AND_MARGIN_INTELLIGENCE.md).

## Niveles de análisis

Global; sucursal y ubicación; canal; rubro y categoría; marca y proveedor; producto y variante; cliente, empleado, caja y turno, siempre bajo permisos adecuados. Los filtros nunca deben duplicar un pedido que pasó por varios sistemas.

## Métricas económicas

- Ventas brutas: valor antes de descuentos, con criterio explícito.
- Descuentos y devoluciones: reducciones comerciales vinculadas.
- Ventas netas: bruto menos descuentos y devoluciones según criterio documentado.
- Costo de mercadería vendida.
- Ganancia bruta = ventas netas menos costo vendido.
- Margen bruto = ganancia bruta / ventas netas.
- Markup = ganancia / costo.
- Contribución por canal = ventas netas menos costos del producto y costos variables atribuibles.
- Resultado operativo = contribución menos gastos operativos asignados bajo criterios visibles.
- Costo de reposición.
- GMROI = ganancia bruta / inventario promedio valorizado a costo, con período y método documentados.

Nunca presentar facturación como ganancia ni margen bruto como resultado neto. Los gastos comunes se muestran separados o asignados con método explícito.

## Costos

Conservar costo de cada recepción, proveedor, fecha, descuento y gasto atribuible. Definir métodos como promedio ponderado o FIFO según necesidad contable. Separar costo histórico de costo de reposición. Mostrar margen realizado y margen de reposición. Excluir de cálculos productos sin costo válido e informar el faltante.

## Rubros, marcas y productos

Porcentaje de ventas y ganancia por rubro; margen y ganancia absoluta por marca y producto; concentración de los principales artículos; amplitud del crecimiento; cambios de composición; comparación de marcas y segmentos. Un rubro puede crecer por uno o dos productos: el informe debe mostrar qué explica la variación.

## Segmentación de marcas y preferencias de compra

Cada producto puede asociarse a una marca y a un segmento comercial configurable por rubro: primera marca/líder, segunda marca, marca económica, marca propia, alternativa o genérico. La clasificación no se infiere automáticamente solo por precio: debe poder definirse y auditarse por categoría.

El análisis debe mostrar:
- Participación por segmento en unidades, ventas netas, tickets y ganancia/contribución.
- Evolución de participación y cambios entre primeras marcas y segundas/económicas.
- Sustitución dentro de una categoría: qué productos capturan las unidades cuando otro pierde participación.
- Precio comparable por unidad de medida, tamaño y presentación.
- Diferencias entre preferencia por unidades y facturación: una marca cara puede liderar ingresos sin liderar cantidades.
- Cambios por sucursal, canal, área, estación y tipo de cliente cuando haya datos válidos.
- Efecto de faltantes: no interpretar ausencia de ventas por falta de stock como pérdida de preferencia.
- Concentración y dependencia de marcas/proveedores.

## Demanda y tendencias

Unidades por día, semana y mes; tickets con cada producto; ticket promedio; unidades por ticket; frecuencia si existe identidad válida; precio promedio; crecimiento y desaceleración; productos emergentes y estancados; demanda no satisfecha registrada; sustitución de marcas; afinidad de compra.

Una subida nominal de facturación no equivale a mayor demanda si las unidades no crecieron.

## Estacionalidad y seguimiento inteligente por períodos

El sistema ofrece seguimiento diario, semanal, mensual, trimestral y por estación del año (verano, otoño, invierno y primavera), además de períodos comerciales configurables. Trimestres calendario y estaciones no son equivalentes y se analizan por separado; en Argentina se utiliza el calendario del hemisferio sur y se puede configurar la región.

Para cada producto, familia, marca, categoría, sucursal, canal y área:
- Comparar unidades, tickets, ventas netas, margen y contribución con el período anterior y el mismo período del año anterior.
- Detectar aceleración, crecimiento sostenido, desaceleración, caída, estancamiento y productos emergentes.
- Anticipar qué productos probablemente aumenten o reduzcan su demanda en el próximo trimestre/estación.
- Considerar calendario escolar, feriados, vacaciones, fechas comerciales, eventos locales y clima solo con fuentes y geografía válidas.
- Separar crecimiento real de unidades de subas nominales por inflación, cambios de precio, mix o presentación.
- Ajustar por días sin stock, horarios cerrados, cambios de surtido, promociones y cambios de canal.
- Mostrar señales tempranas, horizonte, intervalo, evidencia histórica, confianza y factores explicativos.
- Proponer anticipar compras, reducir reposición, revisar precios, promover, sustituir o liquidar excedentes; ninguna acción económica se ejecuta sin aprobación.

Menos de 12 meses es preliminar y no permite afirmar estacionalidad anual recurrente. Entre 12 y 24 meses permite hipótesis iniciales; 24 a 36 meses comparables mejoran la detección de recurrencias, pero no garantizan precisión. El sistema declara insuficiencia de historial y utiliza baselines conservadores cuando corresponda.

## Rentabilidad accionable por producto y marca

El tablero no ordena solo por facturación. Para cada SKU, variante, marca, categoría y área muestra:
- Unidades vendidas, ventas netas y participación.
- Costo de mercadería vendida y costo de reposición.
- Ganancia bruta absoluta y margen porcentual.
- Contribución después de descuentos, comisiones, medios de pago, embalaje y otros costos variables atribuibles.
- Rentabilidad después de costos directos y, separadamente, después de asignaciones compartidas.
- Inventario promedio, capital inmovilizado, rotación y GMROI.
- Evolución de precio, costo, margen y volumen.

Debe identificar alta venta/alta rentabilidad; alta venta/baja rentabilidad; baja venta/alta rentabilidad; baja venta/baja rentabilidad; pérdida de margen; productos rentables que aceleran; y productos que inmovilizan capital. Las recomendaciones explican el cálculo y no confunden margen porcentual con ganancia absoluta.

## Inventario y abastecimiento

Rotación, cobertura, punto de pedido, stock de seguridad, quiebres, exceso, ABC por ventas/ganancia/unidades/inversión, XYZ por variabilidad, GMROI, sell-through, antigüedad, vencimiento, reservas, simulación de compras y riesgo de sobrante.

## Precios y mercado

Historial de costo, precio y margen; precio comparable por unidad; brecha entre marca líder y alternativa; cambios de participación; elasticidad con muestra suficiente; competencia basada en precios públicos y fechados; efecto de promociones, disponibilidad y cambios de surtido; contexto macroeconómico externo.

Una asociación temporal no demuestra causalidad. Mostrar muestra, supuestos y explicaciones alternativas.

## Promociones

Detectar estancamiento, sobrestock o vencimientos; proponer descuentos, combos, cupones y campañas por canal; simular margen y presupuesto; medir contribución incremental, canibalización, stock final y efecto en ticket. El éxito no se mide solo por unidades: se mide por contribución incremental.

## Clientes y canales

Nuevos, recurrentes e inactivos; recencia, frecuencia, ticket y valor acumulado; categorías preferidas; migración de canal; conversión, carritos abandonados y recompra si la fuente lo permite; comisiones, logística, embalaje, devoluciones y publicidad por canal.

## Pronósticos y alertas

Medias móviles, suavizado exponencial, EWMA/CUSUM, detección de puntos de cambio, series temporales, regresión con factores y modelos jerárquicos cuando hay pocos datos. Cada pronóstico guarda fecha, versión, datos, horizonte, supuestos y resultado real posterior. Medir error y sesgo.

## Calidad y confianza

Cada indicador comunica fuente, actualización, cobertura, datos faltantes, operaciones pendientes, período comparable, si es observado/estimado/externo, confianza y límites conocidos. Nunca imputar valores sin indicarlo.

## Asistente

Consulta métricas verificables, explica cálculos y escenarios. No inventa resultados ni ejecuta cambios sensibles sin aprobación. Cada recomendación incluye hallazgo, evidencia, impacto y supuestos, confianza, acción propuesta y medición posterior.


## Plataforma analítica y herramientas candidatas

La caja y las escrituras operativas no deben competir con consultas analíticas pesadas. La dirección es generar proyecciones/read models sobre datos conciliados y mantener el camino transaccional separado.

Composición candidata para el laboratorio:
- DuckDB (MIT) para consultas locales, datasets derivados y Parquet, sin reemplazar el ERP ni su ledger.
- Parquet y Apache Arrow para intercambio columnar portable y tipado.
- Polars (MIT) para transformar datasets cuando una prueba de rendimiento o memoria lo justifique.
- dbt Core (Apache-2.0) para versionar SQL, pruebas y documentación de modelos métricos cuando se estabilicen las fuentes.
- Evidence (MIT) para informes reproducibles en SQL/Markdown y publicación self-hosted.
- Apache Superset (Apache-2.0) si aparece una necesidad real de BI multiusuario, SQL Lab y dashboards.
- Metabase Open Source (AGPL) sólo tras revisar sus obligaciones y condiciones específicas de embedding; no incorporarlo automáticamente en la interfaz de Rubrova.

No se suman todos como dependencias. Primera prueba: DuckDB + Parquet + modelos SQL versionados; luego comparar Evidence para reportes curados y Superset para exploración multiusuario. Las exportaciones a XLSX/CSV también deben abrirse y manipularse fuera de Rubrova en Excel o LibreOffice. Las consultas pesadas operan sobre una capa de lectura con corte visible y conciliación, nunca sobre el camino de escritura del POS.

Cada exportación debe llevar diccionario, granularidad, relaciones, tipos, zona horaria, moneda, unidad, filtros, fórmula, fuentes, fecha de corte, cobertura, checksums y política de enmascaramiento. La IA local futura consulta esta capa de sólo lectura, valida métricas y filtros, limita filas/tiempo, cita los datos fuente y exporta la consulta y supuestos. No se habilita SQL libre de escritura ni envío de datos privados a IA externa por defecto.

Ver [Captura de datos y base analítica](DATA_CAPTURE_AND_ANALYTICAL_FOUNDATION.md) y [Investigación de módulos ampliados](MODULAR_COMPONENT_RESEARCH.md).


## Rentabilidad por área de negocio

La dimensión de unidad de negocio debe mantenerse separada de canal, sucursal, centro de costo, cliente y proyecto. Los tableros muestran resultados de minorista, ecommerce, mayorista/distribución y servicios B2B, y permiten navegar al consolidado.

Cada área necesita ingresos netos, descuentos/devoluciones, costo de mercadería o prestación, costos variables de servir, costos directos fijos y costos compartidos asignados. Se muestra el resultado antes y después de asignaciones, además de los costos aún no distribuidos.

Los datos distinguen devengado, facturado y cobrado. La rentabilidad no se confunde con saldo bancario; una venta a crédito genera ingreso según su política, pero no efectivo hasta el cobro.

Métricas específicas:
- **Mayorista:** volumen, pedido promedio, recurrencia, precio por escala, margen después de flete, costo de servir, días de cobro y morosidad.
- **Servicios:** ingreso recurrente, margen por contrato, utilización, horas consumidas, SLA, retrabajo y costo de desplazamiento.
- **Distribución:** costo por entrega/parada/peso/volumen, entregas a tiempo, reintentos, incidencias y margen logístico.

Ver [Rentabilidad por área](BUSINESS_UNIT_PROFITABILITY.md).


## Forecasting y calidad de las predicciones

La demanda prevista debe calcularse por SKU, familia, sucursal, canal y área según la calidad del historial. No entrenar un modelo único para todos los productos sin evaluar comportamiento y cobertura.

Cada predicción conserva:
- ventana histórica usada, fechas de entrenamiento y horizonte;
- ventas observadas, stockout y días sin disponibilidad para reconocer demanda censurada;
- calendario, estacionalidad, promociones, precio, canal y factores externos disponibles;
- modelo, parámetros, versión, intervalo de predicción y baseline;
- resultados de backtesting y error por horizonte/segmento;
- fecha de próxima revisión y señal de drift.

La primera biblioteca a evaluar es StatsForecast para modelos estadísticos y econométricos, siempre comparada con baselines propios. MLForecast queda como segunda capa cuando las variables externas (precio, promociones, calendario, canal) tengan calidad e historial suficientes. HierarchicalForecast se evalúa después para reconciliar pronósticos agregados. DemandSense es una referencia MIT pequeña para demanda intermitente, backtesting y escenarios, no una dependencia productiva aprobada. Skforecast se conserva como alternativa para comparar sólo si una prueba concreta demuestra una ventaja. DuckDB y Polars preparan datasets; no sustituyen el ledger ni la base transaccional. Para series cortas/intermitentes o productos nuevos, mostrar reglas simples, intervalos amplios o ausencia de pronóstico, no una precisión ficticia.

Toda sugerencia de reposición debe explicar stock disponible/reservado/en tránsito, lead time, múltiplos, mínimo, proveedor, demanda prevista y costo de compra. El sistema propone; la orden de compra solo nace con aprobación y controles de crédito/presupuesto.

La comparación de marcas no se delega a un paquete genérico: Rubrova conserva la clasificación comercial efectiva por categoría, la unidad comparable y los datos históricos de disponibilidad/precio/promoción. ABC y XYZ complementan el análisis, pero no representan primera/segunda marca. La rentabilidad usa el ledger de costo del ERP y no una fórmula calculada sobre el último precio de compra.

El benchmark mensual inicial de demanda usa 48 observaciones sintéticas por serie (regular estacional creciente e intermitente), cuatro cortes de entrenamiento expansivos y horizonte de tres meses. Compara naive, naive estacional, medias móviles y modelos StatsForecast adecuados al tipo de serie. La primera versión no incluye períodos sin stock en el entrenamiento: los trataremos en un conjunto separado para evaluar demanda censurada sin contaminar el ajuste.
