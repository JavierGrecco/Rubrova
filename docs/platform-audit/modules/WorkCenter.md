# Ficha de integración — WorkCenter

**Estado:** fuente base revisada; capacidad operativa avanzada no aceptada.  
**Dominio:** MyCompany 6.2 / Manufacturing.

## Responsabilidad

Maestro de centros donde se ejecutan operaciones. Define nombre, ID y descripción. No registra por sí mismo stock, tiempos reales de empleados ni capacidad finita.

**Fuente:** [WorkCenter.lsf](../../../vendor/mycompany/src/main/lsfusion/manufacturing/workOrders/WorkCenter.lsf).

## Interacción

Formulario \`workCenter\`, lista \`workCenters\`, diálogo \`dialogWorkCenters\`; navegación bajo Manufacturing → Configuration. Las operaciones de una BOM lo referencian y las órdenes de trabajo utilizan el mismo centro.

## Integración

- Crear un centro por recurso/área operativa que se necesite programar.
- Asociarlo a \`Operation\` en BOM y verificar que la orden de trabajo conserva ese vínculo.
- No inferir disponibilidad, calendario laboral, turnos, capacidad, costo de máquina o mantenimiento sólo porque exista un centro.
- No crear centros paralelos en un módulo Rubrova.

## Límites

\`WorkCenterLoad\` presenta una matriz por centro y día que suma duración de WorkOrders, permite ajustar/crear/eliminar duración y filtrar por orden. No demuestra planificación finita, restricciones de capacidad, calendario, secuenciación óptima ni APS.

## Pruebas

Probar ID/nombre duplicado, centro obligatorio en WorkOrder, centro inactivo/eliminado con histórico, accesos por ubicación/proyecto y edición desde WorkCenterLoad.

Seguir: [WorkOrder](WorkOrder.md), [Bom](Bom.md) y [Guía Fabricación + Proyectos](../MYCOMPANY_6_2_MANUFACTURING_PROJECTS_INTEGRATION.md).
