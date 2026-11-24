import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync, readdirSync, existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const read = (relative) => readFileSync(path.join(root, relative), "utf8");

const lock = JSON.parse(read("platform/mycompany-6.2.lock.json"));
const entrypointSource = read("extensions/lsfusion/RubrovaCustom.lsf");
const moduleSource = read("extensions/lsfusion/RubrovaPOSLocalization.lsf");
const resilienceSource = read("extensions/lsfusion/RubrovaIntegrationResilience.lsf");
const bundle = read("extensions/lsfusion/MyCompanyResourceBundle_es_AR.properties");
const preparerSource = read("scripts/platform/prepare-mycompany-6.2.sh");
const runtimeSmokeSource = read("scripts/platform/test-runtime-smoke.sh");
const dockerOverrideSource = read("platform/compose.rubrova.override.yaml");
const deploySmokeSource = read("scripts/platform/test-deploy-mycompany-6.2.sh");
const uiSmokeSource = read("scripts/platform/inspect-mycompany-ui.py");
const posSearchSource = read("vendor/mycompany/src/main/lsfusion/retail/pos/dashboard/PosDashboardSearch.lsf");
const paymentMethodSource = read("vendor/mycompany/src/main/lsfusion/retail/pos/PosPaymentMethod.lsf");
const runtimeWorkflowSource = read(".github/workflows/platform-extension.yml");
const mockProviderSource = read("scripts/platform/mock-integration-provider.py");
const runtimeImageBuilderSource = read("scripts/platform/build-rubrova-runtime-images.sh");
const runtimeServerDockerfile = read("build/rubrova/runtime/Dockerfile.server");
const runtimeClientDockerfile = read("build/rubrova/runtime/Dockerfile.client");
const sourcePatch = read("scripts/platform/apply-rubrova-source-patches.py");
const dialogBoxHelperSource = read("vendor/platform/web-client/src/main/java/lsfusion/gwt/client/base/view/DialogBoxHelper.java");
const modalWindowSource = read("vendor/platform/web-client/src/main/java/lsfusion/gwt/client/base/view/ModalWindow.java");
const formButtonSource = read("vendor/platform/web-client/src/main/java/lsfusion/gwt/client/base/view/FormButton.java");
const spanishGwtMessagesSource = read("patches/lsfusion/ClientMessages_es.properties");
const spanishGwtMessagesVendor = read("vendor/platform/web-client/src/main/java/lsfusion/gwt/client/ClientMessages_es.properties");


function parseProperties(source) {
  const entries = new Map();
  source.split(/\r?\n/).forEach((raw, index) => {
    const line = raw.trim();
    if (!line || line.startsWith("#") || line.startsWith("!")) return;
    const separator = line.indexOf("=");
    assert.ok(separator > 0, "Línea " + (index + 1) + ": falta separador =");
    const key = line.slice(0, separator).trim();
    const value = line.slice(separator + 1).trim();
    assert.ok(!entries.has(key), "Clave duplicada: " + key);
    assert.ok(value.length > 0, "Valor vacío: " + key);
    entries.set(key, value);
  });
  return entries;
}

test("versión, procedencia, licencias y artefactos están fijados", () => {
  assert.equal(lock.application.version, "6.2");
  assert.equal(lock.application.tag, "6.2");
  assert.match(lock.application.sourceCommit, /^[0-9a-f]{40}$/);
  assert.equal(lock.application.license, "Apache-2.0");
  assert.equal(lock.application.platformLicense, "LGPL-3.0");
  assert.match(lock.artifacts.windowsInstaller.sha256, /^[0-9a-f]{64}$/);
  assert.match(lock.artifacts.applicationJar.sha256, /^[0-9a-f]{64}$/);
  assert.match(lock.artifacts.dockerCompose.sha256, /^[0-9a-f]{64}$/);
  assert.match(lock.artifacts.dockerCompose.url, /\/6\.2\/compose\.yaml$/);
  assert.match(lock.artifacts.dockerCompose.sha256Source, /macOS 26 ARM64 run 44785005509/);
  assert.match(preparerSource, new RegExp("^[ \\t]*JAR_SHA256=\"" + lock.artifacts.applicationJar.sha256 + "\"$", "m"));
  assert.match(preparerSource, new RegExp("^COMPOSE_SHA256=\"" + lock.artifacts.dockerCompose.sha256 + "\"$", "m"));
  assert.match(preparerSource, /El Compose existente no coincide con el SHA-256 fijado/);
  assert.match(preparerSource, /Hash SHA-256 incorrecto para el Compose/);
  assert.match(preparerSource, /RUBROVA_SKIP_OFFICIAL_LOGIC_JAR/);
  assert.match(preparerSource, /Omitiendo el JAR oficial de lógica/);
});

