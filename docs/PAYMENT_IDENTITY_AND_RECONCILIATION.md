# Identidad del pagador, pagos y conciliación

**Revisión:** 20 de noviembre de 2026  
**Estado:** diseño de dominio e integraciones; los conectores y la resolución de identidad todavía no están implementados.

## 1. Decisión central

Rubrova no debe usar el medio de pago como identidad del cliente.

Una transacción puede tener varias personas relacionadas:
- **Comprador:** quien elige los productos y realiza la compra.
- **Pagador:** quien origina o confirma el pago.
- **Titular del instrumento:** titular de una tarjeta o cuenta.
- **Receptor:** quien recibe el producto/servicio.
- **Cliente comercial:** cuenta con la que el negocio mantiene la relación.

Pueden ser la misma persona, pero también pueden ser diferentes: tarjeta de un familiar, empleado que paga una compra de la empresa, asistente que paga en nombre del titular, transferencia desde una cuenta conjunta o efectivo entregado por un tercero.

Por eso ningún nombre, tarjeta, alias, CBU/CVU o referencia externa debe fusionar clientes automáticamente. Los datos de pago primero sirven para conciliar el dinero; una identidad de cliente sólo se crea/vincula cuando la fuente, el permiso y la finalidad lo permiten.

## 2. Qué devuelve cada medio

La información varía por proveedor, canal de integración, contrato, versión del API y tipo de pago. No hay un conjunto universal garantizado.

| Medio | Datos que pueden estar disponibles | Lo que no se debe asumir |
|---|---|---|
| Efectivo | Importe recibido, vuelto, caja, cajero, turno, fecha y venta relacionada | Nombre, teléfono o identidad de quien entregó el efectivo |
| Tarjeta presencial | Marca, tipo, últimos cuatro dígitos, emisor, cuotas, terminal, lote, código de autorización/referencia y resultado | Nombre legal del titular, documento o que la persona que usa la tarjeta sea el cliente/consumidor |
| Tarjeta online | Datos de checkout capturados legítimamente (email/nombre/documento cuando se solicita); token de pago y referencias de proveedor; metadatos de tarjeta | Que todos los procesadores devuelvan los mismos campos o expongan el titular a la aplicación del comercio |
| QR con transferencia | ID de orden/pago, importe, estado, referencia externa, billetera/banco de origen y, en algunos reportes/proveedores, nombre y documento del pagador | Que todos los QR, billeteras y APIs entreguen nombre/DNI o una identidad utilizable para CRM |
| QR con tarjeta | Datos de pago y del instrumento que exponga el adquirente; estado de autorización | Que se entregue la identidad del titular de la tarjeta o datos completos del comprador |
| Transferencia bancaria | Referencia bancaria, importe, fecha y descripción; según el banco/PSP, datos del ordenante y cuenta de origen | Que el comercio reciba siempre CBU/CVU/alias, nombre completo o documento de la contraparte |
| Pago mixto | Un registro independiente por cada componente, con su importe, proveedor y estado | Que el conjunto se pueda representar como una sola transacción homogénea |

### Hallazgos confirmados en documentación de proveedores

**Mercado Pago — QR y transferencias**
- Sus reportes documentan `PAYER_NAME`, `PAYER_ID_TYPE` y `PAYER_ID_NUMBER` para pagos QR y transferencias en los casos en que esos datos estén disponibles.
- La propia documentación dice que esos campos sólo pueden utilizarse para conciliación y deben tratarse conforme a la normativa de datos personales. Rubrova no los reutilizará para perfilar clientes, publicidad o marketing.
- Los reportes también ofrecen, según la operación, billetera de origen, banco de origen, nombre/ID de caja y sucursal, últimos cuatro dígitos, bandera de la tarjeta, emisor, cuotas, referencia externa, ID de operación y otros datos de conciliación.
- En QR integrado, Mercado Pago admite códigos estáticos, dinámicos e híbridos. El dinámico es único para cada transacción y permite asociar una order al checkout. Se debe usar una referencia externa interna no personal y una clave de idempotencia.

**Mercado Pago — tarjetas guardadas**
- El API de clientes/tarjetas puede devolver `customer_id`, `card_id`, marca, primeros/últimos dígitos, emisor y, en el contexto del vault de tarjetas de un cliente, datos de cardholder.
- Esto ocurre dentro del flujo de clientes/tarjetas guardadas, no significa que un pago presencial Point o cualquier pago QR revele automáticamente al comercio la persona titular. Nunca usar el card ID o token del proveedor como identidad universal entre proveedores.

**Fiserv — QR con pago mediante tarjeta**
- La documentación pública para QR con tarjeta dice que el comprador no necesita pasar datos al comercio; escanea el QR y, si la billetera lo requiere, ingresa CVV dentro de esa billetera. La pantalla de PosNet/Clover informa aprobación o rechazo.
- Es un ejemplo concreto de por qué no podemos depender del nombre del pagador para todos los cobros QR.

