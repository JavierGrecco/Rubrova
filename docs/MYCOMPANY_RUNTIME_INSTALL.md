# Instalación y carga de la extensión Rubrova — MyCompany 6.2

**Versión objetivo:** MyCompany 6.2 / lsFusion 6.x  
**Estado:** preparación multiplataforma y staging automatizados; la instalación real y el runtime siguen pendientes de ejecutarse en un equipo anfitrión.

Para el uso desde una MacBook, consultar también [Compatibilidad con macOS](MACOS_SUPPORT.md).

## Ruta recomendada para el primer piloto

Para comenzar, recomendamos el instalador oficial en un equipo Windows x64. Es la ruta más directa para levantar el sistema sin depender de Docker. El cliente web permite después operar desde otro equipo de la misma LAN, siempre que la contraseña administrativa y el firewall estén correctamente configurados.

Docker es una alternativa oficial, pero se debe inspeccionar el Compose y las arquitecturas de sus imágenes antes de iniciar contenedores.

## 1. Preparar los artefactos

En Windows, abrir PowerShell en el clon de Rubrova y ejecutar:

    powershell -ExecutionPolicy Bypass -File .\scripts\platform\prepare-mycompany-6.2.ps1

El script descarga el instalador y el JAR oficial a %LOCALAPPDATA%\Rubrova\platforms\mycompany-6.2, valida ambos SHA-256 y no ejecuta archivos.

En macOS/Linux se puede preparar el JAR y el Compose oficial. En macOS la caché predeterminada queda en `~/Library/Caches/Rubrova/platforms/mycompany-6.2` (se puede cambiar con `RUBROVA_CACHE_DIR` o `XDG_CACHE_HOME`):

    bash scripts/platform/prepare-mycompany-6.2.sh

El Compose correcto para MyCompany es:

    https://download.lsfusion.org/solutions/mycompany-docker/6.2/compose.yaml

No confundirlo con el Compose genérico de la plataforma lsFusion en /docker/6.2/compose.yaml: ese archivo no incorpora por sí solo el contenedor con la lógica de MyCompany. El directorio oficial de MyCompany 6.2 publica su archivo versionado, pero la descarga es de tipo binario; el preparador calcula el SHA-256 local y no inicia el stack.

## 2. Instalar de forma aislada

### Windows x64

1. Verificar que los archivos se descargaron con SHA-256 coincidente.
2. Ejecutar manualmente mycompany-6.2-x64.exe, revisar el instalador y completar la instalación.
3. Mantener el firewall activo y limitar los puertos 8080 y 7652 a localhost durante la primera validación.
4. Abrir http://localhost:8080.
5. Iniciar sesión con el usuario inicial indicado por la documentación del producto.
6. Cambiar inmediatamente la contraseña de admin. La guía oficial permite el acceso inicial con `admin` sin contraseña; esa condición se utiliza sólo en la base efímera de CI y nunca debe conservarse en una instalación real. No habilitar acceso LAN hasta cambiarla.

### Docker en macOS/Linux/Windows

1. Instalar Docker Engine o Docker Desktop con Docker Compose.
2. Preparar el directorio de trabajo con el Compose oficial MyCompany 6.2.
3. Leer el archivo y verificar los tags de sus imágenes. No usar latest, SNAPSHOT ni tags de otras series.
4. La documentación específica de MyCompany describe cuatro contenedores: PostgreSQL, servidor de aplicación, lógica MyCompany y cliente web.
5. Ejecutar docker compose config y revisar los puertos publicados antes de iniciar.
6. Iniciar sólo en la máquina local para la primera prueba. Cambiar la contraseña inicial de admin antes de abrir acceso a otros equipos.

**Arquitectura Apple Silicon:** Docker Hub publica `lsfusion/mycompany:6.2` sólo para `linux/amd64`; las imágenes `lsfusion/server:6.2` y `lsfusion/client:6.2` publican `amd64` y `arm64`. El stack no es nativo ARM64 de punta a punta. Docker Desktop puede ejecutar imágenes AMD64 mediante emulación, pero eso no convierte la combinación en una instalación soportada o aceptada por Rubrova: el rendimiento y la estabilidad deben medirse en el equipo real. No se debe forzar `platform: linux/amd64` ni cambiar imágenes del Compose sin comprobar el conjunto completo. En una MacBook Intel, `amd64` coincide con la arquitectura del host, aunque el runtime también sigue pendiente de aceptación.

## 3. Copiar el módulo Rubrova sin modificar el ERP

lsFusion permite cargar un módulo propio desde el classpath y establecer logics.topModule en settings.properties. Rubrova incorpora:

- RubrovaCustom.lsf, el punto de entrada que requiere MyCompany y RubrovaPOSLocalization.
- RubrovaPOSLocalization.lsf, que contiene los captions y overrides de presentación del POS.
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

## 5. Smoke test automatizado del runtime

