#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd)"
PREPARE_SCRIPT="$SCRIPT_DIR/prepare-mycompany-6.2.sh"
DEPLOY_SCRIPT="$SCRIPT_DIR/deploy-mycompany-6.2.sh"

for command_name in docker curl shasum; do
  command -v "$command_name" >/dev/null 2>&1 || {
    echo "Falta el comando requerido: $command_name" >&2
    exit 2
  }
done
docker compose version >/dev/null

if [[ "$(uname -s)" != "Linux" || "$(uname -m)" != "x86_64" ]]; then
  echo "La prueba de runtime MyCompany 6.2 requiere un anfitrión Linux x86_64; no se ejecutará por emulación." >&2
  exit 2
fi

WORK_DIR="${RUBROVA_RUNTIME_WORK_DIR:-$(mktemp -d "${TMPDIR:-/tmp}/rubrova-runtime.XXXXXX")}"
CACHE_DIR="${RUBROVA_CACHE_DIR:-$WORK_DIR/cache}"
COMPOSE_DIR="$WORK_DIR/mycompany-6.2"
PROJECT_NAME="${COMPOSE_PROJECT_NAME:-rubrova-smoke-${GITHUB_RUN_ID:-local}}"
COMPOSE_FILE="$COMPOSE_DIR/compose.yaml"
WEB_URL="${RUBROVA_WEB_URL:-http://127.0.0.1:8080/}"
STARTUP_TIMEOUT_SECONDS="${RUBROVA_STARTUP_TIMEOUT_SECONDS:-900}"
KEEP_WORK_DIR="${RUBROVA_KEEP_RUNTIME_WORK_DIR:-false}"

mkdir -p "$CACHE_DIR" "$COMPOSE_DIR"

compose() {
  COMPOSE_PROJECT_NAME="$PROJECT_NAME" docker compose -f "$COMPOSE_FILE" --project-directory "$COMPOSE_DIR" "$@"
}

cleanup() {
  local exit_code=$?
  trap - EXIT
  set +e
  if [[ -s "$COMPOSE_FILE" ]]; then
    if [[ "$exit_code" -ne 0 ]]; then
      echo "=== Estado final de los contenedores ===" >&2
      compose ps --all >&2
      echo "=== Últimos registros de MyCompany ===" >&2
      compose logs --no-color --tail=180 >&2
    fi
    compose down --volumes --remove-orphans
  fi
  if [[ "$KEEP_WORK_DIR" != "true" ]]; then
    rm -rf "$WORK_DIR"
  else
    echo "Directorio de diagnóstico conservado: $WORK_DIR"
  fi
  exit "$exit_code"
}
trap cleanup EXIT

echo "1/6 Preparando el JAR y Compose oficiales MyCompany 6.2"
RUBROVA_CACHE_DIR="$CACHE_DIR" bash "$PREPARE_SCRIPT"
cp "$CACHE_DIR/compose.yaml" "$COMPOSE_FILE"

echo "2/6 Preparando la extensión Rubrova fuera del código upstream"
bash "$DEPLOY_SCRIPT" docker "$COMPOSE_DIR"
SETTINGS_FILE="$COMPOSE_DIR/docker-server/settings.properties"
grep -qx 'logics.topModule = RubrovaCustom' "$SETTINGS_FILE" || {
  echo "No se configuró el punto de entrada RubrovaCustom." >&2
  exit 1
}
for module_file in RubrovaCustom.lsf RubrovaPOSLocalization.lsf MyCompanyResourceBundle_es_AR.properties; do
  [[ -s "$COMPOSE_DIR/docker-server/$module_file" ]] || {
    echo "No se preparó el archivo de extensión: $module_file" >&2
    exit 1
  }
done

echo "3/6 Validando la configuración efectiva de Docker Compose"
compose config --quiet
SERVICES="$(compose config --services)"
SERVICE_COUNT="$(printf '%s\n' "$SERVICES" | awk 'NF { count++ } END { print count+0 }')"
if [[ "$SERVICE_COUNT" -lt 4 ]]; then
  echo "Se esperaban al menos cuatro servicios en el Compose oficial; se encontraron $SERVICE_COUNT." >&2
  printf '%s\n' "$SERVICES" >&2
  exit 1
fi
printf 'Servicios definidos (%s):\n%s\n' "$SERVICE_COUNT" "$SERVICES"

echo "4/6 Iniciando MyCompany 6.2 en un proyecto efímero"
compose up -d --remove-orphans

echo "5/6 Esperando la respuesta HTTP del cliente web: $WEB_URL"
SECONDS=0
HTTP_STATUS="000"
while (( SECONDS < STARTUP_TIMEOUT_SECONDS )); do
  HTTP_STATUS="$(curl --silent --output "$WORK_DIR/web-response.html" --write-out '%{http_code}' --connect-timeout 3 --max-time 8 "$WEB_URL" 2>/dev/null || true)"
  if [[ "$HTTP_STATUS" =~ ^[23][0-9][0-9]$ ]]; then
    break
  fi
  if (( SECONDS % 60 < 10 )); then
    echo "Esperando cliente web... HTTP=$HTTP_STATUS, transcurridos=${SECONDS}s"
    compose ps --all
  fi
  sleep 10
done

if [[ ! "$HTTP_STATUS" =~ ^[23][0-9][0-9]$ ]]; then
  echo "MyCompany no respondió con HTTP 2xx/3xx en ${STARTUP_TIMEOUT_SECONDS}s; último estado: $HTTP_STATUS." >&2
  exit 1
fi
[[ -s "$WORK_DIR/web-response.html" ]] || {
  echo "El cliente web respondió HTTP $HTTP_STATUS, pero el cuerpo está vacío." >&2
  exit 1
}
echo "Cliente web disponible: HTTP $HTTP_STATUS después de ${SECONDS}s."

echo "6/6 Recopilando evidencia de la configuración Rubrova"
compose ps
if compose logs --no-color 2>&1 | grep -Fq 'RubrovaCustom'; then
  echo "Los registros del servidor mencionan RubrovaCustom."
else
  echo "AVISO: el cliente web respondió, pero los registros no exponen el nombre RubrovaCustom; la carga efectiva del módulo requiere verificación adicional."
fi

echo "OK: MyCompany 6.2 arrancó y el cliente web respondió. Esto no sustituye la aceptación funcional del POS, la seguridad ni backup/restore."
