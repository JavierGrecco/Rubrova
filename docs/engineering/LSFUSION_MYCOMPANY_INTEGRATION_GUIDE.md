# Guía de integración lsFusion 6.2 + MyCompany 6.2

**Estado:** investigación de fuentes fijadas; mapa inicial contrastado con el código incluido en Rubrova.  
**Corte de código:** Rubrova main d9791ff1c7894346d31ea5e0d240077940ba788c.  
**Fuentes upstream:** lsFusion 6.2 dd4dbe5bf9b136e73e18fe25d741253929324350; MyCompany 6.2 d21ca6978717b98b6300d90267f9767db7414008.  
**Alcance:** arquitectura, contratos de módulos, extensión, transacciones, integración externa y circuitos POS/ventas, devoluciones, pagos, caja e inventario. No constituye aceptación productiva.

> Regla de precedencia: para saber qué hace la instalación Rubrova, prevalecen las fuentes 6.2 vendorizadas, sus parches explícitos y los tests sobre esa misma revisión. La documentación pública explica conceptos y escenarios, pero no sustituye la inspección del código exacto. El portal MyCompany v6 identifica su manual como 6.0 y parte de la documentación actual está en 7.0; se usa como apoyo conceptual, no para asumir compatibilidad sin verificar.

## 1. Conclusión arquitectónica

Rubrova parte de una aplicación ERP/POS integrada construida sobre lsFusion. Sus módulos LSF no son microservicios independientes: se cargan en una misma instancia lógica, participan de un mismo modelo de clases/propiedades/acciones y trabajan sobre la persistencia configurada para esa instancia.

La composición actual es:

