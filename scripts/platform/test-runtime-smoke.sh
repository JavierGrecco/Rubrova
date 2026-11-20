#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd)"
PREPARE_SCRIPT="$SCRIPT_DIR/prepare-mycompany-6.2.sh"
DEPLOY_SCRIPT="$SCRIPT_DIR/deploy-mycompany-6.2.sh"

for command_name in docker curl shasum python3; do
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
EXTENSION_OVERRIDE_FILE="$COMPOSE_DIR/compose.rubrova.override.yaml"
IMAGE_OVERRIDE_FILE="$COMPOSE_DIR/compose.images.override.yaml"
WEB_URL="${RUBROVA_WEB_URL:-http://127.0.0.1:8080/}"
STARTUP_TIMEOUT_SECONDS="${RUBROVA_STARTUP_TIMEOUT_SECONDS:-900}"
KEEP_WORK_DIR="${RUBROVA_KEEP_RUNTIME_WORK_DIR:-false}"

mkdir -p "$CACHE_DIR" "$COMPOSE_DIR"

compose() {
  COMPOSE_PROJECT_NAME="$PROJECT_NAME" docker compose -f "$COMPOSE_FILE" -f "$EXTENSION_OVERRIDE_FILE" -f "$IMAGE_OVERRIDE_FILE" --project-directory "$COMPOSE_DIR" "$@"
}

