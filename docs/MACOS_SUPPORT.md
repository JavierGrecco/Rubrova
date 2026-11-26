# Compatibilidad con macOS

**Revisión:** 26 de noviembre de 2026.
**Objetivo:** ejecutar el mismo runtime Rubrova en el equipo local sin Docker, sin confundir la compatibilidad del repositorio con la aceptación del servidor nativo.

## Decisión actual

El runtime nativo sin Docker es la ruta prioritaria de desarrollo local y ya superó un smoke integrado de Apple Silicon en CI. La revisión aceptada es `main` en el commit [`f545c90`](https://github.com/JavierGrecco/Rubrova/commit/f545c907b12a9eed4cf5e532edd3434babb64139).

En [run 45847755524](https://github.com/JavierGrecco/Rubrova/actions/runs/45847755524), el runner macOS ARM64 ejecutó Java 21, PostgreSQL 18, lsFusion/MyCompany y Tomcat sin Docker. Chromium autenticó y navegó al POS; las sondas de inventario, compromisos y recepciones respondieron HTTP 200. Se verificó el export JSON de sólo lectura, una venta sintética por ARS 1.250, pago en efectivo, stock 10 → 9, cierre de turno y persistencia después de reiniciar. La instancia Demo utilizó otra base y puertos separados.

La prueba se ejecutó con salida externa habilitada: `RUBROVA_NATIVE_OFFLINE_ACCEPTANCE=not_tested`. Los jobs Linux nativo y Docker/Linux se omitieron en ese push. Por tanto, todavía no se certifica operación offline macOS, Windows nativo, instalación limpia, periféricos reales ni uso productivo. La prueba del runner tampoco sustituye la ejecución en el Mac físico del usuario.

El camino macOS sigue siendo:
- Java 21 ARM64 para el servidor y la lógica compilados desde Rubrova.
- PostgreSQL 18 ARM64 en un directorio privado persistente.
- Apache Tomcat 9.0.124 para el cliente web en loopback.
- Supervisor Python para arranque, verificación y parada sin borrar los datos.
- Docker no es requisito de ejecución local.

El smoke de plataforma también incorpora en esta revisión una prueba lógica de backup/restore: crear y verificar el paquete y restaurarlo en una base nueva. La copia cubre PostgreSQL únicamente; los documentos, adjuntos y demás archivos todavía no forman parte de un respaldo completo.

## Diferencia entre Intel y Apple Silicon

El servidor y la lógica de lsFusion/MyCompany se ejecutan como bytecode Java. El JAR no necesita una imagen de contenedor AMD64: lo ejecuta la JVM compatible con el equipo. Lo que sí debe ser nativo para el sistema y la arquitectura es Java, PostgreSQL y el propio Tomcat/entorno del sistema operativo.

| Equipo | Runtime nativo esperado | Estado |
|---|---|---|
| Mac Intel (`x86_64`) | Java 21 x64, PostgreSQL 18 x64, Tomcat 9 y Python | Supervisor implementado; aceptación completa pendiente |
| Mac Apple Silicon (`arm64`) | Java 21 ARM64, PostgreSQL 18 ARM64, Tomcat 9 y Python | Smoke integrado y exportación nativa aprobados en CI 45847755524; prueba en el Mac físico, modo offline, periféricos e instalación limpia pendientes |

La imagen Docker de lógica MyCompany 6.2 publica `linux/amd64`. Esto afecta a la ruta Docker sobre Apple Silicon y obliga a emular esa imagen. **No obliga a emular el JAR** cuando se ejecuta el runtime nativo descrito arriba.

## Requisitos para probarlo

Instalá o ubicá estos componentes en el equipo:

1. Java 21 para macOS en la arquitectura del Mac.
2. PostgreSQL 18 con sus herramientas `initdb`, `pg_ctl`, `pg_isready`, `createdb` y `psql`. Postgres.app o Homebrew son opciones para el entorno de desarrollo.
3. Python 3.
4. Los artefactos compilados del fork: `server.jar`, `logics.jar` y `client.war`.
5. Tomcat 9.0.124. El supervisor lo descarga del sitio oficial de Apache y valida SHA-512 la primera vez, o utiliza una instalación ya preparada y configurada.

No se necesita Docker Desktop ni Docker Compose para esta modalidad. Tampoco se debe instalar el servidor de lógica MyCompany desde una imagen Docker.

## Preparar y ejecutar el runtime nativo

**Inicio sencillo:** desde Finder, hacé doble clic en `Iniciar Rubrova.command`, en la raíz del repositorio. El acceso directo verifica que Java 21 y PostgreSQL 18 coincidan con la arquitectura del Mac, detecta si hay que reconstruir los artefactos de la revisión actual, prepara la configuración local, ejecuta `doctor` e inicia el supervisor nativo. Abre el navegador cuando el cliente web está listo. No instala paquetes del sistema ni usa Docker. Si faltan Java o PostgreSQL, muestra el requisito que hay que instalar; la primera compilación necesita Maven y puede descargar dependencias, y Tomcat puede necesitar una descarga inicial.

**Demostración aislada:** hacé doble clic en `Iniciar Rubrova - Demo.command`. Prepara `demo-runtime-config.json`, usa la carpeta de datos `demo-preview` y los puertos 55433/17653/8081. En esa base separada agrega una caja, un artículo de muestra y un stock inicial de 10 unidades, con identificadores `rubrova-demo`. No toca la base normal ni activa los fixtures de aceptación de CI. Las ventas realizadas en esta demostración se conservan en esa base de demostración.

También se puede hacer todo manualmente:

Desde la raíz del repositorio, confirmar la arquitectura:

```bash
uname -m
java -version
```

Para Postgres.app, la ruta habitual de herramientas para PostgreSQL 18 es:

```bash
export RUBROVA_POSTGRES_BIN="/Applications/Postgres.app/Contents/Versions/18/bin"
```

Si utilizás Homebrew, indicá el directorio `bin` de `postgresql@18`. El supervisor no toma posesión de una instancia personal que ya esté corriendo: crea y utiliza un clúster propio bajo los datos de Rubrova, y sólo detiene PostgreSQL cuando él mismo lo inició.

Crear la configuración no instala servicios ni migra datos:

```bash
python3 scripts/platform/runtime-config.py init
python3 scripts/platform/runtime-config.py validate
```

Compilar el servidor, la lógica y el cliente web desde las fuentes vendorizadas:

```bash
mvn -B -ntp -f build/rubrova/pom.xml -Passemble -DskipTests package
mvn -B -ntp -f vendor/platform/pom.xml -pl server,web-client -am -DskipTests package
```

El build Maven puede necesitar Internet la primera vez para descargar dependencias. Después, revisar las herramientas y el Tomcat:

```bash
python3 scripts/platform/run-local-native-preview.py doctor
```

Iniciar el servidor, la base y el cliente web:

```bash
python3 scripts/platform/run-local-native-preview.py --no-open start
```

La URL local es `http://127.0.0.1:8080/login`. Presioná Ctrl+C para cerrar los procesos. La base de datos se conserva para el siguiente inicio; no se borra ni se recrea en cada ejecución. Los logs se guardan en la carpeta local de datos de Rubrova.

### Primer inicio e inicio offline

Si Tomcat 9.0.124 todavía no está disponible en la caché o en la ruta configurada, la primera ejecución necesita Internet para descargarlo y verificar su SHA-512. También hacen falta los artefactos ya compilados y las dependencias Maven. Con Tomcat y los artefactos preparados, se puede impedir cualquier descarga durante el arranque:

```bash
python3 scripts/platform/run-local-native-preview.py --offline doctor
python3 scripts/platform/run-local-native-preview.py --offline --no-open start
```

Esto demuestra el inicio sin descargar dependencias que falten; **no significa que el instalador completo ni la primera instalación estén todavía disponibles offline**. Esa entrega requiere empaquetar PostgreSQL, Java, Tomcat, recursos, dependencias y migraciones en un instalador firmado y probado en un equipo limpio.

La base de esta vista previa es de desarrollo. No debe cargarse información comercial real ni exponerse a la LAN. El clúster usa autenticación `trust` sólo en loopback para el entorno local de pruebas; el instalador productivo deberá configurar SCRAM, guardar credenciales en Keychain y aplicar firewall/permisos apropiados.

## Validación en CI y estado de aceptación

La puerta obligatoria de plataforma es el smoke macOS ARM64 nativo, después de compilar servidor, cliente GWT y lógica MyCompany desde el mismo SHA.

- **macOS ARM64 nativo:** [run 45847755524](https://github.com/JavierGrecco/Rubrova/actions/runs/45847755524), aprobado. Verificó Java 21 ARM64, PostgreSQL 18 ARM64, Tomcat, Chromium, login, exportación nativa, venta, pago, stock, cierre, reinicio/persistencia y Demo aislada. La conectividad externa estuvo habilitada.
- **Linux x86_64 nativo y Docker/Linux:** fueron omitidos en ese push (`skipped`). Se conservan como diagnósticos complementarios; no deben contarse como aprobados por el run actual.
- **Windows:** el trabajo reciente validó sintaxis de scripts PowerShell; no equivale a una instalación y aceptación funcional completa.

La continuidad offline en macOS sigue abierta. El run 45847755524 declara explícitamente `RUBROVA_NATIVE_OFFLINE_ACCEPTANCE=not_tested`. Linux nativo había completado históricamente pruebas con salida bloqueada en ejecuciones previas, pero esa evidencia no sustituye repetir la prueba sobre el SHA actual.

El usuario todavía debe ejecutar el runtime en el Mac físico. La compatibilidad del runner CI tampoco certifica Safari/Chrome, lector, impresora, cajón, balanza, terminal, rendimiento de una jornada ni recuperación en un equipo nuevo.

## Ruta Docker para empaquetado y validación CI

La vista previa `scripts/platform/run-local-preview-macos.sh` mantiene una opción Docker para reproducir el empaquetado localmente. Requiere Docker Desktop, Docker Compose 2.24.4 o superior y los artefactos compilados en `vendor/platform/server/target`, `vendor/mycompany/target` y `vendor/platform/web-client/target`. En Apple Silicon, el contenedor de lógica AMD64 se ejecuta por emulación; para desarrollar localmente se prioriza el runtime nativo descrito en esta guía.

En GitHub Actions, el diagnóstico Docker/Linux se ejecuta automáticamente en cada push o pull request que activa el workflow, pero su fallo no bloquea la aceptación nativa. En `45637101959` pasó el recorrido comercial. La prueba usa PostgreSQL y un simulador HTTP dentro de una red interna sin salida externa. No se necesita Toxiproxy como proxy de paso.

## Usar una MacBook como equipo cliente

Una Mac también puede utilizarse como puesto cliente si el servidor se encuentra en otro equipo de la LAN. El navegador accede a la URL del anfitrión; el acceso debe limitarse a la red privada, con contraseñas cambiadas y firewall configurado. La aceptación final debe comprobar Safari/Chrome, lector, impresora, cajón, balanza y terminal que realmente vayamos a utilizar.


## Prevalidación y arranque local sin Docker

Antes de compilar o iniciar el servidor, desde la raíz del repositorio:

```bash
bash scripts/platform/local-preflight.sh
python3 scripts/platform/run-local-native-preview.py doctor
```

La primera orden ejecuta pruebas rápidas compartidas con CI (Node, Python, contratos, fixtures y scripts); no levanta servicios. La segunda verifica Java 21, PostgreSQL 18, artefactos y configuración del runtime nativo. Si el diagnóstico está limpio, iniciá con:

```bash
bash "Iniciar Rubrova.command"
```

La alternativa manual es `python3 scripts/platform/run-local-native-preview.py --no-open start`. El entorno conserva una base aislada de desarrollo. No lo expongas a la LAN ni cargues datos reales. La prevalidación rápida no sustituye la carga real de módulos ni la prueba autenticada de la API.


## Qué falta antes de declarar compatibilidad completa

1. Repetir en tu Mac Apple Silicon el recorrido que ya pasó en CI, con Java 21 ARM64 y PostgreSQL 18 ARM64; verificar persistencia y logs locales.
2. Verificar el modo Demo aislado en el smoke nativo y repetir el recorrido en tu Mac físico con periféricos reales.
3. Repetir en macOS ARM64 una verificación del POS con la salida externa bloqueada. El smoke macOS actual deja esa condición abierta; Linux nativo ya completó el recorrido con egress bloqueado.
4. Repetir la aceptación en Windows x64, incluida la gestión de procesos y rutas.
5. Empaquetar e instalar en una PC limpia sin Internet; verificar firma, permisos, secretos, actualizaciones y backup/restore.
6. Aceptar navegador y periféricos reales, incluidos lector, impresora, cajón, balanza, terminal, reinicio, contingencias y restauración.

Hasta completar esos puntos, el runtime nativo es un prototipo de desarrollo prometedor, no una instalación productiva aprobada.
