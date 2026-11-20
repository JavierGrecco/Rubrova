# Captura de datos y base analítica de Rubrova

**Revisión:** 20 de noviembre de 2026  
**Estado:** especificación de diseño y aceptación; no implica que estas entidades o reportes ya estén implementados.

## 1. Objetivo

Registrar los hechos necesarios desde la primera venta para poder operar varias actividades, canales, sucursales y formatos comerciales, reconstruir cada operación histórica y analizarla después sin depender de los valores actuales del catálogo.

La amplitud del modelo no debe convertirse en una pantalla con cien campos obligatorios. Rubrova debe capturar automáticamente lo que conoce del contexto operativo, permitir campos opcionales y extensiones sectoriales, y exigir sólo los datos indispensables para cada operación. Una venta minorista anónima no debe exigir CUIT o una ficha de cliente; una factura, un despacho o una venta a crédito sí exige los datos que correspondan a ese proceso.

## 2. Dimensiones que nunca se deben confundir

| Dimensión | Qué describe | Ejemplos |
|---|---|---|
| Organización / entidad legal | Quién opera y quién tiene la obligación fiscal | Organización privada, sociedad con CUIT |
| Área / unidad de negocio | Qué actividad genera el resultado | Minorista, mayorista, distribuidora, ecommerce, servicios |
| Formato / perfil sectorial | Qué tipo de establecimiento o actividad opera | Kiosco, almacén, minimercado, supermercado, panadería, rotisería |
| Canal de origen/venta | Cómo entró o se atendió el pedido | Local, web, WhatsApp, vendedor, teléfono, marketplace |
| Canal asistido | Quién o qué herramienta intervino | Cajero, vendedor, bot, operador |
| Cumplimiento | Cómo se entrega o completa | Retiro, reparto propio, transportista, prestación de servicio |
| Sucursal / ubicación | Dónde ocurre la actividad | Local, centro de distribución, depósito, cocina |
| Depósito / posición | Dónde se guarda el stock | Depósito seco, cámara, góndola, picking |
| Centro de costo / beneficio | Dónde se origina el gasto o se mide el resultado | Administración, marketing, distribución, sucursal |

El formato del establecimiento es un perfil configurable, no un canal. Una venta mayorista puede llegar por WhatsApp, prepararse en el depósito central y entregarse con vehículo propio. Cada una de esas dimensiones debe conservarse sin reducirlas a una categoría única.

Las asignaciones pueden existir a nivel de documento y de línea. Una misma venta o factura puede distribuirse entre más de un área o centro de beneficio; el consolidado debe eliminar movimientos internos para no duplicar ventas ni ganancias.

## 3. Catálogo y evolución histórica

### Producto, presentación y clasificación

Cada SKU/variante debe tener identidad estable y conservar relaciones con:

- producto, variante, código de barras, códigos internos y códigos de proveedor;
- fabricante, marca y proveedor, que son entidades distintas;
- categoría y subcategoría, con clasificación vigente por período;
- segmento comercial configurable por categoría: líder/primera, segunda, económica, propia, alternativa o genérica;
- unidad base, unidad de compra, unidad de venta, contenido neto, unidad comparable y conversiones (unidad, kg, litro, pack, caja, bulto);
- dimensiones, peso, contenido, presentación, lote, serie y vencimiento cuando corresponda;
- impuestos, listas de precios, mínimos, múltiplos y condiciones por cliente/canal/sucursal.

El segmento de marca no se deduce sólo por precio. Debe guardar quién lo asignó, motivo, categoría a la que aplica y desde/hasta cuándo fue válido. Un producto puede cambiar de marca, presentación o clasificación; el histórico no se sobrescribe.

### Historial de valores

Guardar versiones con vigencia y registro temporal para precio de venta, costo de compra, costo puesto, costo de reposición, proveedor preferido, unidad de compra, promoción y reglas fiscales/comerciales. Las líneas de venta y compra conservan una fotografía de los valores aplicados en ese momento.

No alcanza con consultar el precio actual para reconstruir una venta histórica. El costo de mercadería vendida se determina desde la recepción/capa de inventario y el método de valuación aprobado, no copiando automáticamente el último costo de catálogo.

## 4. Hechos operativos y sus tiempos

Los registros deben diferenciar:
- `occurred_at`: cuándo ocurrió el hecho en el negocio o dispositivo;
- `recorded_at`: cuándo Rubrova lo recibió y persistió;
- `effective_from/effective_to`: período en que una regla o valor era válido;
- fecha comercial del negocio (`business_date`) y zona horaria IANA de la sucursal;
- hora UTC para correlación entre sistemas y hora local para operación y reportes.

