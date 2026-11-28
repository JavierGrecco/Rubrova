# MyCompany 6.2 — mapa de retail, POS, sesiones y devoluciones

**Estado: lectura de las 30 fuentes LSF del dominio retail y de las extensiones Rubrova relacionadas; aceptación de runtime, integración fiscal/hardware y conciliación de caja pendientes.**

El dominio retail integra POS, sesiones, medios de pago, facturas, devoluciones, descuentos, lotes, picking y control de caja. El POS operativo no equivale por sí mismo a un sistema fiscal argentino.

## 1. Inventario de los 30 módulos

| Área | Módulos |
|---|---|
| Raíz y parámetros | `Retail`, `RetailSettings` |
| Tarjetas de descuento | `DiscountCard`, `DiscountCardInvoice`, `DiscountCardPartner` |
| Medios de pago | `PaymentMethod`, `PaymentMethodInitial` |
| Cajas POS y medios de pago por caja | `Pos`, `PosPaymentMethod` |
| Controladores de caja | `CashRegister`, `CashRegisterFiscal` |
| Pantalla POS y búsqueda | `PosDashboard`, `PosDashboardSearch` |
| Interacción táctil y atajos | `PosDashboardTouch`, `PosDashboardHotKey` |
| Cobro y descuentos | `PosDashboardPayment`, `PosDashboardDiscountCard` |
| Efectivo | `PosDashboardCash`, `PosDashboardCashInitial` |
| Pedido y despacho | `PosDashboardOrder`, `PosDashboardShipment` |
| Lotes | `PosDashboardLot` |
| Devoluciones | `PosDashboardReturn`, `PosDashboardReturnPayment`, `PosDashboardReturnLot`, `PosDashboardReturnShipment` |
| Sesiones y conciliación por medio de pago | `Session`, `SessionInvoice`, `SessionPayment`, `SessionShipment` |

La composición principal `Retail` requiere la configuración, POS, sesión, medios de pago, componentes del dashboard y tarjetas de descuento. El catálogo de módulos identifica además extensiones propias Rubrova fuera de la carpeta upstream, entre ellas `RubrovaRetailReturns` y `RubrovaRetailRefundLimits`.

## 2. Caja POS

Fuente: `retail/pos/Pos.lsf`.

La clase `Pos` guarda:
- ID y nombre;
- empresa propia titular;
- asignación opcional a una computadora;
- nombre de controlador/driver a partir de `CashRegister`.

La empresa se propone desde la empresa predeterminada. El POS puede limitarse a determinadas computadoras; el dashboard filtra las cajas asignadas a la computadora actual y, si no hay asignaciones, permite seleccionar entre todas.

`PosPaymentMethod` permite habilitar/deshabilitar medios de pago por caja y asignar una cuenta por medio. La cuenta debe pertenecer a la misma empresa del POS. Además, el módulo incluye una restricción para que la cuenta central de caja no sea la misma que la cuenta asociada al medio de efectivo, evitando confundir cuenta de control y cajón de dinero.

**Pendiente:** revisar todas las configuraciones posibles de POS por empresa/computadora, terminal, depósito, impresora, permisos y manejo de una computadora compartida.

## 3. Sesiones de caja

Fuente: `retail/sessions/Session.lsf`.

La sesión:
- tiene número, hora de apertura, hora de cierre y POS;
- recibe la hora de apertura al crearse;
- se considera abierta cuando tiene hora de apertura y no tiene hora de cierre;
- no puede cerrarse antes de su apertura;
- permite un único turno abierto por caja;
- ofrece puntos de extensión `beforeOpen`, `afterOpen`, `beforeClose` y `afterClose` para integrar acciones adicionales.

Al abrir, se crea una sesión asociada a la caja si no existe otra abierta. Si ya hay una, la operación se bloquea con mensaje. Al cerrar, se registra la fecha/hora y se ejecutan los hooks; si el proceso es cancelado, se conserva el estado previo.

`SessionInvoice` vincula facturas y notas de crédito/devolución con la sesión, copia el tipo de factura y la empresa desde el POS, y calcula:
- total de ventas;
- cantidad de ventas;
- total de devoluciones;
- cantidad de devoluciones;
- neto de sesión = ventas menos devoluciones.

`SessionShipment` añade relación con los despachos generados durante la sesión. `SessionPayment` muestra importes cobrados/devueltos por medio de pago.

**Pendiente:** probar un turno con facturas sin cobrar, pagos parciales, notas canceladas, depósitos/retiros, cambio de día, desconexión, cierre interrumpido y reapertura. También demostrar qué documentos pueden quedar asociados a una sesión cerrada.

## 4. Medios de pago y cobro mixto

Fuente: `retail/payments/PaymentMethod.lsf` y `PosDashboardPayment.lsf`.

Cada medio de pago tiene:
- ID y nombre;
- marca que identifica el medio efectivo;
- tipo de cobro entrante;
- tipo de pago saliente para devoluciones.