El repositorio incorpora `scripts/platform/test-runtime-smoke.sh`. En Linux x86_64 con Docker Engine y Compose disponibles:

1. Descarga el JAR y el Compose oficiales y compara ambos SHA-256 con el lock.
2. Copia `RubrovaCustom`, `RubrovaPOSLocalization` y el ResourceBundle a `docker-server` sin editar el código upstream.
3. Valida la configuración con `docker compose config` y confirma al menos cuatro servicios.
4. Inicia el stack con un nombre de proyecto efímero y utiliza el mismo `compose.rubrova.override.yaml` que se entrega en la instalación Docker normal.
5. Añade un segundo override temporal que fija por digest las cuatro imágenes del runtime Linux x86_64, y compara cada imagen descargada contra el lock.
6. Comprueba dentro del contenedor que están montados los archivos Rubrova, que `settings.properties` contiene el punto de entrada, el idioma y el país, y que `JAVA_OPTS` del overlay compartido llegó al proceso Java.
7. Espera la respuesta web y el final de la inicialización de la lógica. La imagen MyCompany 6.2 inicializa 712 módulos base; la prueba exige al menos 714 al incorporar los dos módulos propios.
8. Espera a que el servidor escuche en TCP `7652` y complete `Executing onStarted action finished`; el puerto abierto y los módulos cargados no bastan si las acciones de inicio siguen corriendo.
9. Abre la aplicación con Chromium en locale `es-AR`, reintenta la carga mientras aparezca `NotBoundException` y, sólo en la base efímera de CI, inicia sesión con el usuario inicial `admin` sin contraseña. El test espera la transición a `/main`, tolera el reemplazo temporal del DOM por GWT y confirma el acceso cuando el menú queda estable. Luego navega a `Comercio` (módulo Retail) y abre `Punto de venta` en modo de sólo lectura. Guarda capturas del login, el menú, Comercio y el terminal sólo después de que desaparezca `Loading` y el contenido se mantenga estable en dos lecturas consecutivas. No abre turnos ni registra ventas.
10. En caso de error, muestra estado y registros; siempre detiene los contenedores, elimina los volúmenes y limpia los archivos temporales, incluso los generados con permisos de administrador.

La ejecución base del 20/11/2026 confirmó HTTP 200, ambos módulos Rubrova en la secuencia de inicialización, los cuatro digests y la limpieza completa. La inspección posterior confirmó un tercer estado: el puerto 7652 puede abrir mientras lsFusion todavía ejecuta `onStarted`; en ese momento el cliente puede seguir devolviendo `NotBoundException default/RemoteLogicsLoader`. El smoke test ahora espera el marcador `Executing onStarted action finished` antes de abrir Chromium. El acceso autenticado y la navegación a Comercio/Punto de venta ya tienen una prueba automatizada. La pantalla POS debe pasar además la espera de renderizado estable; el acceso al menú por sí solo no equivale a formulario cargado. Todavía no se abre un turno, registra una venta, procesa un cobro/devolución ni concilia stock. En macOS Apple Silicon no se ejecuta el servidor MyCompany 6.2 mediante emulación; esa plataforma está cubierta por las pruebas estáticas y el uso previsto como cliente web.

## 6. Criterio de finalización del Bloque 0

El bloque sólo se declara completado después de guardar evidencia de:

1. Instalación MyCompany 6.2 iniciada desde el artefacto verificado.
2. Versión de plataforma, PostgreSQL, imágenes y arquitectura registradas.
3. Contraseña inicial modificada y firewall configurado.
4. Módulo superior RubrovaCustom y dependencia RubrovaPOSLocalization cargados con éxito sin parchear upstream.
5. ResourceBundle es_AR detectado; los captions del POS y circuito crítico están traducidos y revisados, incluidos mensajes y filtros que se hayan identificado en la prueba.
6. Backup y restauración en una instancia limpia comprobados.
7. Reinicio de proceso y retorno a servicio documentados.

La CI que valida el lock y el esqueleto de extensión no reemplaza estas pruebas de ejecución.

## Fuentes oficiales

- [Release MyCompany 6.2 y hashes de los artefactos](https://github.com/lsfusion-solutions/mycompany/releases/tag/6.2)
- [Instalación Windows/Linux y acceso inicial](https://mycompany-docs.lsfusion.org/administration/installation/)
- [Compose oficial MyCompany 6.2](https://download.lsfusion.org/solutions/mycompany-docker/6.2/compose.yaml)
- [Instalación Docker de MyCompany](https://mycompany-docs.lsfusion.org/administration/installation-docker/)
- [Agregar módulos propios en MyCompany 6](https://mycompany-docs.lsfusion.org/v6/administration/development/)
- [Docker Hub — MyCompany](https://hub.docker.com/r/lsfusion/mycompany/tags)
- [Docker Hub — lsFusion Server](https://hub.docker.com/r/lsfusion/server/tags)
- [Docker Hub — lsFusion Client](https://hub.docker.com/r/lsfusion/client/tags)
