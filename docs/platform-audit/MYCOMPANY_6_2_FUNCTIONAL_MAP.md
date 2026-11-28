# Mapa funcional de MyCompany 6.2

**Estado del relevamiento: EN CURSO — no habilita el cierre de la puerta 9.7.**

Este documento consolida la primera lectura de la documentación funcional incluida en el snapshot de MyCompany 6.2 y su contraste parcial con los módulos LSF. Describe capacidades que aparecen en la documentación o en el código; no significa que cada pantalla, acción o escenario haya sido ejecutado en el runtime de Rubrova.

## 1. Reglas para interpretar este mapa

Cada capacidad debe pasar por niveles distintos de evidencia:

1. **Documentada:** aparece en el manual de MyCompany.
2. **Identificada en fuente:** se localizó el módulo LSF y se leyó su implementación.
3. **Composición resuelta:** el módulo forma parte del cierre de dependencias de \`RubrovaCustom\`.
4. **Cargada:** se confirmó que se inicia en la configuración real de Rubrova.
5. **Verificada:** se ejecutó la operación y se revisaron sus resultados.
6. **Conciliada:** se comprobaron sus efectos sobre documentos, stock, deuda, ledgers, reportes y relaciones.
7. **Aceptada:** hay pruebas repetibles, incluidos errores, permisos y excepciones.

Un documento funcional no prueba por sí solo el comportamiento de la versión compilada; un módulo en la composición no prueba que cada una de sus funciones esté habilitada; una pantalla visible no prueba que los asientos o saldos resultantes sean correctos.

## 1.1 Cobertura documental por idioma

El índice automático de recursos del snapshot identifica 347 páginas Markdown de MyCompany: 112 en inglés, 121 en polaco y 114 en ruso. Las tres variantes contienen las mismas 112 rutas de documentación general; el polaco agrega nueve páginas del circuito KSeF y el ruso agrega dos páginas específicas de Mango y marcado de productos.

- **Polaco:** \`invoicing/ksef/automatyzacja.md\`, \`dostep-i-logowanie.md\`, \`faktury-zakupu.md\`, \`ksef.md\`, \`pobieranie-faktur.md\`, \`rozwiazywanie-problemow.md\`, \`sesja-i-szyfrowanie.md\`, \`wprowadzenie.md\`, \`wysylka-faktur.md\`.
- **Ruso:** \`crm/mango.md\` y \`retail/marking.md\`.

Esto confirma que el paquete inglés no es suficiente para comprender las particularidades de todas las integraciones regionales. Los 347 documentos ya están indexados por idioma, ruta, título y encabezados en el artefacto generado por \`audit-source-docs.mjs\`; falta leerlos y vincular cada página a su módulo/función. No hay documentación MyCompany en español en el snapshot.

## 2. Composición e inventario de dominios

El catálogo estático de la revisión fijada identifica 800 módulos LSF de MyCompany. La raíz de la aplicación de Rubrova es \`RubrovaCustom\`; desde esa raíz se alcanza un cierre de 719 módulos: 688 de MyCompany, 24 de lsFusion y 7 extensiones propias. Quedan 112 módulos MyCompany fuera del cierre: 96 regionales y 16 no regionales. No se descartan por ese motivo.

| Dominio fuente | Módulos | Cobertura funcional preliminar |
|---|---:|---|
| Facturación y cuentas | 134 | Facturas, facturas de proveedor, impuestos, pagos, deuda, anticipos/correcciones y relaciones con ventas/compras |
| Inventario | 112 | Depósitos, ubicaciones, recepciones, despachos, transferencias, ajustes, lotes, paquetes, reservas y costos |
| Regionalizaciones | 96 | Variantes por país e integraciones asociadas; se deben identificar individualmente y no asumir compatibilidad argentina |
| Ventas | 92 | Clientes, pedidos, listas de precios, descuentos, envíos, facturas, cobranza y reportes |
| Datos maestros | 84 | Productos/servicios, socios, empresas, categorías, unidades, monedas, contratos y datos de referencia |
| Gestión de proyectos | 78 | Proyectos, tareas, equipos, roles, horas, turnos, partes de horas, Kanban, Gantt y reportes |
| Compras | 49 | Pedidos, listas de precios de proveedor, recepciones, facturas de proveedor, compras automáticas y reportes |
| Fabricación | 41 | Listas de materiales, órdenes, consumo, producción, coproductos, operaciones, centros de trabajo y costos |
| Punto de venta | 30 | POS, cajas, sesiones, recibos, cobros, devoluciones, tarjetas de descuento y control de turnos |
| Recursos humanos | 25 | Selección, entrevistas, asistencia, fichadas móviles/kiosco, recibos de sueldo y pagos |
| CRM | 24 | Leads, estados, campañas, comunicaciones, Kanban, llamadas, correos y conversión a documentos |
| Utilidades | 21 | Funciones de soporte; falta clasificar cada módulo y su alcance |
| Flota | 13 | Vehículos, choferes, asignaciones, servicios, kilometraje, contratos y gastos |
| Raíz | 1 | Composición principal de MyCompany |

Las cantidades son conteos de archivos/módulos de la versión fijada, no cantidades de funciones ni porcentajes de cobertura.

## 3. Circuitos de negocio identificados

### 3.1 Datos maestros como base transversal

Los datos maestros alimentan los documentos y controlan las reglas de selección:

- **Socios:** entidades legales externas, empresas propias y personas individuales. Los socios se utilizan como clientes, proveedores, contratistas, transportistas, bancos y contactos.
- **Empresas propias:** permiten operar con más de una entidad en una misma base, seleccionando cuál compra, vende, paga, cobra y participa del contrato.
- **Artículos:** diferencia entre productos físicos que pueden mover stock y servicios que no deben generar movimientos de inventario.
- **Clasificación:** categorías jerárquicas, atributos, unidades de medida, países, monedas y cotizaciones, departamentos, contratos y actividades.
- **Conservación de historial:** los registros usados en documentos no siempre se pueden borrar; la práctica documentada es archivarlos y conservar sus relaciones.

**Relación transversal:** socio + empresa + artículo + moneda + unidad + impuestos + depósito + condiciones de pago alimentan compras, ventas, inventario, facturación, POS, fabricación y CRM.

**Fuentes de documentación:** \`masterdata/masterdata.md\`, \`partners.md\`, \`items.md\`, \`categories.md\`, \`uom.md\`, \`currencies.md\`, \`contracts.md\`, \`departments.md\`, \`activities.md\`.

**Pendiente:** revisar individualmente todas las propiedades, validaciones, atributos, códigos externos, políticas de archivo y deduplicación en los 84 módulos de datos maestros.

### 3.2 Compras: pedido → recepción → factura de proveedor → pago

La documentación describe el circuito principal:

1. Crear un pedido de compra con proveedor, empresa propia, fecha prevista, depósito (si se usa inventario), moneda, condiciones de pago y renglones.
2. Enviar el pedido al proveedor mediante una plantilla imprimible y correo. El envío modifica el estado del pedido.
3. Confirmar el pedido. Según el tipo y la configuración, puede generarse una recepción de reserva y habilitarse la creación de documentos relacionados.
4. Recibir mercadería. Una recepción puede cubrir parte de las cantidades y se pueden registrar varias recepciones por pedido.
5. Crear una factura de proveedor vinculada al pedido. El modo de control define si se factura la cantidad pedida o sólo la recibida.
6. Pagar la factura mediante el circuito de pagos salientes y controlar lo pagado y pendiente.
7. Aplicar las reglas de bloqueo: según el tipo de pedido, se puede impedir el cierre si hay recepciones activas, cantidades sin recibir o cantidades sin pagar.

Capacidades adicionales documentadas:
- Listas de precios de proveedor con fechas de vigencia, líneas por artículo y comentarios/historial.
- Importación de precios desde fuentes externas mediante tipos de importación configurables.
- Autocompletado de compra sugerida: considera demanda, cantidades pedidas/recibidas, períodos y paquetes de compra.
- Una orden de compra puede generarse automáticamente desde necesidades de fabricación; las líneas de consumo se agrupan por proveedor predeterminado y mantienen el vínculo con las órdenes de fabricación.
- La orden puede generar una orden de fabricación para ciertos artículos según la configuración de su tipo.

**Fuentes de código revisadas parcialmente:** \`purchase/orders/PurchaseOrder.lsf\`, \`PurchaseOrderConfirmed.lsf\`, \`purchase/inventory/receipts/orders/PurchaseOrderReceipt.lsf\`, \`purchase/invoicing/bills/orders/PurchaseOrderBill.lsf\`.

**Fuentes de documentación:** \`purchase/purchase.md\`, \`orders.md\`, \`receipts.md\`, \`bills.md\`, \`pricelists.md\`, \`reports.md\`, \`settings.md\`.

**Pendiente:** revisar los módulos de importación, precios, deuda, cantidades por unidad de medida, anulaciones, facturas parciales, moneda, impuestos, conciliación de pagos y todos los eventos de cambio de estado. Ejecutar y conciliar el circuito completo con entregas parciales, facturas parciales, pagos parciales y cancelaciones.

### 3.3 Ventas: lead → pedido → reserva/entrega → factura → cobranza

El flujo de ventas integra CRM, inventario y facturación:

1. Un lead puede originarse en una llamada, un correo o una carga manual.
2. Desde el lead se puede crear un pedido o una factura, conservando el vínculo con el lead y copiando cliente, tipo documental, dirección y ciertos datos comerciales.
3. Un pedido se registra con cliente, empresa, fecha, fecha prevista de envío, ubicación, dirección de entrega, representante, artículos, cantidades, precios y descuentos.
4. El pedido puede enviarse por correo, confirmarse, bloquearse o cancelarse. La configuración del tipo define los documentos que se pueden crear y las restricciones de cierre.
5. Al confirmar, si hay tipo de envío y depósito, el sistema puede crear o mantener un despacho de reserva. La reserva no descuenta stock; el movimiento de salida ocurre al marcar el despacho como realizado.
6. Se pueden generar varios despachos para cubrir parcialmente un pedido. Las cantidades reservadas, despachadas y pendientes se calculan por renglón y contemplan la conversión de unidades/paquetes.
7. La factura puede basarse en cantidades pedidas o despachadas, según la política de facturación. Se controlan cantidades facturadas y pagadas.
8. Las cuentas por cobrar y los pagos se vinculan al circuito de facturación.

Capacidades comerciales:
- Tipos de precio y listas de precios con vigencia, edición masiva, recálculo de márgenes y copia.
- Descuentos porcentuales o por tipo de precio.
- Condiciones de descuento por artículo/categoría, fecha, tipo de precio, depósito, cantidad mínima, importe, volumen acumulado del cliente, etiquetas del cliente y atributos del artículo.
- La selección automática documentada no acumula descuentos: elige una de las coincidencias con el menor precio resultante.
- Reportes de precios comparados entre fechas, pedidos, ventas, cantidades, facturación, costos, márgenes y resumen por cliente/depósito/categoría.

**Fuentes de código revisadas parcialmente:** \`sales/orders/SalesOrder.lsf\`, \`SalesOrderConfirmed.lsf\`, \`sales/inventory/shipments/orders/SalesOrderShipment.lsf\`, \`sales/invoicing/invoices/orders/SalesOrderInvoice.lsf\`, además de módulos de descuentos y ledgers aún por revisar.

**Fuentes de documentación:** \`sales/sales.md\`, \`orders.md\`, \`workflow-and-statuses.md\`, \`shipments.md\`, \`invoices.md\`, \`pricelists.md\`, \`discounts.md\`, \`reports.md\`, \`settings.md\`.

**Pendiente:** revisar las APIs de ventas y listas de precios, reglas completas de descuentos, promociones, coste/margen, notas de crédito y débito, ventas móviles, reservas simultáneas, cancelaciones y conciliación de stock/ventas/deuda/ledger.

### 3.4 Inventario: recepción, reserva, despacho, transferencia y ajustes

El manual describe un modelo de inventario con:
- Depósitos y ubicaciones, potencialmente con jerarquía y posiciones.
- Recepciones, incluidos ingresos relacionados con pedidos de compra.
- Despachos, incluidos despachos relacionados con pedidos de venta.
- Transferencias entre ubicaciones, modeladas sobre documentos de despacho/recepción según la configuración.
- Reservas de stock, picking y tareas móviles, con cantidades disponibles, esperadas y comprometidas.
- Ajustes por diferencias entre el conteo físico y el saldo del sistema.
- Merma/scrap, lotes, series y paquetes.
- SKU alternativos y coeficientes de conversión.
- Valuación planificada/estándar, costo promedio y FIFO por recepciones/lotes, con ledgers de stock y costo.
- Informes de stock actual/histórico, valorización y movimientos por artículo.

**Reglas documentadas a validar:** la reserva de un despacho no descuenta stock; el despacho realizado registra el movimiento. En ajustes, el movimiento surge al completar el documento, mientras que el borrador/en curso no debe confundirse con un ajuste confirmado.

**Fuentes de documentación:** \`inventory/inventory.md\`, \`receipts.md\`, \`shipments.md\`, \`transfers.md\`, \`adjustments.md\`, \`lots-and-packages.md\`, \`costing.md\`, \`reports-and-ledgers.md\`.

**Pendiente:** mapa exacto de las clases y ledgers, reglas de costo por método y fecha, reversión, serialización, lotes, ubicaciones, inventario negativo, reservas simultáneas, permisos y conciliación por depósito/artículo/unidad.

### 3.5 Facturación, deuda, impuestos y pagos

La documentación enumera:
- Facturas de venta y facturas de proveedor.
- Pagos entrantes y salientes, pagos parciales y asociación de pagos a documentos.
- Deuda pendiente, calendario de pagos y condiciones de pago.
- Impuestos configurables y precios con impuesto incluido o separado.
- Devoluciones y documentos de corrección vinculados al documento original.
- Impresión, reportes y generación de documentos relacionados con envíos.

Regla de deuda documentada: el saldo depende del importe del documento y de los pagos efectivamente asociados; un pago no imputado no debe suponerse aplicado a una deuda concreta. Se deben revisar cancelaciones, pagos parciales, moneda y redondeos.

La documentación distingue entre devolución y corrección de un documento existente. También describe facturas de corrección vinculadas a la original y cadenas de correcciones. Es necesario verificar la semántica en el código y en escenarios de prueba antes de mapearla a comprobantes o conceptos fiscales argentinos.

**Advertencia Argentina:** los grupos y tasas de impuesto de ejemplo en la documentación son genéricos. No prueban integración con ARCA, cumplimiento de factura electrónica argentina, CAE, puntos de venta, tipos de comprobante, notas de crédito/débito argentinas, regímenes de percepción/retención ni reglas provinciales. Todo eso debe revisarse de manera independiente.

**Fuentes de documentación:** \`invoicing/invoicing.md\`, \`invoices.md\`, \`bills.md\`, \`refunds-and-corrections.md\`, \`debt-and-calendar.md\`, \`taxes.md\`, \`settings.md\`, \`incoming-payments.md\`, \`outgoing-payments.md\`.

**Pendiente:** verificar ledgers entrantes/salientes, imputación múltiple, anticipos, notas de crédito/débito, reversión, moneda extranjera, cotización, redondeo, impuestos, impresión y API. La función de corrección/anticipos existe también en módulos fuera del cierre actual y debe evaluarse antes de desarrollar un reemplazo.

### 3.6 Fabricación: lista de materiales → orden → operaciones → producción → costo

La documentación describe:
- Listas de materiales (BOM) con componentes, coproductos y operaciones.
- BOM predeterminadas por artículo, activas/archivadas y con posibles estructuras anidadas.
- Órdenes de fabricación con cantidades previstas, componentes, productos terminados, depósitos de consumo y depósito de producto terminado.
- Chequeo de disponibilidad y reserva de materiales.
- Órdenes de trabajo derivadas de operaciones de BOM, incluso de estructuras intermedias anidadas.
- Centros de trabajo, fechas/horas/duraciones, estado de las operaciones y tablero de carga.
- Registro de consumo real y producción real.
- Desarme/unbuild, scrap/merma, lotes y etiquetas.
- Costos de materiales, adicionales por scrap, mano de obra por tiempos de proyectos y servicios imputados desde facturas.
- Distribución del costo a los productos terminados mediante coeficientes. Cuando no hay coeficientes, la documentación indica que el costo se asigna al producto principal.

Estados documentados de orden: borrador, espera, lista para ejecutar, en curso, terminada y cancelada. La verificación de disponibilidad condiciona el paso a lista; al terminar se requiere indicar la ubicación del producto terminado.

Relaciones importantes:
- Una orden de venta puede generar órdenes de fabricación; si ya empezó la fabricación, se restringen cambios en la línea de venta vinculada.
- Las órdenes de fabricación pueden generar pedidos de compra por proveedor para materiales faltantes.
- El costo de mano de obra puede venir del módulo de proyectos; el costo de servicios, de facturas de proveedor.
- Las BOM permiten coproductos y operaciones, por lo que no se debe modelar la fabricación como una simple fórmula de consumo.

**Fuentes de código revisadas parcialmente:** \`manufacturing/bom/Bom.lsf\`, \`BomNested.lsf\`, \`orders/ManufacturingOrder.lsf\`, \`ManufacturingOrderReady.lsf\`, \`ManufacturingOrderCost.lsf\`, \`workOrders/WorkOrder.lsf\`, \`WorkCenterLoad.lsf\`, \`orders/ManufacturingOrderLot.lsf\`.

**Fuentes de documentación:** \`manufacturing/manufacturing.md\`, \`bom.md\`, \`orders.md\`, \`workflow.md\`, \`production-and-consumption.md\`, \`work-orders.md\`, \`costing.md\`, \`by-products.md\`, \`unbuild.md\`, \`scrap.md\`, \`lots-and-printing.md\`, \`reports.md\`, \`settings.md\`, \`sales-orders.md\`.

**Pendiente:** probar rendimiento de BOM anidadas, redondeos y coeficientes, reservas, faltantes, sustituciones, lotes, scrap, desarme, variaciones reales, distribución de costos y conciliación de ledgers.

### 3.7 Retail / POS: sesión → venta → cobro → devolución → cierre

Capacidades documentadas:
- Cajas registradoras vinculadas a empresa y, opcionalmente, computadora.
- Apertura y cierre de sesiones; no se permite abrir una segunda sesión simultánea para la misma caja.
- Pantalla POS con búsqueda, lector de código de barras, grilla táctil por categorías, atajos y ventas contra pedido.
- Identificación de cliente y tarjetas de descuento.
- Artículos marcados y lotes cuando están habilitados.
- Pagos combinados entre distintos medios; cálculo de vuelto para efectivo.
- Controles para no cobrar un importe insuficiente y no exceder el importe a cobrar con medios no efectivo.
- Depósitos y retiros de efectivo.
- Devolución asociada al comprobante original; copia artículos, precios y descuentos y limita el reintegro por medio de pago a lo efectivamente pagado por ese medio en la venta.
- Cierre de sesión con total de ventas menos devoluciones, importes por medio, recibos, devoluciones, depósitos y retiros.

**Distinción fundamental:** el POS y la gestión de sesión/caja sí están documentados; eso no significa que esté resuelta la emisión fiscal argentina. El módulo fiscal genérico fuera del cierre base expone puntos de extensión, pero todavía se debe identificar un controlador concreto, hardware compatible, protocolo, seguridad, manejo de contingencias y homologación que corresponda.

**Fuentes de documentación:** \`retail/retail.md\`, \`pos.md\`, \`sessions.md\`, \`payments.md\`, \`returns.md\`, \`discount-cards.md\`, \`settings.md\`.

**Pendiente:** arqueo esperado versus real, diferencias de caja, retiros/depósitos, cierres parciales, pagos electrónicos, devoluciones sin comprobante original, integración con terminales, impresoras y controlador fiscal argentino.

### 3.8 CRM: consultas → lead → seguimiento → venta

Capacidades documentadas:
- Leads con tipo, estado, persona responsable, cliente, artículo, prioridad, tags y datos de contacto.
- Pronóstico de ingreso, probabilidad y fecha esperada de cierre.
- Campañas, medios y orígenes de marketing.
- Tablero Kanban por estado, cambios mediante arrastrar y soltar, historial y filtros.
- Registro de llamadas y correos, bandeja de comunicaciones por procesar, asociación con leads existentes o creación de uno nuevo.
- Integración documentada con telefonía Zadarma mediante API/webhooks, identificación del contacto, registro de llamada y posible desvío a un interno.
- Conversión de un lead en pedido de venta o factura, conservando el vínculo.
- Reportes por responsable, estado, fecha de creación/cierre, campaña, medio y origen.

**Fuentes de documentación:** \`crm/crm.md\`, \`leads.md\`, \`kanban.md\`, \`communications.md\`, \`sales-and-documents.md\`, \`reports.md\`, \`settings.md\`, \`zadarma.md\`.

**Pendiente:** idempotencia de webhooks, tratamiento de llamadas duplicadas, múltiples contactos para un teléfono, permisos, privacidad, auditoría, plantillas, integración real de correo y telefonía, y relación con los módulos de mensajería externos de lsFusion.

### 3.9 Recursos humanos: selección → empleado → asistencia → haberes

Capacidades documentadas:
- Postulaciones, posiciones, departamentos, reclutadores, entrevistas, participantes y resultados.
- Adjuntos, etiquetas, llamadas y correos al postulante.
- Acciones para contratar o rechazar, con motivo de rechazo y plantillas de correo.
- Registro de asistencia móvil con geolocalización y kiosco con credencial; posibilidad de usar fotos si el dispositivo está configurado.
- Entrada/salida inferida del último registro abierto; control de duplicación de lectura en el kiosco.
- Recibos de sueldo por empleado, período, empresa, moneda y tipo.
- Renglones de haberes y descuentos con cantidad, importe y total; banderas para excluir u ocultar renglones.
- Generación por lote, evitando duplicados para la combinación documentada de período, empleado, entidad legal y tipo.
- Integración con horas cargadas en proyectos y control de importes a pagar versus pagados.

**Advertencia Argentina:** las páginas describen un motor configurable de recibos y pagos, no un sistema de liquidación laboral argentino validado. No se debe inferir cumplimiento de convenio, escalas, cargas sociales, aportes, retenciones, Libro de Sueldos Digital, SICOSS/ARCA, ART, vacaciones, aguinaldo ni normativa provincial a partir de estas funciones genéricas.

**Fuentes de documentación:** \`humanResources/humanResources.md\`, \`recruitment.md\`, \`attendance.md\`, \`payroll.md\`, \`payroll-batch.md\`, \`payslip.md\`, \`net-wage.md\`, \`payroll-time-entries.md\`, \`payroll-payments.md\`, \`settings.md\`.

**Pendiente:** reglas de calendario, horas extras, ausencias, permisos, datos biométricos/fotos, acceso a ubicación, retención de datos, configuración real de haberes y validación legal argentina. La asistencia y el cálculo de sueldo deben analizarse como subsistemas separados.

### 3.10 Gestión de proyectos: tareas → asignaciones → tiempos → costos

Capacidades documentadas:
- Proyectos con tipo, empresa, socio, responsable, fechas y estado.
- Tareas con responsable, asignado, prioridad, fechas, avance, comentarios, archivos e historial.
- Workflows de estados y transiciones por tipo de tarea, rol de proyecto, autor o asignado.
- Kanban y Gantt, dependencias entre tareas y reportes de esfuerzo.
- Equipos, roles, asignaciones y turnos.
- Carga de tiempos/horas por proyecto, tarea y empleado; partes de horas del empleado y del supervisor.
- Integración de horas a costos de mano de obra en órdenes de fabricación.

**Fuentes de documentación:** \`projectManagement/projectManagement.md\`, \`projects.md\`, \`tasks.md\`, \`time-entries.md\`, \`shifts.md\`, \`timesheets.md\`, \`team-and-roles.md\`, \`reports.md\`, \`settings.md\`.

**Pendiente:** autorización de carga retroactiva, cierres de período, redondeos, tarifas históricas, tiempos aprobados/rechazados, dependencias de tareas, notificaciones, calendarios y conciliación de horas con haberes y costos de fabricación.

### 3.11 Flota: vehículo → asignación de conductor → mantenimiento → gasto

Capacidades documentadas:
- Vehículos con dominio, VIN, modelo, categoría, combustible, año, empresa, etiquetas y archivos.
- Asignación de conductores por período con fecha de inicio y fin; historial para conocer quién era responsable en una fecha.
- Servicios de vehículo con fecha, proveedor, odómetro, cantidad, precio, importe, impuesto y descripción.
- Control de kilometraje para historial y mantenimiento.
- Contratos vinculados al vehículo cuando el tipo de contrato lo permite.
- Posibilidad de vincular el gasto de servicio con documentos de facturación.

**Fuentes de documentación:** \`transport/transport.md\`, \`vehicles.md\`, \`drivers.md\`, \`service.md\`, \`contracts.md\`, \`settings.md\`; fuentes LSF bajo \`fleet/vehicles\` y \`fleet/vehicles/service\`.

**Pendiente:** vencimientos, seguros, patentes, VTV, mantenimiento preventivo, combustible, costos por kilómetro, asignaciones superpuestas, odómetros inconsistentes y alertas. No se debe asumir que todo eso esté implementado por el solo hecho de existir el dominio de flota.

## 4. Módulos fuera del cierre actual: revisar antes de programar reemplazos

El inventario completo de los 96 módulos regionales por país y ruta está en [MYCOMPANY_6_2_REGIONAL_MODULES.md](MYCOMPANY_6_2_REGIONAL_MODULES.md). Incluye capacidades iniciales inferidas y el nivel de lectura de fuente; no representa una aceptación funcional.


Los 112 módulos MyCompany fuera del cierre de \`RubrovaCustom\` no están descartados. Se separan en 96 módulos regionales y 16 no regionales. Los 16 no regionales documentados individualmente se detallan en el manual de ingeniería, sección 9.7; incluyen lotes en put-away/picking, correcciones y anticipos, GTIN, impresión de deuda, \`CashRegister\`, \`CashRegisterFiscal\`, \`Crypto\`, \`Audio\` y \`PosDashboardReturnShipment\`.

La regionalización contiene 7 módulos de Bulgaria, 26 de Polonia y 63 de Rusia. Entre ellos hay capacidades de impuestos/impresión/documentos, marcación, pagos, certificados, datos legales, telefonía y conectores específicos. No se debe traducir el nombre de un módulo ni suponer que su presencia equivale a soporte normativo argentino. Cada módulo regional requiere una ficha que explique país, proveedor, servicio externo, configuración, dependencias, licencias, credenciales, datos transmitidos y límites legales.

## 5. Adecuación a Argentina: temas que no se deben dar por resueltos

El relevamiento funcional debe distinguir capacidad genérica de adecuación local. Como mínimo, falta validar por separado:

- Comprobantes y facturación electrónica argentina, integración con ARCA, certificados, puntos de venta, numeración, CAE, notas de crédito/débito y contingencias.
- IVA, percepciones/retenciones, impuestos internos y reglas provinciales/municipales aplicables.
- CUIT, padrones y validación de condición fiscal de clientes/proveedores.
- Monedas, cotizaciones, redondeos, fechas de vigencia y tratamiento contable local.
- Liquidación de haberes, convenios, cargas sociales, aportes y retenciones.
- Medios de pago, adquirentes, transferencias, QR, conciliación bancaria y terminales.
- Protección y conservación de datos personales, geolocalización, fotos, comunicaciones y credenciales.
- Idioma de interfaz, plantillas, reportes, documentación operativa y formatos argentinos.

Que un campo admita una tasa o un identificador no prueba que el sistema implemente la normativa correspondiente. La revisión local requiere estudiar módulos regionales, adaptadores disponibles, dependencias externas y pruebas/certificaciones específicas.

## 6. Estado de evidencia por dominio

| Dominio | Manual fuente | Código revisado | Runtime | Conciliación E2E |
|---|---|---|---|---|
| Datos maestros | Lectura inicial | Parcial | Pendiente | Pendiente |
| Compras | Lectura inicial | Parcial: pedido, confirmación, recepción y factura | Pendiente | Pendiente |
| Ventas | Lectura inicial | Parcial: pedido, confirmación, despacho y factura | Pendiente | Pendiente |
| Inventario | Lectura inicial | Pendiente de profundizar ledgers y reglas | Pendiente | Pendiente |
| Facturación y deuda | Lectura inicial | Parcial | Pendiente | Pendiente |
| Fabricación | Lectura inicial | Parcial: BOM, orden, disponibilidad, costos y work orders | Pendiente | Pendiente |
| Retail/POS | Lectura inicial | Pendiente de profundizar sesión, caja, cobros y devoluciones | Pendiente | Pendiente |
| CRM | Lectura inicial | Pendiente de profundizar ciclo de lead y webhooks | Pendiente | Pendiente |
| Recursos humanos | Lectura inicial | Pendiente de profundizar asistencia y haberes | Pendiente | Pendiente |
| Proyectos | Lectura inicial | Pendiente de profundizar tiempos, roles y workflows | Pendiente | Pendiente |
| Flota | Lectura inicial | Pendiente de profundizar historial y gastos | Pendiente | Pendiente |

**Conclusión:** hay evidencia suficiente para afirmar que MyCompany 6.2 contiene una cobertura ERP amplia y varios circuitos integrados. No hay evidencia suficiente para afirmar que hayamos identificado y comprendido la totalidad de sus 800 módulos ni que los procesos estén probados en Rubrova. La puerta sigue abierta.
