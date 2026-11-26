# Auditoría de reutilización de la base incorporada: lsFusion 6.2 + MyCompany 6.2

**Estado:** auditoría de fuentes y contratos; lo observado en código se distingue de lo que aún requiere prueba de runtime.  
**Revisión Rubrova:** 475ca9224520d296b23990071b1c79f00d6dced9.  
**Plataforma fijada:** lsFusion 6.2, commit dd4dbe5bf9b136e73e18fe25d741253929324350.  
**ERP/POS fijado:** MyCompany 6.2, commit d21ca6978717b98b6300d90267f9767db7414008.

> La regla para el producto es aprovechar primero el comportamiento nativo completo. No crear un documento, ledger, API o proceso Rubrova equivalente hasta haber seguido su implementación base desde la pantalla/acción hasta el documento, los estados, los pagos, los ledgers y los informes.

## 1. Resultado ejecutivo

El inventario fijado por el repositorio declara 1.335 archivos MyCompany, incluidos 800 módulos LSF, y 4.887 archivos de lsFusion, incluidos 3.330 fuentes Java. Los metadatos exactos están en platform/source-lock.json y platform/mycompany-6.2.lock.json. Son snapshots completos, versionados dentro de Rubrova.

La composición principal MyCompany.lsf requiere:
- servicios de plataforma: Eval, ProcessMonitor, Backup, Chat y Documentation;
- datos maestros: MasterDataP;
- Inventory, Invoicing, InvoicingInventory, Purchase, Sales y Retail;
- Manufacturing, ProjectManagement, HumanResources, CRM y Fleet;
- BillReceiptCost y BillReceiptCostService.

La base incorporada es sustancialmente más amplia que lo que Rubrova había comenzado a utilizar. Esta auditoría encontró capacidades adicionales que ya podemos aprovechar:

1. Stocktake de mercadería con teórico, conteo real, hojas separadas, búsqueda por barcode y contabilización de diferencias en el ledger.
2. Transferencias, aceptación, picking por ubicación, put-away, lotes/series y mermas.
3. Costeo FIFO, AVCO/promedio y precio estándar; valoración histórica; costo real de recepciones, despachos, ajustes y fabricación; asignación de fletes/servicios.
4. APIs nativas de catálogo, categorías, atributos, precios, inventario, pedidos y tareas.
5. Autenticación, roles/permisos, acceso por depósito, backups, scheduler, monitor de procesos y visor de documentación.
6. CRM a pedido, órdenes de compra vinculadas a ventas, fabricación a compras, calendario de deudas y caja.
7. Adaptadores regionales opcionales que contienen patrones útiles, pero no están activos ni listos para Argentina.

La conclusión no es cargar todo sin criterio. Es consumir la lógica base, mantener sus ledgers como autoridad, y sumar en Rubrova las diferencias que realmente necesitemos.

## 2. Qué está incorporado y qué está activo

### 2.1 Composición principal

MyCompany.lsf carga la mayoría de los dominios de ERP/POS y los módulos transversales señalados arriba. Que un dominio esté incluido no garantiza que toda función esté activada: dependen de tipos de documento, default data, parámetros, permisos y configuración de compañía.

El código bajo vendor/mycompany/src/main/lsfusion/region/ también está incorporado al snapshot, pero no forma parte de MyCompany.lsf. En el árbol revisado hay raíces regionales BG, PL y RU; no hay raíz Argentina/ARCA.

### 2.2 Integraciones regionales

| Raíz opcional | Ejemplos de capacidad | Decisión para Rubrova |
|---|---|---|
| MyCompanyRu | driver fiscal ATOL, Wazzup, EnterpriseData, CRPT, DaData, FusionWMS, telefonía | no activar indiscriminadamente; adaptar proveedor, seguridad y país |
| MyCompanyPl | KSeF, certificados/tokens, consulta y envío de facturas, REGON | no activar en Argentina |
| BG | telefonía Zadarma y módulos asociados | estudiar el patrón, no la configuración |

MyCompanyRu.lsf y MyCompanyPl.lsf declaran explícitamente las dependencias regionales. No deben agregarse a RubrovaCustom sólo porque sus fuentes estén presentes.

El modelo genérico Tax/TaxGroup/TaxItem permite calcular impuestos y precios con/sin impuestos. No hay una raíz Argentina/ARCA en el snapshot revisado. La facturación fiscal argentina requiere un adaptador propio con CAE/CAEA, comprobantes, puntos de venta, contingencia, reintentos y reconciliación.