cleanup() {
  local exit_code=$?
  trap - EXIT
  set +e
  if [[ -s "$COMPOSE_FILE" && -s "$EXTENSION_OVERRIDE_FILE" && -s "$IMAGE_OVERRIDE_FILE" ]]; then
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

echo "2/7 Preparando la extensión Rubrova y su override Docker compartido"
bash "$DEPLOY_SCRIPT" docker "$COMPOSE_DIR"
SETTINGS_FILE="$COMPOSE_DIR/docker-server/settings.properties"
[[ -s "$EXTENSION_OVERRIDE_FILE" ]] || {
  echo "No se preparó compose.rubrova.override.yaml." >&2
  exit 1
}
cat > "$IMAGE_OVERRIDE_FILE" <<'YAML'
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
grep -qx 'logics.topModule = RubrovaCustom' "$SETTINGS_FILE" || {
  echo "No se configuró el punto de entrada RubrovaCustom." >&2
  exit 1
}
for module_file in RubrovaCustom.lsf RubrovaPOSLocalization.lsf RubrovaIntegrationResilience.lsf MyCompanyResourceBundle_es_AR.properties; do
  [[ -s "$COMPOSE_DIR/docker-server/$module_file" ]] || {
    echo "No se preparó el archivo de extensión: $module_file" >&2
    exit 1
  }
done

echo "Preparando un puesto de caja y cuentas de prueba sólo en la copia efímera de CI."
cat >> "$COMPOSE_DIR/docker-server/RubrovaPOSLocalization.lsf" <<'LSF'

// Datos descartables para la aceptación visual del POS en CI.
// Este bloque se agrega sólo al archivo temporal de docker-server; no está en el despliegue.
loadDefaultData () + {
    IF NOT defaultCurrency() THEN
        NEW currencyCI = Currency {
            id(currencyCI) <- 'ARS';
            name(currencyCI) <- 'Peso argentino';
            defaultCurrency() <- currencyCI;
        }

    IF NOT pos('rubrova-ci') THEN {
        NEW centralAccountCI = CashAccount {
            name(centralAccountCI) <- 'Cuenta central CI';
            holder(centralAccountCI) <- defaultCompany();
            currency(centralAccountCI) <- defaultCurrency();

            NEW cashAccountCI = CashAccount {
                name(cashAccountCI) <- 'Efectivo CI';
                holder(cashAccountCI) <- defaultCompany();
                currency(cashAccountCI) <- defaultCurrency();

                NEW cardAccountCI = CashAccount {
                    name(cardAccountCI) <- 'Tarjeta CI';
                    holder(cardAccountCI) <- defaultCompany();
                    currency(cardAccountCI) <- defaultCurrency();

                    NEW cashRegisterCI = Pos {
                        id(cashRegisterCI) <- 'rubrova-ci';
                        name(cashRegisterCI) <- 'Caja de prueba Rubrova';
                        company(cashRegisterCI) <- defaultCompany();
                        // MyCompany exige un tipo de comprobante para habilitar el puesto POS.
                        invoiceType(cashRegisterCI) <- invoiceType('retail');
                        account(cashRegisterCI) <- centralAccountCI;
                        account(cashRegisterCI, PaymentMethod pm) <- cashAccountCI WHERE pm = cashPaymentMethod();
                        account(cashRegisterCI, PaymentMethod pm) <- cardAccountCI WHERE id(pm) = 'card';
                    }
                }
            }
        }
    }

    // Producto unitario y código de barras sintéticos para la siguiente prueba del circuito de venta.
    IF NOT uom('1') THEN
        NEW unitCI = Uom {
            id(unitCI) <- '1';
            name(unitCI) <- 'Unidad';
        }

    IF NOT rootCategory() THEN
        NEW rootCategoryCI = Category {
            id(rootCategoryCI) <- 'rubrova-ci-root';
            name(rootCategoryCI) <- 'Productos de prueba Rubrova';
        }

    IF NOT item('rubrova-ci-product') THEN
        NEW productCI = Product {
            id(productCI) <- 'rubrova-ci-product';
            dataName(productCI) <- 'Producto de prueba Rubrova';
            category(productCI) <- rootCategory();
            uom(productCI) <- uom('1');
            salesPrice(productCI) <- 1250;
        }

    IF NOT itemBarCode('7790000000013') THEN
        NEW barcodeCI = BarCode {
            id(barcodeCI) <- '7790000000013';
            item(barcodeCI) <- item('rubrova-ci-product');
        }
}
LSF
grep -q "rubrova-ci" "$COMPOSE_DIR/docker-server/RubrovaPOSLocalization.lsf" || {
  echo "No se agregó el puesto POS efímero para CI." >&2
  exit 1
}

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

echo "4/7 Iniciando MyCompany 6.2 en un proyecto efímero"
compose up -d --remove-orphans

echo "5/7 Comprobando que la configuración y los módulos Rubrova estén montados en el servidor"
SERVER_CONTAINER_ID="$(compose ps -q server)"
[[ -n "$SERVER_CONTAINER_ID" ]] || {
  echo "No se encontró el contenedor del servicio server." >&2
  exit 1
}
SERVER_ENV="$(docker inspect --format '{{range .Config.Env}}{{println .}}{{end}}' "$SERVER_CONTAINER_ID")"
for expected_env in "JAVA_OPTS=-Dlogics.topModule=RubrovaCustom" "USER_SETLANGUAGE=es" "USER_SETCOUNTRY=AR"; do
  if ! grep -Fxq "$expected_env" <<< "$SERVER_ENV"; then
    echo "El contenedor server no recibió el parámetro esperado: $expected_env" >&2
    exit 1
  fi
done
echo "Configuración de inicio verificada: RubrovaCustom + español (Argentina)."
SERVER_MOUNTS="$(docker inspect --format '{{range .Mounts}}{{println .Source "->" .Destination}}{{end}}' "$SERVER_CONTAINER_ID")"
printf 'Montajes del servidor:\n%s\n' "$SERVER_MOUNTS"
SERVER_MOUNT_DESTINATION="$(docker inspect "$SERVER_CONTAINER_ID" | python3 -c '
import json, os, sys
expected = os.path.realpath(sys.argv[1])
container = json.load(sys.stdin)[0]
matches = [
    mount["Destination"]
    for mount in container.get("Mounts", [])
    if os.path.realpath(mount.get("Source", "")) == expected
]
if len(matches) != 1:
    print("No se encontró un único montaje docker-server dentro del contenedor.", file=sys.stderr)
    sys.exit(2)
print(matches[0])
' "$COMPOSE_DIR/docker-server")"
echo "docker-server está montado en: $SERVER_MOUNT_DESTINATION"
docker exec "$SERVER_CONTAINER_ID" sh -ec '
  mount_dir="$1"
  for module_file in RubrovaCustom.lsf RubrovaPOSLocalization.lsf RubrovaIntegrationResilience.lsf MyCompanyResourceBundle_es_AR.properties; do
    test -s "$mount_dir/$module_file" || {
      echo "El contenedor server no ve $module_file en $mount_dir" >&2
      exit 1
    }
  done
  grep -qx "logics.topModule = RubrovaCustom" "$mount_dir/settings.properties" || {
    echo "El contenedor server no ve logics.topModule=RubrovaCustom en settings.properties" >&2
    exit 1
  }
  grep -qx "user.setLanguage = es" "$mount_dir/settings.properties" || {
    echo "El contenedor server no ve user.setLanguage=es en settings.properties" >&2
    exit 1
  }
  grep -qx "user.setCountry = AR" "$mount_dir/settings.properties" || {
    echo "El contenedor server no ve user.setCountry=AR en settings.properties" >&2
    exit 1
  }
  echo "Configuración activa visible en el contenedor:"
  grep -E "^[[:space:]]*(logics\\.(topModule|includePaths|excludePaths)|user\\.set(Language|Country))[[:space:]]*=" "$mount_dir/settings.properties" || true
' sh "$SERVER_MOUNT_DESTINATION"

echo "Verificando que JAVA_OPTS llegue al proceso Java del servidor:"
docker exec "$SERVER_CONTAINER_ID" sh -ec '
  found=false
  for process_cmdline in /proc/[0-9]*/cmdline; do
    test -r "$process_cmdline" || continue
    args="$(tr "\000" " " < "$process_cmdline" 2>/dev/null || true)"
    case "$args" in
      *-Dlogics.topModule=RubrovaCustom*)
        echo "Argumento Java activo: -Dlogics.topModule=RubrovaCustom"
        found=true
        ;;
    esac
  done
  if [ "$found" != true ]; then
    echo "JAVA_OPTS no llegó como argumento al proceso Java del servidor." >&2
    exit 1
  fi
