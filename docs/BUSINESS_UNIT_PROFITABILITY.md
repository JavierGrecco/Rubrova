# Rentabilidad por área y resultado consolidado

**Revisión:** 19 de noviembre de 2026  
**Estado:** modelo de gestión propuesto; la configuración contable final debe validarse con asesoramiento profesional argentino.

## Objetivo

El dueño debe poder conocer:
- cuánto vende cada área;
- cuánto margen deja cada producto, cliente, contrato y canal;
- cuánto cuesta atender, preparar, transportar o prestar cada servicio;
- qué áreas crecen, cuáles consumen recursos y cuáles son rentables;
- cuánto aporta cada una al resultado global;
- qué parte del resultado depende de costos compartidos y qué parte aún no está asignada.

Los indicadores de gestión no sustituyen la contabilidad legal. Ambos se concilian y presentan con definiciones claras.

## 1. Dimensiones de análisis

Cada hecho económico debe poder analizarse por las dimensiones relevantes:

- entidad legal;
- unidad de negocio / centro de beneficio;
- centro de costo;
- canal;
- sucursal/depósito;
- territorio;
- cliente y segmento;
- producto, familia o servicio;
- pedido, envío, contrato y proyecto;
- vendedor, equipo o responsable;
- fecha operativa, fecha de factura y fecha de cobro.

La dimensión principal es la unidad de negocio. Canal, sucursal, cliente y producto son ejes adicionales; no deben sustituirla.

Si un pedido contiene líneas de áreas distintas, cada línea tiene su atribución. El documento puede tener una unidad principal para defaults, pero las líneas determinan la distribución efectiva de ingresos y costos.

## 2. Definiciones económicas

Los reportes deben distinguir:
- **Venta bruta:** precio antes de descuentos y devoluciones, sin sumar impuestos que se cobran por cuenta del fisco.
- **Descuentos y bonificaciones:** descuentos de línea/pedido y rebates reconocidos.
- **Devoluciones/notas de crédito:** reducen el ingreso del área original, no el área del día en que se procesó el reintegro.
- **Ingreso neto:** ingreso por venta/servicio menos descuentos y devoluciones, según política contable y fiscal.
- **Costo de mercadería vendida:** costo de los bienes efectivamente vendidos, usando el método de valuación elegido y consistente.
- **Margen bruto:** ingreso neto menos costo de mercadería o costo directo básico de prestación.
- **Costos variables de servir:** picking/packing, flete, reparto, comisiones, comisión de terminal, marketplace, medios de pago, embalaje, subcontratos y consumibles.
- **Margen de contribución:** margen bruto menos costos variables/directos asociados.
- **Costos directos fijos del área:** personal asignado, alquiler dedicado, herramientas/licencias exclusivas y otros costos atribuibles.
- **Costos compartidos:** administración, infraestructura, marketing común, depósito compartido, servicios y dirección.
- **Resultado operativo del área:** contribución menos costos directos fijos y la parte de costos compartidos asignada mediante una política explícita.

Los impuestos indirectos recaudados por cuenta del fisco no se tratan como ingreso propio. Las percepciones/retenciones y saldos fiscales se informan en sus cuentas específicas.

## 3. Costos directos y costos compartidos

**Primero asignar directo, después repartir lo compartido.**

Ejemplos de costos directos:
- flete pagado para un pedido mayorista;
- horas del técnico en un contrato;
- comisión del marketplace de una venta online;
- combustible y peajes de una ruta local;
- comisión de la terminal por una transacción;
- packaging específico.

Los costos compartidos solo se distribuyen con un driver explícito, medible y versionado, por ejemplo:
- metros cuadrados ocupados;
- horas de uso de personal/equipo;
- cantidad de pedidos o líneas procesadas;
- peso/volumen preparado;
- transacciones;
- usuarios o dispositivos;
- ingresos, cuando sea un criterio razonable y justificado.

Cada regla tiene vigencia, base de cálculo, origen, aprobador y método de redondeo. Se conserva el importe original y el detalle de la asignación para reproducir el reporte.

**Mostrar también costos no asignados.** Un resultado antes de costos compartidos y un resultado después de distribución responden preguntas diferentes. No forzar un reparto arbitrario para que todos los sectores cierren.

## 4. Ejemplos de asignación

### Venta con varias áreas
Una orden puede contener mercadería mayorista y un servicio de instalación. Las líneas de producto pertenecen al área mayorista; la instalación pertenece al área de servicios. Los descuentos se atribuyen a las líneas beneficiadas. Los impuestos siguen las reglas fiscales aplicables.

### Transporte compartido
El flete de un camión que lleva pedidos de varios clientes se distribuye por peso/volumen/pallets o una tarifa contractual. Se conserva el costo total del transportista y cada asignación. La suma asignada debe coincidir exactamente con el costo original, incluido el ajuste de redondeo.

### Administración común
El sueldo de administración se registra en centro de costo compartido. Al cierre del período se puede reportar no asignado y, adicionalmente, mostrar una vista con reparto por regla aprobada. La vista consolidada nunca cuenta el gasto original y sus asignaciones como dos costos distintos.

