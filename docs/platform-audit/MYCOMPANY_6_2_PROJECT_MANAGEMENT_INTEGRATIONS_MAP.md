# MyCompany 6.2 — mapa de proyectos, tareas, equipos, tiempos e integraciones

**Estado: 78 módulos LSF inventariados; núcleo de proyectos/tareas, workflow, partes de horas, turnos y varias integraciones leídos en fuente. Pruebas de runtime, conciliación de costos y revisión completa de cada extensión pendientes.**

El dominio `projectManagement` no es solamente un administrador de tareas. La raíz compone proyectos, tareas, equipos, asignaciones, horas, turnos, partes de horas, compras, ventas, inventario, facturación, fabricación, asistencia y recibos de sueldo. Es un eje transversal para asociar trabajo, documentos y costos.

## 1. Inventario de los 78 módulos

### 1.1 Núcleo, equipos, tareas y tiempos

| Grupo | Módulos |
|---|---|
| Raíz y configuración | `ProjectManagement`, `ProjectManagementSettings` |
| Proyectos y asignaciones | `Project`, `ProjectAssignment`, `ProjectFilter`, `ProjectGeo`, `ProjectInitial`, `ProjectRole`, `ProjectShift`, `ProjectStatus`, `ProjectType` |
| Tareas | `Task`, `TaskAPI`, `TaskDependency`, `TaskEmail`, `TaskFilter`, `TaskGantt`, `TaskInitial`, `TaskKanban`, `TaskKanbanTimeEntry`, `TaskNotify`, `TaskPriority`, `TaskStatus`, `TaskTag`, `TaskTimeEntry`, `TaskType`, `TaskWorkflow` |
| Equipos y asignados | `Assignee`, `Team` |
| Registro de horas | `TimeEntry`, `TimeEntryHours`, `TimeEntryType`, `ProjectTimeEntry`, `ProjectTimeEntryAssignment`, `ProjectTaskTimeEntry` |
| Partes de horas | `Timesheet`, `TimesheetEmployee`, `TimesheetSupervisor`, `TimesheetSupervisorMobile`, `TimesheetSupervisorTask`, `TimesheetTask` |
| Turnos | `Shift`, `ShiftSchedule` |

### 1.2 Integraciones con otros dominios

| Área | Módulos |
|---|---|
| Asistencia | `ProjectAssignmentAttendanceMobile`, `ProjectAttendance`, `ProjectAttendanceKiosk`, `ProjectAttendanceMobile`, `ProjectTimeEntryAttendance` |
| Inventario | `ProjectReceipt`, `ProjectShipment`, `ProjectShipmentPrint` |
| Facturación de proveedor | `ProjectBill` |
| Facturas de venta | `ProjectInvoice`, `ProjectInvoicePrint`, `ProjectInvoiceShipment`, `ProjectSalesLedgerInvoice`, `ProjectTimeEntryInvoice` |
| Fabricación | `ProjectManufacturingOrder`, `ProjectManufacturingOrderCost`, `ProjectManufacturingOrderReport`, `ProjectManufacturingOrderTimeEntry`, `ProjectManufacturingOrderTimesheet` |
| Haberes | `ProjectAssignmentPayslip`, `ProjectPayslipLedger`, `ProjectPayslipLine`, `ProjectTimeEntryPayslip`, `ProjectTimeEntryPayslipInitial` |
| Compras | `ProjectPurchaseOrder`, `ProjectPurchaseOrderBill`, `ProjectPurchaseOrderReceipt` |
| Ventas | `ProjectSalesOrder`, `ProjectSalesOrderShipment`, `ProjectSalesOrderInvoice`, `ProjectSalesOrderManufacturing`, `ProjectSalesLedger`, `ProjectSalesLedgerReport` |

La lista identifica archivos/módulos. Algunos extienden clases y formularios definidos en otros dominios y no son entidades independientes. La raíz `ProjectManagement.lsf` declara qué módulos entran en la composición del dominio; la ficha estructural por archivo se mantiene en el registro automático.

## 2. Proyecto como entidad principal

Fuente: `projects/Project.lsf`.