En la caja se pueden deshabilitar determinados medios y asociarles cuentas específicas. La cuenta tiene que pertenecer a la empresa del POS.

### 4.1 Pago mixto

La pantalla de cobro permite ingresar montos por medio de pago. Calcula:
- total ingresado;
- monto que falta cobrar;
- vuelto;
- monto total de medios que no son efectivo.

La validación impide confirmar si el pago total es menor que la factura o si los medios no efectivo exceden el importe de la venta. El vuelto se descuenta del medio efectivo, lo que permite que el efectivo supere el total de la venta y sea el único medio que genere cambio.

Al confirmar:
- crea un `IncomingPayment` por cada medio con importe aplicado;
- lo marca como terminado;
- copia empresa, caja/cuenta, cliente y método de pago;
- aplica el monto a la factura mediante el ledger;
- registra la asociación medio de pago ↔ factura ↔ cobro.

Un mismo cobro puede aplicarse parcialmente a más de una factura en el modelo de facturación general; el cálculo de reintegros de Rubrova usa el importe efectivamente imputado a cada factura y no el total bruto de ese cobro.

**Pendiente:** tarjetas, transferencias, QR, terminales/adquirentes, comisiones, propinas, cuotas, pagos mixtos con múltiples medios electrónicos, conciliación bancaria y errores de respuesta del proveedor.

## 5. Depósitos y retiros de efectivo

Fuente: `pos/dashboard/cash/PosDashboardCash.lsf` y `PosDashboardCashInitial.lsf`.

El POS permite:
- depósito de efectivo a la caja;
- retiro de efectivo desde la caja;
- consultar saldo actual de efectivo;
- ver depósitos/retiros asociados a la sesión.

Estas operaciones crean movimientos nativos:
- depósito: `IncomingPayment`;
- retiro: `OutgoingPayment`.

Se marcan como terminados, usan tipos específicos configurados y se relacionan con la caja, la empresa, las cuentas y la sesión. El módulo inicial registra tipos/numeradores para transferencias y depósitos/retiros.

**Pendiente:** validar si cada movimiento requiere contrapartida en caja central, cuenta bancaria u otra caja, si hay límites por operador, y cómo se concilia saldo esperado contra arqueo físico y diferencias.

## 6. Dashboard, búsqueda, touch, atajos y stock

`PosDashboard` integra:
- selección de caja y sesión abierta;
- factura actual y sus líneas;
- total, descuentos e importe a cobrar;
- facturas de la sesión;
- apertura/cierre de turno;
- búsqueda de artículos y modificación de cantidades;
- cobro, efectivo, devoluciones y movimientos.

`PosDashboardSearch` permite buscar por nombre/código/referencia, filtrar artículos ya agregados a la factura y sumar cantidades. La búsqueda crea/selecciona la línea y posiciona el formulario.

`PosDashboardTouch` construye una vista táctil jerárquica de categorías y artículos; permite ocultar categorías/artículos del panel y navegar por niveles. `PosDashboardHotKey` agrega un nombre de atajo configurable al artículo.

`PosDashboardShipment` puede restringir el POS a ubicaciones a las que el usuario tiene acceso y filtrar artículos por disponibilidad.

`PosDashboardLot` extiende el escaneo con lote: identifica lote/código, busca el producto correspondiente, agrega o selecciona línea y asigna cantidad al lote.

**Pendiente:** pruebas con lector físico, cámara, pantallas táctiles, teclado, múltiples ubicaciones, stock reservado/disponible, lotes, productos no inventariables y ventas contra pedido.

## 7. Tarjetas de descuento

Fuentes:
- `retail/discountCards/DiscountCard.lsf`
- `DiscountCardPartner.lsf`
- `DiscountCardInvoice.lsf`
- `PosDashboardDiscountCard.lsf`

Una tarjeta guarda ID, titular, fecha de emisión y fecha de bloqueo. Se puede crear desde la ficha del socio. La factura valida:
- que el titular de la tarjeta sea el cliente de la factura;
- que la tarjeta no esté bloqueada a la fecha del documento.

En el POS se puede ingresar/leer el código de la tarjeta y asociarla a la factura. El escaneo distingue la tarjeta de descuento de un artículo.

**Límite:** la tarjeta identifica al titular y se vincula al documento; el porcentaje/regla de descuento comercial puede venir de otros módulos y no debe inferirse de la mera existencia de tarjeta.

**Pendiente:** tarjetas repetidas, reposición, bloqueo retroactivo, lectura por barcode, beneficios asociados, uso por familiares, límites y auditoría.

## 8. Devoluciones y notas de crédito

Fuente base: `PosDashboardReturn.lsf` y módulos de facturación `CreditNote` / `BillReady`.

La devolución:
- se crea dentro de una sesión POS abierta;
- se vincula a una factura original;
- copia sus líneas, artículos, precios y datos relacionados;
- crea un documento de nota de crédito/devolución;
- puede vincular la entrada de mercadería y su recepción;
- se registra como devolución de la sesión y reduce el neto de ventas.

