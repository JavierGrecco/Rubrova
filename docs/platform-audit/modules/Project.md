# Ficha de integración — Project

**Estado:** fuente base revisada; seguridad y ciclo E2E pendientes.  
**Dominio:** MyCompany 6.2 / ProjectManagement.

## Responsabilidad

Contexto y contenedor de trabajo: tipo, número, nombre, empresa, socio, fechas, estado, manager, descripción y documentos relacionados. No reemplaza pedidos, órdenes de fabricación, facturas ni partes de horas.

**Fuente:** [Project.lsf](../../../vendor/mycompany/src/main/lsfusion/projectManagement/projects/Project.lsf).

## Interacción y propiedades

Formularios \`project\`, \`projects\`, \`dialogProjects\`; lista con filtros Opened/Closed y Assigned to me. El proyecto expone paneles agregados por módulos de asignaciones, horas, tareas, pedidos, facturas, despachos, fabricación, reportes, etc.

La condición Active deriva de estado no cerrado y fecha final. \`ProjectStatus.closed\` gobierna el cierre configurable.

## Relaciones

- \`ProjectType\`: tipo y numerador; se extiende para definir tipo de orden de fabricación.
- \`ProjectAssignment\`: assignee/empleado, rol y fechas de vigencia.
- \`ProjectTimeEntry\`: partes de horas y acumulación de horas.
- \`ProjectManufacturingOrder\`: órdenes de fabricación vinculadas.
- \`ProjectSalesOrderManufacturing\`: propaga proyecto desde pedido de venta a la orden de fabricación.
- Los módulos de compra, venta, factura, despacho y nómina amplían la misma ficha.

## Integración

Mantener un único Project. Configurar tipo, empresa, manager, socio y estados; controlar accesos por ProjectAssignment y probar filtro por usuario/fecha. Asociar órdenes y horas a través de las extensiones nativas.

## Riesgo de seguridad

El código de ProjectAssignment contempla usuarios con acceso global y calcula acceso global para algunos usuarios sin asignaciones. No asumir aislamiento por proyecto sin revisar configuración, rol, usuario real y pruebas negativas.

## Límites y pruebas

Probar creación, tipos/numeradores, fechas, estado cerrado, asignaciones y vigencia, acceso global, acceso a documentos relacionados, proyecto en orden de fabricación, horas, documentos derivados, archivado y reinicio.

Seguir: [ProjectAssignment](ProjectAssignment.md), [ProjectTimeEntry](ProjectTimeEntry.md), [ProjectManufacturingOrder](ProjectManufacturingOrder.md) y [Guía Fabricación + Proyectos](../MYCOMPANY_6_2_MANUFACTURING_PROJECTS_INTEGRATION.md).
