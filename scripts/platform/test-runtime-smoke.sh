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

WORK_PARENT="${RUBROVA_RUNTIME_WORK_DIR:-${TMPDIR:-/tmp}}"
mkdir -p "$WORK_PARENT"
WORK_DIR="$(mktemp -d "$WORK_PARENT/rubrova-runtime.XXXXXX")"
CACHE_DIR="${RUBROVA_CACHE_DIR:-$WORK_DIR/cache}"
COMPOSE_DIR="$WORK_DIR/mycompany-6.2"
PROJECT_NAME="${COMPOSE_PROJECT_NAME:-rubrova-smoke-${GITHUB_RUN_ID:-local}}"
COMPOSE_FILE="$COMPOSE_DIR/compose.yaml"
OVERRIDE_FILE="$COMPOSE_DIR/compose.rubrova.override.yaml"
WEB_URL="${RUBROVA_WEB_URL:-http://127.0.0.1:8080/}"
STARTUP_TIMEOUT_SECONDS="${RUBROVA_STARTUP_TIMEOUT_SECONDS:-900}"
KEEP_WORK_DIR="${RUBROVA_KEEP_RUNTIME_WORK_DIR:-false}"

mkdir -p "$CACHE_DIR" "$COMPOSE_DIR"

compose() {
  COMPOSE_PROJECT_NAME="$PROJECT_NAME" docker compose -f "$COMPOSE_FILE" -f "$OVERRIDE_FILE" --project-directory "$COMPOSE_DIR" "$@"
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
    cleanup_failed=0
    if ! rm -rf "$WORK_DIR" 2>/dev/null; then
      if command -v sudo >/dev/null 2>&1 && sudo -n rm -rf "$WORK_DIR"; then
        echo "Directorio temporal limpiado con permisos elevados (archivos creados por contenedores)."
      else
        echo "No se pudo eliminar por completo el directorio temporal: $WORK_DIR" >&2
        cleanup_failed=1
      fi
    fi
    if [[ "$exit_code" -eq 0 && "$cleanup_failed" -ne 0 ]]; then
      exit_code=1
    fi
  else
    echo "Directorio de diagnóstico conservado: $WORK_DIR"
  fi
  exit "$exit_code"
}
trap cleanup EXIT

echo "1/6 Preparando el JAR y Compose oficiales MyCompany 6.2"
RUBROVA_CACHE_DIR="$CACHE_DIR" bash "$PREPARE_SCRIPT"
cp "$CACHE_DIR/compose.yaml" "$COMPOSE_FILE"
cat > "$OVERRIDE_FILE" <<'YAML'
services:
  logics:
    image: lsfusion/mycompany:6.2@sha256:9dacff96577de49a56633a53801c7bcd78b5e7df501cd4ebd61098124276bd11
  server:
    image: lsfusion/server:6.2@sha256:79ede6774b177f2bd9dda21e37957412d6c61874706144bf257c263821fecef5
  client:
    image: lsfusion/client:6.2@sha256:fa98e88fb74a1ca855ac85c0c8c6a8102c5defb15309cb4b142324d4dbdca66e
  db:
    image: postgres:18@sha256:eb63372c1e05c755f55fa30cbd07aecc443676fc6c0fa90b9002d01537841e1a
YAML

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

echo "6/6 Recopilando evidencia del runtime, la extensión y las imágenes"
compose ps

echo "Imágenes resueltas por el Compose:"
IMAGES="$(compose config --images)"
printf '%s\n' "$IMAGES"
while IFS= read -r image_name; do
  [[ -n "$image_name" ]] || continue
  image_digest="$(docker image inspect --format '{{index .RepoDigests 0}}' "$image_name" 2>/dev/null || true)"
  expected_digest="${image_name##*@}"
  actual_digest="${image_digest##*@}"
  if [[ -z "$expected_digest" || "$expected_digest" == "$image_name" ]]; then
    echo "La imagen no tiene un digest fijado en el override: $image_name" >&2
    exit 1
  fi
  if [[ -z "$image_digest" || "$image_digest" == "<no value>" || "$actual_digest" != "$expected_digest" ]]; then
    echo "Digest de imagen distinto al fijado para $image_name: esperado $expected_digest, recibido ${actual_digest:-ninguno}" >&2
    exit 1
  fi
  printf 'DIGEST VERIFICADO %s -> %s\n' "$image_name" "$image_digest"
done <<< "$IMAGES"

LOG_DIR="$COMPOSE_DIR/docker-server/logs"
RUBROVA_LOG_EVIDENCE=false
if [[ -d "$LOG_DIR" ]]; then
  echo "Coincidencias relevantes en los registros del servidor:"
  for log_file in "$LOG_DIR"/*.log; do
    [[ -f "$log_file" ]] || continue
    matches="$(grep -Ein 'RubrovaCustom|RubrovaPOSLocalization|topModule|Exception|ERROR|Failed|not found|syntax|module' "$log_file" | tail -n 40 || true)"
    if [[ -n "$matches" ]]; then
      printf '%s\n%s\n' "--- $(basename "$log_file") ---" "$matches"
      if grep -Fq 'RubrovaCustom' <<< "$matches"; then
        RUBROVA_LOG_EVIDENCE=true
      fi
    fi
  done
fi
if [[ "$RUBROVA_LOG_EVIDENCE" == "true" ]]; then
  echo "Los registros del servidor mencionan RubrovaCustom."
else
  echo "AVISO: el cliente web respondió, pero los registros inspeccionados no exponen RubrovaCustom. La carga efectiva del módulo aún requiere una comprobación funcional del POS."
fi

echo "OK: MyCompany 6.2 arrancó y el cliente web respondió. Esto no sustituye la aceptación funcional del POS, la seguridad ni backup/restore."
