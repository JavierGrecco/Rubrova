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

## Diferencia entre el runtime probado y el fork que queremos distribuir

El workflow `.github/workflows/platform-extension.yml` hace lo siguiente:

- `prepare-mycompany-6.2.sh` descarga y verifica el JAR oficial `mycompany-6.2.jar` y el Compose oficial.
- El smoke fija imágenes oficiales `lsfusion/mycompany:6.2`, `lsfusion/server:6.2`, `lsfusion/client:6.2` y PostgreSQL.
- `deploy-mycompany-6.2.sh` copia los cuatro archivos de `extensions/lsfusion` a `docker-server` y prepara el override.
- No ejecuta `mvn -f build/rubrova/pom.xml -Passemble package`, no compila `vendor/platform` ni `vendor/mycompany`, y no incorpora al servidor la clase Java parchada de Rubrova.

El reactor `build/rubrova/pom.xml` existe, pero el propio lock declara pendiente la aceptación del rebuild offline. Por eso el smoke actual valida que las extensiones lsFusion funcionen sobre el runtime oficial, no que el fork fuente de Rubrova compile ni que los cambios Java estén desplegados.

## Brecha de timeout confirmada en el upstream

En el camino de servidor, `CallHTTPAction` calcula el timeout y lo entrega a `ExternalHttpUtils`, que configura timeout de conexión, adquisición de conexión y respuesta, además de un límite de ejecución.

En el camino de navegador:

1. `CallHTTPAction` crea un `HttpClientAction` que sí contiene `timeout`.
2. `ClientActionToGwtConverter` crea `GHttpClientAction` pasando método, URL, cuerpo y encabezados, pero omite `timeout`.
3. `GHttpClientAction` no tiene un campo de timeout.
4. `GwtActionDispatcher` utiliza `XMLHttpRequest` y sólo escucha el cambio de estado a `DONE`; no instala un temporizador.

Los tres archivos del camino GWT coinciden exactamente entre el snapshot Rubrova y el commit upstream fijado. Es una limitación heredada del upstream, no un cambio accidental introducido por Rubrova. La política Java de 10 segundos por defecto / 60 segundos máximo no puede considerarse global hasta corregir y construir también este camino.

El test Toxiproxy actual invoca el helper propio `rubrovaHttpGet` desde servidor con timeout explícito de 1.000 ms. Comprueba ese helper, la clasificación y persistencia de incidencias; no comprueba el camino GWT ni el timeout por defecto del motor.

## Errores PostgreSQL observados

En el mismo arranque se registraron dos errores sobre la tabla interna `dumb`, una escritura concurrente sobre `_auto.Time_currentDate` con error de serialización y varias consultas canceladas. El código upstream confirma que `dumb` es una tabla interna del motor usada para consultas sin columnas y que `TableFactory` debe crearla durante el bootstrap.

Estos eventos ocurrieron durante `onStarted`, antes de finalizar el arranque. No son la causa del falso negativo de «Efectivo»: el servidor completó `onStarted`, abrió el POS, creó el turno, agregó el artículo y luego el test tomó la captura demasiado pronto. Aun así, las consultas de inicialización/serialización deben quedar como una línea separada de investigación y no considerarse aceptadas sólo porque el servidor acaba respondiendo.

## Plan de corrección priorizado

1. **Hecho en esta revisión:** hacer determinista la espera del diálogo de cobro y declarar explícita la dependencia del fixture de precio respecto del módulo POS.
2. Separar la aceptación visual POS de la batería de HTTP/Toxiproxy, para que un fallo del DOM no oculte los resultados de resiliencia.
3. Incorporar un timeout y tratamiento de error/abort al camino GWT `clientAction`, propagándolo desde `HttpClientAction` hasta `GHttpClientAction`.
4. Hacer que CI compile el reactor Maven de Rubrova y que el runtime de aceptación utilice las imágenes construidas por ese proceso; hasta entonces, marcar los parches Java como no probados en runtime.
5. Añadir pruebas de contrato para timeout de conexión, timeout de respuesta, error de red, abort, 408/429/5xx, errores definitivos y recuperación. Mantener la política de no reintentar cobros/emisiones sin idempotencia o conciliación.

## Referencias upstream

- [MyCompany 6.2 — POS payment](https://github.com/lsfusion-solutions/mycompany/blob/d21ca6978717b98b6300d90267f9767db7414008/src/main/lsfusion/retail/pos/dashboard/PosDashboardPayment.lsf)
- [MyCompany 6.2 — POS payment methods](https://github.com/lsfusion-solutions/mycompany/blob/d21ca6978717b98b6300d90267f9767db7414008/src/main/lsfusion/retail/pos/PosPaymentMethod.lsf)
- [MyCompany upstream master](https://github.com/lsfusion-solutions/mycompany/tree/master)
- [lsFusion upstream — browser HTTP dispatcher](https://github.com/lsfusion/platform/blob/dd4dbe5bf9b136e73e18fe25d741253929324350/web-client/src/main/java/lsfusion/gwt/client/controller/dispatch/GwtActionDispatcher.java)
- [lsFusion upstream — client action conversion](https://github.com/lsfusion/platform/blob/dd4dbe5bf9b136e73e18fe25d741253929324350/web-client/src/main/java/lsfusion/gwt/server/convert/ClientActionToGwtConverter.java)
- [lsFusion upstream — server HTTP action](https://github.com/lsfusion/platform/blob/dd4dbe5bf9b136e73e18fe25d741253929324350/server/src/main/java/lsfusion/server/physics/dev/integration/external/to/CallHTTPAction.java)