La clase `Project` contiene:
- tipo y numeración propia;
- nombre;
- empresa;
- socio/cliente;
- fecha de inicio y fin;
- estado;
- responsable/gerente (empleado);
- descripción enriquecida;
- comentarios, archivos e historial mediante utilidades comunes.

Reglas observadas:
- el tipo se propone desde el único tipo disponible cuando corresponde;
- la empresa se inicializa desde la empresa predeterminada;
- la fecha inicial se propone desde el día actual;
- el gerente se propone desde el usuario conectado si éste es empleado;
- `closed` deriva del estado;
- `archived` se calcula cuando la fecha actual supera la fecha final;
- `active` requiere que no esté archivado ni cerrado.

**Distinción:** vencimiento por fecha y cierre por estado no son equivalentes. Un proyecto puede quedar archivado por haber pasado su fecha aunque no tenga un estado cerrado. Hay que probar el efecto de mover su fecha final y de cambiar el estado.

### 2.1 Tipos y estados

`ProjectType` guarda nombre, ID y numerador. Los tipos pueden ampliarse con configuración de tipos documentales de facturas, compras, recepciones, despachos y órdenes de fabricación.

`ProjectStatus` tiene nombre, ID y marca `closed`. El estado cerrado determina el cierre del proyecto.

### 2.2 Geolocalización

`ProjectGeo` amplía datos del proyecto con ubicación geográfica. Los módulos de asistencia móvil pueden utilizar la cercanía al proyecto para validar dónde se registra la asistencia. Requiere revisar geocodificación, coordenadas, permisos y política de ubicación.

## 3. Asignaciones, roles y acceso

Fuentes: `projects/ProjectAssignment.lsf`, `ProjectRole.lsf`, `teams/Assignee.lsf`, `Team.lsf`.

### 3.1 Asignación por período

`ProjectAssignment` enlaza:
- proyecto;
- empleado o equipo mediante `Assignee`;
- rol del proyecto;
- fecha desde;
- fecha hasta.

La fecha hasta no puede ser anterior a la fecha desde. El módulo calcula qué personas/equipos están asignados a un proyecto en una fecha determinada y materializa relaciones/contadores para facilitar consultas.

El rol determina las acciones que un usuario puede realizar en tareas o transiciones. Las funciones de asignación aceptan intervalos y fechas concretas; no se debe asumir que una asignación actual habilita trabajo retroactivo o futuro sin verificar la fecha usada en cada control.

### 3.2 Equipos como asignados

`Assignee` es una clase abstracta que admite extensiones como `Employee` y `Team`. El campo asignado de una tarea puede apuntar a un empleado o a un equipo. `Team` mantiene integrantes mediante `TeamMember` y puede archivarse.

Una tarea asignada a un equipo no necesariamente tiene un único ejecutor. La autorización y la atribución de horas se resuelven por las reglas que identifican el empleado que carga el tiempo.

### 3.3 Acceso

`ProjectAssignment` incluye propiedades abstractas `accessAllProjects` y `hasAccess` y una marca de acceso total por empleado. Los módulos consumidores tienen que implementar el contrato y filtrar los proyectos/tareas disponibles.

**Pendiente crítico:** demostrar la implementación efectiva de `hasAccess` y su relación con roles del sistema, visibilidad de proyectos, empleados externos, supervisores y acceso a tareas. La asignación funcional no equivale por sí sola a permiso de seguridad.

## 4. Tareas y workflow

### 4.1 Datos

Fuente: `tasks/Task.lsf`.

Una tarea guarda:
- ID y nombre;
- autor (empleado/usuario);
- asignado (empleado o equipo);
- fecha de inicio y fecha límite;
- progreso porcentual;
- estado y tipo;
- prioridad;
- tags;
- descripción enriquecida;
- historial, archivos, comentarios y actividades.

El autor se inicializa con el usuario actual cuando es empleado. La fecha inicial se propone con la fecha actual. El tipo puede proponer el primer estado permitido.

### 4.2 Tipo y estado