- **vendor/platform/**: motor, servidor, API y clientes lsFusion 6.2.
- **vendor/mycompany/**: módulos de negocio MyCompany 6.2.
- **extensions/lsfusion/**: módulos Rubrova que dependen del modelo nativo.
- **patches/lsfusion/**: cambios puntuales al motor, sólo si una extensión LSF no alcanza.
- **build/rubrova/pom.xml**: reactor de compilación propio.

El módulo de entrada es **RubrovaCustom** (extensions/lsfusion/RubrovaCustom.lsf). Este requiere **MyCompany** y las extensiones Rubrova. A su vez, MyCompany declara el agregado de módulos de Inventario, Invoicing, Purchase, Sales, Retail, Manufacturing, Project Management, CRM, RR. HH., Fleet y otros.

Esto define dos clases de comunicación que no deben confundirse:

1. **Dentro de la aplicación lsFusion:** dependencia de módulos, propiedades tipadas, acciones, eventos, restricciones y puntos de extensión. No corresponde llamar por HTTP a un módulo vecino que ya reside en la misma instancia.
2. **Fuera de esa instancia:** Action API HTTP, exportaciones de datos, llamadas EXTERNAL, webhooks, dispositivos o procesos independientes. Aquí sí hacen falta esquemas versionados, autenticación, timeouts, idempotencia y conciliación.

Una función sólo debe convertirse en servicio separado si tiene una frontera útil y demostrable: dueño de datos, almacenamiento, contrato, ciclo de despliegue, migraciones, backup/restauración, observabilidad y pruebas independientes. Separar módulos LSF por carpetas no los convierte en microservicios.

## 2. Versiones, procedencia y reproducibilidad

La fuente de verdad está en:

- platform/source-lock.json
- platform/mycompany-6.2.lock.json
- vendor/platform/.rubrova-source.json
- vendor/mycompany/.rubrova-source.json
- vendor/UPSTREAM_SOURCES.md

| Componente | Tag fijado | Commit | Licencia | Ruta |
|---|---|---|---|---|
| lsFusion platform | 6.2 | dd4dbe5bf9b136e73e18fe25d741253929324350 | LGPL-3.0 | vendor/platform/ |
| MyCompany | 6.2 | d21ca6978717b98b6300d90267f9767db7414008 | Apache-2.0 | vendor/mycompany/ |

Estas carpetas son snapshots completos versionados dentro del repo, no submódulos ni referencias flotantes. No deben reemplazarse por latest, una rama remota o un JAR que oculte el origen. Las actualizaciones se preparan en un área temporal, se comparan archivo por archivo, se revisan licencias/dependencias, se registra el nuevo commit y se ejecuta la matriz completa antes de adoptarlas.

## 3. Cómo funciona la composición de módulos

### 3.1 El contrato del encabezado

Un módulo LSF se declara, por ejemplo:

~~~text
MODULE RubrovaFeature;
REQUIRE MyCompany, AnotherBaseModule;
NAMESPACE Rubrova;
~~~

- **MODULE** identifica una unidad lógica de código; su nombre debe ser único.
- **REQUIRE** declara dependencias y fija el orden de inicialización: los módulos requeridos se inicializan antes. No se permiten ciclos.
- **NAMESPACE** determina dónde se crean/resuelven los elementos declarados. Los módulos existentes usan namespaces como Retail, Invoicing, Inventory y Sales.

Por tanto, REQUIRE MyCompany no significa que Rubrova se conecte a un servicio remoto. Significa que el módulo consume los elementos de MyCompany dentro de la misma composición.

La cadena de dependencias debe ser intencional. Una extensión no debe depender de módulos de presentación sólo para alcanzar una entidad de dominio; siempre que sea posible debe depender del módulo que declara el contrato de negocio.

### 3.2 Elementos que forman el contrato

| Elemento | Significado operativo | Uso recomendado |
|---|---|---|
| CLASS | Tipo de objeto del dominio | Crear una clase propia sólo cuando no exista una clase nativa equivalente |
| DATA | Propiedad asociada a clases/objetos, persistente salvo variantes locales | Guardar datos propios o relaciones |
| Propiedad calculada | Expresión declarativa sobre objetos/propiedades | Consultas, saldos, derivaciones y reglas |
| ABSTRACT de propiedad | Contrato para añadir implementaciones | Desacoplar una fórmula base de módulos consumidores |
| Acción | Cambio de estado / ejecución imperativa | Casos de uso y comandos |
| ABSTRACT LIST | Punto de extensión donde pueden agregarse acciones compatibles | Enriquecer un flujo upstream sin modificar su acción concreta |
| WHEN / eventos | Reacción a cambios conforme a los operadores de sesión | Automatismos con momento y orden conocidos |
| CONSTRAINT | Invariante que debe respetarse al validar/aplicar | Proteger dinero, cantidad, relaciones y estados |
| EXTEND FORM / DESIGN | Extensión de interfaz | Presentar comportamiento de dominio, no alojar la regla crítica |

### 3.3 Cómo extender correctamente

Patrones observados en MyCompany 6.2:

**Propiedad abstracta:** se declara el contrato en el módulo base y se añaden fórmulas compatibles desde módulos dependientes mediante +=. Las clases y parámetros de las implementaciones deben coincidir con el contrato. No sobrescribir silenciosamente una propiedad concreta esperando que el comportamiento se acumule.

**Acción abstracta:** el módulo base declara un punto extensible, por ejemplo:

~~~text
fill ABSTRACT LIST (BillLine, InvoiceLine);
~~~

Un módulo dependiente agrega una implementación compatible:

~~~text
fill (BillLine line, InvoiceLine sourceLine) + {
    // completar sólo los datos que pertenecen a esta extensión
}
~~~

Para una acción abstracta el operador es ACTION+ / +, no += (que es la forma usada para extender propiedades).

**Acción concreta:** una acción con cuerpo, como CreditNote.create(Bill, Invoice), no se convierte automáticamente en un punto de extensión. No intentar create(...) + si el código upstream no la declaró abstracta. Buscar en orden: punto abstracto existente; evento o propiedad soportados; extensión pública de clase; y sólo como último recurso un parche aislado y versionado al código upstream.

**Extensión de formularios:** EXTEND FORM y DESIGN permiten sumar objetos, propiedades, eventos visuales y disposición. Son contratos sensibles a la estructura de la pantalla base: si upstream renombra o reubica objetos, filtros o grupos, la extensión puede dejar de compilar o comportarse distinto. Toda extensión de interfaz debe acompañarse de una prueba de carga y navegación en la pantalla real.

Ejemplos nativos para estudiar:

- CreditNote.lsf: fill(BillLine, InvoiceLine) y fill(Bill, Invoice).
- CreditNoteContract.lsf: copia la relación contractual en fill(Bill, Invoice).
- CreditNoteReceipt.lsf: copia la ubicación en el mismo punto de extensión.
- InvoiceShipment.lsf: expone puntos fill para Shipment/Invoice y líneas.
- Session.lsf: beforeOpen, afterOpen, beforeClose, afterClose.
- PosDashboard.lsf: afterCreateInvoice y processBarCode.
- PosDashboardPayment.lsf: afterPosPayment(Invoice).
- PosDashboardReturnPayment.lsf: afterPosPayment(Bill).

No todo punto abstracto es un hook de ejecución equivalente: revisar el tipo (LIST, MULTI, CASE, etc.), firma, orden y condiciones de selección antes de implementarlo.

## 4. Modelo de ejecución y transacciones

### 4.1 Separación entre consulta y comando

La lógica de lsFusion combina propiedades declarativas (valores consultables/derivados) con acciones imperativas (cambios de estado). Para mantener reglas consistentes:

- usar propiedades para expresar cálculos y relaciones;
- usar acciones para coordinar comandos y cambios;
- usar constraints para invariantes que deban bloquear el APPLY;
- evitar recalcular en la interfaz algo que ya tiene una propiedad de dominio autoritativa.

Una propiedad DATA LOCAL no es un registro durable. Es temporal y pertenece al contexto/sesión de ejecución. Los operadores de manejo de sesión pueden resetear propiedades locales; si deben sobrevivir a una sesión anidada o a un APPLY, hay que declarar/solicitar la semántica de anidamiento correspondiente.

### 4.2 APPLY, CANCEL, NEWSESSION y NESTEDSESSION

- **APPLY** intenta aplicar los cambios como una transacción atómica: valida constraints, procesa eventos globales síncronos, actualiza materializaciones y persiste. Si falla la validación o la base de datos, se revierte.
- **CANCEL** cancela los cambios del ciclo correspondiente; no debe confundirse con cancelar un documento ya contabilizado.
- **NEWSESSION** crea un ciclo/sesión de cambios separado; las propiedades locales normalmente se reinician.
- **NESTEDSESSION** permite trabajar sobre cambios locales anidados y devolverlos a la sesión padre. Un APPLY dentro de esa sesión puede copiar cambios al padre sin persistir todavía en la base.

El patrón común de MyCompany es APPLY, comprobar canceled(), y después entrar a NEWSESSION para completar otra etapa. No copiarlo mecánicamente: entender qué se ha confirmado y qué sigue siendo reversible en cada punto.

**Regla crítica:** la acción aplicada dentro de APPLY puede ejecutarse más de una vez si la transacción se reintenta por conflicto, deadlock o timeout. No enviar un cobro, emitir un documento fiscal, imprimir un ticket no repetible ni llamar a un proveedor externo como efecto irreversible dentro de esa transacción. En su lugar:

1. crear/persistir una intención con ID e idempotencia;
2. confirmar localmente el estado pendiente;
3. ejecutar el adaptador externo fuera de la transacción crítica;
4. guardar respuesta/evento y correlación;
5. conciliar el resultado antes de crear el siguiente efecto contable.

Para pagos o emisión fiscal, la respuesta incierta no significa rechazo: puede haberse confirmado en el proveedor aunque se pierda la respuesta. Consultar por la referencia/idempotency key antes de reintentar.

### 4.3 WHEN y eventos

Las expresiones WHEN, ON CHANGE, ON INIT y los eventos locales/globales no son todos equivalentes. Su momento de ejecución depende de la clase de evento y del ciclo de sesión. Un cambio a una propiedad no significa que todas las reacciones globales ya se hayan aplicado. El APPLY procesa los eventos globales síncronos y las restricciones dentro de la transacción.

Los handlers que pueden ejecutarse más de una vez deben ser deterministas e idempotentes. No usar eventos declarativos como sustituto de una llamada externa transaccionalmente segura ni para un efecto físico irreversible.

## 5. Comunicación con sistemas externos

### 5.1 Entrada a lsFusion

La Action API expone acciones concretas por HTTP (por ejemplo /exec), con parámetros y, cuando se configura, propiedades de resultado. lsFusion distingue EXEC, EVAL y EVAL ACTION.

Norma Rubrova:

- exponer acciones nominales específicas con @@api;
- mantener enableAPI=0 y autenticación obligatoria;
- no habilitar @@noauth;
- no habilitar evaluación arbitraria (/eval, /eval/action) para integraciones ordinarias;
- dentro de cada acción comprobar permisos/rol y validar los argumentos; @@api no es por sí mismo una autorización granular por usuario;
- publicar un esquema de respuesta versionado, no el modelo físico completo.

El endpoint de integración debe indicar schemaVersion, unidades, precisión, fecha de corte, significado de NULL, cero, ausencia y listas vacías, errores y semántica de reintentos. Un HTTP 200 no prueba que el JSON sea válido ni completo.

Precaución de v6: una respuesta JSON formada sólo por propiedades NULL o sin registros puede resultar en un valor JSON nulo/cuerpo vacío. No inferir que equivale a []. Cuando un consumidor necesite representar listas vacías, incluir contadores explícitos y probar el cuerpo HTTP real.

### 5.2 Salida desde lsFusion

El operador EXTERNAL permite que la instancia haga llamadas a otro sistema, entre ellas HTTP GET/POST/PUT/PATCH/DELETE. Por defecto la llamada se realiza desde el servidor de aplicaciones; la ejecución en cliente cambia la conectividad y limitaciones.

- cada llamada debe usar timeout finito;
- no reenviar credenciales en logs ni guardar cuerpos sensibles;
- distinguir timeout, error HTTP, autenticación, autorización, conflicto y respuesta inválida;
- reintentar sólo cuando el método/operación y el proveedor permiten hacerlo con seguridad;
- un GET de lectura no equivale a un POST de cobro;
- guardar referencia local, referencia remota opaca e ID de correlación;
- validar firma de webhooks y deduplicar eventos de proveedor.

RubrovaIntegrationResilience ya persiste incidencias, clasifica HTTP y aplica un máximo de 30 segundos a su helper GET; no reintenta automáticamente y no implementa todavía un cliente HTTP genérico para POST/PUT/DELETE. RubrovaPaymentTerminals define el modelo persistente y las pantallas de configuración/trazabilidad de cuentas, terminales, asignaciones, intenciones, intentos, eventos, reintegros y liquidaciones. **Es infraestructura de dominio preparada, no una integración operativa:** el módulo no contiene aún la acción que inicia un cobro real ni la recepción/validación de webhooks o el protocolo del puente local. En todos los casos, estos datos auxiliares no deben convertirse en un segundo ledger contable.

### 5.3 Frontera de autoridad

Un módulo de adaptación es dueño de la conversación con el proveedor (credenciales, correlación, reintentos, payload normalizado y reconciliación). No es dueño de la venta, el dinero en caja o el stock nativo.

Ejemplo: una intención de cobro puede referenciar Invoice, Retail.Pos y Retail.PaymentMethod; el resultado confirmado se registra como Invoicing.IncomingPayment. La referencia del proveedor y la conciliación pertenecen a Rubrova; el movimiento financiero oficial pertenece a MyCompany.

### 5.4 Estado real de terminales y próximos contratos

La revisión de extensions/lsfusion/RubrovaPaymentTerminals.lsf confirma que actualmente están modeladas las entidades:

- PaymentProviderAccount: proveedor, ambiente, referencia de comercio y referencia al secreto del sistema. No guarda el secreto en claro.
- PaymentTerminal y PaymentTerminalAssignment: terminal, transporte, bridge host/port y asociación a caja y medio de pago.
- PaymentTerminalIntent y PaymentTerminalAttempt: factura/caja/medio, importe, moneda, estado, referencias locales/remotas y claves de idempotencia.
- PaymentProviderEvent: clave de evento, tipo, operación, intento, verificación de firma y estado de procesamiento. No se persiste el cuerpo HTTP completo.
- PaymentRefund: relación con intento original, Bill y OutgoingPayment.
- PaymentSettlement y PaymentSettlementLine: bruto, comisiones, impuestos/retenciones, neto y conciliación con IncomingPayment.

El archivo implementa clases, datos, relaciones y formularios de consulta/configuración. No implementa aún el protocolo de cobro contra una terminal, el HTTP POST del proveedor, el worker local, el receptor de webhooks ni las transiciones operativas de los estados. El documento de instalación del runtime ya describe esta pieza como base de configuración y trazabilidad y aclara que todavía no ejecuta cobros reales. La ausencia de acciones EXTERNAL HTTP POST en el código LSF inspeccionado confirma que no se debe vender como integración de terminal terminada.

RubrovaIntegrationResilience:

- Persiste IntegrationIncident en una sesión independiente (NEWSESSION/APPLY); si falla la base principal, intenta un log local de emergencia.
- Clasifica 429, 408/425, 5xx, 401, 403, 409 y fallos de red/timeout.
- Su helper rubrovaHttpGet ejecuta EXTERNAL HTTP GET, tiene timeout configurable de 1 a 30.000 ms, y devuelve estado/categoría para que el llamador decida.
- No reintenta por sí mismo, no expone un cliente HTTP genérico POST/PUT/DELETE y el helper no demuestra todavía firma/verificación de webhooks ni protocolo de terminal local.
- La respuesta, URL completa, cabeceras sensibles y excepción cruda no se persisten en la incidencia.

**Contrato pendiente antes de una integración real:**

1. Definir adapter por proveedor/terminal con operaciones Create/Charge, QueryStatus, Cancel y Refund, más el protocolo de puente local cuando corresponda.
2. Congelar una intención de cobro ligada a una Invoice exacta, caja, medio, moneda e importe; una venta editada debe invalidar o expirar la intención anterior.
3. Derivar una clave estable por intención. Cada reintento de la misma operación remota debe reutilizar la misma clave; una nueva operación comercial recibe otra clave.
4. Distinguir estados terminales confirmados de respuestas inciertas. Timeout después de enviar el cobro significa resultado desconocido y requiere conciliación, no rechazo. Consultar por referencia antes de reintentar.
5. Verificar firma/autenticidad del evento, deduplicar por clave de evento de manera durable y relacionarlo con PaymentTerminalAttempt. Manejar eventos tardíos y fuera de orden.
6. Sólo después de confirmar el cobro, registrar el movimiento autoritativo como Invoicing.IncomingPayment; la intención y el intento no son dinero contabilizado.
7. Conciliar bruto, comisión, impuestos/retenciones y neto en PaymentSettlement/PaymentSettlementLine con el cobro nativo. Las comisiones no deben reducir silenciosamente el total de venta ni duplicarse como egreso.
8. Para un reintegro, enlazar PaymentRefund con el Bill y el OutgoingPayment; distinguir pedido al proveedor, confirmado, rechazado y desconocido. No registrar como reintegrado un importe que sólo fue solicitado.
9. El adaptador debe fallar de manera aislada: efectivo y otras funciones locales siguen operativas aunque el proveedor o el puente estén desconectados.
10. Validar con simulador determinista y luego hardware real: desconexión antes/después de enviar; respuesta perdida; doble click; webhook duplicado/tardío/firma inválida; reinicio; pago parcial; cancelación; reintegro; liquidación con comisión; conciliación tras recuperar red.

El modo offline local no implica que una terminal bancaria o un QR puedan autorizar un pago sin conectividad. Debe preservarse la venta local en efectivo y dejar explícitamente pendiente cualquier método que requiera el proveedor, según las capacidades reales del dispositivo y adquirente. No inventar un pago aprobado offline.

## 6. Mapa de dominios y circuitos comprobados en MyCompany 6.2

### 6.1 Composición superior

MyCompany.lsf incluye como mínimo estos dominios: MasterDataP, Inventory, Invoicing, InvoicingInventory, Purchase, Sales, Retail, Manufacturing, ProjectManagement, HumanResources, CRM y Fleet.

El hecho de que estén incluidos no significa que todas sus opciones estén activadas ni que todos los circuitos se hayan probado en Rubrova. Esta guía profundiza en el núcleo POS, pagos, caja, stock y devoluciones. Compras, mayorista, fabricación, fiscalidad, CRM y demás módulos requieren mapas de uso específicos antes de extenderlos.

### 6.2 Venta POS: de la caja al ledger físico

~~~text
Retail.Pos
  └─ Retail.Session (apertura de turno)
       └─ Invoicing.Invoice
            ├─ Invoicing.InvoiceLine
            └─ Invoicing.IncomingPayment (uno por medio de pago)
                  └─ Invoicing.Payment / saldo de cuenta
       └─ Invoicing.InvoiceShipment
            └─ Inventory.Shipment
                 └─ Inventory.ShipmentLine
                      └─ Inventory.ShipmentInvLedger
                           └─ Inventory.InvLedger / onHand
~~~

Contratos observados:

1. Pos es el objeto de caja. Guarda empresa y asignación a equipo; no es necesario crear una caja espejo para relacionarla con el turno.
2. Session representa el período operativo. Tiene apertura, cierre, caja y propiedades agregadas. openedSession(Pos) selecciona el turno abierto por caja.
3. PosDashboard crea la factura actual asociada al turno y llama al punto abstracto afterCreateInvoice.
4. PosDashboardPayment toma importes por PaymentMethod. Crea un IncomingPayment por cada importe, configura tipo, empresa, cuenta, cliente y factura, lo marca done, marca la factura ready, ejecuta APPLY y después afterPosPayment.
5. PaymentMethod asocia los tipos de ingreso/egreso que debe utilizar. PosPaymentMethod define medios habilitados por POS y cuentas financieras.
6. En MyCompany 6.2, InvoiceShipmentInitial configura el tipo retail con tipo de despacho y autoCreateShipment=true.
7. Cuando la factura minorista queda ready, InvoiceShipment crea automáticamente un Shipment. Si el despacho no es planificado, lo marca inmediato y completo; las líneas toman las cantidades vendidas.
8. ShipmentInvLedger transforma la diferencia entre cantidad efectuada y cantidad ya llevada al ledger en movimientos físicos. El ledger usa la condición active(shipment).

Así, el efecto de stock no es una resta improvisada en la pantalla del POS. Es un movimiento enlazado a la factura y al despacho.

### 6.3 Devolución POS: documento, reintegro y stock

~~~text
Invoice original
  └─ CreditNote.create(Bill, Invoice)
       ├─ Bill / BillLine
       │    └─ invoiceLine(BillLine) → InvoiceLine original
       ├─ OutgoingPayment (por medio de devolución)
       └─ autoCreateReceipt(retailreturn)
            └─ Inventory.Receipt / ReceiptLine
                 └─ Inventory.ReceiptInvLedger
                      └─ InvLedger / onHand
~~~

Contratos observados:

- CreditNote.create(Bill, Invoice) es una acción concreta. Copia tipo, cliente/proveedor, cuentas, empresa, nota, producto, cantidad y relación con la línea original. Por cada línea llama a fill(BillLine, InvoiceLine) y luego llama a fill(Bill, Invoice).
- La relación BillLine → InvoiceLine no es opcional: preserva la procedencia del artículo y permite calcular lo ya devuelto.
- MyCompany valida que la contraparte y el producto de la devolución coincidan con la factura original.
- returned(InvoiceLine) suma cantidades de BillLine de devoluciones activas vinculadas a esa línea.
- La constraint que impide superar la cantidad original sólo se aplica cuando checkReturnedQuantity(type(invoiceLine)) está habilitado.
- CreditNoteInitial asocia retailreturn con el tipo de factura retail; CreditNoteReceiptInitial mapea ese tipo a una recepción de devolución y activa autoCreateReceipt(retailreturn).
- PosDashboardReturnPayment crea documentos OutgoingPayment, los relaciona con Bill y medio de pago, y marca la devolución ready.
- BillReceipt crea una Receipt automáticamente al quedar lista una Bill cuyo tipo tiene autoCreateReceipt; el documento y líneas de recepción se crean completos. ReceiptInvLedger transforma la cantidad completada en entrada física.
- La cantidad física devuelta se acredita a través del ledger de Receipt; no se debe volver a sumar manualmente al stock en un módulo Rubrova.

**Límite funcional relevante:** el formulario nativo limita el importe por medio de pago al importe originalmente pagado con ese medio en la factura, y exige que la suma reintegrada sea igual al importe de la nota. Sin embargo, consulta la factura original y no resta lo reintegrado en devoluciones anteriores. Por tanto, el límite es por cada devolución, no acumulativo para varias devoluciones parciales. Hay que agregar una protección acumulativa Rubrova antes de aceptar ese circuito para operación real.

**Límite técnico:** las devoluciones parciales deben ajustar la línea copiada usando el punto abstracto CreditNote.fill(BillLine, InvoiceLine) antes de completar el documento. No crear una segunda nota de crédito independiente ni modificar manualmente las líneas ya confirmadas. La extensión Rubrova de ese flujo está propuesta en PR #13 y debe superar el smoke funcional completo antes de integrarse a main.

### 6.4 Caja: pagos, cuentas y turno

MyCompany usa una clase financiera común Invoicing.Payment:

- IncomingPayment contribuye con importe positivo a signedAmount.
- OutgoingPayment contribuye con importe negativo.
- Payment.balance(Account) agrega movimientos activos por cuenta; cashBalance(Company) agrega saldos de cuentas de caja.
- Retail.PaymentMethod vincula medios a tipos de ingreso/egreso.
- Retail.PosPaymentMethod vincula cada medio con una cuenta y define cashAccount(Pos) a partir del medio marcado como efectivo.
- Retail.cashBalance(Pos) consulta el saldo de la cuenta de caja de ese POS.
- Los depósitos/retiros del POS crean documentos de ingreso/egreso separados y los relacionan con la sesión. No son una venta ni una devolución.
- SessionPayment calcula lo pagado por medio como cobros de facturas menos egresos de devoluciones para esa sesión.

No confundir:

| Medida | Qué representa |
|---|---|
| Total de ventas | Importe de facturas del turno |
| Total de devoluciones | Importe de notas de crédito del turno |
| Neto comercial del turno | Ventas menos devoluciones |
| Neto por medio | Cobros asociados a ventas menos reintegros asociados a devoluciones |
| Saldo de la cuenta de caja | Ledger de pagos activos de esa cuenta, que también puede incluir depósitos y retiros |
| Arqueo físico | Conteo real de billetes/monedas; no se obtiene automáticamente del ledger |

El modelo de sesión no equivale a un arqueo físico. Diferencias entre efectivo teórico y contado deben tener un documento/registro, motivo, operador, hora y auditoría; no se deben corregir sobrescribiendo el saldo financiero.

Session expone beforeOpen, afterOpen, beforeClose y afterClose. El método habitual openSession(Pos) evita abrir un segundo turno abierto para la misma caja. La lista de sesiones también permite operaciones manuales NEW/EDIT/DELETE: esas operaciones no deben tratarse como equivalentes al caso de uso normal de abrir desde el POS, porque no ejecutan las mismas comprobaciones.

### 6.5 Inventario: físico, reservas y disponible

El ledger físico de MyCompany se construye así:

- InvLedger.quantity es una cantidad abstracta que implementan movimientos concretos.
- inQuantity(location, product) suma movimientos activos y aceptados hacia la ubicación.
- outQuantity(location, product) suma movimientos activos desde la ubicación.
- onHand(location, product) = inQuantity - outQuantity.

Las reservas viven en un modelo separado:

- ResLedger.reserved es el valor firmado del movimiento de reserva.
- Las cantidades positivas representan unidades reservadas.
- Las cantidades negativas representan entradas esperadas.
- planned considera las reservas que no están excluidas (skipAvailable).
- available(location, product) = onHand - planned.

En consecuencia:

- onHand es la existencia física/contable derivada de movimientos ya ejecutados.
- available es lo que queda utilizable después de los compromisos que MyCompany descuenta.
- expected y reserved son componentes de la planificación y no son sinónimos del saldo físico.
- una reserva de despacho no debe restar del ledger físico antes de completar el movimiento;
- una recepción prevista no incrementa necesariamente el disponible hasta que se cumplen los estados/configuraciones de recepción.

InvLedgerAPI.getInventory exporta onHand, no el disponible completo. Para consumir disponible, Rubrova debe usar una propiedad/acción que lo exponga expresamente o derivar el cálculo a partir de componentes compatibles y conciliados; no renombrar onHand como available.

### 6.6 Estados documentales: no inferir semántica desde el nombre

En el código inspeccionado, active se define de forma distinta según el documento:

| Tipo | Expresión observada | Qué habilita |
|---|---|---|
| Invoice | ready AND NOT canceled | Participar como factura activa en los ledgers que la consultan |
| Bill | ready AND NOT canceled | Participar como devolución/factura de proveedor activa |
| IncomingPayment | done AND NOT canceled | Participar en el saldo financiero |
| OutgoingPayment | (ready OR done) AND NOT canceled | Participar en el saldo financiero |
| Shipment | done AND NOT canceled | Participar en el ledger físico de salida |
| Receipt | done AND NOT canceled | Participar en el ledger físico de entrada |

ready y done son propiedades separadas y su significado varía según el módulo. No diseñar código Rubrova que concluya contabilizado, pagado o stock movido sólo por la presencia del documento o por un estado visual. Seguir exactamente la expresión active(...) que consume el ledger que interesa.

### 6.7 Compras y recepción: procure-to-pay

~~~text
Purchase.Order / OrderLine
  └─ confirm Order
       └─ Inventory.Receipt (ready; expected inbound)
            └─ ReceiptLine (initialDemand = residual ordered quantity)
                 ├─ ReceiptResLedger (negative reservation / expected)
                 └─ mark Receipt done
                      └─ ReceiptInvLedger (positive physical stock)
       └─ Invoicing.Bill / BillLine
            └─ Invoicing.BillDebt (supplier liability)
                 └─ OutgoingPayment (supplier payment)
                      └─ Payment / account ledger
~~~

**Confirmación y recepción:**

- Purchase.Order pertenece al namespace Purchase; contiene vendor, company, location, currency, payment terms, representative, lines, quantity y price.
- PurchaseOrderConfirmed.confirm(Order) cambia el pedido a confirmed dentro de una sesión nueva y APPLY.
- PurchaseOrderReceipt relaciona Order/OrderLine con Receipt/ReceiptLine. Calcula recibido como suma de done(ReceiptLine) para recepciones activas y toReceive = ordered - received.
- Cuando el pedido está confirmado, tiene ubicación y su tipo tiene receiptType, el automatismo crea o reutiliza una recepción ready, añade líneas con el remanente toReceive y actualiza sus cantidades previstas. Esto no significa que la mercadería ya haya ingresado físicamente.
- La constraint impide recibir por encima de la cantidad pedida. Varias recepciones parciales se suman por la referencia a la línea de orden original.
- ReceiptResLedger registra reservas esperadas con signo negativo mientras la recepción está ready y no done. La opción increaseAvailableStock(ReceiptType) determina si la recepción esperada se descuenta o no del disponible. No asumir que toda compra confirmada incrementa el stock vendible.
- Al completar la recepción, ReceiptInvLedger crea la entrada física; la existencia pasa a onHand a través del ledger, no por el estado de la orden de compra.
- La recepción enlazada conserva proveedor, ubicación, orden y línea original. La configuración del tipo de orden puede impedir bloquear pedidos con recepciones activas o con faltantes pendientes.

**Costo de mercadería:**

- PurchaseOrderReceiptCost aporta costo de ReceiptLine desde el precio de la línea de orden y la cantidad recibida, ajustada por el coeficiente SKU.
- Es una fuente para enlazar el costo de compra con el movimiento físico, pero no basta por sí sola para aceptar toda la valoración de inventario: todavía hay que mapear lotes, diferencias de precio, moneda, impuestos, ajustes posteriores y política de costo efectiva del resto de módulos.

### 6.8 Factura de proveedor y pago

- PurchaseOrderBill relaciona Order/OrderLine con Bill/BillLine.
- La política InvoicingPolicy.ordered permite facturar el remanente de cantidad pedida que todavía no aparece facturado. La cantidad facturada se calcula desde BillLine de Bills ready y no canceladas.
- La extensión PurchaseOrderBillReceipt añade la política delivered: sólo habilita cantidades de ReceiptLine activas, completadas (done > 0) y todavía no asociadas a una BillLine. Al crear la Bill, copia las cantidades efectivamente recibidas y mantiene los enlaces a la línea original de compra y a la recepción.
- Por ello, pedido, recepción y factura son documentos relacionados pero distintos. Facturar una cantidad no es prueba de que se haya recibido; recibir una cantidad no es prueba de que el proveedor ya haya sido pagado.
- **Precaución de lectura:** en PurchaseOrderBill, la propiedad de línea llamada paid agrega quantity(BillLine) para Bills done. Es una medida basada en estado/cantidad de documento, no un monto monetario liquidado al proveedor. No reutilizarla como importe de caja ni saldo de deuda.
- BillDebt integra Bill al modelo de deuda como IncomingDebt. OutgoingPaymentDebt integra OutgoingPayment como OutgoingDebt; sus acciones de matching relacionan obligaciones y pagos mediante importes pagados y pendientes.
- BillPayment.registerPayment crea un OutgoingPayment vinculado al proveedor, sus cuentas, empresa, moneda y Bill; propone el saldo pendiente y permite registrar el pago. Al completar la conciliación configurada, BillDebt puede cambiar el estado de la Bill a done. Las cuentas y los saldos financieros continúan siendo propiedad del ledger común Payment.

**Invariantes que Rubrova debe preservar:** límite de recibido <= pedido; límite de facturado según la política (pedido o recibido); la misma cantidad recibida/facturada no puede duplicarse por recepciones parciales; deuda y pago se concilian por importe, no por cantidad de producto.

### 6.9 Ventas mayoristas: pedido, reserva, despacho parcial y factura

~~~text
Sales.Order / OrderLine
  └─ confirm Order
       └─ Inventory.Shipment (waiting / reserve)
            ├─ ShipmentResLedger (planned outgoing reservation)
            └─ mark as Ready / Done
                 └─ ShipmentInvLedger (physical outgoing stock)
       └─ Invoicing.Invoice / InvoiceLine
            └─ SalesLedgerInvoice (sales reporting)
~~~

**Pedido y despacho:**

- Sales.Order mantiene customer/department, ubicación, dirección de entrega, moneda, plazo de pago, referencia del cliente, cantidades, precios, descuentos y datos fiscales del pedido.
- SalesOrderConfirmed confirma el pedido con APPLY/NEWSESSION.
- SalesOrderShipment crea o reutiliza un Shipment waiting para el remanente de cada línea confirmada. Ejecuta precheckAvailability, que compara la demanda contra disponible y registra reservas; por tanto, la reserva no es todavía una salida física.
- done(OrderLine) suma unidades despachadas en Shipment activos; toShip es la cantidad pedida menos la despachada. Una constraint impide sobre-despachar.
- El circuito contempla despachos parciales: shipPartially genera un Shipment para el remanente no reservado. Los links a OrderLine permiten conciliar el total despachado a lo largo de varios documentos.
- ShipmentResLedger agrega las reservas netas no completadas; ShipmentInvLedger registra la diferencia efectivamente completada. El stock físico se reduce en el ledger cuando el despacho pasa a su estado final correspondiente, no cuando se confirma el pedido.

**Facturación:**

- SalesOrderInvoice permite facturar lo que queda de la cantidad pedida (InvoicingPolicy.ordered).
- SalesOrderInvoiceShipment agrega la política delivered. La inicialización de ese módulo fija delivered como política predeterminada para los OrderType de Sales.
- Bajo delivered, toInvoiceShipped suma cantidades done de ShipmentLine activas que todavía no tienen InvoiceLine asociada. El hook fill(Invoice, Order) copia sólo las cantidades ya despachadas, mantiene referencia a OrderLine y marca la relación ShipmentLine → InvoiceLine para evitar facturación duplicada.
- En consecuencia, el pedido comercial, la reserva, la salida física y la factura son etapas separadas. Hay que conciliar cada cantidad y no utilizar el estado confirmado como sinónimo de despachado o facturado.

### 6.10 Relación entre venta y aprovisionamiento

SalesOrderPurchase relaciona líneas de Sales.OrderLine con Purchase.OrderLine y permite navegar desde un pedido de venta a sus órdenes de compra relacionadas y viceversa. Suma cantidades de las líneas vinculadas y conserva la trazabilidad de ambas órdenes.

Esto es un vínculo de negocio importante para compras bajo pedido, faltantes, distribución y futura planificación. **No se debe inferir sólo por esta relación que MyCompany compra automáticamente todo lo vendido ni que cada vínculo representa una reserva física**: la generación de compra, las políticas de aprovisionamiento, MOQ, múltiplos, proveedor preferente y cobertura deben mapearse y probarse en módulos separados antes de crear automatismos Rubrova.

### 6.11 Analítica comercial y costo

SalesLedger proporciona una clase abstracta de hechos para informes por producto, cliente, ubicación, fecha, cantidad, precio, costo, margen, impuestos e importe. SalesLedgerInvoice incorpora las líneas de facturas activas con cantidades/importes positivos; SalesLedgerBill incorpora notas de crédito activas con cantidades/importes negativos.

El costo base se deriva de cost(item, date) por cantidad. Esta estructura es preferible a reconstruir ventas desde el formulario POS. Antes de utilizar el margen para decisiones productivas, Rubrova debe verificar la política de costo temporal, ajustes retroactivos, devoluciones parciales, descuentos, impuestos y moneda, y reconciliarlo contra el ledger de costos de inventario.

**Implicación de arquitectura:** los canales local, POS y mayorista deben converger a los documentos y ledgers de origen adecuados; los informes analíticos deben leer esas fuentes con claves de canal/área preservadas. No generar un segundo inventario o una tabla de ventas paralela para cada canal.

## 7. Hallazgos que se deben convertir en regresiones

| Hallazgo | Evidencia en fuente 6.2 | Regla para Rubrova |
|---|---|---|
| GROUP SUM vacío no implica cero | agregados de Session y otras áreas no tienen default intrínseco | Normalizar con OVERRIDE ..., 0 cuando la regla de negocio requiera identidad cero; probar vacío y no vacío |
| El límite de reintegro por medio no es acumulativo | PosDashboardReturnPayment.lsf compara cada Bill con lo pagado en Invoice original | Calcular cuánto ya fue reembolsado en Bills/OutgoingPayments activos y rechazar exceso acumulado |
| La constraint de cantidad devuelta es configurable | CreditNote.lsf condiciona la constraint a checkReturnedQuantity | Activarla explícitamente para retail y probar bypass/rechazo en servidor |
| JSON nulo no es una lista vacía | Action API v6 y exportaciones JSON | Especificar contadores y forma de respuesta; validar cuerpo HTTP |
| APPLY puede reintentarse | contrato transaccional de la plataforma | Nada irreversible dentro de efectos que puedan repetirse |
| Los hooks tienen firma y selección | ABSTRACT LIST / ACTION+ / fill | Extender sólo puntos abstractos y compatibles |
| Formularios dependen del diseño upstream | EXTEND FORM / DESIGN | Probar la pantalla después de cada cambio de base/fork |
| Caja neta no equivale a arqueo | SessionPayment y Payment.balance consultan agregados distintos | Mantener el arqueo físico como registro aparte |
| Las sesiones manuales no son el flujo normal POS | el formulario sessions permite CRUD directo | Abrir/cerrar desde acciones POS controladas; auditar operaciones administrativas |

**Anomalía a verificar:** en el bloque de cancelación de PosDashboardReturnPayment.lsf aparece una eliminación filtrada por IncomingPayment aunque el bloque de confirmación crea OutgoingPayment. No se concluye aún que sea un bug: antes hay que demostrar si la cancelación del diálogo revierte toda la sesión o deja efectos persistentes. Añadir una prueba de cancelación del diálogo y consultar los ledgers antes de tocar el código upstream.

## 8. Método Rubrova para construir sin duplicar ni adivinar

Antes de implementar una capacidad:

1. **Buscar el dueño existente.** Localizar clase, propiedades, acciones, constraints, estados, formularios, REQUIRE y los módulos que los inicializan.
2. **Seguir el caso de uso completo.** No quedarse en la pantalla: documento → pago → ledger → estado → informes → cancelación/reverso.
3. **Identificar la autoridad.** Decidir cuál objeto/ledger es la fuente única de verdad y qué datos nuevos necesita Rubrova.
4. **Buscar un punto de extensión.** Preferir ABSTRACT LIST, ACTION+, propiedad abstracta, EXTEND CLASS o una interfaz expuesta a editar una acción concreta.
5. **Definir el contrato explícito.** Firma, tipos, unidad, moneda, precisión, estados, null/empty, idempotencia, errores, transacción y compatibilidad.
6. **Añadir tests del contrato antes del flujo E2E.** Probar semántica positiva, negativa, vacía, parcial, duplicada, concurrente y cancelada.
7. **Integrar por capas.** Prevalidación estática → compilación → carga real de módulos → API autenticada → caso de uso completo → reinicio/persistencia → backup/restore.
8. **Documentar evidencia.** Commit exacto, runtime, plataforma, resultado, logs y límites de aceptación.

### Matriz de decisiones

| Necesidad | Primera elección | Evitar |
|---|---|---|
| Nuevo campo del dominio existente | DATA sobre la clase nativa, desde módulo Rubrova | tabla espejo independiente para el mismo hecho |
| Nueva regla derivada | propiedad declarativa o constraint sobre fuente nativa | recalcular sólo en UI |
| Enriquecer una acción existente | hook abstracto compatible | ACTION+ sobre acción concreta |
| Mostrar datos Rubrova en pantalla MyCompany | EXTEND FORM + DESIGN | copiar toda la pantalla base |
| Integración con proveedor | adapter + intención + idempotencia + conciliación | bloquear la venta mientras el proveedor está lento |
| Consulta externa del ERP | acción @@api autenticada y esquema versionado | exponer evaluador arbitrario |
| Analítica | proyección/exportación read-only desde ledger y documentos | escribir sobre hechos históricos |
| Capacidad independiente real | servicio con datos y contrato propios | servicio nominal que comparte tablas sin dueño claro |

## 9. Plan de conocimiento pendiente

El repositorio contiene cientos de módulos MyCompany; no es honesto afirmar que todos sus contratos están completamente mapeados por esta primera investigación. Esta guía cubre en profundidad el recorrido POS más crítico. El inventario debe crecer por dominio y evidencia:

1. Compras y abastecimiento: PurchaseOrder → recepción parcial/completa → costos → factura proveedor → pagos.
2. Ventas no POS y mayorista: SalesOrder → despacho parcial → facturación → cobros/deuda.
3. Devoluciones/reembolsos fuera de Retail y notas de crédito no minoristas.
4. Impuestos, documentos fiscales y localización argentina/ARCA.
5. Costos, lotes, vencimientos, fabricación, recetas y mermas.
6. CRM/clientes, cuentas corrientes y límites de crédito.
7. Usuarios, permisos, auditoría y aislamiento por compañía.
8. Integraciones de archivos, impresión, dispositivos y sincronización offline.

Por dominio, producir: mapa de módulos y dependencias; clases y relaciones; acciones públicas; puntos de extensión; estados e invariantes; ciclo de vida del ledger; API/formatos; escenarios de excepción; matriz de tests. No inferir que un módulo es seguro de extender sólo porque su nombre coincide con la necesidad.

## 10. Referencias de código y documentación

### Fuentes exactas de Rubrova

- [Lock MyCompany 6.2](../../platform/mycompany-6.2.lock.json)
- [Lock de fuentes](../../platform/source-lock.json)
- [MyCompany top module](../../vendor/mycompany/src/main/lsfusion/MyCompany.lsf)
- [Retail module](../../vendor/mycompany/src/main/lsfusion/retail/Retail.lsf)
- [POS dashboard](../../vendor/mycompany/src/main/lsfusion/retail/pos/dashboard/PosDashboard.lsf)
- [POS payment](../../vendor/mycompany/src/main/lsfusion/retail/pos/dashboard/PosDashboardPayment.lsf)
- [POS return](../../vendor/mycompany/src/main/lsfusion/retail/pos/dashboard/return/PosDashboardReturn.lsf)
- [POS return payment](../../vendor/mycompany/src/main/lsfusion/retail/pos/dashboard/return/PosDashboardReturnPayment.lsf)
- [Session](../../vendor/mycompany/src/main/lsfusion/retail/sessions/Session.lsf)
- [Session invoices](../../vendor/mycompany/src/main/lsfusion/retail/sessions/SessionInvoice.lsf)
- [Session payment totals](../../vendor/mycompany/src/main/lsfusion/retail/sessions/SessionPayment.lsf)
- [CreditNote](../../vendor/mycompany/src/main/lsfusion/invoicing/invoices/creditnotes/CreditNote.lsf)
- [CreditNoteReceipt](../../vendor/mycompany/src/main/lsfusion/invoicing/inventory/receipts/CreditNoteReceipt.lsf)
- [BillReceipt](../../vendor/mycompany/src/main/lsfusion/invoicing/inventory/receipts/BillReceipt.lsf)
- [InvoiceShipment](../../vendor/mycompany/src/main/lsfusion/invoicing/inventory/shipments/InvoiceShipment.lsf)
- [ShipmentInv ledger](../../vendor/mycompany/src/main/lsfusion/inventory/shipments/ShipmentInv.lsf)
- [ReceiptInv ledger](../../vendor/mycompany/src/main/lsfusion/inventory/receipts/ReceiptInv.lsf)
- [Physical inventory ledger](../../vendor/mycompany/src/main/lsfusion/inventory/ledgers/inv/InvLedger.lsf)
- [Reservation ledger](../../vendor/mycompany/src/main/lsfusion/inventory/ledgers/res/ResLedger.lsf)
- [Payment ledger](../../vendor/mycompany/src/main/lsfusion/invoicing/ledgers/Payment.lsf)
- [POS payment method/account mapping](../../vendor/mycompany/src/main/lsfusion/retail/pos/PosPaymentMethod.lsf)
- [Cash movements](../../vendor/mycompany/src/main/lsfusion/retail/pos/dashboard/cash/PosDashboardCash.lsf)

### Documentación oficial

- [lsFusion 6.x — Modules](https://docs.lsfusion.org/v6/Modules/)
- [lsFusion 6.x — Extensions](https://docs.lsfusion.org/v6/Extensions/)
- [lsFusion 6.x — Action extension](https://docs.lsfusion.org/v6/How-to_Action_extension/)
- [lsFusion 6.x — Session management](https://docs.lsfusion.org/v6/Session_management/)
- [lsFusion 6.x — APPLY](https://docs.lsfusion.org/v6/Apply_changes_APPLY/)
- [lsFusion 6.x — Integration](https://docs.lsfusion.org/v6/Integration/)
- [lsFusion 6.x — Access from an external system](https://docs.lsfusion.org/v6/Access_from_an_external_system/)
- [lsFusion 6.x — EXTERNAL](https://docs.lsfusion.org/v6/Access_to_an_external_system_EXTERNAL/)
- [MyCompany v6 — System modules overview](https://mycompany-docs.lsfusion.org/v6/)
- [MyCompany v6 — Sessions](https://mycompany-docs.lsfusion.org/v6/retail/sessions/)

Los manuales MyCompany v7 sobre POS, pagos y devoluciones son referencias complementarias para el usuario final, no prueba directa del comportamiento de la fuente 6.2 fijada:
- [POS](https://mycompany-docs.lsfusion.org/retail/pos/)
- [Payments](https://mycompany-docs.lsfusion.org/retail/payments/)
- [Returns](https://mycompany-docs.lsfusion.org/retail/returns/)
