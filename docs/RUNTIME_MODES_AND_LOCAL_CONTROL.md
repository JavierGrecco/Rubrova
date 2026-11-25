# Modos de ejecución y control local de Rubrova

**Decisión de arquitectura:** separar el lugar donde corre el POS/ERP de la conectividad con proveedores externos. Ofrecer siempre un control independiente del servidor para consultar estado y cambiar el destino de ejecución.  
**Estado:** contrato de configuración y CLI implementados; existe un primer prototipo de lanzador nativo y pruebas unitarias para sus protecciones principales. El runtime completo aún no superó una aceptación funcional nativa en macOS/Windows; panel visual, instalador offline y migración entre destinos siguen pendientes.

## 1. Decisión

Rubrova tendrá tres destinos seleccionables desde un panel de control independiente:

| Destino | Dónde corre el servidor y la base | Requiere Docker | Requiere Internet para operar el núcleo |
|---|---|---:|---:|
| **Local nativo** | Java, PostgreSQL y Tomcat como procesos/servicios del propio equipo | No | No |
| **Docker local** | Los mismos componentes en contenedores en el propio equipo | Sí | No, una vez instalados y preparados |
| **Servidor remoto** | Servidor y base de datos en otra máquina o infraestructura | No en el puesto | Sí para acceder al servidor remoto |

El destino predeterminado para el desarrollo y la instalación local será **Local nativo**. Docker local se conserva como alternativa de aislamiento, repetibilidad y despliegue. Servidor remoto se configura con una URL HTTPS.

El contrato compartido está en `platform/runtime-config.schema.json`. La herramienta `scripts/platform/runtime-config.py` ya permite inicializar, validar, consultar y guardar el destino elegido. El validador rechaza URLs remotas sin TLS salvo loopback de desarrollo y no permite guardar contraseñas, tokens ni claves en el archivo.

## 2. No confundir ubicación con conectividad

Son dos decisiones diferentes:

- **Destino del núcleo:** dónde se ejecutan el servidor lsFusion/MyCompany, el cliente web y PostgreSQL.
- **Integraciones externas:** si Rubrova tiene habilitado llamar a ARCA, Mercado Pago, adquirentes, marketplaces, mensajería o transportistas.

Por eso, en Local nativo o Docker local se podrá pausar o habilitar las integraciones sin mover el servidor a la nube. Que Mercado Pago necesite Internet no significa que el POS deba estar alojado en Internet. En una caída de Internet el núcleo local seguirá atendiendo las operaciones admitidas; las autorizaciones remotas quedarán pendientes o inciertas y se conciliarán cuando vuelva el proveedor.

El modo híbrido de sucursal —base local autoritativa más sincronización durable con central— es un objetivo posterior, no un interruptor que debamos mostrar como terminado. Sólo se habilitará cuando Outbox/Inbox, idempotencia, conflictos de stock, recuperación y conciliación estén implementados y probados. Mientras tanto, el modo remoto no promete operar sin Internet.

## 3. Por qué conviene un runtime nativo sin Docker

El runtime de Rubrova está compuesto por piezas que pueden ejecutarse directamente en el sistema operativo:

1. **PostgreSQL 18:** proceso de base de datos nativo y persistencia local.
2. **Servidor lsFusion/Rubrova:** Java 21 ejecutando `lsfusion.server.logics.BusinessLogicsBootstrap`, con el artefacto `server.jar` compilado desde `vendor/platform`.
3. **Lógica MyCompany + extensiones Rubrova:** el JAR de lógica compilado desde `vendor/mycompany`, más los módulos y recursos de `extensions/lsfusion`, cargados por el classpath y `logics.topModule=RubrovaCustom`.
4. **Cliente web:** el WAR compilado desde `vendor/platform/web-client`, desplegado en Apache Tomcat 9 compatible con el cliente lsFusion 6.2.
5. **Control de ejecución:** un proceso supervisor que inicia, comprueba, registra, detiene y reinicia los procesos anteriores.