`TaskType` admite una matriz de estados permitidos. Si un tipo tiene estados configurados, se usan esos estados; si no tiene ninguno, la fuente permite considerar todos. Al cambiar el tipo, el estado puede volver al primer estado válido.

`TaskStatus` define nombre, ID, orden de presentación y marca de cierre. El orden determina la secuencia de columnas del Kanban. Los estados cerrados quedan separados de los abiertos.

`TaskPriority` usa la paleta común `Color`. `TaskTag` ofrece clasificación por etiquetas.

### 4.3 Workflow de transiciones

Fuente: `tasks/TaskWorkflow.lsf`.

La matriz de workflow se configura por:
- rol del proyecto;
- tipo de tarea;
- estado de origen;
- estado de destino;
- autorización del rol;
- autorización especial del autor;
- autorización especial del asignado.

La restricción impide cambiar el estado cuando el usuario actual no tiene una transición habilitada para alguno de sus roles, no es autor autorizado ni asignado autorizado.

**No confundir:** `TaskType` define qué estados existen para la tarea; `TaskWorkflow` define quién puede pasar de un estado a otro y bajo qué rol/relación. Los permisos del sistema siguen siendo una capa adicional.

### 4.4 Dependencias

`TaskDependency` relaciona tareas padre/hija, muestra tareas de las que depende una tarea y tareas que dependen de ella, y calcula un nivel mediante recursividad. La fuente revisada no demuestra que se bloqueen ciclos de dependencia.

**Pendiente:** intentar A→B→A, dependencias indirectas circulares, borrado de tareas relacionadas, cambios de fecha y propagación de plazos. No asumir que la visualización Gantt impide inconsistencias.

### 4.5 Kanban y Gantt

- `TaskKanban`: columnas por estado permitido, tarjetas con nombre/proyecto/tipo/prioridad/tags/asignado/fecha límite; permite cambiar estado dentro de la matriz configurada; orden por usuario.
- `TaskGantt`: componente Frappe Gantt; muestra inicio, fin, progreso y dependencias; permite edición desde el gráfico.

Ambos son vistas del mismo objeto `Task`, no fuentes de datos paralelas. Los cambios deben aplicar las mismas validaciones de workflow y permisos que la ficha.

### 4.6 Notificaciones y API

`TaskNotify` lanza una notificación push al asignado cuando cambia la asignación, si el empleado tiene conexión push activa.

`TaskEmail` compone asunto/cuerpo y notifica al autor/asignado según las reglas de comentarios y correo.

`TaskAPI`:
- `getTasks(assignedTo, task, opened, extended)` exporta tareas en JSON;
- valida que la tarea/empleado consultado exista;
- permite filtrar por asignado, tarea e indicador abierta;
- devuelve ID, nombre, autor, asignado, fechas, progreso, proyecto y, opcionalmente, descripción;
- `importTasks` importa/upserta tareas desde JSON por ID, incluyendo autor, asignado, fechas, progreso, proyecto y descripción.

La marca `@@api` identifica los métodos, pero no reemplaza la verificación de autenticación, autorización, validación de datos, idempotencia, límites ni auditoría.

## 5. Registro de horas

### 5.1 TimeEntry

Fuente: `timeEntries/TimeEntry.lsf`.

`TimeEntry` guarda:
- fecha;
- horas numéricas con dos decimales;
- empleado;
- tipo de tiempo;
- descripción.

El empleado se propone desde el usuario conectado. El tipo de tiempo puede tomar un valor predeterminado. Hay índices por empleado/fecha y fecha/empleado, y agregaciones por día, empleado, tipo e intervalo.

### 5.2 Relación con proyecto y tarea

`ProjectTimeEntry` agrega proyecto a `TimeEntry`. El tipo de tiempo puede marcar `projectRequired`; si está habilitado, no se puede guardar una entrada sin proyecto.

`TaskTimeEntry` agrega tarea a la entrada de tiempo. `ProjectTaskTimeEntry`:
- copia el proyecto desde la tarea si corresponde;
- impide que la tarea y la entrada de horas pertenezcan a proyectos distintos.