## 3. Capacidades nativas que Rubrova debe reutilizar

### 3.1 Datos maestros

MyCompany ya tiene:
- Item/Product/Service, categorías jerárquicas, variantes, atributos, UOM, imágenes y códigos de barra;
- Partner, Individual, LegalEntity, clientes/proveedores, contactos, bancos, historial, etiquetas y atributos;
- Employee, Company, Department, Location, Currency, Country y ExchangeRate;
- ItemCost con costo planificado por fecha.

Rutas principales: masterdata/items/, masterdata/partners/, masterdata/partners/employees/, masterdata/company/, masterdata/locations/ y masterdata/currency/.

**Regla:** no crear clases paralelas de producto, cliente, proveedor, sucursal o marca cuando corresponda extender el objeto nativo. Una integración no debe fabricar una segunda identidad del mismo artículo.

### 3.2 POS, turnos, pagos y caja

MyCompany implementa:
- Pos como caja lógica y Session como turno;
- openedSession(Pos) y openSession para evitar dos turnos abiertos en una caja;
- beforeOpen/afterOpen y beforeClose/afterClose como puntos abstractos;
- factura minorista, líneas, búsqueda, barcode, touch, descuentos y totalización;
- pagos divididos por PaymentMethod, creando IncomingPayment por cada medio;
- devolución Bill y egresos OutgoingPayment por medio;
- depósito y retiro de efectivo como movimientos financieros separados;
- saldos teóricos por cuenta y netos del turno por medio.

Fuentes: retail/pos/, retail/sessions/Session.lsf, SessionInvoice.lsf, SessionPayment.lsf, PosDashboardPayment.lsf y PosDashboardCash.lsf.

Los medios iniciales son efectivo y tarjeta. QR, transferencia y otros métodos se configuran con PaymentMethod, tipos financieros y cuentas; no justifican crear otro ledger.

**Distinción crítica:** Session/POS conserva pagos, depósitos, retiros y saldo teórico. En el modelo POS central inspeccionado no encontré conteo físico de billetes/monedas. El arqueo de efectivo es una capacidad Rubrova pendiente, distinta del stocktake de mercadería descrito abajo. No ajustar el saldo financiero sobrescribiendo Payment.

### 3.3 Compras, ventas, facturas y deuda

MyCompany ya soporta:
- pedidos de compra/venta confirmados;
- recepciones y despachos parciales;
- reservas antes del movimiento físico;
- políticas de facturación por cantidad pedida o por cantidad recibida/despachada;
- Bills/Invoices, notas de crédito, cobros, pagos y conciliación de deuda;
- descuentos por producto, atributos, tags de socio y ubicación;
- listas de precios y precios históricos;
- impuestos genéricos y tax-inclusive price.

Los documentos mantienen relaciones a sus líneas originales. Pedido, recepción/despacho, factura/nota de crédito y pago son etapas diferentes; sus estados y cantidades no son intercambiables.

Módulos representativos: PurchaseOrderReceipt, PurchaseOrderBill, PurchaseOrderBillReceipt, SalesOrderShipment, SalesOrderInvoice, SalesOrderInvoiceShipment, BillDebt, BillPayment, InvoiceDebt, SessionPayment y Payment.

### 3.4 Inventario físico: el stocktake ya existe

Esta fue una omisión importante de la investigación anterior. MyCompany ya implementa un circuito de conteo físico con diferencias contabilizadas en el ledger.

Fuentes:
- inventory/adjustments/Adjustment.lsf
- AdjustmentInProgress.lsf
- AdjustmentDone.lsf
- AdjustmentCreate.lsf
- inventory/adjustments/lists/AdjustmentList.lsf
- AdjustmentListSearch.lsf
- AdjustmentCost.lsf

Flujo observado:
1. Se crea Adjustment para ubicación, tipo y opcionalmente categoría.
2. Fill crea las líneas de productos/ubicaciones elegibles y calcula theoreticalQuantity desde prevOnHandB(location, product, dateTime(ajuste)); es teórico histórico a la fecha del conteo.
3. En borrador, realQuantity se inicia con theoreticalQuantity si no se usa la agregación de hojas.
4. Mark as ToDo pasa el ajuste a inProgress; el operador carga cantidades reales y puede filtrar mismatch, surplus y missing.
5. Con useList se crean AdjustmentList separadas; se agregan cantidades por producto/ubicación al ajuste padre. AdjustmentListSearch incorpora captura por barcode.
6. Validate marca done y genera InvAdjustment con realQuantity menos theoreticalQuantity.
7. InvAdjustment se incorpora al InvLedger; AdjustmentCost contempla su costo.

