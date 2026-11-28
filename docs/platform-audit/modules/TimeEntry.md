# Ficha de integración — TimeEntry

**Estado:** fuente base revisada; aprobación, nómina y costo laboral deben validarse por composición.  
**Dominio:** MyCompany 6.2 / ProjectManagement.

## Responsabilidad

Registro común de horas por empleado, fecha y tipo, con descripción. Las extensiones le agregan asociaciones a proyecto, tarea, orden de fabricación, asistencia y nómina.

**Fuente:** [TimeEntry.lsf](../../../vendor/mycompany/src/main/lsfusion/projectManagement/timeEntries/TimeEntry.lsf).

## Datos e interacción

Fecha (default hoy), Employee, TimeEntryType, horas, descripción y formularios \`timeEntry\`/ \`timeEntries\`. Permite copiar un registro; la copia incluye empleado, fecha, horas, tipo y descripción.

\`TimeEntryHours\` agrega plantillas de horas por tipo y una validación de compatibilidad del tipo de plantilla.

## Asociaciones por extensión

- \`ProjectTimeEntry\`: Project y obligación opcional de proyecto por TimeEntryType.
- \`TaskTimeEntry\`: Task.
- \`ProjectManufacturingOrderTimeEntry\`: ManufacturingOrder.
- \`ProjectTimeEntryPayslip\`: tarifa, salario y detalle de recibo.
- Timesheet de empleado/supervisor/móvil para carga por fecha y período.

No inferir que una hora registrada está aprobada, liquidada o imputada a costo de fabricación hasta verificar la extensión y su estado real.

## Integración y pruebas

No crear una segunda entidad de horas. Usar el TimeEntry nativo y sus extensiones. Probar duplicados empleado/fecha/tipo/proyecto, horas decimales, tipo, plantillas, asociación y desvinculación, permisos, autosave, edición, borrado, copia y reinicio.

Seguir: [ProjectTimeEntry](ProjectTimeEntry.md), [ProjectManufacturingOrderTimeEntry](ProjectManufacturingOrderTimeEntry.md) y [Guía Fabricación + Proyectos](../MYCOMPANY_6_2_MANUFACTURING_PROJECTS_INTEGRATION.md).
