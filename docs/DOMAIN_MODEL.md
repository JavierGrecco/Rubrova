# Modelo de dominio

**Estado:** modelo conceptual inicial; entidades y límites se ajustarán durante la evaluación técnica.

## Organización y dimensiones

- Organization: propietario lógico del entorno privado.
- LegalEntity: entidad fiscal con CUIT, libros, impuestos y numeración propia.
- BusinessUnit: área de negocio, con responsables, políticas, objetivos y resultado.
- ProfitCenter: unidad responsable de un resultado económico.
- CostCenter: equipo o función donde se originan gastos.
- SalesChannel: canal de captación/atención; no equivale a BusinessUnit.
- Branch / Location / Warehouse: establecimientos, ubicaciones y depósitos.
- Territory: zona comercial/logística.
- Project: trabajo u objetivo acotado.
- ServiceContract / SupplyAgreement: compromisos con cliente y reglas de cumplimiento.

## Personas y clientes

- Party: identidad común de persona u organización.
- CustomerAccount: relación comercial con una o varias unidades de negocio.
- OrganizationAccount: cliente empresa con identificador fiscal, sedes y contactos.
- CustomerContact: comprador, autorizante, referente técnico o receptor.
- CustomerSite / Address: lugar de entrega o prestación.
- CustomerCommercialProfile: listas, crédito, territorio y políticas por unidad.

## Catálogo y reglas comerciales

- Product / Service / Variant / SKU / Barcode.
- UOM / UOMConversion / PackagingRule.
- PriceList / CustomerPrice / ContractPrice / PriceTier.
- PromotionRule / RebateAgreement / Coupon.
- MinimumOrderRule: mínimo por SKU, grupo, cesta, valor, territorio o período.
- CommercialSnapshot: reglas, precios, descuentos, impuestos y vigencia aplicados a una operación.

## Venta, pedido y cobro

- Quote / SalesOrder / SalesOrderLine: oferta, compromiso y líneas.
- OrderLineAllocation: unidad de negocio, centro de costo, canal, proyecto/contrato y distribución por línea.
- Cart / CartRevision / CheckoutSession: carrito editable y sesión de cobro.
- Sale / SaleLine: venta confirmada y sus líneas.
- PaymentIntent / PaymentAttempt / PaymentAllocation: intención, intento y distribución del cobro.
- CashTender / CashChange / CashMovement / RegisterShift: efectivo recibido, vuelto, libro de caja y turno.
- Invoice / CreditNote / FiscalDocument: factura, nota de crédito y documento fiscal separado.

## Terminales y pagos presenciales

- PaymentProviderAccount: cuenta del comercio en un PSP/adquirente y referencia segura a sus credenciales.
- PaymentTerminal: dispositivo físico, proveedor, modelo, firmware y modalidad de conexión.
- PaymentTerminalAssignment: asociación temporal entre caja, medio de pago y terminal.
- PaymentIntent / PaymentAttempt: intención comercial e intento concreto enviado a una terminal/proveedor.
- ProviderOperation / ProviderWebhookEvent: referencia externa, estado y notificación autenticada.
- Payment / PaymentAllocation: pago confirmado y su aplicación a la venta.
- PaymentRefund / PaymentReversal / Chargeback: efectos posteriores vinculados a la operación original.
- PaymentSettlement / SettlementLine: liquidación, bruto, comisiones, impuestos, retenciones y neto.

La terminal captura el medio de pago; el proveedor procesa la autorización. El pago confirmado no equivale a liquidación acreditada. Las asignaciones de pago mixto permanecen independientes. Véase [Arquitectura de terminales de pago y conciliación](PAYMENT_TERMINAL_INTEGRATION_ARCHITECTURE.md).

## Fulfillment y logística

- FulfillmentOrder: tareas de preparación derivadas de un pedido/venta.
- Shipment: despacho físico, separado de la venta/factura.
- ShipmentLine: cantidad de cada línea asignada a un envío.
- HandlingUnit: bulto, caja, pallet o contenedor.
- ShipmentLeg: tramo propio o de transportista.
- Carrier / CarrierService / CarrierBooking: operador y servicio contratado.
- TrackingReference: guía, código o ID externo, que puede incorporarse después de la venta.
- TrackingEvent: historial de estados y ubicaciones.
- HandoverEvent / ProofOfDelivery: entrega al transportista y prueba de entrega.
- DeliveryRoute / Stop / Vehicle / Driver: reparto propio.

Un pedido puede tener varias entregas. Un envío puede consolidar pedidos compatibles. La referencia del transportista no es requisito del pedido ni de la venta; sí se registra antes de publicar estados que requieren seguimiento externo.

## Inventario y compras

- StockLedger / InventoryMovement / StockReservation.
- Warehouse / Bin / Lot / Serial / Expiry.
- PurchaseOrder / PurchaseReceipt / SupplierInvoice.
- PickList / PackList / Transfer / StockCount.
- ProductionOrder / BOM / Recipe / Workstation / Waste / Yield.

## Servicios y contratos

- ServiceCatalogItem / ServiceAgreement / ContractVersion.
- ContractLine / Entitlement / SLA / ServiceCalendar.
- ServiceObligation / Recurrence / Appointment.
- WorkOrder / WorkTask / Assignment / Technician.
- TimeEntry / MaterialConsumption / TravelExpense / Subcontract.
- Evidence / CustomerAcceptance / ServiceVisit.
- ServiceInvoice / ContractConsumption / Renewal.

