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
RESTART_LOG_FILE="$WORK_DIR/native-runtime-restart.log"
RESTART_UI_LOG_FILE="$WORK_DIR/restart-ui-smoke.log"
SUPERVISOR_LOG_FILE="$WORK_DIR/native-runtime.log"
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
      "$RESTART_LOG_FILE" \
      "$RESTART_UI_LOG_FILE" \
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

report_native_startup_failure() {
  local stage="$1"
  local supervisor_log="$2"
  local data_root="$3"
  local log_file source_location logic_failure_found=false

  echo "RUBROVA_NATIVE_FAILURE_STAGE=$stage"
  for log_file in \
    "$supervisor_log" \
    "$data_root/logs/server-console.log" \
    "$data_root"/runtime/lsfusion/logs/*.log; do
    [[ -s "$log_file" ]] || continue
    echo "### Evidencia de inicio: $log_file"

    if grep -Fq "Exception while starting logics instance" "$log_file"; then
      logic_failure_found=true
      echo "RUBROVA_NATIVE_FAILURE_KIND=lsfusion_logic_initialization"
      source_location="$(grep -Eo '[[:alnum:]_]+:[0-9]+:[0-9]+' "$log_file" | tail -n 1 || true)"
      if [[ -n "$source_location" ]]; then
        echo "RUBROVA_NATIVE_SOURCE_LOCATION=$source_location"
      fi
    fi

    grep -n -A 8 -B 2 -E \
      "Exception while starting logics instance|Error starting server|Caused by:|ERROR StartLogger|^ERROR:|FATAL" \
      "$log_file" | tail -n 100 || true
  done

  if [[ "$logic_failure_found" != "true" ]]; then
    echo "RUBROVA_NATIVE_LSFUSION_INIT_ERROR=not_detected"
  fi
}

record_failed_native_supervisor_exit() {
  local stage="$1"
  local supervisor_log="$2"
  local data_root="$3"
  local exit_status=0

  if wait "$SUPERVISOR_PID"; then
    exit_status=0
  else
    exit_status=$?
  fi
  SUPERVISOR_PID=""
  echo "RUBROVA_NATIVE_SUPERVISOR_EXIT_CODE=$exit_status"
  report_native_startup_failure "$stage" "$supervisor_log" "$data_root"
}

stop_native_supervisor() {
  local supervisor_log="${1:-$SUPERVISOR_LOG_FILE}"
  if [[ -n "$SUPERVISOR_PID" ]]; then
    if kill -0 "$SUPERVISOR_PID" 2>/dev/null; then
      echo "Solicitando cierre ordenado del supervisor nativo..."
      kill -TERM "$SUPERVISOR_PID" 2>/dev/null || true
      for _ in $(seq 1 90); do
        kill -0 "$SUPERVISOR_PID" 2>/dev/null || break
        sleep 1
      done
      if kill -0 "$SUPERVISOR_PID" 2>/dev/null; then
        echo "El supervisor no cerró en 90 segundos; se fuerza su terminación." >&2
        kill -KILL "$SUPERVISOR_PID" 2>/dev/null || true
        wait "$SUPERVISOR_PID" 2>/dev/null || true
        SUPERVISOR_PID=""
        return 1
      fi
    fi
    wait "$SUPERVISOR_PID" || {
      echo "El supervisor terminó con error durante el cierre ordenado." >&2
      SUPERVISOR_PID=""
      return 1
    }
    SUPERVISOR_PID=""
  fi
  grep -Fq "Rubrova quedó detenido. Los datos locales se conservaron." "$supervisor_log" || {
    echo "El supervisor no confirmó el cierre ordenado de Tomcat, lsFusion y PostgreSQL." >&2
    return 1
  }
  echo "RUBROVA_NATIVE_SUPERVISOR_SHUTDOWN_CLEAN=true"
}

assert_native_ports_released() {
  local port active
  for port in 7652 55432; do
    active=""
    for _ in $(seq 1 30); do
      if [[ "$HOST_OS" == "Darwin" ]]; then
        active="$(lsof -nP -t -iTCP:"$port" -sTCP:LISTEN 2>/dev/null || true)"
      else
        active="$(ss -H -ltn "sport = :$port" 2>/dev/null || true)"
      fi
      [[ -z "$active" ]] && break
      sleep 1
    done
    if [[ -n "$active" ]]; then
      echo "El puerto nativo $port continúa en escucha después del cierre ordenado:" >&2
      echo "$active" >&2
      return 1
    fi
  done
  echo "RUBROVA_NATIVE_PORTS_RELEASED=true"
}

cleanup() {
  local exit_code=$?
  trap - EXIT
  set +e

  if [[ "$EGRESS_RULES_INSTALLED" == "true" ]]; then
    sudo -n iptables -D OUTPUT ! -o lo -j REJECT >/dev/null 2>&1 || true
    sudo -n iptables -D OUTPUT -o lo -j ACCEPT >/dev/null 2>&1 || true
  fi

  if [[ -n "$SUPERVISOR_PID" ]]; then
    stop_native_supervisor "$SUPERVISOR_LOG_FILE" || true
  fi

  if [[ -n "$MOCK_PROVIDER_PID" ]] && kill -0 "$MOCK_PROVIDER_PID" 2>/dev/null; then
    kill -TERM "$MOCK_PROVIDER_PID" 2>/dev/null || true
    wait "$MOCK_PROVIDER_PID" 2>/dev/null || true
  fi

  collect_native_diagnostics
  if [[ "$exit_code" -ne 0 ]]; then
    echo "=== Últimos registros del runtime nativo ===" >&2
    if [[ -s "$LOG_FILE" ]]; then tail -n 180 "$LOG_FILE" >&2; fi
    if [[ -s "$RESTART_LOG_FILE" ]]; then tail -n 180 "$RESTART_LOG_FILE" >&2; fi
    if [[ -s "$RESTART_UI_LOG_FILE" ]]; then tail -n 100 "$RESTART_UI_LOG_FILE" >&2; fi
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
SUPERVISOR_LOG_FILE="$LOG_FILE"

STARTUP_TIMEOUT="${RUBROVA_NATIVE_STARTUP_TIMEOUT_SECONDS:-1200}"
SECONDS=0
HTTP_STATUS=""
while (( SECONDS < STARTUP_TIMEOUT )); do
  if ! kill -0 "$SUPERVISOR_PID" 2>/dev/null; then
    echo "El supervisor nativo terminó antes de que la interfaz estuviera disponible." >&2
    record_failed_native_supervisor_exit "initial-startup" "$LOG_FILE" "$NATIVE_DATA_ROOT"
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

echo "3/5 Verificando la política de conectividad externa del runner"
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
  echo "RUBROVA_NATIVE_OFFLINE_ACCEPTANCE=not_tested"
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
  "UI_PARTIAL_RETURNS_OVER_RETURN_REJECTED=true" \
  "UI_PARTIAL_RETURNS_REMAINING_QUANTITY_RECONCILED=true" \
  "UI_PARTIAL_RETURNS_REFUNDS_RECONCILED=true" \
  "UI_PARTIAL_RETURNS_STOCK_REENTERED=true" \
  "UI_PARTIAL_RETURNS_RECONCILED=true" \
  "UI_CUMULATIVE_REFUNDS_OVER_LIMIT_REJECTED=true" \
  "UI_CUMULATIVE_REFUNDS_CONCURRENT_SERIALIZED=true" \
  "UI_CUMULATIVE_REFUNDS_BILL_CANCEL_DOES_NOT_RELEASE_CAP=true" \
  "UI_CUMULATIVE_REFUNDS_PAYMENT_CANCEL_RELEASES_CAP=true" \
  "UI_CUMULATIVE_REFUNDS_RECONCILED=true" \
  "UI_SESSION_CLOSED=true" \
  "UI_SESSION_SALES_RECONCILED=true" \
  "UI_SESSION_CASH_RECONCILED=true" \
  "UI_INTEGRATION_INCIDENT_PERSISTED=true" \
  "UI_REPLENISHMENT_SOURCE_EXPORT_VERIFIED=true" \
  "UI_RETURN_QUANTITY_GUARD_ENABLED=true" \
  "UI_STOCKTAKE_BARCODE_ZERO_PRESERVED=true" \
  "UI_STOCKTAKE_BARCODE_NULL_CLEARED=true" \
  "UI_STOCKTAKE_BARCODE_AGGREGATE_RECONCILED=true" \
  "UI_REPLENISHMENT_POSITIVE_FIXTURES="; do
  grep -Fq "$marker" "$UI_LOG_FILE" || {
    echo "La aceptación comercial nativa no confirmó el resultado esperado: $marker" >&2
    exit 1
  }
done
# Several web RMI connections may be initialized at once for the same user.
# Fail if PostgreSQL/lsFusion reports the previously observed client-locale write conflict.
AUTH_CONTEXT_CONFLICT="SQLConflictException: UPDATE_CONFLICT UPDATE Authentication_customUser SET Authentication_clientLanguage_CustomUser"
if [[ -d "$NATIVE_DATA_ROOT/logs" ]] && grep -R -Fq "$AUTH_CONTEXT_CONFLICT" "$NATIVE_DATA_ROOT/logs"; then
  echo "Se detectó un conflicto concurrente al guardar el locale del usuario admin." >&2
  grep -R -F -n "$AUTH_CONTEXT_CONFLICT" "$NATIVE_DATA_ROOT/logs" >&2 || true
  exit 1
fi
echo "RUBROVA_AUTH_USER_CONTEXT_SERIALIZATION=passed"

echo "RUBROVA_NATIVE_POS_ACCEPTANCE=passed"
[[ -s "$SCREENSHOT" ]] || {
  echo "La inspección local no generó la captura de interfaz esperada: $SCREENSHOT" >&2
  exit 1
}
echo "RUBROVA_NATIVE_UI_SMOKE=passed"

echo "5.1/7 Creando, verificando y restaurando un respaldo PostgreSQL en una base aislada"
BACKUP_BUNDLE="$WORK_DIR/rubrova-db-backup.rubrova-db-backup"
python3 "$SCRIPT_DIR/native-postgres-backup.py" --config "$RUBROVA_RUNTIME_CONFIG_PATH" create --output "$BACKUP_BUNDLE"
python3 "$SCRIPT_DIR/native-postgres-backup.py" --config "$RUBROVA_RUNTIME_CONFIG_PATH" verify "$BACKUP_BUNDLE"
python3 "$SCRIPT_DIR/native-postgres-backup.py" --config "$RUBROVA_RUNTIME_CONFIG_PATH" restore "$BACKUP_BUNDLE" --target-database rubrova_restore_ci --confirm-new-database
echo "RUBROVA_NATIVE_POSTGRES_BACKUP_RESTORE=passed"

echo "4/5 Verificando que el supervisor y el servidor siguen activos tras la inspección"
kill -0 "$SUPERVISOR_PID" || {
  echo "El supervisor nativo se cerró después de cargar la interfaz." >&2
  exit 1
}
curl --silent --output /dev/null --fail --connect-timeout 2 --max-time 8 "$WEB_URL" || {
  echo "La interfaz dejó de responder después de la prueba de estabilidad local." >&2
  exit 1
}
echo "RUBROVA_NATIVE_RUNTIME_SURVIVED_LOCAL_PROBE=true"
if [[ "${RUBROVA_BLOCK_EGRESS:-false}" == "true" ]]; then
  echo "RUBROVA_NATIVE_RUNTIME_SURVIVED_OFFLINE_CHECK=true"
fi

echo "5/7 Reiniciando el servidor nativo para verificar la persistencia real en PostgreSQL"
stop_native_supervisor "$LOG_FILE"
assert_native_ports_released

if curl --silent --fail --connect-timeout 2 --max-time 3 "$WEB_URL" >/dev/null 2>&1; then
  echo "El cliente web sigue respondiendo después del cierre; los procesos nativos no se liberaron." >&2
  exit 1
fi

RUBROVA_CI_SALES_FIXTURE=true RUBROVA_CI_MOCK_PROVIDER_PORT="$MOCK_PROVIDER_PORT" python3 -u "$SCRIPT_DIR/run-local-native-preview.py" --no-open start >"$RESTART_LOG_FILE" 2>&1 &
SUPERVISOR_PID=$!
SUPERVISOR_LOG_FILE="$RESTART_LOG_FILE"
RESTART_STARTUP_TIMEOUT="${RUBROVA_NATIVE_RESTART_TIMEOUT_SECONDS:-600}"
SECONDS=0
RESTART_HTTP_STATUS=""
while (( SECONDS < RESTART_STARTUP_TIMEOUT )); do
  if ! kill -0 "$SUPERVISOR_PID" 2>/dev/null; then
    echo "El supervisor nativo terminó durante el reinicio de persistencia." >&2
    record_failed_native_supervisor_exit "restart-startup" "$RESTART_LOG_FILE" "$NATIVE_DATA_ROOT"
    exit 1
  fi
  RESTART_HTTP_STATUS="$(curl --silent --output "$WORK_DIR/restart-web-response.html" --write-out '%{http_code}' --connect-timeout 2 --max-time 8 "$WEB_URL" 2>/dev/null || true)"
  if [[ "$RESTART_HTTP_STATUS" =~ ^[23][0-9][0-9]$ ]]; then break; fi
  if (( SECONDS % 30 < 3 )); then
    echo "Esperando servidor después del reinicio: HTTP=$RESTART_HTTP_STATUS, tiempo=${SECONDS}s."
  fi
  sleep 3
done
if [[ ! "$RESTART_HTTP_STATUS" =~ ^[23][0-9][0-9]$ ]]; then
  echo "El cliente local no volvió a responder tras el reinicio dentro de ${RESTART_STARTUP_TIMEOUT}s (último: $RESTART_HTTP_STATUS)." >&2
  tail -n 180 "$RESTART_LOG_FILE" >&2 || true
  exit 1
fi
grep -Fq "Servidor Rubrova y PostgreSQL están listos." "$RESTART_LOG_FILE" || {
  echo "El supervisor no confirmó la inicialización completa después del reinicio." >&2
  tail -n 180 "$RESTART_LOG_FILE" >&2 || true
  exit 1
}

RUBROVA_UI_SCREENSHOT="$SCREENSHOT" RUBROVA_UI_TEST_LOGIN=true RUBROVA_UI_TEST_USERNAME=admin RUBROVA_UI_STOP_AFTER_LOGIN=false RUBROVA_UI_VERIFY_PERSISTED_ONLY=true RUBROVA_UI_REQUIRE_POSITIVE_REPLENISHMENT=true "$PLAYWRIGHT_PYTHON" "$SCRIPT_DIR/inspect-mycompany-ui.py" "$WEB_URL" 2>&1 | tee "$RESTART_UI_LOG_FILE"
RESTART_REQUIRED_MARKERS=(
  "UI_RESTART_PERSISTENCE_SALE_RECONCILED=true"
  "UI_RESTART_PERSISTENCE_STOCK_RECONCILED=true"
  "UI_RESTART_PERSISTENCE_SESSION_CLOSED=true"
  "UI_RESTART_PERSISTENCE_CASH_RECONCILED=true"
  "UI_RESTART_PERSISTENCE_STOCKTAKE=true"
  "UI_RESTART_PERSISTENCE_PARTIAL_RETURNS=true"
  "UI_RESTART_PERSISTENCE_CUMULATIVE_REFUNDS=true"
  "UI_RESTART_PERSISTENCE_INCIDENTS_RETAINED=true"
  "UI_RETURN_QUANTITY_GUARD_ENABLED=true"
  "UI_RESTART_PERSISTENCE_VERIFIED=true"
)
for marker in "${RESTART_REQUIRED_MARKERS[@]}"; do
  grep -Fq "$marker" "$RESTART_UI_LOG_FILE" || {
    echo "La comprobación de persistencia tras reinicio no confirmó el resultado esperado: $marker" >&2
    exit 1
  }
done
echo "RUBROVA_NATIVE_RESTART_PERSISTENCE=passed"

echo "6/7 Cerrando la instancia de persistencia y liberando sus puertos"
stop_native_supervisor "$RESTART_LOG_FILE"

if [[ -n "$MOCK_PROVIDER_PID" ]] && kill -0 "$MOCK_PROVIDER_PID" 2>/dev/null; then
  kill -TERM "$MOCK_PROVIDER_PID" 2>/dev/null || true
  wait "$MOCK_PROVIDER_PID" 2>/dev/null || true
fi
MOCK_PROVIDER_PID=""

echo "7/7 Iniciando una segunda instancia con datos de demostración y PostgreSQL separado"
mkdir -p "$DEMO_USER_DATA_ROOT"
export RUBROVA_RUNTIME_CONFIG_PATH="$DEMO_CONFIG_PATH"
python3 "$SCRIPT_DIR/run-local-native-preview.py" init-demo

RUBROVA_LOCAL_DEMO_DATA=true python3 -u "$SCRIPT_DIR/run-local-native-preview.py" --no-open start >"$DEMO_LOG_FILE" 2>&1 &
SUPERVISOR_PID=$!
SUPERVISOR_LOG_FILE="$DEMO_LOG_FILE"
DEMO_WEB_URL="http://127.0.0.1:8081/login"
DEMO_STARTUP_TIMEOUT="${RUBROVA_NATIVE_DEMO_STARTUP_TIMEOUT_SECONDS:-900}"
SECONDS=0
DEMO_HTTP_STATUS=""
while (( SECONDS < DEMO_STARTUP_TIMEOUT )); do
  if ! kill -0 "$SUPERVISOR_PID" 2>/dev/null; then
    echo "El supervisor de demostración terminó antes de que la interfaz estuviera disponible." >&2
    record_failed_native_supervisor_exit "demo-startup" "$DEMO_LOG_FILE" "$DEMO_DATA_ROOT"
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