Así se puede rastrear horas por proyecto, tarea, empleado y tipo.

### 5.3 Timesheets

`Timesheet` permite editar horas por día/proyecto/tipo:
- guarda el proyecto seleccionado localmente en la sesión;
- permite seleccionar tipo de tiempo y unidad de horas;
- crea/actualiza/elimina entradas para el empleado y día;
- permite copiar horas del día anterior;
- puede limpiar todas las entradas de un día después de confirmación;
- tiene opción `autoSaveTimesheetHours`.

`TimesheetEmployee` permite al empleado consultar/cargar sus horas, o a usuarios con acceso general consultar las de otros empleados. `TimesheetSupervisor` permite a supervisores editar horas de los empleados asignados al proyecto, con opción de auto-guardado.

**Riesgo:** las operaciones de timesheet pueden actualizar o borrar múltiples registros de un día/proyecto; probar confirmación, transacción, concurrencia, permisos, edición retroactiva y recuperación ante error.

## 6. Turnos y planificación

`Shift` guarda fecha, intervalo horario, empleado asignado, nota y descripción. Puede tener archivos y asociarse a un proyecto mediante `ProjectShift`.

`ShiftSchedule`:
- permite definir plantillas con intervalos horarios;
- expone plantillas y empleados a un componente web de agenda;
- importa JSON con plantilla/fecha/empleado y crea turnos;
- utiliza recursos `shiftschedule.js` y `shiftschedule.css`.

No confundir `Shift` con `Attendance`: un turno planificado es el horario previsto; la asistencia registra la entrada/salida real.

**Pendiente:** superposición de turnos, turnos nocturnos, horas extra, feriados, permisos, cambios de horario, ausencias y relación con calendario laboral.

## 7. Integración con asistencia

`ProjectAttendance` vincula cada asistencia con proyecto y materializa conteos/horas por proyecto, empleado y fecha.

`ProjectAttendanceMobile` añade selector de proyecto a la asistencia móvil:
- se requiere que el proyecto esté activo;
- se valida que esté cerca de la ubicación del empleado, salvo excepciones;
- si hay un único proyecto cercano, puede proponerse automáticamente;
- la asistencia creada se vincula al proyecto elegido.

`ProjectAttendanceKiosk` agrega el selector de proyecto al kiosco de fichadas.

`ProjectAssignmentAttendanceMobile` y `ProjectTimeEntryAttendance` completan las relaciones entre asignaciones, asistencias y partes de horas. Hay una propiedad abstracta `skipAttendance` para excepciones de control por proyecto/usuario.

**Pendiente:** límites geográficos, precisión, falsa ubicación, proyectos cercanos superpuestos, empleado asignado a varios proyectos, entrada sin GPS, privacidad y conciliación de asistencia con horas de proyecto.

## 8. Integración con fabricación y costos

`ProjectManufacturingOrder`:
- permite configurar tipo de orden de fabricación en `ProjectType`;
- vincula orden de fabricación con proyecto;
- al crear desde proyecto, copia proyecto, tipo y empresa.

`ProjectManufacturingOrderTimeEntry` agrega orden de fabricación al `TimeEntry` y exige que el proyecto de la entrada coincida con el proyecto de la orden.

`ProjectManufacturingOrderTimesheet` añade selección de orden de fabricación al timesheet supervisor y copia esa orden a la entrada de tiempo.

`ProjectManufacturingOrderCost` agrega el costo de mano de obra de las entradas vinculadas al costo de la orden de fabricación.

Es una integración directa entre trabajo imputado, orden de fabricación y costo de producción. No debe sumarse otra vez en un módulo propio sin entender la fórmula y el ledger que finalmente recibe el costo.

## 9. Integración con recibos de sueldo

`ProjectTimeEntryPayslip` define `rateSalary(TimeEntry)` como punto abstracto y calcula salario por entrada como horas × tarifa horaria (redondeado a dos decimales). La tarifa puede implementarse a nivel de empleado/proyecto/equipo o por otro módulo.

