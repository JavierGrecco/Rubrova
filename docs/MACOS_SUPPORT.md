# Compatibilidad con macOS

**Revisión:** 25 de noviembre de 2026.
**Objetivo:** ejecutar el mismo runtime Rubrova en el equipo local sin Docker, sin confundir la compatibilidad del repositorio con la aceptación del servidor nativo.

## Decisión actual

El camino previsto para macOS es nativo:

- Java 21 ejecuta el servidor lsFusion y la lógica MyCompany/Rubrova desde los JAR compilados por el propio repositorio.
- PostgreSQL 18 se ejecuta como proceso nativo y conserva los datos en una carpeta privada de Rubrova.
- Apache Tomcat 9.0.124 sirve el WAR del cliente web desde `127.0.0.1`.
- Python 3 supervisa el arranque, comprueba los procesos/puertos y los detiene sin borrar la base.
- Docker no es requisito para el runtime nativo local en macOS. En CI, la aceptación nativa macOS ARM64 es obligatoria; el smoke Docker/Linux se conserva como diagnóstico suplementario no bloqueante de empaquetado y despliegue.

El supervisor está en `scripts/platform/run-local-native-preview.py`. Sus pruebas unitarias cubren la espera de RMI y `onStarted`, el aislamiento de PostgreSQL, la versión exacta de Tomcat, la configuración RMI del WAR y el enlace de la web a loopback. En el run CI `45558057837`, el smoke completó en `macos-26` ARM64 el ciclo de abrir turno, vender, cobrar, conciliar stock, cerrar caja y simular fallos de integraciones con salida externa bloqueada. Confirma el runtime nativo en un runner Apple Silicon, pero no sustituye la prueba en tu Mac ni es un instalador final.

## Diferencia entre Intel y Apple Silicon

El servidor y la lógica de lsFusion/MyCompany se ejecutan como bytecode Java. El JAR no necesita una imagen de contenedor AMD64: lo ejecuta la JVM compatible con el equipo. Lo que sí debe ser nativo para el sistema y la arquitectura es Java, PostgreSQL y el propio Tomcat/entorno del sistema operativo.

| Equipo | Runtime nativo esperado | Estado |
|---|---|---|
| Mac Intel (`x86_64`) | Java 21 x64, PostgreSQL 18 x64, Tomcat 9 y Python | Supervisor implementado; aceptación completa pendiente |
| Mac Apple Silicon (`arm64`) | Java 21 ARM64, PostgreSQL 18 ARM64, Tomcat 9 y Python | Aceptación nativa comercial básica aprobada en CI `45548326798`; prueba en un Mac de usuario, periféricos e instalación limpia pendientes |

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

La CI ejecuta tres verificaciones de runtime distintas, a partir de los artefactos compilados desde la misma revisión:

- **macOS ARM64 nativo (obligatorio):** runner Apple Silicon `macos-26`, Java 21 ARM64, PostgreSQL 18 ARM64, Tomcat 9 y Chromium. En `45548326798` completó login, apertura de turno, venta, cobro, factura/pago, descuento de stock, cierre y conciliación de caja, además de persistir una incidencia simulada de integración.
- **Docker/Linux (diagnóstico no bloqueante):** ejecuta automáticamente el smoke POS dentro del runtime en contenedores, con PostgreSQL y proveedor HTTP simulado en red interna. En `45558057837` el cliente no respondió HTTP (`000`) durante 900 segundos, aunque el servidor cargó los 717 módulos y Tomcat desplegó la aplicación. El fallo se conserva para investigación y no bloquea el runtime nativo.
- **Linux x86_64 nativo (smoke complementario):** en `45558057837` inició Java, PostgreSQL y Tomcat, bloqueó la salida externa y completó el mismo ciclo POS: turno, venta, cobro, stock, cierre y pruebas de integración. No se necesita Docker para este recorrido.

El smoke macOS exitoso no bloqueó toda la salida externa, por lo que no demuestra por sí solo el comportamiento offline del navegador en esa plataforma. La verificación Linux nativa bajo bloqueo de salida todavía no completa el render del POS. No se debe confundir ninguna de estas pruebas con una instalación offline lista para una PC limpia.

La aceptación Docker histórica `45503956218` y la aceptación nativa macOS/Linux del run `45558057837` son evidencias separadas. Todas cubren venta por ARS 1.250, factura/pago, stock y cierre básico; faltan los restantes circuitos comerciales y la prueba de Docker bajo el nuevo diagnóstico.

## Ruta Docker para empaquetado y validación CI

La vista previa `scripts/platform/run-local-preview-macos.sh` mantiene una opción Docker para reproducir el empaquetado localmente. Requiere Docker Desktop, Docker Compose 2.24.4 o superior y los artefactos compilados en `vendor/platform/server/target`, `vendor/mycompany/target` y `vendor/platform/web-client/target`. En Apple Silicon, el contenedor de lógica AMD64 se ejecuta por emulación; para desarrollar localmente se prioriza el runtime nativo descrito en esta guía.

En GitHub Actions, el diagnóstico Docker/Linux se ejecuta automáticamente en cada push o pull request que activa el workflow, pero su fallo no bloquea la aceptación nativa. La prueba usa PostgreSQL y un simulador HTTP dentro de una red interna sin salida externa. Los escenarios HTTP se ejecutan contra el simulador local; no se necesita Toxiproxy como proxy de paso.

## Usar una MacBook como equipo cliente

Una Mac también puede utilizarse como puesto cliente si el servidor se encuentra en otro equipo de la LAN. El navegador accede a la URL del anfitrión; el acceso debe limitarse a la red privada, con contraseñas cambiadas y firewall configurado. La aceptación final debe comprobar Safari/Chrome, lector, impresora, cajón, balanza y terminal que realmente vayamos a utilizar.

## Qué falta antes de declarar compatibilidad completa

1. Repetir en tu Mac Apple Silicon el recorrido que ya pasó en CI, con Java 21 ARM64 y PostgreSQL 18 ARM64; verificar persistencia y logs locales.
2. Investigar el HTTP `000` del cliente en Docker/Linux y conservar sus logs/capturas sin bloquear el runtime nativo.
3. Investigar por separado el smoke Linux nativo: `PosDashboard` queda cargando cuando se bloquea la salida externa; revisar la dependencia de navegador que solicita `marked.min.js` y el error de registro del service worker sin asumir que ya son la causa.
4. Repetir la aceptación en Windows x64, incluida la gestión de procesos y rutas.
5. Empaquetar e instalar en una PC limpia sin Internet; verificar firma, permisos, secretos, actualizaciones y backup/restore.
6. Aceptar navegador y periféricos reales, incluidos lector, impresora, cajón, balanza, terminal, reinicio, contingencias y restauración.

Hasta completar esos puntos, el runtime nativo es un prototipo de desarrollo prometedor, no una instalación productiva aprobada.
