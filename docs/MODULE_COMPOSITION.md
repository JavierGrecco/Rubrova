# Composición de módulos y contratos de integración

**Revisión:** 19 de noviembre de 2026  
**Dirección:** monolito modular como primera opción; adaptadores y servicios laterales cuando un componente externo o un dispositivo lo justifique.

## La regla central

Podemos incorporar partes útiles de proyectos distintos como módulos independientes. Pero “independiente” no significa que cada componente pueda ser dueño del mismo dato ni que los módulos escriban directamente en las tablas de los demás. Cada dominio tiene una autoridad, contratos estables y pruebas de integración.

## Formas de incorporación

| Forma | Cuándo conviene | Cómo se conecta |
|---|---|---|
| Módulo interno | Código fuente que encaja en nuestro runtime y puede mantenerse aislado | API pública de aplicación y dominio |
| Biblioteca/adaptador | Función técnica acotada, como ESC/POS, scanner o SDK fiscal | Puerto/capacidad implementada por el adaptador |
| Servicio local (sidecar) | Driver nativo, hardware o componente con runtime independiente | HTTP/gRPC/IPC local autenticado y versionado |
| Servicio externo | Adquirente, marketplace, ARCA o plataforma que no controlamos | API/webhooks con firma, idempotencia y conciliación |
| Plataforma integral | Resuelve gran parte del negocio con menor costo de adaptación | Se evalúa como base única, no en paralelo como otra fuente de verdad |

## Propiedad de datos

| Dato/ledger | Módulo responsable |
|---|---|
| Catálogo, SKU, variantes y unidades | Catálogo |
| Precio aplicado y fotografía de venta | Precios/Ventas |
| Carrito y checkout | Checkout/POS |
| Venta confirmada | Ventas |
| Intento y resultado de cobro | Pagos/adaptador del adquirente |
| Turno y libro de caja | Caja |
| Stock físico y libro de movimientos | Inventario/WMS, con ámbito de autoridad explícito |
| Pedido externo y fulfillment | Pedidos/Canales |
| Cupón, gift card y puntos | Promociones/Fidelización |
| Documento fiscal y autorización | Fiscal |
| Indicadores y pronósticos | Inteligencia (solo lectura) |
| Auditoría y autorizaciones | Seguridad/Auditoría |

Si se incorpora un WMS externo, decidir si ese WMS será dueño del stock físico de depósito y Rubrova mantendrá la vista comercial, o si el WMS solo aporta tareas. No permitir que ambos ajusten libremente la misma existencia.

## Contrato mínimo de un módulo

Cada módulo documenta responsabilidad, límites, datos propios, API/casos de uso, eventos, esquemas versionados, autorización, IDs externos, correlación, claves de idempotencia, errores tipados, reintentos, timeouts, transacciones, outbox/inbox, migraciones, auditoría, métricas, pruebas, licencia, versión y plan de sustitución.

El contrato habla el lenguaje del negocio; no filtra el modelo interno de un tercero.

## Integridad entre módulos

1. Guardar un intento interno con ID estable e idempotencia.
2. Confirmar localmente el estado pendiente antes de llamar al exterior.
3. Invocar el adaptador con referencia y clave de idempotencia.
4. Persistir respuesta/evento y correlacionarlo.
5. Actualizar el estado según transiciones permitidas.
6. Si no llega respuesta, consultar antes de repetir.
7. Si una etapa posterior falla, usar compensación explícita (cancelar, liberar reserva, reembolsar o emitir nota de crédito cuando aplique).
8. Conciliar periódicamente el estado local contra la autoridad externa.

Los mensajes pueden entregarse más de una vez; un único efecto de negocio se consigue mediante idempotencia y conciliación, no prometiendo “exactly once” de transporte.

## Eventos internos

Cada evento incluye event_id, event_type/version, occurred_at, recorded_at, business_id, branch_id, device_id/actor_id cuando corresponda, aggregate_type/id/version, correlation_id, causation_id y payload tipado. No contiene secretos ni datos personales innecesarios.

Los consumidores deduplican event_id y no asumen orden perfecto. Validan versiones y consultan la fuente autoritativa si hay huecos o eventos tardíos. Los eventos no reemplazan la transacción que confirma una venta o movimiento.

## Adaptadores por sistema operativo

- Dominio, casos de uso y contratos: neutrales al OS.
- UI web/PWA: navegador en Windows, Linux y macOS.
- API, conectores cloud y webhooks: runtime/servidor.
- USB/serie/Bluetooth: puente local con implementaciones por OS/modelo.
- Paquetes nativos: solo si la experiencia o el dispositivo lo requiere.

No se descarta una biblioteca por cubrir solo un OS. Se incorpora detrás de una interfaz estable y se implementan adaptadores para los sistemas faltantes cuando el valor lo justifique. La matriz de hardware registra modelo, proveedor, OS, versión, conexión y prueba física.

## Puertas de aceptación

Ningún módulo externo pasa a operación real hasta probar contratos, permisos, aislamiento, idempotencia, fallos parciales, recuperación, backup, auditoría, actualización, licencia, sustitución y ausencia de segunda fuente de verdad.

Ver [Arquitectura](ARCHITECTURE.md), [Modelo de dominio](DOMAIN_MODEL.md), [Checkout y terminales](CHECKOUT_AND_PAYMENT_TERMINALS.md) y [Calidad y pruebas](QUALITY_AND_TESTING.md).


## Módulos que habilitan varias áreas de negocio

- **Organización y dimensiones:** entidad legal, unidad de negocio, centros de beneficio/costo, sucursal, canal, territorio y permisos.
- **Ventas y precios:** ofertas, pedidos, reglas de mínimos, listas de precios, promociones, crédito y snapshots comerciales.
- **Fulfillment/WMS/TMS:** preparación, bultos, despachos parciales, tramos de transportista, tracking y pruebas de entrega.
- **Contratos/servicios:** acuerdos, SLA, calendarios, obligaciones, órdenes de trabajo, tiempos, materiales y aceptación.
- **Finanzas/analítica:** dimensiones contables, costos directos, pools compartidos, políticas de asignación y P&L por unidad.

Una cuenta de cliente compartida puede relacionarse con distintas áreas, pero la propiedad del maestro permanece en el módulo de clientes. Los contratos, acuerdos de suministro, pedidos y servicios referencian el mismo CustomerAccount.

## Contratos entre pedido, envío y tracking

El adaptador de transporte no crea la venta ni es dueño del inventario comercial. Recibe una orden de despacho, reserva/crea el envío, devuelve una referencia/guía cuando existe y publica eventos normalizados. La guía se puede registrar después de la venta, pero todo cambio se correlaciona con el Shipment y queda auditado.

Los envíos se pueden dividir y consolidar; la cantidad despachada nunca puede superar la cantidad confirmada y disponible/reservada. Los movimientos físicos se ejecutan una sola vez por ShipmentLine.

## Contratos, calendario y trabajo de servicio

El módulo de servicios posee contratos, SLA, obligaciones, agendas y órdenes de trabajo. El módulo de clientes conserva la identidad; ventas/facturación conserva los importes; inventario registra consumos de materiales; proyectos asigna costos cuando corresponda. Ninguna orden de trabajo puede crear una segunda factura por un trabajo ya facturado.

## Dimensiones y costos cruzados

Una operación mixta puede asignar distintas líneas a unidades diferentes. Los costos comunes usan AllocationPolicy versionada con base de reparto. Un módulo de analítica solo consulta los hechos y las asignaciones; no reescribe transacciones ni crea otro ledger.