'

echo "Diagnóstico de rutas de configuración y parámetros superiores dentro del contenedor:"
docker exec "$SERVER_CONTAINER_ID" sh -ec '
  for root in "$1" /etc/lsfusion6-server /etc/lsfusion-server /opt/lsfusion /app; do
    test -d "$root" || continue
    for file in "$root/lsfusion.properties" "$root/settings.properties" "$root/conf/settings.properties"; do
      test -f "$file" || continue
      echo "CONFIG_FILE=$file"
      grep -HnE "^[[:space:]]*logics\\\\.topModule[[:space:]]*=" "$file" || true
      grep -HnE "^[[:space:]]*logics\\\\.(includePaths|excludePaths)[[:space:]]*=" "$file" || true
    done
    find "$root" -maxdepth 4 -type f -name "lsfusion.properties" -print 2>/dev/null || true
    find "$root" -maxdepth 4 -type f -name "settings.properties" -print 2>/dev/null || true
  done
  echo "JAVA_TOP_MODULE_ARGUMENTS:"
  grep -aoE -- "-Dlogics\\\\.topModule=[^[:cntrl:]]+" /proc/1/cmdline || true
  echo "RELEVANT_ENVIRONMENT_KEYS:"
  env | cut -d= -f1 | grep -Ei "JAVA_OPTS|LOGICS|SETTINGS|CONFIG" || true
' sh "$SERVER_MOUNT_DESTINATION"

