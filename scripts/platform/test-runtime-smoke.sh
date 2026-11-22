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
MOCK_PROVIDER_PORT="${RUBROVA_MOCK_PROVIDER_PORT:-18765}"
MOCK_PROVIDER_PID=""
BUILD_ARTIFACTS_DIR="${RUBROVA_BUILD_ARTIFACTS_DIR:-$WORK_DIR/build-artifacts}"
RUBROVA_IMAGE_TAG="${RUBROVA_RUNTIME_IMAGE_TAG:-${GITHUB_SHA:-local}}"
RUBROVA_IMAGE_TAG="${RUBROVA_IMAGE_TAG:0:12}"
SERVER_IMAGE="rubrova/server:6.2-$RUBROVA_IMAGE_TAG"
LOGICS_IMAGE="rubrova/logics:6.2-$RUBROVA_IMAGE_TAG"
CLIENT_IMAGE="rubrova/client:6.2-$RUBROVA_IMAGE_TAG"

mkdir -p "$CACHE_DIR" "$COMPOSE_DIR"

compose() {
  COMPOSE_PROJECT_NAME="$PROJECT_NAME" docker compose -f "$COMPOSE_FILE" -f "$EXTENSION_OVERRIDE_FILE" -f "$IMAGE_OVERRIDE_FILE" --project-directory "$COMPOSE_DIR" "$@"
}