**Uso Rubrova:** extender el proceso nativo con conteo ciego, asignación por zona/operador, reconteo, tolerancias, autorización de diferencias, evidencias y auditoría si hacen falta. No crear una segunda tabla de stock ni otro motor de diferencias.

**Pruebas pendientes:** producto omitido, conteo cero, líneas duplicadas en hojas, producto en varias ubicaciones, cambio de stock entre fecha teórica y conteo, reconteo, cancelación, doble validación, permisos y costo de ajuste. Verificar Fill para productos con onHand cero y el mecanismo para agregar artículos no incluidos automáticamente.

### 3.5 Operación logística, lotes y mermas

MyCompany también incluye:
- TransferBulkCreate y TransferMobile;
- ShipmentAcceptance con confirmación de recepción por depósito;
- LocationProduct para ubicar productos;
- ShipmentPicking por ubicación y PickingTaskMobile;
- ReceiptPutAway para distribuir mercadería recibida en ubicaciones hijas;
- Scrap/ScrapInv para registrar merma y salida física;
- Lot, ReceiptLot, ShipmentLot, AdjustmentLot, ScrapLot, InvoiceLot, CreditNoteLot y POS lotes/series.

Los módulos de lotes manejan barcode, asignación de cantidad por lote y validación de que la suma de lotes coincida con la cantidad de línea. La cantidad física sigue contabilizándose a través de sus ledgers, no mediante un stock Rubrova duplicado.

### 3.6 Costos y rentabilidad

Hay tres conceptos diferentes:

1. ItemCost: costo planificado/histórico del producto por fecha.
2. CostLedger: costo real de movimientos de inventario, con métodos standardPrice, avco y fifo, heredados/configurados por categoría/producto.
3. SalesLedger: hechos comerciales de facturas y devoluciones con cantidad, importe, impuestos, costo y margen.

Módulos:
- inventory/ledgers/cost/CostProduct.lsf
- masterdata/items/ItemCost.lsf
- inventory/ledgers/cost/CostLedger.lsf
- inventory/receipts/ReceiptCost.lsf
- inventory/shipments/ShipmentCost.lsf
- inventory/adjustments/AdjustmentCost.lsf
- invoicing/inventory/receipts/BillReceiptCost.lsf
- BillReceiptCostService.lsf
- manufacturing/orders/ManufacturingOrderCost.lsf
- sales/ledgers/SalesLedger.lsf
- SalesLedgerInvoiceShipment.lsf
- SalesLedgerBillReceipt.lsf

BillReceiptCost y BillReceiptCostService asignan costo de la factura de proveedor y gastos de servicios a las recepciones. ManufacturingOrderCost separa materiales, extra, mano de obra y servicios. SalesLedgerInvoiceShipment añade costos reales de ShipmentLine a las facturas vinculadas; SalesLedgerBillReceipt añade costos reales de ReceiptLine a las devoluciones vinculadas.

**Regla para los márgenes:** usar el ledger comercial y preservar si el costo viene de ItemCost planificado o del movimiento real. Probar facturas con/sin ShipmentLine, devoluciones con/sin ReceiptLine, descuentos, costos de servicio, moneda y ajustes retroactivos.

**Riesgo FIFO que requiere regresión:** CostLedger.lsf tiene comentados filtros temporales dateTime(InCostLedger) <= dateTime(OutCostLedger) en dos bloques de asignación FIFO. No concluyo que sea un bug; sí significa que no debemos afirmar que el costo FIFO histórico está validado hasta probar una salida fechada antes de una entrada, varias capas y recálculo desde fecha.

### 3.7 Fabricación y compras por demanda

BOM, operaciones, centros de trabajo, ManufacturingOrder, WorkOrder y costos ya están implementados. Consumos y productos terminados alimentan InvLedger; reservas de materiales y producción planificada afectan ResLedger/available según la opción increaseAvailableStock. PurchaseOrderManufacturingAuto calcula demanda de materiales por consumos/periodos y MyCompany 6.2 permite crear pedidos de compra desde órdenes de fabricación seleccionadas.

No reconstruir BOM, cálculo de consumo, reservas de fabricación o costo de producción como servicios Rubrova paralelos.

### 3.8 CRM, proyectos, RR. HH. y flota

