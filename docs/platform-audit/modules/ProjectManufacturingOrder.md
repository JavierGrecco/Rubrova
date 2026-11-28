# Ficha de integración — ProjectManufacturingOrder

**Estado:** fuente revisada; creación desde proyecto y conciliación E2E pendientes.  
**Dominio:** MyCompany 6.2 / ProjectManagement + Manufacturing.

## Responsabilidad

Extiende ManufacturingOrder con una referencia a Project, incluye el listado de órdenes dentro del proyecto y expone el proyecto en la orden.

**Fuente:** [ProjectManufacturingOrder.lsf](../../../vendor/mycompany/src/main/lsfusion/projectManagement/manufacturing/orders/ProjectManufacturingOrder.lsf).

## Contrato observado

- \`project(ManufacturingOrder)\` es el vínculo persistente.
- \`ProjectType\` puede configurar \`ManufacturingOrderType\`.
- Crear orden desde Project copia proyecto, tipo y empresa; luego ejecuta el punto de extensión \`fill(o,p)\`.
- Project muestra órdenes relacionadas, estado, fecha, artículo y BOM.
- La orden muestra el proyecto.

## Integración con ventas

\`ProjectSalesOrderManufacturing\` extiende \`SalesOrderManufacturing\` y propaga a la orden de fabricación el proyecto del pedido de venta. No duplicar esa propagación en código propio sin demostrar un caso que la extensión no cubra.

## Límites y pruebas

El punto \`fill(o,p)\` es abstracto/extensible: no asumir que completa BOM, cantidad, fecha o ubicaciones sin revisar las implementaciones presentes en el cierre. Probar proyecto y empresa, tipo asociado, creación, edición, copia, proyecto cerrado, creación desde venta, permisos y conciliación con la orden.

Seguir: [Project](Project.md), [ManufacturingOrder](ManufacturingOrder.md), [ProjectManufacturingOrderTimeEntry](ProjectManufacturingOrderTimeEntry.md) y [Guía Fabricación + Proyectos](../MYCOMPANY_6_2_MANUFACTURING_PROJECTS_INTEGRATION.md).
