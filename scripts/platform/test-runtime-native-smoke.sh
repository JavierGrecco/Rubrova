#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd)"
source "$SCRIPT_DIR/native-listener-check.sh"

for command_name in python3 curl; do
  command -v "$command_name" >/dev/null 2>&1 || {
    echo "Falta el comando requerido: $command_name" >&2
    exit 2
  }
done

[[ -n "${RUBROVA_BUILD_ARTIFACTS_DIR:-}" && -d "$RUBROVA_BUILD_ARTIFACTS_DIR" ]] || {
  echo "RUBROVA_BUILD_ARTIFACTS_DIR debe apuntar a server.jar, logics.jar y client.war compilados." >&2
  exit 2
}
for artifact in server.jar logics.jar client.war; do
  [[ -s "$RUBROVA_BUILD_ARTIFACTS_DIR/$artifact" ]] || {
    echo "Falta el artefacto nativo requerido: $RUBROVA_BUILD_ARTIFACTS_DIR/$artifact" >&2
    exit 2
  }
done

HOST_OS="$(uname -s)"
HOST_ARCH="$(uname -m)"
case "$HOST_OS:$HOST_ARCH" in
  Linux:x86_64|Darwin:arm64)
    ;;
  *)
    echo "Arquitectura no admitida para el smoke nativo: $HOST_OS/$HOST_ARCH (se requiere Linux x86_64 o macOS ARM64)." >&2
    exit 2
    ;;
esac

WORK_DIR="${RUBROVA_NATIVE_SMOKE_DIR:-$(mktemp -d "${TMPDIR:-/tmp}/rubrova-native-smoke.XXXXXX")}"
mkdir -p "$WORK_DIR"
LOG_FILE="$WORK_DIR/native-runtime.log"
WEB_URL="${RUBROVA_NATIVE_WEB_URL:-http://127.0.0.1:8080/login}"
SCREENSHOT="${RUBROVA_NATIVE_SCREENSHOT:-$WORK_DIR/rubrova-native-login.png}"
PLAYWRIGHT_PYTHON="${RUBROVA_PLAYWRIGHT_PYTHON:-}"

export RUBROVA_RUNTIME_CONFIG_PATH="${RUBROVA_RUNTIME_CONFIG_PATH:-$WORK_DIR/runtime-config.json}"
export XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$WORK_DIR/config}"
export XDG_DATA_HOME="${XDG_DATA_HOME:-$WORK_DIR/data}"
export XDG_CACHE_HOME="${XDG_CACHE_HOME:-$WORK_DIR/cache}"
NATIVE_DATA_ROOT="$WORK_DIR/data/Rubrova/native-preview"
if [[ "$HOST_OS" == "Darwin" ]]; then
  DEMO_USER_DATA_ROOT="$HOME/Library/Application Support/Rubrova"
else
  DEMO_USER_DATA_ROOT="$XDG_DATA_HOME/Rubrova"
fi
DEMO_DATA_ROOT="$DEMO_USER_DATA_ROOT/demo-preview"
DEMO_CONFIG_PATH="$DEMO_USER_DATA_ROOT/demo-runtime-config.json"
DEMO_LOG_FILE="$WORK_DIR/demo-runtime.log"
DEMO_UI_LOG_FILE="$WORK_DIR/demo-ui-smoke.log"
DEMO_SCREENSHOT_BASE="$WORK_DIR/rubrova-native.png"
DEMO_SCREENSHOT="$WORK_DIR/rubrova-native-demo.png"
DIAGNOSTICS_FILE="$WORK_DIR/native-diagnostics.log"

