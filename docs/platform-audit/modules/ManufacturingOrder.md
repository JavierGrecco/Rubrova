# Ficha de integración — ManufacturingOrder

**Estado:** fuente central revisada; aceptación runtime y conciliación E2E pendientes.  
**Dominio:** MyCompany 6.2 / Manufacturing.

## Responsabilidad

Documento propietario de planificación y ejecución de fabricación o desarme. Mantiene cabecera, BOM, ubicaciones, cantidades planificadas/reales, líneas de materiales y productos terminados.

**Fuente:** [ManufacturingOrder.lsf](../../../vendor/mycompany/src/main/lsfusion/manufacturing/orders/ManufacturingOrder.lsf).

## Modelo

- Cabecera: tipo, fecha, numerador, artículo, responsable, empresa, BOM, ubicación de materiales y nota.
- \`ConsumedLine\`: artículo, unidad y \`toConsume/consumed\`.
- \`FinishedLine\`: producto, unidad, \`toProduce/produced\` y \`costRatio\`.
- Extensiones: estado, reservas, inventario, costo, lotes, mermas, relación de proveedor/venta y proyecto.

## Formularios y acciones

Formulario \`manufacturingOrder\`, lista \`manufacturingOrders\`, acciones \`Create Lines\`, \`Mark as Todo\`, \`Check availability\`, \`Unreserve\`, \`Manufacture\`, \`Mark as Done\`, \`Cancel\`, copia, merma y creación masiva. Las acciones provienen de distintos módulos requeridos por el compositor \`Manufacturing\`.

## Ciclo y reglas

\`Draft → Waiting → Ready → In progress → Done/Canceled\`.

- BOM debe coincidir con artículo de orden.
- Ubicación de materiales se exige para reserva; destino de productos se exige al terminar.
- La disponibilidad se calcula usando el ledger de reservas/disponible; la reserva debe cubrir líneas requeridas.
- Producción/consumo reales pueden distribuirse proporcionalmente al cambiar la cantidad total.
- \`Mark as Done\` fija fecha de ejecución y activa movimientos físicos/costo.

**Riesgo crítico:** si \`produced\` o \`consumed\` están vacíos, \`markAsDone\` usa las cantidades planificadas. Rubrova debe bloquear ese cierre sin confirmación explícita de cantidades reales.

## Ledgers

- \`ManufacturingOrderInv\`: entrada de producto terminado y salida de materiales.
- \`ManufacturingOrderRes\`: reservas de consumo y expectativa de producción.
- \`ManufacturingOrderCost\`: costo de consumo y costo distribuido al terminado.
- \`ManufacturingOrderLot\`: asignación de lotes a consumo/producción.
- \`ManufacturingOrderScrap\` + \`ScrapInv/ScrapCost\`: merma física y económica.

No escribir en estos ledgers ni recalcular saldos desde código propio.

## Integración con Proyectos

\`ProjectManufacturingOrder\` asocia la orden al proyecto; \`ProjectManufacturingOrderTimeEntry\` asocia los partes de horas; \`ProjectManufacturingOrderCost\` incorpora el salario de esos partes a \`laborCost\`. Ver las fichas específicas y la guía integral.

## Límites y pruebas

Probar parciales, sobreconsumo, insuficiencia de reserva, concurrencia, desreserva/cancelación, cantidades reales vacías, fecha/ubicación de costo, lotes, mermas, costo de servicios, costo laboral, permisos en ambas ubicaciones, pedido de venta origen, proyecto e idempotencia de acciones. La presencia del módulo o la compilación no demuestra la conciliación.

Seguir: [InvLedger](InvLedger.md), [ResLedger](ResLedger.md), [CostLedger](CostLedger.md), [Bom](Bom.md) y [Guía Fabricación + Proyectos](../MYCOMPANY_6_2_MANUFACTURING_PROJECTS_INTEGRATION.md).
