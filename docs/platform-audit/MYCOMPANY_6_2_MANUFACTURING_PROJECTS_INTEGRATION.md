# Integración obligatoria: Fabricación + Proyectos — MyCompany 6.2

**Estado:** análisis de fuente avanzado; aceptación funcional E2E pendiente.  
**Snapshot:** MyCompany 6.2 \`d21ca6978717b98b6300d90267f9767db7414008\`; lsFusion 6.2 \`dd4dbe5bf9b136e73e18fe25d741253929324350\`.  
**Propósito:** instrucción obligatoria para diseñar, configurar, extender, probar y operar fabricación y proyectos en Rubrova sin duplicar capacidades nativas.

> Esta guía separa tres niveles: lo que la documentación de MyCompany explica, lo que el código fuente 6.2 confirma y lo que Rubrova todavía debe demostrar en runtime. Una fuente presente o compilada no constituye aceptación funcional.

## 1. Regla de arquitectura

Rubrova utiliza MyCompany + lsFusion como una **suite ERP integrada**, con un único modelo transaccional y una única base de datos para estos dominios. Los módulos internos se conectan mediante composición \`REQUIRE\`, clases, propiedades, acciones, formularios, eventos y extensiones de puntos de entrada. No se debe introducir HTTP, colas, microservicios ni una segunda base de datos para comunicar internamente Fabricación con Proyectos.

Las integraciones externas sí requieren adaptadores y contratos explícitos. Deben respetar el dueño nativo del dato, autenticación, permisos, idempotencia, errores, conciliación y recuperación. La extensión actual \`RubrovaIntegrationResilience\` no debe presentarse como una plataforma genérica de workers/outbox/reintentos: su alcance implementado es más acotado.

**Consecuencia:** una orden de fabricación no debe actualizar existencias, reservas o costos escribiendo tablas o recalculando saldos por fuera de las acciones y ledgers propietarios de MyCompany.

## 2. Qué aporta cada dominio

### Fabricación

El compositor \`Manufacturing\` exige BOM, BOM anidadas, estructura/costo, importación, operaciones, órdenes, estados, reservas, inventario, costos, lotes, mermas, reportes, centros de trabajo y órdenes de trabajo. El inventario completo del árbol contiene 41 archivos LSF de fabricación. El número de archivos no equivale a 41 fichas aceptadas: la lectura profunda y la aceptación deben seguir registrándose por separado.

Fuentes de entrada:
- [Manufacturing.lsf](../../../vendor/mycompany/src/main/lsfusion/manufacturing/Manufacturing.lsf)
- [BOM](../../../vendor/mycompany/src/main/lsfusion/manufacturing/bom/Bom.lsf), [BOM anidada](../../../vendor/mycompany/src/main/lsfusion/manufacturing/bom/BomNested.lsf), [operaciones](../../../vendor/mycompany/src/main/lsfusion/manufacturing/bom/BomOperation.lsf)
- [Orden de fabricación](../../../vendor/mycompany/src/main/lsfusion/manufacturing/orders/ManufacturingOrder.lsf)
- [Reservas](../../../vendor/mycompany/src/main/lsfusion/manufacturing/orders/ManufacturingOrderRes.lsf), [inventario](../../../vendor/mycompany/src/main/lsfusion/manufacturing/orders/ManufacturingOrderInv.lsf), [costos](../../../vendor/mycompany/src/main/lsfusion/manufacturing/orders/ManufacturingOrderCost.lsf)
- [Lotes](../../../vendor/mycompany/src/main/lsfusion/manufacturing/orders/ManufacturingOrderLot.lsf), [mermas](../../../vendor/mycompany/src/main/lsfusion/manufacturing/orders/scrap/ManufacturingOrderScrap.lsf)
- [WorkCenter](../../../vendor/mycompany/src/main/lsfusion/manufacturing/workOrders/WorkCenter.lsf), [WorkOrder](../../../vendor/mycompany/src/main/lsfusion/manufacturing/workOrders/WorkOrder.lsf)

### Proyectos y tiempos

El compositor \`ProjectManagement\` incluye proyectos, asignaciones, tareas, equipos, partes de horas, timesheets de empleado/supervisor/móvil, compras, ventas, despachos, facturación, fabricación, costos de mano de obra, reportes y nómina. La integración con fabricación no es una asociación visual: almacena un \`Project\` en la orden de fabricación, propaga el proyecto a los partes de horas relacionados y deriva costo laboral de esos registros.

Fuentes de entrada:
- [ProjectManagement.lsf](../../../vendor/mycompany/src/main/lsfusion/projectManagement/ProjectManagement.lsf)
- [Project](../../../vendor/mycompany/src/main/lsfusion/projectManagement/projects/Project.lsf), [asignaciones y acceso](../../../vendor/mycompany/src/main/lsfusion/projectManagement/projects/ProjectAssignment.lsf)
- [TimeEntry](../../../vendor/mycompany/src/main/lsfusion/projectManagement/timeEntries/TimeEntry.lsf), [ProjectTimeEntry](../../../vendor/mycompany/src/main/lsfusion/projectManagement/projects/timeentries/ProjectTimeEntry.lsf)
- [ProjectManufacturingOrder](../../../vendor/mycompany/src/main/lsfusion/projectManagement/manufacturing/orders/ProjectManufacturingOrder.lsf)
- [ProjectManufacturingOrderTimeEntry](../../../vendor/mycompany/src/main/lsfusion/projectManagement/manufacturing/orders/ProjectManufacturingOrderTimeEntry.lsf), [Timesheet](../../../vendor/mycompany/src/main/lsfusion/projectManagement/timesheet/Timesheet.lsf)
- [Costo laboral por orden](../../../vendor/mycompany/src/main/lsfusion/projectManagement/manufacturing/orders/ProjectManufacturingOrderCost.lsf)

## 3. Propiedad de datos: no crear modelos paralelos

| Concepto | Dueño nativo | Regla para Rubrova |
|---|---|---|
| Producto, unidad y código | Master Data / \`Item\`, \`Product\` | Reutilizar artículo y sus unidades; no crear un maestro de insumos separado. |
| Receta/estructura | \`Bom\`, \`ComponentLine\`, \`ByproductLine\` | Reutilizar BOM y sus componentes/subproductos. |
| Orden y cantidades planificadas/reales | \`ManufacturingOrder\`, \`ConsumedLine\`, \`FinishedLine\` | La orden es el documento de ejecución; respetar estados y validaciones nativos. |
| Operación/centro/tiempo estimado | \`Operation\`, \`WorkCenter\`, \`WorkOrder\` | WorkOrder organiza tareas y carga estimada; no es otro inventario ni un MES completo. |
| Proyecto, estado y responsable | \`Project\`, \`ProjectType\`, \`ProjectStatus\` | El proyecto contextualiza trabajo y documentos; no reemplaza pedido, orden ni factura. |
| Miembros/roles/vigencia | \`ProjectAssignment\`, \`ProjectRole\` | Respetar fechas, roles y filtros de acceso nativos. |
| Horas efectivas | \`TimeEntry\` + extensiones \`ProjectTimeEntry\`, \`TaskTimeEntry\` | Un parte de horas debe mantener empleado, fecha, tipo, horas y sus asociaciones válidas. |
| Vínculo orden↔proyecto | \`ProjectManufacturingOrder\` | No duplicar el vínculo en una tabla de Rubrova. |
| Vínculo parte↔orden | \`ProjectManufacturingOrderTimeEntry\` | Validar que el proyecto del parte coincida con el proyecto de su orden. |
| Existencia física | \`InvLedger\` / \`ManufacturingOrderInv\` | No modificar saldos directamente. |
| Disponible/comprometido/esperado | \`ResLedger\` / \`ManufacturingOrderRes\` | Respetar signo, ubicación y \`skipAvailable\`. No confundir con stock físico. |
| Valoración | \`CostLedger\` / \`ManufacturingOrderCost\` | Dejar que el ledger calcule costo con la fecha/ubicación correctas. |
| Costo de mano de obra | \`TimeEntry\` + \`ProjectTimeEntryPayslip\` + \`ProjectManufacturingOrderCost\` | Configurar y probar la fuente de \`rateSalary\`; no inventar un costo/hora paralelo. |
| Costo de servicios y mermas | \`BillCost\`, \`ScrapCost\`, \`ManufacturingOrderCost\` | Usar asignación nativa de costos y documentos de merma. |

El grafo \`REQUIRE\` expresa dependencias de código; no reemplaza el mapa de relaciones comerciales/documentales. La ficha de cada módulo debe revisar ambos.

## 4. Recorrido operativo de fabricación

### 4.1 BOM y estructura

1. Crear el artículo terminado, componentes y unidades en Master Data.
2. Crear una BOM para el artículo, definiendo su cantidad base y unidad.
3. Incorporar componentes con sus cantidades normativas; registrar subproductos por separado.
4. Definir las operaciones de la BOM, cada una con centro de trabajo, hora de inicio y duración estimada.
5. Para estructuras multinivel, usar BOM anidadas y marcar los intermedios que deban generar routing.
6. Revisar la vista de estructura/costo antes de habilitar la receta. La BOM por defecto debe estar activa, no archivada, y corresponder al mismo artículo que la orden.

La generación de líneas calcula cantidades proporcionalmente a la cantidad base de BOM. Recalcular líneas reconstruye las líneas de consumo/producción y las órdenes de trabajo derivadas: no debe hacerse después de registrar ejecución real sin entender qué datos reemplazará. La importación/exportación XLSX existente cubre cabeceras, componentes y subproductos.

### 4.2 Orden, reserva y ejecución

El recorrido nativo documentado es:

\`Draft → Waiting → Ready → In progress → Done\` (o \`Canceled\`).

- **Draft:** tipo, artículo, BOM, responsable, empresa, fecha y ubicación de materiales. \`Create Lines\` ejecuta \`fillByQuantity\`.
- **Waiting:** pedido listo para abastecimiento. \`Check availability\` calcula disponible en la ubicación de materiales y registra reservas en \`ResLedger\`.
- **Ready:** sólo debe alcanzarse cuando las líneas requeridas quedaron reservadas completamente. La acción permite \`Unreserve\`.
- **In progress:** se registran \`consumed\` en materiales y \`produced\` en productos terminados. Al cambiar una cantidad total, la lógica nativa distribuye proporcionalmente los valores de las líneas.
- **Done:** exige ubicación de productos terminados y fija fecha de ejecución; activa los ledgers físicos y de costo.
- **Canceled:** libera/termina el ciclo según las acciones nativas. Deben comprobarse reservas y movimientos antes de asumir que cancelar equivale a revertir cualquier efecto.

**Bloqueo funcional prioritario:** \`ManufacturingOrderDone.markAsDone\` asigna las cantidades planificadas a producción y consumo cuando no hay cantidades reales registradas. El botón de cierre, por sí solo, no prueba una fabricación real. Antes de usarlo para producción comercial, Rubrova debe impedir el cierre basado únicamente en cantidades planificadas y exigir confirmación explícita de cantidades reales, responsable y lote cuando corresponda.

### 4.3 Existencias, reservas y costos

- \`ManufacturingOrderInv\` registra salidas de componentes desde la ubicación de materiales y entradas de terminados en la ubicación de productos.
- \`ManufacturingOrderRes\` reserva materiales y también registra una expectativa negativa de los terminados. El parámetro \`increaseAvailableStock\` del tipo controla si esa expectativa influye en el disponible; mantenerlo desactivado hasta justificar y probar la política.
- \`ManufacturingOrderCost\` calcula costo de materiales a partir del consumo real, la ubicación de materiales y la fecha de ejecución.
- El costo total suma materiales, \`extraCost\`, \`laborCost\` y \`serviceCost\`.
- La merma genera un documento \`Scrap\` separado, con baja física y costo; cuando está vinculada a la orden, alimenta \`extraCost\`.
- El costo laboral se obtiene de salarios asociados a partes de horas de la orden.
- Las líneas de servicio de facturas de proveedor pueden distribuirse a órdenes abiertas mediante \`ManufacturingOrderBillCost\`.
- El total se distribuye entre líneas de producto terminado por \`costRatio\`; si no hay coeficientes, la regla nativa concentra el costo en el artículo principal.

### 4.4 Lotes, subproductos y desarme

La base soporta lotes en materiales consumidos y productos elaborados, generación de lotes e impresión de etiquetas cuando están configuradas. No equivale a un sistema completo de vida útil: en las fuentes revisadas no se confirmó vencimiento, retención sanitaria, liberación de calidad ni asignación FEFO transaccional. Tampoco debe confundirse un subproducto planificado con una merma no planificada.

El desarme (\`Unbuild\`) es una orden con tipo especial: consume el producto fuente y recibe componentes de su BOM. Pasa por el mismo circuito de disponibilidad, ejecución, destino y costo.

## 5. Recorrido operativo de proyectos

### 5.1 Proyecto y permisos

\`Project\` contiene tipo, numerador, empresa, socio, fechas, estado, responsable/manager, descripción y documentos asociados. El estado cerrado depende de \`ProjectStatus.closed\`; la condición de activo también contempla fecha de finalización.

\`ProjectAssignment\` vincula proyecto, empleado/assignee, rol y fechas de vigencia. Las propiedades \`hasAccess\`, \`accessAllProjects\`, los filtros de proyecto y las asignaciones condicionan el acceso. **Advertencia:** el código concede \`accessAllProjects\` a determinados usuarios sin asignaciones; no inferir mínimo privilegio sin revisar configuración, roles y fixtures reales.

### 5.2 Partes de horas y timesheets

\`TimeEntry\` es el registro común: fecha, empleado, tipo, horas y descripción. \`ProjectTimeEntry\` agrega la asociación a proyecto y permite configurar \`projectRequired\` por tipo de parte. \`TaskTimeEntry\` agrega otra dimensión opcional: tarea. No reemplazar estas asociaciones con una tabla local de horas.

La suite incorpora timesheet de empleado, supervisor, supervisor móvil y asociación a tareas. \`autoSaveTimesheetHours\` modifica cuándo se aplica el cambio; la variante móvil confirma en su acción de cambio. El comportamiento debe probarse con los permisos y tipos reales de parte de horas.

### 5.3 Vinculación proyecto↔orden↔parte de horas

1. \`ProjectManufacturingOrder\` agrega \`project(ManufacturingOrder)\`, muestra las órdenes dentro del proyecto y el proyecto en la orden.
2. El tipo de proyecto puede definir el tipo de orden de fabricación. La creación desde el proyecto copia el proyecto, tipo y empresa y llama al punto de extensión \`fill(o,p)\`.
3. \`ProjectManufacturingOrderTimeEntry\` agrega \`manufacturingOrder(TimeEntry)\`, muestra las horas dentro de la orden y las órdenes dentro de los partes de horas.
4. Si cambia el proyecto de la orden y no se especificó otro proyecto en el parte, se propaga el proyecto; una restricción impide que parte y orden queden asociados a proyectos diferentes.
5. \`ProjectManufacturingOrderTimesheet\` permite cargar partes de horas desde timesheet del supervisor con una orden seleccionada, validando consistencia con el proyecto elegido.
6. \`ProjectManufacturingOrderCost\` suma \`salary(TimeEntry)\` de las horas asociadas a la orden dentro de \`laborCost\`.

La tarifa \`rateSalary\` está declarada como valor abstracto en \`ProjectTimeEntryPayslip\`; su fuente efectiva y su autorización no deben asumirse. Hay que inspeccionar la composición que la implementa, configurar el cálculo y probar importes, períodos, redondeos y permisos antes de aceptar costo laboral.

### 5.4 Venta que origina fabricación

\`SalesOrderManufacturing\` agrega BOM a la línea de pedido y puede crear órdenes de fabricación vinculadas a la línea cuando el pedido está confirmado y su tipo tiene configurado un tipo de fabricación. Si se activa \`autoCreateManufacturingOrder\`, la confirmación dispara la creación. El código impide cancelar o modificar ciertas dimensiones de líneas cuando ya existe una orden de fabricación iniciada.

\`ProjectSalesOrderManufacturing\` extiende ese punto de creación para copiar el proyecto del pedido de venta a la orden de fabricación. Por tanto, la cadena comercial puede ser:

\`Project → SalesOrder → OrderLine/BOM → ManufacturingOrder → WorkOrder/TimeEntry → Inventory/CostLedger → Invoice/Sales\`.

No recrear esta cadena desde Rubrova; configurar y probar sus puntos de extensión.

## 6. Qué es nativo, qué se configura y qué requiere extensión

| Necesidad | Decisión inicial | Qué verificar antes de desarrollar |
|---|---|---|
| Recetas, componentes y subproductos | Nativo: BOM | Unidades, cantidades base, artículos, costos, versiones/archivo y BOM anidadas. |
| Órdenes y estados de fabricación | Nativo: ManufacturingOrder | Transiciones, permisos, reservas y semántica de cantidades reales. |
| Routing y centros de trabajo | Nativo: BomOperation / WorkOrder / WorkCenter | Centros, duración, generación/reconstrucción de órdenes y cierre de operaciones. |
| Planificación finita, calendarios y capacidad por recurso | No demostrada por WorkCenterLoad | Relevar necesidades; la vista nativa agrega horas por día/centro, no prueba un motor APS. |
| Stock, reservas y costo | Nativo: ledgers | Ubicaciones, signos, concurrencia, fecha de valoración y conciliación. |
| Lotes de fabricación | Nativo: módulos de lotes | Elegibilidad, lotes de entrada/salida, saldo, impresión y trazabilidad. |
| Vencimiento, retención, liberación y FEFO | Extensión requerida | Metadata, reglas, concurrencia y controles antes de consumo/venta/despacho. |
| Proyectos y asignaciones | Nativo: Project / ProjectAssignment | Tipos, estados, manager, roles, fechas y acceso real. |
| Partes de horas por proyecto/tarea | Nativo: TimeEntry + extensiones | Tipos, obligación de proyecto/tarea, auto guardado, duplicados y aprobaciones aplicables. |
| Horas ligadas a fabricación y costo laboral | Nativo: ProjectManufacturingOrderTimeEntry / Cost | Imputación, tarifa abstracta, moneda, períodos, redondeos y permisos. |
| Servicios imputados a producción | Nativo: ManufacturingOrderBillCost | Cuentas, asignación y conciliación con factura de proveedor. |
| Cierre sólo con cantidades reales | Extensión/guardia Rubrova prioritaria | Impedir que markAsDone complete silenciosamente el plan; pruebas parciales y reinicio. |

## 7. Configuración mínima previa a un piloto

### Maestros y configuración
- [ ] Artículos, servicios, componentes, productos y unidades normalizados.
- [ ] Empresas, socios, depósitos y ubicaciones con reglas de acceso.
- [ ] Tipos y numeradores de proyecto; estados y criterio de cierre.
- [ ] Asignaciones, roles, vigencia y política de acceso por proyecto.
- [ ] Tipos de orden de fabricación, numerador, ubicación de materiales, ubicación de productos y tipo de merma.
- [ ] BOM activas, cantidad base, componentes, subproductos y routing.
- [ ] Centros de trabajo y operaciones.
- [ ] Tipos de partes de horas, plantillas de horas y regla projectRequired.
- [ ] Implementación configurada de rateSalary; período, moneda y redondeo aprobados.
- [ ] Política para increaseAvailableStock revisada y probada.
- [ ] Lotes y etiquetas configurados, sin declarar FEFO/vencimiento hasta contar con guardas validadas.

### Comprobación de composición
- [ ] Ejecutar el CLI para cada módulo citado y revisar estado en el cierre de RubrovaCustom.
- [ ] Confirmar que los módulos proveedores están en el cierre real, no sólo presentes en vendor.
- [ ] Revisar REQUIRE y consumidores directos/transitivos; revisar por separado relaciones de documento/ledger.
- [ ] Confirmar qué módulos opcionales/regionales no se activarán y por qué.
- [ ] No activar módulos regionales rusos/polacos/búlgaros para resolver un caso argentino sin evaluación legal/técnica específica.

## 8. Comunicación y transacciones: contrato de integración

**Entre módulos internos:** clases y propiedades compartidas, \`REQUIRE\`, extensiones de clases/formularios y puntos abstractos como \`fill\`/\`fillByQuantity\`. Se conserva el contexto nativo de sesión y transacción. Las acciones que modifican documentos deben respetar \`APPLY\`, \`NEWSESSION\`, validaciones y cancelación de la interfaz.

**Entre documentos y ledgers:** la orden genera hechos físicos, reservas y costo mediante los módulos nativos. No insertar filas en ledgers, no calcular \`onHand\` a mano y no usar un parte de horas como sustituto de costo contable.

**Entre Rubrova y servicios externos:** usar un adaptador explícito y los contratos versionados del proyecto. Definir quién es dueño del dato, autenticación, identificador idempotente, correlación, timeout, errores, reintentos realmente implementados, conciliación y operación manual. No usar HTTP interno para evitar estudiar una extensión lsFusion ya disponible.

**Al extender upstream:** preferir, en este orden: configuración nativa; módulo nativo no activado si satisface el caso; \`REQUIRE\` y extensión nativa; hook/acción/property abstracta; adaptador externo cuando corresponde; parche upstream mínimo sólo si no hay extensión segura. Todo parche debe estar versionado, ser determinista/idempotente cuando corresponda y tener prueba que detecte cambios upstream.

## 9. Pruebas obligatorias antes de declarar aceptado el circuito

1. **BOM:** cantidad base distinta de uno, redondeos/unidades, BOM anidada, intermedio, subproducto, ciclo prohibido, cambio de BOM y recalculado de líneas.
2. **Reservas:** suficiente/insuficiente, múltiples ubicaciones, reserva parcial, desreserva, cancelación, concurrencia y reinicio.
3. **Ejecución:** producción y consumo parciales, diferencias contra plan, cero producido, sobreconsumo, cierre sin cantidades reales y destino incorrecto.
4. **Ledgers:** salidas/entradas físicas, reservas/esperados, costo histórico, ubicación de costo, cantidad por lote y ausencia de doble contabilización.
5. **WorkOrder:** creación desde operaciones, BOM intermedia, regeneración tras recalcular, centro obligatorio, cambios de fecha/duración, estados y orden madre cerrada.
6. **Mermas/subproductos/desarme:** documento independiente, stock, costo, distribución por salida y vínculo correcto con la orden.
7. **Proyectos y acceso:** empleado asignado/no asignado, rol, vigencia futura/vencida, usuario con acceso global, proyecto cerrado y empresa.
8. **Partes de horas:** tipo que requiere/no requiere proyecto, tarea, empleado/fecha/tipo repetido, timesheet de empleado/supervisor/móvil, autosave, borrado y reinicio.
9. **Imputación laboral:** parte vinculado a orden, proyecto copiado, discrepancia rechazada, tarifa, moneda, períodos, redondeo, costo en orden e informe.
10. **Integración comercial:** pedido confirmado → orden de fabricación; modo automático/manual; cambios antes/después de iniciar; cancelación; propagación del proyecto.
11. **Permisos y reportes:** acceso a ambas ubicaciones, proyecto, empleado, orden, informes y exportación.
12. **Recuperación:** reinicio del servidor, backup/restore y conciliación documental/ledger posterior.

Cada prueba debe identificar SHA, plataforma, modo de runtime, datos semilla, acción ejecutada, resultado esperado/real, consulta de conciliación y evidencia adjunta. Las fixtures sintéticas no reemplazan el ensayo con una base nativa aislada del mismo snapshot.

## 10. Orden de integración recomendado

1. Cerrar la lectura de módulos y relaciones de la versión fijada; documentar cada hueco.
2. Preparar un escenario de prueba con una empresa, un proyecto, un empleado, dos artículos de componente, un terminado, una BOM, un centro y una ubicación de materiales/productos.
3. Configurar y ejecutar el circuito nativo de BOM → orden → reserva → producción → inventario/costo, sin extensiones de Rubrova.
4. Incorporar proyecto y asignaciones; ejecutar partes de horas asociados a la orden; verificar costo laboral y reportes.
5. Probar pedido de venta → orden de fabricación y propagación del proyecto.
6. Sólo entonces diseñar extensiones Rubrova para las brechas probadas: cantidades reales obligatorias, vencimiento/retención/FEFO, autorizaciones de producción y controles de trazabilidad.
7. Aceptar por separado cada etapa y documentar rollback/recuperación.

## 11. Reglas obligatorias para desarrolladores

- Antes de tocar cualquier módulo citado, ejecutar \`node scripts/platform/module-integration-route.mjs --module NombreExacto\` y leer ficha, guía y relaciones.
- No agregar modelos paralelos para BOM, orden, proyecto, parte de horas, centro, lote, inventario, reserva o costo.
- No escribir saldos, reservas o ledgers directamente.
- No inferir que \`REQUIRE\` significa uso en runtime, ni que un formulario significa aceptación de seguridad.
- No asumir que WorkCenterLoad es planificación finita, que el lote tiene vencimiento/FEFO o que rateSalary está listo.
- No cerrar producción cuando cantidades reales están vacías.
- Documentar cada modificación de extensión, prueba, limitación y decisión reuse-first en el dossier y el Manual técnico.
- Mantener las modificaciones de producto en \`main\` después de pruebas y revisión; no crear ramas persistentes innecesarias.

## 12. Fuentes de usuario y fichas

La documentación de MyCompany vendorizada está bajo \`vendor/mycompany/src/main/resources/docs/en/manufacturing/\` (manufacturing, bom, orders, workflow, production-and-consumption, costing, scrap, unbuild, by-products, work-orders, settings, reports y lotes). Se usa como guía de interacción, contrastada contra las fuentes LSF 6.2.

Fichas prioritarias:
- [BOM](modules/Bom.md) · [ManufacturingOrder](modules/ManufacturingOrder.md) · [WorkCenter](modules/WorkCenter.md) · [WorkOrder](modules/WorkOrder.md)
- [Project](modules/Project.md) · [ProjectAssignment](modules/ProjectAssignment.md) · [TimeEntry](modules/TimeEntry.md) · [ProjectTimeEntry](modules/ProjectTimeEntry.md)
- [ProjectManufacturingOrder](modules/ProjectManufacturingOrder.md) · [ProjectManufacturingOrderTimeEntry](modules/ProjectManufacturingOrderTimeEntry.md)

**Estado de cierre:** esta documentación vuelve obligatoria la ruta de lectura y deja una arquitectura de integración recomendada. No cierra la aceptación runtime de fabricación/proyectos ni la puerta general de conocimiento de MyCompany/lsFusion.