test("el smoke test ejecuta sólo en Linux x86_64, configura la extensión y limpia el stack", () => {
  assert.match(runtimeSmokeSource, /uname -s/);
  assert.match(runtimeSmokeSource, /uname -m/);
  assert.match(runtimeSmokeSource, /Linux.*x86_64/);
  assert.match(runtimeSmokeSource, /logics\.topModule = RubrovaCustom/);
  assert.match(runtimeSmokeSource, /compose config --quiet/);
  assert.match(runtimeSmokeSource, /compose up -d/);
  assert.match(runtimeSmokeSource, /build-rubrova-runtime-images[.]sh/);
  assert.match(runtimeSmokeSource, /pull_policy: never/);
  assert.match(runtimeSmokeSource, /rubrova\/server:6[.]2-/);
  assert.match(runtimeSmokeSource, /rubrova\/logics:6[.]2-/);
  assert.match(runtimeSmokeSource, /rubrova\/client:6[.]2-/);
  assert.doesNotMatch(runtimeSmokeSource, /image: lsfusion\/(mycompany|server|client):/);
  assert.match(runtimeSmokeSource, /RUBROVA_BUILD_ARTIFACTS_DIR/);
  assert.match(runtimeSmokeSource, /compose config --images/);
  assert.match(runtimeSmokeSource, /RUBROVA_PLAYWRIGHT_PYTHON/);
  assert.match(runtimeSmokeSource, /rubrova-ci/);
  assert.match(runtimeSmokeSource, /rubrova-ci-product/);
  assert.match(runtimeSmokeSource, /Producto de prueba Rubrova/);
  assert.match(runtimeSmokeSource, /7790000000013/);
  assert.match(runtimeSmokeSource, /salesPrice\(productCI\) <- 1250/);
  assert.match(runtimeSmokeSource, /rubrova-ci-location/);
  assert.match(runtimeSmokeSource, /rubrovaCITestStockSeeded/);
  assert.match(runtimeSmokeSource, /AdjustmentType[.]all/);
  assert.match(runtimeSmokeSource, /realQuantity\(adjustmentLineCI\) <- 10/);
  assert.match(runtimeSmokeSource, /Retail[.]location\(Retail[.]pos\('rubrova-ci'\)\) <- rubrovaCITestLocation\(\)/);
  assert.match(runtimeSmokeSource, /rubrovaTestSalesReconciliationApi/);
  assert.match(runtimeSmokeSource, /rubrovaTestInventoryApi/);
  assert.match(uiSmokeSource, /UI_SALE_STOCK_DEDUCTED=true/);
  assert.match(runtimeSmokeSource, /Cuenta central CI/);
  assert.match(runtimeSmokeSource, /Efectivo CI/);
  assert.match(runtimeSmokeSource, /Tarjeta CI/);
  assert.match(runtimeSmokeSource, /defaultCurrency\(\)/);
  assert.match(runtimeSmokeSource, /invoiceType\(cashRegisterCI\) <- invoiceType\('retail'\)/);
  assert.match(runtimeSmokeSource, /MyCompany exige un tipo de comprobante/);
  assert.match(runtimeSmokeSource, /CashAccount/);
  assert.match(runtimeSmokeSource, /account\(cashRegisterCI, PaymentMethod pm\)/);
  assert.match(runtimeSmokeSource, /inspect-mycompany-ui[.]py/);
  assert.match(runtimeSmokeSource, /Inspeccionando el login y la pantalla autenticada con Chromium/);
  assert.match(runtimeSmokeSource, /RUBROVA_RMI_TIMEOUT_SECONDS/);
  assert.match(runtimeSmokeSource, /RUBROVA_ONSTARTED_TIMEOUT_SECONDS/);
  assert.match(runtimeSmokeSource, /DB_BOOTSTRAP_STATE=/);
  assert.ok(runtimeSmokeSource.includes("SELECT EXISTS (SELECT 1 FROM dumb) AND EXISTS (SELECT 1 FROM _auto WHERE time_currentdate IS NOT NULL)"));
  assert.match(runtimeSmokeSource, /PostgreSQL verificado: dumb existe con su registro interno/);
  assert.match(runtimeSmokeSource, /Executing onStarted action finished/);
  assert.match(runtimeSmokeSource, /ONSTARTED_READY/);
  assert.match(runtimeSmokeSource, /onStarted terminó/);
  assert.match(runtimeSmokeSource, /RMI_READY/);
  assert.match(runtimeSmokeSource, /:1DE4/);
  assert.match(runtimeSmokeSource, /RUBROVA_UI_TEST_LOGIN/);
  assert.match(uiSmokeSource, /locale="es-AR"/);
  assert.match(uiSmokeSource, /page[.]goto[(]url/);
  assert.match(uiSmokeSource, /RUBROVA_UI_TEST_LOGIN/);
  assert.match(uiSmokeSource, /input\[type="submit"\]/);
  assert.match(uiSmokeSource, /UI_LOGIN_SUBMIT_CLICKED=true/);
  assert.ok(uiSmokeSource.includes('page.wait_for_url("**/main", timeout=30_000)'), "Falta la espera explícita de la ruta autenticada /main.");
  assert.match(uiSmokeSource, /UI_LOGIN_NAVIGATION_STATUS=main/);
  assert.match(uiSmokeSource, /UI_LOGIN_BODY_STABLE=true/);
  assert.match(uiSmokeSource, /body can be temporarily unavailable/);
  assert.match(uiSmokeSource, /submit_field[.]click[(]no_wait_after=True[)]/);
  assert.match(uiSmokeSource, /UI_LOGIN_STATUS=authenticated/);
  assert.match(uiSmokeSource, /click_exact_link\(page, "Punto de venta"\)/);
  assert.match(uiSmokeSource, /UI_RETAIL_NAVIGATION/);
  assert.match(uiSmokeSource, /wait_until_form_loaded\(page, "UI_POS_SCREEN", timeout_seconds=45\)/);
  assert.match(uiSmokeSource, /UI_POS_SCREEN_AVAILABLE=true/);
  assert.doesNotMatch(uiSmokeSource, /UI_POS_SCREEN_AVAILABLE=false/);
  assert.match(uiSmokeSource, /def click_exact_action\(page: Any, label: str\)/);
  assert.match(uiSmokeSource, /ACTION_CONTAINER_BY_LABEL = \{/);
  assert.match(uiSmokeSource, /"Abrir turno": "PROPERTY\(openSession\(p\)\)"/);
  assert.match(uiSmokeSource, /"Ok \(ctrl ENTER\)": "PROPERTY\(overFormOk\)"/);
  assert.ok(uiSmokeSource.includes('button[lsfusion-container="{container}"]'));
  assert.match(uiSmokeSource, /UI_ACTION_.*_MATCH_COUNT/);
  assert.match(uiSmokeSource, /UI_ACTION_.*_CLICKED=true/);
  assert.match(uiSmokeSource, /wait_for_session_open\(page, timeout_seconds=45\)/);
  assert.match(uiSmokeSource, /UI_SESSION_OPEN=true/);
  assert.match(uiSmokeSource, /UI_SESSION_CLOSE_ACTION_FOUND=true/);
  assert.match(uiSmokeSource, /UI_SESSION_SCREENSHOT/);
  assert.match(uiSmokeSource, /Buscar artículos/);
  assert.match(uiSmokeSource, /Producto de prueba Rubrova/);
  assert.match(uiSmokeSource, /UI_TEST_PRODUCT_FOUND=true/);
  assert.match(uiSmokeSource, /UI_TEST_PRODUCT_ADDED_TO_RECEIPT=true/);
  assert.match(uiSmokeSource, /click_exact_action\(page, "Select \(DBLCLK\)"\)/);
  assert.ok(uiSmokeSource.includes('[lsfusion-container="GRID(l)"]'), "El smoke debe comprobar el grid real de líneas de InvoiceLine.");
  assert.match(uiSmokeSource, /UI_RECEIPT_PRODUCT_LINE_COUNT/);
  assert.match(uiSmokeSource, /UI_RECEIPT_PRODUCT_LINES/);
  assert.match(posSearchSource, /selectPosSearch 'Select' \(Invoice i, Item it\)/);
  assert.match(posSearchSource, /setQuantity\(i, it, 1\)/);
  assert.match(posSearchSource, /CHANGEMOUSE 'DBLCLK'/);
  assert.match(uiSmokeSource, /UI_PAYMENT_DIALOG_OPEN=true/);
  assert.match(uiSmokeSource, /UI_PAYMENT_CASH_METHOD_AVAILABLE=true/);
  assert.match(uiSmokeSource, /UI_PAYMENT_CONFIRM_ACTION_CLICKED=true/);
  assert.match(uiSmokeSource, /UI_PAYMENT_CONFIRMED=true/);
  assert.match(uiSmokeSource, /rubrovaTestSalesReconciliationApi/);
  assert.match(uiSmokeSource, /rubrovaTestInventoryApi/);
  assert.match(uiSmokeSource, /sales_api_base = url[.]rstrip\("\/"\) \+ "\/exec\/Sales\."/);
  assert.ok(uiSmokeSource.includes('sales_api_base + "rubrovaTestSalesReconciliationApi"'));
  assert.ok(uiSmokeSource.includes('sales_api_base + "rubrovaTestInventoryApi"'));
  assert.match(uiSmokeSource, /UI_SALE_PAYMENT_RECONCILED=true/);
  assert.match(uiSmokeSource, /UI_SALE_CASH_BALANCE_RECONCILED=true/);
  assert.match(uiSmokeSource, /UI_SALE_STOCK_DEDUCTED=true/);
  assert.doesNotMatch(uiSmokeSource, /UI_PAYMENT_CLOSED_WITHOUT_CHARGE/);
  assert.match(uiSmokeSource, /UI_RECEIPT_WITH_ITEM/);
  assert.match(uiSmokeSource, /UI_ITEM_SCREENSHOT/);
  assert.match(uiSmokeSource, /la venta sintética se confirmará explícitamente/);
  assert.doesNotMatch(uiSmokeSource, /click_exact_action\(page, "Cobrar"\)/);
  assert.match(uiSmokeSource, /\{label\}_RENDER_STATUS=ready/);
  assert.match(uiSmokeSource, /stable_reads >= 2/);
  assert.match(uiSmokeSource, /timeout_seconds: int = 45/);
  assert.match(uiSmokeSource, /"loading" in normalized or "cargando" in normalized/);
  assert.match(uiSmokeSource, /UI_POS_SCREEN/);
  assert.match(uiSmokeSource, /-retail/);
  assert.match(uiSmokeSource, /-pos/);
  assert.match(uiSmokeSource, /AppServerNotAvailableDispatchException/);
  assert.match(uiSmokeSource, /NotBoundException/);
  assert.match(uiSmokeSource, /wait_for_application_server/);
  assert.match(uiSmokeSource, /RUBROVA_UI_READY_TIMEOUT_SECONDS/);
  assert.match(uiSmokeSource, /UI_APPLICATION_SERVER_READY=true/);
  assert.match(uiSmokeSource, /page[.]screenshot/);
  assert.match(uiSmokeSource, /_INPUTS=/);
  assert.match(uiSmokeSource, /_SELECTORS=/);
  assert.match(uiSmokeSource, /selectedText/);
  assert.match(uiSmokeSource, /Caja de prueba Rubrova/);
  assert.match(uiSmokeSource, /Abrir turno/);
  assert.match(uiSmokeSource, /\{label\}_POS_REGISTER_FOUND=true/);
  assert.match(uiSmokeSource, /\{label\}_RENDER_STATUS=ready/);
  assert.match(uiSmokeSource, /_BUTTONS=/);
  assert.match(uiSmokeSource, /_LINKS=/);
  assert.match(uiSmokeSource, /_ALERTS=/);
  assert.match(uiSmokeSource, /className: typeof element.className/);
  assert.match(uiSmokeSource, /UI_INITIAL/);
  assert.match(uiSmokeSource, /UI_AFTER_LOGIN/);
  assert.match(runtimeWorkflowSource, /playwright==1[.]65[.]2/);
  assert.match(runtimeWorkflowSource, /playwright install chromium/);
  assert.match(runtimeWorkflowSource, /RUBROVA_UI_TEST_LOGIN: "true"/);
  assert.match(runtimeWorkflowSource, /RUBROVA_UI_READY_TIMEOUT_SECONDS: 180/);
  assert.ok(runtimeWorkflowSource.includes("group: rubrova-runtime-smoke-${{ github.ref }}"));
  assert.match(runtimeWorkflowSource, /build-fork:/);
  assert.ok(runtimeWorkflowSource.includes("group: rubrova-build-fork-${{ github.ref }}"));
  assert.equal(
    (runtimeWorkflowSource.match(/cancel-in-progress: true/g) || []).length,
    2,
    "El build y el smoke deben cancelar ejecuciones obsoletas de main."
  );
  assert.doesNotMatch(runtimeWorkflowSource, /cancel-in-progress: false/);
  assert.equal(
    (runtimeWorkflowSource.match(/CHECKED_OUT_SHA=/g) || []).length,
    2,
    "Build y smoke deben registrar y verificar el SHA exacto del checkout."
  );

  assert.match(runtimeWorkflowSource, /needs: \[validate, build-fork\]/);
  assert.match(runtimeWorkflowSource, /java-version: "21"/);
  assert.match(runtimeWorkflowSource, /mvn -B -ntp -f build\/rubrova\/pom[.]xml -Passemble -DskipTests package/);
  assert.match(runtimeWorkflowSource, /Recompilar servidor y cliente web con dependencias de runtime/);
  assert.match(runtimeWorkflowSource, /mvn -B -ntp -f vendor\/platform\/pom[.]xml -pl server,web-client -am -DskipTests package/);
  assert.doesNotMatch(runtimeWorkflowSource, /-f vendor\/platform\/pom[.]xml -pl server,web-client -am -Passemble/);
  assert.match(runtimeWorkflowSource, /WEB-INF\/lib\/api-6[.]2[.]jar/);
  assert.match(runtimeWorkflowSource, /rubrova-client-api[.]jar/);
  assert.match(runtimeWorkflowSource, /lsfusion\/base\/DaemonThreadFactory[.]class/);
  assert.match(runtimeWorkflowSource, /lsfusion\/base\/log\/CustodianDailyRollingFileAppender[.]class/);
  assert.match(runtimeWorkflowSource, /org\/apache\/log4j\/rolling\/RollingFileAppender[.]class/);
  assert.match(runtimeWorkflowSource, /Servidor autónomo: API, logging y runtime están incluidos en server[.]jar/);
  assert.match(runtimeWorkflowSource, /vendor\/platform\/web-client\/target/);
  assert.match(runtimeWorkflowSource, /Smoke POS sobre runtime construido desde fuentes Rubrova/);
  assert.match(runtimeWorkflowSource, /actions\/upload-artifact@v4/);
  assert.match(runtimeWorkflowSource, /actions\/download-artifact@v4/);
  assert.match(runtimeWorkflowSource, /rubrova-runtime-application/);
  assert.match(runtimeWorkflowSource, /cancel-in-progress: true/);
  assert.match(runtimeWorkflowSource, /after-login[.]png/);
  assert.match(runtimeWorkflowSource, /rubrova-mycompany-ui-retail[.]png/);
  assert.match(runtimeWorkflowSource, /rubrova-mycompany-ui-pos[.]png/);
  assert.match(runtimeSmokeSource, /EXTENSION_OVERRIDE_FILE/);
  assert.match(runtimeSmokeSource, /IMAGE_OVERRIDE_FILE/);
  assert.match(dockerOverrideSource, /JAVA_OPTS:/);
  assert.match(dockerOverrideSource, /RubrovaCustom/);
  assert.match(dockerOverrideSource, /USER_SETLANGUAGE: "es"/);
  assert.match(dockerOverrideSource, /USER_SETCOUNTRY: "AR"/);
  assert.match(runtimeSmokeSource, /JAVA_OPTS=-Dlogics\.topModule=RubrovaCustom/);
  assert.match(runtimeSmokeSource, /Argumento Java activo/);
  assert.match(runtimeSmokeSource, /RUBROVA_CUSTOM_LOG_EVIDENCE/);
  assert.match(runtimeSmokeSource, /RUBROVA_LOCALIZATION_LOG_EVIDENCE/);
  assert.match(runtimeSmokeSource, /Los registros confirman los módulos Rubrova y el fixture de precios CI/);
  assert.match(runtimeSmokeSource, /RUBROVA_CI_SALES_LOG_EVIDENCE/);
  assert.match(uiSmokeSource, /UI_RECEIPT_PRODUCT_LINES/);
  assert.match(uiSmokeSource, /UI_RECEIPT_LINE_COUNT/);
  assert.match(runtimeSmokeSource, /RubrovaIntegrationResilience=\$RUBROVA_RESILIENCE_LOG_EVIDENCE/);
  assert.match(runtimeSmokeSource, /docker inspect/);
  assert.match(runtimeSmokeSource, /docker exec/);
  assert.match(runtimeSmokeSource, /logics\\\\\.\(topModule\|includePaths\|excludePaths\)/);
  assert.match(runtimeSmokeSource, /EXPECTED_UPSTREAM_MODULES=712/);
  assert.match(runtimeSmokeSource, /EXPECTED_TOTAL_MODULES/);
  assert.ok(runtimeSmokeSource.includes('EXPECTED_UPSTREAM_MODULES + 4'));
  assert.match(runtimeSmokeSource, /RubrovaCISalesFixture[.]lsf/);
  assert.match(runtimeSmokeSource, /currency\(priceType\('retail'\)\) <- MasterData[.]defaultCurrency\(\)/);
  assert.match(runtimeSmokeSource, /RUBROVA_CI_SALES_LOG_EVIDENCE/);
  assert.match(uiSmokeSource, /UI_RECEIPT_PRODUCT_LINES/);
  assert.match(uiSmokeSource, /UI_RECEIPT_LINE_COUNT/);
  assert.match(runtimeSmokeSource, /RUBROVA_RESILIENCE_LOG_EVIDENCE/);
  assert.match(runtimeSmokeSource, /RubrovaIntegrationResilience\|RubrovaCISalesFixture\|topModule/);
  assert.match(runtimeSmokeSource, /MODULE_PROGRESS_CHANGED_AT/);
  assert.match(runtimeSmokeSource, /Exception while starting logics instance/);
  assert.match(runtimeSmokeSource, /missing \.\+ at/);
  assert.match(runtimeSmokeSource, /se cancela la espera de arranque/);
  assert.match(runtimeSmokeSource, /módulos Rubrova/);
  assert.match(runtimeSmokeSource, /http:\/\/127\.0\.0\.1:8080/);
  assert.match(runtimeImageBuilderSource, /server[.]jar/);
  assert.match(runtimeImageBuilderSource, /logics[.]jar/);
  assert.match(runtimeImageBuilderSource, /client[.]war/);
  assert.match(runtimeImageBuilderSource, /vendor\/platform\/server\/entrypoint[.]sh/);
  assert.match(runtimeImageBuilderSource, /vendor\/platform\/server\/src\/main\/resources\/logics\/docker\/Dockerfile/);
  assert.match(runtimeImageBuilderSource, /docker build --platform linux\/amd64/);
  assert.match(runtimeImageBuilderSource, /rubrova\/server:6[.]2-/);
  assert.match(runtimeImageBuilderSource, /rubrova\/logics:6[.]2-/);
  assert.match(runtimeImageBuilderSource, /rubrova\/client:6[.]2-/);
  assert.match(runtimeServerDockerfile, /COPY server[.]jar \/server[.]jar/);
  assert.doesNotMatch(runtimeServerDockerfile, /ADD https?:/);
  assert.match(runtimeClientDockerfile, /COPY client[.]war \/usr\/local\/tomcat\/webapps\/ROOT[.]war/);
  assert.doesNotMatch(runtimeClientDockerfile, /ADD https?:/);
  assert.match(runtimeSmokeSource, /compose down --volumes --remove-orphans/);
  assert.match(runtimeSmokeSource, /trap cleanup EXIT/);
  assert.match(runtimeSmokeSource, /mktemp -d.*rubrova-runtime/);
  assert.match(runtimeSmokeSource, /sudo -n rm -rf/);
  assert.match(runtimeSmokeSource, /docker image inspect/);
  assert.match(runtimeSmokeSource, /IMAGEN LOCAL VERIFICADA/);
  assert.ok(runtimeSmokeSource.includes('compose ps -a -q "$local_service"'), "La verificación debe incluir el contenedor logics aunque haya terminado correctamente.");
  assert.match(runtimeSmokeSource, /DIGEST EXTERNO VERIFICADO/);
  assert.match(runtimeSmokeSource, /show_client_tomcat_logs/);
  assert.match(runtimeSmokeSource, /One or more listeners failed to start/);
  assert.ok(runtimeSmokeSource.includes(":1DE4[[:space:]]+"), "El healthcheck del servidor debe comprobar el puerto RMI 7652 en /proc/net/tcp.");
  assert.match(runtimeSmokeSource, /service_healthy/);
  const postgresDigest = lock.dockerImages.postgres.digest;
  assert.match(postgresDigest, /^sha256:[0-9a-f]{64}$/);
  assert.ok(runtimeSmokeSource.includes(`image: postgres:18@${postgresDigest}`));
  assert.ok(runtimeSmokeSource.includes(lock.testTools.toxiproxy.digest));
  assert.doesNotMatch(runtimeSmokeSource, /image: lsfusion\/(mycompany|server|client):/);
  assert.equal(lock.dockerImages.postgres.volumeMount, "/var/lib/postgresql");
  assert.equal(lock.dockerImages.postgres.dataDirectory, "/var/lib/postgresql/18/docker");
  assert.ok(dockerOverrideSource.includes("image: postgres:18@" + lock.dockerImages.postgres.digest));
  assert.match(dockerOverrideSource, /\.\/docker-db-pg18:\/var\/lib\/postgresql/);
  assert.match(dockerOverrideSource, /condition: service_healthy/);
  assert.match(dockerOverrideSource, /pg_isready -U postgres -d postgres/);
  assert.match(runtimeSmokeSource, /\.\/docker-db-pg18:\/var\/lib\/postgresql/);
  assert.match(runtimeSmokeSource, /condition: service_healthy/);
  assert.match(runtimeSmokeSource, /pg_isready -U postgres -d postgres/);
  assert.match(runtimeSmokeSource, /DB_PGDATA=.*PGDATA/);
  assert.match(runtimeSmokeSource, /docker-db-pg18 -> \/var\/lib\/postgresql/);
  assert.match(runtimeSmokeSource, /PG_VERSION/);
  assert.match(runtimeSmokeSource, /DB_CONTAINER_ID/);
  assert.equal(lock.dockerImages.digestPlatform, "linux/amd64");
  assert.equal(lock.testTools.toxiproxy.scope, "ci-only");
  assert.equal(lock.testTools.toxiproxy.license, "MIT");
  assert.match(lock.testTools.toxiproxy.digest, /^sha256:[0-9a-f]{64}$/);
  assert.equal(lock.testTools.toxiproxy.platform, "linux/amd64");
  assert.ok(runtimeSmokeSource.includes(`image: ${lock.testTools.toxiproxy.image}@${lock.testTools.toxiproxy.digest}`), "Toxiproxy debe usar la imagen CI fijada en el lock.");
  assert.match(runtimeSmokeSource, /docker-server\/logs/);
  assert.match(runtimeSmokeSource, /compose logs --no-color --tail=180 server/);
  assert.match(runtimeSmokeSource, /tail -n 80/);
  assert.match(runtimeSmokeSource, /successfully started/);
  assert.match(runtimeSmokeSource, /RubrovaPOSLocalization/);
  assert.match(runtimeSmokeSource, /RubrovaIntegrationResilience/);
});

test("la extensión superior requiere MyCompany sin copiar sus módulos", () => {
  assert.match(entrypointSource, /^MODULE RubrovaCustom;/m);
  assert.match(entrypointSource, /^REQUIRE MyCompany, RubrovaPOSLocalization, RubrovaIntegrationResilience;/m);
  assert.match(moduleSource, /^MODULE RubrovaPOSLocalization;/m);
  assert.match(moduleSource, /^REQUIRE MyCompany;/m);
  assert.match(resilienceSource, /^MODULE RubrovaIntegrationResilience;/m);
  assert.match(resilienceSource, /^REQUIRE MyCompany;/m);
  assert.match(resilienceSource, /timeoutHttp\(\) <- timeoutMilliseconds/);
  assert.match(resilienceSource, /HEADERSTO responseHeaders/);
  assert.match(resilienceSource, /responseHeaders\(STRING\[100\] headerName\)/, "HEADERSTO debe consultar el nombre del encabezado con la clase STRING[100], no con la clase del valor TEXT.");
  assert.match(resilienceSource, /GROUP MAX responseHeaders\(STRING\[100\] headerName\)/);
  assert.match(resilienceSource, /retryAfterHeader 'Reintentar después de' = DATA ISTRING\[100\] \(IntegrationIncident\)/);
  assert.match(resilienceSource, /retryAfterHeader\(incident\) <- retryAfterHeaderValue/);
  assert.match(resilienceSource, /timeoutMilliseconds > 30000/);
  assert.match(resilienceSource, /NEWSESSION/);
  assert.match(resilienceSource, /rubrovaRecordIntegrationIncident/);
  assert.match(resilienceSource, /logToFile\('rubrova-integration-emergency'/);
  assert.match(resilienceSource, /resolveIntegrationIncident/);
  assert.match(resilienceSource, /rubrovaHttpGet/);
  assert.ok(resilienceSource.indexOf("rubrovaHandleHttpStatusFailure 'Clasificar error HTTP externo'") < resilienceSource.indexOf("rubrovaHttpGet 'Consultar servicio externo (GET)'"), "El clasificador HTTP debe declararse antes de su primera llamada en lsFusion.");
  assert.match(resilienceSource, /EXTERNAL HTTP GET url/);
  assert.match(resilienceSource, /TIMEOUT_OR_NETWORK/);
  assert.match(resilienceSource, /rubrovaHandleHttpStatusFailure/);
  assert.match(resilienceSource, /RATE_LIMITED/);
  assert.match(resilienceSource, /REMOTE_5XX/);
  assert.match(resilienceSource, /REMOTE_TRANSIENT/);
  assert.match(resilienceSource, /rubrovaHttpCanRetry = DATA LOCAL BOOLEAN/);
  assert.match(resilienceSource, /rubrovaHttpCanRetry\(\) <- responseStatus = 408/);
  assert.match(resilienceSource, /responseStatus = 408 OR responseStatus = 425/);
  assert.match(resilienceSource, /rubrovaShowIntegrationFailure/);
  assert.match(resilienceSource, /REMOTE_HTTP_ERROR/);
  assert.match(resilienceSource, /rubrovaHttpSucceeded\(\) <- TRUE/);
  assert.doesNotMatch(resilienceSource, /technicalDetail\(incident\) <- messageCaughtException/);
  assert.match(resilienceSource, /safeToRetry/);
  assert.match(resilienceSource, /technicalDetail/);
  assert.match(resilienceSource, /DO NOT STORE|No almacenar tokens/i);
  assert.equal(lock.extension.topModule, "RubrovaCustom");
  assert.match(moduleSource, /^NAMESPACE Retail;/m);
  assert.match(moduleSource, /DESIGN posDashboard/);
  assert.match(moduleSource, /DESIGN posPayment/);
  assert.ok(runtimeSmokeSource.includes("Invoicing.currency(Invoicing.invoiceType('retail')) <- MasterData.defaultCurrency()"));
  assert.match(moduleSource, /Sales[.]currency\(Sales[.]priceType\('retail'\)\) <- defaultCurrency\(\)/);
  assert.match(moduleSource, /name\(cashPaymentMethod\(\)\) <- 'Efectivo'/);
  assert.match(moduleSource, /name\(paymentMethod\('card'\)\) <- 'Tarjeta'/);
  assert.match(moduleSource, /DESIGN posPaymentReturn/);
  assert.match(moduleSource, /PROPERTY\(invoicePaid\(b, pm\)\)/);
  assert.match(moduleSource, /PROPERTY\(overFormOk\)/);
  assert.match(moduleSource, /PROPERTY\(nameVendor\(b\)\)/);
  assert.match(moduleSource, /PROPERTY\(amount\(b\)\).*rubrova\.pos\.return_amount/);
  assert.match(moduleSource, /nameDepositPaymentType/);
  assert.match(moduleSource, /nameWithdrawPaymentType/);
  assert.match(moduleSource, /nameIncomingPaymentType/);
  assert.match(moduleSource, /nameOutgoingPaymentType/);
});

test("el glosario inicial tiene claves únicas, no vacías y necesarias para el POS", () => {
  const entries = parseProperties(bundle);
  const required = [
    "Cash", "Cash_register", "Open_session", "Close_session", "Session",
    "Payment_method", "Payments", "To_pay", "Change", "Customer",
    "Barcode", "Product", "Quantity", "Price", "Total", "Inventory",
    "On_hand", "Purchase", "Purchase_order", "Invoice", "Return",
    "Sales", "Vendor", "Date", "Search", "Cancel", "Confirm",
    "rubrova.pos.title", "rubrova.pos.cash_register", "rubrova.pos.to_pay",
    "rubrova.pos.payment_title", "rubrova.pos.amount_due", "rubrova.pos.refunds",
    "rubrova.pos.return_payment_title", "rubrova.pos.previous_payment",
    "rubrova.pos.refund_by_method", "rubrova.pos.confirm_return",
    "rubrova.payment.method_title",
    "Attributes", "Companies", "Partners", "Countries", "Configuration",
    "Images", "Operations", "Manufacturing", "Retail", "sales", "Settings",
    "Employees", "Units_of_measure", "Contracts", "Positions", "Currencies",
    "Exchange_rates", "Projects", "Human_resources", "Activities", "Fleet",
    "Documentation"
  ];
  for (const key of required) assert.ok(entries.has(key), "Falta traducción obligatoria: " + key);
  assert.ok(entries.size >= 70, "Glosario inicial demasiado pequeño: " + entries.size);
  const customIds = [...moduleSource.matchAll(/\{(rubrova\.[^}]+)\}/g)].map((match) => match[1]);
  for (const id of customIds) assert.ok(entries.has(id), "Falta traducción del caption Rubrova: " + id);
  assert.equal(entries.get("Retail"), "Comercio");
  for (const key of ["Retail", "Manufacturing", "Human_resources", "Projects", "Fleet", "Documentation"]) {
    assert.ok(entries.get(key), "Falta traducción de navegación: " + key);
  }
  assert.equal(lock.extension.locale, "es_AR");
  assert.match(lock.extension.translationStatus, /partial/);
});

test("los scripts de despliegue configuran el módulo y conservan backups", () => {
  const shell = read("scripts/platform/deploy-mycompany-6.2.sh");
  const powershell = read("scripts/platform/deploy-mycompany-6.2.ps1");
  assert.match(shell, /"logics\.topModule": "RubrovaCustom"/);
  assert.match(shell, /"user\.setLanguage": "es"/);
  assert.match(shell, /"user\.setCountry": "AR"/);
  assert.match(shell, /compose\.rubrova\.override\.yaml/);
  assert.match(shell, /OVERRIDE_SOURCE/);
  assert.match(deploySmokeSource, /cmp -s/);
  assert.match(deploySmokeSource, /resilience_backup_count/);
  assert.match(deploySmokeSource, /override_backup_count/);
  assert.match(shell, /"user\.setLanguage": "es"/);
  assert.match(shell, /"user\.setCountry": "AR"/);
  assert.match(shell, /docker-server/);
  assert.match(shell, /RubrovaPOSLocalization\.lsf/);
  assert.match(shell, /RubrovaIntegrationResilience\.lsf/);
  assert.match(shell, /systemctl restart lsfusion6-server|systemctl start lsfusion6-server/);
  assert.match(powershell, /"logics\.topModule" = "RubrovaCustom"/);
  assert.match(powershell, /"user\.setLanguage" = "es"/);
  assert.match(powershell, /"user\.setCountry" = "AR"/);
  assert.match(powershell, /"user\.setLanguage" = "es"/);
  assert.match(powershell, /"user\.setCountry" = "AR"/);
  assert.match(powershell, /RubrovaPOSLocalization\.lsf/);
  assert.match(powershell, /RubrovaIntegrationResilience\.lsf/);
  assert.match(powershell, /rubrova-backup/);
  assert.match(powershell, /lsFusion 6 Server/);
});

test("el lock distingue la imagen MyCompany AMD64 de server/client multi-arquitectura", () => {
  assert.deepEqual(lock.dockerImages.mycompany.platforms, ["linux/amd64"]);
  assert.equal(lock.dockerImages.mycompany.arm64Available, false);
  assert.ok(lock.dockerImages.server.platforms.includes("linux/arm64"));
  assert.ok(lock.dockerImages.client.platforms.includes("linux/arm64"));
  assert.match(lock.artifacts.dockerCompose.url, /solutions\/mycompany-docker\/6\.2\/compose\.yaml$/);
});

test("la prueba de resiliencia inyecta timeout, verifica recuperación y persiste la incidencia", () => {
  assert.equal(
    runtimeSmokeSource.split('"$SCRIPT_DIR/inspect-mycompany-ui.py"').length - 1,
    1,
    "El smoke visual del POS debe ejecutarse una sola vez: la segunda pasada intenta abrir un turno ya abierto."
  );
  assert.equal(
    runtimeSmokeSource.split("8/9 Inspeccionando el login y la pantalla autenticada con Chromium").length - 1,
    1,
    "No debe repetirse la aceptación visual dentro del mismo runtime efímero."
  );
  assert.equal(
    runtimeSmokeSource.split("4.1/7 Preparando los proxies de fallos de red en Toxiproxy").length - 1,
    1,
    "La configuración de Toxiproxy debe ejecutarse una sola vez por instancia efímera."
  );
  const timeoutEndpoint = runtimeSmokeSource.split("rubrovaTestHttpTimeout () {")[1]?.split("} @@api;")[0] || "";
  const rateLimitEndpoint = runtimeSmokeSource.split("rubrovaTestHttpRateLimit () {")[1]?.split("} @@api;")[0] || "";
  assert.ok(!timeoutEndpoint.includes("incidentRetryAfterPersisted"), "La persistencia de Retry-After no pertenece al endpoint de timeout.");
  assert.ok(rateLimitEndpoint.includes("incidentRetryAfterPersisted = rubrovaHttp429RetryAfterIncidentCount() = 1"), "El endpoint HTTP 429 debe exponer la comprobación del encabezado persistido.");
  assert.match(runtimeSmokeSource, /mock-integration-provider[.]py/);
  assert.match(runtimeSmokeSource, /host[.]docker[.]internal:host-gateway/);
  assert.match(runtimeSmokeSource, /ghcr[.]io\/shopify\/toxiproxy:2[.]13[.]0/);
  assert.match(runtimeSmokeSource, /9941f0357759e6c9bfe0ad45e20c415100505113da0f5c436cfd0a4d27579fdc/);
  assert.match(runtimeSmokeSource, /127[.]0[.]0[.]1:18474:8474/);
  assert.match(runtimeSmokeSource, /rubrova_ci_normal/);
  assert.doesNotMatch(runtimeSmokeSource, /rubrova_ci_timeout|drop-response|MOCK_PROVIDER_TIMEOUT_URL/);
  assert.match(runtimeSmokeSource, /MOCK_PROVIDER_URL="http:\/\/toxiproxy:8666"/);
  assert.match(runtimeSmokeSource, /\/slow\?delay=5/);
  assert.match(runtimeSmokeSource, /Toxiproxy listo: proxy HTTP hacia el simulador/);
  assert.match(runtimeSmokeSource, /TOXIPROXY_AUTH_TOKEN/);
  assert.match(runtimeSmokeSource, /secrets[.]token_urlsafe\(32\)/);
  assert.ok(runtimeSmokeSource.includes('Authorization: Bearer $TOXIPROXY_AUTH_TOKEN'));
  assert.match(runtimeSmokeSource, /rubrovaTestHttpTimeout/);
  assert.ok(runtimeSmokeSource.includes("userMessage = rubrovaHttpFailureMessage()"));
  assert.match(runtimeSmokeSource, /rubrovaTestHttpRecovery/);
  assert.match(runtimeSmokeSource, /rubrovaTestHttpRateLimit/);
  assert.ok(runtimeSmokeSource.includes("retryAfter = rubrovaHttpRetryAfter()"));
  assert.ok(runtimeSmokeSource.includes("retryAfterHeader(i) = '2'"));
  assert.ok(runtimeSmokeSource.includes("incidentRetryAfterPersisted = rubrovaHttp429RetryAfterIncidentCount() = 1"));
  assert.match(uiSmokeSource, /incidentRetryAfterPersisted/);
  assert.match(runtimeSmokeSource, /rubrovaTestHttpTransientStatus/);
  assert.ok(runtimeSmokeSource.includes("rubrovaHttp408IncidentCount() = GROUP SUM 1"));
  assert.ok(runtimeSmokeSource.includes("incidentCount = rubrovaHttp408IncidentCount()"));
  assert.ok(runtimeSmokeSource.includes("incidentRetryable = safeToRetry(IntegrationIncident i)"));
  assert.match(runtimeSmokeSource, /rubrovaTestHttpServerError/);
  assert.ok(runtimeSmokeSource.includes("retryable = rubrovaHttpCanRetry(),"), "Los endpoints transitorios deben exponer la decisión local de reintento.");
  assert.match(runtimeSmokeSource, /rubrovaTestHttp400/);
  assert.match(runtimeSmokeSource, /rubrovaTestHttp401/);
  assert.match(runtimeSmokeSource, /rubrovaTestHttp403/);
  assert.match(runtimeSmokeSource, /rubrovaTestHttp409/);
  assert.ok(mockProviderSource.includes('if request.path == "/status/400":'));
  assert.ok(mockProviderSource.includes('if request.path == "/status/401":'));
  assert.ok(mockProviderSource.includes('if request.path == "/status/403":'));
  assert.ok(mockProviderSource.includes('if request.path == "/status/409":'));
  assert.match(runtimeSmokeSource, /rubrovaTestIncidentCountApi/);
  assert.match(runtimeSmokeSource, /rubrovaTestPosConfigurationApi/);
  assert.ok(runtimeSmokeSource.includes("priceType(Invoicing.invoiceType('retail')) <- priceType('retail')"));
  assert.ok(runtimeSmokeSource.includes("Invoicing.currency(Invoicing.invoiceType('retail')) <- MasterData.defaultCurrency()"));
  assert.match(uiSmokeSource, /UI_POS_EFFECTIVE_CONFIGURATION/);
  assert.match(uiSmokeSource, /def wait_for_payment_dialog\(page: Any, timeout_seconds: int = 20\)/);
  assert.match(uiSmokeSource, /def click_exact_action\(page: Any, label: str\) -> bool/);
  assert.match(uiSmokeSource, /page[.]get_by_role\("button", name=label, exact=True\)/);
  assert.doesNotMatch(uiSmokeSource, /def wait_for_exact_link\(/);
  assert.ok(uiSmokeSource.includes('search_tab.click(no_wait_after=True)'));
  assert.ok(uiSmokeSource.includes('UI_ITEM_SEARCH_TAB_CLICKED=true'));
  assert.doesNotMatch(uiSmokeSource, /search_tab[.]click\(no_wait_after=True\)\\s*\\n\\s*page[.]wait_for_timeout\(750\)/);
  assert.match(uiSmokeSource, /button[.]click\(no_wait_after=True\)/);
  assert.doesNotMatch(uiSmokeSource, /page[.]locator\(selector\)[.]nth\(index\)[.]click/);
  assert.match(uiSmokeSource, /NAVIGATOR_CONTAINER_BY_LABEL = \{/);
  assert.match(uiSmokeSource, /"Comercio": "Retail[.]retail"/);
  assert.match(uiSmokeSource, /"Punto de venta": "Retail[.]posDashboard"/);
  assert.ok(uiSmokeSource.includes("page.locator(f'a[lsfusion-container=\"{container}\"]')"));
  assert.match(uiSmokeSource, /UI_NAV_LINK_.*_MATCH_COUNT/);
  assert.match(uiSmokeSource, /navigator_diagnostics\(page\)/);
  assert.doesNotMatch(uiSmokeSource, /page[.]get_by_role\("link", name=label, exact=True\)/);
  assert.match(uiSmokeSource, /submenu_label: str \| None = None/);
  assert.match(uiSmokeSource, /UI_NAV_LINK_.*_CLICKED=true/);
  assert.ok(uiSmokeSource.includes('click_exact_link(page, "Comercio", submenu_label="Punto de venta")'));
  assert.match(uiSmokeSource, /UI_PAYMENT_FORM_RENDERED=true/);
  assert.match(uiSmokeSource, /wait_for_payment_dialog\(page, timeout_seconds=20\)/);
  assert.doesNotMatch(uiSmokeSource, /page[.]wait_for_timeout\(1200\)\\s*\\n\\s*payment_text/);
  assert.ok(uiSmokeSource.includes('UI_INTEGRATION_{status_code}_CLASSIFIED=true'));
  assert.match(uiSmokeSource, /rubrovaTestPosConfigurationApi/);
  assert.match(uiSmokeSource, /UI_INTEGRATION_TIMEOUT_CAPTURED=true/);
  assert.match(uiSmokeSource, /UI_INTEGRATION_TIMEOUT_BOUNDARY_PROVEN=true/);
  assert.match(uiSmokeSource, /timeout_elapsed < 0[.]75/);
  assert.match(uiSmokeSource, /UI_INTEGRATION_TIMEOUT_MESSAGE=true/);
  assert.match(mockProviderSource, /time[.]sleep\(delay\)/);
  assert.match(uiSmokeSource, /UI_INTEGRATION_408_CLASSIFIED=true/);
  assert.match(uiSmokeSource, /UI_INTEGRATION_408_INCIDENT_PERSISTED=true/);
  assert.match(uiSmokeSource, /incident_count != 1/);
  assert.match(uiSmokeSource, /incidentRetryable/);
  assert.match(uiSmokeSource, /UI_INTEGRATION_429_CLASSIFIED=true/);
  assert.match(uiSmokeSource, /UI_INTEGRATION_503_CLASSIFIED=true/);
  assert.match(uiSmokeSource, /UI_INTEGRATION_RECOVERY_SUCCEEDED=true/);
  assert.match(uiSmokeSource, /UI_INTEGRATION_INCIDENT_PERSISTED=true/);
  assert.match(mockProviderSource, /ThreadingHTTPServer/);
  assert.ok(mockProviderSource.includes('if request.path == "/slow":'));
  assert.ok(mockProviderSource.includes('if request.path == "/ok":'));
  assert.ok(mockProviderSource.includes('if request.path == "/status/408":'));
});

test("el timeout HTTP también se propaga y se aplica en el navegador GWT", () => {
  const httpClientActionSource = read("vendor/platform/api/src/main/java/lsfusion/interop/session/HttpClientAction.java");
  const gHttpClientActionSource = read("vendor/platform/web-client/src/main/java/lsfusion/gwt/client/action/GHttpClientAction.java");
  const clientActionConverterSource = read("vendor/platform/web-client/src/main/java/lsfusion/gwt/server/convert/ClientActionToGwtConverter.java");
  const gwtDispatcherSource = read("vendor/platform/web-client/src/main/java/lsfusion/gwt/client/controller/dispatch/GwtActionDispatcher.java");

  assert.match(httpClientActionSource, /public Long timeout/);
  assert.match(gHttpClientActionSource, /public Long timeout/);
  assert.match(clientActionConverterSource, /action[.]timeout/);
  assert.match(gwtDispatcherSource, /Math[.]min\(action[.]timeout == null \? 10_000L : action[.]timeout, 60_000L\)/);
  assert.match(gwtDispatcherSource, /timeoutTimer[.]schedule\(timeoutMillis\)/);
  assert.match(gwtDispatcherSource, /request[.]abort\(\)/);
  assert.match(gwtDispatcherSource, /request[.]clearOnReadyStateChange\(\)/);
  assert.match(gwtDispatcherSource, /completed[.]compareAndSet\(false, true\)/);
  assert.match(gwtDispatcherSource, /xhr[.]getReadyState\(\) == XMLHttpRequest[.]DONE/);
  assert.match(gwtDispatcherSource, /"Request timed out"/);
  assert.match(gwtDispatcherSource, /new GExternalHttpResponse\(null, null,/);
  assert.match(gwtDispatcherSource, /xhr[.]getStatus\(\) == 0 \? null/);
});

test("el cierre del turno acepta el CONFIRM GWT original y concilia la sesión", () => {
  assert.ok(runtimeSmokeSource.includes("rubrovaCITestSession() = GROUP MAX Retail.Session"));
  assert.ok(runtimeSmokeSource.includes("rubrovaTestSessionCloseApi"));
  assert.ok(runtimeSmokeSource.includes("Retail.closingDateTime(rubrovaCITestSession())"));
  assert.ok(runtimeSmokeSource.includes("Retail.countInvoices(rubrovaCITestSession())"));
  assert.ok(runtimeSmokeSource.includes("Retail.paid(rubrovaCITestSession(), Retail.cashPaymentMethod())"));
  assert.ok(uiSmokeSource.includes('"Cerrar turno": "PROPERTY(close(s))"'));
  assert.ok(uiSmokeSource.includes("STABLE_SELECTOR_HIDDEN=true"));
  assert.ok(uiSmokeSource.includes('page.get_by_role("button", name=label, exact=True)'));
  assert.ok(uiSmokeSource.includes('input[type="submit"][value='));
  assert.ok(uiSmokeSource.includes("Never retain a DOM index"));
  assert.ok(uiSmokeSource.includes("def accept_ls_fusion_confirmation"));
  assert.ok(uiSmokeSource.includes('page.locator(".modal.show")'));
  assert.ok(uiSmokeSource.includes('modal.locator(".modal-footer button.btn-primary")'));
  assert.ok(uiSmokeSource.includes('affirmative_label != "Sí"'));
  assert.ok(uiSmokeSource.includes("UI_GWT_CONFIRMATION_ACCEPTED=true"));
  assert.ok(!uiSmokeSource.includes('page.once("dialog", accept_session_close_dialog)'));
  assert.ok(uiSmokeSource.includes('page.get_by_text("Turno", exact=True)'));
  assert.ok(uiSmokeSource.includes("visible_session_tabs"));
  assert.ok(uiSmokeSource.includes("UI_SESSION_TAB_VISIBLE_MATCHES="));
  assert.ok(uiSmokeSource.includes("UI_SESSION_TAB_CANDIDATES="));
  assert.ok(uiSmokeSource.includes("UI_SESSION_TAB_ACTIVATED=true"));
  assert.ok(uiSmokeSource.includes("UI_SESSION_CLOSE_BUTTON_VISIBLE=true"));
  assert.ok(uiSmokeSource.includes("UI_SESSION_CLOSE_ACTION_CLICKED=true"));
  assert.ok(uiSmokeSource.includes("UI_SESSION_CLOSE_TIMESTAMP_PERSISTED=true"));
  assert.ok(uiSmokeSource.includes("UI_SESSION_CLOSED=true"));
  assert.ok(uiSmokeSource.includes("UI_SESSION_SALES_RECONCILED=true"));
  assert.ok(uiSmokeSource.includes("UI_SESSION_CASH_RECONCILED=true"));
  assert.ok(uiSmokeSource.includes("UI_SESSION_CLOSED_SCREENSHOT"));

  // In lsFusion 6.2, CONFIRM becomes a MessageBox; YES is the unique primary button.
  assert.ok(dialogBoxHelperSource.includes("new MessageBox(caption, contents, timeout, closeCallback, options[initialValue], options)"));
  assert.ok(dialogBoxHelperSource.includes("option.isPrimary() ? FormButton.ButtonStyle.PRIMARY : FormButton.ButtonStyle.SECONDARY"));
  assert.ok(modalWindowSource.includes('GwtClientUtils.addClassName(modal, "show")'));
  assert.ok(formButtonSource.includes('GwtClientUtils.addClassName(this, "btn-primary")'));
});

test("los botones de confirmación del cliente GWT están localizados al español", () => {
  const entries = parseProperties(spanishGwtMessagesSource);
  assert.equal(entries.get("yes"), "Sí");
  assert.equal(entries.get("no"), "No");
  assert.equal(entries.get("ok"), "Aceptar");
  assert.equal(entries.get("cancel"), "Cancelar");
  assert.deepEqual(
    parseProperties(spanishGwtMessagesVendor),
    entries,
    "El bundle español generado dentro del cliente GWT debe coincidir con la fuente Rubrova."
  );
  assert.ok(sourcePatch.includes("GWT_MESSAGES_SOURCE"));
  assert.ok(sourcePatch.includes("GWT_MESSAGES_TARGET"));
});

test("el POS separa la cuenta central del cajón de efectivo", () => {
  assert.ok(paymentMethodSource.includes("CONSTRAINT account(Pos p) = cashAccount(p)"));
  assert.ok(paymentMethodSource.includes("La cuenta central de caja no puede ser la misma que la cuenta de efectivo"));
  assert.ok(sourcePatch.includes("CASH_ACCOUNT_REQUIRED_MARKER"));
  assert.ok(sourcePatch.includes("CASH_ACCOUNT_ANCHOR"));
  assert.ok(runtimeSmokeSource.includes("centralCashAccountName = Retail.nameAccount"));
  assert.ok(uiSmokeSource.includes("UI_POS_CASH_ACCOUNTS_DISTINCT=true"));
  assert.ok(runtimeWorkflowSource.includes("CONSTRAINT account(Pos p) = cashAccount(p)"));
});

test("MyCompany guarda cambios pendientes antes de abrir NEWSESSION en acciones documentales", () => {
  const expectedPaths = [
    "vendor/mycompany/src/main/lsfusion/inventory/receipts/Receipt.lsf",
    "vendor/mycompany/src/main/lsfusion/inventory/receipts/ReceiptScrap.lsf",
    "vendor/mycompany/src/main/lsfusion/inventory/receipts/shipment/ReceiptShipment.lsf",
    "vendor/mycompany/src/main/lsfusion/inventory/scraps/Scrap.lsf",
    "vendor/mycompany/src/main/lsfusion/inventory/shipments/Shipment.lsf",
    "vendor/mycompany/src/main/lsfusion/inventory/shipments/receipt/ShipmentReceipt.lsf",
    "vendor/mycompany/src/main/lsfusion/invoicing/bills/Bill.lsf",
    "vendor/mycompany/src/main/lsfusion/invoicing/invoices/Invoice.lsf",
    "vendor/mycompany/src/main/lsfusion/purchase/orders/PurchaseOrder.lsf",
    "vendor/mycompany/src/main/lsfusion/sales/orders/SalesOrder.lsf"
  ];
  assert.ok(sourcePatch.includes("NEWSESSION_GUARD_TARGETS"));
  assert.ok(sourcePatch.includes("def apply_newsession_guards()"));
  assert.ok(sourcePatch.includes("remainder.startswith(expected_guard)"));
  for (const path of expectedPaths) assert.ok(sourcePatch.includes(path), "Falta el backport: " + path);
  assert.ok(sourcePatch.includes("9dca1499bd4e2615d34983fe77c2927560fd5f9b"));
});

test("todas las llamadas HTTP heredadas tienen un límite global efectivo", () => {
  const callHttpSource = read("vendor/platform/server/src/main/java/lsfusion/server/physics/dev/integration/external/to/CallHTTPAction.java");
  assert.match(callHttpSource, /RUBROVA_DEFAULT_EXTERNAL_HTTP_TIMEOUT_MS = 10_000L/);
  assert.match(callHttpSource, /RUBROVA_MAX_EXTERNAL_HTTP_TIMEOUT_MS = 60_000L/);
  assert.match(callHttpSource, /Math\.min\(configuredTimeout, RUBROVA_MAX_EXTERNAL_HTTP_TIMEOUT_MS\)/);
  assert.match(callHttpSource, /return RUBROVA_DEFAULT_EXTERNAL_HTTP_TIMEOUT_MS/);
  assert.match(sourcePatch, /10_000L/);
  assert.match(sourcePatch, /60_000L/);
  assert.match(sourcePatch, /REPLACEMENTS/);
  assert.match(sourcePatch, /No se aplicó el parche/);

  const sourceRoots = [
    path.join(root, "vendor/mycompany/src/main/lsfusion"),
    path.join(root, "extensions/lsfusion")
  ];
  const sourceFiles = [];
  const walk = (directory) => {
    for (const entry of readdirSync(directory, { withFileTypes: true })) {
      const fullPath = path.join(directory, entry.name);
      if (entry.isDirectory()) walk(fullPath);
      else if (entry.isFile() && entry.name.endsWith(".lsf")) sourceFiles.push(fullPath);
    }
  };
  for (const directory of sourceRoots) {
    if (existsSync(directory)) walk(directory);
  }
  const numericOverrides = [];
  let externalHttpCalls = 0;
  for (const file of sourceFiles) {
    const source = readFileSync(file, "utf8");
    externalHttpCalls += (source.match(/EXTERNAL HTTP/g) || []).length;
    for (const match of source.matchAll(/timeoutHttp\(\)\s*<-\s*(\d+)\s*;/g)) {
      numericOverrides.push({ file, value: Number(match[1]) });
    }
  }
  assert.ok(externalHttpCalls > 0, "No se inspeccionaron llamadas HTTP de los módulos integrados.");
  const unsafe = numericOverrides.filter(item => item.value < 1 || item.value > 60_000);
  assert.deepEqual(unsafe, [], "Hay módulos que exceden el máximo global de timeout HTTP.");
});
