# Ficha de integración — ProjectAssignment

**Estado:** fuente revisada; permisos runtime y aislamiento multiusuario pendientes.  
**Dominio:** MyCompany 6.2 / ProjectManagement.

## Responsabilidad

Asocia proyecto y assignee con rol y período de vigencia. Sus relaciones y propiedades alimentan roles, filtros y acceso a proyectos.

**Fuente:** [ProjectAssignment.lsf](../../../vendor/mycompany/src/main/lsfusion/projectManagement/projects/ProjectAssignment.lsf).

## Datos y reglas

- Project (obligatorio).
- Employee/Assignee (obligatorio; el tipo base es Assignee).
- ProjectRole.
- fromDate (default currentDate) y toDate opcional.
- Restricción: toDate no puede ser anterior a fromDate.
- Las consultas de asignación consideran vigencia y fechas del período solicitado.

## Seguridad

\`hasAccess(Project, CustomUser)\` reconoce usuarios asignados. \`accessAllProjects\` puede conceder acceso global por configuración o por ausencia de asignaciones, según la lógica de la fuente. Los formularios de proyectos y diálogo aplican filtros de acceso. Los módulos de partes de horas también filtran por acceso/empleado.

No reemplazar estas reglas con una lista visual o un filtro sólo del cliente. Validar cada API y acción de escritura.

## Integración y pruebas

Configurar roles y períodos; probar empleado asignado/no asignado, assignee no Employee, rol, asignación futura/vencida, cambio de proyecto, usuario con acceso global, usuario sin asignaciones y accesos a proyectos relacionados. Probar filtros por fecha y por rango.

Seguir: [Project](Project.md), [ProjectTimeEntry](ProjectTimeEntry.md) y [Guía Fabricación + Proyectos](../MYCOMPANY_6_2_MANUFACTURING_PROJECTS_INTEGRATION.md).