echo "6/7 Esperando respuesta web y fin de la carga completa de la lógica Rubrova"
SECONDS=0
HTTP_STATUS="000"
LOG_DIR="$COMPOSE_DIR/docker-server/logs"
START_LOG="$LOG_DIR/start.log"
STDOUT_LOG="$LOG_DIR/stdout.log"
EXPECTED_UPSTREAM_MODULES=712
EXPECTED_TOTAL_MODULES=$((EXPECTED_UPSTREAM_MODULES + 3))
MODULES_READY=false
LAST_MODULE_PROGRESS=""
MODULE_PROGRESS_CHANGED_AT=0
while (( SECONDS < STARTUP_TIMEOUT_SECONDS )); do
  HTTP_STATUS="$(curl --silent --output "$WORK_DIR/web-response.html" --write-out '%{http_code}' --connect-timeout 3 --max-time 8 "$WEB_URL" 2>/dev/null || true)"
  MODULE_PROGRESS="$(grep -hE 'Initializing main logic for module.*#[0-9]+ of [0-9]+' "$START_LOG" "$STDOUT_LOG" 2>/dev/null | tail -n 1 || true)"
  if [[ "$MODULE_PROGRESS" != "$LAST_MODULE_PROGRESS" && -n "$MODULE_PROGRESS" ]]; then
    LAST_MODULE_PROGRESS="$MODULE_PROGRESS"
    MODULE_PROGRESS_CHANGED_AT="$SECONDS"
    echo "Progreso de inicialización: $MODULE_PROGRESS"
  fi

  ALL_MODULES_READY=false
  PROGRESS_NUMBERS="$(printf '%s\n' "$MODULE_PROGRESS" | sed -nE 's/.*#([0-9]+) of ([0-9]+).*/\1 \2/p')"
  if [[ -n "$PROGRESS_NUMBERS" ]]; then
    read -r current_module total_modules <<< "$PROGRESS_NUMBERS"
    if (( current_module == total_modules && total_modules >= EXPECTED_TOTAL_MODULES )); then
      ALL_MODULES_READY=true
    elif (( current_module == total_modules && total_modules < EXPECTED_TOTAL_MODULES && SECONDS - MODULE_PROGRESS_CHANGED_AT >= 60 )); then
      echo "La inicialización terminó con $total_modules módulos; se esperaban al menos $EXPECTED_TOTAL_MODULES (MyCompany + tres módulos Rubrova)." >&2
      exit 1
    fi
  fi

  if [[ "$HTTP_STATUS" =~ ^[23][0-9][0-9]$ && "$ALL_MODULES_READY" == "true" ]]; then
    MODULES_READY=true
    break
  fi

  if (( SECONDS % 30 < 5 )); then
    echo "Esperando inicio completo... HTTP=$HTTP_STATUS, lógica completa=$ALL_MODULES_READY, módulos esperados>=$EXPECTED_TOTAL_MODULES, transcurridos=${SECONDS}s"
    compose ps --all
  fi
  sleep 5
done

if [[ ! "$HTTP_STATUS" =~ ^[23][0-9][0-9]$ ]]; then
  echo "El cliente web no respondió HTTP 2xx/3xx en ${STARTUP_TIMEOUT_SECONDS}s; último estado: $HTTP_STATUS." >&2
  exit 1
fi
[[ -s "$WORK_DIR/web-response.html" ]] || {
  echo "El cliente web respondió HTTP $HTTP_STATUS, pero el cuerpo está vacío." >&2
  exit 1
}
if [[ "$MODULES_READY" != "true" ]]; then
  echo "El cliente web respondió HTTP $HTTP_STATUS, pero la lógica no completó la inicialización esperada." >&2
  echo "Se esperaban al menos $EXPECTED_TOTAL_MODULES módulos (712 de MyCompany 6.2 + 3 de Rubrova)." >&2
  echo "Último progreso: ${LAST_MODULE_PROGRESS:-sin datos}" >&2
  exit 1
fi
echo "Cliente web disponible: HTTP $HTTP_STATUS; carga de al menos $EXPECTED_TOTAL_MODULES módulos finalizada después de ${SECONDS}s."

echo "6/8 Esperando que el servidor de aplicación escuche en TCP 7652"
RMI_TIMEOUT_SECONDS="${RUBROVA_RMI_TIMEOUT_SECONDS:-180}"
SECONDS=0
RMI_READY=false
while (( SECONDS < RMI_TIMEOUT_SECONDS )); do
  if docker exec "$SERVER_CONTAINER_ID" sh -c 'grep -iqE ":1DE4[[:space:]]+[[:xdigit:]]+:[[:xdigit:]]+[[:space:]]+0A" /proc/net/tcp /proc/net/tcp6' >/dev/null 2>&1; then
    RMI_READY=true
    break
  fi
  if (( SECONDS % 20 < 2 )); then
    echo "El servidor todavía no escucha en 7652; transcurridos=${SECONDS}s."
  fi
  sleep 2
