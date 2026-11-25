#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd)"

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

if [[ "$(uname -s)" != "Linux" ]]; then
  echo "Este smoke de CI usa Linux nativo. macOS ARM64 se validará en un job específico." >&2
  exit 2
fi
[[ "$(uname -m)" == "x86_64" ]] || {
  echo "El runner Linux de aceptación debe ser x86_64." >&2
  exit 2
}

WORK_DIR="${RUBROVA_NATIVE_SMOKE_DIR:-$(mktemp -d "${TMPDIR:-/tmp}/rubrova-native-smoke.XXXXXX")}"
mkdir -p "$WORK_DIR"
LOG_FILE="$WORK_DIR/native-runtime.log"
WEB_URL="${RUBROVA_NATIVE_WEB_URL:-http://127.0.0.1:8080/}"
SCREENSHOT="${RUBROVA_NATIVE_SCREENSHOT:-$WORK_DIR/rubrova-native-login.png}"
PLAYWRIGHT_PYTHON="${RUBROVA_PLAYWRIGHT_PYTHON:-}"

export RUBROVA_RUNTIME_CONFIG_PATH="${RUBROVA_RUNTIME_CONFIG_PATH:-$WORK_DIR/runtime-config.json}"
export XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$WORK_DIR/config}"
export XDG_DATA_HOME="${XDG_DATA_HOME:-$WORK_DIR/data}"
export XDG_CACHE_HOME="${XDG_CACHE_HOME:-$WORK_DIR/cache}"

SUPERVISOR_PID=""
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

  if [[ "$exit_code" -ne 0 ]]; then
    echo "=== Últimos registros del runtime nativo ===" >&2
    if [[ -s "$LOG_FILE" ]]; then tail -n 180 "$LOG_FILE" >&2; fi
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
python3 "$SCRIPT_DIR/runtime-config.py" validate

echo "2/5 Iniciando PostgreSQL, lsFusion/MyCompany y Tomcat sin Docker"
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
command -v ss >/dev/null 2>&1 || {
  echo "Falta ss (iproute2) para verificar las interfaces de escucha." >&2
  exit 2
}
RMI_LISTENERS="$(ss -H -ltn 'sport = :7652' || true)"
printf 'RMI listeners:\n%s\n' "$RMI_LISTENERS"
grep -Eq '127[.]0[.]0[.]1:7652([[:space:]]|$)' <<< "$RMI_LISTENERS" || {
  echo "RMI no quedó enlazado exclusivamente al loopback 127.0.0.1:7652." >&2
  exit 1
}
if grep -Eq '(0[.]0[.]0[.]0|\[::\]|\*):7652([[:space:]]|$)' <<< "$RMI_LISTENERS"; then
  echo "RMI quedó expuesto en una interfaz no local." >&2
  exit 1
fi
PG_LISTENERS="$(ss -H -ltn 'sport = :55432' || true)"
printf 'PostgreSQL listeners:\n%s\n' "$PG_LISTENERS"
grep -Eq '127[.]0[.]0[.]1:55432([[:space:]]|$)' <<< "$PG_LISTENERS" || {
  echo "PostgreSQL no quedó enlazado al loopback configurado." >&2
  exit 1
}
if grep -Eq '(0[.]0[.]0[.]0|\[::\]|\*):55432([[:space:]]|$)' <<< "$PG_LISTENERS"; then
  echo "PostgreSQL quedó expuesto en una interfaz no local." >&2
  exit 1
fi
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
RUBROVA_UI_STOP_AFTER_LOGIN=true \
"$PLAYWRIGHT_PYTHON" "$SCRIPT_DIR/inspect-mycompany-ui.py" "$WEB_URL" | tee "$UI_LOG_FILE"
grep -Fq "UI_LOGIN_AND_LOCAL_NAVIGATION_VERIFIED=true" "$UI_LOG_FILE" || {
  echo "El smoke visual no confirmó el acceso y la carga del menú." >&2
  exit 1
}
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

echo "5/5 Finalizando: se conservan los datos hasta que termine el diagnóstico"
echo "RUBROVA_NATIVE_SMOKE=passed"
