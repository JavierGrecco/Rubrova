# Plan de trabajo

**Revisión:** 20 de noviembre de 2026  
**Dirección prioritaria:** POS y operación comercial → ERP de gestión → contabilidad/fiscalidad → análisis y reportes → perfiles sectoriales y canales → logística avanzada.

## Estado real

Rubrova se encuentra en **Fase 0: selección del núcleo operativo**. Hay visión, alcance, requisitos POS, modelo de dominio, arquitectura, investigación de plataformas, shortlist de código reutilizable y un dataset sintético. Todavía no hay aplicación funcional ni se incorporó código externo.

El workflow existente validó 21 pruebas del dataset y reglas aritméticas en su última ejecución registrada del 19/11/2026. Esa validación no instala ni prueba un POS, ERP, API, integración, backup o flujo real de Rubrova. Las nuevas modificaciones documentales tampoco se deben presentar como pruebas funcionales.

La dirección completa está en [Plan maestro de implementación](MASTER_IMPLEMENTATION_PLAN.md). La selección reuse-first está en [Estrategia de reutilización](REUSE_FIRST_IMPLEMENTATION_STRATEGY.md) y la prueba comparativa en [Evaluación de plataformas](PLATFORM_EVALUATION.md).

## Prioridad del producto

El seguimiento de envíos **no es una prioridad de inicio**. Se conserva en el modelo de dominio para que una venta pueda despacharse después y tenga uno o varios envíos, pero los conectores de transportistas se dejan para la última etapa.

| Orden | Resultado | Qué tiene que resolver |
|---:|---|---|
| 1 | POS y venta | Carrito, catálogo, clientes, precios, descuentos, cobro, vuelto, pagos mixtos, caja, devoluciones y ticket |
| 2 | ERP de gestión | Stock, depósitos, compras, proveedores, recepción, costo, clientes, cuentas corrientes y sucursales |
| 3 | Contabilidad y fiscalidad argentina | Libro mayor, cuentas, bancos, impuestos, ARCA, facturas, notas y conciliación |
| 4 | Reportes y control de gestión | Ventas, caja, compras, inventario, margen, rentabilidad por producto/marca/canal/área y resultados |
| 5 | Capacidades sectoriales | Recetas, producción, mermas, lotes, vencimientos, mayorista, distribución y servicios B2B |
| 6 | Canales externos | Ecommerce, Mercado Libre, WhatsApp, delivery y pedidos de otras plataformas |
| 7 | Logística avanzada | Transportistas, tarifas, etiquetas, retiro, entrega, tracking y reclamos |

Las dimensiones que afectan costos y reportes (unidad de negocio, canal, sucursal, centro de costo, depósito y proyecto) se incorporan desde el primer modelo. Se posterga el desarrollo sofisticado de BI, no la captura correcta de sus datos.

## Fase 0 — seleccionar la base del POS y la gestión

**Objetivo:** decidir qué aplicación o composición puede resolver el circuito POS + ERP sin comprometer propiedad de datos, operación local, recuperación ni arquitectura.

### Orden de evaluación

1. **ERPNext 16 / Frappe 16:** prueba inicial por la cobertura de POS, inventario, compras, contabilidad, dimensiones y reportes.
2. **MyCompany 6.2 / lsFusion:** prueba inicial por su Retail POS integrado y amplitud de CRM, ventas, compras, inventario, fabricación y facturación.
3. **Tryton 8.0 + tryton-ar 8.0:** candidato prioritario porque existe un conjunto de ocho ramas argentinas alineadas. Se debe probar instalación, tests y homologación antes de elegirlo. Tryton 8.2 queda como actualización posterior con port/revalidación.
4. **Dolibarr 24.0.3:** filtro de menor complejidad para POS/ERP y API.
5. **Posnic 1.9.2:** referencia POS secundaria, no candidato a ERP principal. Revisar licencias y dependencias, localización india, límites offline y compatibilidad de escritorio.

No se comparan por folleto ni por número de módulos. Se ejecuta el mismo circuito: catálogo → carrito editable → venta → pago y vuelto → caja → stock → devolución → reportes → recuperación.

### Tareas pendientes

- [ ] Fijar tags/commits y dependencias actuales de ERPNext 16, MyCompany 6.2, Tryton 8.0 + ocho módulos tryton-ar 8.0 y Dolibarr 24.0.3.
- [ ] Ejecutar filtro documental, de licencia, instalación, API, exportación, backup y restauración.
- [ ] Probar ERPNext y MyCompany con el flujo POS completo y jornada simulada.
- [ ] Instalar Tryton 8.0 con las ocho ramas tryton-ar fijadas en el [lock reproducible](TRYTON_ARGENTINA_8_0_LOCK.md), ejecutar tests y homologar WSFE/WSFEX; dejar Tryton 8.2 como upgrade posterior sujeto a port y revalidación.
- [ ] Ejecutar filtro corto de Dolibarr y decidir si entra en la comparación profunda.
- [ ] Mantener Posnic como comparador POS sólo si aporta una ventaja medible frente al POS incluido en los ERP.
- [ ] Llevar como máximo dos candidatos a la prueba profunda P01–P44.
- [ ] Decidir qué responsabilidades pueden quedar en una aplicación de dominio externa y qué dominios requieren servicios Rubrova independientes.
- [ ] Documentar decisión, evidencia, riesgos, licencias, costo de adaptación y camino de actualización.