Al generar un recibo:
- crea detalle `PayslipTimeEntry` por proyecto;
- copia cantidad = horas del período;
- copia total = salario acumulado;
- permite consultar dentro del recibo las entradas de tiempo, el proyecto, tarifa y salario.

`ProjectPayslipLedger` y `ProjectPayslipLine` agregan proyecto al ledger/línea de sueldo y permiten consultar montos por proyecto.

**Límite:** este mecanismo calcula costos/imputaciones de tiempo y puede aportar líneas al recibo genérico. No prueba el cálculo legal de haberes argentinos ni la tarifa correcta para cada régimen.

## 10. Integración con ventas, compras, inventario y facturación

El mapa de módulos incluye:
- `ProjectSalesOrder`: pedidos de venta vinculados al proyecto;
- `ProjectSalesOrderShipment`: despachos del pedido y proyecto;
- `ProjectSalesOrderInvoice`, `ProjectInvoice`, `ProjectInvoiceShipment`: factura y conversión de despachos vinculados;
- `ProjectSalesOrderManufacturing`: orden de fabricación surgida de la venta;
- `ProjectPurchaseOrder`, `ProjectPurchaseOrderBill`, `ProjectPurchaseOrderReceipt`: pedidos/recepciones/facturas de proveedor vinculados al proyecto;
- `ProjectReceipt` y `ProjectShipment`: movimientos físicos asociados directamente a proyectos;
- `ProjectBill`: factura de proveedor relacionada con proyecto;
- `ProjectSalesLedger`, `ProjectSalesLedgerInvoice` y `ProjectSalesLedgerReport`: atribución de ventas/ledger a proyecto;
- `ProjectInvoicePrint` y `ProjectShipmentPrint`: impresión asociada.

Las extensiones hacen que el proyecto pueda representar una orden de trabajo rentable: acumular ingresos, costos de materiales/servicios, tiempo de mano de obra, recepciones, despachos y documentos relacionados.

**Pendiente:** leer y probar cada extensión para saber qué campos se copian, qué tipo documental se selecciona, si hereda empresa/socio, cómo se cancelan documentos y cómo evitar doble contabilización de costos/ingresos.

## 11. Pruebas obligatorias

| Área | Escenarios mínimos |
|---|---|
| Proyectos | Estado cerrado vs fecha vencida, responsable, empresa/socio, archivo |
| Asignaciones | Desde/hasta, roles múltiples, empleado/equipo, fecha pasada/futura, permiso |
| Tareas | Tipo/estado, autor/asignado, workflow, prioridad, tags, cierre y reapertura |
| Dependencias | A→B→A, ciclos indirectos, borrar padre, mover plazos y Gantt |
| Kanban/Gantt | Estado inválido, permiso cambiado, concurrencia y orden por usuario |
| API | Acceso sin permiso, tarea inexistente, empleado inexistente, upsert repetido, datos inválidos |
| Horas | Múltiples tipos/proyectos/tareas, decimales, edición retroactiva y duplicados |
| Timesheet | Guardado automático, borrar día, copiar día, error parcial y concurrencia |
| Turnos | Solapamientos, medianoche, plantillas, import JSON y empleado sin asignación |
| Asistencia | GPS, proyectos cercanos, excepciones y diferencias con turno |
| Fabricación | Horas vinculadas a orden, tarifa, costo de mano de obra y asiento/ledger final |
| Nómina | Tarifa por empleado/proyecto, recibo por período, cambios de tarifa y pago parcial |
| Compras/ventas | Documentos por proyecto, facturas/recepciones/despachos, cancelaciones |
| Rentabilidad | Ingresos, costos, mano de obra, costos de servicio y doble imputación |

## 12. Estado

Las 78 fuentes están inventariadas y se revisó el núcleo de proyecto, asignaciones, tareas, workflow, dependencias, Kanban/Gantt, API, equipos, horas, timesheets, turnos y enlaces directos a asistencia, fabricación, nómina, ventas, compras, inventario y facturación.

**No se declara cerrado:** falta lectura funcional exhaustiva de cada extensión de integración, ejecución de circuitos en runtime, conciliación de costos/ingresos/horas y validación de permisos y excepciones.
