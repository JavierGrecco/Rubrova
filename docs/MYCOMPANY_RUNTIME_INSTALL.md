# Instalación y carga de la extensión Rubrova — MyCompany 6.2

**Versión objetivo:** MyCompany 6.2 / lsFusion 6.x  
**Estado:** lsFusion 6.2 y MyCompany 6.2 están vendorizados; el build produce servidor, lógica y cliente desde nuestras fuentes. El smoke nativo macOS ARM64 fue aceptado en CI en el run #609, incluyendo el circuito sintético POS, pruebas de reinicio y la conciliación de cancelación de recepciones previstas. La aceptación comercial sigue limitada: quedan fuera la operación offline certificada, el equipo físico del usuario, Windows funcional, periféricos, datos comerciales reales y homologación productiva.

Para macOS, consultar también [Compatibilidad con macOS](MACOS_SUPPORT.md).

## Estado actual de aceptación del runtime

La validación integrada más reciente es [run #609](https://github.com/JavierGrecco/Rubrova/actions/runs/46113654320), revisión `12f041d93d361d16a938a48f803248e70e5b6e8f`. Terminó con `success`: prevalidación compartida, sintaxis PowerShell, compilación completa y empaquetado del runtime, además del smoke nativo macOS ARM64 sin Docker. El snapshot MyCompany/lsFusion protegido también quedó incorporado en [`32c5d75`](https://github.com/JavierGrecco/Rubrova/commit/32c5d759b07d7af0c620633bf87cc33b38b585ac); el workflow #28 está comprobando la compilación desde esas fuentes ya incorporadas y no se marca como aprobado hasta su conclusión.

El smoke #609 ejecutó Java 21 ARM64, PostgreSQL 18 ARM64, servidor lsFusion/MyCompany, Tomcat y Chromium. Confirmó login y navegación, operaciones sintéticas POS/inventario, APIs de reposición y recepciones, cancelación nativa de una recepción prevista, persistencia tras reinicio y aceptación de una segunda instancia Demo aislada. Los marcadores finales fueron `RUBROVA_NATIVE_SMOKE=passed` y `RUBROVA_NATIVE_DEMO_ACCEPTANCE=passed`.

La sonda de cancelación consultó el mismo conjunto de datos antes y después del reinicio. En la fase inicial registró `expected/planned/available = 3/2/8`; con `increaseAvailableStock=TRUE`, `3/-1/11`; después de cancelar la recepción, `0/2/8`; y al regenerar una recepción distinta por 4 unidades, `4/-2/12`. Ambas lecturas terminaron con `UI_REPLENISHMENT_RECEIPT_CANCELLATION_DIAGNOSTICS_VERIFIED=true`. El siguiente run incorpora también aserciones de `onHand` para cada fase.

Los alcances que siguen pendientes son: aceptación con egress bloqueado, prueba en el Mac físico, instalación/operación Windows, Linux/Docker, periféricos, conciliación con una base comercial real y homologación productiva. Esta ejecución no es una autorización para producción.

Límites de la ejecución:
- `RUBROVA_NATIVE_EGRESS_BLOCKED=false`; el modo offline macOS quedó `not_tested`.
- Linux nativo y Docker/Linux fueron `skipped`.
- Windows sólo validó sintaxis PowerShell; no es una instalación nativa funcional.
- La exportación de reposición aún debe conciliarse con una base comercial MyCompany real.
- Falta ejecutar el runtime en el Mac físico, con periféricos y una jornada supervisada.

## Ruta recomendada de desarrollo: runtime nativo

El servidor, la lógica y el interfaz web pueden ejecutarse directamente en el sistema operativo:

- Java 21 ejecuta `BusinessLogicsBootstrap` con `server.jar` y `logics.jar`.
- PostgreSQL 18 conserva los datos en un directorio independiente de Rubrova.
- Tomcat 9.0.124 publica el `client.war` en loopback.
- El supervisor Python controla el arranque y la detención; no reemplaza al servidor ni al motor de base de datos.

El runtime nativo es la ruta por defecto para desarrollo y la CI. Docker y Linux nativo quedan como diagnósticos manuales de empaquetado/compatibilidad; no se ejecutan automáticamente en cada PR ni son requisito para operar el POS local una vez instaladas sus dependencias.


## 1. Preparar los artefactos

En Windows, abrir PowerShell en el clon de Rubrova y ejecutar:

    powershell -ExecutionPolicy Bypass -File .\scripts\platform\prepare-mycompany-6.2.ps1

El script descarga el instalador y el JAR oficial a %LOCALAPPDATA%\Rubrova\platforms\mycompany-6.2, valida ambos SHA-256 y no ejecuta archivos.

En macOS/Linux se puede preparar el JAR y el Compose oficial. En macOS la caché predeterminada queda en `~/Library/Caches/Rubrova/platforms/mycompany-6.2` (se puede cambiar con `RUBROVA_CACHE_DIR` o `XDG_CACHE_HOME`):

    bash scripts/platform/prepare-mycompany-6.2.sh

El Compose correcto para MyCompany es:

    https://download.lsfusion.org/solutions/mycompany-docker/6.2/compose.yaml

No confundirlo con el Compose genérico de la plataforma lsFusion en /docker/6.2/compose.yaml: ese archivo no incorpora por sí solo el contenedor con la lógica de MyCompany. El directorio oficial de MyCompany 6.2 publica su archivo versionado, pero la descarga es de tipo binario; el preparador calcula el SHA-256 local y no inicia el stack.

## 2. Vista previa nativa de desarrollo sin Docker

Esta vista previa utiliza los mismos artefactos compilados desde `vendor/platform` y `vendor/mycompany`. No usa las imágenes oficiales de Docker ni modifica el código upstream.

Dependencias locales: Java 21, herramientas PostgreSQL 18 (incluidos `initdb` y `pg_ctl`), Python 3 y los artefactos `server.jar`, `logics.jar` y `client.war`. El supervisor descarga Tomcat 9.0.124 desde Apache y verifica SHA-512 en el primer inicio, salvo que ya esté instalado y configurado.

Antes de compilar hay que validar el snapshot vendorizado y aplicar dos veces los parches controlados. La segunda pasada debe ser idempotente; cualquier drift o estado parcial debe detener el build:

    bash scripts/platform/validate-vendored-sources.sh
    python3 scripts/platform/apply-rubrova-source-patches.py
    python3 scripts/platform/apply-rubrova-source-patches.py

Compilar desde la raíz del repositorio:

    mvn -B -ntp -f build/rubrova/pom.xml -Passemble -DskipTests package
    mvn -B -ntp -f vendor/platform/pom.xml -pl server,web-client -am -DskipTests package

Crear y validar preferencias:

    python3 scripts/platform/runtime-config.py init
    python3 scripts/platform/runtime-config.py validate

Comprobar dependencias e iniciar:

    python3 scripts/platform/run-local-native-preview.py doctor
    python3 scripts/platform/run-local-native-preview.py --no-open start

La vista previa sirve el cliente en `http://127.0.0.1:8080/login`. Presionar Ctrl+C detiene servidor, Tomcat y sólo el PostgreSQL iniciado por ese supervisor; la base local se conserva. Se puede ejecutar `--offline doctor` y `--offline --no-open start` cuando Tomcat ya está verificado en caché y los artefactos están compilados. El build Maven puede necesitar Internet en la primera preparación.

Esta modalidad sigue siendo un entorno de desarrollo: la configuración local de PostgreSQL usa autenticación `trust` sobre loopback, el usuario inicial de la base puede no tener contraseña y no debe exponerse a la LAN ni recibir datos reales. El instalador productivo deberá usar SCRAM, almacén de secretos del sistema operativo, firma y permisos correctos.

**Todavía no se acepta como instalación comercial:** completar la aceptación offline con egress bloqueado, probar el instalador y la operación en el Mac físico y Windows, validar periféricos y recuperación en una PC limpia, y ejecutar una jornada supervisada con datos reales.

## 3. Instalar de forma aislada

### Windows x64

1. Verificar que los archivos se descargaron con SHA-256 coincidente.
2. Ejecutar manualmente mycompany-6.2-x64.exe, revisar el instalador y completar la instalación.
3. Mantener el firewall activo y limitar los puertos 8080 y 7652 a localhost durante la primera validación.
4. Abrir http://localhost:8080.
5. Iniciar sesión con el usuario inicial indicado por la documentación del producto.
6. Cambiar inmediatamente la contraseña de admin. La guía oficial permite el acceso inicial con `admin` sin contraseña; esa condición se utiliza sólo en la base efímera de CI y nunca debe conservarse en una instalación real. No habilitar acceso LAN hasta cambiarla.

### Docker (alternativa secundaria y smoke manual)

1. Instalar Docker Engine o Docker Desktop con Docker Compose.
2. Preparar el directorio de trabajo con el Compose oficial MyCompany 6.2.
3. Leer el archivo y verificar los tags de sus imágenes. No usar latest, SNAPSHOT ni tags de otras series.
4. La documentación específica de MyCompany describe cuatro contenedores: PostgreSQL, servidor de aplicación, lógica MyCompany y cliente web.
5. Ejecutar docker compose config y revisar los puertos publicados antes de iniciar.
6. Rubrova fija PostgreSQL 18 por digest. Su directorio persistente es `./docker-db-pg18`, montado en `/var/lib/postgresql`; PostgreSQL 18 guarda allí los datos bajo `18/docker`. El override también espera el healthcheck `pg_isready` antes de iniciar el servidor lsFusion.
7. Si ya existe una instalación anterior, no borres ni renombres `docker-db`: el directorio de Rubrova para PostgreSQL 18 es nuevo y no migra automáticamente datos de PostgreSQL 17 o anteriores. Hacé un backup lógico y una migración validada antes de cambiar la base activa.
8. Iniciar sólo en la máquina local para la primera prueba. Cambiar la contraseña inicial de admin antes de abrir acceso a otros equipos.

**Arquitectura Apple Silicon:** la imagen Docker `lsfusion/mycompany:6.2` sólo publica `linux/amd64`, por lo que ese camino necesita emulación. En el runtime nativo el JAR de lógica se ejecuta sobre Java 21 ARM64; PostgreSQL y Tomcat también deben ser nativos para el equipo. Esa compatibilidad está prevista pero todavía falta aceptarla en la Mac real. No confundas la limitación de la imagen Docker con una limitación intrínseca del JAR.

## 3. Copiar el módulo Rubrova sin modificar el ERP

lsFusion permite cargar un módulo propio desde el classpath y establecer logics.topModule en settings.properties. Rubrova incorpora:

- RubrovaCustom.lsf, el punto de entrada que requiere MyCompany y los módulos propios.
- RubrovaPOSLocalization.lsf, que contiene los captions y overrides de presentación del POS.
- RubrovaIntegrationResilience.lsf, que concentra el manejo seguro de fallos de integraciones externas.
- RubrovaPaymentTerminals.lsf, que registra cuentas de proveedor, terminales, asignaciones a caja/medio, intenciones, intentos, eventos, reintegros y líneas de liquidación. Es una base de configuración y trazabilidad; todavía no ejecuta cobros reales.
- RubrovaReplenishmentExport.lsf, que expone cuatro acciones `@@api` autenticadas de solo lectura para inventario, compromisos de venta, recepciones y exportación consolidada. Sus contratos y fixtures pasaron el smoke nativo #609, incluida lectura posterior a reinicio; aún debe conciliarse con una base comercial MyCompany real antes de usarlo para sugerir compras reales.
- MyCompanyResourceBundle_es_AR.properties, con traducciones de recursos base y los identificadores `rubrova.*`.

Una limitación importante: varias cadenas del código 6.2 son literales ingleses en los módulos upstream. Los archivos ResourceBundle por sí solos sólo resuelven las cadenas que utilizan identificadores de localización. Por eso Rubrova cambia los captions necesarios mediante su propio `DESIGN` y claves entre llaves, sin editar los módulos originales. Los mensajes de error heredados y algunas etiquetas de filtros todavía no están traducidos; hay que registrarlos durante la prueba real y decidir si se resuelven con una extensión adicional o un parche de localización pequeño y mantenible.

### Docker

Con el Compose oficial descargado en un directorio, ejecutar:

    bash scripts/platform/deploy-mycompany-6.2.sh docker /ruta/al/directorio

El script crea o utiliza `docker-server`, copia los módulos y el ResourceBundle, actualiza `settings.properties` con el punto de entrada y el idioma español de Argentina, y copia `compose.rubrova.override.yaml` junto al Compose oficial. Si ya existía un archivo reemplazado, crea una copia `.rubrova-backup.*`. El override configura `JAVA_OPTS=-Dlogics.topModule=RubrovaCustom`, `USER_SETLANGUAGE=es` y `USER_SETCOUNTRY=AR`; así el servidor aplica la extensión y el ResourceBundle en el arranque. **El script no inicia ni reinicia contenedores.** Para aplicar la configuración, ejecutar desde la carpeta de instalación:

    docker compose -f compose.yaml -f compose.rubrova.override.yaml up -d

No ejecutar sólo `docker compose up -d`: ese comando no aplica el override de Rubrova.

### Linux nativo

Ejecutar desde el clon de Rubrova con permisos administrativos:

    sudo bash scripts/platform/deploy-mycompany-6.2.sh native

El script utiliza el classpath `/var/lib/lsfusion` y la configuración `/etc/lsfusion6-server/settings.properties`, rutas documentadas para lsFusion 6. Hace una copia de seguridad de settings, instala los módulos y el ResourceBundle, actualiza `logics.topModule`, `user.setLanguage=es` y `user.setCountry=AR`, y reinicia el servicio `lsfusion6-server`.

### Windows nativo

Abrir PowerShell como administrador. Localizar la configuración del servidor:

    Get-ChildItem "$env:ProgramFiles\lsFusion 6" -Filter settings.properties -Recurse -File

Si aparece más de un archivo, elegir el que utiliza el servicio lsFusion 6 Server. Ejecutar:

    powershell -ExecutionPolicy Bypass -File .\scripts\platform\deploy-mycompany-6.2.ps1 -SettingsPath "RUTA_COMPLETA\settings.properties"

El script copia los módulos y el ResourceBundle a `C:\Program Files\lsFusion 6\Server\lib`, respalda los archivos que pudiera reemplazar, configura `logics.topModule`, `user.setLanguage=es` y `user.setCountry=AR`, y reinicia el servicio si estaba activo. Si la instalación utiliza otra carpeta de classpath, pasarla mediante `-ModuleDirectory`.

## 4. Qué comprobar después del reinicio

No basta con que el servicio figure como activo. Confirmar:

- El servidor cargó RubrovaCustom sin errores de sintaxis, dependencias ni recursos duplicados.
- MyCompanyResourceBundle_es_AR.properties se detecta y la preferencia de idioma del usuario está configurada en español (Argentina).
- El cliente web abre y muestra las pantallas POS críticas.
- El acceso inicial de administración está protegido y sólo se exponen los puertos necesarios.
- Se obtiene una copia de seguridad y se restaura en una instancia limpia antes de introducir datos reales.

La traducción actual es parcial. No habilitar el uso diario mientras falten textos críticos o los errores estén en inglés.

## 6. Pruebas automatizadas del runtime

### Camino principal: smoke nativo

El workflow `.github/workflows/platform-extension.yml` construye los tres artefactos desde las fuentes Rubrova y ejecuta un smoke sin Docker en Linux x86_64. Instala Java 21 y PostgreSQL 18 nativos, prepara Tomcat, inicia el runtime con `run-local-native-preview.py`, bloquea la salida externa y comprueba que el login y la navegación en español siguen disponibles por loopback.

La ruta nativa ya ejecuta el smoke funcional con fixtures sintéticas en macOS ARM64. El run #609 pasó login, navegación y operaciones POS/inventario, verificó APIs de reposición y reservas de recepciones, reinició servidor y base y comprobó la persistencia. La conciliación de cancelación de una recepción prevista quedó verificada antes y después del reinicio. No se incluyen aún datos comerciales reales, modo offline bloqueado, hardware físico ni aceptación productiva.

### Camino secundario: smoke Docker manual

El repositorio conserva `scripts/platform/test-runtime-smoke.sh`. Se activa manualmente en GitHub Actions con el input `run_docker_smoke=true`, en Linux x86_64 con Docker Engine y Compose:

1. Descarga el JAR y el Compose oficiales y compara ambos SHA-256 con el lock.
2. Copia `RubrovaCustom`, `RubrovaPOSLocalization`, `RubrovaIntegrationResilience`, `RubrovaPaymentTerminals` y el ResourceBundle a `docker-server` sin editar el código upstream.
3. Valida la configuración con `docker compose config` y confirma al menos cuatro servicios.
4. Inicia el stack con un nombre de proyecto efímero y utiliza el mismo `compose.rubrova.override.yaml` que se entrega en la instalación Docker normal.
5. Añade un segundo override temporal que fija por digest las cuatro imágenes del runtime Linux x86_64, y compara cada imagen descargada contra el lock.
6. Comprueba dentro del contenedor que están montados los archivos Rubrova, que `settings.properties` contiene el punto de entrada, el idioma y el país, y que `JAVA_OPTS` del overlay compartido llegó al proceso Java.
7. Espera la respuesta web y el final de la inicialización de la lógica. MyCompany 6.2 inicializa 712 módulos base; el smoke exige 718: los cinco módulos propios de Rubrova (`RubrovaIntegrationResilience`, `RubrovaPOSLocalization`, `RubrovaPaymentTerminals`, `RubrovaReplenishmentExport`, `RubrovaCustom`) y un fixture de venta que sólo se agrega al directorio temporal de CI.
8. Espera a que el servidor escuche en TCP `7652` y complete `Executing onStarted action finished`; el puerto abierto y los módulos cargados no bastan si las acciones de inicio siguen corriendo.
9. Abre la aplicación con Chromium en locale `es-AR`, reintenta la carga mientras aparezca `NotBoundException` y, sólo en la base efímera de CI, inicia sesión con el usuario inicial `admin` sin contraseña. El test espera la transición a `/main`, tolera el reemplazo temporal del DOM por GWT y confirma el acceso cuando el menú queda estable. Luego navega a `Comercio → Punto de venta`, abre el turno sintético, busca un producto de prueba y lo agrega al recibo mediante la acción nativa de MyCompany. Confirma una venta por ARS 1.250 en efectivo, verifica factura/pago persistidos, entrada de stock 10 → 9 y conciliación de caja; luego cierra el turno y exige estado `CLOSED`, venta y efectivo conciliados. Finalmente simula timeout y respuestas HTTP 400/401/403/408/409/429/503, valida la clasificación/persistencia de ocho incidencias y confirma recuperación del proveedor. El puesto, el producto, las cuentas, los módulos de fixture y el resto de los datos son exclusivos de la base efímera; no se modifica el despliegue ni se incorporan datos de demostración al producto. Las capturas se guardan sólo tras estabilizarse el contenido.
10. En caso de error, muestra estado y registros; siempre detiene los contenedores, elimina los volúmenes y limpia los archivos temporales, incluso los generados con permisos de administrador.

La aceptación comercial completa [45503956218](https://github.com/JavierGrecco/Rubrova/actions/runs/45503956218) compiló servidor, lógica y cliente desde fuentes Rubrova y comprobó con Chromium login, venta por ARS 1.250, pago exacto en efectivo, factura/pago, stock 10 → 9, caja y cierre `CLOSED`. También reinició servidor/cliente sin borrar PostgreSQL y comprobó persistencia, ocho escenarios HTTP y recuperación. **Esa prueba se ejecutó en Docker.** Es evidencia complementaria, no sustituto del smoke nativo macOS ARM64 #609.

La ruta nativa es la puerta automática de CI; Docker/Linux permanece como diagnóstico manual y Windows sólo tiene validación sintáctica en el run #609. La compilación y el smoke nativo del run #609 terminaron correctamente, pero la segunda compilación que se ejecuta desde el árbol vendorizado integrado (#28) no debe considerarse aprobada hasta que concluya.

## 6. Criterio de finalización del Bloque 0

El bloque sólo se declara completado después de guardar evidencia de:

1. Instalación MyCompany 6.2 iniciada desde el artefacto verificado.
2. Versión de plataforma, PostgreSQL, imágenes y arquitectura registradas.
3. Contraseña inicial modificada y firewall configurado.
4. Módulo superior RubrovaCustom y sus dependencias RubrovaPOSLocalization, RubrovaIntegrationResilience y RubrovaPaymentTerminals cargados con éxito sin parchear upstream.
5. ResourceBundle es_AR detectado; los captions del POS y circuito crítico están traducidos y revisados, incluidos mensajes y filtros que se hayan identificado en la prueba.
6. Backup y restauración en una instancia limpia comprobados.
7. Reinicio de proceso y retorno a servicio documentados.

La compilación del fork y las pruebas unitarias tampoco reemplazan la aceptación de una instalación nativa con venta, persistencia, reinicio, bloqueo de Internet y restauración.

## Fuentes oficiales

- [Release MyCompany 6.2 y hashes de los artefactos](https://github.com/lsfusion-solutions/mycompany/releases/tag/6.2)
- [Instalación Windows/Linux y acceso inicial](https://mycompany-docs.lsfusion.org/administration/installation/)
- [Compose oficial MyCompany 6.2](https://download.lsfusion.org/solutions/mycompany-docker/6.2/compose.yaml)
- [Instalación Docker de MyCompany](https://mycompany-docs.lsfusion.org/administration/installation-docker/)
- [Agregar módulos propios en MyCompany 6](https://mycompany-docs.lsfusion.org/v6/administration/development/)
- [Docker Hub — MyCompany](https://hub.docker.com/r/lsfusion/mycompany/tags)
- [Docker Hub — lsFusion Server](https://hub.docker.com/r/lsfusion/server/tags)
- [Docker Hub — lsFusion Client](https://hub.docker.com/r/lsfusion/client/tags)