- CRM: leads, actividades/llamadas, campaña/medio/fuente, artículos y acción de creación de Sales.Order desde un Lead.
- Proyectos: Project/Task, asignación, equipos, kanban, horas, timesheets, asistencia, turnos y relaciones a ventas, compras, facturas, fabricación y logística.
- HR: empleados, postulaciones, asistencia, nómina/payslips, tipos y numeración, tarifas históricas.
- Fleet: vehículos, conductores, contratos, mantenimiento y servicios.

Estos dominios ya existen. Sólo debemos activarlos y extenderlos cuando haya un caso de uso real.

### 3.9 Cuentas, deuda, bancos y calendario

Además de IncomingPayment/OutgoingPayment, MyCompany trae:
- Payment/Account y saldos históricos;
- IncomingDebt/OutgoingDebt, matching y saldos pendientes;
- importación/exportación bancaria;
- PaymentCalendar para proyectar cambios de deuda y saldo esperado;
- Tax/TaxGroup/TaxItem y cálculos genéricos;
- documentos aduaneros y otros flujos financieros.

El saldo proyectado no equivale a extracto bancario conciliado ni a efectivo contado.

## 4. APIs existentes que no debemos ignorar

Los módulos siguientes están en los árboles de dominio requeridos y aportan acciones marcadas @@api:

| API nativa | Función | Límite observado |
|---|---|---|
| MasterData.getItems | catálogo, barcode, categoría, UOM, país; imagen/descripción opcional | probar filtros, volumen y esquema |
| MasterData.getCategories | jerarquía de categorías | versionado y claves |
| MasterData.getItemAttributes | valores de atributos por artículo | atributos opcionales/dinámicos |
| Sales.getPrices | precio por tipo/lista y fecha | moneda, impuestos y vigencia |
| Inventory.getInventory | onHand por producto/ubicación | no devuelve available/reservas |
| Sales.newOrders | importar pedidos y líneas desde JSON | sólo alta; número existente hace que se ignore la fila |
| Sales.deleteOrders | borrar pedidos por número | sólo estado draft; no cancela confirmados |
| ProjectManagement.getTasks/addTasks | consultar/importar tareas | mapear relaciones, IDs y asignados |

### SalesOrderAPI: contrato observado

newOrders importa JSON, crea Sales.Order si el número no existe y copia cabecera y líneas; luego aplica el cambio y eleva applyMessage si la transacción no se pudo confirmar. No es un upsert: un número ya existente no actualiza sus líneas/campos. No hay idempotencyKey ni schemaVersion explícitos en la implementación inspeccionada. deleteOrders borra sólo drafts por número. El ejemplo de exportación está comentado.

**Decisión:** comenzar por API nativa. Si la integración necesita upsert, eventos, idempotencia remota, paginación, versión, correlación, permisos o reconciliación, agregar un wrapper/adapter versionado sobre el dueño nativo. No exponer la API suponiendo que es un contrato bidireccional completo.

## 5. Plataforma: seguridad, scheduler, monitor y backup

### 5.1 Seguridad y permisos

Authentication y Security implementan usuarios, roles múltiples, rol principal y permisos permit/forbid/default por navegación, grupos, propiedades y acciones. MyCompany LocationEmployee agrega acceso a ubicaciones por empleado; macros documentales insertan filtros y constraints en documentos según el depósito.

Reutilizar esos mecanismos. Rubrova sí debe agregar auditoría de negocio y matriz de permisos por función sensible, pero no otro login ni una autorización basada solamente en ocultar botones.

### 5.2 Scheduler y operación

Scheduler permite periodicidad, fecha/hora, días, orden de acciones, timeout, ignoreExceptions y logs. Se activa desde onStarted; las tareas deben existir y estar activas. ProcessMonitor aporta diagnóstico de procesos, stack y SQL. Documentation brinda visor Markdown; Eval es el intérprete administrativo y no debe exponerse a integraciones.

Que exista una tarea configurada no garantiza que corra cuando la PC está apagada.

### 5.3 Backup nativo vs backup Rubrova

Backup.lsf aporta backup completo/parcial, exclusión de datos, logs, retención y restauración selectiva. El valor por defecto crea una tarea diaria a las 01:00 con makeBackup y decimateBackups desde loadDefaultData; hay que verificar configuración/actividad del scheduler y dumpDir/binPath en cada instalación.

PostgreDataAdapter usa pg_dump en custom format o directory multithreaded. La restauración selectiva usa pg_restore en una base temporal, para leer tablas/columnas y reintroducir datos al modelo lógico; no es sustituto de restaurar toda la base.

