# Diagnóstico de diferencias y fallos de validación — 20 de noviembre de 2026

## Conclusión ejecutiva

Los últimos fallos del smoke test no tienen una sola causa. Hay tres clases diferentes:

1. **Falso negativo intermitente en la prueba visual del cobro.** El test esperaba 1,2 segundos tras pulsar «Cobrar» y consultaba el DOM una sola vez. lsFusion carga el diálogo de forma asíncrona. En una ejecución la inspección capturó el formulario de venta antes de que aparecieran los medios; en otra, la misma configuración sí mostró «Cobro», «Efectivo» y «Tarjeta». No era una diferencia de configuración POS.
2. **La validación de runtime no construye el fork de Rubrova.** Arranca artefactos oficiales precompilados de MyCompany/lsFusion y les copia los módulos propios. El reactor Maven que compila `vendor/platform` y `vendor/mycompany` no se ejecuta en ese workflow. Por eso el smoke no está verificando las modificaciones Java del fork.
3. **La política global de timeout tiene un camino sin cubrir.** El cambio propio de `CallHTTPAction` cubre las llamadas ejecutadas en servidor. El camino `clientAction` del navegador transforma `HttpClientAction` en `GHttpClientAction` sin transportar el timeout; el dispatcher GWT usa `XMLHttpRequest` sin límite temporal. Este comportamiento también existe en el upstream fijado.

No corresponde resolver estos tres problemas agregando más condiciones a los datos del POS.

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

## Diferencia entre el runtime probado y el fork que queremos distribuir

El workflow `.github/workflows/platform-extension.yml` hace lo siguiente:

- `prepare-mycompany-6.2.sh` descarga y verifica el JAR oficial `mycompany-6.2.jar` y el Compose oficial.
- El smoke fija imágenes oficiales `lsfusion/mycompany:6.2`, `lsfusion/server:6.2`, `lsfusion/client:6.2` y PostgreSQL.
- `deploy-mycompany-6.2.sh` copia los cuatro archivos de `extensions/lsfusion` a `docker-server` y prepara el override.
- El nuevo job `build-fork` ejecuta `mvn -f build/rubrova/pom.xml -Passemble -DskipTests package`, con Java 21, después de verificar las fuentes y aplicar idempotentemente el parche de timeout.
- Ese job compila `vendor/platform`, el cliente GWT y `vendor/mycompany`; además verifica los artefactos JAR/WAR generados.
- El job de smoke visual sigue descargando y ejecutando las imágenes oficiales `lsfusion/mycompany:6.2`, `lsfusion/server:6.2` y `lsfusion/client:6.2`. No instala todavía los JAR/WAR del reactor en una imagen de Rubrova.

Esto separa por fin dos garantías distintas: **compilación del fork** y **aceptación visual de las extensiones sobre el runtime oficial**. El build del fork debe aprobarse antes de ejecutar el smoke, pero aún falta empaquetar imágenes propias y ejecutar el mismo flujo POS contra esos artefactos compilados. El lock conserva pendiente la aceptación del rebuild offline y no se debe marcar completado hasta que la compilación CI también termine y sus artefactos se inspeccionen.

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

## Errores PostgreSQL observados

En el mismo arranque se registraron dos errores sobre la tabla interna `dumb`, una escritura concurrente sobre `_auto.Time_currentDate` con error de serialización y varias consultas canceladas. El código upstream confirma que `dumb` es una tabla interna del motor usada para consultas sin columnas y que `TableFactory` debe crearla durante el bootstrap.

Estos eventos ocurrieron durante `onStarted`, antes de finalizar el arranque. No son la causa del falso negativo de «Efectivo»: el servidor completó `onStarted`, abrió el POS, creó el turno, agregó el artículo y luego el test tomó la captura demasiado pronto. Aun así, las consultas de inicialización/serialización deben quedar como una línea separada de investigación y no considerarse aceptadas sólo porque el servidor acaba respondiendo.

## Plan de corrección priorizado

1. **Corregido en la automatización:** esperar el formulario de cobro renderizado, usar locators accesibles estables para navegación y botones, retirar índices DOM guardados y quitar esperas fijas sin condición de éxito.
2. **Compilación inicial aprobada:** el reactor de Rubrova ya compiló lsFusion, GWT y MyCompany; la revisión posterior del cuerpo nulo está en recompilación.
3. Ejecutar el smoke visual sobre el último commit después de la compilación. El smoke actual sigue usando el runtime oficial; no validar todavía los parches Java/GWT como desplegados.
4. Construir imágenes propias: servidor con el perfil `embed-server` e imagen cliente Tomcat con el WAR GWT construido. Sustituir ambas imágenes en el Compose de aceptación y ejecutar el mismo flujo POS.
5. Añadir prueba de contrato de `EXTERNAL HTTP CLIENT` en el navegador, con endpoint de timeout CORS; probar timeout, error de red, abort y recuperación, además del smoke Toxiproxy del camino servidor.
6. Investigar por separado los errores de creación de la tabla interna `dumb` y la serialización concurrente de `_auto.Time_currentDate`; no marcar el bootstrap como limpio hasta explicar los registros.
7. Aceptar rebuild offline y runtime aislado de Internet; siguen pendientes en `platform/source-lock.json`.

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

## Actualización posterior: runtime propio probado en run 163 (22 de noviembre de 2026)

La ejecución [44975665176](https://github.com/JavierGrecco/Rubrova/actions/runs/44975665176), commit `8905827ca2eb1eded7e7e56194148be4feb2cb58`, confirmó lo siguiente:

- `validate` y `validate-windows` aprobaron.
- El reactor compiló lsFusion 6.2, MyCompany y GWT. Después se reconstruyó el servidor sin `-Passemble`; el JAR incluyó `BusinessLogicsBootstrap`, `DaemonThreadFactory`, `CustodianDailyRollingFileAppender` y `RollingFileAppender`.
- Las tres imágenes Rubrova se construyeron y el Compose las utilizó. La lógica completó los 716 módulos, ejecutó `onStarted` y exportó RMI en 7652.
- La aceptación falló en el cliente web: Tomcat registró que el listener de `ROOT.war` no pudo iniciar y la ruta raíz quedó en HTTP 404. El servidor de lógica terminó su inicialización; la web no quedó aceptada.

La revisión del WAR generado bajo `-Passemble` mostró que no contiene `WEB-INF/lib/api-6.2.jar`. El perfil `assemble` declara `api` como `provided` para crear el ensamblado de lógica, pero ese alcance no sirve para un WAR web autónomo. La reconstrucción siguiente compila servidor y cliente web sin ese perfil y exige que el WAR incluya la API. El Compose también hace que Tomcat espere la disponibilidad real de RMI en 7652 antes de desplegar el cliente.

Se corrigió otra condición del propio test: las imágenes `rubrova/*` no se publican en un registry y por eso no tienen `RepoDigest`. Se verificará su ID local frente al ID usado por cada contenedor; PostgreSQL y Toxiproxy seguirán requiriendo los digests fijados.

Finalmente, la prueba de timeout usa una respuesta lenta real de cinco segundos y exige que la operación termine entre 0,75 y 4 segundos con un timeout configurado de un segundo. Ya no podrá aprobar por un rechazo de conexión casi instantáneo.

**Estado tras run 163:** compilación de servidor propio aprobada; carga de lógica y RMI aprobadas; WAR/arranque web y smoke funcional POS aún pendientes. Venta cobrada, impacto en stock, cierre de caja, instalación offline, ARM64, backup/restore y aceptación productiva siguen pendientes.
