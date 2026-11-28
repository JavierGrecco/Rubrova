# Índice integral y rutas obligatorias de conocimiento — MyCompany 6.2 / lsFusion 6.2

**Archivo:** `docs/platform-audit/README.md`.

**Este es el punto de entrada obligatorio para cualquier integrante, desarrollador o agente que trabaje en Rubrova.** Su propósito es localizar toda la investigación existente, indicar el orden de lectura según la tarea y conectar los mapas de dominio con los documentos de arquitectura, producto, seguridad, runtime y reutilización. No alcanza con abrir un único mapa y asumir que la funcionalidad está aislada.

**Estado del catálogo documental del repositorio:** el árbol recursivo de `main` registra **1.113 archivos Markdown** en total (corte de esta revisión, árbol sin truncar):
- **75 documentos mantenidos por Rubrova fuera de `vendor/`**: los **71 documentos Markdown en `docs/`** (54 generales + 17 de `platform-audit/`), más `README.md`, `AGENTS.md`, `.github/pull_request_template.md` y `patches/lsfusion/README.md`.
- **1.038 archivos Markdown dentro de `vendor/`**: 1.031 páginas de documentación upstream incluidas en las cinco raíces que indexa `audit-source-docs.mjs` (347 MyCompany + 684 lsFusion), más 7 README/CHANGELOG/guías de soporte del snapshot.

El catálogo de documentos mantenidos por Rubrova está enlazado en este archivo; las 1.031 páginas upstream se enumeran por ruta, idioma, título y encabezados en el registro generado `rubrova-source-document-catalog`. Los siete Markdown adicionales del snapshot se enumeran expresamente en la sección 9. Los archivos binarios/imagenes upstream también quedan listados en el catálogo generado, pero ni el índice ni el registro afirman que cada página o imagen haya sido leída funcionalmente.

