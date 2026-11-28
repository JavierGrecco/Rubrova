# Ficha de integración — ProjectManufacturingOrderTimeEntry

**Estado:** fuente revisada; costo laboral y validación de partes pendientes de runtime.  
**Dominio:** MyCompany 6.2 / ProjectManagement + Manufacturing.

## Responsabilidad

Vincula TimeEntry con ManufacturingOrder y agrega el registro de horas al formulario de fabricación y a sus reportes.

**Fuente:** [ProjectManufacturingOrderTimeEntry.lsf](../../../vendor/mycompany/src/main/lsfusion/projectManagement/manufacturing/orders/ProjectManufacturingOrderTimeEntry.lsf).

## Contrato de datos

- \`manufacturingOrder(TimeEntry)\` es el vínculo con la orden.
- Expone número/fecha de orden y artículo en el parte.
- Agrega cantidad de partes y total de horas a ManufacturingOrder.
- Muestra partes dentro de la orden y la orden dentro del parte.
- Cuando cambia el proyecto de la orden, propaga el proyecto al parte si no fue modificado explícitamente.
- Restricción: si parte y orden tienen proyecto, deben coincidir; el guardado informa discrepancia.
- La copia de TimeEntry conserva la orden vinculada.

## Timesheet del supervisor

\`ProjectManufacturingOrderTimesheet\` agrega selección de orden en el timesheet del supervisor, exige coherencia entre proyecto seleccionado y proyecto de la orden y usa un hook \`newTimesheet\` para establecer el vínculo.

## Costos y reportes

\`ProjectManufacturingOrderCost\` agrega la suma de \`salary(TimeEntry)\` al \`laborCost\` de la orden. \`ProjectManufacturingOrderReport\` agrega horas, tarifa y salario al reporte pivot y aplica acceso a ubicaciones de materiales/productos.

La tarifa procede de \`rateSalary\`, valor abstracto en ProjectTimeEntryPayslip; verificar su implementación, moneda, período y redondeo.

## Pruebas

Crear parte desde la orden, desde el proyecto y desde timesheet; probar proyecto coincidente/discrepante, cambio de proyecto, copia, empleado asignado/no asignado, horas parciales, tarifa y costo, informe, acceso a ubicaciones y reinicio. No aceptar costo laboral si sólo se verificó la suma de horas.

Seguir: [ProjectTimeEntry](ProjectTimeEntry.md), [TimeEntry](TimeEntry.md), [ProjectManufacturingOrder](ProjectManufacturingOrder.md), [ManufacturingOrder](ManufacturingOrder.md) y [Guía Fabricación + Proyectos](../MYCOMPANY_6_2_MANUFACTURING_PROJECTS_INTEGRATION.md).