collect_native_diagnostics() {
  {
    echo "RUBROVA_NATIVE_DIAGNOSTICS=true"
    echo "NATIVE_DATA_ROOT=$NATIVE_DATA_ROOT"
    echo "--- Archivos relevantes del contexto ROOT ---"
    if [[ -d "$NATIVE_DATA_ROOT/runtime/tomcat-base/webapps" ]]; then
      find "$NATIVE_DATA_ROOT/runtime/tomcat-base/webapps" -type f \
        \( -name web.xml -o -name main.jsp -o -name login.jsp -o -name index.html \) -print | sort
    else
      echo "No existe webapps en el CATALINA_BASE esperado."
    fi
    echo "--- Configuración del conector y del Host Tomcat ---"
    if [[ -f "$NATIVE_DATA_ROOT/runtime/tomcat-base/conf/server.xml" ]]; then
      grep -E '(<Connector|<Host|appBase=|unpackWARs=|autoDeploy=)' \
        "$NATIVE_DATA_ROOT/runtime/tomcat-base/conf/server.xml" || true
    fi
    echo "--- Registros de Tomcat, lsFusion y supervisor ---"
    for log_file in \
      "$NATIVE_DATA_ROOT"/runtime/tomcat-base/logs/*.log \
      "$NATIVE_DATA_ROOT"/runtime/tomcat-base/logs/*.txt \
      "$NATIVE_DATA_ROOT"/runtime/lsfusion/logs/*.log \
      "$NATIVE_DATA_ROOT"/logs/*.log \
      "$DEMO_DATA_ROOT"/runtime/tomcat-base/logs/*.log \
      "$DEMO_DATA_ROOT"/runtime/lsfusion/logs/*.log \
      "$DEMO_DATA_ROOT"/logs/*.log \
      "$DEMO_LOG_FILE" \
      "$DEMO_UI_LOG_FILE" \
      "$MOCK_PROVIDER_LOG_FILE"; do
      [[ -f "$log_file" ]] || continue
      echo "### $log_file ($(wc -c < "$log_file" | tr -d ' ') bytes)"
      tail -n 120 "$log_file" | sed -E \
        's/((password|passwd|secret|token|api[_-]?key)[[:space:]]*[=:][[:space:]]*)[^[:space:],;]+/\1[REDACTADO]/Ig'
    done
  } > "$DIAGNOSTICS_FILE"
}

SUPERVISOR_PID=""
MOCK_PROVIDER_PID=""
MOCK_PROVIDER_PORT="${RUBROVA_CI_MOCK_PROVIDER_PORT:-18765}"
MOCK_PROVIDER_LOG_FILE="$WORK_DIR/mock-provider.log"
EGRESS_RULES_INSTALLED=false

cleanup() {
  local exit_code=$?
  trap - EXIT
  set +e

  if [[ "$EGRESS_RULES_INSTALLED" == "true" ]]; then
    sudo -n iptables -D OUTPUT ! -o lo -j REJECT >/dev/null 2>&1 || true
    sudo -n iptables -D OUTPUT -o lo -j ACCEPT >/dev/null 2>&1 || true
  fi

  if [[ -n "$SUPERVISOR_PID" ]] && kill -0 "$SUPERVISOR_PID" 2>/dev/null; then
    echo "Deteniendo supervisor nativo..."
    kill -TERM "$SUPERVISOR_PID" 2>/dev/null || true
    for _ in $(seq 1 45); do
      kill -0 "$SUPERVISOR_PID" 2>/dev/null || break
      sleep 1
    done
    if kill -0 "$SUPERVISOR_PID" 2>/dev/null; then
      echo "El supervisor no cerró dentro del plazo; se fuerza su terminación." >&2
      kill -KILL "$SUPERVISOR_PID" 2>/dev/null || true
    fi
    wait "$SUPERVISOR_PID" 2>/dev/null || true
  fi

  if [[ -n "$MOCK_PROVIDER_PID" ]] && kill -0 "$MOCK_PROVIDER_PID" 2>/dev/null; then
    kill -TERM "$MOCK_PROVIDER_PID" 2>/dev/null || true
    wait "$MOCK_PROVIDER_PID" 2>/dev/null || true
  fi

  collect_native_diagnostics
  if [[ "$exit_code" -ne 0 ]]; then
    echo "=== Últimos registros del runtime nativo ===" >&2
    if [[ -s "$LOG_FILE" ]]; then tail -n 180 "$LOG_FILE" >&2; fi
    echo "=== Diagnóstico del cliente web nativo ===" >&2
    if [[ -s "$DIAGNOSTICS_FILE" ]]; then cat "$DIAGNOSTICS_FILE" >&2; fi
    if [[ -s "$DEMO_LOG_FILE" ]]; then tail -n 180 "$DEMO_LOG_FILE" >&2; fi
    if [[ -s "$DEMO_UI_LOG_FILE" ]]; then tail -n 100 "$DEMO_UI_LOG_FILE" >&2; fi
  fi

  if [[ "${RUBROVA_KEEP_NATIVE_SMOKE_DATA:-false}" == "true" ]]; then
    echo "Datos de diagnóstico conservados: $WORK_DIR"
  else
    rm -rf "$WORK_DIR"
  fi
  exit "$exit_code"
}
trap cleanup EXIT

echo "1/5 Validando configuración y artefactos del runtime nativo"
python3 "$SCRIPT_DIR/runtime-config.py" init
python3 - "$RUBROVA_RUNTIME_CONFIG_PATH" "$NATIVE_DATA_ROOT" <<'PY'
import json
import sys
from pathlib import Path

config_path = Path(sys.argv[1])
data_directory = Path(sys.argv[2])
config = json.loads(config_path.read_text(encoding="utf-8"))
config["local_runtime"]["data_directory"] = str(data_directory)
config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Directorio temporal de datos del smoke: {data_directory}")
PY
python3 "$SCRIPT_DIR/runtime-config.py" validate

echo "2/5 Iniciando el proveedor simulado local y PostgreSQL, lsFusion/MyCompany y Tomcat sin Docker"
python3 -u "$SCRIPT_DIR/mock-integration-provider.py" --host 127.0.0.1 --port "$MOCK_PROVIDER_PORT" >"$MOCK_PROVIDER_LOG_FILE" 2>&1 &
MOCK_PROVIDER_PID=$!
MOCK_PROVIDER_READY=false
for _ in $(seq 1 30); do
  if ! kill -0 "$MOCK_PROVIDER_PID" 2>/dev/null; then
    echo "El proveedor HTTP local terminó antes de estar disponible." >&2
    exit 1
  fi
  if curl --fail --silent --max-time 2 "http://127.0.0.1:$MOCK_PROVIDER_PORT/health" >/dev/null; then
    MOCK_PROVIDER_READY=true
    break
  fi
  sleep 1
done
if [[ "$MOCK_PROVIDER_READY" != "true" ]]; then
  echo "El proveedor HTTP local no respondió en 30 segundos." >&2
  exit 1
fi
echo "RUBROVA_NATIVE_MOCK_PROVIDER_READY=true"
RUBROVA_CI_SALES_FIXTURE=true RUBROVA_CI_MOCK_PROVIDER_PORT="$MOCK_PROVIDER_PORT" \
  python3 -u "$SCRIPT_DIR/run-local-native-preview.py" --no-open start >"$LOG_FILE" 2>&1 &
SUPERVISOR_PID=$!

STARTUP_TIMEOUT="${RUBROVA_NATIVE_STARTUP_TIMEOUT_SECONDS:-1200}"
SECONDS=0
HTTP_STATUS=""
while (( SECONDS < STARTUP_TIMEOUT )); do
  if ! kill -0 "$SUPERVISOR_PID" 2>/dev/null; then
    echo "El supervisor nativo terminó antes de que la interfaz estuviera disponible." >&2
    exit 1
  fi
  HTTP_STATUS="$(curl --silent --output "$WORK_DIR/web-response.html" --write-out '%{http_code}' \
    --connect-timeout 2 --max-time 8 "$WEB_URL" 2>/dev/null || true)"
  if [[ "$HTTP_STATUS" =~ ^[23][0-9][0-9]$ ]]; then
    break
  fi
  if (( SECONDS % 30 < 3 )); then
    echo "Esperando servidor local: HTTP=$HTTP_STATUS, tiempo=${SECONDS}s."
  fi
  sleep 3
done
if [[ ! "$HTTP_STATUS" =~ ^[23][0-9][0-9]$ ]]; then
  echo "El cliente local no respondió HTTP 2xx/3xx dentro de ${STARTUP_TIMEOUT}s (último: $HTTP_STATUS)." >&2
  exit 1
fi
grep -Fq "Servidor Rubrova y PostgreSQL están listos." "$LOG_FILE" || {
  echo "El supervisor no confirmó que el servidor hubiera terminado su inicialización." >&2
  exit 1
}
if [[ "$HOST_OS" == "Linux" ]]; then
  command -v ss >/dev/null 2>&1 || {
    echo "Falta ss (iproute2) para verificar las interfaces de escucha." >&2
    exit 2
  }
  RMI_LISTENERS="$(ss -H -ltn 'sport = :7652' || true)"
  PG_LISTENERS="$(ss -H -ltn 'sport = :55432' || true)"
else
  command -v lsof >/dev/null 2>&1 || {
    echo "Falta lsof para verificar las interfaces de escucha en macOS." >&2
    exit 2
  }
  RMI_LISTENERS="$(lsof -nP -iTCP:7652 -sTCP:LISTEN || true)"
  PG_LISTENERS="$(lsof -nP -iTCP:55432 -sTCP:LISTEN || true)"
fi
printf 'RMI listeners:\n%s\n' "$RMI_LISTENERS"
rubrova_assert_loopback_listeners "$HOST_OS" "RMI" 7652 "$RMI_LISTENERS" || exit 1
printf 'PostgreSQL listeners:\n%s\n' "$PG_LISTENERS"
rubrova_assert_loopback_listeners "$HOST_OS" "PostgreSQL" 55432 "$PG_LISTENERS" || exit 1
echo "RUBROVA_NATIVE_RMI_LOOPBACK=true"
echo "RUBROVA_NATIVE_POSTGRES_LOOPBACK=true"
echo "RUBROVA_NATIVE_SERVER_READY=true"
echo "RUBROVA_NATIVE_WEB_HTTP=$HTTP_STATUS"

echo "3/5 Comprobando que la interfaz sigue disponible sin salida a Internet"
if [[ "${RUBROVA_BLOCK_EGRESS:-false}" == "true" ]]; then
  command -v iptables >/dev/null 2>&1 || {
    echo "Se solicitó bloquear Internet, pero iptables no está instalado." >&2
    exit 2
  }
  sudo -n iptables -I OUTPUT 1 -o lo -j ACCEPT
  EGRESS_RULES_INSTALLED=true
  sudo -n iptables -I OUTPUT 2 ! -o lo -j REJECT
  sudo -n iptables -C OUTPUT ! -o lo -j REJECT
  echo "RUBROVA_NATIVE_EGRESS_BLOCKED=true"
  if curl --insecure --fail --silent --show-error --connect-timeout 2 --max-time 5 \
      https://1.1.1.1/ >/dev/null 2>&1; then
    echo "La salida externa sigue disponible pese a la regla de aislamiento." >&2
    exit 1
  fi
  echo "RUBROVA_NATIVE_EXTERNAL_CONNECTIVITY=blocked"
else
  echo "RUBROVA_NATIVE_EGRESS_BLOCKED=false"
fi

[[ -n "$PLAYWRIGHT_PYTHON" && -x "$PLAYWRIGHT_PYTHON" ]] || {
  echo "Definí RUBROVA_PLAYWRIGHT_PYTHON con el intérprete que tiene Playwright y Chromium instalados." >&2
  exit 2
}
UI_LOG_FILE="$WORK_DIR/ui-smoke.log"
RUBROVA_UI_SCREENSHOT="$SCREENSHOT" \
RUBROVA_UI_TEST_LOGIN=true \
RUBROVA_UI_TEST_USERNAME=admin \
RUBROVA_UI_STOP_AFTER_LOGIN=false \
RUBROVA_UI_REQUIRE_POSITIVE_REPLENISHMENT=true \
"$PLAYWRIGHT_PYTHON" "$SCRIPT_DIR/inspect-mycompany-ui.py" "$WEB_URL" 2>&1 | tee "$UI_LOG_FILE"
for marker in \
  "UI_LOGIN_STATUS=authenticated:admin" \
  "UI_POS_SCREEN_AVAILABLE=true" \
  "UI_MARKDOWN_DEPENDENCIES_LAZY_LOADED=true" \
  "UI_SESSION_OPEN=true" \
  "UI_SALE_DOCUMENT_CREATED=true" \
  "UI_SALE_PAYMENT_RECONCILED=true" \
  "UI_SALE_STOCK_DEDUCTED=true" \
  "UI_SESSION_CLOSED=true" \
  "UI_SESSION_SALES_RECONCILED=true" \
  "UI_SESSION_CASH_RECONCILED=true" \
  "UI_INTEGRATION_INCIDENT_PERSISTED=true"; do
  grep -Fq "$marker" "$UI_LOG_FILE" || {
    echo "La aceptación comercial nativa no confirmó el resultado esperado: $marker" >&2
    exit 1
  }
done
echo "RUBROVA_NATIVE_POS_ACCEPTANCE=passed"
[[ -s "$SCREENSHOT" ]] || {
  echo "La inspección local no generó la captura de interfaz esperada: $SCREENSHOT" >&2
  exit 1
}
echo "RUBROVA_NATIVE_UI_SMOKE=passed"

echo "4/5 Verificando que el supervisor y el servidor siguen activos tras la inspección"
kill -0 "$SUPERVISOR_PID" || {
  echo "El supervisor nativo se cerró después de cargar la interfaz." >&2
  exit 1
}
curl --silent --output /dev/null --fail --connect-timeout 2 --max-time 8 "$WEB_URL" || {
  echo "La interfaz dejó de responder después de la prueba offline." >&2
  exit 1
}
echo "RUBROVA_NATIVE_RUNTIME_SURVIVED_OFFLINE_CHECK=true"

echo "5/6 Cerrando la primera instancia y liberando sus puertos"
if [[ -n "$SUPERVISOR_PID" ]] && kill -0 "$SUPERVISOR_PID" 2>/dev/null; then
  kill -TERM "$SUPERVISOR_PID" 2>/dev/null || true
  wait "$SUPERVISOR_PID" 2>/dev/null || true
fi
SUPERVISOR_PID=""

if [[ -n "$MOCK_PROVIDER_PID" ]] && kill -0 "$MOCK_PROVIDER_PID" 2>/dev/null; then
  kill -TERM "$MOCK_PROVIDER_PID" 2>/dev/null || true
  wait "$MOCK_PROVIDER_PID" 2>/dev/null || true
fi
MOCK_PROVIDER_PID=""

echo "6/6 Iniciando una segunda instancia con datos de demostración y PostgreSQL separado"
mkdir -p "$DEMO_USER_DATA_ROOT"
export RUBROVA_RUNTIME_CONFIG_PATH="$DEMO_CONFIG_PATH"
python3 "$SCRIPT_DIR/run-local-native-preview.py" init-demo

RUBROVA_LOCAL_DEMO_DATA=true python3 -u "$SCRIPT_DIR/run-local-native-preview.py" --no-open start >"$DEMO_LOG_FILE" 2>&1 &
SUPERVISOR_PID=$!
DEMO_WEB_URL="http://127.0.0.1:8081/login"
DEMO_STARTUP_TIMEOUT="${RUBROVA_NATIVE_DEMO_STARTUP_TIMEOUT_SECONDS:-900}"
SECONDS=0
DEMO_HTTP_STATUS=""
while (( SECONDS < DEMO_STARTUP_TIMEOUT )); do
  if ! kill -0 "$SUPERVISOR_PID" 2>/dev/null; then
    echo "El supervisor de demostración terminó antes de que la interfaz estuviera disponible." >&2
    tail -n 180 "$DEMO_LOG_FILE" >&2 || true
    exit 1
  fi
  DEMO_HTTP_STATUS="$(curl --silent --output "$WORK_DIR/demo-web-response.html" --write-out '%{http_code}' \
    --connect-timeout 2 --max-time 8 "$DEMO_WEB_URL" 2>/dev/null || true)"
  if [[ "$DEMO_HTTP_STATUS" =~ ^[23][0-9][0-9]$ ]]; then
    break
  fi
  if (( SECONDS % 30 < 3 )); then
    echo "Esperando runtime demo: HTTP=$DEMO_HTTP_STATUS, tiempo=${SECONDS}s."
  fi
  sleep 3
done
if [[ ! "$DEMO_HTTP_STATUS" =~ ^[23][0-9][0-9]$ ]]; then
  echo "El runtime de demostración no respondió HTTP 2xx/3xx dentro de ${DEMO_STARTUP_TIMEOUT}s (último: $DEMO_HTTP_STATUS)." >&2
  exit 1
fi
grep -Fq "Datos de demostración Rubrova activados en la base local aislada." "$DEMO_LOG_FILE" || {
  echo "El supervisor no confirmó la activación de los módulos de demostración." >&2
  tail -n 180 "$DEMO_LOG_FILE" >&2 || true
  exit 1
}
grep -Fq "Servidor Rubrova y PostgreSQL están listos." "$DEMO_LOG_FILE" || {
  echo "El servidor de demostración no confirmó su inicialización completa." >&2
  tail -n 180 "$DEMO_LOG_FILE" >&2 || true
  exit 1
}

RUBROVA_UI_SCREENSHOT="$DEMO_SCREENSHOT_BASE" \
RUBROVA_UI_TEST_LOGIN=true \
RUBROVA_UI_TEST_USERNAME=admin \
RUBROVA_UI_STOP_AFTER_LOGIN=false \
RUBROVA_UI_DEMO_MODE=true \
RUBROVA_UI_POS_REGISTER_NAME="Caja de demostración Rubrova" \
"$PLAYWRIGHT_PYTHON" "$SCRIPT_DIR/inspect-mycompany-ui.py" "$DEMO_WEB_URL" 2>&1 | tee "$DEMO_UI_LOG_FILE"
for marker in "UI_LOCAL_DEMO_SESSION_OPEN=true" "UI_LOCAL_DEMO_PRODUCT_FOUND=true"; do
  grep -Fq "$marker" "$DEMO_UI_LOG_FILE" || {
    echo "La aceptación de demostración no confirmó el resultado esperado: $marker" >&2
    exit 1
  }
done
[[ -s "$DEMO_SCREENSHOT" ]] || {
  echo "La inspección de demostración no generó la captura esperada: $DEMO_SCREENSHOT" >&2
  exit 1
}
curl --silent --output /dev/null --fail --connect-timeout 2 --max-time 8 "$DEMO_WEB_URL" || {
  echo "El cliente web de demostración dejó de responder después de la inspección." >&2
  exit 1
}
echo "RUBROVA_NATIVE_DEMO_ACCEPTANCE=passed"
echo "RUBROVA_NATIVE_SMOKE=passed"
echo "RUBROVA_NATIVE_DIAGNOSTICS_FILE=$DIAGNOSTICS_FILE"