**Transferencias y cuentas**
- BCRA/Argentina distinguen CBU, CVU y alias. CBU y CVU identifican cuentas; el alias es una referencia vinculada a una cuenta. El BCRA define CVU como un código único de 22 dígitos que identifica una cuenta de un PSP.
- Que un identificador de cuenta sea unívoco no significa que el comercio tenga derecho o capacidad técnica para recibirlo. El dato sólo se registra si lo entrega un canal autorizado y es necesario para la conciliación; no se utiliza como CRM por defecto.

**Tarjeta / PCI**
- No almacenar PAN completo, banda/track, PIN/PIN block ni CVV/CVC. PCI SSC prohíbe conservar datos sensibles de autenticación después de autorizar, incluso cifrados.
- Preferir tokenización/hosted fields del proveedor. Conservar como máximo los metadatos de conciliación permitidos (por ejemplo marca y últimos cuatro dígitos) y referencias/token del proveedor cuando el contrato lo permita. Nunca reconstruir ni pedir al cajero que copie los datos de tarjeta.

## 3. Política de identificación transversal

### Tres capas independientes

1. **Identidad de cliente:** cuenta/Party del negocio, formada por datos provistos directamente por el cliente o una relación comercial válida. Puede tener teléfono o email verificado, identificador de fidelización, CUIT de empresa y contactos autorizados.
2. **Observación de pagador:** datos que el PSP/banco/acquirer proporciona para conciliar una operación. Se conservan con procedencia y finalidad exactas. No pasan automáticamente a la ficha de cliente.
3. **Instrumento o cuenta de pago:** token/card reference/brand/last4 o referencia bancaria/CBU/CVU/alias cuando esté permitido. Pertenece al proveedor y al instrumento, no al cliente comercial.

### Estados para vincular una operación a un cliente

- `unlinked`: no hay una identidad de cliente válida.
- `candidate`: existe una coincidencia técnica que sólo sirve para sugerir una revisión y cuya utilización está permitida por la fuente.
- `confirmed`: la operación se vinculó por una sesión autenticada, identificador de fidelización presentado, confirmación del usuario u otra relación verificada.
- `rejected`: una coincidencia propuesta se descartó.
- `restricted_reconciliation_only`: la fuente entrega datos sólo para conciliación (por ejemplo ciertos campos de pagador de Mercado Pago); esos datos quedan aislados y no se pueden usar para CRM.

No calcular una puntuación de "persona probable" usando el nombre de la tarjeta, últimos cuatro dígitos o nombre del ordenante para fusionar fichas. Los nombres no son únicos; los instrumentos pueden pertenecer a terceros; una empresa puede pagar muchas compras de distintos empleados.

### Cómo reconocer al mismo cliente entre efectivo, tarjeta, QR y transferencia

La clave es asociar la venta a una identidad de cliente **antes o durante la operación**, independientemente del medio de pago:
- código/QR de cliente o fidelización que el comprador presenta;
- teléfono/email verificado mediante un flujo voluntario y breve;
- sesión de usuario de tienda online/WhatsApp vinculada a la cuenta;
- cuenta empresarial/B2B y contacto/orden de compra;
- identificación de cliente ya confirmada por el empleado autorizado para una relación comercial.

Luego, cada componente de pago se vincula a la venta y ésta a la cuenta comercial. Así una misma persona puede pagar hoy en efectivo, mañana con tarjeta y después por QR sin que Rubrova tenga que deducirlo del instrumento.

Cuando una API entrega un dato de pagador que sólo puede usarse para conciliación, no mostrarlo como "posible cliente", no hacer matching contra la ficha CRM y no incorporarlo a campañas. Otros datos podrán usarse para vinculación únicamente si el contrato del proveedor, el propósito informado y la base legal lo permiten; el caso debe documentarse por integración.

La venta de mostrador sigue permitiendo cliente anónimo. El cajero no debe pedir DNI, teléfono o correo para cobrar.

## 4. Esquema canónico de pagos e identidad

Separar las siguientes entidades:

- `PaymentIntent`: intención de cobrar un importe por un checkout/venta.
- `PaymentAttempt`: intento ante un proveedor o terminal; puede ser aprobado, rechazado, cancelado, pendiente o incierto.
- `Payment`: dinero confirmado y asignado a una venta/orden.
- `PaymentAllocation`: distribución de pagos mixtos entre la venta y sus saldos.
- `ProviderOperation`: ID, referencia, order/intent, estado y respuesta del PSP/adquirente.
- `ProviderWebhookEvent`: evento recibido, ID del evento, firma/verificación, fecha y clave idempotente.
- `PaymentSettlement`: lote/liquidación, fecha de liberación, bruto, comisiones, impuestos y neto.
- `PaymentRefund` / `PaymentReversal` / `Chargeback`: efectos posteriores relacionados con la operación original.
- `PayerObservation`: campos de pagador recibidos, su origen, uso permitido, fecha de retención y nivel de sensibilidad.
- `PaymentInstrumentReference`: referencia tokenizada del proveedor; nunca PAN ni CVV.