## 5. Reportes por área y consolidado

Cada unidad debe tener un estado de resultados:
1. ventas brutas;
2. descuentos, bonificaciones y devoluciones;
3. ingreso neto;
4. costo de mercadería o prestación directa;
5. margen bruto;
6. costos variables de servir;
7. margen de contribución;
8. gastos directos del área;
9. resultado antes de costos compartidos;
10. costos compartidos asignados;
11. resultado operativo después de asignaciones.

El consolidado suma las unidades sin volver a contar operaciones. Los costos compartidos originales aparecen una sola vez; los repartos son una vista de gestión y no un nuevo gasto.

## 6. Métricas específicas por área

| Área | Demanda y volumen | Rentabilidad / eficiencia |
|---|---|---|
| Minorista local | tickets, unidades, frecuencia, ticket promedio, franja horaria, quiebres | margen por SKU/categoría, costo por ticket, comisión de cobro, productividad por hora |
| Comercio online | visitas/conversión (si hay dato), pedidos, abandono, devoluciones, entrega | margen luego de comisión, picking, embalaje, envío, publicidad y devolución |
| Mayorista/distribuidora | cotizaciones, conversión, pedidos, unidades, volumen, recurrencia, clientes activos, cobertura territorial | margen por cliente y nivel de precio, costo por pedido, flete, costo de servir, días de cobro, mora |
| Servicios B2B | contratos, órdenes, visitas, horas, backlog, renovaciones, SLA | ingreso recurrente, margen por contrato/servicio, utilización, retrabajo, costo de desplazamiento, rentabilidad por técnico |

## 7. Tres perspectivas que no deben mezclarse

- **Devengado:** qué ingresos/costos pertenecen al período económico.
- **Facturado:** qué documentos se emitieron y cuándo.
- **Caja/cobrado:** qué dinero ingresó o salió y cuándo.

Una venta mayorista a 30 días puede mejorar el ingreso y el margen del período, pero no aumentar el efectivo disponible. Un contrato anual facturado por anticipado puede crear cobro, pero el reconocimiento del ingreso puede distribuirse según la política contable. El tablero muestra la perspectiva y no llama “ganancia” al saldo bancario.

## 8. Calidad de datos y cierres

- No se publica rentabilidad de un área si faltan costos materiales relevantes sin indicarlo.
- Se distinguen costos estimados de reales y se muestra la cobertura.
- Se registran costos tardíos y se permite recalcular con nueva versión, conservando el reporte anterior.
- Los repartos se pueden reproducir por fecha y versión.
- La suma de asignaciones coincide con el importe original.
- Ventas, facturas, devoluciones, inventario, pagos y bancos se concilian.
- Cada reporte explica fórmula, fuente, filtros y fecha de actualización.

## 9. Referencias investigadas

ERPNext documenta centros de costo jerárquicos, asignación a nivel de línea, repartos porcentuales, dimensiones contables personalizadas y P&L filtrado por centro/proyecto/dimensión:
- https://docs.frappe.io/erpnext/cost-center
- https://docs.frappe.io/erpnext/accounting-dimensions
- https://docs.frappe.io/erpnext/profit-and-loss-report

El modelo de Rubrova debe tomar esta capacidad como referencia, no copiar literalmente la semántica de un proveedor. Unidad de negocio, canal, centro de costo, sucursal y proyecto son dimensiones distintas.


## 10. Operaciones internas entre áreas y consolidación

Una unidad puede suministrar bienes o servicios a otra. Por ejemplo, el depósito mayorista entrega insumos a la unidad de servicios para cumplir un contrato, o un equipo central presta horas a otra área.

### Dentro de la misma entidad legal

- Registrar el movimiento físico/consumo una sola vez y conservar SKU, cantidad, depósito, lote y costo real.
- Atribuir el costo al área que consume el recurso. La unidad que administra el stock/personas conserva la trazabilidad de origen.
- Si se usa un precio de transferencia gerencial, registrarlo como dimensión/indicador interno, no como ingreso externo ni factura fiscal ficticia.
- El informe por área puede mostrar cargos y créditos internos para evaluar desempeño, pero la vista consolidada elimina ambos lados.
- El costo real del recurso aparece una sola vez en el resultado consolidado.
- Un movimiento interno no crea cobro, saldo de cliente ni IVA de una venta externa.

### Entre entidades legales distintas

Si las áreas pertenecen a CUIT/entidades legales diferentes, no tratarlas como simples centros de costo. La operación puede requerir factura, cuenta a cobrar/pagar, impuestos y documentación intercompany. La consolidación de grupo puede eliminar saldos/ingresos/gastos internos, pero debe conservar libros e impuestos de cada entidad.

Las reglas fiscales, de precios de transferencia y consolidación deben validarse con un profesional argentino antes de operar.

### Prueba de integridad

- El consumo aparece en el área destino y el origen queda trazable.
- Existe un único movimiento físico.
- Las imputaciones gerenciales internas se compensan/eliminan en la vista consolidada.
- El costo original no se duplica ni desaparece.
- Si cambia la entidad legal, se exige el circuito intercompany configurado, no una transferencia gerencial informal.