**Criterio de salida:** candidato/composición elegida con pruebas reproducibles; autoridades de venta, pago, caja, stock, contabilidad y fiscalidad definidas; no se construyen módulos propios sobre una plataforma aún no seleccionada.

## Fase 1 — primera entrega: POS con gestión mínima real

**Objetivo:** tener un circuito comercial que se pueda usar y auditar, no una pantalla de demostración.

Alcance:

- Organización, sucursal, usuarios, roles, dispositivos, caja y depósito básicos.
- Catálogo, variantes, códigos de barras, unidades, productos pesables, precios y clientes.
- Carrito editable antes del cobro; descuentos, promociones e impuestos recalculables.
- Efectivo, vuelto, medios mixtos y registro del resultado de cada pago.
- Apertura, movimientos, arqueo y cierre de caja.
- Venta, ticket propio, cancelación y devolución parcial/total.
- Reservas y movimientos de stock con una autoridad única y ledger trazable.
- Documento fiscal separado del ticket, con estados visibles.
- Lector e impresora mediante adaptadores; terminal de pago real sólo tras pruebas de sandbox/homologación.
- Panel operativo con ventas netas, devoluciones, medios de pago, diferencia de caja y productos vendidos.
- Persistencia local, idempotencia, audit trail, backup/restore y reinicio del proceso.

**Criterio de salida:** una jornada repetible sin pérdida ni duplicación; ventas, pagos, caja, stock y documento fiscal conciliados; recuperación demostrada.

## Fase 2 — ERP administrativo

**Objetivo:** administrar el negocio de punta a punta detrás de la caja.

Alcance:

- Clientes/empresas, proveedores, contactos, condiciones y listas de precios.
- Cuenta corriente, crédito, vencimientos, saldos y límites con aprobación.
- Compras, órdenes, recepción parcial/total, devoluciones a proveedor y costos accesorios.
- Depósitos, transferencias, conteos, ajustes autorizados, reservas, lotes y vencimientos según el rubro.
- Valuación de stock y costo histórico/reposición con método documentado.
- Importación masiva, normalización y validación de datos.
- Sucursales y varias áreas de negocio; captura de unidad de negocio y centro de costo por línea cuando corresponda.
- Documentos, adjuntos, historial y auditoría.

**Criterio de salida:** ventas, recepciones, compras, costo y disponibilidad coinciden; toda diferencia tiene origen, responsable y tratamiento.

## Fase 3 — contabilidad, fiscalidad y administración argentina

**Objetivo:** convertir los hechos comerciales en resultados contables/fiscales confiables.

Alcance:

- Libro mayor, plan de cuentas, diarios, períodos, cierres y asientos.
- Cuentas por cobrar/pagar, bancos, conciliación, medios de pago, liquidaciones y comisiones.
- Impuestos, tipos documentales, puntos de venta, numeración y reglas argentinas.
- ARCA en homologación; emisión, consulta, estados inciertos, nota de crédito/débito y recuperación.
- CUIT, condición fiscal, retenciones/percepciones aplicables.
- Exportación e importación idempotente para el estudio o sistema contable usado (Tango, Catedral, Bejerman, Xubio, Colppy u otro).
- Conciliación desde la venta hasta el pago, el movimiento de stock, el comprobante y el asiento.

Bigcapital sólo se prueba si la contabilidad de la plataforma elegida no alcanza. No se mantienen libros mayores paralelos.

**Criterio de salida:** débitos/créditos, saldos, impuestos, ventas y documentos conciliados; ARCA homologado antes de cualquier habilitación productiva.

## Fase 4 — reportes y control de gestión

**Objetivo:** transformar datos correctos en decisiones sin inventar costos o conclusiones.

Orden de construcción:

1. Cierre diario: ventas netas, tickets, ticket promedio, descuentos, devoluciones, pagos y caja.
2. Ventas: artículo, variante, marca, categoría, cajero, cliente, sucursal, canal y área.
3. Inventario: disponible, reservado, en tránsito, rotación, cobertura, quiebres, excedentes, antigüedad y vencimientos.
4. Costos y margen: costo vendido, margen bruto, contribución neta de comisiones, embalaje y logística, precio de reposición y GMROI.
5. Compras y proveedores: cumplimiento, plazos, costos, diferencias y propuesta de reposición.
6. Finanzas: cuentas por cobrar/pagar, mora, caja, bancos, flujo y estados contables.
7. Rentabilidad por área y consolidado: minorista, ecommerce, mayorista/distribución y servicios.

Primero usar reportes nativos del núcleo. Para análisis local, probar DuckDB sobre datasets/exports canónicos. Metabase o Superset sólo se agregan si necesitamos BI multiusuario; sus consultas son de lectura y no reemplazan ledgers.

