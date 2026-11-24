# Compatibilidad con macOS

**Revisión:** 20 de noviembre de 2026.
**Objetivo:** permitir trabajar con Rubrova desde una MacBook sin confundir compatibilidad del repositorio, equipo cliente y servidor.

## Qué está cubierto

- Los scripts de preparación y staging se ejecutan con Bash en macOS.
- El preparador usa `~/Library/Caches/Rubrova/platforms/mycompany-6.2` como caché predeterminada; respeta `RUBROVA_CACHE_DIR` y `XDG_CACHE_HOME`.
- El staging Docker puede copiar la extensión y actualizar `settings.properties` sin iniciar contenedores.
- La CI agrega un runner macOS 26 Apple Silicon para ejecutar pruebas estáticas, probar las herramientas BSD, ejercitar el staging y descargar/verificar el JAR y el Compose contra sus SHA-256 fijados.
- Una MacBook puede utilizarse como puesto cliente del sistema web cuando el servidor se encuentre disponible en un equipo compatible de la red.

La primera ejecución del workflow [44785005509](https://github.com/JavierGrecco/Rubrova/actions/runs/44785005509) terminó correctamente en Linux, Windows y macOS ARM64. Sus logs permitieron fijar el SHA-256 del Compose oficial (`4b7eeb62c92a4701f46f18255c290f9227ab9694986aa82e8034b2ea8a3d2def`); la segunda ejecución desde caché devolvió la misma huella.

La CI no instala MyCompany, no inicia el Compose y no certifica periféricos, navegador ni una jornada POS completa.

## Diferencia entre Intel y Apple Silicon

| Equipo | Preparación y herramientas | Servidor MyCompany 6.2 local | Estado |
|---|---|---|---|
| Mac Intel (`x86_64`) | Bash, `curl` y `shasum`; staging Docker | La imagen de lógica `linux/amd64` coincide con la arquitectura de CPU del host | Preparación cubierta por CI macOS ARM64 y smoke test; runtime todavía pendiente de aceptación |
| Mac Apple Silicon (`arm64`) | Bash, `curl` y `shasum`; staging Docker | La imagen `lsfusion/mycompany:6.2` sólo publica `linux/amd64`; requiere emulación para ejecutarla localmente | Preparación y staging cubiertos por CI ARM64; runtime emulado todavía no aceptado |

Las imágenes `lsfusion/server:6.2` y `lsfusion/client:6.2` publican ARM64, pero eso no vuelve ARM64 al stack completo mientras la imagen de lógica MyCompany siga siendo AMD64.

Docker Desktop permite ejecutar contenedores AMD64 en Apple Silicon mediante emulación. Para Rubrova sigue siendo una modalidad experimental: sirve para que puedas abrir y probar el POS localmente, pero no equivale a soporte nativo ni a aceptación productiva. La vista previa usa un override temporal que fija las imágenes de aplicación en `linux/amd64`, y publica el navegador y RMI sólo en `127.0.0.1`. El Compose oficial descargado no se modifica. Para acelerar la emulación, Docker indica activar Rosetta bajo Apple Virtualization Framework; Docker VMM no admite actualmente Rosetta. Consultá [los ajustes de Docker Desktop](https://docs.docker.com/desktop/settings-and-maintenance/settings/) y [Virtual Machine Manager](https://docs.docker.com/desktop/features/vmm/).

Referencias oficiales: [GitHub-hosted runners](https://docs.github.com/en/actions/reference/runners/github-hosted-runners), [Docker Desktop para Mac](https://docs.docker.com/docker-for-mac/install/), [ajustes de Docker Desktop](https://docs.docker.com/desktop/settings-and-maintenance/settings/) y [Virtual Machine Manager](https://docs.docker.com/desktop/features/vmm/).

## Comprobaciones locales desde una MacBook

No necesitás instalar MyCompany ni tener Docker para validar los archivos del proyecto. Con Git, Bash, Python 3 y Node.js 24:

```bash
git pull --ff-only
bash -n scripts/platform/prepare-mycompany-6.2.sh
bash -n scripts/platform/deploy-mycompany-6.2.sh
node --test scripts/platform/validate-mycompany-extension.test.mjs
bash scripts/platform/test-deploy-mycompany-6.2.sh
```

Para descargar el JAR y el Compose oficial y verificar el SHA-256 del JAR:

```bash
bash scripts/platform/prepare-mycompany-6.2.sh
```

Este comando no ejecuta el instalador, no instala MyCompany y no inicia Docker. Si no querés descargar todavía los artefactos, omitilo: la CI macOS hace esa comprobación de manera independiente.

Para revisar la arquitectura del equipo:

```bash
uname -m
```

`arm64` identifica Apple Silicon; `x86_64` identifica Intel.

## Probar Rubrova localmente en Apple Silicon

La vista previa está preparada en `scripts/platform/run-local-preview-macos.sh`. Necesita Docker Desktop, Docker Compose 2.24.4 o superior y los tres artefactos compilados en `vendor/platform/server/target`, `vendor/mycompany/target` y `vendor/platform/web-client/target`. También instala Chromium/Playwright en una caché del usuario; no instala MyCompany en macOS ni modifica los módulos versionados.

Desde la raíz del repositorio:

```bash
git pull --ff-only
bash scripts/platform/run-local-preview-macos.sh
```

El script construye las imágenes propias desde tus artefactos, descarga y verifica el Compose oficial, despliega la extensión en una carpeta temporal, crea una base nueva con una caja y un producto sintéticos, ejecuta el recorrido de aceptación, reinicia servidor y cliente y comprueba la persistencia de factura, pago, caja, stock y turno cerrado. Si termina correctamente, deja los contenedores y la base encendidos para que puedas seguir probando en `http://127.0.0.1:8080`. La captura inicial queda en el Escritorio como `rubrova-local-preview.png`.

El usuario inicial de la base sintética es `admin` sin contraseña, sólo para esta prueba aislada. No cargues datos reales ni habilites acceso desde la LAN. El simulador HTTP de fallos se ejecuta como un contenedor dentro de la misma red Docker interna que el runtime; esa red no tiene salida a Internet y el puerto del simulador no se publica en el host. La prueba comprueba también que los servicios no queden conectados a otra red con salida externa. La preparación (descarga de Compose, imágenes base y dependencias) todavía puede requerir Internet; esta prueba demuestra aislamiento durante la ejecución, no una instalación inicial offline.

Al terminar, el propio script imprime un comando único para detener los contenedores, borrar los volúmenes y eliminar la carpeta temporal. No lo ejecutes hasta terminar de probar. Si faltan artefactos compilados, el script imprime los dos comandos Maven necesarios para generarlos.

En Apple Silicon el arranque puede ser lento y sigue siendo emulado; esta prueba no certifica rendimiento, soporte nativo ni producción. En Mac Intel, el mismo script funciona sin emulación ARM64.

## Usar una MacBook como equipo cliente

Cuando MyCompany esté instalado y asegurado en el equipo anfitrión, se podrá abrir su cliente web desde el navegador de la MacBook mediante la dirección local del servidor. El acceso debe limitarse a la red privada, con contraseña de administración cambiada y firewall configurado. La aceptación final debe comprobar Safari/Chrome, lector, impresora, cajón, balanza y terminal que realmente vayamos a utilizar.

Esto permite trabajar desde Mac aunque el servidor POS/ERP esté alojado en un equipo Windows x64 o Linux compatible. No requiere que el proceso de base de datos ni el servidor de lógica se ejecuten dentro de macOS.

## Qué falta antes de declarar compatibilidad completa

1. Verificar el Compose fijado en futuros entornos y revisar los tags/digests de sus imágenes antes de iniciar contenedores.
2. Instalar MyCompany 6.2 en un anfitrión x64 compatible y demostrar que carga `RubrovaCustom`, `RubrovaPOSLocalization` y `es_AR`.
3. Probar el stack completo en Apple Silicon mediante emulación, o confirmar que la Mac se usará como cliente de un anfitrión x64.
4. Aceptar la operación real en navegador y periféricos, incluidos reinicio, backup y restauración.

Hasta completar esos puntos, macOS queda cubierto como entorno de desarrollo/validación y como equipo cliente previsto; no se declara un servidor MyCompany ARM64 nativo.