cleanup() {
  local exit_code=$?
  trap - EXIT
  set +e
  if [[ -n "$MOCK_PROVIDER_PID" ]]; then
    kill "$MOCK_PROVIDER_PID" 2>/dev/null || true
    wait "$MOCK_PROVIDER_PID" 2>/dev/null || true
  fi
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

echo "Preparando simulador HTTP local para probar timeout y recuperación."
python3 "$SCRIPT_DIR/mock-integration-provider.py" --host 0.0.0.0 --port "$MOCK_PROVIDER_PORT" > "$WORK_DIR/mock-provider.log" 2>&1 &
MOCK_PROVIDER_PID=$!
MOCK_READY=false
for attempt in 1 2 3 4 5 6 7 8 9 10; do
  if curl --silent --fail --connect-timeout 1 --max-time 2 "http://127.0.0.1:$MOCK_PROVIDER_PORT/health" >/dev/null; then
    MOCK_READY=true
    break
  fi
  sleep 1
done
if [[ "$MOCK_READY" != "true" ]]; then
  echo "El simulador HTTP local no inició correctamente." >&2
  cat "$WORK_DIR/mock-provider.log" >&2 || true
  exit 1
fi
echo "Simulador HTTP local disponible en el puerto $MOCK_PROVIDER_PORT."

echo "1/6 Preparando el Compose MyCompany 6.2; las imágenes de aplicación salen del fork Rubrova"
RUBROVA_CACHE_DIR="$CACHE_DIR" bash "$PREPARE_SCRIPT"
cp "$CACHE_DIR/compose.yaml" "$COMPOSE_FILE"

echo "2/7 Preparando la extensión Rubrova y su override Docker compartido"
bash "$DEPLOY_SCRIPT" docker "$COMPOSE_DIR"
SETTINGS_FILE="$COMPOSE_DIR/docker-server/settings.properties"
[[ -s "$EXTENSION_OVERRIDE_FILE" ]] || {
  echo "No se preparó compose.rubrova.override.yaml." >&2
  exit 1
}
echo "2.1/7 Construyendo imágenes propias desde los artefactos compilados del SHA actual"
if [[ "${RUBROVA_BUILD_ARTIFACTS_DIR:-}" == "" ]]; then
  mkdir -p "$BUILD_ARTIFACTS_DIR"
  cp "$REPO_ROOT/vendor/platform/server/target/lsfusion-server-6.2.jar" "$BUILD_ARTIFACTS_DIR/server.jar"
  cp "$REPO_ROOT/vendor/mycompany/target/lsfusion-server-6.2.jar" "$BUILD_ARTIFACTS_DIR/logics.jar"
  cp "$REPO_ROOT/vendor/platform/web-client/target/lsfusion-client-6.2.war" "$BUILD_ARTIFACTS_DIR/client.war"
fi
bash "$SCRIPT_DIR/build-rubrova-runtime-images.sh" "$BUILD_ARTIFACTS_DIR" "$RUBROVA_IMAGE_TAG"

cat > "$IMAGE_OVERRIDE_FILE" <<YAML
services:
  logics:
    image: $LOGICS_IMAGE
    pull_policy: never
  server:
    depends_on:
      db:
        condition: service_healthy
      logics:
        condition: service_completed_successfully
      toxiproxy:
        condition: service_started
    extra_hosts:
      - "host.docker.internal:host-gateway"
    image: $SERVER_IMAGE
    pull_policy: never
  client:
    image: $CLIENT_IMAGE
    pull_policy: never
  db:
    image: postgres:18@sha256:eb63372c1e05c755f55fa30cbd07aecc443676fc6c0fa90b9002d01537841e1a
    volumes:
      - ./docker-db-pg18:/var/lib/postgresql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d postgres"]
      interval: 2s
      timeout: 3s
      retries: 30
      start_period: 5s
  # Test-only network fault injector; its control API is bound to loopback on the CI host.
  toxiproxy:
    image: ghcr.io/shopify/toxiproxy:2.13.0@sha256:9941f0357759e6c9bfe0ad45e20c415100505113da0f5c436cfd0a4d27579fdc
    environment:
      TOXIPROXY_AUTH_TOKEN: "\${TOXIPROXY_AUTH_TOKEN:?}"
    extra_hosts:
      - "host.docker.internal:host-gateway"
    ports:
      - "127.0.0.1:18474:8474"
YAML

grep -qx 'logics.topModule = RubrovaCustom' "$SETTINGS_FILE" || {
  echo "No se configuró el punto de entrada RubrovaCustom." >&2
  exit 1
}
echo "Preparando tipo de precio minorista con moneda ARS en un módulo de prueba aislado."
cat > "$COMPOSE_DIR/docker-server/RubrovaCISalesFixture.lsf" <<'LSF'
MODULE RubrovaCISalesFixture;
REQUIRE MyCompany, RubrovaPOSLocalization;

NAMESPACE Sales;

// El POS convierte el precio de lista usando la moneda del tipo de precio.
// En CI asociamos el tipo minorista a la moneda ARS sintética del fixture.
loadDefaultData () + {
    // Ensure invoice type, invoice price type and price type share the organization currency.
    currency(priceType('retail')) <- defaultCurrency();
    priceType(Invoicing.invoiceType('retail')) <- priceType('retail');
    Invoicing.currency(Invoicing.invoiceType('retail')) <- defaultCurrency();
}
LSF

ENTRYPOINT_FILE="$COMPOSE_DIR/docker-server/RubrovaCustom.lsf"
python3 - "$ENTRYPOINT_FILE" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
source = path.read_text(encoding="utf-8")
old = "REQUIRE MyCompany, RubrovaPOSLocalization, RubrovaIntegrationResilience;"
new = "REQUIRE MyCompany, RubrovaPOSLocalization, RubrovaIntegrationResilience, RubrovaCISalesFixture;"
if source.count(old) != 1:
    raise SystemExit("No se encontró una única lista de REQUIRE esperada en RubrovaCustom.lsf.")
path.write_text(source.replace(old, new, 1), encoding="utf-8")
PY

for module_file in RubrovaCustom.lsf RubrovaPOSLocalization.lsf RubrovaIntegrationResilience.lsf RubrovaCISalesFixture.lsf MyCompanyResourceBundle_es_AR.properties; do
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

MOCK_PROVIDER_URL="http://toxiproxy:8666"
MOCK_PROVIDER_TIMEOUT_URL="http://toxiproxy:8667"
cat >> "$COMPOSE_DIR/docker-server/RubrovaIntegrationResilience.lsf" <<LSF

// Endpoints exclusivos de la base efímera CI: nunca se instalan en Rubrova.
rubrovaTestHttpTimeout () {
    rubrovaHttpGet('Rubrova Mock Provider', 'Prueba de timeout', 'ci-timeout-001',
        '$MOCK_PROVIDER_TIMEOUT_URL/ok', 1000);
    EXPORT JSON FROM
        outcome = IF rubrovaHttpSucceeded() THEN 'unexpected-success' ELSE 'failure-captured',
        category = rubrovaHttpFailureCategory(),
        retryable = rubrovaHttpCanRetry(),
        retryAfter = rubrovaHttpRetryAfter(),
        httpStatus = statusHttp(),
        userMessage = rubrovaHttpFailureMessage();
} @@api;

rubrovaHttp408IncidentCount() = GROUP SUM 1
    IF correlationId(IntegrationIncident i) = 'ci-http-408-001';

rubrovaHttp408RetryableIncidentCount() = GROUP SUM 1
    IF correlationId(IntegrationIncident i) = 'ci-http-408-001' AND safeToRetry(i);

rubrovaTestHttpTransientStatus () {
    rubrovaHttpGet('Rubrova Mock Provider', 'Prueba de respuesta transitoria 408', 'ci-http-408-001',
        '$MOCK_PROVIDER_URL/status/408', 4000);
    // EXPORT JSON debe exponer un escalar: se cuenta el valor BOOLEAN persistido.
    // Antes del cambio, incidentRetryable = safeToRetry(IntegrationIncident i) no agregaba las filas.
    EXPORT JSON FROM
        outcome = IF rubrovaHttpSucceeded() THEN 'unexpected-success' ELSE 'captured',
        category = rubrovaHttpFailureCategory(),
        retryable = rubrovaHttpCanRetry(),
        httpStatus = statusHttp(),
        incidentCount = rubrovaHttp408IncidentCount(),
        incidentRetryable = rubrovaHttp408RetryableIncidentCount() = 1;
} @@api;

rubrovaHttp429RetryAfterIncidentCount() = GROUP SUM 1
    IF correlationId(IntegrationIncident i) = 'ci-rate-limit-001' AND retryAfterHeader(i) = '2';

rubrovaTestHttpRateLimit () {
    rubrovaHttpGet('Rubrova Mock Provider', 'Prueba de límite de solicitudes', 'ci-rate-limit-001',
        '$MOCK_PROVIDER_URL/status/429', 4000);
    EXPORT JSON FROM
        outcome = IF rubrovaHttpSucceeded() THEN 'unexpected-success' ELSE 'captured',
        category = rubrovaHttpFailureCategory(),
        retryable = rubrovaHttpCanRetry(),
        retryAfter = rubrovaHttpRetryAfter(),
        incidentRetryAfterPersisted = rubrovaHttp429RetryAfterIncidentCount() = 1,
        httpStatus = statusHttp(),
        userMessage = rubrovaHttpFailureMessage();
} @@api;

rubrovaTestHttpServerError () {
    rubrovaHttpGet('Rubrova Mock Provider', 'Prueba de error 503', 'ci-server-error-001',
        '$MOCK_PROVIDER_URL/status/503', 4000);
    EXPORT JSON FROM
        outcome = IF rubrovaHttpSucceeded() THEN 'unexpected-success' ELSE 'captured',
        category = rubrovaHttpFailureCategory(),
        retryable = rubrovaHttpCanRetry(),
        httpStatus = statusHttp(),
        userMessage = rubrovaHttpFailureMessage();
} @@api;

rubrovaTestHttp400 () {
    rubrovaHttpGet('Rubrova Mock Provider', 'Prueba de error HTTP 400', 'ci-http-400-001',
        '$MOCK_PROVIDER_URL/status/400', 4000);
    EXPORT JSON FROM
        outcome = IF rubrovaHttpSucceeded() THEN 'unexpected-success' ELSE 'captured',
        category = rubrovaHttpFailureCategory(),
        retryable = rubrovaHttpCanRetry(),
        httpStatus = statusHttp(),
        userMessage = rubrovaHttpFailureMessage();
} @@api;

rubrovaTestHttp401 () {
    rubrovaHttpGet('Rubrova Mock Provider', 'Prueba de error HTTP 401', 'ci-http-401-001',
        '$MOCK_PROVIDER_URL/status/401', 4000);
    EXPORT JSON FROM
        outcome = IF rubrovaHttpSucceeded() THEN 'unexpected-success' ELSE 'captured',
        category = rubrovaHttpFailureCategory(),
        retryable = rubrovaHttpCanRetry(),
        httpStatus = statusHttp(),
        userMessage = rubrovaHttpFailureMessage();
} @@api;

rubrovaTestHttp403 () {
    rubrovaHttpGet('Rubrova Mock Provider', 'Prueba de error HTTP 403', 'ci-http-403-001',
        '$MOCK_PROVIDER_URL/status/403', 4000);
    EXPORT JSON FROM
        outcome = IF rubrovaHttpSucceeded() THEN 'unexpected-success' ELSE 'captured',
        category = rubrovaHttpFailureCategory(),
        retryable = rubrovaHttpCanRetry(),
        httpStatus = statusHttp(),
        userMessage = rubrovaHttpFailureMessage();
} @@api;

rubrovaTestHttp409 () {
    rubrovaHttpGet('Rubrova Mock Provider', 'Prueba de error HTTP 409', 'ci-http-409-001',
        '$MOCK_PROVIDER_URL/status/409', 4000);
    EXPORT JSON FROM
        outcome = IF rubrovaHttpSucceeded() THEN 'unexpected-success' ELSE 'captured',
        category = rubrovaHttpFailureCategory(),
        retryable = rubrovaHttpCanRetry(),
        httpStatus = statusHttp(),
        userMessage = rubrovaHttpFailureMessage();
} @@api;

rubrovaTestHttpRecovery () {
    rubrovaHttpGet('Rubrova Mock Provider', 'Prueba de recuperación', 'ci-recovery-001',
        '$MOCK_PROVIDER_URL/ok', 4000);
    EXPORT JSON FROM
        outcome = IF rubrovaHttpSucceeded() THEN 'success' ELSE 'failure',
        category = rubrovaHttpFailureCategory();
} @@api;

rubrovaMockIncidentCount () = GROUP SUM 1
    IF provider(IntegrationIncident i) = 'Rubrova Mock Provider';

rubrovaTestIncidentCountApi () {
    EXPORT JSON FROM incidentCount = rubrovaMockIncidentCount();
} @@api;

rubrovaTestPosConfigurationApi () {
    EXPORT JSON FROM
        defaultCurrencyName = name(defaultCurrency()),
        retailInvoiceCurrencyName = Invoicing.nameCurrency(Invoicing.invoiceType('retail')),
        retailInvoicePriceTypeName = Sales.namePriceType(Invoicing.invoiceType('retail')),
        retailPriceTypeCurrencyName = Sales.nameCurrency(Sales.priceType('retail')),
        cashMethodName = name(Retail.cashPaymentMethod()),
        cardMethodName = name(Retail.paymentMethod('card')),
        cashAccountName = Retail.nameAccount(Retail.pos('rubrova-ci'), Retail.cashPaymentMethod()),
        cardAccountName = Retail.nameAccount(Retail.pos('rubrova-ci'), Retail.paymentMethod('card')),
        cashDisabled = Retail.disabled(Retail.pos('rubrova-ci'), Retail.cashPaymentMethod()),
        cardDisabled = Retail.disabled(Retail.pos('rubrova-ci'), Retail.paymentMethod('card')),
        openSessionNumber = Retail.number(Retail.openedSession(Retail.pos('rubrova-ci')));
} @@api;
LSF

# Token efímero para la API de control de Toxiproxy: la red de contenedores también puede alcanzarla.
TOXIPROXY_AUTH_TOKEN="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
export TOXIPROXY_AUTH_TOKEN

echo "3/6 Validando que Compose use sólo las imágenes de aplicación construidas por Rubrova"
compose config --quiet
COMPOSE_IMAGES="$(compose config --images)"
for expected_image in "$LOGICS_IMAGE" "$SERVER_IMAGE" "$CLIENT_IMAGE"; do
  grep -Fxq "$expected_image" <<< "$COMPOSE_IMAGES" || {
    echo "Compose no quedó configurado con la imagen Rubrova esperada: $expected_image" >&2
    printf '%s\n' "$COMPOSE_IMAGES" >&2
    exit 1
  }
done
if grep -Eq '^lsfusion/(mycompany|server|client):' <<< "$COMPOSE_IMAGES"; then
  echo "El runtime conserva una imagen oficial de aplicación; no se acepta como build propio." >&2
  printf '%s\n' "$COMPOSE_IMAGES" >&2
  exit 1
fi
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

echo "4.0/7 Comprobando la ubicación y persistencia de PostgreSQL 18"
DB_CONTAINER_ID="$(compose ps -q db)"
[[ -n "$DB_CONTAINER_ID" ]] || { echo "No se encontró el contenedor PostgreSQL." >&2; exit 1; }
DB_PGDATA="$(compose exec -T db sh -c 'printf "%s" "$PGDATA"' | tr -d "\r")"
[[ "$DB_PGDATA" == "/var/lib/postgresql/18/docker" ]] || {
  echo "PostgreSQL 18 usa un PGDATA inesperado: $DB_PGDATA" >&2
  exit 1
}
DB_MOUNTS="$(docker inspect --format '{{range .Mounts}}{{println .Source "->" .Destination}}{{end}}' "$DB_CONTAINER_ID")"
printf 'Montajes de PostgreSQL:\n%s\n' "$DB_MOUNTS"
grep -Fq 'docker-db-pg18 -> /var/lib/postgresql' <<< "$DB_MOUNTS" || {
  echo "PostgreSQL no está usando el bind mount persistente docker-db-pg18 en /var/lib/postgresql." >&2
  exit 1
}
compose exec -T db sh -c 'test -s "$PGDATA/PG_VERSION"' || {
  echo "PostgreSQL no creó PG_VERSION dentro del PGDATA persistente." >&2
  exit 1
}
echo "PostgreSQL 18 verificado: PGDATA y bind mount persistente correctos."

echo "4.1/7 Preparando los proxies de fallos de red en Toxiproxy"
TOXIPROXY_API_URL="http://127.0.0.1:18474"
TOXIPROXY_READY=false
for attempt in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15; do
  if curl --silent --fail --connect-timeout 1 --max-time 2 \
      --header "Authorization: Bearer $TOXIPROXY_AUTH_TOKEN" \
      "$TOXIPROXY_API_URL/version" >/dev/null; then
    TOXIPROXY_READY=true
    break
  fi
  sleep 1
done
if [[ "$TOXIPROXY_READY" != "true" ]]; then
  echo "Toxiproxy no respondió en su API local durante el plazo esperado." >&2
  compose logs --no-color --tail=120 toxiproxy >&2 || true
  exit 1
fi
curl --fail --silent --show-error --connect-timeout 2 --max-time 5 \
  --request POST --header "Content-Type: application/json" \
  --header "Authorization: Bearer $TOXIPROXY_AUTH_TOKEN" \
  --data-binary '[{"name":"rubrova_ci_normal","listen":"0.0.0.0:8666","upstream":"host.docker.internal:'"$MOCK_PROVIDER_PORT"'","enabled":true},{"name":"rubrova_ci_timeout","listen":"0.0.0.0:8667","upstream":"host.docker.internal:'"$MOCK_PROVIDER_PORT"'","enabled":true}]' \
  "$TOXIPROXY_API_URL/populate" >/dev/null
curl --fail --silent --show-error --connect-timeout 2 --max-time 5 \
  --request POST --header "Content-Type: application/json" \
  --header "Authorization: Bearer $TOXIPROXY_AUTH_TOKEN" \
  --data-binary '{"name":"drop-response","type":"timeout","stream":"downstream","toxicity":1.0,"attributes":{"timeout":0}}' \
  "$TOXIPROXY_API_URL/proxies/rubrova_ci_timeout/toxics" >/dev/null
PROXY_CONFIG="$(curl --fail --silent --show-error --connect-timeout 2 --max-time 5 \
  --header "Authorization: Bearer $TOXIPROXY_AUTH_TOKEN" "$TOXIPROXY_API_URL/proxies")"
python3 - "$PROXY_CONFIG" <<'PY'
import json
import sys

payload = json.loads(sys.argv[1])
required = {"rubrova_ci_normal", "rubrova_ci_timeout"}
if not required.issubset(payload):
    raise SystemExit("Toxiproxy no creó los dos proxies de aceptación requeridos.")
toxics = payload["rubrova_ci_timeout"].get("toxics", [])
if not any(item.get("name") == "drop-response" and item.get("type") == "timeout" for item in toxics):
    raise SystemExit("No quedó activo el corte de respuesta TCP para el test de timeout.")
PY
echo "Toxiproxy listo: un proxy normal y otro que retiene respuestas hasta que el cliente agota su timeout."

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
EXPECTED_TOTAL_MODULES=$((EXPECTED_UPSTREAM_MODULES + 4))
MODULES_READY=false
LAST_MODULE_PROGRESS=""
MODULE_PROGRESS_CHANGED_AT=0
while (( SECONDS < STARTUP_TIMEOUT_SECONDS )); do
  if (( SECONDS % 10 < 5 )); then
    STARTUP_LOGS="$(compose logs --no-color --tail=100 server 2>/dev/null || true)"
    if grep -Eiq "Exception while starting logics instance|Error starting server|missing .+ at|no viable alternative|mismatched input|failed to compile|compilation failed" <<< "$STARTUP_LOGS"; then
      echo "MyCompany informó un error fatal al compilar o inicializar la lógica; se cancela la espera de arranque." >&2
      printf '%s\\n' "$STARTUP_LOGS" | grep -Ei "Exception while starting logics instance|Error starting server|missing .+ at|no viable alternative|mismatched input|failed to compile|compilation failed" | tail -n 40 >&2 || true
      exit 1
    fi
  fi
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
      echo "La inicialización terminó con $total_modules módulos; se esperaban al menos $EXPECTED_TOTAL_MODULES (MyCompany + 3 módulos propios de Rubrova + 1 fixture temporal de CI)." >&2
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
  echo "Se esperaban al menos $EXPECTED_TOTAL_MODULES módulos (712 de MyCompany 6.2 + 3 módulos Rubrova + 1 fixture temporal de CI)." >&2
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
echo "Comprobando que el bootstrap dejó las tablas internas y la fecha del sistema persistidas."
DB_BOOTSTRAP_STATE="$(compose exec -T db psql -X -v ON_ERROR_STOP=1 -U postgres -d lsfusion -Atqc \
  "SELECT EXISTS (SELECT 1 FROM dumb) AND EXISTS (SELECT 1 FROM _auto WHERE time_currentdate IS NOT NULL)")" || {
  echo "No se pudo verificar el estado persistente de PostgreSQL después del arranque." >&2
  exit 1
}
if [[ "$DB_BOOTSTRAP_STATE" != "t" ]]; then
  echo "El bootstrap terminó, pero falta el registro interno dumb o la fecha del sistema en _auto." >&2
  exit 1
fi
echo "PostgreSQL verificado: dumb existe con su registro interno y Time.currentDate quedó persistida."


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
RUBROVA_CI_SALES_LOG_EVIDENCE=false
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
    matches="$(grep -Ein 'RubrovaCustom|RubrovaPOSLocalization|RubrovaIntegrationResilience|RubrovaCISalesFixture|topModule|Exception|ERROR|Failed|not found|syntax|module|successfully started' "$log_file" | tail -n 40 || true)"
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
      if grep -Fq 'RubrovaCISalesFixture' <<< "$matches"; then
        RUBROVA_CI_SALES_LOG_EVIDENCE=true
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
  if grep -Fq 'RubrovaCISalesFixture' <<< "$SERVER_MATCHES"; then
    RUBROVA_CI_SALES_LOG_EVIDENCE=true
  fi
else
  echo "Últimas líneas del servicio server:"
  printf '%s\n' "$SERVER_LOGS" | tail -n 60
fi

if [[ "$RUBROVA_CUSTOM_LOG_EVIDENCE" != "true" || "$RUBROVA_LOCALIZATION_LOG_EVIDENCE" != "true" || "$RUBROVA_RESILIENCE_LOG_EVIDENCE" != "true" || "$RUBROVA_CI_SALES_LOG_EVIDENCE" != "true" ]]; then
  echo "No se encontró evidencia de carga de los tres módulos Rubrova y el fixture de precios CI: RubrovaCustom=$RUBROVA_CUSTOM_LOG_EVIDENCE, RubrovaPOSLocalization=$RUBROVA_LOCALIZATION_LOG_EVIDENCE, RubrovaIntegrationResilience=$RUBROVA_RESILIENCE_LOG_EVIDENCE, RubrovaCISalesFixture=$RUBROVA_CI_SALES_LOG_EVIDENCE." >&2
  exit 1
fi
echo "Los registros confirman los módulos Rubrova y el fixture de precios CI."

echo "OK: MyCompany 6.2 arrancó, respondió HTTP y cargó los módulos Rubrova y el fixture de precios CI. Esto no sustituye la aceptación funcional del POS, la seguridad ni backup/restore."
