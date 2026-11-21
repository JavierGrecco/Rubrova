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
const runtimeWorkflowSource = read(".github/workflows/platform-extension.yml");
const mockProviderSource = read("scripts/platform/mock-integration-provider.py");
const sourcePatch = read("scripts/platform/apply-rubrova-source-patches.py");

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
  assert.match(preparerSource, new RegExp("^JAR_SHA256=\"" + lock.artifacts.applicationJar.sha256 + "\"$", "m"));
  assert.match(preparerSource, new RegExp("^COMPOSE_SHA256=\"" + lock.artifacts.dockerCompose.sha256 + "\"$", "m"));
  assert.match(preparerSource, /El Compose existente no coincide con el SHA-256 fijado/);
  assert.match(preparerSource, /Hash SHA-256 incorrecto para el Compose/);
});

test("el smoke test ejecuta sólo en Linux x86_64, configura la extensión y limpia el stack", () => {
  assert.match(runtimeSmokeSource, /uname -s/);
  assert.match(runtimeSmokeSource, /uname -m/);
  assert.match(runtimeSmokeSource, /Linux.*x86_64/);
  assert.match(runtimeSmokeSource, /logics\.topModule = RubrovaCustom/);
  assert.match(runtimeSmokeSource, /compose config --quiet/);
  assert.match(runtimeSmokeSource, /compose up -d/);
  assert.match(runtimeSmokeSource, /RUBROVA_PLAYWRIGHT_PYTHON/);
  assert.match(runtimeSmokeSource, /rubrova-ci/);
  assert.match(runtimeSmokeSource, /rubrova-ci-product/);
  assert.match(runtimeSmokeSource, /Producto de prueba Rubrova/);
  assert.match(runtimeSmokeSource, /7790000000013/);
  assert.match(runtimeSmokeSource, /salesPrice\(productCI\) <- 1250/);
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
  assert.match(uiSmokeSource, /click_exact_link\(page, "Comercio"\)/);
  assert.match(uiSmokeSource, /def wait_for_exact_link\(page: Any, label: str, timeout_seconds: int = 12\)/);
  assert.match(uiSmokeSource, /wait_for_exact_link\(page, "Punto de venta", timeout_seconds=12\)/);
  assert.match(uiSmokeSource, /El menú Comercio no mostró la opción/);
  assert.match(uiSmokeSource, /click_exact_link\(page, "Punto de venta"\)/);
  assert.match(uiSmokeSource, /UI_RETAIL_NAVIGATION/);
  assert.match(uiSmokeSource, /wait_until_form_loaded\(page, "UI_POS_SCREEN", timeout_seconds=45\)/);
  assert.match(uiSmokeSource, /UI_POS_SCREEN_AVAILABLE=true/);
  assert.doesNotMatch(uiSmokeSource, /UI_POS_SCREEN_AVAILABLE=false/);
  assert.match(uiSmokeSource, /def click_exact_action\(page: Any, label: str\)/);
  assert.match(uiSmokeSource, /UI_ACTION_.*_CLICKED=true/);
  assert.match(uiSmokeSource, /wait_for_session_open\(page, timeout_seconds=45\)/);
  assert.match(uiSmokeSource, /UI_SESSION_OPEN=true/);
  assert.match(uiSmokeSource, /UI_SESSION_CLOSE_ACTION_FOUND=true/);
  assert.match(uiSmokeSource, /UI_SESSION_SCREENSHOT/);
  assert.match(uiSmokeSource, /Buscar artículos/);
  assert.match(uiSmokeSource, /Producto de prueba Rubrova/);
  assert.match(uiSmokeSource, /UI_TEST_PRODUCT_FOUND=true/);
  assert.match(uiSmokeSource, /UI_TEST_PRODUCT_ADDED_TO_RECEIPT=true/);
  assert.match(uiSmokeSource, /UI_PAYMENT_DIALOG_OPEN=true/);
  assert.match(uiSmokeSource, /UI_PAYMENT_CASH_METHOD_AVAILABLE=true/);
  assert.match(uiSmokeSource, /UI_PAYMENT_DIALOG_CLOSED_WITHOUT_CHARGE=true/);
  assert.match(uiSmokeSource, /UI_RECEIPT_WITH_ITEM/);
  assert.match(uiSmokeSource, /UI_ITEM_SCREENSHOT/);
  assert.match(uiSmokeSource, /no se registra ninguna venta/);
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
  assert.match(uiSmokeSource, /UI_CART_PRODUCT_DOM/);
  assert.match(uiSmokeSource, /UI_CART_AMOUNT_LABELS/);
  assert.match(runtimeSmokeSource, /RubrovaIntegrationResilience=\$RUBROVA_RESILIENCE_LOG_EVIDENCE/);
  assert.match(runtimeSmokeSource, /docker inspect/);
  assert.match(runtimeSmokeSource, /docker exec/);
  assert.match(runtimeSmokeSource, /logics\\\\\.\(topModule\|includePaths\|excludePaths\)/);
  assert.match(runtimeSmokeSource, /EXPECTED_UPSTREAM_MODULES=712/);
  assert.match(runtimeSmokeSource, /EXPECTED_TOTAL_MODULES/);
  assert.ok(runtimeSmokeSource.includes('EXPECTED_UPSTREAM_MODULES + 4'));
  assert.match(runtimeSmokeSource, /RubrovaCISalesFixture[.]lsf/);
  assert.match(runtimeSmokeSource, /currency\(priceType\('retail'\)\) <- defaultCurrency\(\)/);
  assert.match(runtimeSmokeSource, /RUBROVA_CI_SALES_LOG_EVIDENCE/);
  assert.match(uiSmokeSource, /UI_CART_PRODUCT_DOM/);
  assert.match(uiSmokeSource, /UI_CART_AMOUNT_LABELS/);
  assert.match(runtimeSmokeSource, /RUBROVA_RESILIENCE_LOG_EVIDENCE/);
  assert.match(runtimeSmokeSource, /RubrovaIntegrationResilience\|RubrovaCISalesFixture\|topModule/);
  assert.match(runtimeSmokeSource, /MODULE_PROGRESS_CHANGED_AT/);
  assert.match(runtimeSmokeSource, /Exception while starting logics instance/);
  assert.match(runtimeSmokeSource, /missing \.\+ at/);
  assert.match(runtimeSmokeSource, /se cancela la espera de arranque/);
  assert.match(runtimeSmokeSource, /módulos Rubrova/);
  assert.match(runtimeSmokeSource, /http:\/\/127\.0\.0\.1:8080/);
  assert.match(runtimeSmokeSource, /compose down --volumes --remove-orphans/);
  assert.match(runtimeSmokeSource, /trap cleanup EXIT/);
  assert.match(runtimeSmokeSource, /mktemp -d.*rubrova-runtime/);
  assert.match(runtimeSmokeSource, /sudo -n rm -rf/);
  assert.match(runtimeSmokeSource, /docker image inspect/);
  for (const [service, image] of Object.entries({
    mycompany: "lsfusion/mycompany:6.2",
    server: "lsfusion/server:6.2",
    client: "lsfusion/client:6.2",
    postgres: "postgres:18"
  })) {
    const digest = lock.dockerImages[service].digest;
    assert.match(digest, /^sha256:[0-9a-f]{64}$/);
    assert.ok(runtimeSmokeSource.includes(`image: ${image}@${digest}`), `Falta digest fijado en el smoke test: ${service}`);
  }
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
  assert.match(resilienceSource, /GROUP MAX responseHeaders/);
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
  assert.ok(runtimeSmokeSource.includes("Invoicing.currency(Invoicing.invoiceType('retail')) <- defaultCurrency()"));
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
  assert.match(runtimeSmokeSource, /mock-integration-provider[.]py/);
  assert.match(runtimeSmokeSource, /host[.]docker[.]internal:host-gateway/);
  assert.match(runtimeSmokeSource, /ghcr[.]io\/shopify\/toxiproxy:2[.]13[.]0/);
  assert.match(runtimeSmokeSource, /9941f0357759e6c9bfe0ad45e20c415100505113da0f5c436cfd0a4d27579fdc/);
  assert.match(runtimeSmokeSource, /127[.]0[.]0[.]1:18474:8474/);
  assert.match(runtimeSmokeSource, /rubrova_ci_normal/);
  assert.match(runtimeSmokeSource, /rubrova_ci_timeout/);
  assert.match(runtimeSmokeSource, /"type":"timeout"/);
  assert.match(runtimeSmokeSource, /"timeout":0/);
  assert.match(runtimeSmokeSource, /MOCK_PROVIDER_TIMEOUT_URL="http:\/\/toxiproxy:8667"/);
  assert.match(runtimeSmokeSource, /drop-response/);
  assert.match(runtimeSmokeSource, /Toxiproxy listo/);
  assert.match(runtimeSmokeSource, /TOXIPROXY_AUTH_TOKEN/);
  assert.match(runtimeSmokeSource, /secrets[.]token_urlsafe\(32\)/);
  assert.ok(runtimeSmokeSource.includes('Authorization: Bearer $TOXIPROXY_AUTH_TOKEN'));
  assert.match(runtimeSmokeSource, /rubrovaTestHttpTimeout/);
  assert.match(runtimeSmokeSource, /rubrovaTestHttpRecovery/);
  assert.match(runtimeSmokeSource, /rubrovaTestHttpRateLimit/);
  assert.match(runtimeSmokeSource, /rubrovaTestHttpTransientStatus/);
  assert.match(runtimeSmokeSource, /rubrovaTestHttpServerError/);
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
  assert.ok(runtimeSmokeSource.includes("Invoicing.currency(Invoicing.invoiceType('retail')) <- defaultCurrency()"));
  assert.match(uiSmokeSource, /UI_POS_EFFECTIVE_CONFIGURATION/);
  assert.ok(uiSmokeSource.includes('UI_INTEGRATION_{status_code}_CLASSIFIED=true'));
  assert.match(uiSmokeSource, /rubrovaTestPosConfigurationApi/);
  assert.match(uiSmokeSource, /UI_INTEGRATION_TIMEOUT_CAPTURED=true/);
  assert.match(uiSmokeSource, /UI_INTEGRATION_TIMEOUT_MESSAGE=true/);
  assert.match(uiSmokeSource, /UI_INTEGRATION_408_CLASSIFIED=true/);
  assert.match(uiSmokeSource, /UI_INTEGRATION_429_CLASSIFIED=true/);
  assert.match(uiSmokeSource, /UI_INTEGRATION_503_CLASSIFIED=true/);
  assert.match(uiSmokeSource, /UI_INTEGRATION_RECOVERY_SUCCEEDED=true/);
  assert.match(uiSmokeSource, /UI_INTEGRATION_INCIDENT_PERSISTED=true/);
  assert.match(mockProviderSource, /ThreadingHTTPServer/);
  assert.ok(mockProviderSource.includes('if request.path == "/slow":'));
  assert.ok(mockProviderSource.includes('if request.path == "/ok":'));
  assert.ok(mockProviderSource.includes('if request.path == "/status/408":'));
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
