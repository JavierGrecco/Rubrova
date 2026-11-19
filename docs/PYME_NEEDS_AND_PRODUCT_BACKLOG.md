# Investigación de necesidades de PyMEs y backlog de mejoras

**Revisión:** 19 de noviembre de 2026  
**Alcance:** evidencia de encuestas y conversaciones públicas consultadas; no es una investigación estadísticamente representativa de todos los comercios argentinos.

## 1. Lo que muestran los datos de PyMEs

El informe Radar PyME de ENAC del tercer trimestre de 2026 releva 242 empresas de 15 provincias. Entre los resultados publicados:
- 93% reportó aumentos en costos operativos, pero 71,5% pudo aumentar precios.
- 39,7% reportó caída de ventas en volumen.
- La brecha promedio de caja por cobrar y pagar fue 16,4 días: 53,3 días para cobrar frente a 37 días para pagar.
- 69,8% informó extensiones unilaterales de plazos de pago; 49,6% reportó más incumplimientos.
- 55,4% recurrió a endeudamiento y las principales causas reportadas incluyeron capital de trabajo, costos fijos e impuestos.

Fuentes:
- https://enac.org.ar/contenido/5003/ya-esta-disponible-el-informe-radar-pyme-3t-2026-leelo-aca
- https://enac.org.ar/download/multimedia.archivo.b8e975fc405a4594.YXJjaGl2by5wZGY%3D.pdf

Estos datos justifican que Rubrova no se limite a facturar y contar stock: necesita explicar márgenes, caja futura, deuda de clientes, compromisos con proveedores y necesidades de reposición. Las cifras corresponden a la muestra y metodología de ENAC, no deben extrapolarse como si representaran automáticamente a todas las PyMEs.

## 2. Patrones observados en foros y comunidades argentinas

Los hilos consultados son relatos individuales, no una encuesta. Sin embargo, permiten diseñar pruebas y descubrir fricciones recurrentes:

| Patrón observado | Ejemplo público | Respuesta funcional que debe ofrecer Rubrova |
|---|---|---|
| Omnicanalidad rota y ventas sin facturar | PyME que vende por Mercado Libre, suma Tiendanube y abre un local; una falla de sincronización dejó más de 200 ventas sin facturar | Inbox/outbox durable, conciliación diaria, alertas de pedidos sin comprobante y recuperación idempotente |
| Offline y costos de licencias/terminales | Comercio del interior busca software local que siga operando sin internet y evita cargos crecientes por terminal/usuario | Operación local prioritaria, sincronización explícita, política de licencias propia y medición del costo total |
| Retail + mayorista con descuentos por artículo | Fiambrería con sucursales minoristas y mayorista pide descuentos discriminados por línea y reportes correctos | Descuento y motivo por renglón, ticket/comprobante detallado, reglas por área y reporte verificable |
| Almacén caótico con miles de SKUs | Ferretería con más de 10.000 artículos sin códigos, categorías ni ubicación digital | Importación/normalización masiva, ubicación bin/estante, códigos internos/barcode, conteo cíclico y búsqueda rápida |
| No saber si un producto deja dinero | Comerciantes preguntan por margen por SKU, costo de reposición, flete, comisión, precio gancho y punto de equilibrio | Costeo landed/replacement, margen por producto/pedido/canal y simulación de promociones |
| Gestión básica de distribuidora | Mayorista pide stock, ventas, compras, proveedores, cuentas corrientes, caja y estadísticas | Flujo integral pedido-compra-stock-cobro-pago, aging y reportes operativos |

Conversaciones consultadas:
- https://www.reddit.com/r/NegociosArgentina/comments/1wzw2pp/sistema_erp/
- https://www.reddit.com/r/NegociosArgentina/comments/1uz8b2e/sistema_de_gesti%C3%B3n/
- https://www.reddit.com/r/NegociosArgentina/comments/1x0sn48/alguien_usa_zeus_de_infosis_mi_experiencia_con/
- https://www.reddit.com/r/NegociosArgentina/comments/1sid1i0/tengo_una_ferreter%C3%ADa_con_10000_productos_en_un/
- https://www.reddit.com/r/NegociosArgentina/comments/1tzwagz/c%C3%B3mo_manejan_los_m%C3%A1rgenes_en_sus_negocios_fisicos/
- https://www.reddit.com/r/NegociosArgentina/comments/1lluxtb

## 3. Mejoras que conviene incorporar al alcance

### A. Confiabilidad operacional y sincronización

La pérdida silenciosa de pedidos es un problema grave. Todo evento externo debe ingresar a una bandeja Inbox duradera, con clave idempotente, estado, intentos, errores, fecha de última actualización y opción de reproceso controlado.

Requerimientos:
- panel de pedidos externos recibidos, procesados, pendientes y rechazados;
- comprobante fiscal pendiente o fallido por cada venta;
- órdenes repetidas detectadas sin duplicar stock/pagos;
- reintentos automáticos con límites y cola de errores;
- reconciliación por plataforma, período, pedido y total;
- alertas por ventas sin factura, pagos sin aplicar, envíos sin tracking o diferencias de liquidación;
- replay auditable de eventos sin volver a ejecutar efectos ya confirmados.

### B. Costos, precios y margen real

No usar un único porcentaje fijo de markup. Mostrar el costo que se usó y permitir comparar costo promedio, última compra y costo de reposición. El costo puesto en depósito incorpora flete de compra, seguro, gastos y prorrateos configurados.