done
if [[ "$RMI_READY" != "true" ]]; then
  echo "El servidor no abrió el puerto RMI 7652 en ${RMI_TIMEOUT_SECONDS}s." >&2
  compose logs --no-color --tail=180 server >&2 || true
  exit 1
fi
echo "Puerto RMI 7652 en escucha después de ${SECONDS}s."

echo "7/9 Esperando que finalice el arranque de la aplicación"
ONSTARTED_TIMEOUT_SECONDS="${RUBROVA_ONSTARTED_TIMEOUT_SECONDS:-180}"
SECONDS=0
ONSTARTED_READY=false
while (( SECONDS < ONSTARTED_TIMEOUT_SECONDS )); do
  SERVER_STARTUP_LOGS="$(compose logs --no-color --tail=100 server 2>/dev/null || true)"
  if grep -Fq 'Executing onStarted action finished' <<< "$SERVER_STARTUP_LOGS"; then
    ONSTARTED_READY=true
    break
  fi
  if (( SECONDS % 30 < 2 )); then
    echo "El servidor todavía está ejecutando onStarted; transcurridos=${SECONDS}s."
  fi
  sleep 2
done
if [[ "$ONSTARTED_READY" != "true" ]]; then
  echo "El servidor no confirmó el fin de onStarted en ${ONSTARTED_TIMEOUT_SECONDS}s." >&2
  printf '%s\n' "$SERVER_STARTUP_LOGS" | tail -n 100 >&2
  exit 1
fi
echo "Arranque completo: onStarted terminó después de ${SECONDS}s."

if [[ -n "${RUBROVA_PLAYWRIGHT_PYTHON:-}" ]]; then
  [[ -x "$RUBROVA_PLAYWRIGHT_PYTHON" ]] || {
    echo "No se encuentra el intérprete Playwright configurado: $RUBROVA_PLAYWRIGHT_PYTHON" >&2
    exit 1
  }
  echo "8/9 Inspeccionando el login y la pantalla autenticada con Chromium"
  RUBROVA_UI_SCREENSHOT="${RUBROVA_UI_SCREENSHOT:-$WORK_DIR/mycompany-ui.png}" \
    RUBROVA_UI_TEST_LOGIN="${RUBROVA_UI_TEST_LOGIN:-false}" \
    RUBROVA_UI_TEST_USERNAME="${RUBROVA_UI_TEST_USERNAME:-admin}" \
    RUBROVA_UI_TEST_PASSWORD="${RUBROVA_UI_TEST_PASSWORD:-}" \
    "$RUBROVA_PLAYWRIGHT_PYTHON" "$SCRIPT_DIR/inspect-mycompany-ui.py" "$WEB_URL"
else
  echo "AVISO: se omitió la inspección de Chromium porque RUBROVA_PLAYWRIGHT_PYTHON no está configurado."
fi

echo "9/9 Recopilando evidencia del runtime, la extensión y las imágenes"
compose ps

echo "Configuración efectiva de los cuatro servicios (sin valores de entorno):"
for service_name in $SERVICES; do
  service_container="$(compose ps -a -q "$service_name" | head -n 1)"
  [[ -n "$service_container" ]] || continue
  docker inspect --format 'SERVICE={{.Name}} IMAGE={{.Config.Image}} PATH={{.Path}} ARGS={{json .Args}} WORKDIR={{.Config.WorkingDir}}' "$service_container"
  docker inspect --format '{{range .Mounts}}{{println "MOUNT" .Source "->" .Destination}}{{end}}' "$service_container"
  docker inspect --format '{{range .Config.Env}}{{println .}}{{end}}' "$service_container" | sed 's/=.*$/=<oculto>/'