Esto permite distinguir una entrega tardía de una operación realmente tardía, reconstruir cierres y corregir datos sin fingir que se conocían antes. Los documentos históricos conservan la fotografía de dimensiones y condiciones vigentes al confirmarse. Las correcciones se registran como eventos/movimientos compensatorios y con auditoría; no se reescribe silenciosamente un hecho confirmado.

## 5. Datos que se capturan por dominio

### Pedidos, ventas y líneas

Guardar pedido, origen, fecha de creación/confirmación/cancelación, cliente o comprador anónimo, dirección/contacto cuando corresponda, canal, área, sucursal, vendedor/cajero, turno, caja, estado y referencias externas. Cada línea conserva SKU, descripción y presentación histórica, marca/segmento, unidad y cantidad, precio bruto, descuento asignado, impuestos, precio neto, motivo de ajuste, promoción aplicada y referencia a costo/valuación.

El carrito puede editarse; una venta confirmada es un hecho. Un cambio posterior crea cancelación, devolución o nota compensatoria y referencia a la venta original.

### Compras, proveedores y recepción

Separar cotización, orden de compra, confirmación del proveedor, recepción física, factura del proveedor y pago. En cada línea guardar proveedor y código de artículo, cantidad pedida/recibida/aceptada/rechazada, unidad de compra y equivalencia, lote/vencimiento si aplica, precio, bonificación, impuestos, flete y otros costos de puesta. Registrar fecha de pedido, fecha prometida, llegada, control y contabilización.

Una recepción parcial no se debe convertir en recepción total. Las diferencias, faltantes, roturas, sustituciones y devoluciones al proveedor quedan trazadas a la orden y recepción originales.

### Inventario y disponibilidad

Mantener un ledger de movimientos append-only: entrada, salida por venta, devolución, reserva/liberación, transferencia, producción/consumo, ajuste, merma, vencimiento, rotura, conteo y devolución a proveedor. Cada movimiento incluye artículo, cantidad y unidad base, depósito/ubicación, lote/serie si aplica, origen documental y línea, actor, dispositivo, motivo, timestamps, costo/capa y correlación.

Registrar cuándo un SKU estuvo disponible, reservado, en tránsito, bloqueado o agotado por ubicación. Capturar duración del quiebre, horario de apertura y surtido activo. Si se conoce demanda no satisfecha, guardar cantidad solicitada, cantidad entregada, faltante, sustituto ofrecido, cancelación y motivo. Cero ventas durante un quiebre no significa demanda cero.

### Pagos, cobros y conciliación

Separar medio de pago, proveedor/adquirente, cuenta, terminal y operación externa. Permitir pagos mixtos, cuotas, anticipos, pagos parciales, reintentos, autorizaciones, capturas, anulaciones, reversos, contracargos, liquidaciones, comisiones y reintegros.

Cada intento debe tener estado, importe/moneda, timestamps, referencia de proveedor, terminal/caja, operador, clave de idempotencia y correlación con venta/pedido. Una referencia de pago no equivale a un cobro confirmado. Conciliar contra liquidaciones y extractos. Nunca almacenar PAN completo ni CVV de tarjetas; utilizar tokenización o referencias del proveedor.

### Caja, cajeros y turnos

Guardar sucursal, caja física/lógica, dispositivo, cajero responsable, supervisor, apertura, fondo inicial, cambio de responsable, ingresos/egresos no vinculados a venta, retiros, depósitos, arqueo, efectivo esperado/contado, diferencia, cierre y aprobaciones. Una sesión de caja no se infiere del usuario conectado. Las operaciones manuales llevan actor, motivo y autorización.

### Promociones, descuentos y acuerdos

Cada promoción tiene versión, vigencia, alcance, canal/área/sucursal, condiciones, elegibilidad, presupuesto/límite, acumulabilidad, artículos participantes y motivo. Los descuentos automáticos, cupones, puntos, bonificaciones del proveedor y ajustes manuales se distinguen y se asignan a las líneas de forma reproducible. Un precio sobrescrito exige motivo y, según permiso, autorización.

### Devoluciones, reclamos y envíos

Separar reclamo, autorización de devolución, recepción física, disposición del artículo, reintegro y nota de crédito. Registrar motivo, condición, cantidad, responsable, evidencia, resolución, compensación, origen y línea original. Una queja puede resolverse sin devolución ni reintegro; una devolución puede existir sin reclamo.

Vincular pedido/venta, líneas, uno o varios envíos, bultos, transportista, guía, eventos, entregas parciales y prueba de entrega. Los IDs y estados externos deben conservarse para conciliación; los envíos no son autoridad sobre venta, cobro ni stock maestro.