El contrato define lo prometido; las obligaciones definen qué debe suceder; las órdenes de trabajo registran qué se ejecutó; los consumos y evidencias soportan facturación y rentabilidad.

## Gestión económica y analítica

- LedgerEntry: hecho económico contabilizado.
- BusinessDimension: unidad, canal, sucursal, centro de costo, territorio, cliente, proyecto o contrato.
- DirectCost: costo atribuible directamente a una operación/unidad.
- SharedCostPool: costo común aún no distribuido.
- AllocationPolicy / AllocationRun / AllocationLine: método versionado de reparto y sus resultados.
- ProfitabilitySnapshot: estado de resultados por área y consolidado, con fecha, fuente y versión.
- KPI / MetricDefinition / Forecast: métricas y estimaciones reproducibles.

## Reglas de integridad

1. Cada agregado tiene un módulo propietario y una sola autoridad.
2. Los documentos conservan su fotografía de condiciones y dimensiones.
3. La venta, el pago, el movimiento de stock, el despacho y la factura son hechos relacionados pero distintos.
4. Los envíos y las órdenes de trabajo pueden dividirse y evolucionar sin duplicar el pedido origen.
5. Los costos compartidos se asignan con reglas explícitas; la suma asignada debe coincidir con el costo original.
6. Las integraciones usan IDs, correlación, idempotencia, estados tipados y conciliación.
7. Las dimensiones económicas se guardan a nivel de línea cuando una operación pertenece a varias áreas.


## Captura temporal y trazabilidad ampliada

El modelo conceptual se completa con la especificación [Captura de datos y base analítica](DATA_CAPTURE_AND_ANALYTICAL_FOUNDATION.md). Como mínimo, mantener entidades/relaciones para:

- establecimiento y perfil sectorial, separados de canal, área y fulfillment;
- empleado, asignación, sesión de caja, cajero, supervisor, terminal y dispositivo;
- versión temporal de categoría, marca/segmento, presentación, unidad, precio, costo, lista y promoción;
- orden de compra, línea, recepción parcial, lote, factura proveedor y costo puesto;
- movimiento de stock, reserva, transferencia y período de disponibilidad/quiebre por ubicación;
- intención, intento, autorización, captura, reintegro, contracargo, liquidación y conciliación de pago;
- promoción/versiones, descuento por línea, cupón, ajuste manual y aprobación;
- reclamo, devolución autorizada, ingreso físico, disposición, reintegro y documento compensatorio;
- referencia externa, idempotencia, auditoría, instante de ocurrencia y de registro.

## Reglas temporales y analíticas

1. Mantener `occurred_at`, `recorded_at`, vigencia efectiva y `business_date` como conceptos distintos; conservar UTC e IANA timezone.
2. Las dimensiones que cambian deben mantener versiones/vigencias; los documentos confirmados conservan snapshots de valores y clasificaciones aplicados.
3. El ledger de inventario y los hechos financieros/fiscales no se corrigen sobrescribiendo historia: se registran ajustes y compensaciones trazables.
4. Un quiebre de stock debe estar representado como disponibilidad en el tiempo, no inferido sólo desde ausencia de ventas.
5. Los informes derivan de una capa de lectura conciliada y nunca escriben en los agregados transaccionales.
6. Las exportaciones deben incluir tipos, relaciones, IDs, moneda, unidades, zona horaria, fórmula de métricas, filtros y corte de datos.


## Cliente 360 y segmentación conductual

El maestro Party/CustomerAccount comparte identidad y relaciones entre las áreas de negocio, pero no fuerza identificación en ventas anónimas. Para B2B soporta sedes, contactos y roles de comprador/aprobador/recepción/administración.

Las clasificaciones estables (retail, mayorista, empresa, institucional) se distinguen de los segmentos conductuales temporales (RFM, activo, en riesgo, inactivo, leal). Cada evaluación de segmento guarda fecha de cálculo, período, regla/modelo, entradas, versión, confianza y explicación. Las preferencias derivadas de compras se separan de las declaradas por el cliente y de las recomendaciones predictivas.

La especificación de entidades, métricas, privacidad y pruebas está en [Perfil 360 e inteligencia por cliente](CUSTOMER_360_AND_INTELLIGENCE.md).


## Pagos: separar cliente, pagador e instrumento

Agregar como agregados/entidades tipadas:
- PaymentIntent / PaymentAttempt / Payment / PaymentAllocation;
- ProviderOperation / ProviderWebhookEvent / PaymentSettlement;
- PaymentRefund / PaymentReversal / Chargeback;
- PayerObservation y PaymentInstrumentReference;
- ProviderAccount / Acquirer / PSP / Wallet / Bank / Terminal.

Un Payment puede asignarse a una venta y una venta a CustomerAccount, pero el pagador observado no se convierte automáticamente en cliente. Cada PayerObservation debe llevar proveedor, canal, campo, fuente, finalidad permitida, retención y estado de vinculación. Los datos restringidos a conciliación no pueden consultarse desde los servicios CRM/BI. El token/ID de tarjeta o cuenta es sólo referencia del proveedor y no una clave global de persona.

Ver [Identidad del pagador, pagos y conciliación](PAYMENT_IDENTITY_AND_RECONCILIATION.md) para flujos, controles y pruebas.