done
echo "Parámetros logics.* del settings.properties montado:"
grep -nE '^[[:space:]]*logics\.' "$SETTINGS_FILE" || true
echo "Últimos registros específicos del servicio logics:"
compose logs --no-color --tail=120 logics || true

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
RUBROVA_CUSTOM_LOG_EVIDENCE=false
RUBROVA_LOCALIZATION_LOG_EVIDENCE=false
RUBROVA_RESILIENCE_LOG_EVIDENCE=false
echo "Archivos creados en docker-server (primeros 80):"
find "$COMPOSE_DIR/docker-server" -maxdepth 3 -type f -print | sort | head -n 80 || true
if [[ -d "$LOG_DIR" ]]; then
  echo "Archivos de log del servidor:"
  for log_file in "$LOG_DIR"/*.log; do
    [[ -f "$log_file" ]] || continue
    printf '%s (%s bytes)\n' "$(basename "$log_file")" "$(wc -c < "$log_file" | tr -d ' ')"
    case "$(basename "$log_file")" in
      start.log|stdout.log|stderr.log|server-remote.log)
        echo "--- Últimas 80 líneas: $(basename "$log_file") ---"
        tail -n 80 "$log_file"
        ;;
    esac
    matches="$(grep -Ein 'RubrovaCustom|RubrovaPOSLocalization|RubrovaIntegrationResilience|topModule|Exception|ERROR|Failed|not found|syntax|module|successfully started' "$log_file" | tail -n 40 || true)"
    if [[ -n "$matches" ]]; then
      printf '%s\n%s\n' "--- Coincidencias: $(basename "$log_file") ---" "$matches"
      if grep -Fq 'RubrovaCustom' <<< "$matches"; then
        RUBROVA_CUSTOM_LOG_EVIDENCE=true
      fi
      if grep -Fq 'RubrovaPOSLocalization' <<< "$matches"; then
        RUBROVA_LOCALIZATION_LOG_EVIDENCE=true
      fi
      if grep -Fq 'RubrovaIntegrationResilience' <<< "$matches"; then
        RUBROVA_RESILIENCE_LOG_EVIDENCE=true
      fi
    fi
  done
else
  echo "No se encontró el directorio de logs esperado: $LOG_DIR"
fi

SERVER_LOGS="$(compose logs --no-color --tail=180 server 2>&1 || true)"
SERVER_MATCHES="$(printf '%s\n' "$SERVER_LOGS" | grep -Ei 'Rubrova|topModule|module|logic|compile|ERROR|Exception|WARN|failed|successfully started' | tail -n 80 || true)"
if [[ -n "$SERVER_MATCHES" ]]; then
  echo "Mensajes relevantes del servicio server:"
  printf '%s\n' "$SERVER_MATCHES"
  if grep -Fq 'RubrovaCustom' <<< "$SERVER_MATCHES"; then
    RUBROVA_CUSTOM_LOG_EVIDENCE=true
  fi
  if grep -Fq 'RubrovaPOSLocalization' <<< "$SERVER_MATCHES"; then
    RUBROVA_LOCALIZATION_LOG_EVIDENCE=true
  fi
  if grep -Fq 'RubrovaIntegrationResilience' <<< "$SERVER_MATCHES"; then
    RUBROVA_RESILIENCE_LOG_EVIDENCE=true
  fi
else
  echo "Últimas líneas del servicio server:"
  printf '%s\n' "$SERVER_LOGS" | tail -n 60
fi

if [[ "$RUBROVA_CUSTOM_LOG_EVIDENCE" != "true" || "$RUBROVA_LOCALIZATION_LOG_EVIDENCE" != "true" || "$RUBROVA_RESILIENCE_LOG_EVIDENCE" != "true" ]]; then
  echo "No se encontró evidencia de carga de los tres módulos propios: RubrovaCustom=$RUBROVA_CUSTOM_LOG_EVIDENCE, RubrovaPOSLocalization=$RUBROVA_LOCALIZATION_LOG_EVIDENCE, RubrovaIntegrationResilience=$RUBROVA_RESILIENCE_LOG_EVIDENCE." >&2
  exit 1
fi
echo "Los registros confirman los tres módulos Rubrova: RubrovaCustom, RubrovaPOSLocalization y RubrovaIntegrationResilience."

echo "OK: MyCompany 6.2 arrancó, respondió HTTP y cargó los dos módulos Rubrova. Esto no sustituye la aceptación funcional del POS, la seguridad ni backup/restore."