### Empleados, dispositivos y auditoría

Los usuarios representan acceso; los empleados representan personas y funciones. Separar identidad, rol, permisos, asignaciones, sucursal, turno y dispositivo. Registrar autor, aprobador, origen, aplicación, dispositivo, acción, valor anterior/nuevo cuando corresponda, motivo, correlación e instante. Aplicar permisos por entidad, área, sucursal, caja y dato sensible.

## 6. Modelo temporal y calidad

Usar IDs estables y relaciones explícitas; conservar ID externo, sistema de origen y mapping al migrar desde ERP. Las dimensiones que cambian (marca/segmento, categoría, precio, proveedor preferido, jerarquía de sucursales, clasificación de canal) necesitan versiones con vigencia. Para hechos financieros, fiscales y de inventario, conservar tanto la fecha efectiva como la fecha en que se registró una corrección.

Evitar un modelo EAV genérico como estructura principal y evitar una tabla gigante con columnas para todos los rubros. Usar entidades tipadas, relaciones, extensiones específicas por sector y atributos configurables sólo donde agreguen valor. No exigir datos que no se conocen ni inferirlos sin indicar su origen/confianza.

La captura debe probarse con escenarios de ventas anónimas, ventas con cliente, canal mixto, múltiples áreas por línea, compras parciales, quiebres de stock, cambio de marca, cambio de precio, pagos divididos, pago fallido seguido de uno exitoso, devolución parcial, reclamo sin reintegro, entrega parcial y operación fuera de línea sincronizada después.

## 7. Arquitectura de informes y exportación

Las consultas históricas, los pronósticos y los informes pesados no deben bloquear la caja ni escribir en el ledger transaccional. Mantener una capa analítica de lectura, actualizada desde transacciones confirmadas, con fecha de corte visible y reconciliación contra el ERP.

La salida portable recomendada por tipo de uso es:
- CSV UTF-8: apertura simple e intercambio tabular; incluir convención decimal, delimitador, moneda y zona horaria.
- XLSX: informe para Excel/LibreOffice con hojas por tabla, filtros, formatos, fórmulas visibles y diccionario resumido.
- Parquet: dataset analítico eficiente, tipado y comprimido para grandes volúmenes, DuckDB, Python y otros motores.
- JSON/JSONL: eventos, APIs, estructuras anidadas y auditoría.
- PDF: fotografía legible de un informe, nunca el único formato exportable.

Cada exportación incluye manifiesto, fecha de corte, filtros, zona horaria, moneda, unidades, definición de métricas, nombres de campos, tipos, IDs/relaciones, cobertura, filas omitidas y checksums. Permitir exportar el informe filtrado y también el detalle subyacente autorizado. Los datos personales, fiscales y de pago se minimizan o enmascaran según rol.

Cada KPI tiene definición única (nombre, fórmula, granularidad, tratamiento de devoluciones/descuentos/impuestos, fecha de corte, fuentes, versión y propietario). Se debe poder abrir desde el indicador hasta sus filas fuente, sin contar dos veces pedidos que cruzan canales o envíos.

## 8. Proyectos y herramientas para evaluar

| Proyecto | Rol propuesto | Licencia/estado investigado | Decisión |
|---|---|---|---|
| DuckDB | Motor local analítico sobre snapshots y Parquet | MIT; documentación oficial de lectura/escritura Parquet | Candidato prioritario para laboratorio BI |
| Parquet / Apache Arrow | Formatos portables de datos columnares y memoria | Estándares abiertos; Arrow define tipos, esquema y transporte | Base de exportación analítica |
| Polars | Transformación y análisis tabular eficientes | MIT | Biblioteca candidata; no sustituye la base operativa |
| dbt Core | Versionar modelos SQL, pruebas y documentación de métricas | Apache-2.0 | Evaluar cuando haya contratos SQL estables |
| Evidence | Informes reproducibles escritos en SQL/Markdown y publicación self-hosted | MIT | Candidato para informes curados y reproducibles |
| Apache Superset | BI multiusuario, dashboards, SQL Lab y exportaciones | Apache-2.0 | Alternativa potente, pero despliegue más pesado |
| Metabase Open Source | Exploración visual y dashboards para usuarios de negocio | AGPL; embedding tiene condiciones propias | No incrustar automáticamente; revisar obligaciones antes de adoptar |
| StatsForecast | Pronósticos estadísticos | Apache-2.0; ya fijado en benchmark inicial | Primera evaluación de series temporales, no verdad productiva |
| Ollama | Ejecución local de modelos de lenguaje con API local | Runtime MIT; cada modelo/ponderación tiene licencia propia | Candidato de facilidad de instalación y administración local |
| llama.cpp | Inferencia local CPU/GPU y servidor HTTP compatible con APIs de modelos | MIT; cada modelo/ponderación tiene licencia propia | Alternativa de mayor control y optimización por hardware |
| SQLGlot | Parseo, AST, transformación y dialectos SQL | MIT | Ayuda a inspeccionar SQL generado; no es una barrera de seguridad ni un validador de consultas |
| JupyterLab | Análisis exploratorio reproducible y notebooks locales | BSD-3-Clause | Herramienta de analista, no interfaz operativa para cajeros/usuarios ocasionales |