**Criterio de salida:** las métricas cuadran con los movimientos originales, muestran fórmula/fuente/filtros/actualización y declaran costos o datos faltantes. Los reportes no bloquean la caja.

## Fase 5 — perfiles sectoriales y capacidades de expansión

- Gastronomía, panadería y rotisería: recetas, BOM, rendimiento, merma, tandas de producción, comandas, cocina, pesables y vencimientos.
- Mayorista/distribución: mínimos, múltiplos, escalas, listas por cliente, crédito, entregas parciales y costo de servir.
- Servicios B2B: contratos, recurrencias, agenda, SLA, órdenes de trabajo, técnicos, horas, materiales, viáticos y rentabilidad.
- Varias áreas: permisos, recursos y resultados separados; consolidado sin ingresos internos ficticios.

**Criterio de salida:** perfiles que reutilizan los mismos maestros y servicios, sin duplicar clientes, ventas, inventario ni reglas contables.

## Fase 6 — canales e integraciones comerciales

- Ecommerce, pedidos por WhatsApp, Mercado Libre, delivery y otros canales reales.
- Integrar un canal por vez; probar pedidos, cancelaciones, pagos, comisiones y devoluciones.
- Webhooks firmados, idempotencia, estados externos, conciliación y prevención de doble factura/sobreventa.
- Spree o Saleor sólo como posible canal ecommerce, nunca como ERP/POS paralelo.
- PowerSync sólo si una prueba demuestra valor para lecturas/tareas offline; no coordina la última unidad de stock.

**Criterio de salida:** cada pedido externo se reconcilia con venta, pago, inventario y fiscalidad sin duplicados.

## Fase 7 — logística avanzada

El modelo de fulfillment y la posibilidad de agregar una guía después de vender existen desde el diseño inicial. La construcción de integraciones se posterga:

1. Retiro por cliente y entrega/reparto propio.
2. Carga manual de operador, guía, paquete y eventos.
3. Andreani, Correo Argentino PAQ.AR y OCA con credenciales de QA.
4. Vía Cargo como tracking externo mientras no haya API de booking verificada.
5. Agregadores, cotización, etiquetas, manifiestos, reclamos y analítica logística.
6. Kangu sólo si se confirma operación argentina.

**Criterio de salida:** los transportistas no controlan venta, pago ni stock maestro; cada envío conserva su vínculo con el pedido y su trazabilidad.

## Calidad transversal y definición de terminado

Todas las fases deben pasar las pruebas que correspondan:

- POS: rapidez, accesibilidad, teclado, lector, pantalla táctil, carrito editable, devoluciones y permisos.
- Integridad: idempotencia, CAS para stock, caja reconciliada y ausencia de doble emisión.
- Resiliencia: corte de red, terminación abrupta del proceso, reintentos, broker caído, restore y rollback.
- Seguridad: permisos en servidor, aislamiento por negocio/sucursal, gestión de secretos y auditoría.
- Datos: importación validada, fórmulas trazables, moneda/redondeos y costo explícito.
- Operación: instalación local, actualización, documentación en español y recuperación por una persona autorizada.
- Reutilización: versión/commit, licencia por archivo/dependencia, avisos, pruebas y costo de mantenimiento.

Ninguna capacidad se marca terminada porque exista una pantalla, documentación o demo. Se requiere evidencia reproducible.

## Entregables de investigación ya completados

- [x] Catálogo de código reutilizable y estrategia reuse-first.
- [x] Requisitos POS, checkout, efectivo, vuelto, pagos mixtos y terminales.
- [x] Modelo de dominio que separa venta, pago, stock, comprobante y envío.
- [x] Arquitectura de servicios de dominio, APIs/eventos, ownership, idempotencia, CAS, Outbox/Inbox y recuperación.
- [x] Dataset sintético y validador automático; última ejecución registrada: 21/21 pruebas de fixture aprobadas.
- [x] Investigación de ERPNext, MyCompany/lsFusion, Tryton, Dolibarr y Posnic.
- [x] Revisión de la localización argentina Odoo y de tryton-ar; se encontraron ocho ramas coordinadas 8.0 con manifiestos y tests; instalación y homologación pendientes.
- [x] Shortlist de componentes para fiscalidad, importación, hardware, analítica, producción, ecommerce, backup y logística.
- [x] Requisitos de reportes, métricas y rentabilidad por área.

## Próximos pasos concretos

1. Ejecutar el filtro comparativo POS + ERPNext 16 y MyCompany 6.2 con el mismo dataset y circuito.
2. Ejecutar Tryton 8.0 en paralelo con las ramas argentinas 8.0; instalar el conjunto, ejecutar tests y homologar. Tryton 8.2 se evalúa como actualización posterior.
3. Pasar Dolibarr 24.0.3 por el filtro corto y llevar como máximo dos finalistas a P01–P44.
4. Resolver las puertas de licencia, API, localización argentina, exportación, backup/restore y límite de dominio.
5. Elegir la base del primer circuito y recién entonces implementar/adaptar las brechas concretas.

La [investigación logística argentina](ARGENTINA_LOGISTICS_INTEGRATION.md) se conserva, pero no desplaza estos pasos ni condiciona el inicio del producto.
