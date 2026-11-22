# Diagnóstico de diferencias y fallos de validación — 20 de noviembre de 2026

## Conclusión ejecutiva

El estado cambió después de la aceptación [CI #172](https://github.com/JavierGrecco/Rubrova/actions/runs/44982716337), commit `3d1cfbf1038e25608768c1561349390708dca6ec`. La prueba ahora compila lsFusion 6.2, MyCompany 6.2 y el cliente GWT desde las fuentes vendorizadas de Rubrova, construye las imágenes propias y ejecuta el POS sobre ese runtime en Linux x86_64.

La ejecución #172 confirmó una venta minorista sintética de ARS 1.250 desde Chromium y concilió los datos persistidos:

- Una factura y una factura pagada.
- Un pago entrante, aplicado por ARS 1.250.
- ARS 1.250 cobrados en efectivo y reflejados en el turno y la cuenta de caja.
- Inventario: 10 unidades iniciales, una salida y nueve disponibles.

Los tres grupos de errores PostgreSQL observados se separaron y revisaron contra el código del motor: los dos `relation "dumb" does not exist` corresponden a las comprobaciones de primera instalación antes de sincronizar tablas; el conflicto serializable de `_auto.Time_currentDate` se recuperó durante `ChangeCurrentDate` y el valor quedó persistido; los `SQLTimeoutException` se registran como excepciones manejadas del motor, aunque su frecuencia y el coste de arranque siguen mereciendo seguimiento.

El primer circuito comercial está aceptado en CI; el proyecto no está listo para producción. Cierre de turno, devoluciones, vuelto, tarjeta, persistencia tras reinicio, backup/restore, paquete offline y prueba real del camino HTTP del navegador siguen pendientes.

## Comparación contra MyCompany original

Snapshots fijados en `platform/source-lock.json`:

- MyCompany 6.2: `d21ca6978717b98b6300d90267f9767db7414008`.
- lsFusion 6.2: `dd4dbe5bf9b136e73e18fe25d741253929324350`.

Comparé los módulos críticos de POS del snapshot local con el repositorio oficial en el commit fijado. Coinciden exactamente:

- `PosDashboardPayment.lsf`: hash de blob `f9bfbfdff163f01bbd2167035807cddfbe866ede`.
- `SessionInvoice.lsf`.
- `PosPaymentMethod.lsf`.
- `PaymentMethodInitial.lsf`.
- `PosDashboard.lsf`.

También comparé el módulo de pago principal con el `master` oficial consultado el 20 de noviembre. `PosDashboardPayment.lsf` y `PaymentMethodInitial.lsf` siguen idénticos. El `master` sí contiene cambios posteriores en otros módulos:

- `PosPaymentMethod.lsf` incorpora una restricción para que la cuenta central de caja no sea la misma que la cuenta del cajón de efectivo. El fixture de Rubrova ya usa dos cuentas distintas, por lo que cumple esa regla.
- `SessionInvoice.lsf` cambia la presentación de paneles.
- `PosDashboard.lsf` cambia una navegación de `SEEK` a `ACTIVATE`.

No encontré en esos cambios una corrección posterior del filtro de medios de pago del diálogo. Por tanto, no hay evidencia de que Rubrova haya alterado accidentalmente el código de pago heredado.

El snapshot upstream fijado no trae un workflow de GitHub Actions ni archivos de tests identificados por nombre. El repositorio original distribuye un JAR y un Compose oficiales, y ofrece una demo; la suite de navegación, los fixtures sintéticos y los escenarios de fallo que hoy estamos ejecutando son aportes de Rubrova, no pruebas heredadas de MyCompany.

## Causa reproducible del falso fallo de «Efectivo»

El script `inspect-mycompany-ui.py` hacía:

1. pulsar «Cobrar»;
2. dormir exactamente 1.200 ms;
3. leer el texto de pantalla una sola vez;
4. fallar si aún no aparecía «Efectivo».

En el run `44852351887`, la captura se tomó mientras seguía visible el formulario de venta y aún no aparecía el cuerpo del diálogo. En el run anterior `44851985684`, la misma configuración sí mostró «Cobro → Medio de pago → Efectivo / Tarjeta». En ambos, el diagnóstico del servidor devolvió la misma moneda, tipo de precio, métodos y cuentas.

La corrección es esperar una condición visible y estable —título «Cobro» y los dos medios de pago en dos lecturas consecutivas— con un límite máximo, no una pausa fija. El test sigue sin confirmar el pago ni crear una venta.

La comparación del historial de CI reveló una segunda carrera de la misma familia: las funciones de navegación y botones guardaban índices calculados de listas DOM y luego hacían clic con `locator(...).nth(index)`. GWT vuelve a renderizar el navegador y sus controles de forma asíncrona, por lo que el índice puede apuntar a otro elemento o a un control que ya fue sustituido. La corrección final usa locators accesibles por nombre exacto, re-resueltos al momento del clic; para «Comercio» espera que «Punto de venta» aparezca antes de seguir. Se eliminó el helper antiguo que devolvía índices y las pausas fijas de 750/1.000 ms que no comprobaban ningún estado.

## Runtime propio: build y smoke de aceptación

El workflow `.github/workflows/platform-extension.yml` separa la compilación y el smoke, pero ambos se ejecutan contra el mismo SHA:

1. Valida snapshots, extensiones y parche idempotente del timeout.
2. Compila el reactor de Rubrova con Java 21: lsFusion, cliente GWT y MyCompany.
3. Recompila servidor y cliente web con las dependencias necesarias para su runtime autónomo.
4. Verifica los artefactos del servidor, la lógica y el WAR cliente.
5. Publica los tres artefactos y los entrega al job de smoke.
6. Construye las imágenes `rubrova/server`, `rubrova/logics` y `rubrova/client`; Compose comprueba que cada contenedor usa el ID de imagen local recién construido.
7. Arranca PostgreSQL 18, MyCompany y el cliente web; Chromium ejecuta la aceptación del POS.

La ejecución #172 completó todos esos pasos. No utilizó las imágenes de aplicación oficiales como sustituto de las construidas por Rubrova. Las imágenes auxiliares externas (PostgreSQL y herramientas CI) siguen fijadas por digest.

Esta prueba demuestra el runtime propio en Linux x86_64 dentro de CI. No demuestra todavía una instalación local totalmente offline, un paquete de usuario final ni la ejecución nativa en Windows/macOS. El rebuild Maven completo también sigue siendo online: la caché y el repositorio de dependencias deberán prepararse y probarse en modo offline por separado.

## Brecha de timeout confirmada en el upstream

En el camino de servidor, `CallHTTPAction` calcula el timeout y lo entrega a `ExternalHttpUtils`, que configura timeout de conexión, adquisición de conexión y respuesta, además de un límite de ejecución.

En el camino de navegador:

1. `CallHTTPAction` crea un `HttpClientAction` que sí contiene `timeout`.
2. `ClientActionToGwtConverter` crea `GHttpClientAction` pasando método, URL, cuerpo y encabezados, pero omite `timeout`.
3. `GHttpClientAction` no tiene un campo de timeout.
4. `GwtActionDispatcher` utiliza `XMLHttpRequest` y sólo escucha el cambio de estado a `DONE`; no instala un temporizador.

Los tres archivos del camino GWT coinciden exactamente entre el snapshot Rubrova y el commit upstream fijado. Es una limitación heredada del upstream, no un cambio accidental introducido por Rubrova. La política Java de 10 segundos por defecto / 60 segundos máximo no puede considerarse global hasta corregir y construir también este camino.

El test Toxiproxy actual invoca el helper propio `rubrovaHttpGet` desde servidor con timeout explícito de 1.000 ms. Comprueba ese helper, la clasificación y persistencia de incidencias; no comprueba el camino GWT ni el timeout por defecto del motor.



## Corrección añadida después del diagnóstico: timeout GWT

El commit `4bb52b2bd61a3bcabae4b3be33a25f5ec7dd370c` añade el campo `timeout` a `GHttpClientAction`, lo propaga desde el conversor y aplica en `GwtActionDispatcher` un temporizador con máximo de 60 segundos. Si vence, aborta XHR y completa el callback con estado 0; una bandera evita que la ruta de aborto y el evento de estado final completen dos veces la misma acción. El listener de estado se registra antes de `send()`.

La solución mantiene `XMLHttpRequest` para no perder las respuestas binarias `arraybuffer`. GWT documenta `RequestBuilder.setTimeoutMillis`, pero el cliente existente depende del acceso directo a `ArrayBuffer`, así que el cambio conserva el transporte actual y añade el límite a su alrededor. La compilación de GWT es ahora una condición explícita del job `build-fork`.

## Primera compilación completa del fork

El job `build-fork` terminó con éxito en el run [44854238946](https://github.com/JavierGrecco/Rubrova/actions/runs/44854238946), commit `4039f48696211b7eba88f0e74768ed9eaab613f9`:

- 13 módulos del reactor terminaron en `BUILD SUCCESS` en 9 min 13 s.
- Compiló 421 fuentes del API, 1.734 del servidor, 791 del cliente web y 5 fuentes Java de MyCompany.
- El compilador GWT compiló el módulo `lsfusion.gwt.main` en 8 permutaciones.
- Generó `vendor/platform/web-client/target/lsfusion-client-6.2.war`, `vendor/platform/server/target/server-6.2.jar` y `vendor/mycompany/target/mycompany-6.2.jar`; la verificación de artefactos terminó correctamente.

Esta primera aprobación incluye el cambio que propaga el timeout al cliente GWT. **No incluye todavía** el refinamiento posterior que devuelve cuerpo `null` para timeout/error de red (commit `5ef1606b421beeefef9b47aa8b3f571f527e19c4`), ni los últimos cambios del test visual. Ese commit posterior está en proceso de recompilación. Tampoco significa que el smoke visual haya usado esos artefactos: sigue ejecutando las imágenes oficiales de MyCompany/lsFusion.

La compilación fue online (descarga inicial de dependencias Maven); el rebuild offline con repositorio Maven verificado sigue sin aceptarse.

## Errores PostgreSQL observados: diagnóstico con el código fuente

Los registros ya no se tratan como un único grupo ni como un fallo genérico de arranque. Se identificaron tres situaciones diferentes.

### 1. Dos lecturas de `dumb` durante la detección de una base vacía

En el primer arranque de PostgreSQL vacío aparecen dos mensajes `relation "dumb" does not exist`. El origen está en la secuencia de inicialización del motor:

1. `BusinessLogics` ejecuta `initBLTask`.
2. `initClassDataIndicesTask` depende de `initReflectionEventsTask`.
3. `InitReflectionEventsTask.run()` llama a `DBManager.initReflectionEvents()`.
4. `DBManager.initReflectionEvents()` ejecuta `isFirstStart(sql)` dos veces.
5. `isFirstStart()` consulta la estructura anterior mediante `getOldDBStructure(sql)`. Si PostgreSQL responde SQLSTATE `42P01` (undefined table), el método lo interpreta explícitamente como una base vacía y devuelve `true`.

La tabla `dumb` aún no se ha creado en esa fase. Más adelante, `DBManager.onInit()` inicia `synchronizeDB()`, y `synchronizeDB()` llama a `TableFactory.fillDB(sql, LM.baseClass)`, que crea las tablas internas y el registro vacío. Por eso las dos consultas iniciales fallidas son los dos sondeos de primera instalación previstos por el código; no indican que `dumb` falte después del bootstrap.

La ejecución #172 verificó posteriormente que `dumb` existe y contiene su registro interno. El test también verificó que `_auto.Time_currentDate` ya estaba persistida.

### 2. Conflicto serializable al establecer `Time.currentDate`

En una ejecución de primera instalación, PostgreSQL registró:

`could not serialize access due to concurrent update`

sobre:

`UPDATE _auto SET Time_currentDate=CAST($1 AS date) FROM dumb WHERE 1=1`

El log del servidor muestra `ChangeCurrentDate started: from null to 2026-11-22`, seguido del error de PostgreSQL y, 55 ms después, `ChangeCurrentDate finished`. La comprobación posterior encontró el valor persistido.

El motor convierte conflictos de actualización/deadlock en `SQLConflictException`. `DataSession.transactApply()` revierte una transacción con `SQLHandledException` reintentable y vuelve a ejecutar la aplicación. La secuencia observada y el valor persistido son coherentes con esa recuperación. Este evento se clasifica como conflicto transitorio recuperado, no como arranque fallido; debe seguir observándose para detectar recurrencia anormal.

### 3. `SQLTimeoutException` durante consultas de inicialización y operación

Los logs #166, #171 y #172 contienen consultas canceladas por el límite adaptativo de lsFusion, registradas en `INFO SQLHandLogger`. En el motor, `SQLTimeoutException` deriva de `SQLHandledException`; los intentos que forman parte de un apply transaccional pueden hacer rollback y repetirse mediante `DataSession.transactApply()`. No todo timeout aislado demuestra por sí mismo que esa consulta específica se reintentó, por lo que no se deben borrar del diagnóstico ni declararlos inocuos de manera general.

La evidencia funcional de #172 muestra que estos registros no impidieron completar el circuito: el cobro se confirmó y la factura, el pago, la caja y el inventario quedaron conciliados. Aun así, hay que medir arranque frío frente a reinicio, contar los reintentos y localizar las consultas más costosas. No corresponde elevar límites SQL globales ni desactivar controles sólo para silenciar los logs.

## Estado y próximos pasos después de CI #172

**Aceptado:** build desde fuentes Rubrova, imágenes propias, arranque de PostgreSQL/MyCompany/cliente web, login, POS, apertura de turno, selección de producto, confirmación del cobro y conciliación de factura/pago/caja/stock.

**Siguiente bloque:**
1. Cierre de turno con conciliación de ventas, devoluciones, ingresos, retiros y saldo final.
2. Devolución nativa de MyCompany: Bill relacionado con factura, reintegro por el medio realmente abonado, OutgoingPayment y efecto inverso de inventario.
3. Vuelto, tarjeta y pagos mixtos; comprobar los saldos por medio y el tratamiento de operaciones inciertas.
4. Reiniciar servidor y cliente sin borrar PostgreSQL y volver a conciliar los mismos registros; después backup/restore y rollback sobre copia.
5. Probar en Chromium `EXTERNAL HTTP CLIENT` con endpoint lento/CORS, timeout, abort, error de red y recuperación. El test GET del servidor no cubre ese camino.
6. Preparar paquete offline y validar en PC limpia; luego runtime real Windows y macOS ARM64.
7. Mantener la localización y la regresión ERP creciendo por módulos, sin alterar los procesos originales de MyCompany que ya cumplen.

No se deben habilitar conectores productivos (ARCA, adquirentes, marketplaces o logística) antes de tener idempotencia, Outbox, circuit breaker, auditoría y conciliación demostradas.

## Referencias upstream

- [MyCompany 6.2 — POS payment](https://github.com/lsfusion-solutions/mycompany/blob/d21ca6978717b98b6300d90267f9767db7414008/src/main/lsfusion/retail/pos/dashboard/PosDashboardPayment.lsf)
- [MyCompany 6.2 — POS payment methods](https://github.com/lsfusion-solutions/mycompany/blob/d21ca6978717b98b6300d90267f9767db7414008/src/main/lsfusion/retail/pos/PosPaymentMethod.lsf)
- [MyCompany upstream master](https://github.com/lsfusion-solutions/mycompany/tree/master)
- [lsFusion upstream — browser HTTP dispatcher](https://github.com/lsfusion/platform/blob/dd4dbe5bf9b136e73e18fe25d741253929324350/web-client/src/main/java/lsfusion/gwt/client/controller/dispatch/GwtActionDispatcher.java)
- [lsFusion upstream — client action conversion](https://github.com/lsfusion/platform/blob/dd4dbe5bf9b136e73e18fe25d741253929324350/web-client/src/main/java/lsfusion/gwt/server/convert/ClientActionToGwtConverter.java)
- [lsFusion upstream — server HTTP action](https://github.com/lsfusion/platform/blob/dd4dbe5bf9b136e73e18fe25d741253929324350/server/src/main/java/lsfusion/server/physics/dev/integration/external/to/CallHTTPAction.java)

## Diferencia adicional detectada: persistencia PostgreSQL 18

El test fijaba `postgres:18` pero heredaba el mount antiguo `./docker-db:/var/lib/postgresql/data` del Compose original. La imagen oficial cambió en PostgreSQL 18 el `PGDATA` predeterminado a `/var/lib/postgresql/18/docker` y recomienda montar el padre `/var/lib/postgresql`. Con el mount viejo, el servidor puede escribir en el volumen anónimo de la imagen en lugar del directorio esperado; al recrear el contenedor, los datos no quedan en el bind mount que creíamos persistente. Rubrova ahora crea un volumen independiente `docker-db-pg18`, monta `/var/lib/postgresql` y espera `pg_isready` antes de iniciar el servidor. El directorio antiguo `docker-db` se conserva, no se elimina ni se migra automáticamente.

Fuente: [documentación Docker oficial de PostgreSQL](https://github.com/docker-library/docs/blob/master/postgres/content.md).

## Hito histórico: run 163 (22 de noviembre de 2026)

La ejecución 163 documentó el primer arranque de las imágenes propias y el problema del WAR sin `api-6.2.jar`. Ese fallo del cliente web se corrigió en la recompilación posterior del WAR con dependencias de runtime. La aceptación más reciente y completa es CI #172, detallada a continuación.


## Aceptación comercial del POS en CI #172 (22 de noviembre de 2026)

Ejecución: [44982716337](https://github.com/JavierGrecco/Rubrova/actions/runs/44982716337)  
Commit: `3d1cfbf1038e25608768c1561349390708dca6ec`.

Los cinco jobs del workflow terminaron correctamente: validación Linux, validación PowerShell, build desde fuentes, recompilación/validación de artefactos y smoke de runtime Linux x86_64. macOS ARM64 quedó omitido porque es un job manual.

Chromium confirmó el diálogo nativo de cobro. La automatización anterior buscaba `Ok (ctrl ENTER)` por nombre accesible y GWT no lo exponía como esperaba Playwright, aunque el botón sí existía en el DOM. El test ahora usa el identificador estable `PROPERTY(overFormOk)`; no se cambió el proceso de pago original.

La respuesta del test de conciliación fue:

```json
{
  "salesCount": 1,
  "paidSalesCount": 1,
  "invoiceAmount": 1250,
  "paidAmount": 1250,
  "cashPaidAmount": 1250,
  "incomingPaymentCount": 1,
  "sessionCashPaid": 1250,
  "cashBalance": 1250
}
```

La conciliación de inventario devolvió:

```json
{
  "incomingQuantity": 10,
  "outgoingQuantity": 1,
  "onHand": 9
}
```

Los valores son consultados después de confirmar el cobro en la base temporal. El fixture crea una moneda ARS, una caja, una ubicación y un ajuste inicial sintéticos. La venta utiliza el POS original de MyCompany y el despacho automático minorista; no escribe importes ni movimientos desde el test.

Esta prueba cierra el primer circuito comercial de POS en runtime Rubrova. No cubre cierre de turno, devolución, vuelto, tarjeta, reinicio con persistencia, backup/restore, instalación offline ni el camino HTTP CLIENT desde navegador.