La imagen oficial `lsfusion/mycompany:6.2` publicada para Docker es `linux/amd64`; eso limita esa imagen en Apple Silicon, no convierte al JAR de lógica en un binario AMD64. Java, JAR y WAR son ejecutables por una JVM compatible; PostgreSQL y el runtime Java sí se deben elegir para la arquitectura del equipo. Por eso la ruta nativa evita la emulación de la imagen de lógica en tu Mac ARM64.

La documentación oficial de lsFusion describe instalaciones manuales y automáticas con servidor Java, PostgreSQL y Tomcat, además de Docker. MyCompany publica una ruta de instalación en Windows x64 y Linux; Rubrova debe empaquetar su propio runtime para macOS y para una instalación offline verificable, sin depender del instalador online de MyCompany.

### Investigación de proyectos y ramas que comparten las fuentes

La conclusión de la revisión es que **no necesitamos un fork distinto para quitar Docker**. El propio lsFusion 6.2 ya define instalación manual, automática y mediante Docker. El camino manual oficial levanta el servidor desde Java y `BusinessLogicsBootstrap`; Docker no es una dependencia del motor ni de MyCompany, sino una forma de empaquetar y aislar esos procesos.

Fuentes y proyectos comparados:

| Proyecto o referencia | Qué aporta | Decisión para Rubrova |
|---|---|---|
| [lsFusion platform 6.2](https://github.com/lsfusion/platform/tree/6.2) y [su guía de instalación](https://docs.lsfusion.org/v6/Install/) | Instalación manual nativa. El servidor se ejecuta como proceso Java; PostgreSQL y Tomcat funcionan como servicios del sistema. El [entrypoint Docker de la misma versión](https://github.com/lsfusion/platform/blob/6.2/server/entrypoint.sh) también ejecuta `BusinessLogicsBootstrap` con el classpath del servidor. | Reutilizar el mecanismo del propio motor; mantener el mismo JAR y el mismo classpath, no crear otro servidor. |
| [MyCompany 6.2](https://github.com/lsfusion-solutions/mycompany/tree/6.2) y [guía oficial de instalación](https://mycompany-docs.lsfusion.org/administration/installation/) | Instalación nativa documentada para Linux y un instalador Windows x64. La lógica MyCompany se puede incorporar al classpath del servidor lsFusion. | Mantener la lógica original, sumar los módulos Rubrova y desplegarla como instalación nativa. |
| [Guía oficial de desarrollo MyCompany](https://mycompany-docs.lsfusion.org/administration/development/) | Describe el trabajo sobre las fuentes, JDK, PostgreSQL, ejecución del servidor desde el IDE y carga de módulos propios. | Reutilizar el flujo directo de desarrollo; no hace falta convertir cada ciclo de prueba en una compilación de imagen Docker. |
| [NikitaKolotushkin/lsfusion-myCompany](https://github.com/NikitaKolotushkin/lsfusion-myCompany) | Clon de MyCompany con `compose.yaml` y README que instruye `docker-compose up -d`; no aporta un lanzador nativo sin Docker. | No importar su configuración de despliegue. |
| [ichavchavadze/lsfusion-aggregate](https://github.com/ichavchavadze/lsfusion-aggregate) | Integra plataforma, MyCompany, samples y plugin mediante Git subtrees y sincroniza las fuentes conservando su historial. | Es una referencia útil para sincronización y trazabilidad del código fuente, no para ejecutar el servidor. Rubrova ya usa snapshots fijados en `platform/source-lock.json`. |
| [laigor/lsfusion-mycompany](https://github.com/laigor/lsfusion-mycompany) y [nd989/mycompany](https://github.com/nd989/mycompany) | Copias con instrucciones de instalación nativa o manual, pero sus POM ya apuntan a 7.0-SNAPSHOT. La rama `v6` de MyCompany también avanzó a 6.3-SNAPSHOT. | No transplantar sus cambios de build a nuestro fork 6.2: cambian la versión de plataforma y pueden introducir incompatibilidades. |

La búsqueda de repositorios públicos y forks relevantes no es una prueba de que no exista ningún despliegue privado o no indexado. Sí alcanza para una decisión de ingeniería: no encontré un fork público de lsFusion/MyCompany 6.2 cuya modificación nativa justifique sustituir el mecanismo oficial. Los forks revisados que sí pudimos inspeccionar son ejemplos de Docker, espejos de código o versiones posteriores; ninguno aporta una pieza de runtime mejor que la vía manual del proveedor.

### Aprendizajes que aplicamos

1. El servidor no se debe reescribir ni envolver en un microservicio Python. Python sólo supervisa procesos; lsFusion sigue ejecutando la lógica y PostgreSQL conserva los datos.
2. El orden correcto es PostgreSQL listo → `BusinessLogicsBootstrap` inicializado → RMI disponible → `onStarted` finalizado → Tomcat/cliente web disponible. Un puerto abierto o una respuesta HTTP temprana no es suficiente.
3. El servidor debe trabajar con una carpeta de datos exclusiva y persistente de Rubrova. El lanzador no puede adoptar ni detener una instalación PostgreSQL ajena.
4. En Apple Silicon hay que usar Java y PostgreSQL nativos ARM64. El hecho de que la imagen MyCompany 6.2 de Docker publique `linux/amd64` no impide ejecutar el JAR de lógica desde una JVM ARM64.
5. El código de la plataforma y MyCompany debe seguir ligado al SHA 6.2 registrado. No mezclaremos soluciones de 6.3/7.0 para solucionar el método de arranque.

## 4. Prototipo de supervisor nativo y límites actuales

Ya existe `scripts/platform/run-local-native-preview.py`. Usa Python estándar como **supervisor**, no como sustituto del servidor lsFusion, de la lógica MyCompany, de PostgreSQL ni de Tomcat. Descubre Java 21 y PostgreSQL 18, prepara un clúster separado, descarga Tomcat 9 con SHA-512 verificado, despliega el WAR y lanza el servidor Java directamente.

El prototipo ya aplica varias protecciones: enlaza la web y PostgreSQL sólo a `127.0.0.1`, cambia el host/puerto RMI del `web.xml`, verifica que el clúster PostgreSQL corresponda al directorio privado de Rubrova, no detiene una instancia PostgreSQL que ya estaba en marcha y espera el mensaje de arranque, RMI y finalización de `onStarted` antes de iniciar Tomcat. La autenticación PostgreSQL `trust` queda limitada a este clúster local de desarrollo; **no es la configuración del instalador productivo**, que debe usar SCRAM y el almacén seguro del sistema operativo.

Las pruebas unitarias de `scripts/platform/test_runtime_native_preview.py` cubren la espera de arranque, el aislamiento de PostgreSQL, el enlace a loopback y la validación de rutas del WAR. Estas pruebas validan el supervisor; **no demuestran todavía que toda la aplicación haya arrancado y completado una venta nativa**. No presentar el prototipo como producto aceptado ni como instalador listo para uso diario.

El prototipo actual ya realiza el ciclo de desarrollo: detecta Java 21 y PostgreSQL 18, valida Tomcat 9.0.124, crea el clúster privado, inicia PostgreSQL, ejecuta `BusinessLogicsBootstrap`, espera el marcador de inicio, RMI y finalización de `onStarted`, inicia Tomcat y espera la respuesta web. También supervisa los procesos mientras está abierto, detiene el árbol de Tomcat/Java y sólo detiene el clúster PostgreSQL si lo inició ese mismo proceso. La base queda persistida entre ejecuciones.

El proceso de CI nativo ya está incorporado: compila los JAR/WAR en otro job, los entrega al smoke sin Docker, prepara PostgreSQL 18 y Java 21, bloquea la salida externa y comprueba el acceso con Chromium. La primera aceptación nativa se limita al arranque, login y navegación; **todavía falta mover el fixture comercial y probar venta, pago, stock, caja, cierre y reinicio**. Docker ya no debe ser requisito para avanzar en las pruebas del POS.

Para macOS, Postgres.app y Homebrew son opciones para disponer de las herramientas PostgreSQL 18 nativas. El supervisor admite indicar el directorio con `RUBROVA_POSTGRES_BIN` o `local_runtime.postgres_bin`; admite una ruta explícita de Tomcat en `local_runtime.tomcat_home` y verifica que sea la versión 9.0.124 fijada. La primera descarga de Tomcat requiere conexión; después se puede ejecutar con `--offline`.

El prototipo sigue siendo sólo de desarrollo: PostgreSQL utiliza autenticación `trust` limitada a loopback. Para el instalador comercial hay que incorporar Java/PostgreSQL/Tomcat y todos los recursos, utilizar SCRAM y el almacén seguro del sistema operativo, y no exigir que el usuario instale Python ni herramientas de compilación.

## 5. Panel de configuración siempre disponible

El selector no debe vivir exclusivamente dentro del POS: si el servidor no arranca, el operador igual necesita abrir Configuración, ver logs, corregir el destino y volver a iniciar.

La interfaz final tendrá dos accesos al mismo estado:

- **Rubrova Control**, una aplicación/menú independiente que puede seguir abierto aunque el servidor esté detenido. Desde allí se ve el destino activo, estado de PostgreSQL/servidor/cliente, URL, logs, diagnóstico, inicio/detención y configuración.
- **Administración dentro de Rubrova**, con un acceso a la misma configuración para que un administrador pueda consultar o preparar cambios mientras opera el sistema.

La app de control será independiente del proceso servidor. Primero se construirá y probará el backend supervisor en Python; después se lo empaquetará para cada sistema operativo y se conectará a una interfaz nativa sencilla. No se hará depender el producto de que el usuario tenga Python instalado: el intérprete y los recursos de soporte se incorporarán al paquete final o se utilizará un lanzador equivalente.

El archivo de configuración no contendrá contraseñas, tokens ni secretos. Esos datos irán a Keychain en macOS, Credential Manager/DPAPI en Windows o al almacén seguro correspondiente en Linux. La configuración se escribe de manera atómica y conserva la anterior ante un error.

## 6. Cambiar de destino sin perder datos

El control de ejecución estará disponible en todo momento, pero cambiar de destino no debe ser un simple cambio de URL cuando hay datos en dos bases distintas.

- **Native local ↔ Docker local:** cada runtime puede tener su propio clúster PostgreSQL. No se deben montar los archivos de datos nativos de macOS dentro de PostgreSQL Linux ni compartir el mismo directorio de base entre sistemas operativos. El cambio usará backup lógico y restore validado con versión compatible.
- **Local ↔ remoto:** requiere definir qué instalación es la autoridad de ventas, pagos, stock y caja. Si existe una cola de sincronización pendiente, no se permite cambiar a ciegas ni sobrescribir el estado más reciente.
- **Remote → local:** debe obtenerse una exportación/backup consistente del servidor remoto y restaurarse en el nodo local; después se comprueban saldos, ventas, pagos, turnos y stock.
- **Local → remote:** debe hacerse la misma validación en sentido inverso. Las operaciones locales no confirmadas o pendientes no pueden desaparecer.

Antes de aplicar un cambio, el panel debe mostrar qué base se usará, crear un backup, comprobar espacio, detener servicios, migrar, iniciar el nuevo destino y ejecutar validaciones de lectura y conciliación. Si algo falla, conserva el destino anterior y ofrece volver atrás. El selector actual sólo guarda preferencias; no afirma que la migración esté implementada.

## 7. Versiones y compatibilidad

- Java 21 es la línea del build del fork actual; se probará y empaquetará la misma versión de runtime.
- PostgreSQL 18 es la versión fijada actualmente en los artefactos de Rubrova.
- lsFusion 6.2 usa un cliente web basado en APIs Java EE `javax.*`; por eso el runtime actual emplea Tomcat 9, no se debe cambiarlo a Tomcat 10/11 sin probar la migración del cliente.
- Riesgo de mantenimiento: Apache anunció el fin de soporte de Tomcat 9.0.x para el 31 de marzo de 2027. Debemos planificar y probar la compatibilidad del cliente lsFusion con la siguiente rama soportada antes de esa fecha; no debemos ignorar ese vencimiento ni forzar una actualización no validada.

## 8. Pruebas que deben ejecutarse sin Docker

El **camino principal de desarrollo y CI** será el runtime nativo. Docker queda como verificación secundaria de empaquetado, compatibilidad de imágenes e aislamiento; no debe bloquear cada cambio funcional.

El smoke nativo debe:

1. preparar Java 21, PostgreSQL 18 y Tomcat 9 en el runner;
2. construir server JAR, MyCompany logic JAR y client WAR desde las fuentes fijadas de Rubrova;
3. iniciar un clúster PostgreSQL temporal con un directorio exclusivo;
4. iniciar el servidor y Tomcat mediante el supervisor nativo;
5. inyectar los mismos fixtures sintéticos de POS y de integración que hoy se agregan al Compose efímero;
6. iniciar el proveedor HTTP simulado como proceso local y abrir la UI con Chromium;
7. ejecutar una venta de efectivo, validar factura/pago/caja/stock/turno en los datos persistidos;
8. reiniciar servidor y cliente sin borrar PostgreSQL y volver a conciliar sin duplicar operaciones;
9. bloquear la salida a Internet y demostrar que las funciones locales siguen funcionando; la llamada al proveedor simulado debe permanecer en loopback;
10. detener únicamente los procesos de prueba y borrar exclusivamente los datos temporales de CI.

También simplificaremos el escenario de fallos externos: el smoke actual usa Toxiproxy como un proxy de paso hacia `mock-provider` (crea el proxy y consulta su API, pero no configura toxics). El servidor simulado ya expone directamente rutas lentas y respuestas HTTP 400/401/403/408/409/429/503. Para el camino nativo se lo consultará en `127.0.0.1`; dentro de Docker, en `mock-provider:18765`. Así eliminamos una dependencia innecesaria sin perder los escenarios que medimos.

La primera puerta de CI será el smoke funcional nativo en Linux. Después se repetirá en macOS ARM64 y Windows x64. El runtime sólo se marcará aprobado cuando pase el ciclo completo y no sólo el diagnóstico de dependencias o la compilación.

## 9. Estado real y siguiente entrega

**Implementado:** esquema JSON y CLI de configuración, supervisor de procesos nativo, clúster PostgreSQL privado, validación de Tomcat/RMI, pruebas unitarias y job CI nativo sin Docker que bloquea la salida externa y comprueba login/navegación.

**Pendiente:** resultado verde del smoke nativo integrado (build más arranque/login), migrar los fixtures de venta para aceptar factura/pago/stock/caja/cierre/reinicio en native, aceptación real en tu Mac y Windows, panel de control, empaquetado autónomo, instalación offline y migración segura entre bases.

El primer objetivo de prueba será tu MacBook Air: ejecutar los mismos JAR/WAR del proyecto en Java 21 nativo ARM64, con PostgreSQL 18 y Tomcat local, sin Docker Desktop. Después incorporaremos el paquete autónomo para una PC limpia y Windows.

## Referencias técnicas

- lsFusion, [opciones de instalación: manual, automática y Docker](https://docs.lsfusion.org/v6/Install/).
- lsFusion, [instalación de producción](https://docs.lsfusion.org/Execution_auto/).
- MyCompany, [guía de instalación](https://mycompany-docs.lsfusion.org/administration/installation/).
- PostgreSQL, [plataformas soportadas](https://www.postgresql.org/docs/18/supported-platforms.html) y [paquetes macOS](https://www.postgresql.org/download/macosx/).
- Postgres.app, [descargas de PostgreSQL 18](https://postgresapp.com/downloads.html).
- Apache Tomcat, [Tomcat 9.0.124](https://downloads.apache.org/tomcat/tomcat-9/v9.0.124/bin/) y [fin de soporte de Tomcat 9.0.x](https://tomcat.apache.org/tomcat-9.0.x-eos).
- Eclipse Temurin, [Java 21 para macOS ARM64 y Windows x64](https://adoptium.net/temurin/releases/?version=21).