Campos comunes por intento:
- `provider`, `provider_account_id`, `provider_operation_id`, `provider_order_id`, `external_reference`;
- `payment_method`, `payment_method_type`, `wallet/bank/acquirer/issuer` cuando corresponda;
- `amount`, `currency`, `installments`, `fee`, `net_amount`, `status`, `status_detail`;
- `occurred_at`, `authorized_at`, `captured_at`, `settled_at`, `recorded_at`;
- `branch_id`, `register_id`, `terminal_id`, `cashier_id`, `shift_id`;
- `idempotency_key`, `correlation_id`, `sale_id/order_id`;
- referencias y metadatos no sensibles expuestos por el proveedor.

Los datos crudos de la API se conservan sólo lo necesario para auditoría/conciliación, con filtrado de secretos y datos prohibidos. La transformación normalizada guarda el origen del campo y la versión del adaptador.

## 5. Flujo recomendado por medio

### QR dinámico integrado

1. Rubrova confirma el carrito y crea la venta/checkout pendiente.
2. Genera una referencia externa aleatoria propia, sin DNI, nombre, teléfono ni otros datos personales.
3. Crea una order/QR dinámico con el importe exacto, POS/sucursal y clave idempotente.
4. Muestra QR y espera notificación autenticada; la notificación nunca se acepta sólo por mensaje del navegador.
5. Consulta el estado de la order/payment al proveedor y concilia importe, moneda y referencia.
6. Confirma la venta una sola vez y registra el pago con proveedor/operación.
7. Guarda el detalle de pagador sólo en el propósito autorizado de conciliación. Nunca convierte el nombre/DNI recibido en un perfil CRM cuando el proveedor lo restringe.

### QR estático

El QR estático no crea por sí mismo una correspondencia única entre ticket y pago. Si el proveedor o portal no entrega una referencia explícita, se requiere conciliación por importe/fecha/caja y revisión de excepciones; no asignar automáticamente pagos a ventas cuando existan importes repetidos. Preferir QR dinámico para integrar el POS si el adquirente lo permite.

### Tarjeta presencial / terminal

1. Rubrova envía importe, moneda y referencia idempotente al adaptador terminal.
2. El cliente interactúa con el dispositivo certificado.
3. La terminal devuelve estado y referencias del adquirente.
4. Rubrova confirma según estado definitivo consultado/verificado, nunca por una captura de pantalla o respuesta temporal.
5. Guardar marca, últimos cuatro dígitos y datos de conciliación sólo si se entregan y están permitidos.
6. El titular de tarjeta no se usa para identificar automáticamente al cliente.

### Transferencia manual

Mostrar al cajero una referencia bancaria y permitir importar conciliación desde una API/archivo de extracto cuando exista. No aceptar una captura del comprador como confirmación definitiva. Guardar ordenante y cuenta de origen sólo si el banco/PSP entrega esos datos y la finalidad permitida lo autoriza; ocultar identificadores completos en las pantallas operativas.

### Efectivo y pago mixto

Efectivo registra importe recibido y vuelto en caja. Pago mixto crea un intento/pago por cada medio, cada uno con estado y referencia independiente. La suma de las asignaciones confirmadas debe cerrar el total; un componente pendiente no se muestra como cobrado.

## 6. Proveedores y reutilización evaluados

| Proveedor/proyecto | Evidencia y uso | Decisión para Rubrova |
|---|---|---|
| Mercado Pago QR API | Orders QR estático/dinámico/híbrido, consulta de estado, notificaciones y reintegros; external_reference e idempotencia | Primer adaptador a prototipar si el proveedor de cobro elegido es Mercado Pago. Utilizar SDK oficial Node.js MIT o API documentada; nunca suponer que devuelve identidad CRM |
| Mercado Pago Point | Integración de terminal/pagos presenciales, notificaciones, reportes y referencias | Adaptador aparte del QR; probar dispositivos/firmware y estados reales |
| Payway Online / Decidir | SDK JS oficial público para tokenización web; requiere SDK de backend Java/PHP/.NET/Node. El frontend maneja PAN y CVV para generar token | Reutilizar mediante la integración oficial/servida por proveedor, no hacer que los componentes propios reciban PAN/CVV. El repositorio público no declara licencia; no copiar su código sin autorización |
| Payway QR / Paystore | Portal público lista APIs para QR, pagos de terminal, devoluciones, anulaciones y liquidaciones | Evaluar con credenciales/documentación de comercio. No es un paquete open-source confirmado |
| Getnet Get POS Integrado | Integración por API cloud-to-cloud o SDK local USB/Wi-Fi; retorno del resultado a sistema de gestión; admite desconexión del sistema de gestión para seguir cobrando | Candidato para terminal física. Solicitar SDK, sandbox, modelo de eventos, referencias, cierre de lote y contrato |
| MODO Conexiones | API PCT Online para merchant con consentimiento previo de la entidad/PSP y autenticación mutua TLS | Evaluar si hay una necesidad de integración directa; no asumir acceso abierto a identidad del pagador |
| Fiserv / PosNet / Clover QR | QR con billeteras interoperables; en QR con tarjeta el cliente no necesita entregar datos al comercio | Confirmación de que pagos QR no garantizan identidad del comprador |
| S-Tech | Hardware transaccional, kioscos y soluciones de efectivo/pagos; integración técnica no publicada | Potencial partner/dispositivo, no proveedor de una identidad unificada por defecto |

