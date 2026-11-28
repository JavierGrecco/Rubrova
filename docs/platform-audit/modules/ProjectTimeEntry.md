# Ficha de integración — ProjectTimeEntry

**Estado:** fuente revisada; controles de acceso y horas en runtime pendientes.  
**Dominio:** MyCompany 6.2 / ProjectManagement.

## Responsabilidad

Extiende TimeEntry con una asociación a Project y agregados de cantidad de partes/horas por proyecto, empleado y período.

**Fuentes:** [ProjectTimeEntry.lsf](../../../vendor/mycompany/src/main/lsfusion/projectManagement/projects/timeentries/ProjectTimeEntry.lsf), [ProjectTimeEntryAssignment.lsf](../../../vendor/mycompany/src/main/lsfusion/projectManagement/projects/timeentries/ProjectTimeEntryAssignment.lsf).

## Datos y reglas

- \`project(TimeEntry)\` almacena el Project.
- \`projectRequired(TimeEntryType)\` permite exigir proyecto para determinados tipos; la restricción impide guardar parte sin proyecto cuando está activado.
- Agrega horas por proyecto, empleado, día y rango; muestra partes dentro del formulario de proyecto.
- La extensión Assignment filtra registros por acceso del proyecto o por el propio empleado y puede asignar defaultProject cuando corresponde.

## Integración con fabricación

\`ProjectManufacturingOrderTimeEntry\` suma una segunda asociación a ManufacturingOrder y controla que el proyecto del TimeEntry no contradiga al proyecto de la orden. El costo laboral usa la extensión de nómina, no el total de horas aislado.

## Integración y pruebas

Configurar qué TimeEntryType exige Project; validar acceso a lectura y escritura, empleados propios y supervisores, defaultProject, asociación a orden, proyecto discrepante, período y totales. No considerar suficientes los filtros del formulario: probar la autorización del servidor y los informes.

Seguir: [TimeEntry](TimeEntry.md), [ProjectAssignment](ProjectAssignment.md), [ProjectManufacturingOrderTimeEntry](ProjectManufacturingOrderTimeEntry.md) y [Guía Fabricación + Proyectos](../MYCOMPANY_6_2_MANUFACTURING_PROJECTS_INTEGRATION.md).