No incorporar toda esta lista como dependencias. Primera prueba: DuckDB + Parquet + consultas SQL versionadas; Polars sólo si mejora una transformación medida. Probar Evidence para informes propios; comparar Superset si aparece una necesidad real de BI multiusuario. Metabase queda condicionado a revisar el modelo de uso y sus términos de embedding. El motor transaccional y el ERP conservan la autoridad sobre ventas, inventario, pagos y contabilidad.

## 9. Uso de IA sobre datos del negocio

El usuario debe poder descargar los resultados, abrirlos en Excel o LibreOffice y analizarlos con herramientas externas. Más adelante, un asistente de IA local puede consultar la capa analítica aprobada, generar filtros, explicar fórmulas, comparar períodos y preparar pronósticos alternativos.

La IA debe ser de sólo lectura por defecto, usar métricas/datasets autorizados, declarar filtros y período, enlazar cada hallazgo a los datos fuente y diferenciar hechos, estimaciones e hipótesis. Las consultas generadas se validan contra un catálogo semántico y límites de tiempo/filas/costo; no se permite SQL arbitrario sobre la base transaccional ni escribir precios, pagos, stock o asientos. El informe generado se exporta junto con consulta, parámetros, modelo/versión y supuestos para que otra persona pueda reproducirlo. Los datos sensibles se excluyen, enmascaran o requieren autorización explícita; no enviar información comercial privada a un servicio externo por defecto.

Para un modo estrictamente local se probarán Ollama y llama.cpp como runtimes alternativos, ambos con código MIT, pero la licencia de cada modelo descargado se revisará por separado. Ollama prioriza una experiencia de instalación/gestión sencilla; llama.cpp ofrece más control de ejecución y backends para CPU, GPU y Apple Metal. La primera instalación puede necesitar descargar el modelo; después se debe poder operar sin conexión, verificando que no dependa de APIs externas. No se fijará modelo sin probar calidad en español, razonamiento tabular, velocidad, memoria, compatibilidad de hardware y licencia.

SQLGlot puede convertir una petición a un AST SQL para inspección y normalización, pero su documentación advierte que el parser es deliberadamente tolerante y no valida por sí solo que una consulta sea válida o segura. La defensa debe combinar un catálogo de vistas permitido, AST allowlist, ejecución con conexión/rol de sólo lectura, parámetros, límites de tiempo/filas/memoria, sin acceso al filesystem ni extensiones arbitrarias y pruebas de consultas adversariales. JupyterLab queda como herramienta de análisis avanzado/exportación reproducible para uso técnico, no como requisito del POS.

Los pronósticos numéricos no se delegan al LLM: StatsForecast y, si las pruebas lo justifican, MLForecast/HierarchicalForecast calculan los modelos, intervalos y backtests. El LLM ayuda a elegir preguntas, sugerir variables, crear una hipótesis o explicar resultados; la predicción reportada siempre debe provenir de un modelo probado y declarar su error.

## 10. Nuevas pruebas de plataforma

Agregar a la batería común:
- **P50 — Dimensiones sin confusión:** separar área, canal, formato, sucursal, depósito y fulfillment; comprobar venta mayorista por WhatsApp y minorista local/digital.
- **P51 — Historial de catálogo:** reconstruir marca, segmento, presentación, unidad, precio y costo vigentes al vender; cambio posterior no altera el pasado.
- **P52 — Tiempo y disponibilidad:** separar ocurrido/registrado/efectivo; registrar recepción, movimiento y quiebre por ubicación sin interpretar stockout como demanda cero.
- **P53 — Pagos y referencias:** pagos mixtos, intentos fallidos, referencias externas, idempotencia, comisión, liquidación, devolución y conciliación sin duplicados.
- **P54 — Caja y personal:** identificar cajero, supervisor, caja, turno, dispositivo, apertura, egresos, arqueo y diferencias auditables.
- **P55 — Promociones y descuentos:** reproducir reglas/versiones y asignación por línea; explicar quién autorizó un precio manual.
- **P56 — Reclamos y devoluciones:** diferenciar reclamo, devolución física, reintegro, nota de crédito y envío; todos referenciados sin duplicación.
- **P57 — Exportación y analítica:** exportar el mismo informe a CSV, XLSX y Parquet con manifiesto/diccionario; abrirlo fuera del ERP y reproducir totales desde DuckDB o una herramienta compatible.

