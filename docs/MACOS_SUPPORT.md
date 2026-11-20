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

Docker Desktop ofrece emulación AMD64 en Apple Silicon. Debe tratarse como una alternativa experimental para este piloto: la emulación puede afectar rendimiento y comportamiento, y la opción Docker VMM no admite actualmente la aceleración Rosetta. No vamos a modificar el Compose ni fijar `platform: linux/amd64` sin una prueba completa y reproducible.

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

## Usar una MacBook como equipo cliente

Cuando MyCompany esté instalado y asegurado en el equipo anfitrión, se podrá abrir su cliente web desde el navegador de la MacBook mediante la dirección local del servidor. El acceso debe limitarse a la red privada, con contraseña de administración cambiada y firewall configurado. La aceptación final debe comprobar Safari/Chrome, lector, impresora, cajón, balanza y terminal que realmente vayamos a utilizar.

Esto permite trabajar desde Mac aunque el servidor POS/ERP esté alojado en un equipo Windows x64 o Linux compatible. No requiere que el proceso de base de datos ni el servidor de lógica se ejecuten dentro de macOS.

## Qué falta antes de declarar compatibilidad completa

1. Verificar el Compose fijado en futuros entornos y revisar los tags/digests de sus imágenes antes de iniciar contenedores.
2. Instalar MyCompany 6.2 en un anfitrión x64 compatible y demostrar que carga `RubrovaCustom`, `RubrovaPOSLocalization` y `es_AR`.
3. Probar el stack completo en Apple Silicon mediante emulación, o confirmar que la Mac se usará como cliente de un anfitrión x64.
4. Aceptar la operación real en navegador y periféricos, incluidos reinicio, backup y restauración.

Hasta completar esos puntos, macOS queda cubierto como entorno de desarrollo/validación y como equipo cliente previsto; no se declara un servidor MyCompany ARM64 nativo.