El retorno físico de mercadería no es el mismo efecto que el reintegro de dinero. Los documentos de devolución, la recepción de inventario y el egreso de efectivo son entidades distintas que deben quedar conciliadas.

### 8.1 Reintegro por medio de pago

`PosDashboardReturnPayment` arma el pago de devolución como `OutgoingPayment` por medio de pago. La extensión de Rubrova:
- identifica la factura original desde la nota de crédito;
- calcula cuánto se cobró efectivamente por cada medio de pago usando imputaciones activas;
- calcula cuánto se reintegró por cada medio;
- calcula el saldo reintegrable por medio;
- impide que el total reintegrado supere lo cobrado originalmente por ese mismo medio.

### 8.2 Cantidades devueltas

`RubrovaRetailReturns` calcula cuánto se devolvió antes del documento actual para cada línea original y limita la cantidad restante. Excluye la nota actual al sumar las devoluciones anteriores, evitando contarse dos veces durante la creación del documento.

### 8.3 Cancelaciones

La extensión señala un riesgo explícito: cancelar la nota de crédito no cancela automáticamente el egreso nativo. El reintegro deja de consumir cupo cuando el pago de salida también queda cancelado.

**Pendiente:** probar devoluciones parciales repetidas, una venta con cobro mixto, reintegro por medio distinto, pagos cancelados, notas canceladas sin cancelar el pago, lotes, stock devuelto y conciliación de caja.

## 9. Controlador de caja y fiscalización

### 9.1 Configuración genérica

`CashRegister` agrega a POS:
- driver/controlador;
- host;
- puerto;
- login;
- contraseña.

La contraseña se representa como campo de tipo secreto en la interfaz, pero falta comprobar cómo se almacena, quién puede leerla, cómo se cifra y si se excluye de logs/backups.

### 9.2 Contrato fiscal abstracto

`CashRegisterFiscal` define hooks abstractos para:
- apertura de turno fiscal;
- cierre de turno fiscal;
- ingreso/egreso de efectivo;
- emisión de comprobante de venta;
- emisión de comprobante de devolución;
- continuación de impresión;
- reporte X.

Los hooks se conectan al ciclo de sesión, cobro, devolución y movimientos de efectivo. También guarda marcas de apertura/cierre fiscal y una acción de refiscalización.

**Conclusión importante:** el módulo base es una interfaz de extensión, no un driver concreto ni una certificación fiscal. No demuestra compatibilidad con controladores homologados, protocolos argentinos, factura electrónica ni ARCA. El driver ruso ATOL aparece en la regionalización correspondiente y no debe considerarse solución argentina.

## 10. Extensiones propias de Rubrova

| Módulo | Función |
|---|---|
| `RubrovaRetailReturns` | Limita la cantidad total devuelta de cada línea original y normaliza el importe del egreso en moneda funcional |
| `RubrovaRetailRefundLimits` | Limita reintegros acumulados por medio de pago al importe efectivamente cobrado originalmente por ese medio |

Estas extensiones deben mantenerse separadas del código upstream y contar con pruebas que protejan los invariantes de devolución. El contrato de `CashRegisterFiscal` sigue siendo nativo/abstracto y no se vuelve concreto por incorporar estos límites.

## 11. Pruebas y conciliación obligatorias

| Escenario | Qué debe conciliarse |
|---|---|
| Venta en efectivo | Factura, cobro, caja, sesión y ledger |
| Venta con dos medios | Importe aplicado a cada medio, vuelto y saldo |
| Venta con pago electrónico | Medio, cuenta, respuesta del proveedor y conciliación bancaria |
| Depósito/retiro | Pago entrante/saliente, caja POS, cuenta central y sesión |
| Cierre de turno | Ventas, devoluciones, pagos, depósitos, retiros y saldo esperado |
| Devolución parcial | Cantidad original, devolución acumulada, nota, recepción y stock |
| Reintegro mixto | Importe cobrado/reintegrado por cada medio y saldo disponible |
| Nota cancelada | Estado de nota y estado del egreso; evitar reintegros huérfanos |
| Fiscalización | Apertura/cierre, tickets, X-report, errores de hardware, reintentos e idempotencia |
| Desconexión | Sesión, factura, pago, impresión y recuperación del estado |

## 12. Estado

Las 30 fuentes retail fueron inventariadas. La lectura de fuente identifica la caja, sesión, medios de pago, pagos mixtos, efectivo, dashboard, búsqueda, touch, atajos, stock, lotes, tarjetas, devolución, conciliación por medio y contrato fiscal abstracto. También se identificaron dos extensiones Rubrova para límites de cantidad y reintegro.

**No está aceptado:** falta ejecutar los escenarios en runtime, verificar hardware y servicios, conciliar sesiones/cuentas/inventario y validar fiscalidad argentina. La puerta general de relevamiento sigue ABIERTA.
