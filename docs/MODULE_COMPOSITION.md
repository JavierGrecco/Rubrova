# Composición de módulos y contratos de integración

**Revisión:** 20 de noviembre de 2026  
**Dirección:** núcleo POS+ERP integrado cuando resulte la opción más sólida, combinado con servicios Rubrova independientes sólo donde aporten valor. Los servicios propios tienen datos/contratos/ciclo de vida propios; los módulos internos de una suite compartida no se describen como microservicios.

## La regla central

Podemos incorporar proyectos completos, módulos, servicios o bibliotecas. La prioridad es reutilizar módulos maduros antes de escribir su equivalente. La modularidad lógica no demuestra independencia de despliegue: si varios módulos comparten base, runtime y migraciones son una aplicación integrada. Eso no impide adoptarla como núcleo POS+ERP si completa el circuito, mantiene una autoridad transaccional única, exporta y restaura todos los datos y permite conectar componentes externos por interfaces soportadas. Un servicio propio conserva su almacenamiento y ciclo de despliegue; una biblioteca se integra dentro del componente que la posee. Ningún segundo componente puede mantener el mismo ledger ni escribir directamente en tablas privadas ajenas.

## Formas de incorporación

| Forma | Cuándo conviene | Cómo se conecta |
|---|---|---|
| Servicio de dominio | Capacidad de negocio que necesita aislamiento, ciclo de vida o despliegue propio | API versionada y eventos durables; almacenamiento propio |
| Biblioteca compartida | Código técnico reutilizable que no necesita proceso o almacenamiento propio | Dependencia versionada, interfaz pequeña y tests del servicio consumidor |
| Biblioteca/adaptador | Función técnica acotada, como ESC/POS, scanner o SDK fiscal | Puerto/capacidad implementada por el adaptador |
| Servicio local (sidecar) | Driver nativo, hardware o componente con runtime independiente | HTTP/gRPC/IPC local autenticado y versionado |
| Servicio externo | Adquirente, marketplace, ARCA o plataforma que no controlamos | API/webhooks con firma, idempotencia y conciliación |
| Núcleo operativo integrado POS+ERP | Una suite existente cubre de punta a punta caja, ventas, inventario, compras, costos y/o contabilidad con una autoridad única | Se acepta como una aplicación de dominio integrada si pasa P01–P48, exportación, backup/restore en otra PC, permisos, extensibilidad y actualización. Sus módulos no se llaman microservicios; Rubrova se conecta por APIs/eventos/exports soportados y no duplica ledgers |
| Plataforma integrada especializada | Una aplicación cubre sólo un área (por ejemplo WMS, ecommerce o archivo documental) | Se adopta como servicio externo acotado si tiene contrato, datos/credenciales, backup/restore y ciclo de actualización propios; no absorbe autoridades ajenas |

Los módulos de la interfaz y las bibliotecas pueden agruparse por función, pero las capacidades operativas se comunican mediante APIs/eventos entre procesos. La descripción completa de gateway, broker, datos por servicio, Outbox/Inbox, Sagas y nodo local está en [Arquitectura modular distribuida](DISTRIBUTED_MODULAR_ARCHITECTURE.md).

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

Cuando el núcleo ERP elegido sea la autoridad integrada de ventas, compras, inventario y costos, la tabla de propiedad se interpreta como límites lógicos dentro de esa aplicación. No obliga a separarlos en bases/procesos; sí prohíbe que otros componentes mantengan una copia editable de esos ledgers. Inteligencia recibe snapshots de sólo lectura y concilia sus métricas con la fuente.

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


## Operaciones entre módulos y áreas

Cuando una unidad utiliza recursos de otra, el módulo propietario del recurso registra el hecho real. El módulo destino registra la asignación de consumo con una referencia al movimiento origen y su costo. Una política de transferencia gerencial puede calcular un cargo interno separado; no puede crear una segunda venta, factura fiscal, cobro o movimiento físico.

En el consolidado de una misma entidad legal se eliminan los cargos/créditos internos, dejando el costo externo original una sola vez. Entre entidades legales distintas se usa el contrato intercompany, con facturación y obligaciones fiscales propias, más las eliminaciones de consolidación cuando haya estados de grupo.

La auditoría conserva origen del costo, área emisora/receptora, política/tarifa aplicada y asiento de eliminación.


## Incorporación de una suite como fuente propia

Cuando una suite se convierte en el núcleo de Rubrova y la independencia operativa es un requisito, puede incorporarse como snapshot completo versionado en el repositorio, no como submódulo ni artefacto remoto. En esta composición inicial:
- vendor/platform/ contiene lsFusion 6.2.
- vendor/mycompany/ contiene MyCompany 6.2.
- extensions/lsfusion/ contiene los módulos Rubrova.
- patches/lsfusion/ contiene sólo las modificaciones directas del motor que no puedan resolverse por extensión.
- build/rubrova/pom.xml mantiene el reactor de compilación.

El código de terceros no pasa a ser de autoría de Rubrova: se mantienen licencias y atribuciones. Sí pasa a estar disponible en nuestro repositorio para modificación, auditoría, build y operación sin consultar el repositorio original. El procedimiento de upgrade compara el snapshot con el nuevo origen antes de integrar cualquier cambio.