Antes de cambiar precios, simular:
- margen bruto y contribución;
- comisiones por canal/medio de pago;
- costo de envío/embalaje;
- descuentos e impuestos que correspondan;
- comparación con la lista vigente y precios de otros canales si están disponibles;
- impacto por segmento, cliente y unidad de negocio.

Permitir precio mínimo, margen objetivo, artículos gancho, combos y escalas con autorización. El sistema explica qué regla aplicó y alerta cuando una promoción erosiona la contribución.

### C. Inventario que se pueda encontrar y reponer

- jerarquía de almacén, zona, pasillo, estante, nivel y bin;
- etiqueta y código de barras propio aunque el proveedor no tenga GTIN;
- variantes y atributos configurables (talle, color, medida, presentación);
- UOM, packs, cajas, bultos, kg/litro y conversión exacta;
- lote, serie, vencimiento y trazabilidad;
- conteo cíclico ABC y ajustes autorizados;
- stock reservado, disponible, en tránsito, dañado y comprometido;
- mínimos, máximos, safety stock, lead time y sugerencia de compra;
- quiebres, sobrestock, lento movimiento y productos sustitutos;
- compra, recepción parcial, putaway y devolución al proveedor.

### D. Capital de trabajo y cobranza

Un panel de gestión diaria debe mostrar caja, bancos, cuentas por cobrar, vencimientos y compromisos a proveedores. Las ventas a crédito necesitan límite, plazo, exposición, promesa de pago, cobranzas parciales, morosidad y autorización de excepciones.

Un pronóstico móvil de 13 semanas debería combinar:
- efectivo/bancos y liquidaciones pendientes;
- cobros previstos por fecha y probabilidad;
- pagos a proveedores, impuestos, salarios, alquiler y servicios;
- cuotas/deuda;
- escenarios de retraso de cobros, baja de ventas y suba de costos.

El reporte debe distinguir real, confirmado, estimado y escenario; no presentar una previsión como saldo disponible.

### E. Migración e importación de datos

El cambio de sistema es una barrera real. Debemos ofrecer un asistente:
1. detectar CSV/XLSX y hojas;
2. sugerir correspondencias de columnas y unidades;
3. normalizar CUIT, códigos, fechas, monedas y unidades;
4. detectar duplicados y conflictos;
5. mostrar muestra y errores por fila;
6. simular sin escribir;
7. importar con upsert y claves externas;
8. registrar quién, cuándo y qué se importó;
9. permitir revertir el lote cuando no haya movimientos posteriores dependientes.

### F. Reportes y explicación

Los reportes deben poder filtrarse por unidad, sucursal, canal, almacén, cliente, producto, vendedor, contrato y período. Permitir guardar filtros, exportar y programar. Cada cifra muestra definición, fuente, fecha de actualización y nivel de cobertura.

## 4. Backlog priorizado

| Prioridad | Capacidad | Justificación | Criterio de aceptación |
|---|---|---|---|
| P0 | Centro de conciliación y recuperación de integraciones | Evita ventas omitidas/duplicadas y comprobantes pendientes invisibles | Se puede identificar, reintentar y conciliar todo evento externo |
| P0 | Interoperabilidad contable y exportación verificable | No obliga a abandonar Tango, Catedral, Bejerman, Xubio o Colppy | Lote balanceado, mapeado, idempotente, con acuse y conciliación |
| P0 | Importación/migración asistida | Reduce barrera de entrada y dependencia de hojas/manual | Dry-run, errores, upsert y reversión demostrables |
| P1 | Flujo de caja y cuentas corrientes | Presión sobre plazos de cobro y capital de trabajo | Aging, alertas, flujo 13 semanas y conciliación real vs previsto |
| P1 | Motor de costo de reposición y precios | Costos crecen a distinta velocidad y se sacrifica margen | Simular cambios sin alterar precios hasta autorizar |
| P1 | WMS de ubicaciones/barcodes/conteos | Inventario físico caótico y miles de SKUs | Ubicación rastreable, conteo y diferencias auditadas |
| P1 | Reportes de margen y rentabilidad | El movimiento de facturación no asegura ganancia | P&L por unidad/canal/SKU y consolidado conciliado |
| P1 | Compras y reposición sugerida | Evita faltantes y exceso de capital inmovilizado | Sugerencia explica demanda, stock, lead time y mínimo |
| P2 | Archivo documental y OCR asistido | Reduce carga manual de facturas y comprobantes | Original preservado, campos extraídos revisables y vínculo al asiento |
| P2 | Automatización de casos repetitivos | Recordatorios, alertas y tareas operativas | Toda automatización registra ejecución, error y resultado |

## 5. Indicadores que deberían acompañar el backlog

- pedidos externos ingresados vs conciliados;
- venta confirmada sin comprobante, pago, movimiento de stock o fulfillment esperado;
- tiempo para recuperar una integración caída;
- porcentaje de inventario con ubicación y código verificables;
- exactitud de inventario por depósito;
- quiebres y ventas perdidas;
- margen por SKU con porcentaje de costo cubierto;
- variación entre precio actual y precio mínimo rentable;
- días de ventas pendientes de cobro y días de pago a proveedores;
- desvío de caja prevista frente a caja real;
- porcentaje de lotes contables aceptados/rechazados;
- tiempo de importación/migración y cantidad de registros sin resolver.

## 6. Criterio de diseño

Los datos de encuestas orientan prioridades de gestión; los foros revelan fricción concreta, pero no prueban prevalencia. Rubrova debe permitir configurar estos procesos por área, y activar solo los que esa organización usa. No se implementa una pantalla o módulo genérico sin un flujo completo, dueño del dato, estados, auditoría y criterio de aceptación.