El test `scripts/platform/test-platform-map-entry.mjs` comprueba que los **75 Markdown mantenidos por Rubrova fuera de vendor/** estén incluidos en el índice y que los siete documentos auxiliares del snapshot no queden omitidos. `audit-source-docs.mjs` vuelve a generar el índice completo de páginas upstream desde los cinco directorios fijados. Si se incorpora un documento, fuente, idioma o recurso nuevo, debe clasificarse y enlazarse antes de pasar la prevalidación.

**Persistencia de los registros generados:** GitHub Actions publica `rubrova-lsf-source-catalog` y `rubrova-source-document-catalog` como artefactos con retención de 30 días. No son archivos permanentes de Git ni reemplazan este índice. Para conservar una copia consultable de los registros en el equipo de trabajo, ejecutar desde la raíz:

```bash
mkdir -p /tmp/rubrova-platform-map
RUBROVA_PREFLIGHT_OUTPUT_DIR=/tmp/rubrova-platform-map bash scripts/platform/local-preflight.sh --platform
```

Quedan allí `lsfusion-source-catalog.json`, `lsfusion-module-register.md`, `source-document-catalog.json` y `source-document-register.md`. El preflight borra su carpeta temporal predeterminada cuando no se especifica `RUBROVA_PREFLIGHT_OUTPUT_DIR`. El código de ambos generadores y sus pruebas sí permanece versionado. Ante una actualización de los locks, regenerar y revisar los registros antes de aprobar el nuevo snapshot.

**Estado del relevamiento técnico:** **EN CURSO / puerta 9.7 ABIERTA.** El catálogo documental exhaustivo no significa que se hayan leído y conciliado funcionalmente todos los módulos, páginas fuente, herramientas o capacidades. Los 800 módulos MyCompany están inventariados estructuralmente, no todos tienen ficha funcional completa ni pruebas de runtime. No se debe declarar completo el mapeo de MyCompany/lsFusion.

## 1. Autoridad, precedencia y alcance

- `docs/ENGINEERING_MASTER.md` es la fuente de verdad vigente para estado, evidencia, contratos, decisiones, riesgos y roadmap.
- Este índice es el mapa de navegación y cobertura documental. No crea una segunda fuente de decisiones.
- Los dossiers de `docs/platform-audit/` contienen análisis de fuente por dominio. Sus estados parciales se deben conservar; no elevarlos a aceptados por estar enlazados.
- Los documentos de producto especifican necesidades y comportamiento esperado. No prueban por sí solos que MyCompany/lsFusion lo implemente.
- `vendor/mycompany/` y `vendor/platform/` contienen los snapshots concretos. Siempre contrastar el documento con los commits de `platform/source-lock.json`.
- Las decisiones de reutilización se hacen sobre la versión fijada, no sobre documentación de otra versión ni sobre el nombre de un módulo.

**Regla fundamental:** antes de crear un equivalente, hay que buscar primero la capacidad en MyCompany, en las utilidades compartidas, en módulos fuera de la composición y en lsFusion; después seguir sus relaciones y demostrar qué brecha queda. No conocer una función no significa que no exista.

## 2. Orden recomendado de lectura

### 2.1 Incorporación de una persona nueva

1. [README principal](../../README.md): propósito, estado actual, tecnología y enlaces de entrada.
2. [AGENTS.md](../../AGENTS.md): instrucciones obligatorias para asistentes y agentes.
3. Este índice: entender dónde está cada parte del conocimiento y qué secuencia seguir.
4. [Manual técnico canónico](../ENGINEERING_MASTER.md): secciones vigentes 1–11 primero; en especial cómo se mantiene la fuente de verdad, estado de `main`, contratos, decisiones, evidencias, sección 9 y puerta 9.7.
5. [Arquitectura](../ARCHITECTURE.md), [composición de módulos](../MODULE_COMPOSITION.md), [inicio de implementación](../IMPLEMENTATION_START.md) y [procedencia/fork](../SOURCE_OWNERSHIP_AND_OFFLINE_RUNTIME.md).
6. [Forma de trabajo](../WORKFLOW.md): procedimiento de cambios, pruebas, revisión e integración.
7. Elegir la ruta funcional de la sección 4. No es necesario leer de punta a punta los 71 documentos para cada tarea; sí es obligatorio consultar el recorrido relevante y los documentos relacionados que indique.

### 2.2 Antes de implementar cualquier capacidad

```text
Necesidad / caso de uso
        |
        v
Documento de producto y criterio de aceptación
        |
        v
Índice de mapeo + dossier MyCompany del dominio
        |
        v
Dossiers relacionados (datos maestros, ledgers, utilidades, etc.)
        |
        v
Mapa de capacidades lsFusion + catálogo estructural de fuentes
        |
        v
Código 6.2: REQUIRE, extensiones, formularios, acciones, eventos,
restricciones, permisos, APIs, estados, ledgers e informes
        |
        v
Decisión explícita: reutilizar / extender / adaptar / crear /
parchear upstream / dependencia externa
        |
        v
Pruebas de runtime + conciliación + seguridad + recuperación
        |
        v
Actualizar dossier + este índice si cambia la cobertura +
ENGINEERING_MASTER + tests + roadmap
```

Nunca saltar desde el requisito directamente a una implementación propia. No alcanza con hallar un archivo por nombre, una referencia documental o un módulo en `REQUIRE`.

## 3. Cobertura de fuentes y números que se deben interpretar correctamente

### 3.1 MyCompany 6.2

- Snapshot: `lsfusion-solutions/mycompany`, commit `d21ca6978717b98b6300d90267f9767db7414008`.
- **800 módulos LSF** identificados estructuralmente.
- Cierre desde `RubrovaCustom`: **719 módulos** (688 MyCompany, 24 plataforma lsFusion y 7 extensiones Rubrova).
- Fuera del cierre: **112 módulos MyCompany** (96 regionales y 16 no regionales), más sus dependencias y recursos por revisar.
- Documentación upstream: **347 páginas Markdown** (112 inglés, 121 polaco, 114 ruso). El índice automatizado registra rutas/idiomas/títulos/encabezados; no demuestra lectura y asociación funcional completa. No hay bundle de documentación upstream en español.

### 3.2 lsFusion 6.2

- Snapshot: `lsfusion/platform`, commit `dd4dbe5bf9b136e73e18fe25d741253929324350`.
- **49 módulos LSF**, **3.330 archivos Java**, cuatro módulos Maven principales (`api`, `desktop-client`, `server`, `web-client`).
- Documentación upstream: **684 páginas Markdown** (342 inglés y 342 ruso) y **178 imágenes**.
- Hay páginas sin encabezados estructurados y referencias documentales a 6.1 dentro del snapshot 6.2 que deben contrastarse.

### 3.3 Lo que los conteos no significan

Los conteos por dominio se solapan. Un mismo módulo puede extender otros dominios o vivir en carpetas transversales; no sumar cantidades por dossier para obtener un total. Los registros automáticos detectan archivos, dependencias y declaraciones; no sustituyen la lectura semántica, ni certifican pantallas, permisos, carga, ejecución o conciliación.

### 3.4 Niveles de evidencia

| Nivel | Significado |
|---|---|
| Inventariado | Se conoce nombre, ruta, tipo y dominio inicial |
| Documentado | Se encontró una descripción o procedimiento |
| Fuente revisada | Se siguió implementación, dependencias y efectos |
| Composición resuelta | Se conoce si entra por `REQUIRE`/extensión |
| Cargado | Se confirmó en el runtime y configuración concretos |
| Verificado | Se ejecutó operación y se conservó evidencia |
| Conciliado | Documentos, estados, ledgers, reportes y efectos coinciden |
| Aceptado | Pruebas repetibles cubren permisos, excepciones y recuperación |

No convertir un nivel en otro por inferencia.

## 4. Rutas de lectura por tipo de trabajo

### 4.0 Integración por módulo exacto — ruta obligatoria

Cuando una tarea nombra un módulo o archivo LSF concreto, la lectura debe empezar por el **nombre declarado en `MODULE`**, no sólo por el dominio:

1. Abrir el [directorio de integración por módulo](MYCOMPANY_6_2_MODULE_INTEGRATION_DIRECTORY.md) (`docs/platform-audit/MYCOMPANY_6_2_MODULE_INTEGRATION_DIRECTORY.md`). Contiene rutas rápidas para los módulos centrales de cada circuito, sección exacta del dossier y relaciones que deben leerse antes de modificar.
2. Para cualquier módulo que no figure en la tabla manual, ejecutar `node scripts/platform/module-integration-route.mjs --module NombreExacto`. También acepta la ruta o el nombre exacto del archivo `.lsf`. La salida muestra `MODULE`, ruta, namespace, estado en `RubrovaCustom`, `REQUIRE` directos y consumidores directos, además del dossier y lecturas transversales.
3. Abrir la [plantilla obligatoria de ficha de integración](MODULE_INTEGRATION_PASSPORT_TEMPLATE.md) (`docs/platform-audit/MODULE_INTEGRATION_PASSPORT_TEMPLATE.md`) cuando no exista una ficha adecuada o el cambio descubra relaciones/contratos nuevos. No completar huecos con suposiciones.
4. Seguir por separado el grafo de dependencias de código (`REQUIRE`) y las relaciones de negocio (documentos, estados, reservas, ledgers, pagos, costos y reportes). La herramienta informa dependencias directas; el dossier y la fuente deben explicar la relación funcional.
5. Verificar si el módulo está dentro del cierre desde `RubrovaCustom`. Un módulo encontrado en `vendor/` puede estar fuera de composición y no debe asumirse cargado ni habilitado.

| Necesidad de integración | Primera ficha/dossier | Siguientes lecturas obligatorias |
|---|---|---|
| Ledger, documento o movimiento de inventario | [Directorio por módulo](MYCOMPANY_6_2_MODULE_INTEGRATION_DIRECTORY.md), luego `InvLedger`, `ResLedger`, `CostLedger`, `Receipt`, `Shipment`, `Adjustment` o `Scrap` según el cambio | Inventory/Ledger → Master Data → Purchase → Sales → Invoicing → Utilities → lsFusion |
| Pedido de venta, precio o despacho derivado | Directorio por módulo, luego `SalesOrder`, `SalesOrderShipment`, `SalesOrderInvoice` o `SalesOrderManufacturing` | Sales/Pricing → Inventory → Invoicing → Purchase/Manufacturing → Master Data |
| Pedido de compra, recepción o reposición | Directorio por módulo, luego `PurchaseOrder`, `PurchaseOrderReceipt`, `PurchaseOrderBill` o `PurchaseOrderShipmentAuto` | Purchase/Replenishment → Inventory → Invoicing → Master Data → Manufacturing |
| Factura, deuda, cobro, pago o cuenta | Directorio por módulo, luego `Invoice`, `Bill`, `Debt`, `IncomingPayment`, `OutgoingPayment` o `Payment` | Invoicing/Ledgers → Sales/Purchase/Retail → Inventory/Returns → Accounting Interoperability |
| Caja, turno, pago mixto o devolución POS | Directorio por módulo, luego `Pos`, `PosDashboardPayment`, `PosDashboardReturn`, `Session`, `SessionInvoice` o `SessionPayment` | Retail/POS → Sales → Invoicing/Payments → Inventory → Terminales/identidad/seguridad |
| Producto, socio, empresa, empleado, unidad o SKU | Directorio por módulo, luego `Item`, `Product`, `Partner`, `Company`, `Employee` o `ProductSku` | Master Data → todos los documentos consumidores → Utilities |
| BOM, orden de fabricación u operación | Directorio por módulo, luego `Bom`, `ManufacturingOrder`, `WorkCenter` o `WorkOrder` | Manufacturing → Sales → Purchase → Inventory/CostLedger → Master Data |
| CRM, asistencia, flota o proyecto | Directorio por módulo y dossier específico | Master Data → Sales/Invoicing/Projects/HR/Fleet → Utilities → Security |


Estas secuencias son deliberadas. El documento de la primera columna es el disparador; los pasos siguientes son dependencias de lectura y revisión, no enlaces decorativos.

### 4.1 POS, caja y venta minorista

`POS_REQUIREMENTS` → mapa Retail/POS/Sesiones → Ventas y precios → Facturación y pagos → Inventario y reservas → Datos maestros → Utilidades compartidas → capacidades lsFusion.

Complementar obligatoriamente con:
- `CHECKOUT_AND_PAYMENT_TERMINALS.md` y `PAYMENT_TERMINAL_INTEGRATION_ARCHITECTURE.md` al modificar cobros, postnet, QR o estados de terminal.
- `PAYMENT_IDENTITY_AND_RECONCILIATION.md` cuando se vincule pagador, titular de tarjeta/cuenta o cliente comercial.
- `SECURITY_POSTURE.md`, `INTEGRATION_RESILIENCE_AND_ERROR_HANDLING.md` y `OPERATIONAL_RESILIENCE_AND_RECOVERY.md` para pagos, reintentos, timeout, reversos o recuperación.
- `ENGINEERING_MASTER.md` secciones 5.2–5.5 y REP correspondiente para semántica ya investigada de venta, devolución, caja e inventario.

### 4.2 Venta mayorista, pedidos y distribución

`WHOLESALE_AND_DISTRIBUTION.md` → mapa Sales/Pricing/Ledger → Inventory/Ledger → Invoicing/Ledger → Master Data → Utilities.

Agregar `CHANNELS_AND_INTEGRATIONS.md` y `ARGENTINA_LOGISTICS_INTEGRATION.md` para canal, fulfillment, transporte y tracking. Revisar `ACCOUNTING_INTEROPERABILITY.md` cuando los documentos o saldos se compartan con un sistema contable externo.

### 4.3 Compras y proveedores

`MYCOMPANY_6_2_PURCHASE_REPLENISHMENT_MAP.md` → Inventory/Ledger → Invoicing/Ledger → Master Data → Utilities.

Para demanda, proyección o sugerencias de reposición, continuar con `PROJECTED_STOCK_AND_REPLENISHMENT.md`, `DATA_CAPTURE_AND_ANALYTICAL_FOUNDATION.md`, `DEMAND_AND_MARGIN_INTELLIGENCE.md` y `BUSINESS_INTELLIGENCE.md`. Para fabricación, sumar el dominio Manufacturing del mapa funcional y el perfil sectorial pertinente.

### 4.4 Inventario, stock, depósitos, conteos y costos

`MYCOMPANY_6_2_INVENTORY_LEDGER_MAP.md` es la entrada principal. Seguir en este orden:

1. `MYCOMPANY_6_2_MASTERDATA_RELATIONSHIPS_MAP.md`: producto/servicio, unidad, pack, variante, barcode, categoría, depósito y socio.
2. `MYCOMPANY_6_2_PURCHASE_REPLENISHMENT_MAP.md`: origen de recepciones, compras, compromisos y entradas esperadas.
3. `MYCOMPANY_6_2_SALES_PRICING_LEDGER_MAP.md`: origen de pedidos, reservas, despachos y salidas.
4. `MYCOMPANY_6_2_INVOICING_LEDGER_MAP.md`: factura, devolución, deuda, pago y costos documentales.
5. `MYCOMPANY_6_2_UTILITY_MODULES.md`: documentos, estados, historial, numeración, archivos e importación.
6. `PROJECTED_STOCK_AND_REPLENISHMENT.md`, `FOOD_PRODUCTION_AND_TRACEABILITY.md`, `WHOLESALE_AND_DISTRIBUTION.md` o BI según el caso.

No modificar un saldo aislado antes de conocer qué documento y ledger lo producen, qué otros dominios lo consumen y qué significa cada reserva/estado/costo.

### 4.5 Fabricación, gastronomía y trazabilidad alimentaria

`FOOD_PRODUCTION_AND_TRACEABILITY.md` → sección Manufacturing del mapa funcional general → Inventory/Ledger → Purchase/Replenishment → Master Data → Invoicing/Ledger → Utilities.

Comprobar BOM/recetas, consumos, producción, coproductos, lotes, vencimientos, merma, costo, ubicación y venta. No crear un segundo inventario ni presentar la especificación alimentaria como una implementación ya aceptada.

### 4.6 CRM y clientes

`MYCOMPANY_6_2_CRM_LEADS_MAP.md` → Master Data → Sales/Pricing → Invoicing/Ledger → Utilities.

Sumar `CUSTOMER_360_AND_INTELLIGENCE.md`, `DATA_CAPTURE_AND_ANALYTICAL_FOUNDATION.md` y `PAYMENT_IDENTITY_AND_RECONCILIATION.md` cuando se trate de identidad, historial o perfil consolidado. No fusionar automáticamente al comprador, pagador, titular del instrumento y cliente.

### 4.7 RR. HH., asistencia, proyectos, tareas y tiempos

Para personal: HR/Attendance/Payroll → Project Management/Integrations → Master Data → Invoicing/Ledger → Utilities.

Para proyectos/tiempos: Project Management/Integrations → HR/Attendance/Payroll → Sales, Purchase, Inventory, Manufacturing e Invoicing según las conexiones del caso. Seguir horas, aprobaciones, asistencia, partes de horas y costos hasta su documento/ledger consumidor. Revisar privacidad, geolocalización, roles y requisitos laborales argentinos.

### 4.8 Flota, vehículos y mantenimiento

Fleet/Vehicle Costs → Master Data → Project Management/Integrations → Invoicing/Ledger → Utilities.

Comprobar vehículo, conductor, asignación, odómetro, servicio, contrato, gasto y documento financiero. No asumir alertas automáticas ni planificación de mantenimiento cuando el dossier sólo haya identificado campos/relaciones.

### 4.9 Facturación, impuestos, deuda, pagos y contabilidad argentina

Invoicing/Ledger → Sales/Pricing y Purchase/Replenishment → Master Data → Retail/POS (cuando aplica) → Regional Modules → `ACCOUNTING_INTEROPERABILITY.md` → `TRYTON_ARGENTINA_8_0_LOCK.md` (contraste separado).

Sumar los documentos de checkout/terminal y de identidad/conciliación si hay adquirente, banco o billetera. Ningún patrón regional extranjero constituye adecuación argentina por sí solo; ARCA, impuestos, comprobantes, padrones y conciliación deben tener pruebas y evidencia separadas.

### 4.10 APIs, integraciones externas, módulos o servicios nuevos

LSFusion Capability Map → MyCompany Functional Map → Utility Modules → Domain dossiers → Architecture → Module Composition → Integration Resilience → Security Posture → documento del proveedor/capacidad.

Antes de agregar Laravel, JavaScript, Python, un framework, broker, base, microservicio o biblioteca, revisar la investigación de reutilización y justificar qué capacidad concreta falta en MyCompany/lsFusion y por qué la extensión nativa no basta.

### 4.11 Runtime, despliegue, migraciones, actualización o backup

Source Ownership and Offline Runtime → MyCompany Runtime Install → Runtime Modes and Local Control → Platform Lab Setup / OS support → Backup and Migration → Operational Resilience → Security Posture → Upstream-vs-Rubrova Test Diagnosis → Workflow.

Ante una actualización upstream, regenerar catálogos, comparar snapshots y parches, comprobar dependencias y ejecutar build, smoke, contratos, migración, restore y operación offline antes de cambiar locks.

### 4.12 Reportes, rentabilidad, pronóstico e inteligencia

Inventory, Sales y Invoicing ledgers → Data Capture and Analytical Foundation → Demand and Margin Intelligence → Business Intelligence → Business Unit Profitability / Customer 360 según dimensión.

El sistema transaccional sigue siendo dueño de ventas, pagos, caja, compras, stock y costos. La analítica consume hechos conciliados; no escribe en ledgers ni convierte estimaciones en órdenes.

## 5. Dossiers fuente de MyCompany y lsFusion: qué contiene cada uno y a dónde conduce

| Dossier | Alcance y limitación actual | Seguir leyendo / dependencias |
|---|---|---|
| [MYCOMPANY_6_2_FUNCTIONAL_MAP](../platform-audit/MYCOMPANY_6_2_FUNCTIONAL_MAP.md) · `docs/platform-audit/MYCOMPANY_6_2_FUNCTIONAL_MAP.md` | Mapa funcional general, composición, clasificación de dominios y cobertura de los 800 módulos. | Todos los dominios; Manufacturing; módulos fuera del cierre; 16 módulos no regionales y composición de RubrovaCustom. |
| [MYCOMPANY_6_2_RETAIL_POS_SESSIONS_MAP](../platform-audit/MYCOMPANY_6_2_RETAIL_POS_SESSIONS_MAP.md) · `docs/platform-audit/MYCOMPANY_6_2_RETAIL_POS_SESSIONS_MAP.md` | POS, caja, sesiones, medios de pago, devoluciones, picking y turnos. | Sales/Pricing, Invoicing/Ledger, Inventory/Ledger, Master Data, Utilities y capacidades lsFusion; terminales y checkout cuando aplique. |
| [MYCOMPANY_6_2_SALES_PRICING_LEDGER_MAP](../platform-audit/MYCOMPANY_6_2_SALES_PRICING_LEDGER_MAP.md) · `docs/platform-audit/MYCOMPANY_6_2_SALES_PRICING_LEDGER_MAP.md` | Ventas, pedidos, precios, descuentos, despacho, ledger comercial, costo y margen. | Retail/POS, Inventory/Ledger, Invoicing/Ledger, CRM, Master Data y Utilities. |
| [MYCOMPANY_6_2_INVOICING_LEDGER_MAP](../platform-audit/MYCOMPANY_6_2_INVOICING_LEDGER_MAP.md) · `docs/platform-audit/MYCOMPANY_6_2_INVOICING_LEDGER_MAP.md` | Facturas, notas, deuda, imputaciones, pagos, cuentas, impuestos y ledger. | Sales, Purchase, Retail/POS, Inventory, Master Data, Accounting Interoperability y Payments. |
| [MYCOMPANY_6_2_INVENTORY_LEDGER_MAP](../platform-audit/MYCOMPANY_6_2_INVENTORY_LEDGER_MAP.md) · `docs/platform-audit/MYCOMPANY_6_2_INVENTORY_LEDGER_MAP.md` | Inventario físico, reservas, disponible, recepción, despacho, transferencias, ajustes y costos. | Master Data, Purchase, Sales, Invoicing, Utilities, Projected Stock, Food Traceability y BI. |
| [MYCOMPANY_6_2_PURCHASE_REPLENISHMENT_MAP](../platform-audit/MYCOMPANY_6_2_PURCHASE_REPLENISHMENT_MAP.md) · `docs/platform-audit/MYCOMPANY_6_2_PURCHASE_REPLENISHMENT_MAP.md` | Compras, proveedores, pedidos, recepción, políticas de facturación y reposición. | Inventory/Ledger, Invoicing/Ledger, Master Data, Manufacturing, Projected Stock y Demand Intelligence. |
| [MYCOMPANY_6_2_MASTERDATA_RELATIONSHIPS_MAP](../platform-audit/MYCOMPANY_6_2_MASTERDATA_RELATIONSHIPS_MAP.md) · `docs/platform-audit/MYCOMPANY_6_2_MASTERDATA_RELATIONSHIPS_MAP.md` | Datos maestros, socios, productos, unidades, variantes, códigos, contratos y relaciones. | Todos los dossiers de negocio; es dependencia común para productos, socios, monedas, unidades, códigos, categorías y contratos. |
| [MYCOMPANY_6_2_CRM_LEADS_MAP](../platform-audit/MYCOMPANY_6_2_CRM_LEADS_MAP.md) · `docs/platform-audit/MYCOMPANY_6_2_CRM_LEADS_MAP.md` | Leads, estados, Kanban, comunicaciones, campañas y conversión a documentos. | Master Data, Sales/Pricing, Invoicing/Ledger, Project Management y Customer 360. |
| [MYCOMPANY_6_2_HR_ATTENDANCE_PAYROLL_MAP](../platform-audit/MYCOMPANY_6_2_HR_ATTENDANCE_PAYROLL_MAP.md) · `docs/platform-audit/MYCOMPANY_6_2_HR_ATTENDANCE_PAYROLL_MAP.md` | Reclutamiento, asistencia, turnos, recibos, deuda y pagos de haberes. | Project Management/Integrations, Master Data, Invoicing/Ledger, seguridad, privacidad y reglas laborales. |
| [MYCOMPANY_6_2_PROJECT_MANAGEMENT_INTEGRATIONS_MAP](../platform-audit/MYCOMPANY_6_2_PROJECT_MANAGEMENT_INTEGRATIONS_MAP.md) · `docs/platform-audit/MYCOMPANY_6_2_PROJECT_MANAGEMENT_INTEGRATIONS_MAP.md` | Proyectos, tareas, equipos, workflow, tiempos y conexiones con otros dominios. | HR, Fleet, Inventory, Purchase, Sales, Invoicing y Manufacturing. |
| [MYCOMPANY_6_2_FLEET_VEHICLE_COSTS_MAP](../platform-audit/MYCOMPANY_6_2_FLEET_VEHICLE_COSTS_MAP.md) · `docs/platform-audit/MYCOMPANY_6_2_FLEET_VEHICLE_COSTS_MAP.md` | Vehículos, conductores, asignaciones, odómetro, servicios, contratos y gastos. | Master Data, Project Management e Invoicing/Ledger; confirmar automatizaciones en runtime. |
| [MYCOMPANY_6_2_UTILITY_MODULES](../platform-audit/MYCOMPANY_6_2_UTILITY_MODULES.md) · `docs/platform-audit/MYCOMPANY_6_2_UTILITY_MODULES.md` | Utilidades compartidas, documentos, historial, archivos, correo, numeración, geo, barcode y criptografía. | Es transversal: consultar en cualquier cambio que use documentos, historial, archivos, correo, numeración, geo, barcode, crypto o macros compartidas. |
| [MYCOMPANY_6_2_REGIONAL_MODULES](../platform-audit/MYCOMPANY_6_2_REGIONAL_MODULES.md) · `docs/platform-audit/MYCOMPANY_6_2_REGIONAL_MODULES.md` | Los 96 módulos regionales de Bulgaria, Polonia y Rusia: inventario inicial y auditoría pendiente. | MyCompany Functional Map, Invoicing, CRM, Retail, Security y Accounting Interoperability; no asumir adecuación argentina. |
| [LSFUSION_6_2_CAPABILITY_MAP](../platform-audit/LSFUSION_6_2_CAPABILITY_MAP.md) · `docs/platform-audit/LSFUSION_6_2_CAPABILITY_MAP.md` | Capacidades de lenguaje, ejecución, clientes, persistencia, APIs, seguridad y herramientas de lsFusion. | Module Composition, Source Ownership, Utility Modules y dossier MyCompany del dominio que se esté cambiando. |
| [MYCOMPANY_6_2_MODULE_INTEGRATION_DIRECTORY](../platform-audit/MYCOMPANY_6_2_MODULE_INTEGRATION_DIRECTORY.md) · `docs/platform-audit/MYCOMPANY_6_2_MODULE_INTEGRATION_DIRECTORY.md` | Directorio de integración por nombre exacto para módulos centrales; fuente LSF, sección de lectura, dependencias y relaciones | Leer primero al integrar/modificar un módulo concreto; para los restantes usar el CLI de consulta. |
| [MODULE_INTEGRATION_PASSPORT_TEMPLATE](../platform-audit/MODULE_INTEGRATION_PASSPORT_TEMPLATE.md) · `docs/platform-audit/MODULE_INTEGRATION_PASSPORT_TEMPLATE.md` | Plantilla de responsabilidad, entidades, casos de uso, contratos, estados, ledgers, permisos, excepciones, pruebas y decisión reuse-first | Completar una ficha por módulo o grupo cohesivo cuando el dossier de dominio no sea suficiente. |

### 5.1 Lectura de los estados de estos dossiers

La tabla no indica que estén completos. Cada archivo declara su estado y pendientes en su encabezado y sección final. En particular:
- Inventario, compras, ventas, flota, regionales, CRM, RR. HH. y proyectos tienen apartados de lectura parcial o pruebas pendientes.
- Datos maestros y utilidades tienen revisión inicial de fuentes, pero faltan pruebas de runtime, extensiones o validación argentina.
- El mapa de capacidad lsFusion mantiene abierta su puerta de relevamiento.
- El mapa funcional general es una entrada y panorama de dominios, no reemplaza el análisis detallado por módulo/circuito.

Los documentos de dominio se actualizan cuando cambia el conocimiento, no sólo cuando se agrega una función. Un resultado negativo ("esta capacidad no está en el módulo", "la acción no está habilitada", "el módulo requiere un proveedor") también se registra porque evita búsquedas repetidas y desarrollos duplicados.

## 6. Mapa de relaciones entre los documentos de dominio

Las relaciones siguientes son el recorrido mínimo de dependencias que debe seguir quien investiga. Un dominio puede tener dependencias adicionales: el dossier debe nombrarlas y ampliar el grafo cuando se descubran.

| Dominio de entrada | Relaciones que se deben seguir |
|---|---|
| Retail / POS | Sales → Invoicing/Payments → Inventory → Master Data → Utilities → lsFusion |
| Sales / Pricing | CRM → Master Data → Inventory/Shipments → Invoicing/Debt → Utilities |
| Inventory / Ledgers | Master Data → Purchase/Receipts → Sales/Shipments → Invoicing/Returns → Costing → Reports |
| Purchase / Replenishment | Master Data → Inventory/Reservations → Invoicing/Supplier debt → Manufacturing → Forecast |
| Invoicing / Payments | Sales + Purchase + Retail → Debt/Payment ledgers → Inventory/Returns/Costs → Accounting integration |
| Manufacturing | Master Data/BOM → Purchase → Inventory/Consumption → Costing → Invoicing/Sales |
| CRM / Leads | Partner/Contact master data → Sales → Invoicing → Communication/Utilities |
| HR / Payroll | Employee/master data → Attendance/Projects → Payslip/Payment → Costs/Reports |
| Project Management | Project/Team/Task → HR/Time entries → Inventory/Purchase/Sales/Manufacturing/Invoicing |
| Fleet | Partner/Vehicle/Employee master data → Assignment/Service → Expense/Bill → Projects |
| Utilities | Proveen funciones comunes; no son dominio final y deben analizarse desde cada consumidor real |
| Regional modules | Módulos base + integración específica + proveedor/servicio + seguridad + normativa local |

## 7. Registro exhaustivo de los otros documentos de `docs/`

Este catálogo complementa los 14 dossiers anteriores. Incluye **todos** los documentos Markdown generales existentes en `docs/`, incluso los que son requisitos de producto o investigación y no describen directamente fuente upstream. Su inclusión permite conocer su finalidad y evita que las decisiones de arquitectura o de dominio se tomen ignorando requisitos ya escritos.

### Núcleo del proyecto, arquitectura y forma de trabajo

| Documento | Para qué sirve y cuándo consultarlo |
|---|---|
| [ARCHITECTURE](../ARCHITECTURE.md) · `docs/ARCHITECTURE.md` | Arquitectura, límites entre núcleo integrado y servicios, reuse-first y principios de autoridad de datos. |
| [MODULE COMPOSITION](../MODULE_COMPOSITION.md) · `docs/MODULE_COMPOSITION.md` | Composición de módulos, contratos, ownership de datos y formas válidas de integración. |
| [ENGINEERING MASTER](../ENGINEERING_MASTER.md) · `docs/ENGINEERING_MASTER.md` | Fuente única vigente de decisiones, estado, evidencia, contratos, investigaciones y roadmap; contiene anexos históricos A–K. |
| [IMPLEMENTATION START](../IMPLEMENTATION_START.md) · `docs/IMPLEMENTATION_START.md` | Decisión de adopción MyCompany/lsFusion, módulos fuente iniciales, composición y primeros recorridos. |
| [SOURCE OWNERSHIP AND OFFLINE RUNTIME](../SOURCE_OWNERSHIP_AND_OFFLINE_RUNTIME.md) · `docs/SOURCE_OWNERSHIP_AND_OFFLINE_RUNTIME.md` | Procedencia, commits upstream, licencias, vendorización, modificaciones y operación sin Internet. |
| [WORKFLOW](../WORKFLOW.md) · `docs/WORKFLOW.md` | Procedimiento de cambios, reuse-first, validaciones e integración sobre main. |
| [BRANCHING STRATEGY](../BRANCHING_STRATEGY.md) · `docs/BRANCHING_STRATEGY.md` | Gobierno de ramas, consolidación y limpieza de la historia de trabajo. |

### Investigación, selección y reutilización de componentes

| Documento | Para qué sirve y cuándo consultarlo |
|---|---|
| [CODE REUSE CATALOG](../CODE_REUSE_CATALOG.md) · `docs/CODE_REUSE_CATALOG.md` | Catálogo de proyectos, módulos, componentes, versiones, licencias, madurez y condiciones de uso. |
| [OPEN SOURCE STRATEGY](../OPEN_SOURCE_STRATEGY.md) · `docs/OPEN_SOURCE_STRATEGY.md` | Reglas de procedencia, licencia, dependencias, modificaciones y actualización de terceros. |
| [REUSE FIRST IMPLEMENTATION STRATEGY](../REUSE_FIRST_IMPLEMENTATION_STRATEGY.md) · `docs/REUSE_FIRST_IMPLEMENTATION_STRATEGY.md` | Orden de decisión: adoptar, extender, integrar, mantener fork o construir una brecha propia. |
| [REUSE COMPONENTS SHORTLIST](../REUSE_COMPONENTS_SHORTLIST.md) · `docs/REUSE_COMPONENTS_SHORTLIST.md` | Investigación de bibliotecas y herramientas concretas por capacidad; candidatos, límites y posibles usos. |
| [PLATFORM EVALUATION](../PLATFORM_EVALUATION.md) · `docs/PLATFORM_EVALUATION.md` | Comparación reproducible de suites POS+ERP y criterios de selección. |
| [PLATFORM LAB SETUP](../PLATFORM_LAB_SETUP.md) · `docs/PLATFORM_LAB_SETUP.md` | Preparación y protocolo de laboratorio para comparar plataformas con datos sintéticos. |
| [RESEARCH](../RESEARCH.md) · `docs/RESEARCH.md` | Fuentes y referencias de investigación técnica, estándares y proyectos. |
| [MODULAR COMPONENT RESEARCH](../MODULAR_COMPONENT_RESEARCH.md) · `docs/MODULAR_COMPONENT_RESEARCH.md` | Investigación de proyectos modulares, conectores, WMS, promociones y otros componentes. |
| [TOOLING AND REUSE RESEARCH 2026 11](../TOOLING_AND_REUSE_RESEARCH_2026_11.md) · `docs/TOOLING_AND_REUSE_RESEARCH_2026_11.md` | Investigación de herramientas técnicas, pruebas, observabilidad y reutilización de noviembre de 2026. |
| [S TECH EVALUATION](../S_TECH_EVALUATION.md) · `docs/S_TECH_EVALUATION.md` | Evaluación técnica complementaria y antecedentes de selección. |
| [TRYTON ARGENTINA 8 0 LOCK](../TRYTON_ARGENTINA_8_0_LOCK.md) · `docs/TRYTON_ARGENTINA_8_0_LOCK.md` | Repositorios, commits y versiones fijadas del conjunto argentino Tryton usado como contraste. |
| [COMPETITIVE MARKET REVIEW](../COMPETITIVE_MARKET_REVIEW.md) · `docs/COMPETITIVE_MARKET_REVIEW.md` | Comparación de plataformas y referencias del mercado; contexto, no prueba de integración. |
| [MARKET RESEARCH AND ADDITIONAL OPPORTUNITIES](../MARKET_RESEARCH_AND_ADDITIONAL_OPPORTUNITIES.md) · `docs/MARKET_RESEARCH_AND_ADDITIONAL_OPPORTUNITIES.md` | Oportunidades sectoriales y alternativas investigadas para futuras etapas. |

### Runtime, seguridad, calidad y continuidad

| Documento | Para qué sirve y cuándo consultarlo |
|---|---|
| [MYCOMPANY RUNTIME INSTALL](../MYCOMPANY_RUNTIME_INSTALL.md) · `docs/MYCOMPANY_RUNTIME_INSTALL.md` | Instalación, dependencias, compilación y operación del runtime MyCompany/lsFusion. |
| [RUNTIME MODES AND LOCAL CONTROL](../RUNTIME_MODES_AND_LOCAL_CONTROL.md) · `docs/RUNTIME_MODES_AND_LOCAL_CONTROL.md` | Modos de ejecución, control local, procesos, servicios y límites de operación. |
| [MACOS SUPPORT](../MACOS_SUPPORT.md) · `docs/MACOS_SUPPORT.md` | Compatibilidad y procedimientos de ejecución en macOS/Apple Silicon. |
| [BACKUP AND MIGRATION STRATEGY](../BACKUP_AND_MIGRATION_STRATEGY.md) · `docs/BACKUP_AND_MIGRATION_STRATEGY.md` | Estrategia de backup, migración, restore y protección de datos. |
| [OPERATIONAL RESILIENCE AND RECOVERY](../OPERATIONAL_RESILIENCE_AND_RECOVERY.md) · `docs/OPERATIONAL_RESILIENCE_AND_RECOVERY.md` | Continuidad, incidentes, recuperación, rollback y compensación de efectos. |
| [SECURITY AND AUDIT](../SECURITY_AND_AUDIT.md) · `docs/SECURITY_AND_AUDIT.md` | Requisitos transversales de identidad, acceso, auditoría, privacidad y seguridad. |
| [SECURITY POSTURE](../SECURITY_POSTURE.md) · `docs/SECURITY_POSTURE.md` | Estado de controles: verificados, diseñados y pendientes antes de producción. |
| [INTEGRATION RESILIENCE AND ERROR HANDLING](../INTEGRATION_RESILIENCE_AND_ERROR_HANDLING.md) · `docs/INTEGRATION_RESILIENCE_AND_ERROR_HANDLING.md` | Timeouts, reintentos, idempotencia, errores, aislamiento y recuperación de integraciones. |
| [DISTRIBUTED MODULAR ARCHITECTURE](../DISTRIBUTED_MODULAR_ARCHITECTURE.md) · `docs/DISTRIBUTED_MODULAR_ARCHITECTURE.md` | Límites de datos, contratos entre procesos, eventos y condiciones para separar servicios. |
| [UPSTREAM VS RUBROVA TEST DIAGNOSIS 2026 11 20](../UPSTREAM_VS_RUBROVA_TEST_DIAGNOSIS_2026_11_20.md) · `docs/UPSTREAM_VS_RUBROVA_TEST_DIAGNOSIS_2026_11_20.md` | Diagnóstico de regresiones y diferencias entre fuente upstream, modificaciones Rubrova y suites de prueba. |

### Producto, perfiles y requisitos funcionales

| Documento | Para qué sirve y cuándo consultarlo |
|---|---|
| [EXECUTIVE PRODUCT BRIEF](../EXECUTIVE_PRODUCT_BRIEF.md) · `docs/EXECUTIVE_PRODUCT_BRIEF.md` | Resumen del producto, usuarios, alcance, propuesta de valor y estado. |
| [PRODUCT VISION](../PRODUCT_VISION.md) · `docs/PRODUCT_VISION.md` | Visión y principios de producto. |
| [PRODUCT CAPABILITY MAP](../PRODUCT_CAPABILITY_MAP.md) · `docs/PRODUCT_CAPABILITY_MAP.md` | Mapa de capacidades objetivo de Rubrova por área y etapa. |
| [FUNCTIONAL SCOPE](../FUNCTIONAL_SCOPE.md) · `docs/FUNCTIONAL_SCOPE.md` | Alcance funcional general y documentación detallada vinculada. |
| [DOMAIN MODEL](../DOMAIN_MODEL.md) · `docs/DOMAIN_MODEL.md` | Entidades, estados, relaciones y límites conceptuales del dominio. |
| [POS REQUIREMENTS](../POS_REQUIREMENTS.md) · `docs/POS_REQUIREMENTS.md` | Requisitos del punto de venta; especifica comportamiento esperado, no aceptación de MyCompany. |
| [PYME NEEDS AND PRODUCT BACKLOG](../PYME_NEEDS_AND_PRODUCT_BACKLOG.md) · `docs/PYME_NEEDS_AND_PRODUCT_BACKLOG.md` | Necesidades de negocios pequeños/medianos y backlog funcional. |
| [BUSINESS LINES AND SEGMENTS](../BUSINESS_LINES_AND_SEGMENTS.md) · `docs/BUSINESS_LINES_AND_SEGMENTS.md` | Unidades de negocio, segmentos, canales y dimensiones de operación. |
| [SECTOR PROFILES](../SECTOR_PROFILES.md) · `docs/SECTOR_PROFILES.md` | Perfiles sectoriales y variantes de uso del núcleo común. |
| [WHOLESALE AND DISTRIBUTION](../WHOLESALE_AND_DISTRIBUTION.md) · `docs/WHOLESALE_AND_DISTRIBUTION.md` | Venta mayorista, condiciones B2B, picking, entregas parciales y distribución. |
| [B2B SERVICES AND CONTRACTS](../B2B_SERVICES_AND_CONTRACTS.md) · `docs/B2B_SERVICES_AND_CONTRACTS.md` | Servicios a empresas, contratos, ejecución, SLA, aceptación y facturación. |
| [FOOD PRODUCTION AND TRACEABILITY](../FOOD_PRODUCTION_AND_TRACEABILITY.md) · `docs/FOOD_PRODUCTION_AND_TRACEABILITY.md` | Elaboración gastronómica, recetas/BOM, lotes, vencimientos y trazabilidad; especificación, no flujo productivo aceptado. |
| [ARGENTINA LOGISTICS INTEGRATION](../ARGENTINA_LOGISTICS_INTEGRATION.md) · `docs/ARGENTINA_LOGISTICS_INTEGRATION.md` | Investigación de transportistas, cotización, etiquetas, despacho y tracking argentino. |
| [CHANNELS AND INTEGRATIONS](../CHANNELS_AND_INTEGRATIONS.md) · `docs/CHANNELS_AND_INTEGRATIONS.md` | Canales de origen/venta/cobro/entrega y relaciones omnicanal. |
| [CHECKOUT AND PAYMENT TERMINALS](../CHECKOUT_AND_PAYMENT_TERMINALS.md) · `docs/CHECKOUT_AND_PAYMENT_TERMINALS.md` | Checkout, caja y terminales; estados, flujo y límites de los adaptadores. |
| [PAYMENT IDENTITY AND RECONCILIATION](../PAYMENT_IDENTITY_AND_RECONCILIATION.md) · `docs/PAYMENT_IDENTITY_AND_RECONCILIATION.md` | Diferencia comprador, pagador, titular del instrumento y cliente; identidad y conciliación. |
| [PAYMENT TERMINAL INTEGRATION ARCHITECTURE](../PAYMENT_TERMINAL_INTEGRATION_ARCHITECTURE.md) · `docs/PAYMENT_TERMINAL_INTEGRATION_ARCHITECTURE.md` | Arquitectura y contratos de terminales/adquirentes, modos de integración y pruebas. |
| [ACCOUNTING INTEROPERABILITY](../ACCOUNTING_INTEROPERABILITY.md) · `docs/ACCOUNTING_INTEROPERABILITY.md` | Interoperabilidad contable/fiscal argentina, propietarios de documentos y proveedores evaluados. |

### Datos, inteligencia y planificación

| Documento | Para qué sirve y cuándo consultarlo |
|---|---|
| [DATA CAPTURE AND ANALYTICAL FOUNDATION](../DATA_CAPTURE_AND_ANALYTICAL_FOUNDATION.md) · `docs/DATA_CAPTURE_AND_ANALYTICAL_FOUNDATION.md` | Hechos, dimensiones, historial, trazabilidad y base analítica desde el origen transaccional. |
| [DEMAND AND MARGIN INTELLIGENCE](../DEMAND_AND_MARGIN_INTELLIGENCE.md) · `docs/DEMAND_AND_MARGIN_INTELLIGENCE.md` | Demanda, pronóstico, rentabilidad, marcas y recomendaciones; reglas de no escritura sobre ledgers. |
| [BUSINESS INTELLIGENCE](../BUSINESS_INTELLIGENCE.md) · `docs/BUSINESS_INTELLIGENCE.md` | Indicadores, cortes y reporting de gestión. |
| [BUSINESS UNIT PROFITABILITY](../BUSINESS_UNIT_PROFITABILITY.md) · `docs/BUSINESS_UNIT_PROFITABILITY.md` | Rentabilidad por unidad de negocio y reglas de distribución de costos. |
| [CUSTOMER 360 AND INTELLIGENCE](../CUSTOMER_360_AND_INTELLIGENCE.md) · `docs/CUSTOMER_360_AND_INTELLIGENCE.md` | Vista consolidada de cliente e inteligencia de relación, con límites de identidad y privacidad. |
| [PROJECTED STOCK AND REPLENISHMENT](../PROJECTED_STOCK_AND_REPLENISHMENT.md) · `docs/PROJECTED_STOCK_AND_REPLENISHMENT.md` | Stock proyectado, contrato de exportación nativa y planificador conservador; no genera órdenes. |

### 7.1 Recursos de soporte y fixtures bajo `docs/`

Además de los 71 Markdown, el directorio `docs/` contiene siete JSON y un SVG. El inventario actual suma **79 archivos**. Estos recursos no son texto auxiliar descartable: forman parte de los experimentos reproducibles, los contratos y la presentación del proyecto.

| Archivo | Qué contiene / para qué sirve | Leer junto con |
|---|---|---|
| [demand-monthly-history.json](../fixtures/demand-monthly-history.json) · `docs/fixtures/demand-monthly-history.json` | Benchmark sintético de demanda mensual 2022–2025, estacionalidad del hemisferio sur y backtesting walk-forward | [Demanda y margen](../DEMAND_AND_MARGIN_INTELLIGENCE.md), [BI](../BUSINESS_INTELLIGENCE.md) y los tests del motor de pronóstico |
| [stockout-censored-demand.json](../fixtures/stockout-censored-demand.json) · `docs/fixtures/stockout-censored-demand.json` | Escenario sintético de demanda censurada por quiebres de stock; separa ventas observadas de demanda latente usada sólo para evaluar | [Demanda y margen](../DEMAND_AND_MARGIN_INTELLIGENCE.md) y los tests del estimador de demanda censurada |
| [platform-evaluation.json](../fixtures/platform-evaluation.json) · `docs/fixtures/platform-evaluation.json` | Datos/escenarios comunes sintéticos para comparar plataformas POS+ERP bajo condiciones equivalentes | [Laboratorio de evaluación](../PLATFORM_LAB_SETUP.md), [Evaluación de plataformas](../PLATFORM_EVALUATION.md) y `scripts/evaluation/` |
| [mycompany-native-replenishment-export.json](../fixtures/mycompany-native-replenishment-export.json) · `docs/fixtures/mycompany-native-replenishment-export.json` | Ejemplo sintético del contrato JSON de exportación nativa MyCompany 6.2, sólo lectura, con conteos, ledgers y semánticas explícitas | [Stock proyectado y reposición](../PROJECTED_STOCK_AND_REPLENISHMENT.md), [compras](MYCOMPANY_6_2_PURCHASE_REPLENISHMENT_MAP.md) e [inventario](MYCOMPANY_6_2_INVENTORY_LEDGER_MAP.md) |
| [mycompany-replenishment-snapshot.json](../fixtures/mycompany-replenishment-snapshot.json) · `docs/fixtures/mycompany-replenishment-snapshot.json` | Snapshot normalizado de reposición con inventario, reservas, recepciones y entradas de planificación | [Stock proyectado y reposición](../PROJECTED_STOCK_AND_REPLENISHMENT.md), `scripts/replenishment/import_mycompany_snapshot.py` |
| [replenishment-planning-policy.json](../fixtures/replenishment-planning-policy.json) · `docs/fixtures/replenishment-planning-policy.json` | Política de demostración explícita (demanda, lead time, revisión, stock de seguridad, MOQ y múltiplos); no se infiere de ledgers | [Stock proyectado y reposición](../PROJECTED_STOCK_AND_REPLENISHMENT.md), `scripts/replenishment/plan_replenishment.py` |
| [replenishment-planning.json](../fixtures/replenishment-planning.json) · `docs/fixtures/replenishment-planning.json` | Casos sintéticos para decisión de reposición, expedición, supresión por pronóstico insuficiente y revisión de datos | [Stock proyectado y reposición](../PROJECTED_STOCK_AND_REPLENISHMENT.md) y `scripts/replenishment/test_plan_replenishment.py` |
| [rubrova-hero.svg](../assets/rubrova-hero.svg) · `docs/assets/rubrova-hero.svg` | Imagen vectorial de identidad/portada usada por el README; no contiene contrato funcional | [README principal](../../README.md) |

**Regla:** un fixture es una muestra sintética con propósito y límites concretos, no evidencia de datos reales ni de aceptación comercial. Al cambiar un esquema o una regla, actualizar el fixture, su validador/test y el documento que explica su semántica. No reutilizar fixtures para producción ni introducir datos personales reales.

## 8. Investigaciones históricas del Manual técnico: anexos A–K

El Manual técnico es extenso y contiene antecedentes que no deben perderse ni convertirse en fuentes competidoras. Las secciones 1–11 son el estado vigente. Los anexos conservan investigación, decisiones y planes previos; cuando haya contradicción, prevalece el estado vigente y se corrige la discrepancia.

| Anexo | Contenido preservado | Cuándo consultarlo |
|---|---|---|
| [A — Auditoría reuse-first de MyCompany y lsFusion](../ENGINEERING_MASTER.md#a-reuse-first) | Capacidades nativas, módulos y composiciones, candidatos de reutilización y análisis inicial por dominio | Siempre que se evalúe reutilizar o se investigue una capacidad nativa |
| [B — Guía de integración lsFusion 6.2 y MyCompany 6.2](../ENGINEERING_MASTER.md#b-integration) | Composición, extensiones, sesiones, transacciones, permisos, API y límites de integración | Antes de extender módulos, usar API, modificar acciones o tocar datos |
| [C — Contratos de integración históricos](../ENGINEERING_MASTER.md#c-contracts) | Contratos, productor/consumidor, idempotencia, estados, semántica de datos y errores | Al crear o cambiar contratos, exports, adaptadores o procesos asíncronos |
| [D — Relaciones y propiedad de datos](../ENGINEERING_MASTER.md#d-domain-relationships) | Grafo inicial de entidades, ledgers, fuentes y consumidores de reposición | Al cambiar inventario, reservas, ventas, compras, pagos o costos |
| [E — Decisiones de arquitectura](../ENGINEERING_MASTER.md#e-decisions) | ADR-0001 en adelante, razones y consecuencias de decisiones adoptadas | Antes de reabrir una decisión o proponer arquitectura alternativa |
| [F — Investigaciones y pruebas cronológicas](../ENGINEERING_MASTER.md#f-iterations) | Registros REP, errores, hipótesis, experimentos, cambios y evidencias | Ante una regresión, una prueba histórica o un comportamiento ya investigado |
| [G — Plantilla histórica de registro](../ENGINEERING_MASTER.md#g-record-template) | Formato histórico para reportar síntomas, evidencia y cierre | Para mantener trazabilidad de una investigación; la regla actual sigue en secciones 1–2 |
| H — Roadmap previo preservado | Fases anteriores, prioridades, entregas y definición de terminado | Para conocer el razonamiento histórico; el roadmap vigente manda |
| I — Estado previo preservado | Capturas históricas de estado y validación de plataforma | Para comparar evolución; no utilizar como estado actual |
| J — Plan maestro previo preservado | Diseño y alternativas que antecedieron a la decisión actual | Para recuperar contexto si se reabre una alternativa |
| K — Calidad y pruebas previas preservadas | Checks, criterios de aceptación, seguridad, rendimiento y continuidad | Al ampliar una matriz de pruebas; prevalecen los gates actuales |

No hay que leer el manual de cientos de kilobytes linealmente para cada tarea. Consultar su tabla de contenidos, la sección vigente que gobierna la cuestión y el anexo histórico relacionado. No copiar partes de anexos a nuevos documentos sin actualizar la fuente canónica.

## 9. Herramientas de auditoría y fuentes concretas

| Ruta | Función | Cuándo usarla |
|---|---|---|
| `platform/source-lock.json` | Fija las revisiones de las dos fuentes upstream | Antes de leer, comparar o actualizar código |
| `platform/mycompany-6.2.lock.json` | Lock específico de la fuente MyCompany | Al verificar versión/composición de MyCompany |
| `extensions/lsfusion/RubrovaCustom.lsf` | Raíz real de composición de Rubrova | Para calcular el cierre de `REQUIRE`; no asumir que la raíz es sólo `MyCompany` |
| `scripts/platform/audit-lsf-source.mjs` | Catálogo estructural de módulos, REQUIRE, namespaces, declaraciones y cierre de dependencias | Para obtener inventario reproducible de 800/49/7 y cambios del snapshot |
| `scripts/platform/module-integration-route.mjs` | Consulta cualquier módulo por nombre exacto o archivo .lsf; devuelve fuente, namespace, composición, REQUIRE, consumidores y ruta de lectura | Obligatorio antes de integrar/modificar un módulo concreto |
| `scripts/platform/module-integration-route.test.mjs` | Protege la resolución exacta, dependencias/consumidores, módulos fuera del cierre y enlaces de fuentes LSF | Ejecutar junto con los tests del mapa documental |
| `scripts/platform/audit-lsf-source.test.mjs` | Pruebas del parser y del grafo estructural | Al cambiar el generador |
| `scripts/platform/audit-source-docs.mjs` | Índice de páginas Markdown, idioma, ruta, título y encabezados de docs upstream | Para localizar material de MyCompany/lsFusion por idioma y tema |
| `scripts/platform/audit-source-docs.test.mjs` | Pruebas del índice documental | Al cambiar el indexador |
| `scripts/platform/local-preflight.sh` | Ejecuta tests de auditoría y de plataforma antes del build | Obligatorio antes de validar una entrega |
| `.github/workflows/documentation-map.yml` | Valida catálogo, rutas por módulo, plantilla, generadores upstream y recursos de `docs/` ante cambios documentales | Gate CI documental obligatorio |
| `.github/workflows/documentation-map.yml` | Ejecuta el test de cobertura de los 79 recursos de `docs/`, prueba ambos generadores y publica los catálogos de 30 días | Se activa cuando cambia documentación, instrucciones, plantilla, parches o auditorías |
| `.github/pull_request_template.md` | Solicita documentar el caso, los módulos nativos revisados, la decisión reuse-first, los contratos y la evidencia | Completar en cada PR; en commits directos a `main`, dejar el mismo registro en la documentación/commit |
| `scripts/platform/validate-vendored-sources.sh` | Comprueba integridad y cantidades mínimas de fuentes vendorizadas | Al incorporar o actualizar snapshots |
| `patches/lsfusion/README.md` | Política para parches directos al motor: cuándo usar extensión, procedencia, archivos upstream afectados, versión y pruebas | Antes de modificar directamente `vendor/platform` |
| `vendor/UPSTREAM_SOURCES.md` | Procedencia y límites de los snapshots upstream incluidos | Al revisar licencias, procedencia o cambios de origen |
| `vendor/mycompany/README.md` y `vendor/mycompany/CHANGELOG.md` | Orientación y cambios declarados por MyCompany upstream | Al investigar un comportamiento, regresión o actualización de MyCompany |
| `vendor/platform/README.md`, `vendor/platform/README_ru.md` y `vendor/platform/CHANGELOG.md` | Orientación y cambios declarados por lsFusion upstream | Al investigar lenguaje, runtime o actualizar la plataforma |
| `vendor/platform/server/src/main/resources/web/objects/multiselect/README.md` | Documentación incluida junto al componente multiselect del servidor web | Al extender o diagnosticar ese componente visual |

**Cobertura upstream:** los 1.031 documentos de las cinco raíces oficiales (347 MyCompany en inglés/polaco/ruso; 684 lsFusion en inglés/ruso) aparecen individualmente en `source-document-register.md` y `source-document-catalog.json`. El registro es estructural (ruta, idioma, título, encabezados e imágenes), no una lectura ni una certificación de la semántica. Los siete archivos de soporte indicados arriba quedan fuera de esas raíces y por eso se catalogan aquí por separado.
| `scripts/platform/apply-rubrova-source-patches.py` | Aplica parches Rubrova sobre fuentes upstream con controles explícitos | Al compilar la fuente modificada |
| `extensions/lsfusion/` | Extensiones propias de Rubrova | Antes de modificar módulos upstream; revisar si la extensión existente basta |
| `patches/lsfusion/` | Parches que afectan directamente el motor | Sólo cuando una extensión no alcanza; documentar origen, motivo y tests |

Los generadores publican en CI los artefactos `rubrova-lsf-source-catalog` (JSON + registro Markdown) y `rubrova-source-document-catalog` (JSON + registro Markdown). Son índices generados del snapshot actual. No forman parte del repositorio como documentación manual y **no sustituyen** las fichas semánticas de cada módulo.

## 10. Ficha que debe completarse para cada módulo/capacidad

Aplicar la ficha definida en `ENGINEERING_MASTER.md` sección 9.3 y esta lista como guía de navegación:

1. Identidad: nombre real del módulo, ruta, versión, namespace, dueño, dominio y nivel de evidencia.
2. Composición: `REQUIRE`, extensiones, clases consumidoras/productoras, módulos fuera del cierre y recursos Java/JS/CSS/SQL/Jasper asociados.
3. Modelo: clases, jerarquías, datos maestros, relaciones, propiedades persistentes/calculadas/abstractas, índices/materializaciones y claves.
4. Interacción: formularios, navegador, filtros, diálogos, acciones, atajos, informes, importadores y exportadores.
5. Reglas: validaciones, restricciones, eventos, estados, permisos, transacciones, concurrencia y semántica de NULL/cero/vacío.
6. Circuito: alta, edición, confirmación, cancelación, duplicación, devolución/reversión y recuperación.
7. Efectos: documentos relacionados, líneas, ledgers, deuda, caja, inventario, costo, reportes, APIs y sistemas externos.
8. Operación: configuración, usuario/rol, servicios necesarios, secretos, logs, monitorización, backup y restore.
9. Reutilización: nativo, extensión, adaptador, módulo propio, parche o dependencia; justificar la decisión.
10. Evidencia: fuentes/line ranges, versión, SHA, tests, entorno, resultado y pendientes.

Una ficha no se marca completa con sólo un resumen de lo que hace el módulo. Si no aplica un campo, explicarlo; si no se conoce, registrarlo como pendiente.

## 11. Reglas para mantener este catálogo

- Todo archivo `.md` bajo `docs/` debe quedar clasificado aquí; el test lo comprueba. Un documento nuevo no está "documentado" hasta estar relacionado con el material y las rutas que lo usan.
- Un dossier nuevo o una ampliación de dominio debe incorporarse a la tabla de la sección 5, a la ruta de la sección 4/6 y al Manual técnico si altera estado, decisión, evidencia o roadmap.
- Cada investigación debe dejar referencias hacia atrás (fuentes y análisis previos) y hacia adelante (módulos relacionados, consumidores, pruebas y documentos que el equipo debe leer después).
- Cuando un documento quede reemplazado, no borrar el conocimiento útil: marcarlo como histórico, indicar su sucesor y mover la precedencia al Manual técnico.
- Las rutas de lectura no deben suponer que cada cambio toca todo el ERP. Consultar el conjunto mínimo suficiente, pero seguir siempre las dependencias reales y las relaciones transversales identificadas.
- Los módulos regionales y fuera de la composición no se descartan sin análisis individual.
- No se cierra la puerta 9.7 por completar este catálogo: la cobertura documental, el análisis de fuente, la carga, la verificación, la conciliación y la aceptación son estados distintos.

## 12. Alcance que todavía falta cerrar

Aunque el catálogo de documentos está completo para el árbol `docs/`, queda trabajo técnico sustancial:
- leer y clasificar funcionalmente los 800 módulos MyCompany, incluidas las 112 fuentes fuera del cierre;
- seguir en profundidad formularios, propiedades, acciones, eventos, restricciones, permisos y efectos de los módulos activos y opcionales;
- completar la asociación de las 347 páginas Markdown de MyCompany con módulos y capacidades;
- clasificar y relacionar las 684 páginas y 178 imágenes de lsFusion con lenguaje, API, runtime y herramientas;
- completar el relevamiento de los 25 módulos LSF de plataforma fuera de la composición;
- probar en runtime las capacidades prioritarias, conciliar los ledgers y comprobar seguridad, fallos y recuperación;
- verificar localización es_AR y adecuación fiscal/legal argentina por módulo/flujo;
- completar una matriz reuse-first explícita para cada capacidad de producto priorizada.

**Conclusión de estado:** el inventario documental de `docs/` está catalogado, pero la investigación funcional integral de MyCompany 6.2 y lsFusion 6.2 continúa incompleta. Hasta cerrar los puntos anteriores, se mantiene abierta la puerta 9.7 y no se inicia desarrollo funcional nuevo salvo la investigación, documentación, auditoría y correcciones técnicas imprescindibles para completar el relevamiento.
