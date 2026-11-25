#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd)"

for command_name in docker python3 curl shasum; do
  command -v "$command_name" >/dev/null 2>&1 || {
    echo "Falta el comando requerido: $command_name" >&2
    exit 2
  }
done

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "Esta vista previa está pensada para ejecutarse desde macOS." >&2
  exit 2
fi

if ! docker info >/dev/null 2>&1; then
  echo "Docker Desktop no está iniciado. Abrí Docker Desktop y volvé a ejecutar este script." >&2
  echo "Instalación oficial: https://docs.docker.com/desktop/setup/install/mac-install/"
  exit 2
fi

docker compose version
COMPOSE_VERSION="$(docker compose version --short 2>/dev/null | sed 's/^v//')"
python3 - "$COMPOSE_VERSION" <<'PY'
import re
import sys

parts = tuple(int(x) for x in re.findall(r"\d+", sys.argv[1])[:3])
parts = (parts + (0, 0, 0))[:3]
if parts < (2, 24, 4):
    raise SystemExit(
        "La vista previa necesita Docker Compose 2.24.4 o superior para reemplazar "
        f"los puertos a localhost. Se detectó {sys.argv[1]!r}."
    )
PY

if [[ "$(uname -m)" == "arm64" ]]; then
  echo "Apple Silicon detectado: se necesita emulación AMD64 para MyCompany 6.2."
  echo "Docker Desktop: Settings > General > Virtual Machine Manager: Apple Virtualization Framework."
  echo "Activá también 'Use Rosetta for x86_64/amd64 emulation on Apple Silicon'."
  echo "No selecciones Docker VMM para esta prueba: hoy no admite Rosetta."
  emulated_arch="$(docker run --rm --platform linux/amd64 busybox:1.36 uname -m)"
  [[ "$emulated_arch" == "x86_64" ]] || {
    echo "Docker no pudo ejecutar un contenedor linux/amd64. Revisá Virtualization Framework y Rosetta." >&2
    exit 2
  }
fi

for artifact in \
  "$REPO_ROOT/vendor/platform/server/target/lsfusion-server-6.2.jar" \
  "$REPO_ROOT/vendor/mycompany/target/lsfusion-server-6.2.jar" \
  "$REPO_ROOT/vendor/platform/web-client/target/lsfusion-client-6.2.war"; do
  if [[ ! -s "$artifact" ]]; then
    echo "Falta el artefacto compilado: $artifact" >&2
    echo "Generalo una vez desde la raíz de Rubrova con:"
    echo "  mvn -B -ntp -f build/rubrova/pom.xml -Passemble -DskipTests package"
    echo "  mvn -B -ntp -f vendor/platform/pom.xml -pl server,web-client -am -DskipTests package"
    exit 2
  fi
done

PLAYWRIGHT_VENV="${RUBROVA_PLAYWRIGHT_VENV:-$HOME/Library/Caches/Rubrova/playwright-1.65.2}"
mkdir -p "$(dirname "$PLAYWRIGHT_VENV")"
if [[ ! -x "$PLAYWRIGHT_VENV/bin/python" ]]; then
  python3 -m venv "$PLAYWRIGHT_VENV"
fi
if ! "$PLAYWRIGHT_VENV/bin/python" -c 'import playwright' >/dev/null 2>&1; then
  "$PLAYWRIGHT_VENV/bin/python" -m pip install --disable-pip-version-check playwright==1.65.2
fi
"$PLAYWRIGHT_VENV/bin/python" -m playwright install chromium

SCREENSHOT_DIR="$HOME/Desktop"
[[ -d "$SCREENSHOT_DIR" ]] || SCREENSHOT_DIR="$HOME"

export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-rubrova-local-preview-$(date +%Y%m%d%H%M%S)}"
export RUBROVA_ALLOW_EXPERIMENTAL_MACOS_AMD64_EMULATION=true
export RUBROVA_KEEP_RUNTIME_STACK=true
export RUBROVA_KEEP_RUNTIME_WORK_DIR=true
export RUBROVA_RUNTIME_WORK_DIR="${RUBROVA_RUNTIME_WORK_DIR:-$HOME/Library/Caches/Rubrova/runtime-work}"
export RUBROVA_SKIP_OFFICIAL_LOGIC_JAR=true
export RUBROVA_PLAYWRIGHT_PYTHON="$PLAYWRIGHT_VENV/bin/python"
export RUBROVA_UI_TEST_LOGIN=true
export RUBROVA_UI_TEST_USERNAME=admin
export RUBROVA_UI_SCREENSHOT="${RUBROVA_UI_SCREENSHOT:-$SCREENSHOT_DIR/rubrova-local-preview.png}"
export RUBROVA_STARTUP_TIMEOUT_SECONDS="${RUBROVA_STARTUP_TIMEOUT_SECONDS:-1800}"
export RUBROVA_RMI_TIMEOUT_SECONDS="${RUBROVA_RMI_TIMEOUT_SECONDS:-300}"
export RUBROVA_ONSTARTED_TIMEOUT_SECONDS="${RUBROVA_ONSTARTED_TIMEOUT_SECONDS:-600}"
export RUBROVA_SERVER_FINAL_START_TIMEOUT_SECONDS="${RUBROVA_SERVER_FINAL_START_TIMEOUT_SECONDS:-600}"
export RUBROVA_RESTART_TIMEOUT_SECONDS="${RUBROVA_RESTART_TIMEOUT_SECONDS:-600}"
export RUBROVA_UI_READY_TIMEOUT_SECONDS="${RUBROVA_UI_READY_TIMEOUT_SECONDS:-300}"

cd "$REPO_ROOT"
echo ""
echo "Vista previa local de Rubrova."
echo "Se crea una base sintética nueva, se realiza una venta de aceptación y se comprueba la persistencia tras reiniciar."
echo "Si todo sale bien, los contenedores quedarán encendidos para seguir probando."
echo "URL: http://127.0.0.1:8080/login"
echo "Captura: $RUBROVA_UI_SCREENSHOT"
echo ""

bash "$SCRIPT_DIR/test-runtime-smoke.sh"
