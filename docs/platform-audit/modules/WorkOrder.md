# Ficha de integración — WorkOrder

**Estado:** fuentes centrales revisadas; aceptación de secuencia de operaciones pendiente.  
**Dominio:** MyCompany 6.2 / Manufacturing.

## Responsabilidad

Representa una operación/tarea de una orden de fabricación, en un centro de trabajo y con fecha/hora/duración. No es la orden de fabricación ni un ledger de inventario.

**Fuentes:** [WorkOrder.lsf](../../../vendor/mycompany/src/main/lsfusion/manufacturing/workOrders/WorkOrder.lsf), [WorkOrderOperation.lsf](../../../vendor/mycompany/src/main/lsfusion/manufacturing/workOrders/WorkOrderOperation.lsf), [WorkCenterLoad.lsf](../../../vendor/mycompany/src/main/lsfusion/manufacturing/workOrders/WorkCenterLoad.lsf).

## Datos e interacción

Nombre, ManufacturingOrder, WorkCenter, fecha de inicio, hora de inicio, duración y nota. Formularios \`workOrder\` y \`workOrders\`; estados Ready, In Progress y Done, con acciones Start y Mark as Done. Se muestra dentro de la orden de fabricación y en lista global.

## Generación

\`WorkOrderOperation.fillByQuantity\` elimina y reconstruye WorkOrders de la orden a partir de operaciones de la BOM; también genera routing de BOM intermedias marcadas como intermediate. La copia de una orden copia las WorkOrders y sus referencias/horarios.

**Cuidado:** regenerar líneas o BOM puede reemplazar WorkOrders existentes. No recalcular una orden con ejecución operativa sin evaluar el impacto.

## WorkCenterLoad

La vista resume duración por centro/día y permite crear/editar/eliminar una WorkOrder en una celda. No es evidencia de capacidad máxima, calendario ni programación avanzada.

## Integración

Usar WorkOrder para descomponer la ejecución y ver carga estimada. Para horas efectivas/personas y costo laboral usar TimeEntry/ProjectManufacturingOrderTimeEntry; no derivar salarios de la duración planificada.

## Pruebas

Generación de operaciones simples y anidadas, centro obligatorio, duración cero/negativa, cambios de fecha, estados, WorkOrder cerrada, edición desde tablero, regeneración tras cambio BOM, copia, acceso y reinicio.

Seguir: [WorkCenter](WorkCenter.md), [Bom](Bom.md), [ManufacturingOrder](ManufacturingOrder.md) y [Guía Fabricación + Proyectos](../MYCOMPANY_6_2_MANUFACTURING_PROJECTS_INTEGRATION.md).