## Estado

La especificación amplía el modelo y el protocolo de selección. Los candidatos de plataforma aún deben demostrar estos criterios en un laboratorio. Las herramientas de BI citadas son opciones a probar, no componentes ya instalados ni aprobados.

## Fuentes oficiales consultadas

- [Libsodium: password hashing](https://doc.libsodium.org/password_hashing) y [derivación con Argon2id](https://doc.libsodium.org/password_hashing/default_phf): la API usa Argon2id, admite almacenar algoritmo/parámetros y permite ajustar costo de memoria/CPU. La versión de libsodium y sus parámetros deberán fijarse en el formato del backup.
- [DuckDB: FAQ y licencia MIT](https://duckdb.org/faq), [lectura/escritura Parquet](https://duckdb.org/docs/data/parquet) y [exportación Parquet](https://duckdb.org/docs/current/guides/file_formats/parquet_export).
- [Apache Arrow: formato columnar](https://arrow.apache.org/docs/format/Columnar.html), con esquema tipado y representación portable en memoria.
- [Polars: repositorio y licencia MIT](https://github.com/pola-rs/polars).
- [dbt Core: pyproject y Apache-2.0](https://github.com/dbt-labs/dbt-core/blob/main/pyproject.toml).
- [Evidence: repositorio y licencia MIT](https://github.com/evidence-dev/evidence) y [archivo LICENSE](https://github.com/evidence-dev/evidence/blob/main/LICENSE).
- [Apache Superset: repositorio y Apache-2.0](https://github.com/apache/superset).
- [Metabase: términos de licencia y embedding](https://www.metabase.com/license); su edición Open Source usa AGPL y el embedding tiene condiciones específicas.
- [Frappe REST API](https://docs.frappe.io/framework/user/en/api/rest) y [ERPNext Data Export](https://docs.frappe.io/erpnext/data-export): ejemplos de API y exportación CSV/Excel a evaluar en la prueba de plataforma.
- [Superset SQL Lab API](https://superset.apache.org/developer-docs/api/sql-lab/) y [exportación de dashboard a Excel](https://superset.apache.org/user-docs/using-superset/exporting-dashboard-data/).
- [Microsoft Excel / Power Query: importación desde fuentes de datos](https://support.microsoft.com/en-us/excel/import-data-from-data-sources-power-query).
- [Ollama: repositorio y licencia MIT](https://github.com/ollama/ollama) y [API local](https://github.com/ollama/ollama/blob/main/docs/api.md).
- [llama.cpp: repositorio/licencia MIT](https://github.com/ggml-org/llama.cpp), [servidor local](https://github.com/ggml-org/llama.cpp/tree/master/tools/server) y [backends de compilación](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).
- [SQLGlot: repositorio MIT](https://github.com/tobymao/sqlglot) y [documentación del AST](https://sqlglot.com/sqlglot.html); su FAQ aclara que el parser no es un validador de ejecución.
- [JupyterLab: repositorio y licencia BSD-3-Clause](https://github.com/jupyterlab/jupyterlab).

Las licencias y capacidades deben volver a verificarse para cada versión/archivo que se fije en el laboratorio. Esta lista respalda una selección de candidatos; no es una autorización para ignorar licencias de dependencias ni una decisión de adopción.


## 11. Captura para perfil 360 de clientes

Cada operación debe conservar el CustomerAccount o el estado explícito de venta anónima, fuente/canal, área, sucursal, vendedor/cajero y líneas históricas. Para la ficha del cliente se derivan RFM, cohortes, marcas/categorías, frecuencia y contribución; no se guardan como hechos los pronósticos o segmentos calculados. Cada ejecución analítica conserva periodo, regla/modelo, entradas, versión, cobertura y confianza.

Registrar preferencias declaradas y permisos de contacto por canal (correo, WhatsApp, SMS u otros) con origen, fecha y versión del aviso. No inferir atributos sensibles ni identificar compradores anónimos por coincidencias débiles. La ficha y los límites de uso se detallan en [Perfil 360 e inteligencia por cliente](CUSTOMER_360_AND_INTELLIGENCE.md).