### Código y licencias

- [Mercado Pago Node.js SDK](https://github.com/mercadopago/sdk-nodejs): repo oficial, licencia MIT, Node.js 18+ según documentación consultada. Se puede evaluar como dependencia para el backend cuando el runtime elegido lo permita.
- [Payway JS SDK](https://github.com/payway-ar/sdk-javascript-ventaonline): es código público para tokenización del front-end, pero el metadata del repositorio indica `license: null` y el árbol público inspeccionado no contiene LICENSE. No se debe copiar, forkear ni modificar como si fuera open source. Puede servir como documentación de integración; usar SDK/API oficial autorizada o pedir licencia explícita.
- Payway enumera SDKs de backend Java, PHP, .NET y Node, pero su repositorio público JS no sustituye a esos componentes.
- MODO y Getnet publican APIs/SDKs comerciales o documentación de integración; eso no significa que el código propietario sea reutilizable.
- Todos los conectores se encapsulan en adaptadores. Nunca duplicar el ledger de pagos/caja del ERP ni meter reglas del proveedor en el POS central.

## 7. Privacidad, PCI y retención

- Datos provistos para conciliación permanecen en el área de conciliación, con acceso restringido y finalidad documentada.
- No almacenar PAN completo, CVV, PIN, PIN block, track ni datos de autenticación sensibles.
- No guardar CBU/CVU/alias completos como identificador de CRM. Si un extracto debe conservarse por conciliación, limitar acceso, redactar valores en logs y definir retención.
- No enviar PII en `external_reference`, descripción de QR, metadata pública o IDs que se expongan al cliente.
- Separar aceptación de tratamiento necesario para la transacción de la autorización de comunicaciones comerciales.
- Registrar fuente, finalidad, fecha, texto/versión de aviso y preferencias de contacto por canal; respetar bajas.
- Aplicar derechos de acceso/rectificación y plazos de retención bajo Ley 25.326 y normas vigentes de AAIP.

## 8. Pruebas de aceptación

- **P61 — Datos de pagador por canal:** probar efectivo, tarjeta presencial, tarjeta web, QR interoperable con transferencia, QR con tarjeta y transferencia bancaria; registrar sólo campos realmente entregados y su procedencia.
- **P62 — Uso restringido de identidad de pago:** si un proveedor limita nombre/documento a conciliación, el sistema impide que el perfil 360, segmentación, búsqueda de clientes y campañas consulten esos campos.
- **P63 — Mismo comprador, métodos distintos:** cliente identificado voluntariamente paga tickets separados en efectivo, tarjeta y QR; todos se asocian a la misma cuenta por su CustomerAccount/loyalty identity, no por PAN/CBU/nombre del pagador. Una tarjeta de un tercero no fusiona clientes.
- **P64 — Aprobación y conciliación idempotente:** QR dinámico, terminal y transferencia; webhook duplicado, timeout, importe incorrecto, pago tardío, reembolso parcial, contracargo y cierre de lote; no hay doble cobro ni confirmación prematura.
- **P65 — Datos PCI y minimización:** verificar por test/inspección que PAN/CVV/PIN no pasan a logs, eventos, base propia, backups ni reportes.
- **P66 — Identidad dudosa y revisión humana:** coincidencia de nombre, teléfono no verificado o instrumento compartido queda sin vínculo o en revisión; no fusiona automáticamente registros.
- **P67 — Integración y recuperación del proveedor:** caída de red, reinicio de POS, consulta de estado tras timeout y restauración; reconciliar el resultado del proveedor antes de reintentar.

## Estado

La arquitectura, investigación y pruebas están especificadas. Aún no se conectó una terminal real ni se recibieron credenciales/sandbox de ningún proveedor. Ningún dato de pagador debe tratarse como identificador universal hasta que exista evidencia contractual y técnica por canal.