**Riesgo upstream concreto:** customRestoreDB devuelve el nombre de la DB temporal desde el catch de IOException de pg_restore y no hace dropDB en ese catch. Por tanto, un retorno no nulo no demuestra una restauración correcta y puede dejar una DB parcial. No usar restauración selectiva para recuperar datos críticos hasta agregar/regresar esa condición y validar limpieza.

La rutina Rubrova native-postgres-backup.py ya crea un paquete con manifiesto/SHA-256 y restaura sólo en una DB nueva, protegiendo la original. Mantenerla como complemento; sumar copia fuera del equipo y cobertura de archivos/adjuntos/configuración/secretos.

## 6. Integraciones regionales: patrones sí, activación no

### ATOL / driver fiscal local

CashRegister.lsf define CashDriver por POS. CashRegisterAtol extiende esa clase con bridge local HTTP, autenticación Basic y hooks openShift/closeShift/cashIn/cashOut/sell/sellReturn. Es un patrón valioso para futura impresora/driver fiscal argentino. El payload ATOL, los tipos de impuestos y el protocolo corresponden a Rusia; no se pueden reutilizar tal cual para ARCA.

### Wazzup / WhatsApp CRM

Wazzup sincroniza Leads por POST y recibe eventos de contactos/deals. El handler revisado lleva @@api @@noauth, registra el body completo y no muestra verificación de firma. No copiar ese comportamiento: Rubrova requiere verificar origen/firma, deduplicar durablemente, no loguear PII innecesaria y guardar credenciales en un secreto seguro.

### EnterpriseData, KSeF, WMS y telefonía

EnterpriseData importa/exporta estructura de pagos y cuentas estilo 1C; KSeF gestiona certificado/token, sesión, envío y consulta de documentos polacos; FusionWMS integra almacén; CRPT/trazabilidad, DaData y Mango/Zadarma son regionales. Son ejemplos para estudiar la arquitectura del adapter, no integraciones listas para Argentina.

## 7. Qué utiliza Rubrova hoy y qué no

| Módulo Rubrova | Estado real |
|---|---|
| RubrovaPOSLocalization | extensión visual/configuración de MyCompany; no sustituye venta/pagos nativos |
| RubrovaReplenishmentExport | exportación de sólo lectura de hechos nativos y semántica versionada |
| RubrovaIntegrationResilience | incidencias, clasificación HTTP y helper GET con timeout; no es cliente POST genérico ni motor de reintentos |
| RubrovaPaymentTerminals | modelo de cuentas/terminales/intenciones/intentos/eventos/reintegros/liquidaciones; no ejecuta cobros reales ni bridge/webhook |
| RubrovaRetailReturns | extensión de CreditNote.fill para cantidades remanentes, en PR #13; todavía requiere aceptación funcional y merge |
| RubrovaCISalesFixture | datos y escenarios sintéticos de CI; no son operaciones comerciales reales |

No se debe interpretar “modelo de datos”, “módulo requerido” o “compila” como “integración operativa”.

## 8. Matriz de reutilización prioritaria

| Prioridad | Capacidad Rubrova | Base que se debe reutilizar | Extensión propia justificada |
|---|---|---|---|
| P0 | POS/ventas/devoluciones | Invoice, Bill, Payment, Session, ledgers | brechas de devolución acumulada, auditoría y UX |
| P0 | Inventario físico | Adjustment/AdjustmentList/InvAdjustment | conteo ciego, reconteo, asignación y autorización |
| P0 | Caja | Session/Payment/depósitos/retiros | arqueo físico de efectivo y diferencias |
| P0 | Permisos | Security/LocationEmployee | matriz específica de operaciones y trazabilidad |
| P1 | Rentabilidad | CostLedger/InventoryValuation/SalesLedger | análisis por área/canal y verificación de coste real |
| P1 | Compras/ventas mayoristas | PurchaseOrder/SalesOrder, recepciones/despachos parciales | compra sugerida, condiciones, logística y canales |
| P1 | E-commerce/marketplaces | Item/Category/Price/Order/Inventory APIs | wrapper versionado, stock disponible, idempotencia y reconciliación |
| P1 | Lotes/vencimientos | Lot/ReceiptLot/ShipmentLot/POS lot | FEFO, alertas y políticas locales |
| P1 | Fabricación | BOM/ManufacturingOrder/WorkOrder/costos | planificación de capacidad y análisis de demanda |
| P2 | CRM/proyectos/HR/flota | dominios completos existentes | activar módulos según necesidad del negocio |
| P2 | ARCA | Tax genérico y documentos base | adapter fiscal argentino homologado |
| P2 | Terminales | CashDriver y patrón ATOL como referencia | driver argentino, bridge, webhook, idempotencia y hardware E2E |

## 9. Método obligatorio antes de implementar

1. Localizar el módulo dueño y el módulo raíz que lo carga.
2. Leer documento, líneas, estados, constraints, hooks y datos iniciales.
3. Seguir la relación hasta el ledger y los informes que consumen el hecho.
4. Comprobar cancelación, devolución, edición, duplicados y concurrencia.
5. Consumir el proceso/API nativa cuando cubra el caso.
6. Crear wrapper o hook Rubrova sólo para lo que falta y documentar su contrato.
7. Añadir pruebas de vacío/NULL, parcial, duplicado, límite, permiso, cancelación, concurrencia, reinicio y datos históricos.
8. Ejecutar preflight, compilación, carga real, API autenticada y E2E con DB controlada.
9. Mantener la diferencia entre inspección de código, aceptación CI, datos reales y producción.

## 10. Riesgos que deben convertirse en tests

| Riesgo | Prueba requerida |
|---|---|
| FIFO con fechas retroactivas | salida antes de entrada, varias capas, transferencia y recálculo |
| SalesLedger | factura con/sin ShipmentLine; devolución con/sin ReceiptLine; prioridad planificado vs real |
| Stocktake | cero, omitido, duplicado entre hojas, reconteo, cambio de stock después de fecha teórica y doble confirmación |
| Efectivo físico | contado vs esperado, diferencias, permisos, motivos y ajuste sin tocar Payment.balance |
| SalesOrderAPI | número duplicado con payload distinto, draft vs confirmado, cliente/empresa/ubicación inválidos, timeout tras APPLY |
| Inventory API | onHand vs available, reservas, múltiples ubicaciones y colección vacía |
| Webhook | firma inválida, replay, duplicado, evento tardío, PII y secreto |
| Bridge fiscal | timeout después de aceptar, UUID idempotente, polling, reinicio, cancelación y reimpresión |
| Backup | fallo de pg_restore, DB temporal parcial, tareas inactivas, retención y restauración real |
| Permisos | rol, depósito, compañía y acción administrativa |

## 11. Referencias de código

- platform/source-lock.json
- platform/mycompany-6.2.lock.json
- vendor/UPSTREAM_SOURCES.md
- vendor/mycompany/CHANGELOG.md
- vendor/mycompany/src/main/lsfusion/MyCompany.lsf
- vendor/mycompany/src/main/lsfusion/inventory/adjustments/
- vendor/mycompany/src/main/lsfusion/inventory/ledgers/
- vendor/mycompany/src/main/lsfusion/inventory/reporting/
- vendor/mycompany/src/main/lsfusion/sales/ledgers/
- vendor/mycompany/src/main/lsfusion/sales/orders/SalesOrderAPI.lsf
- vendor/mycompany/src/main/lsfusion/retail/
- vendor/mycompany/src/main/lsfusion/region/
- vendor/platform/server/src/main/lsfusion/system/Security.lsf
- vendor/platform/server/src/main/lsfusion/utils/Backup.lsf
- vendor/platform/server/src/main/lsfusion/system/Scheduler.lsf
- vendor/platform/server/src/main/java/lsfusion/server/data/sql/adapter/PostgreDataAdapter.java

Documentación pública de apoyo:
- lsFusion 6.x Modules: https://docs.lsfusion.org/v6/Modules/
- lsFusion 6.x Extensions: https://docs.lsfusion.org/v6/Extensions/
- lsFusion 6.x Action extension: https://docs.lsfusion.org/v6/How-to_Action_extension/
- lsFusion 6.x Security policy: https://docs.lsfusion.org/v6/Security_policy/
- lsFusion 6.x Scheduler: https://docs.lsfusion.org/v6/Scheduler/
- lsFusion 6.x EXTERNAL: https://docs.lsfusion.org/v6/Access_to_an_external_system_EXTERNAL/
- MyCompany portal v6: https://mycompany-docs.lsfusion.org/v6/

**Límite documental:** el portal MyCompany /v6/ se identifica como documentación 6.0. Para afirmar comportamiento exacto de 6.2 prevalecen CHANGELOG.md y las fuentes vendorizadas fijadas por Rubrova.
