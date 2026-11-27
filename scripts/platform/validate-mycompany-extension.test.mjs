import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync, readdirSync, existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const read = (relative) => readFileSync(path.join(root, relative), "utf8");

const lock = JSON.parse(read("platform/mycompany-6.2.lock.json"));
const entrypointSource = read("extensions/lsfusion/RubrovaCustom.lsf");
const remoteConnectionSource = read("vendor/platform/server/src/main/java/lsfusion/server/physics/admin/authentication/controller/remote/RemoteConnection.java");
const moduleSource = read("extensions/lsfusion/RubrovaPOSLocalization.lsf");
const resilienceSource = read("extensions/lsfusion/RubrovaIntegrationResilience.lsf");
const paymentTerminalSource = read("extensions/lsfusion/RubrovaPaymentTerminals.lsf");
const replenishmentExportSource = read("extensions/lsfusion/RubrovaReplenishmentExport.lsf");
const retailReturnsSource = read("extensions/lsfusion/RubrovaRetailReturns.lsf");
const retailRefundLimitsSource = read("extensions/lsfusion/RubrovaRetailRefundLimits.lsf");
const creditNoteSource = read("vendor/mycompany/src/main/lsfusion/invoicing/invoices/creditnotes/CreditNote.lsf");
const creditNoteReceiptInitialSource = read("vendor/mycompany/src/main/lsfusion/invoicing/inventory/receipts/CreditNoteReceiptInitial.lsf");
const returnPaymentSource = read("vendor/mycompany/src/main/lsfusion/retail/pos/dashboard/return/PosDashboardReturnPayment.lsf");
const cashMovementSource = read("vendor/mycompany/src/main/lsfusion/retail/pos/dashboard/cash/PosDashboardCash.lsf");
const replenishmentBridgeSource = read("scripts/replenishment/adapt_mycompany_native_export.py");
const replenishmentBridgeTestsSource = read("scripts/replenishment/test_adapt_mycompany_native_export.py");
const nativeReplenishmentFixture = JSON.parse(read("docs/fixtures/mycompany-native-replenishment-export.json"));
const replenishmentPolicyFixture = JSON.parse(read("docs/fixtures/replenishment-planning-policy.json"));
const paymentArchitectureSource = read("docs/PAYMENT_TERMINAL_INTEGRATION_ARCHITECTURE.md");
const bundle = read("extensions/lsfusion/MyCompanyResourceBundle_es_AR.properties");
const preparerSource = read("scripts/platform/prepare-mycompany-6.2.sh");
const runtimeSmokeSource = read("scripts/platform/test-runtime-smoke.sh");
const nativeSmokeSource = read("scripts/platform/test-runtime-native-smoke.sh");
const nativeSalesFixtureSource = read("scripts/platform/fixtures/RubrovaCISalesFixture.lsf");
const paymentLedgerSource = read("vendor/mycompany/src/main/lsfusion/invoicing/ledgers/Payment.lsf");
const nativeRetailFixtureSource = read("scripts/platform/fixtures/RubrovaCIRetailFixture.lsf");
const nativeLocalDemoRetailSource = read("scripts/platform/fixtures/RubrovaLocalDemoRetail.lsf");
const retailPaymentMethodInitialSource = read("vendor/mycompany/src/main/lsfusion/retail/payments/PaymentMethodInitial.lsf");
const incomingPaymentInitialSource = read("vendor/mycompany/src/main/lsfusion/invoicing/payments/incoming/IncomingPaymentInitial.lsf");
const outgoingPaymentInitialSource = read("vendor/mycompany/src/main/lsfusion/invoicing/payments/outgoing/OutgoingPaymentInitial.lsf");
const nativeIntegrationFixtureSource = read("scripts/platform/fixtures/RubrovaCIIntegrationFixture.lsf");
const nativeReplenishmentFixtureSource = read("scripts/platform/fixtures/RubrovaCIReplenishmentFixture.lsf");
const uiSmokeSource = read("scripts/platform/inspect-mycompany-ui.py");
const nativeListenerCheckSource = read("scripts/platform/native-listener-check.sh");
const nativeListenerCheckTestsSource = read("scripts/platform/test-native-listener-check.sh");
const nativePreviewSource = read("scripts/platform/run-local-native-preview.py");
const nativeRuntimeTestsSource = read("scripts/platform/test_runtime_native_preview.py");
const localPreviewSource = read("scripts/platform/run-local-preview-macos.sh");
const dockerOverrideSource = read("platform/compose.rubrova.override.yaml");
const deploySmokeSource = read("scripts/platform/test-deploy-mycompany-6.2.sh");
const nativeRuntimeUrlSource = read("scripts/platform/native_runtime_url.py");
const nativeRuntimeUrlTestsSource = read("scripts/platform/test_native_runtime_url.py");
const posSearchSource = read("vendor/mycompany/src/main/lsfusion/retail/pos/dashboard/PosDashboardSearch.lsf");
const paymentMethodSource = read("vendor/mycompany/src/main/lsfusion/retail/pos/PosPaymentMethod.lsf");
const cashAccountSource = read("vendor/mycompany/src/main/lsfusion/invoicing/accounts/cash/CashAccount.lsf");
const bankAccountSource = read("vendor/mycompany/src/main/lsfusion/invoicing/accounts/bank/BankAccount.lsf");
const billSource = read("vendor/mycompany/src/main/lsfusion/invoicing/bills/Bill.lsf");
const invoiceSource = read("vendor/mycompany/src/main/lsfusion/invoicing/invoices/Invoice.lsf");
const incomingPaymentSource = read("vendor/mycompany/src/main/lsfusion/invoicing/payments/incoming/IncomingPayment.lsf");
const outgoingPaymentSource = read("vendor/mycompany/src/main/lsfusion/invoicing/payments/outgoing/OutgoingPayment.lsf");
const itemAttributeSource = read("vendor/mycompany/src/main/lsfusion/masterdata/items/attributes/ItemAttribute.lsf");
const adjustmentListSource = read("vendor/mycompany/src/main/lsfusion/inventory/adjustments/lists/AdjustmentList.lsf");
const markdownViewerSource = read("vendor/mycompany/src/main/lsfusion/utils/MarkdownViewer.lsf");
const runtimeWorkflowSource = read(".github/workflows/platform-extension.yml");
const plannerWorkflowSource = read(".github/workflows/replenishment-planner.yml");
const localPreflightSource = read("scripts/platform/local-preflight.sh");
const mockProviderSource = read("scripts/platform/mock-integration-provider.py");
const runtimeImageBuilderSource = read("scripts/platform/build-rubrova-runtime-images.sh");
const runtimeServerDockerfile = read("build/rubrova/runtime/Dockerfile.server");
const runtimeClientDockerfile = read("build/rubrova/runtime/Dockerfile.client");
const sourcePatch = read("scripts/platform/apply-rubrova-source-patches.py");
const dialogBoxHelperSource = read("vendor/platform/web-client/src/main/java/lsfusion/gwt/client/base/view/DialogBoxHelper.java");
const modalWindowSource = read("vendor/platform/web-client/src/main/java/lsfusion/gwt/client/base/view/ModalWindow.java");
const formButtonSource = read("vendor/platform/web-client/src/main/java/lsfusion/gwt/client/base/view/FormButton.java");
const spanishGwtMessagesSource = read("patches/lsfusion/ClientMessages_es.properties");
const gwtModuleSource = read("vendor/platform/web-client/src/main/java/lsfusion/gwt/main.gwt.xml");
const spanishGwtMessagesVendor = read("vendor/platform/web-client/src/main/java/lsfusion/gwt/client/ClientMessages_es.properties");
const spanishServerMessagesSource = read("patches/lsfusion/ServerResourceBundle_es.properties");
const spanishServerMessagesVendor = read("vendor/platform/server/src/main/resources/ServerResourceBundle_es.properties");
const spanishWebMessagesSource = read("patches/lsfusion/ServerMessages_es.properties");
const spanishWebMessagesVendor = read("vendor/platform/web-client/src/main/resources/ServerMessages_es.properties");
const serverMessagesClass = read("vendor/platform/web-client/src/main/java/lsfusion/base/ServerMessages.java");


function braceDepthAt(source, stopAt) {
  let depth = 0;
  let quote = null;
  let lineComment = false;
  let blockComment = false;
  for (let index = 0; index < stopAt; index += 1) {
    const current = source[index];
    const next = source[index + 1];
    if (lineComment) {
      if (current === "\n") lineComment = false;
      continue;
    }
    if (blockComment) {
      if (current === "*" && next === "/") {
        blockComment = false;
        index += 1;
      }
      continue;
    }
    if (quote) {
      if (current === "\\") {
        index += 1;
      } else if (current === quote) {
        quote = null;
      }
      continue;
    }
    if (current === "/" && next === "/") {
      lineComment = true;
      index += 1;
    } else if (current === "/" && next === "*") {
      blockComment = true;
      index += 1;
    } else if (current === "'" || current === '"') {
      quote = current;
    } else if (current === "{") {
      depth += 1;
    } else if (current === "}") {
      depth -= 1;
    }
  }
  return depth;
}

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

test("la inicialización de conexiones RMI serializa las escrituras de locale por usuario", () => {
  const init = remoteConnectionSource.split("public void initConnectionContext")[1]?.split("private void initUser")[0] || "";
  assert.match(remoteConnectionSource, /private static final Object\[\] userContextLocks = createUserContextLocks\(\)/);
  assert.match(remoteConnectionSource, /Math[.]floorMod\(login == null \? 0 : login[.]hashCode\(\), userContextLocks[.]length\)/);
  assert.match(init, /String userLogin = securityManager[.]parseToken\(token\)/);
  assert.match(init, /synchronized \(userContextLock\(userLogin\)\)/);
  assert.ok(
    init.indexOf("synchronized (userContextLock(userLogin))") < init.indexOf("getExecSession()"),
    "El bloqueo por usuario debe adquirirse antes de abrir una transacción PostgreSQL."
  );
  assert.match(remoteConnectionSource, /clientLanguage[.]change\(userInfo[.]language, session, user\)/);
});

test("el smoke aceptado corre en Linux x86_64 y sólo admite emulación Mac con opt-in", () => {
  assert.match(runtimeSmokeSource, /uname -s/);
  assert.match(runtimeSmokeSource, /uname -m/);
  assert.match(runtimeSmokeSource, /Linux.*x86_64/);
  assert.match(runtimeSmokeSource, /Darwin.*arm64/);
  assert.match(runtimeSmokeSource, /RUBROVA_ALLOW_EXPERIMENTAL_MACOS_AMD64_EMULATION/);
  assert.match(runtimeSmokeSource, /LOCAL_MAC_PREVIEW=true/);
  assert.match(runtimeSmokeSource, /platform: linux\/amd64/);
  assert.match(runtimeSmokeSource, /ports: !override/);
  assert.match(runtimeSmokeSource, /127[.]0[.]0[.]1:8080:8080/);
  assert.match(runtimeSmokeSource, /127[.]0[.]0[.]1:7652:7652/);
  assert.match(runtimeSmokeSource, /RUBROVA_KEEP_RUNTIME_STACK/);
  assert.match(runtimeSmokeSource, /VISTA PREVIA RUBROVA ACTIVA/);
  assert.match(runtimeSmokeSource, /logics\.topModule = RubrovaCustom/);
  assert.match(runtimeSmokeSource, /compose config --quiet/);
  assert.match(runtimeSmokeSource, /compose up -d/);
  assert.ok(runtimeSmokeSource.includes('    image: $CLIENT_IMAGE\n    platform: linux/amd64\n    networks:\n      - default\n      - ingress\n    # Publish through the non-internal ingress bridge, bound only to loopback.\n    ports: !override\n      - "127.0.0.1:8080:8080"\n    pull_policy: never'));
  assert.match(runtimeSmokeSource, /CLIENT_HOST_BINDINGS_JSON/);
  assert.match(runtimeSmokeSource, /HostIp/);
  assert.match(runtimeSmokeSource, /HostPort/);
  assert.match(runtimeSmokeSource, /RUBROVA_CLIENT_LOOPBACK_BINDING=127[.]0[.]0[.]1:8080/);
  assert.match(runtimeSmokeSource, /diagnose_client_web_connectivity/);
  assert.match(runtimeSmokeSource, /--noproxy/);
  assert.match(runtimeSmokeSource, /RUBROVA_HTTP_DIAGNOSTIC_GRACE_SECONDS/);
  assert.match(runtimeSmokeSource, /:1F90/);
  assert.match(runtimeSmokeSource, /CLIENT_INTERNAL_HTTP/);
  assert.match(runtimeSmokeSource, /RUBROVA_CLIENT_PUBLISHED_PORT=127[.]0[.]0[.]1:8080/);
  assert.match(runtimeSmokeSource, /enable_ip_masquerade: "false"/);
  assert.match(runtimeSmokeSource, /networks:\n      - default\n      - ingress/);
  assert.match(runtimeSmokeSource, /RUBROVA_CLIENT_EXTERNAL_EGRESS=blocked/);
  assert.match(runtimeSmokeSource, /RUBROVA_INGRESS_EGRESS_MASQUERADE=false/);
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
  assert.match(runtimeSmokeSource, /COLD_SERVER_LOGS/);
  assert.match(runtimeSmokeSource, /SERVER_FINAL_START_TIMEOUT_SECONDS/);
  assert.match(runtimeSmokeSource, /COLD_SERVER_READY=true/);
  assert.match(runtimeSmokeSource, /Server has successfully started in/);
  assert.match(runtimeSmokeSource, /METRIC_COLD_SERVER_STARTUP_MS/);
  assert.match(runtimeSmokeSource, /METRIC_COLD_SQL_TIMEOUTS/);
  assert.match(runtimeSmokeSource, /METRIC_COLD_MATERIALIZATION_TIMEOUTS/);
  assert.ok(
    runtimeSmokeSource.includes('COLD_MATERIALIZATION_TIMEOUTS="$(count_file_matches "$LOG_DIR/adjust.log" \'FAILED TIMEOUT\')"'),
    "Los timeouts de materialización se registran en adjust.log, no en start.log."
  );
  assert.ok(
    runtimeSmokeSource.includes('PRE_RESTART_MATERIALIZATION_TIMEOUTS="$(count_file_matches "$LOG_DIR/adjust.log" \'FAILED TIMEOUT\')"')
    && runtimeSmokeSource.includes('AFTER_RESTART_MATERIALIZATION_TIMEOUTS="$(count_file_matches "$LOG_DIR/adjust.log" \'FAILED TIMEOUT\')"'),
    "La medición fría y caliente debe leer el mismo archivo adjust.log."
  );
  assert.match(runtimeSmokeSource, /compose restart server/);
  assert.match(runtimeSmokeSource, /compose restart client/);
  assert.ok(runtimeSmokeSource.includes('extract_last_server_startup_ms "$SERVER_RESTART_LOGS"'));
  assert.ok(
    runtimeSmokeSource.indexOf('Arranque completo: onStarted terminó') <
    runtimeSmokeSource.indexOf('COLD_SERVER_READY=true'),
    "La medición fría debe esperar a la finalización del motor, posterior a onStarted."
  );
  assert.match(runtimeSmokeSource, /METRIC_WARM_SERVER_STARTUP_MS/);
  assert.match(runtimeSmokeSource, /METRIC_WARM_ONSTARTED_EVENTS/);
  assert.match(runtimeSmokeSource, /METRIC_WARM_SQL_TIMEOUTS/);
  assert.match(runtimeSmokeSource, /METRIC_WARM_MATERIALIZATION_TIMEOUTS/);
  assert.match(runtimeSmokeSource, /RUBROVA_UI_VERIFY_PERSISTED_ONLY/);
  assert.match(runtimeSmokeSource, /RUBROVA_UI_TEST_LOGIN:-false/);
  assert.match(runtimeSmokeSource, /count_delta_after_restart/);
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
  assert.match(uiSmokeSource, /def wait_until_form_loaded\(/);
  assert.match(uiSmokeSource, /register_name: str = "Caja de prueba Rubrova"/);
  assert.match(uiSmokeSource, /register_available = register_name in searchable/);
  assert.match(uiSmokeSource, /register_name=pos_register_name/);
  assert.match(uiSmokeSource, /def select_pos_register\(page: Any, register_name: str\)/);
  assert.ok(uiSmokeSource.includes('radio_id = visible_matches[0].get_attribute("for")'));
  assert.ok(uiSmokeSource.includes("radio.is_checked()"));
  assert.ok(uiSmokeSource.includes("UI_POS_REGISTER_ALREADY_SELECTED=true"));
  assert.ok(uiSmokeSource.includes("page.mouse.move(0, 0)"));
  assert.ok(uiSmokeSource.includes("radio.check(timeout=10_000)"));
  assert.ok(uiSmokeSource.includes("UI_POS_REGISTER_SELECTION_VERIFIED=true"));
  assert.match(uiSmokeSource, /select_pos_register\(page, pos_register_name\)/);
  assert.match(uiSmokeSource, /rubrovaTestPosSessionSelectionApi/);
  assert.match(uiSmokeSource, /UI_POS_SESSION_BOUND_TO_REQUESTED_REGISTER=true/);
  assert.match(nativeSalesFixtureSource, /rubrovaTestPosSessionSelectionApi/);
  assert.match(nativeSalesFixtureSource, /mainOpenSessions = rubrovaCIMainOpenSessionCount\(\)/);
  assert.match(nativeSalesFixtureSource, /refundOpenSessions = rubrovaCIRefundOpenSessionCount\(\)/);
  assert.match(uiSmokeSource, /RUBROVA_UI_POS_REGISTER_NAME/);
  assert.match(uiSmokeSource, /wait_until_form_loaded\([\s\S]*?"UI_POS_SCREEN",[\s\S]*?register_name=pos_register_name,[\s\S]*?\)/);
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
  assert.ok(uiSmokeSource.includes('sales_api_base = application_endpoint_url(url, "exec/Sales.")'));
  assert.ok(uiSmokeSource.includes('api_base = application_endpoint_url(url, "exec/Rubrova.")'));
  assert.ok(uiSmokeSource.includes('base = application_endpoint_url(url, "exec/")'));
  assert.ok(!uiSmokeSource.includes('url.rstrip("/") + "/exec/'));
  assert.match(uiSmokeSource, /def attach_browser_diagnostics\(/);
  assert.match(uiSmokeSource, /page[.]on\("pageerror", on_page_error\)/);
  assert.ok(uiSmokeSource.includes('"dispatch_responses"'));
  assert.match(nativeRuntimeUrlSource, /urlsplit\(base_url\)/);
  assert.match(nativeRuntimeUrlSource, /urlunsplit\(/);
  assert.match(nativeRuntimeUrlTestsSource, /test_login_route_does_not_become_an_api_path_prefix/);
  assert.ok(uiSmokeSource.includes('sales_api_base + "rubrovaTestSalesReconciliationApi"'));
  assert.ok(uiSmokeSource.includes('sales_api_base + "rubrovaTestInventoryApi"'));
  assert.match(uiSmokeSource, /UI_SALE_PAYMENT_RECONCILED=true/);
  assert.match(uiSmokeSource, /UI_SALE_CASH_BALANCE_RECONCILED=true/);
  assert.match(uiSmokeSource, /UI_SALE_STOCK_DEDUCTED=true/);
  assert.match(uiSmokeSource, /def verify_restarted_persistence\(/);
  assert.match(uiSmokeSource, /RUBROVA_UI_VERIFY_PERSISTED_ONLY/);
  assert.match(uiSmokeSource, /UI_RESTART_PERSISTENCE_SALE_RECONCILED=true/);
  assert.match(uiSmokeSource, /UI_RESTART_PERSISTENCE_STOCK_RECONCILED=true/);
  assert.match(uiSmokeSource, /UI_RESTART_PERSISTENCE_SESSION_CLOSED=true/);
  assert.match(uiSmokeSource, /UI_RESTART_PERSISTENCE_INCIDENTS_RETAINED=true/);
  assert.match(uiSmokeSource, /UI_RESTART_PERSISTENCE_VERIFIED=true/);
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
  assert.match(uiSmokeSource, /RUBROVA_UI_STOP_AFTER_LOGIN/);
  assert.match(runtimeWorkflowSource, /playwright==1[.]65[.]2/);
  assert.match(runtimeWorkflowSource, /playwright install chromium/);
  assert.equal((runtimeWorkflowSource.match(/PLAYWRIGHT_BROWSERS_PATH:/g) || []).length, 6, "Cada instalación y ejecución de Playwright debe declarar una caché de navegadores explícita.");
  assert.equal(runtimeWorkflowSource.split("PLAYWRIGHT_BROWSERS_PATH: ${{ runner.temp }}/rubrova-native-playwright-browsers").length - 1, 4, "Los smokes nativos deben compartir la misma caché de Chromium.");
  assert.equal(runtimeWorkflowSource.split("PLAYWRIGHT_BROWSERS_PATH: ${{ runner.temp }}/rubrova-playwright-browsers").length - 1, 2, "El smoke Docker debe compartir la caché de Chromium entre instalación y ejecución.");
  assert.equal((runtimeWorkflowSource.match(/RUBROVA_PLAYWRIGHT_BROWSER_READY=true/g) || []).length, 3, "Cada job que instala Chromium debe comprobar que el navegador realmente puede arrancar.");
  assert.match(runtimeWorkflowSource, /RUBROVA_UI_TEST_LOGIN: "true"/);
  assert.match(runtimeWorkflowSource, /RUBROVA_UI_READY_TIMEOUT_SECONDS: 180/);
  assert.ok(runtimeWorkflowSource.includes("group: rubrova-runtime-smoke-${{ github.ref }}"));
  assert.match(runtimeWorkflowSource, /build-fork:/);
  assert.ok(runtimeWorkflowSource.includes("group: rubrova-build-fork-${{ github.ref }}"));
  assert.ok(
    runtimeWorkflowSource.includes("group: rubrova-platform-${{ github.event.pull_request.number || github.ref }}"),
    "El workflow completo debe cancelar la corrida anterior del mismo PR cuando llega un commit nuevo."
  );
  assert.equal(
    (runtimeWorkflowSource.match(/^      cancel-in-progress: true$/gm) || []).length,
    4,
    "El build, los dos smoke nativos y la aceptación Docker deben conservar sus controles de concurrencia por job."
  );
  assert.doesNotMatch(runtimeWorkflowSource, /cancel-in-progress: false/);
  assert.match(runtimeWorkflowSource, /native-runtime-smoke:\n    if: github[.]event_name == 'workflow_dispatch'/);
  assert.match(runtimeWorkflowSource, /runtime-smoke:\n    if: github[.]event_name == 'workflow_dispatch'/);
  assert.match(runtimeWorkflowSource, /native-runtime-smoke-macos-arm64:/);
  assert.match(runtimeWorkflowSource, /runs-on: macos-26/);
  assert.match(runtimeWorkflowSource, /brew --prefix postgresql@18/);
  assert.match(runtimeWorkflowSource, /python-version: "3[.]13"/);
  assert.match(runtimeWorkflowSource, /RUBROVA_BLOCK_EGRESS: "false"/);
  assert.doesNotMatch(runtimeWorkflowSource, /if: github[.]event_name == 'workflow_dispatch' && inputs[.]validate_macos/);
  assert.match(runtimeWorkflowSource, /RUBROVA_BLOCK_EGRESS: "true"/);
  assert.match(runtimeWorkflowSource, /RUBROVA_POSTGRES_BIN: \/usr\/lib\/postgresql\/18\/bin/);
  assert.doesNotMatch(runtimeWorkflowSource, /if: github[.]event_name == 'workflow_dispatch' && inputs[.]run_docker_smoke/);
  assert.match(runtimeWorkflowSource, /continue-on-error: true/);
  assert.match(runtimeWorkflowSource, /Diagnóstico POS sobre runtime Docker\/Linux \(no bloqueante\)/);
  assert.match(nativeSmokeSource, /run-local-native-preview[.]py/);
  assert.match(nativeSmokeSource, /inspect-mycompany-ui[.]py/);
  assert.match(nativeSmokeSource, /RUBROVA_NATIVE_EGRESS_BLOCKED=true/);
  assert.match(nativeSmokeSource, /RUBROVA_NATIVE_OFFLINE_ACCEPTANCE=not_tested/);
  assert.match(nativeSmokeSource, /RUBROVA_NATIVE_RUNTIME_SURVIVED_LOCAL_PROBE=true/);
  assert.match(nativeSmokeSource, /mock-integration-provider[.]py/);
  assert.match(nativeSmokeSource, /RUBROVA_CI_SALES_FIXTURE=true/);
  assert.match(nativeSmokeSource, /RUBROVA_NATIVE_POS_ACCEPTANCE=passed/);
  assert.match(nativeSmokeSource, /UI_SALE_PAYMENT_RECONCILED=true/);
  assert.match(nativeSmokeSource, /UI_SALE_STOCK_DEDUCTED=true/);
  assert.match(nativeSmokeSource, /RUBROVA_NATIVE_RESTART_PERSISTENCE=passed/);
  assert.match(nativeSmokeSource, /RUBROVA_NATIVE_PORTS_RELEASED=true/);
  assert.match(nativeSmokeSource, /assert_native_ports_released/);
  assert.match(nativeSmokeSource, /lsof -nP -t -iTCP:/);
  assert.match(nativeSmokeSource, /ss -H -ltn/);
  assert.match(nativeSmokeSource, /RUBROVA_UI_VERIFY_PERSISTED_ONLY=true/);
  assert.match(nativeSmokeSource, /UI_RESTART_PERSISTENCE_INCIDENTS_RETAINED=true/);
  assert.match(nativePreviewSource, /signal[.]signal\(signal[.]SIGTERM, handle_shutdown_signal\)/);
  assert.match(nativePreviewSource, /os[.]killpg\(process[.]pid, signal[.]SIGTERM\)/);
  assert.match(nativePreviewSource, /os[.]killpg\(process[.]pid, signal[.]SIGKILL\)/);
  assert.match(nativePreviewSource, /raise KeyboardInterrupt/);
  assert.match(nativePreviewSource, /def ensure_ci_sales_fixture/);
  assert.match(nativePreviewSource, /RUBROVA_CI_SALES_FIXTURE/);
  assert.match(nativeSalesFixtureSource, /REQUIRE MyCompany, RubrovaPOSLocalization, RubrovaCIRetailFixture/);
  assert.match(nativeSalesFixtureSource, /rubrovaTestSalesReconciliationApi/);
  assert.match(nativeSalesFixtureSource, /rubrovaTestSessionCloseApi/);
  assert.match(nativeRetailFixtureSource, /Caja de prueba Rubrova/);
  assert.match(nativeIntegrationFixtureSource, /rubrovaTestHttpRecovery/);
  assert.match(nativePreviewSource, /RubrovaCIReplenishmentFixture[.]lsf/);
  assert.match(nativePreviewSource, /RubrovaCIReplenishmentFixture/);
  assert.match(nativeReplenishmentFixtureSource, /rubrova-ci-outgoing/);
  assert.match(nativeReplenishmentFixtureSource, /rubrova-ci-incoming/);
  const outgoingOrderGrouping = nativeReplenishmentFixtureSource
    .split("rubrovaCIOutgoingOrder() = ")[1]
    ?.split(";")[0] ?? "";
  assert.ok(outgoingOrderGrouping.startsWith("GROUP MAX Sales.Order o"));
  assert.ok(
    outgoingOrderGrouping.includes("\n    IF Sales.customerReference(o) = 'rubrova-ci-outgoing'"),
    "La agrupación lsFusion debe filtrar con IF; WHERE no está permitido en este GroupingType."
  );
  assert.ok(
    !outgoingOrderGrouping.includes("WHERE"),
    "No introducir WHERE después de GROUP MAX en el fixture nativo."
  );
  assert.match(nativeReplenishmentFixtureSource, /rubrovaCIReplenishmentPartner\(\) <- partnerCI/);
  assert.match(nativeReplenishmentFixtureSource, /Sales[.]customer\(salesOrderCI\) <- rubrovaCIReplenishmentPartner\(\)/);
  assert.match(nativeReplenishmentFixtureSource, /Purchase[.]vendor\(purchaseOrderCI\) <- rubrovaCIReplenishmentPartner\(\)/);
  assert.match(nativeReplenishmentFixtureSource, /Sales[.]confirmed\(salesOrderCI\)/);
  assert.match(nativeReplenishmentFixtureSource, /Purchase[.]confirmed\(purchaseOrderCI\)/);
  assert.match(nativeReplenishmentFixtureSource, /rubrovaPrepareOutgoingReservation/);
  assert.match(nativeReplenishmentFixtureSource, /Inventory[.]precheckAvailability\(rubrovaCIOutgoingShipment\(\)\)/);
  assert.match(uiSmokeSource, /def prepare_ci_outgoing_reservation\(/);
  assert.match(uiSmokeSource, /rubrovaPrepareOutgoingReservation/);
  assert.match(uiSmokeSource, /UI_REPLENISHMENT_CI_RESERVATION_PREPARED=/);
  assert.match(nativeReplenishmentFixtureSource, /Inventory[.]increaseAvailableStock\(Inventory[.]receiptType\('receipt'\)\) <- NULL/);
  assert.match(nativeSmokeSource, /RUBROVA_UI_REQUIRE_POSITIVE_REPLENISHMENT=true/);
  assert.match(uiSmokeSource, /RUBROVA_UI_REQUIRE_POSITIVE_REPLENISHMENT/);
  assert.match(uiSmokeSource, /UI_REPLENISHMENT_POSITIVE_FIXTURES/);
  assert.match(uiSmokeSource, /row[.]get\("increaseAvailableStock"\) is not None/);
  assert.match(uiSmokeSource, /incoming_increase_available is True/);
  assert.match(nativeReplenishmentFixtureSource, /increaseAvailableStock.*<- NULL/);
  assert.match(nativeSmokeSource, /native-diagnostics[.]log/);
  assert.match(runtimeWorkflowSource, /rubrova-native-smoke\/native-diagnostics[.]log/);
  assert.doesNotMatch(nativeSmokeSource, /(^|[ \\t])docker([ \\t]|$)|docker-compose/);
  assert.match(nativePreviewSource, /RUBROVA_BUILD_ARTIFACTS_DIR/);
  assert.match(nativePreviewSource, /-Dlsfusion[.]rmi[.]bindAddress=127[.]0[.]0[.]1/);
  assert.match(nativePreviewSource, /def tomcat_startup_diagnostics/);
  assert.match(nativePreviewSource, /ports\['web'\]\}\/login/);
  assert.match(nativeSmokeSource, /RUBROVA_NATIVE_WEB_URL.*8080\/login/);
  assert.match(uiSmokeSource, /127[.]0[.]0[.]1:8080\/login/);
  assert.match(nativePreviewSource, /HTTP 404 en el cliente/);
  assert.match(nativePreviewSource, /ET[.]register_namespace\("", namespace\[1:-1\]\)/);
  assert.match(nativePreviewSource, /manager[.]set\("pathname", ""\)/);
  assert.match(nativeRuntimeTestsSource, /test_existing_tomcat_session_manager_is_made_non_persistent/);
  assert.match(nativePreviewSource, /lsFusion's web sessions contain Spring\/lsFusion objects/);
  assert.match(nativePreviewSource, /PostgreSQL/);
  assert.match(nativePreviewSource, /Tomcat servlet mapping:/);
  assert.match(nativePreviewSource, /Ruta \/login declarada en web.xml/);
  assert.match(nativeRuntimeTestsSource, /self[.]assertIn\('xmlns="http:\/\/java[.]sun[.]com\/xml\/ns\/javaee"'/);
  assert.match(nativeRuntimeTestsSource, /self[.]assertEqual\(servlet_classes[.]get\("LSFWeb"\)/);
  assert.match(nativeRuntimeTestsSource, /self[.]assertIn\("\/login", mappings[.]get\("LSFWeb", \[\]\)\)/);

  assert.match(sourcePatch, /RMI_SERVER_SOCKET_TARGET/);
  assert.match(sourcePatch, /System[.]getProperty\("lsfusion[.]rmi[.]bindAddress"\)/);
  assert.match(sourcePatch, /new InetSocketAddress\(InetAddress[.]getByName/);
  assert.match(nativeSmokeSource, /RMI_LISTENERS=.*ss -H -ltn/);
  assert.match(nativeSmokeSource, /lsof -nP -iTCP:7652 -sTCP:LISTEN/);
  assert.match(nativeSmokeSource, /Linux:x86_64\|Darwin:arm64/);
  assert.match(nativeSmokeSource, /config\["local_runtime"\]\["data_directory"\]/);
  assert.match(nativeSmokeSource, /RUBROVA_NATIVE_RMI_LOOPBACK=true/);
  assert.match(nativeSmokeSource, /RUBROVA_NATIVE_POSTGRES_LOOPBACK=true/);
  assert.match(nativeSmokeSource, /source "\$SCRIPT_DIR\/native-listener-check[.]sh"/);
  assert.match(nativeListenerCheckSource, /\[::ffff:127[.]0[.]0[.]1\]/);
  assert.match(nativeListenerCheckSource, /listener fuera del loopback permitido/);
  assert.match(nativeListenerCheckTestsSource, /192[.]168[.]1[.]20:7652/);
  assert.match(nativeListenerCheckTestsSource, /mixed loopback and external listeners/);
  assert.match(nativeSmokeSource, /RUBROVA_NATIVE_EXTERNAL_CONNECTIVITY=blocked/);
  assert.equal(
    (runtimeWorkflowSource.match(/CHECKED_OUT_SHA=/g) || []).length,
    3,
    "Build y smoke deben registrar y verificar el SHA exacto del checkout."
  );

  assert.match(runtimeWorkflowSource, /needs: \[validate, build-fork\]/);
  assert.match(runtimeWorkflowSource, /java-version: "21"/);
  assert.match(runtimeWorkflowSource, /mvn -B -ntp -f build\/rubrova\/pom[.]xml -Passemble -DskipTests package/);
  assert.match(runtimeWorkflowSource, /Empaquetar servidor y cliente reutilizando GWT/);
  assert.match(runtimeWorkflowSource, /mvn -B -ntp -f vendor/);
  assert.match(runtimeWorkflowSource, /-DskipTests -Dgwt[.]skipCompilation=true package/);
  assert.match(runtimeWorkflowSource, /GWT compilation is skipped/);
  assert.match(runtimeWorkflowSource, /if grep -Fq "Compiling module lsfusion[.]gwt[.]main"/);
  assert.match(runtimeWorkflowSource, /GWT_BOOTSTRAP/);
  assert.match(runtimeWorkflowSource, /GWT_FRAGMENT/);
  assert.match(runtimeWorkflowSource, /timeout --signal=TERM --kill-after=30s 8m/);
  assert.match(runtimeWorkflowSource, /GWT_BOOTSTRAP/);
  assert.match(runtimeWorkflowSource, /GWT_FRAGMENT/);
  assert.match(runtimeWorkflowSource, /timeout --signal=TERM --kill-after=30s 8m/);
  assert.doesNotMatch(runtimeWorkflowSource, /-f vendor\/platform\/pom[.]xml -pl server,web-client -am -Passemble/);
  assert.match(runtimeWorkflowSource, /WEB-INF\/lib\/api-6[.]2[.]jar/);
  assert.match(runtimeWorkflowSource, /rubrova-client-api[.]jar/);
  assert.match(runtimeWorkflowSource, /lsfusion\/base\/DaemonThreadFactory[.]class/);
  assert.match(runtimeWorkflowSource, /lsfusion\/base\/log\/CustodianDailyRollingFileAppender[.]class/);
  assert.match(runtimeWorkflowSource, /org\/apache\/log4j\/rolling\/RollingFileAppender[.]class/);
  assert.match(runtimeWorkflowSource, /Servidor autónomo: API, logging y runtime están incluidos en server[.]jar/);
  assert.match(runtimeWorkflowSource, /vendor\/platform\/web-client\/target/);
  assert.match(runtimeWorkflowSource, /Diagnóstico POS sobre runtime Docker\/Linux \(no bloqueante\)/);
  assert.match(runtimeWorkflowSource, /actions\/setup-java@v6/);
  assert.match(runtimeWorkflowSource, /actions\/upload-artifact@v7/);
  assert.match(runtimeWorkflowSource, /actions\/download-artifact@v8/);
  assert.doesNotMatch(runtimeWorkflowSource, /actions\/setup-java@v4/);
  assert.doesNotMatch(runtimeWorkflowSource, /actions\/(upload|download)-artifact@v4/);
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
  assert.ok(runtimeSmokeSource.includes('EXPECTED_UPSTREAM_MODULES + 8'));
  assert.match(runtimeSmokeSource, /RubrovaCISalesFixture[.]lsf/);
  assert.match(runtimeSmokeSource, /currency\(priceType\('retail'\)\) <- MasterData[.]defaultCurrency\(\)/);
  assert.match(runtimeSmokeSource, /RUBROVA_CI_SALES_LOG_EVIDENCE/);
  assert.match(uiSmokeSource, /UI_RECEIPT_PRODUCT_LINES/);
  assert.match(uiSmokeSource, /UI_RECEIPT_LINE_COUNT/);
  assert.match(runtimeSmokeSource, /RUBROVA_RESILIENCE_LOG_EVIDENCE/);
  assert.match(runtimeSmokeSource, /RUBROVA_REPLENISHMENT_EXPORT_LOG_EVIDENCE/);
  assert.match(runtimeSmokeSource, /RubrovaIntegrationResilience\|RubrovaPaymentTerminals\|RubrovaReplenishmentExport\|RubrovaRetailReturns\|RubrovaRetailRefundLimits\|RubrovaCISalesFixture\|topModule/);
  assert.match(runtimeSmokeSource, /MODULE_PROGRESS_CHANGED_AT/);
  assert.match(runtimeSmokeSource, /Exception while starting logics instance/);
  assert.match(runtimeSmokeSource, /missing \.\+ at/);
  assert.match(runtimeSmokeSource, /se cancela la espera de arranque/);
  assert.match(runtimeSmokeSource, /módulos Rubrova/);
  assert.match(runtimeSmokeSource, /http:\/\/127\.0\.0\.1:8080\/login/);
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
  assert.match(runtimeSmokeSource, /docker-server\/logs/);
  assert.match(runtimeSmokeSource, /compose logs --no-color --tail=180 server/);
  assert.match(runtimeSmokeSource, /tail -n 80/);
  assert.match(runtimeSmokeSource, /successfully started/);
  assert.match(runtimeSmokeSource, /RubrovaPOSLocalization/);
  assert.match(runtimeSmokeSource, /RubrovaIntegrationResilience/);
});


test("la vista previa macOS prepara Chromium y conserva una base sintética para probar el POS", () => {
  assert.match(localPreviewSource, /playwright==1[.]65[.]2/);
  assert.match(localPreviewSource, /parts < \(2, 24, 4\)/);
  assert.match(localPreviewSource, /rubrova-local-preview-.*date \+%Y%m%d%H%M%S/);
  assert.match(localPreviewSource, /playwright install chromium/);
  assert.match(localPreviewSource, /RUBROVA_ALLOW_EXPERIMENTAL_MACOS_AMD64_EMULATION=true/);
  assert.match(localPreviewSource, /RUBROVA_KEEP_RUNTIME_STACK=true/);
  assert.match(localPreviewSource, /RUBROVA_KEEP_RUNTIME_WORK_DIR=true/);
  assert.match(localPreviewSource, /RUBROVA_UI_TEST_LOGIN=true/);
  assert.ok(nativePreviewSource.includes("RubrovaReplenishmentExport, RubrovaRetailReturns, RubrovaRetailRefundLimits;"));
  assert.doesNotMatch(nativePreviewSource, /RubrovaRetailRefundLimits, RubrovaRetailRefundLimits;/);
  assert.match(localPreviewSource, /bash .*test-runtime-smoke[.]sh/);
  assert.match(localPreviewSource, /http:\/\/127[.]0[.]0[.]1:8080\/login/);
});

test("el guard acumulado es visible para el POS sin crear un ciclo con MyCompany", () => {
  assert.match(retailReturnsSource, /^REQUIRE CreditNote, OutgoingPaymentDebt;/m);
  assert.equal((retailReturnsSource.match(/^NAMESPACE /gm) || []).length, 1,
    "Cada módulo LSF debe declarar un único NAMESPACE.");
  assert.ok(!retailReturnsSource.split("\n")[1].split("//")[0].includes("MyCompany"));
  assert.match(retailRefundLimitsSource, /^REQUIRE CreditNote, SessionPayment, IncomingPaymentDebt, RubrovaRetailReturns;/m);
  assert.equal((retailRefundLimitsSource.match(/^NAMESPACE /gm) || []).length, 1,
    "Cada módulo LSF debe declarar un único NAMESPACE.");
  assert.ok(!retailRefundLimitsSource.split("\n")[1].split("//")[0].includes("MyCompany"));
  assert.match(moduleSource, /^REQUIRE MyCompany, RubrovaRetailRefundLimits;$/m);
  assert.match(moduleSource, /PROPERTY\(rubrovaOriginalPaidForReturn\(b, pm\)\)/);
  assert.match(moduleSource, /PROPERTY\(rubrovaRefundRemaining\(b, pm\)\)/);
  assert.doesNotMatch(moduleSource, /invoicePaid\s*\(b,\s*pm\)/);
  assert.match(sourcePatch, /RETURN_PAYMENT_REQUIRE_BEFORE = "REQUIRE PosDashboardReturn, PosDashboardPayment, CreditNote, OutgoingPaymentDone;"/);
  assert.match(sourcePatch, /RETURN_PAYMENT_REQUIRE_AFTER = "REQUIRE PosDashboardReturn, PosDashboardPayment, CreditNote, OutgoingPaymentDone, RubrovaRetailRefundLimits;"/);
  assert.ok(sourcePatch.includes("source = source.replace(RETURN_PAYMENT_REQUIRE_BEFORE, RETURN_PAYMENT_REQUIRE_AFTER, 1)"));
  assert.ok(returnPaymentSource.includes("REQUIRE PosDashboardReturn, PosDashboardPayment, CreditNote, OutgoingPaymentDone;"));
});


test("la extensión superior requiere MyCompany sin copiar sus módulos", () => {
  assert.match(entrypointSource, /^MODULE RubrovaCustom;/m);
  assert.match(entrypointSource, /^REQUIRE MyCompany, RubrovaPOSLocalization, RubrovaIntegrationResilience, RubrovaPaymentTerminals, RubrovaReplenishmentExport, RubrovaRetailReturns, RubrovaRetailRefundLimits;/m);
  assert.match(moduleSource, /^MODULE RubrovaPOSLocalization;/m);
  assert.match(moduleSource, /^REQUIRE MyCompany, RubrovaRetailRefundLimits;/m);
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
  assert.ok(moduleSource.includes("PROPERTY(index(l)) { caption = '{rubrova.pos.line_short}'; charWidth = 3; }"));
  assert.ok(moduleSource.includes("PROPERTY(quantity(l)) { caption = '{rubrova.pos.quantity_short}'; charWidth = 7; }"));
  assert.ok(moduleSource.includes("PROPERTY(discount(l)) { caption = '{rubrova.pos.discount_percent_short}'; charWidth = 7; }"));
  assert.ok(moduleSource.includes("PROPERTY(discountPrice(l)) { caption = '{rubrova.pos.discount_price_short}'; charWidth = 10; }"));
  assert.ok(moduleSource.includes("PROPERTY(available(i, it)) { caption = '{rubrova.pos.available_short}'; charWidth = 8; }"));
  assert.ok(moduleSource.includes("PROPERTY(quantity(i, it)) { caption = '{rubrova.pos.quantity_short}'; charWidth = 7; }"));
  assert.match(moduleSource, /DESIGN posPayment/);
  assert.ok(runtimeSmokeSource.includes("Invoicing.currency(Invoicing.invoiceType('retail')) <- MasterData.defaultCurrency()"));
  assert.match(moduleSource, /Sales[.]currency\(Sales[.]priceType\('retail'\)\) <- defaultCurrency\(\)/);
  assert.match(moduleSource, /Invoicing[.]checkReturnedQuantity\(Invoicing[.]invoiceType\('retail'\)\) <- TRUE/);
  assert.match(nativeSalesFixtureSource, /rubrovaReturnSafetyApi/);
  assert.match(nativeSalesFixtureSource, /retailReturnQuantityGuardEnabled = Invoicing[.]checkReturnedQuantity/);
  assert.match(uiSmokeSource, /verify_return_quantity_guard\(context, url\)/);
  assert.match(uiSmokeSource, /UI_RETURN_QUANTITY_GUARD_ENABLED=true/);
  assert.match(nativeSmokeSource, /UI_RETURN_QUANTITY_GUARD_ENABLED=true/);
  assert.match(moduleSource, /name\(cashPaymentMethod\(\)\) <- 'Efectivo'/);
  assert.match(moduleSource, /name\(paymentMethod\('card'\)\) <- 'Tarjeta'/);
  assert.match(moduleSource, /DESIGN posPaymentReturn/);
  assert.match(moduleSource, /PROPERTY\(rubrovaOriginalPaidForReturn\(b, pm\)\)/);
  assert.match(moduleSource, /PROPERTY\(rubrovaRefundRemaining\(b, pm\)\)/);
  assert.doesNotMatch(moduleSource, /invoicePaid\s*\(b,\s*pm\)/);
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
    "rubrova.pos.refund_by_method", "rubrova.pos.refund_remaining", "rubrova.pos.confirm_return",
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
  assert.equal(entries.get("By_order"), "Por pedido");
  assert.equal(entries.get("Name_full_"), "Nombre completo");
  assert.equal(entries.get("Discount_p"), "Descuento, %");
  assert.equal(entries.get("Date"), "Fecha");
  assert.equal(entries.get("Reference"), "Referencia");
  assert.ok(moduleSource.includes("FOR MasterData.id(MasterData.Individual i) = 'unknown' DO {"));
  assert.ok(!moduleSource.includes("FOR MasterData.Individual i WHERE"));
  assert.ok(!moduleSource.includes("FOR MasterData.Individual i DO {"));
  assert.ok(!moduleSource.includes("IF MasterData.id(i) = 'unknown' THEN"));
  assert.ok(moduleSource.includes("MasterData.lastName(i) <- 'Consumidor final'"));
  assert.equal(entries.get("rubrova.pos.search_price"), "Precio");
  assert.equal(entries.get("rubrova.pos.line_short"), "Nº");
  assert.equal(entries.get("rubrova.pos.quantity_short"), "Cant.");
  assert.equal(entries.get("rubrova.pos.discount_short"), "Desc.");
  assert.equal(entries.get("rubrova.pos.discount_percent_short"), "Desc. %");
  assert.equal(entries.get("rubrova.pos.discount_price_short"), "P. c/desc.");
  assert.equal(entries.get("rubrova.pos.available_short"), "Disp.");
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
    2,
    "Se espera una pasada para vender/cerrar y otra pasada de sólo lectura tras reiniciar."
  );
  assert.equal(
    runtimeSmokeSource.split('RUBROVA_UI_VERIFY_PERSISTED_ONLY="true"').length - 1,
    1,
    "La segunda pasada debe estar limitada a verificar datos persistidos, sin abrir otro turno."
  );
  assert.equal(
    runtimeSmokeSource.split("8/10 Inspeccionando el login y la pantalla autenticada con Chromium").length - 1,
    1,
    "La aceptación visual/venta inicial debe ocurrir una sola vez."
  );
  assert.equal(
    uiSmokeSource.split('click_exact_action(page, "Abrir turno")').length - 1,
    1,
    "El navegador no debe intentar abrir un segundo turno en la comprobación de persistencia."
  );
  assert.equal(
    runtimeSmokeSource.split("4.1/7 El servidor usa directamente mock-provider:").length - 1,
    1,
    "El servidor debe acceder directamente al simulador HTTP dentro de la red interna."
  );
  const timeoutEndpoint = runtimeSmokeSource.split("rubrovaTestHttpTimeout () {")[1]?.split("} @@api;")[0] || "";
  const rateLimitEndpoint = runtimeSmokeSource.split("rubrovaTestHttpRateLimit () {")[1]?.split("} @@api;")[0] || "";
  assert.ok(!timeoutEndpoint.includes("incidentRetryAfterPersisted"), "La persistencia de Retry-After no pertenece al endpoint de timeout.");
  assert.ok(rateLimitEndpoint.includes("incidentRetryAfterPersisted = rubrovaHttp429RetryAfterIncidentCount() = 1"), "El endpoint HTTP 429 debe exponer la comprobación del encabezado persistido.");
  assert.match(runtimeSmokeSource, /mock-integration-provider[.]py/);
  assert.match(runtimeSmokeSource, /rubrova\/mock-provider:6[.]2-/);
  assert.match(runtimeSmokeSource, /FROM python:3[.]13-alpine/);
  assert.match(runtimeSmokeSource, /internal: true/);
  assert.match(runtimeSmokeSource, /RUBROVA_RUNTIME_EXTERNAL_EGRESS=blocked/);
  assert.doesNotMatch(runtimeSmokeSource, /host[.]docker[.]internal:host-gateway/);
  assert.match(runtimeSmokeSource, /MOCK_PROVIDER_URL="http:\/\/mock-provider:\$MOCK_PROVIDER_PORT"/);
  assert.match(runtimeSmokeSource, /mock-provider:[^\n]+within the internal network|4[.]1\/7 El servidor usa directamente mock-provider/);
  assert.doesNotMatch(runtimeSmokeSource, /toxiproxy|TOXIPROXY|18474|rubrova_ci_normal/i);
  assert.doesNotMatch(runtimeSmokeSource, /rubrova_ci_timeout|drop-response|MOCK_PROVIDER_TIMEOUT_URL/);
  assert.match(runtimeSmokeSource, /\/slow\?delay=5/);
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
  assert.ok(runtimeSmokeSource.includes("sessionStatus = CASE WHEN Retail.opened(rubrovaCITestSession()) THEN 'OPEN' ELSE 'CLOSED'"));
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
  assert.ok(uiSmokeSource.includes('closed_session_payload.get("sessionStatus") == "CLOSED"'));
  assert.ok(uiSmokeSource.includes('closed_session_payload.get("sessionStatus") != "CLOSED"'));
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

test("el cliente GWT compila la variante española y expone Sí/No", () => {
  assert.ok(gwtModuleSource.includes('<extend-property name="locale" values="ru,en,be,uk,es"/>'));
  assert.ok(gwtModuleSource.includes('<set-property name="locale" value="ru,en,be,uk,es"/>'));
  const messages = parseProperties(spanishGwtMessagesSource);
  assert.equal(messages.get("yes"), "Sí");
  assert.equal(messages.get("no"), "No");
  assert.ok(sourcePatch.includes("GWT_MESSAGES_SOURCE"));
  assert.ok(sourcePatch.includes("GWT_MESSAGES_TARGET"));
});

test("los botones de confirmación del cliente GWT están localizados al español", () => {
  const entries = parseProperties(spanishGwtMessagesSource);
  assert.equal(entries.get("yes"), "Sí");
  assert.equal(entries.get("no"), "No");
  assert.equal(entries.get("ok"), "Aceptar");
  assert.equal(entries.get("cancel"), "Cancelar");
  for (const [key, value] of [
    ["formGridExport", "Exportar"],
    ["formGridPreferences", "Preferencias de la grilla"],
    ["busyDialogLoading", "Cargando"],
    ["formFilterAddCondition", "Agregar condición"],
    ["rmiConnectionLost", "Conexión perdida"]
  ]) assert.equal(entries.get(key), value, "Traducción GWT incorrecta: " + key);
  assert.deepEqual(
    parseProperties(spanishGwtMessagesVendor),
    entries,
    "El bundle español generado dentro del cliente GWT debe coincidir con la fuente Rubrova."
  );
  assert.ok(sourcePatch.includes("GWT_MESSAGES_SOURCE"));
  assert.ok(sourcePatch.includes("GWT_MESSAGES_TARGET"));
});

test("los mensajes críticos del motor servidor están localizados al español", () => {
  const entries = parseProperties(spanishServerMessagesSource);
  assert.deepEqual(
    parseProperties(spanishServerMessagesVendor),
    entries,
    "El bundle español generado para el servidor debe coincidir con la fuente Rubrova."
  );
  assert.equal(entries.get("form.instance.do.you.really.want.to.take.action"), "¿Confirma que desea ejecutar la acción");
  assert.equal(entries.get("form.instance.do.you.really.want.to.edit.property"), "¿Confirma que desea editar la propiedad");
  assert.equal(entries.get("form.instance.changes.saved"), "Los cambios se guardaron correctamente...");
  assert.equal(entries.get("form.do.you.really.want.to.undo.changes"), "¿Desea deshacer los cambios?");
  for (const [key, value] of [
    ["logics.delete", "Eliminar"],
    ["navigator.account", "Cuenta"],
    ["navigator.administration", "Administración"],
    ["navigator.pin.mode", "Fijar paneles de navegación"],
    ["authentication.color.theme", "Tema de color"],
    ["reflection.find.navigator", "Buscar"],
    ["service.setting", "Configuración"],
    ["master.data.master.data", "Datos maestros"],
    ["system.group.base", "Atributos"],
    ["system.events.design", "Diseño"],
    ["system.events.auto.mode", "Tema automático"],
    ["system.events.navigator.pin.navbar", "Fijar barra de navegación"],
    ["messenger.chat", "Mensajes"]
  ]) assert.equal(entries.get(key), value, "Traducción incorrecta: " + key);
  assert.ok(sourcePatch.includes("SERVER_MESSAGES_SOURCE"));
  assert.ok(sourcePatch.includes("SERVER_MESSAGES_TARGET"));
});

test("la pantalla de acceso y los errores web usan el bundle español ServerMessages", () => {
  const entries = parseProperties(spanishWebMessagesSource);
  assert.deepEqual(
    parseProperties(spanishWebMessagesVendor),
    entries,
    "El bundle español incluido en el cliente web debe coincidir con su fuente Rubrova."
  );
  for (const [key, value] of [
    ["sign.in", "Ingresar"],
    ["sign.in.title", "Ingresar"],
    ["login", "Usuario"],
    ["password", "Contraseña"],
    ["password.forgot", "¿Olvidaste tu contraseña?"],
    ["register", "Registrarse"],
    ["run.desktop.client", "Abrir cliente de escritorio"],
    ["app.server.unavailable", "El servidor de aplicación no está disponible"],
    ["internal.server.error", "Error interno del servidor"]
  ]) assert.equal(entries.get(key), value, "Mensaje web sin traducción: " + key);
  assert.ok(serverMessagesClass.includes('LocalizeUtils.getBundle("ServerMessages", locale)'));
  assert.ok(sourcePatch.includes("SERVER_TEXT_MESSAGES_SOURCE"));
  assert.ok(sourcePatch.includes("SERVER_TEXT_MESSAGES_TARGET"));
});

test("el POS separa la cuenta central del cajón y aísla las cuentas del fixture de reintegros", () => {
  assert.ok(paymentMethodSource.includes("CONSTRAINT account(Pos p) = cashAccount(p)"));
  assert.ok(paymentMethodSource.includes("La cuenta central de caja no puede ser la misma que la cuenta de efectivo"));
  assert.ok(paymentMethodSource.includes("cashBalance 'Cash at the checkout' (Pos p) = balance(cashAccount(p));"));
  assert.ok(sourcePatch.includes("CASH_ACCOUNT_REQUIRED_MARKER"));
  assert.ok(sourcePatch.includes("CASH_ACCOUNT_ANCHOR"));
  assert.ok(runtimeSmokeSource.includes("centralCashAccountName = Retail.nameAccount"));
  assert.ok(uiSmokeSource.includes("UI_POS_CASH_ACCOUNTS_DISTINCT=true"));
  assert.ok(runtimeWorkflowSource.includes("CONSTRAINT account(Pos p) = cashAccount(p)"));
  const bankScopeStart = nativeRetailFixtureSource.indexOf("NEW bankCI = Bank {");
  const cardAccountScopeStart = nativeRetailFixtureSource.indexOf("NEW cardAccountCI = BankAccount {");
  const cashRegisterScopeStart = nativeRetailFixtureSource.indexOf("NEW cashRegisterCI = Pos {");
  const refundCentralScopeStart = nativeRetailFixtureSource.indexOf("NEW refundCentralAccountCI = CashAccount {");
  const refundCashScopeStart = nativeRetailFixtureSource.indexOf("NEW refundCashAccountCI = CashAccount {");
  const refundCardScopeStart = nativeRetailFixtureSource.indexOf("NEW refundCardAccountCI = BankAccount {");
  const refundRegisterScopeStart = nativeRetailFixtureSource.indexOf("NEW refundCashRegisterCI = Pos {");
  assert.ok(
    bankScopeStart >= 0 && cardAccountScopeStart > bankScopeStart &&
    cashRegisterScopeStart > cardAccountScopeStart && refundCentralScopeStart > cashRegisterScopeStart &&
    refundCashScopeStart > refundCentralScopeStart && refundCardScopeStart > refundCashScopeStart &&
    refundRegisterScopeStart > refundCardScopeStart,
    "La caja principal debe crearse primero y la cadena de reintegros después, manteniendo los ámbitos anidados."
  );
  const bankBodyDepth = braceDepthAt(nativeRetailFixtureSource, bankScopeStart) + 1;
  for (const [declaration, expectedDepth] of [
    ["NEW cardAccountCI = BankAccount {", bankBodyDepth],
    ["NEW cashRegisterCI = Pos {", bankBodyDepth + 1],
    ["NEW refundCentralAccountCI = CashAccount {", bankBodyDepth],
    ["NEW refundCashAccountCI = CashAccount {", bankBodyDepth + 1],
    ["NEW refundCardAccountCI = BankAccount {", bankBodyDepth + 2],
    ["NEW refundCashRegisterCI = Pos {", bankBodyDepth + 3]
  ]) {
    const declarationStart = nativeRetailFixtureSource.indexOf(declaration);
    assert.ok(declarationStart >= 0, "Falta " + declaration);
    assert.equal(
      braceDepthAt(nativeRetailFixtureSource, declarationStart),
      expectedDepth,
      declaration + " debe quedar anidada en el NEW que declara los parámetros que consume."
    );
  }
  assert.ok(nativeRetailFixtureSource.includes("account(refundCashRegisterCI) <- refundCentralAccountCI;"));
  assert.ok(nativeRetailFixtureSource.includes("account(refundCashRegisterCI, PaymentMethod pm) <- refundCashAccountCI WHERE pm = cashPaymentMethod();"));
  assert.ok(nativeRetailFixtureSource.includes("account(refundCashRegisterCI, PaymentMethod pm) <- refundCardAccountCI WHERE id(pm) = 'card';"));
  assert.ok(!nativeRetailFixtureSource.includes("account(refundCashRegisterCI, PaymentMethod pm) <- cashAccountCI"));
  assert.ok(!nativeRetailFixtureSource.includes("account(refundCashRegisterCI, PaymentMethod pm) <- cardAccountCI"));
});

test("MyCompany guarda cambios pendientes antes de abrir NEWSESSION en acciones documentales", () => {
  const expectedPaths = [
    "vendor/mycompany/src/main/lsfusion/crm/leads/Lead.lsf",
    "vendor/mycompany/src/main/lsfusion/fleet/vehicles/service/VehicleService.lsf",
    "vendor/mycompany/src/main/lsfusion/inventory/receipts/Receipt.lsf",
    "vendor/mycompany/src/main/lsfusion/inventory/receipts/ReceiptScrap.lsf",
    "vendor/mycompany/src/main/lsfusion/inventory/receipts/shipment/ReceiptShipment.lsf",
    "vendor/mycompany/src/main/lsfusion/inventory/scraps/Scrap.lsf",
    "vendor/mycompany/src/main/lsfusion/inventory/shipments/Shipment.lsf",
    "vendor/mycompany/src/main/lsfusion/inventory/shipments/receipt/ShipmentReceipt.lsf",
    "vendor/mycompany/src/main/lsfusion/invoicing/bills/Bill.lsf",
    "vendor/mycompany/src/main/lsfusion/invoicing/invoices/Invoice.lsf",
    "vendor/mycompany/src/main/lsfusion/manufacturing/bom/Bom.lsf",
    "vendor/mycompany/src/main/lsfusion/manufacturing/orders/ManufacturingOrder.lsf",
    "vendor/mycompany/src/main/lsfusion/manufacturing/orders/scrap/ManufacturingOrderScrap.lsf",
    "vendor/mycompany/src/main/lsfusion/masterdata/items/products/Product.lsf",
    "vendor/mycompany/src/main/lsfusion/masterdata/items/services/ServiceP.lsf",
    "vendor/mycompany/src/main/lsfusion/projectManagement/timeEntries/TimeEntry.lsf",
    "vendor/mycompany/src/main/lsfusion/purchase/orders/PurchaseOrder.lsf",
    "vendor/mycompany/src/main/lsfusion/purchase/pricelists/PurchasePricelist.lsf",
    "vendor/mycompany/src/main/lsfusion/region/pl/invoicing/ksef/invoices/KSeFInvoiceSend.lsf",
    "vendor/mycompany/src/main/lsfusion/sales/orders/SalesOrder.lsf",
    "vendor/mycompany/src/main/lsfusion/sales/pricelists/SalesPricelist.lsf"
  ];
  assert.equal(expectedPaths.length, 21);
  assert.ok(sourcePatch.includes("NEWSESSION_GUARD_TARGETS"));
  assert.ok(sourcePatch.includes("def apply_newsession_guards()"));
  assert.ok(sourcePatch.includes("remainder.startswith(expected_guard)"));
  for (const path of expectedPaths) assert.ok(sourcePatch.includes(path), "Falta el backport: " + path);
  assert.ok(sourcePatch.includes("9dca1499bd4e2615d34983fe77c2927560fd5f9b"));
});

test("las búsquedas de cuenta de caja restringen la clase CashAccount", () => {
  assert.ok(cashAccountSource.includes("WHERE a IS CashAccount AND holder(a) = p IF countCashAccount(p) = 1"));
  assert.ok(cashAccountSource.includes("WHERE a IS CashAccount AND holder(a) = legalEntity(e) AND responsible(a) = e"));
  assert.ok(sourcePatch.includes("CASH_ACCOUNT_QUERY_REPLACEMENTS"));
  assert.ok(sourcePatch.includes("def apply_cash_account_query_filters()"));
});

test("la búsqueda de cuenta bancaria restringe la clase BankAccount", () => {
  assert.ok(bankAccountSource.includes("WHERE a IS BankAccount AND holder(a) = p IF countBankAccount(p) = 1;"));
  assert.ok(sourcePatch.includes("BANK_ACCOUNT_QUERY_REPLACEMENTS"));
  assert.ok(sourcePatch.includes("a IS BankAccount AND holder(a) = p IF countBankAccount(p) = 1;"));
  assert.ok(sourcePatch.includes("def apply_bank_account_query_filters()"));
  assert.ok(sourcePatch.includes("if not apply_bank_account_query_filters():"));
});

test("el historial de facturas y compras registra los cambios de impuestos por línea", () => {
  assert.ok(billSource.includes("@defineDocHistoryLineProperty(bill, BillLine, untaxedAmount, '{Amount}', nameItem);"));
  assert.ok(invoiceSource.includes("@defineDocHistoryLineProperty(invoice, InvoiceLine, untaxedAmount, '{Amount}', nameItem);"));
  assert.ok(sourcePatch.includes("TAX_HISTORY_TARGETS"));
  assert.ok(sourcePatch.includes("@defineDocHistoryLineProperty(bill, BillLine, taxes, 'Taxes', nameItem);"));
  assert.ok(sourcePatch.includes("@defineDocHistoryLineProperty(invoice, InvoiceLine, taxes, 'Taxes', nameItem);"));
  assert.ok(sourcePatch.includes("def apply_tax_history_line_tracking()"));
  assert.ok(sourcePatch.includes("if not apply_tax_history_line_tracking():"));
});

test("el navegador de atributos usa el caption español y Numerators se traduce desde el motor", () => {
  assert.ok(itemAttributeSource.includes("FORM attributes '{Attributes}'"));
  assert.ok(!itemAttributeSource.includes("FORM attributes 'Attributes'"));
  assert.ok(sourcePatch.includes("ITEM_ATTRIBUTE_NAVIGATION_TARGET"));
  assert.ok(sourcePatch.includes("def apply_item_attribute_navigation_caption()"));
  assert.ok(sourcePatch.includes("if not apply_item_attribute_navigation_caption():"));
  assert.equal(parseProperties(bundle).get("Attributes"), "Atributos");
  const serverEntries = parseProperties(spanishServerMessagesSource);
  assert.equal(serverEntries.get("numerator.numerators"), "Numeradores");
  assert.equal(serverEntries.get("numerator.numerator"), "Numerador");
});

test("los movimientos de caja usan la clave española de fecha en lugar de un caption literal", () => {
  assert.ok(incomingPaymentSource.includes("dateTime '{Date}' = DATA DATETIME (IncomingPayment) NONULL IN id;"));
  assert.ok(outgoingPaymentSource.includes("dateTime '{Date}' = DATA DATETIME (OutgoingPayment) NONULL IN id;"));
  assert.ok(!incomingPaymentSource.includes("dateTime 'Date' = DATA DATETIME"));
  assert.ok(!outgoingPaymentSource.includes("dateTime 'Date' = DATA DATETIME"));
  assert.ok(sourcePatch.includes("CASH_MOVEMENT_DATE_CAPTION_TARGETS"));
  assert.ok(sourcePatch.includes("def apply_cash_movement_date_captions()"));
  assert.ok(sourcePatch.includes("if not apply_cash_movement_date_captions():"));
  assert.ok(bundle.includes("Date=Fecha"));
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


test("la API nativa de reposición sólo exporta hechos MyCompany y conserva magnitudes distintas", () => {
  assert.match(replenishmentExportSource, /^MODULE RubrovaReplenishmentExport;/m);
  assert.match(replenishmentExportSource, /^REQUIRE MyCompany;/m);
  assert.match(replenishmentExportSource, /rubrovaExportReplenishmentSource/);
  assert.match(replenishmentExportSource, /} @@api;/);
  const replenishmentApiActions = [
    ...replenishmentExportSource.matchAll(/^\w+\s+'[^']+'\s+\(\)\s*\{([\s\S]*?)^\}\s*@@api;/gm)
  ];
  assert.equal(
    replenishmentApiActions.length,
    4,
    "La exportación y las tres sondas deben seguir siendo endpoints autenticados independientes."
  );
  for (const [index, action] of replenishmentApiActions.entries()) {
    assert.match(
      action[1],
      /^\s*EXPORT JSON FROM/m,
      "El endpoint MyCompany " + (index + 1) + " debe usar EXPORT JSON FROM compatible con lsFusion 6.2."
    );
    assert.doesNotMatch(
      action[1],
      /^\s*RETURN JSON FROM/m,
      "RETURN JSON FROM no es sintaxis del RETURN sin expresión de lsFusion 6.2."
    );
  }
  for (const field of [
    "Inventory.onHand(l, p)",
    "Inventory.available(l, p)",
    "onHandNative = Inventory.onHand(l, p)",
    "availableNative = Inventory.available(l, p)",
    "OVERRIDE Inventory.available(l, p)",
    "OVERRIDE Inventory.planned(l, p)",
    "Inventory.planned(l, p)",
    "Sales.toShip(ol)",
    "Sales.order(Sales.OrderLine ol)",
    "Sales.index(ol)",
    "Sales.shippedProduct(ol)",
    "Sales.scheduledDateTime(Sales.order(ol))",
    "Sales.index(ol)",
    "Inventory.index(Inventory.line(rr))",
    "Purchase.index(Purchase.orderLine(Inventory.line(rr)))",
    "sourceLineId = (CONCAT",
    "lineId = (CONCAT",
    "Inventory.scheduledDateTime(Inventory.receipt(Inventory.line(rr)))",
    "Inventory.expected(l, p)",
    "Inventory.reserved(l, p)",
    "Inventory.ShipmentLine sl",
    "Sales.orderLine(sl)",
    "Inventory.reserved(sl)",
    "Inventory.ledgerReserved(sl)",
    "Inventory.toReserve(Inventory.shipment(sl))",
    "Inventory.ReceiptResLedger",
    "Inventory.increaseAvailableStock",
    "expectedReservationSigned = Inventory.reserved(rr)",
    "Inventory.ready(Inventory.receipt(Inventory.line(rr)))",
    "NOT Inventory.done(Inventory.receipt(Inventory.line(rr)))",
    "NOT Inventory.canceled(Inventory.receipt(Inventory.line(rr)))"
  ]) {
    assert.ok(replenishmentExportSource.includes(field), "La extracción debe incluir " + field);
  }
  assert.doesNotMatch(replenishmentExportSource, /fillAuto\s*\(/);
  assert.doesNotMatch(replenishmentExportSource, /NEW\s+\w+\s*=|DELETE\s+/);
  assert.match(replenishmentExportSource, /snapshotType = 'mycompany-replenishment-source-export'/);
  assert.match(replenishmentExportSource, /quantityPrecision = 3/);
  assert.match(replenishmentExportSource, /readOnly = TRUE/);
  assert.match(replenishmentExportSource, /asOfDateTime = currentDateTime\(\)/);
  assert.match(replenishmentExportSource, /emptyAggregatePolicy =/);
  assert.match(replenishmentExportSource, /emptyCollectionPolicy = 'collection counts are authoritative/);
  for (const countField of ["inventoryCount", "outgoingCommitmentsCount", "outgoingReservationsCount", "receiptsCount"]) {
    assert.ok(
      replenishmentExportSource.includes(countField + " = (OVERRIDE"),
      countField + " debe usar un conteo agregado con fallback explícito."
    );
    assert.ok(
      replenishmentExportSource.split(countField + " =").length - 1 >= 2,
      countField + " debe existir tanto en la exportación completa como en su sonda aislada."
    );
  }
  assert.ok(uiSmokeSource.includes("def _native_collection("));
  assert.ok(uiSmokeSource.includes("expected_count == 0"));
  assert.ok(uiSmokeSource.includes("outgoingReservationsCount"));
  assert.ok(uiSmokeSource.includes("reserveEligible"));
  assert.ok(uiSmokeSource.includes("reservedQuantityNative"));
  assert.ok(uiSmokeSource.includes("ledgerReservedQuantityNative"));
  assert.ok(uiSmokeSource.includes("Emit the exact source facts before semantic validation"));
  assert.ok(uiSmokeSource.includes("len(rows) != expected_count"));
  assert.ok(uiSmokeSource.includes("UI_REPLENISHMENT_PROBE_OUTGOING_COMMITMENTS_ROWS_JSON="));
  assert.ok(uiSmokeSource.includes("reserved > commitments_by_id[line_id] + 0.001"));
  const outgoingExportQuery = replenishmentExportSource.split("outgoingCommitments = (JSON FROM")[1]?.split("outgoingReservations = (JSON FROM")[0] ?? "";
  assert.ok(outgoingExportQuery.includes("openQuantity = Sales.toShip(ol)"));
  assert.doesNotMatch(outgoingExportQuery, /effectiveReserved|Sales\.reserved\(ol\)/,
    "La fila de Sales.OrderLine no debe calcular reservas agregadas dentro de JSON FROM.");
  const outgoingExportReservationsQuery = replenishmentExportSource.split("outgoingReservations = (JSON FROM")[1]?.split("        receipts = (JSON FROM")[0] ?? "";
  for (const field of [
    "Sales.orderLine(Inventory.ShipmentLine sl)",
    "Inventory.reserved(sl)",
    "Inventory.ledgerReserved(sl)",
    "Inventory.toReserve(Inventory.shipment(sl))",
    "reserveEligible = Inventory.toReserve(Inventory.shipment(sl))",
    "shipmentLineId = (CONCAT"
  ]) {
    assert.ok(outgoingExportReservationsQuery.includes(field), "La API debe exportar el hecho nativo " + field);
  }
  assert.doesNotMatch(outgoingExportReservationsQuery, /GROUP SUM|Sales\.reserved\(|Inventory\.lineReserved\(sl\)/,
    "La colección de reservas expone filas nativas sin agregación correlacionada.");
  const outgoingProbeQuery = replenishmentExportSource.split("rubrovaProbeOutgoingCommitments")[1]?.split("rubrovaProbeReceipts")[0] ?? "";
  assert.ok(outgoingProbeQuery.includes("outgoingReservations = (JSON FROM"));
  assert.ok(outgoingProbeQuery.includes("Inventory.reserved(sl)"));
  assert.ok(outgoingProbeQuery.includes("Inventory.ledgerReserved(sl)"));
  assert.doesNotMatch(outgoingProbeQuery, /effectiveReserved =|Sales\.reserved\(ol\)/);
  assert.equal(
    (replenishmentExportSource.match(/outgoingReservations = \(JSON FROM/g) ?? []).length,
    2,
    "Exportación y sonda deben incluir ambas las líneas nativas de reserva."
  );
  assert.equal(
    (outgoingExportQuery.match(/Sales\.OrderLine ol/g) ?? []).length,
    1,
    "Sales.OrderLine debe declararse una sola vez en la consulta de compromisos; el resto de campos reutiliza ol."
  );
  assert.ok(
    !replenishmentExportSource.includes("BPSTRING[10]"),
    "Los índices de línea deben conservar su fuente de conjunto y no quedar ocultos tras BPSTRING."
  );
  assert.match(replenishmentExportSource, /reservedQuantityNative = \(OVERRIDE Inventory\.reserved\(sl\), 0\)/);
  assert.match(replenishmentExportSource, /ledgerReservedQuantityNative = \(OVERRIDE Inventory\.ledgerReserved\(sl\), 0\)/);
  assert.doesNotMatch(replenishmentExportSource, /Inventory\.lineReserved\(sl\)/);
  assert.match(
    nativeReplenishmentFixtureSource,
    /NEWSESSION\s*\{\s*Inventory\.precheckAvailability\(rubrovaCIOutgoingShipment\(\)\);\s*APPLY;\s*\}/s,
    "El fixture debe persistir el precheck nativo en una sesión independiente antes de validar la exportación."
  );
  assert.match(replenishmentExportSource, /Inventory\.ready\(Inventory\.receipt\(Inventory\.line\(rr\)\)\)/);
  assert.match(replenishmentExportSource, /NOT Inventory\.done\(Inventory\.receipt\(Inventory\.line\(rr\)\)\)/);
  assert.match(replenishmentExportSource, /NOT Inventory\.canceled\(Inventory\.receipt\(Inventory\.line\(rr\)\)\)/);
  assert.doesNotMatch(replenishmentExportSource, /<>/);
  assert.equal(
    (replenishmentExportSource.match(/(?:sourceLineId|lineId|purchaseOrderLineId) = \(CONCAT /g) ?? []).length,
    8,
    "Todos los identificadores compuestos deben agrupar CONCAT dentro de JSON FROM para conservar los límites de columnas."
  );
  assert.doesNotMatch(
    replenishmentExportSource,
    /(?:sourceLineId|lineId|purchaseOrderLineId) = CONCAT\b/,
    "No se permite CONCAT sin paréntesis en columnas de JSON FROM."
  );
  assert.doesNotMatch(replenishmentExportSource, /(?:Sales|Purchase)\.id\(/);
  assert.doesNotMatch(replenishmentExportSource, /Inventory\.id\(Inventory\.line\(/);
  assert.doesNotMatch(replenishmentExportSource, /LONG\((?:ol|Sales\.order|Inventory\.line|Inventory\.receipt|Purchase\.order|Purchase\.orderLine)/);
  assert.match(replenishmentExportSource, /outgoingIdentity = 'Sales\.number\(Order\) \+ Sales\.index\(OrderLine\)'/);
  assert.match(replenishmentExportSource, /incomingIdentity = 'Receipt\.number \+ ReceiptLine\.index'/);
  assert.match(replenishmentExportSource, /expectedReservationSigned = Inventory\.reserved\(rr\)/);
  assert.match(replenishmentExportSource, /Inventory\.expected\(l, p\) != 0/);
  assert.match(uiSmokeSource, /verify_replenishment_source_export\(context, url\)/);
  for (const probe of [
    "rubrovaProbeInventory",
    "rubrovaProbeOutgoingCommitments",
    "rubrovaProbeReceipts"
  ]) {
    assert.ok(replenishmentExportSource.includes(probe), "Falta la sonda de diagnóstico " + probe);
    assert.ok(uiSmokeSource.includes(probe), "El smoke debe ejecutar la sonda " + probe);
  }
  assert.ok(uiSmokeSource.includes("probe_replenishment_source_sections(context, url)"));
  assert.ok(uiSmokeSource.includes("UI_REPLENISHMENT_CI_RESERVATION_DIAGNOSTICS="));
  assert.ok(uiSmokeSource.includes("UI_REPLENISHMENT_SOURCE_EXPORT_OUTGOING_ROWS="));
  for (const fragment of [
    "outgoingLinkedShipmentLineCount",
    "outgoingLinkedReservedQuantity",
    "outgoingLinkedPositiveReservedQuantity",
    "outgoingLinkedReservableReservedQuantity",
    "outgoingLinkedEffectiveReservedQuantity",
    "outgoingNativeSalesReservedQuantity",
    "outgoingNativeLedgerReservedQuantity",
    "linkedToFixtureOrder"
  ]) {
    assert.ok(!replenishmentExportSource.includes(fragment),
      "Los diagnósticos deben quedar aislados en el fixture temporal de CI.");
    assert.ok(read("scripts/platform/fixtures/RubrovaCIReplenishmentFixture.lsf").includes(fragment),
      "Falta evidencia temporal del vínculo de reserva: " + fragment);
  }
  assert.match(uiSmokeSource, /UI_REPLENISHMENT_SOURCE_EXPORT_VERIFIED=true/);
});

test("el puente nativo bloquea snapshots cuando las magnitudes MyCompany no concilian", () => {
  for (const fragment of [
    "from decimal import Decimal",
    "def _milli(",
    "if available != on_hand - planned:",
    "plannedNetReservationMilli",
    "expectedInboundMilli",
    "outgoing_reservations",
    "receipt_quantities",
    "increaseAvailableStock=true",
    "Falta una política de planificación explícita",
    "adapt_snapshot(snapshot)"
  ]) {
    assert.ok(replenishmentBridgeSource.includes(fragment), "El puente debe validar " + fragment);
  }
  for (const forbidden of ["psycopg", "psycopg2", "sqlalchemy", "requests.", "urllib."]) {
    assert.equal(replenishmentBridgeSource.includes(forbidden), false, "El puente no debe conectarse directamente a bases o servicios externos.");
  }
  assert.ok(replenishmentBridgeTestsSource.includes("test_unmodeled_planned_reservations_block_planning_even_when_available_matches"));
  assert.ok(replenishmentBridgeTestsSource.includes("test_unrepresented_negative_reservations_block_planning"));
  assert.ok(replenishmentBridgeTestsSource.includes("test_quantities_with_more_than_three_decimals_are_rejected_not_rounded"));
  assert.ok(
    uiSmokeSource.includes("\"outgoingEffectiveReservation\": \"SUM((reservedQuantityNative - ledgerReservedQuantityNative) > 0 where reserveEligible = true, grouped by sourceLineId)\","),
    "El inspector debe validar la agregación de hechos ShipmentLine por sourceLineId."
  );
  assert.ok(uiSmokeSource.includes("def _outgoing_reservation_totals("));
  assert.ok(uiSmokeSource.includes("UI_REPLENISHMENT_SOURCE_EXPORT_OUTGOING_EFFECTIVE_TOTALS="));
  assert.equal(nativeReplenishmentFixture.snapshotType, "mycompany-replenishment-source-export");
  assert.equal(nativeReplenishmentFixture.schemaVersion, 2);
  assert.equal(
    nativeReplenishmentFixture.sourceSemantics.outgoingEffectiveReservation,
    "SUM((reservedQuantityNative - ledgerReservedQuantityNative) > 0 where reserveEligible = true, grouped by sourceLineId)"
  );
  assert.ok(
    replenishmentBridgeSource.includes("SUM((reservedQuantityNative - ledgerReservedQuantityNative) > 0 where reserveEligible = true, grouped by sourceLineId)"),
    "El puente debe agregar hechos ShipmentLine por sourceLineId con el filtro reserveEligible."
  );
  assert.equal(nativeReplenishmentFixture.readOnly, true);
  assert.ok(nativeReplenishmentFixture.inventory.length > 0);
  assert.equal(replenishmentPolicyFixture.schemaVersion, 1);
  assert.equal(replenishmentPolicyFixture.policies.length, nativeReplenishmentFixture.inventory.length);
});

test("el modelo de terminales se carga desde el punto de entrada y el lock", () => {
  assert.ok(entrypointSource.includes("RubrovaPaymentTerminals"));
  assert.ok(entrypointSource.includes("RubrovaReplenishmentExport"));
  assert.ok(entrypointSource.includes("RubrovaRetailReturns"));
  const terminalModule = lock.extension.modules.find((item) => item.name === "RubrovaPaymentTerminals");
  assert.ok(terminalModule, "El módulo debe estar incluido en el lock reproducible.");
  const customModule = lock.extension.modules.find((item) => item.name === "RubrovaCustom");
  assert.ok(customModule.requires.includes("RubrovaIntegrationResilience"));
  assert.ok(customModule.requires.includes("RubrovaPaymentTerminals"));
  const localizationModule = lock.extension.modules.find((item) => item.name === "RubrovaPOSLocalization");
   assert.ok(localizationModule, "La localización debe estar incluida en el lock reproducible.");
   assert.deepEqual(localizationModule.requires, ["MyCompany", "RubrovaRetailRefundLimits"]);
   const retailReturnsModule = lock.extension.modules.find((item) => item.name === "RubrovaRetailReturns");
  const retailRefundLimitsModule = lock.extension.modules.find((item) => item.name === "RubrovaRetailRefundLimits");
  assert.ok(retailReturnsModule, "El cálculo del remanente de devoluciones debe estar en el lock reproducible.");
  assert.deepEqual(retailReturnsModule.requires, ["CreditNote", "OutgoingPaymentDebt"]);
  assert.ok(customModule.requires.includes("RubrovaRetailReturns"));
  assert.ok(retailRefundLimitsModule, "El límite acumulado debe estar incluido en el lock reproducible.");
  assert.deepEqual(retailRefundLimitsModule.requires, ["CreditNote", "SessionPayment", "IncomingPaymentDebt", "RubrovaRetailReturns"]);
  assert.ok(customModule.requires.includes("RubrovaRetailRefundLimits"));
  const replenishmentModule = lock.extension.modules.find((item) => item.name === "RubrovaReplenishmentExport");
  assert.ok(replenishmentModule, "La exportación nativa debe estar incluida en el lock reproducible.");
  assert.ok(customModule.requires.includes("RubrovaReplenishmentExport"));
  assert.deepEqual(terminalModule.requires, ["MyCompany"]);
  assert.doesNotMatch(paymentTerminalSource, /rubrovaHttpGet|rubrovaRecordIntegrationIncident/);
  for (const entity of [
    "PaymentProviderAccount",
    "PaymentTerminal",
    "PaymentTerminalAssignment",
    "PaymentTerminalIntent",
    "PaymentTerminalAttempt",
    "PaymentProviderEvent",
    "PaymentRefund",
    "PaymentSettlement",
    "PaymentSettlementLine"
  ]) {
    assert.ok(paymentTerminalSource.includes("CLASS " + entity), "Falta entidad " + entity);
  }
  assert.ok(paymentTerminalSource.includes("credentialReference"));
  assert.ok(paymentTerminalSource.includes("attemptIdempotencyKey"));
  assert.ok(paymentTerminalSource.includes("intentIdempotencyKey"));
  assert.ok(paymentTerminalSource.includes("providerEventKey"));
  assert.ok(paymentTerminalSource.includes("refundIdempotencyKey"));
  assert.ok(paymentTerminalSource.includes("settlementLineIncomingPayment"));
  assert.ok(paymentTerminalSource.includes("attemptNeedsReconciliation"));
  assert.ok(paymentTerminalSource.includes("providerEventSignatureVerified"));
  assert.ok(paymentTerminalSource.includes("settlementNetAmount"));
  assert.match(paymentTerminalSource, /NEW FOLDER paymentConfiguration 'Configuración de pagos'/);
  assert.match(paymentTerminalSource, /NEW FOLDER paymentOperations 'Operaciones de pago'/);
  assert.doesNotMatch(paymentTerminalSource, /^\\s*(settings|operations)\\s*\\{/m);

});

test("el módulo de terminales no contiene credenciales ni datos sensibles de tarjeta", () => {
  assert.ok(paymentTerminalSource.includes("credentialReference"));
  assert.ok(paymentTerminalSource.includes("Deliberadamente no existe una columna para guardar el cuerpo HTTP completo."));
  assert.ok(!paymentTerminalSource.includes("cardNumber"));
  assert.ok(!paymentTerminalSource.includes("cardholderData"));
  assert.ok(!paymentTerminalSource.includes("trackData"));
  assert.ok(!paymentTerminalSource.includes("rawPayload"));
});

test("la configuración de terminales se despliega en todas las rutas de ejecución", () => {
  assert.ok(read("scripts/platform/deploy-mycompany-6.2.sh").includes("RubrovaPaymentTerminals.lsf"));
  assert.ok(read("scripts/platform/deploy-mycompany-6.2.sh").includes("RubrovaReplenishmentExport.lsf"));
  assert.ok(read("scripts/platform/deploy-mycompany-6.2.sh").includes("RubrovaRetailReturns.lsf"));
  assert.ok(read("scripts/platform/deploy-mycompany-6.2.sh").includes("RubrovaRetailRefundLimits.lsf"));
  assert.ok(read("scripts/platform/deploy-mycompany-6.2.ps1").includes("RubrovaPaymentTerminals.lsf"));
  assert.ok(read("scripts/platform/deploy-mycompany-6.2.ps1").includes("RubrovaReplenishmentExport.lsf"));
  assert.ok(read("scripts/platform/deploy-mycompany-6.2.ps1").includes("RubrovaRetailReturns.lsf"));
  assert.ok(read("scripts/platform/deploy-mycompany-6.2.ps1").includes("RubrovaRetailRefundLimits.lsf"));
  assert.ok(nativePreviewSource.includes("RubrovaPaymentTerminals.lsf"));
  assert.ok(nativePreviewSource.includes("RubrovaReplenishmentExport.lsf"));
  assert.ok(nativePreviewSource.includes("RubrovaRetailReturns.lsf"));
  assert.ok(nativePreviewSource.includes("RubrovaRetailRefundLimits.lsf"));
  assert.ok(runtimeSmokeSource.includes("RubrovaPaymentTerminals.lsf"));
  assert.ok(runtimeSmokeSource.includes("RubrovaReplenishmentExport.lsf"));
  assert.ok(runtimeSmokeSource.includes("RubrovaRetailReturns.lsf"));
  assert.ok(runtimeSmokeSource.includes("RubrovaRetailRefundLimits.lsf"));
  assert.ok(runtimeSmokeSource.includes("EXPECTED_TOTAL_MODULES=$((EXPECTED_UPSTREAM_MODULES + 8))"));
  assert.ok(runtimeSmokeSource.includes("7 módulos propios de Rubrova + 1 fixture temporal de CI"));
  assert.ok(deploySmokeSource.includes("RubrovaPaymentTerminals.lsf"));
  assert.ok(deploySmokeSource.includes("RubrovaReplenishmentExport.lsf"));
  assert.ok(deploySmokeSource.includes("replenishment_export_backup_count"));
  assert.ok(deploySmokeSource.includes("payment_terminal_backup_count"));
});

test("la arquitectura de terminales documenta los tres modos, diagramas y límites de red", () => {
  for (const diagram of ["flowchart TD", "sequenceDiagram", "erDiagram"]) {
    assert.ok(paymentArchitectureSource.includes(diagram), "Falta diagrama " + diagram);
  }
  for (const mode of ["Terminal autónoma", "Integración local", "Integración cloud-to-cloud"]) {
    assert.ok(paymentArchitectureSource.includes(mode), "Falta modalidad " + mode);
  }
  for (const rule of ["idempotente", "resultado incierto", "liquidación acreditada", "127.0.0.1"]) {
    assert.ok(paymentArchitectureSource.toLowerCase().includes(rule.toLowerCase()), "Falta regla " + rule);
  }
  assert.ok(paymentArchitectureSource.includes("No hay todavía un adaptador productivo homologado"));
});


test("las devoluciones parciales calculan importes después de los eventos locales y diagnostican respuestas no JSON", () => {
  const helperStart = nativeSalesFixtureSource.indexOf("rubrovaCreateCIReturn");
  const helperEnd = nativeSalesFixtureSource.indexOf("rubrovaTestPartialReturnsApi", helperStart);
  assert.ok(helperStart >= 0 && helperEnd > helperStart);
  const helper = nativeSalesFixtureSource.slice(helperStart, helperEnd);
  assert.ok(helper.indexOf("Invoicing.create(b, i)") < helper.indexOf("executeLocalEvents()"));
  assert.ok(helper.lastIndexOf("executeLocalEvents()") < helper.indexOf("NEW p = Invoicing.OutgoingPayment"));
  assert.ok(helper.includes("Invoicing.amount(p) <- Invoicing.amount(b)"));
  assert.match(uiSmokeSource, /UI_PARTIAL_RETURNS_RESPONSE_CONTENT_TYPE=/);
  assert.match(uiSmokeSource, /UI_PARTIAL_RETURNS_RESPONSE_BODY=/);
  assert.match(uiSmokeSource, /json[.]loads\(response_body\)/);
});



test("el conteo nativo distingue cero de NULL, propaga las hojas y persiste tras reinicio", () => {
  assert.match(adjustmentListSource, /WHEN SETCHANGED\(listRealQuantity/);
  assert.ok(sourcePatch.includes("STOCKTAKE_LIST_AGGREGATE_BEFORE"));
  assert.ok(sourcePatch.includes("STOCKTAKE_LIST_AGGREGATE_AFTER"));
  assert.match(sourcePatch, /GROUP MAX 0[.]000 IF realQuantity\(AdjustmentListLine l\)/);
  assert.match(sourcePatch, /OVERRIDE listRealQuantitySum\(a, p, loc\), listRealQuantityZeroFallback\(a, p, loc\)/);
  assert.ok(sourcePatch.includes("if not apply_stocktake_list_zero_aware_aggregate():"));
  assert.match(nativeSalesFixtureSource, /rubrovaTestStocktakeBarcodeZeroApi/);
  assert.match(nativeSalesFixtureSource, /rubrovaTestStocktakeBarcodeNullApi/);
  assert.match(nativeSalesFixtureSource, /rubrovaTestStocktakeBarcodePositiveApi/);
  assert.match(nativeSalesFixtureSource, /Inventory[.]setRealQuantity\(rubrovaCIStocktakeList\(\), rubrovaCITestProduct\(\), rubrovaCITestLocation\(\), 0\)/);
  assert.match(nativeSalesFixtureSource, /Inventory[.]setRealQuantity\(rubrovaCIStocktakeList\(\), rubrovaCITestProduct\(\), rubrovaCITestLocation\(\), NULL\)/);
  assert.match(nativeSalesFixtureSource, /Inventory[.]useList\(stocktakeCI\) <- TRUE/);
  assert.match(nativeSalesFixtureSource, /rubrovaCIStocktakeListLineQuantity/);
  assert.match(nativeSalesFixtureSource, /Inventory[.]realQuantity\(rubrovaCIStocktakeListLine\(\)\)/);
  assert.doesNotMatch(nativeSalesFixtureSource, /Inventory[.]realQuantity\(rubrovaCIStocktakeList\(\),/);
  assert.match(nativeSalesFixtureSource, /adjustmentQuantityIsNull = NOT Inventory[.]realQuantity\(rubrovaCIStocktakeAdjustmentLine\(\)\)/);
  assert.doesNotMatch(nativeSalesFixtureSource, /\bIS NULL\b/);
  assert.match(nativeSalesFixtureSource, /onHand = Inventory[.]onHand\(rubrovaCITestLocation\(\), rubrovaCITestProduct\(\)\)/);
  assert.match(uiSmokeSource, /[Ee]l conteo descartable alteró el stock físico/);
  assert.match(uiSmokeSource, /adjustmentQuantityIsNull/);
  assert.ok(uiSmokeSource.includes('_stocktake_number(state, "onHand", "restart") - 10.0'));
  assert.ok(uiSmokeSource.includes("después de la venta y las devoluciones POS:"));
  assert.match(nativeSalesFixtureSource, /rubrovaCIStocktakeListLineCount\(\) = \(OVERRIDE/);
  assert.match(nativeSalesFixtureSource, /rubrovaCIStocktakeAdjustmentLineCount\(\) = \(OVERRIDE/);
  assert.match(uiSmokeSource, /def verify_stocktake_barcode_semantics\(/);
  assert.match(uiSmokeSource, /def verify_stocktake_persistence\(/);
  assert.match(uiSmokeSource, /UI_STOCKTAKE_BARCODE_ZERO_PRESERVED=true/);
  assert.match(uiSmokeSource, /UI_STOCKTAKE_BARCODE_NULL_CLEARED=true/);
  assert.match(uiSmokeSource, /UI_STOCKTAKE_BARCODE_AGGREGATE_RECONCILED=true/);
  assert.match(uiSmokeSource, /UI_RESTART_PERSISTENCE_STOCKTAKE=true/);
  assert.match(nativeSmokeSource, /UI_STOCKTAKE_BARCODE_ZERO_PRESERVED=true/);
  assert.match(nativeSmokeSource, /UI_STOCKTAKE_BARCODE_NULL_CLEARED=true/);
  assert.match(nativeSmokeSource, /UI_STOCKTAKE_BARCODE_AGGREGATE_RECONCILED=true/);
  assert.match(nativeSmokeSource, /UI_RESTART_PERSISTENCE_STOCKTAKE=true/);
});

test("los reintegros mixtos respetan el cupo acumulado y las confirmaciones concurrentes", () => {
  assert.match(retailRefundLimitsSource, /rubrovaOriginalPaidByMethod/);
  assert.match(retailRefundLimitsSource, /Invoicing[.]active\(p\)/);
  assert.match(retailRefundLimitsSource, /rubrovaOriginalInvoiceForReturn/);
  assert.match(retailRefundLimitsSource, /rubrovaOriginalPaidForReturn/);
  assert.match(retailRefundLimitsSource, /Invoicing[.]paid\(Invoicing[.]IncomingPayment p, originalInvoice\)/);
  assert.match(retailRefundLimitsSource, /rubrovaRefundedByMethod/);
  assert.match(retailRefundLimitsSource, /rubrovaRefundedBefore/);
  assert.match(retailRefundLimitsSource, /rubrovaRefundRemaining/);
  assert.equal((retailRefundLimitsSource.match(/Invoicing[.]in\(originalInvoice, Invoicing[.]Bill previousBill\)/g) || []).length, 2);
  assert.match(retailRefundLimitsSource, /paymentMethod\(previousBill, p\) = pm/);
  assert.match(retailRefundLimitsSource, /Invoicing[.]active\(p\)/);
  assert.ok(retailReturnsSource.includes("rubrovaOutgoingLedgerAmount (OutgoingPayment p) = amount[Debt](p);"));
  assert.doesNotMatch(retailRefundLimitsSource, /rubrovaOutgoingLedgerAmount \(OutgoingPayment/);
  assert.match(retailRefundLimitsSource, /GROUP SUM Invoicing[.]rubrovaOutgoingLedgerAmount\(Invoicing[.]OutgoingPayment p\)/);
  assert.match(retailRefundLimitsSource, /Saldo reintegrable/);
  assert.match(retailRefundLimitsSource, /CONSTRAINT SET\(rubrovaRefundedByMethod/);
  assert.match(retailRefundLimitsSource, /El total reintegrado por medio de pago supera el importe cobrado originalmente/);
  assert.ok(sourcePatch.includes("RETURN_PAYMENT_INVALID_BEFORE"));
  assert.ok(sourcePatch.includes("RETURN_PAYMENT_INVALID_AFTER"));
  assert.ok(sourcePatch.includes("RETURN_PAYMENT_FORM_AFTER"));
  assert.ok(sourcePatch.includes("RETURN_PAYMENT_DESIGN_BEFORE"));
  assert.ok(sourcePatch.includes("RETURN_PAYMENT_DESIGN_AFTER"));
  assert.ok(sourcePatch.includes("RETURN_PAYMENT_DESIGN_AFTER = chr(10).join(("));
  assert.ok(sourcePatch.includes("if RETURN_PAYMENT_DESIGN_BEFORE in source:"));
  assert.ok(returnPaymentSource.includes("PROPERTY(invoicePaid(b, pm)) { fontSize = 24; }"));
  assert.ok(sourcePatch.includes("rubrovaOriginalPaidForReturn(b, pm)"));
  assert.ok(sourcePatch.includes("RETURN_PAYMENT_APPLY_BEFORE"));
  assert.ok(sourcePatch.includes("RETURN_PAYMENT_APPLY_AFTER"));
  assert.match(sourcePatch, /APPLY SERIALIZABLE/);
  assert.match(sourcePatch, /def apply_cumulative_refund_guard\(/);
  assert.ok(sourcePatch.includes("if not apply_cumulative_refund_guard():"));
  // customerbank exige BankAccount; customercash admite CashAccount.
  assert.match(retailPaymentMethodInitialSource, /incomingPaymentType\(p\) <- incomingPaymentType\('customerbank'\)/);
  assert.match(retailPaymentMethodInitialSource, /outgoingPaymentType\(p\) <- outgoingPaymentType\('customerbank'\)/);
  assert.match(incomingPaymentInitialSource, /id\(i\) <- 'customerbank';\s*bank\(i\) <- TRUE;/);
  assert.match(incomingPaymentInitialSource, /id\(i\) <- 'customercash';\s*cash\(i\) <- TRUE;/);
  assert.match(outgoingPaymentInitialSource, /id\(i\) <- 'customerbank';\s*bank\(i\) <- TRUE;/);
  assert.match(outgoingPaymentInitialSource, /id\(i\) <- 'customercash';\s*cash\(i\) <- TRUE;/);
  assert.match(incomingPaymentSource, /companyAccount\(IncomingPayment p\) IS CashAccount AND NOT cash\(type\(p\)\)/);
  assert.match(outgoingPaymentSource, /companyAccount\(OutgoingPayment p\) IS CashAccount AND NOT cash\(type\(p\)\)/);
  assert.match(bankAccountSource, /number 'Account number' = DATA STRING\[30\] \(BankAccount\) IN id NONULL/);
  assert.match(bankAccountSource, /bank 'Bank' = DATA Bank \(BankAccount\) NONULL/);
  assert.match(nativeRetailFixtureSource, /NEW cardAccountCI = BankAccount/);
  assert.match(nativeRetailFixtureSource, /number\(cardAccountCI\) <- '000000000001'/);
  assert.match(nativeRetailFixtureSource, /bank\(cardAccountCI\) <- bankCI/);
  assert.doesNotMatch(nativeRetailFixtureSource, /NEW cardAccountCI = CashAccount/);
  assert.match(nativeLocalDemoRetailSource, /NEW cardAccountDemo = BankAccount/);
  assert.match(nativeLocalDemoRetailSource, /number\(cardAccountDemo\) <- '000000000099'/);
  assert.match(nativeLocalDemoRetailSource, /bank\(cardAccountDemo\) <- bankDemo/);
  assert.ok(
    nativeLocalDemoRetailSource.indexOf("NEW bankDemo = Bank {") <
      nativeLocalDemoRetailSource.indexOf("NEW cardAccountDemo = BankAccount {"),
  );
  assert.ok(
    nativeLocalDemoRetailSource.indexOf("NEW cardAccountDemo = BankAccount {") <
      nativeLocalDemoRetailSource.indexOf("NEW cashRegisterDemo = Pos {"),
  );
  assert.match(nativeLocalDemoRetailSource, /account\(pos\('rubrova-demo'\), PaymentMethod pm\) <- rubrovaDemoCardAccount\(\)/);
  assert.doesNotMatch(nativeLocalDemoRetailSource, /NEW cardAccountDemo = CashAccount/);
  assert.match(nativeRetailFixtureSource, /rubrova-ci-refund/);
  // Los fondos independientes evitan que el constraint de saldo de cuenta
  // enmascare el límite acumulado de reintegros por factura y medio de pago.
  assert.match(incomingPaymentInitialSource, /id\(i\) <- 'initial';[\s\S]*?bank\(i\) <- TRUE;[\s\S]*?cash\(i\) <- TRUE;/);
  assert.match(paymentLedgerSource, /balance 'Balance' \(Account a\) = GROUP SUM signedAmount\(Payment p\)/);
  assert.match(paymentLedgerSource, /CONSTRAINT balance\(Account a\) < 0 AND NOT allowNegative\(a\)/);
  assert.match(nativeSalesFixtureSource, /rubrovaCIMixedOpeningCashPayment = DATA Invoicing[.]IncomingPayment/);
  assert.match(nativeSalesFixtureSource, /rubrovaCIMixedOpeningCardPayment = DATA Invoicing[.]IncomingPayment/);
  assert.match(nativeSalesFixtureSource, /incomingPaymentType\('initial'\)/);
  assert.match(nativeSalesFixtureSource, /rubrova-ci-opening-cash/);
  assert.match(nativeSalesFixtureSource, /rubrova-ci-opening-card/);
  assert.match(nativeSalesFixtureSource, /Invoicing[.]amount\(openingCash\) <- 1000/);
  assert.match(nativeSalesFixtureSource, /Invoicing[.]amount\(openingCard\) <- 1000/);
  assert.match(nativeSalesFixtureSource, /cashAccountBalance = Invoicing[.]balance/);
  assert.match(nativeSalesFixtureSource, /cardAccountBalance = Invoicing[.]balance/);
  const openingBalanceSource = nativeSalesFixtureSource.slice(
    nativeSalesFixtureSource.indexOf("rubrovaEnsureCIMixedOpeningBalances"),
    nativeSalesFixtureSource.indexOf("rubrovaEnsureCIMixedSale"),
  );
  assert.doesNotMatch(openingBalanceSource, /Invoicing[.]paid|Retail[.]paymentMethod\((?:openingCash|openingCard),/);
  assert.match(uiSmokeSource, /"cashAccountBalance": 1300/);
  assert.match(uiSmokeSource, /"cardAccountBalance": 1450/);
  assert.match(uiSmokeSource, /"cashAccountBalance": 1000/);
  assert.match(uiSmokeSource, /"cardAccountBalance": 1000/);
  assert.match(uiSmokeSource, /not in rejection_message/);
  assert.match(nativeSalesFixtureSource, /rubrovaTestCumulativeRefundsApi/);
  assert.match(nativeSalesFixtureSource, /Retail[.]beforeOpen\(mixedSession\)/);
  assert.ok(nativeSalesFixtureSource.includes("IF Retail.session(Invoicing.Bill b) = rubrovaCITestSession()"));
  assert.ok(nativeSalesFixtureSource.includes("IF Retail.session(Invoicing.Bill b) = rubrovaCIMixedSession()"));
  assert.match(nativeSalesFixtureSource, /Retail[.]afterOpen\(mixedSession\)/);
  assert.match(nativeSalesFixtureSource, /NEWSESSION \{[\s\S]*Retail[.]beforeOpen\(mixedSession\)/);
  assert.match(nativeSalesFixtureSource, /rubrovaTestCumulativeRefundRaceAApi/);
  assert.match(nativeSalesFixtureSource, /rubrovaTestCumulativeRefundRaceBApi/);
  assert.match(nativeSalesFixtureSource, /rubrovaTestCumulativeRefundBillCancelApi/);
  assert.match(nativeSalesFixtureSource, /rubrovaTestCumulativeRefundReleaseApi/);
  assert.match(nativeSalesFixtureSource, /rubrovaCumulativeRefundsReconciliationApi/);
  assert.match(nativeSalesFixtureSource, /Retail[.]paid\(rubrovaCIMixedInvoice\(\), Retail[.]cashPaymentMethod\(\)\)/);
  assert.match(nativeSalesFixtureSource, /Retail[.]paid\(rubrovaCIMixedInvoice\(\), Retail[.]paymentMethod\('card'\)\)/);
  assert.match(nativeSalesFixtureSource, /Invoicing[.]cancel\(rubrovaCIMixedFirstRefundBill\(\)\)/);
  assert.match(nativeSalesFixtureSource, /originalBillCanceled = Invoicing[.]canceled/);
  assert.match(nativeSalesFixtureSource, /originalBillReady = Invoicing[.]ready/);
  assert.match(nativeSalesFixtureSource, /originalBillActivityState = CASE WHEN Invoicing[.]active/);
  assert.match(uiSmokeSource, /cancelled_payload[.]get\("originalBillCanceled"\) is not True/);
  assert.match(uiSmokeSource, /cancelled_payload[.]get\("originalBillActivityState"\) != "inactive"/);
  assert.match(uiSmokeSource, /released_payload[.]get\("originalBillCanceled"\) is not True/);
  assert.match(uiSmokeSource, /state[.]get\("originalBillCanceled"\) is not True/);
  assert.doesNotMatch(uiSmokeSource, /cancelled_payload[.]get\("originalBillActive"\) is not False/);
  assert.match(nativeSalesFixtureSource, /Invoicing[.]cancel\(p\)/);
  assert.match(nativeSalesFixtureSource, /APPLY SERIALIZABLE/);
  assert.match(uiSmokeSource, /def verify_cumulative_refunds\(context: Any, url: str, browser: Any\)/);
  assert.match(uiSmokeSource, /ThreadPoolExecutor\(max_workers=2/);
  assert.match(uiSmokeSource, /UI_CUMULATIVE_REFUNDS_OVER_LIMIT_REJECTED=true/);
  assert.match(uiSmokeSource, /UI_CUMULATIVE_REFUNDS_CONCURRENT_SERIALIZED=true/);
  assert.match(uiSmokeSource, /UI_CUMULATIVE_REFUNDS_BILL_CANCEL_DOES_NOT_RELEASE_CAP=true/);
  assert.match(uiSmokeSource, /UI_CUMULATIVE_REFUNDS_PAYMENT_CANCEL_RELEASES_CAP=true/);
  assert.match(uiSmokeSource, /UI_CUMULATIVE_REFUNDS_RECONCILED=true/);
  assert.match(uiSmokeSource, /UI_RESTART_PERSISTENCE_CUMULATIVE_REFUNDS=true/);
  for (const marker of [
    "UI_CUMULATIVE_REFUNDS_OVER_LIMIT_REJECTED=true",
    "UI_CUMULATIVE_REFUNDS_CONCURRENT_SERIALIZED=true",
    "UI_CUMULATIVE_REFUNDS_BILL_CANCEL_DOES_NOT_RELEASE_CAP=true",
    "UI_CUMULATIVE_REFUNDS_PAYMENT_CANCEL_RELEASES_CAP=true",
    "UI_CUMULATIVE_REFUNDS_RECONCILED=true",
    "UI_RESTART_PERSISTENCE_CUMULATIVE_REFUNDS=true",
  ]) assert.ok(nativeSmokeSource.includes(marker), "Falta exigir el marcador " + marker);
});

test("el visor Markdown no bloquea el inicio POS ni requiere CDN para abrir el turno", () => {
  const markdownViewerIsUpstream =
    markdownViewerSource.includes("onWebClientLoad() +") &&
    markdownViewerSource.includes("https://cdn.jsdelivr.net/npm/marked/marked.min.js");
  const markdownViewerIsAlreadyPatched =
    !markdownViewerSource.includes("onWebClientLoad() +") &&
    markdownViewerSource.includes("marked@18.3.0/lib/marked.umd.js") &&
    markdownViewerSource.includes("marked-gfm-heading-id@4.1.4/lib/index.umd.js");
  assert.ok(
    markdownViewerIsUpstream || markdownViewerIsAlreadyPatched,
    "El visor debe ser la versión upstream conocida o la versión Rubrova de carga diferida."
  );
  assert.ok(sourcePatch.includes("MARKDOWN_VIEWER_TARGET"));
  assert.ok(sourcePatch.includes("MARKDOWN_VIEWER_CDN_BLOCK"));
  assert.ok(sourcePatch.includes("def apply_markdown_viewer_lazy_load()"));
  assert.ok(sourcePatch.includes("marked@18.3.0/lib/marked.umd.js"));
  assert.ok(sourcePatch.includes("marked-gfm-heading-id@4.1.4/lib/index.umd.js"));
  assert.ok(sourcePatch.includes("if not apply_markdown_viewer_lazy_load():"));
  assert.match(uiSmokeSource, /"markdown_requests": \[\]/);
  assert.match(uiSmokeSource, /UI_MARKDOWN_DEPENDENCIES_LAZY_LOADED=true/);
  assert.match(nativeSmokeSource, /UI_MARKDOWN_DEPENDENCIES_LAZY_LOADED=true/);
});


test("el preflight rápido se comparte entre el equipo y los workflows CI", () => {
  assert.match(localPreflightSource, /--platform/);
  assert.match(localPreflightSource, /--replenishment/);
  assert.match(localPreflightSource, /--all/);
  assert.match(localPreflightSource, /validate-mycompany-extension[.]test[.]mjs/);
  assert.match(localPreflightSource, /test_adapt_mycompany_native_export[.]py/);
  assert.ok(runtimeWorkflowSource.includes("bash scripts/platform/local-preflight.sh --platform"));
  assert.ok(plannerWorkflowSource.includes("bash scripts/platform/local-preflight.sh --replenishment"));
  assert.match(runtimeWorkflowSource, /native-runtime-smoke-macos-arm64:/);
  const workflowLines = runtimeWorkflowSource.split(String.fromCharCode(10));
  const macosJobLine = workflowLines.indexOf("  native-runtime-smoke-macos-arm64:");
  assert.ok(macosJobLine >= 0, "Debe existir un job nativo específico para macOS ARM64.");
  const nextJobLine = workflowLines.findIndex((line, index) => index > macosJobLine && /^  [a-z][a-z0-9-]*:$/.test(line));
  const macosJobSource = workflowLines.slice(macosJobLine, nextJobLine < 0 ? undefined : nextJobLine).join(String.fromCharCode(10));
  assert.match(macosJobSource, /runs-on: macos-26/);
  assert.doesNotMatch(macosJobSource, /if: github[.]event_name == 'workflow_dispatch'/,
    "El smoke nativo macOS ARM64 debe correr automáticamente en cada PR.");
});


test("las devoluciones parciales usan el documento original y sólo permiten el remanente", () => {
  assert.match(entrypointSource, /RubrovaRetailReturns/);
  assert.match(retailReturnsSource, /^MODULE RubrovaRetailReturns;/m);
  assert.match(retailReturnsSource, /^NAMESPACE Invoicing;/m);
  assert.doesNotMatch(retailReturnsSource, /^NAMESPACE Retail;/m);
  assert.match(retailRefundLimitsSource, /^MODULE RubrovaRetailRefundLimits;/m);
  assert.match(retailRefundLimitsSource, /^NAMESPACE Retail;/m);
  assert.match(retailRefundLimitsSource, /^REQUIRE CreditNote, SessionPayment, IncomingPaymentDebt, RubrovaRetailReturns;/m);
  assert.match(retailReturnsSource, /^REQUIRE CreditNote, OutgoingPaymentDebt;/m);
  assert.match(retailReturnsSource, /fill \(BillLine currentLine, InvoiceLine originalLine\) \+/);
  assert.match(creditNoteSource, /fill ABSTRACT LIST \(BillLine, InvoiceLine\)/);
  assert.match(retailReturnsSource, /type\(invoice\(originalLine\)\) = invoiceType\('retail'\)/);
  assert.match(retailReturnsSource, /invoiceLine\(previousLine\) = originalLine/);
  assert.match(retailReturnsSource, /bill\(previousLine\) != currentBill/);
  assert.match(retailReturnsSource, /active\(bill\(previousLine\)\)/);
  assert.match(retailReturnsSource, /max\(quantity\(invoiceLine\(currentLine\)\) \(-\)/);
  assert.match(retailReturnsSource, /DELETE currentLine/);
  assert.match(creditNoteSource, /@defineDocLineRelation\(invoice, bill, 'Invoice', 'Return', i, b\)/);
  assert.match(creditNoteSource, /returned 'Returned' \(InvoiceLine il\) =/);
  assert.match(creditNoteSource, /CONSTRAINT SET\(returned\(InvoiceLine il\) > OVERRIDE quantity\(il\), 0[.]0\) AND checkReturnedQuantity\(type\(il\)\)/);
  assert.match(creditNoteReceiptInitialSource, /autoCreateReceipt\(BillType t\) <- TRUE WHERE id\(t\) = 'retailreturn'/);
  assert.match(returnPaymentSource, /invalidAmount\(Bill b, PaymentMethod pm\) = amount\(pm\) > OVERRIDE invoicePaid\(b, pm\), 0[.]0/);
  assert.match(returnPaymentSource, /done\(p\) <- TRUE/);
  assert.match(cashMovementSource, /session\(ip\) <- openedSession\(p\)/);
  assert.match(cashMovementSource, /session\(op\) <- openedSession\(p\)/);
  assert.match(nativeSalesFixtureSource, /rubrovaTestPartialReturnsApi/);
  assert.match(nativeSalesFixtureSource, /explicitQuantity/);
  assert.match(nativeSalesFixtureSource, /Invoicing[.]quantity\(bl\) <- 0[.]7/);
  assert.match(nativeSalesFixtureSource, /Invoicing[.]amount\(p\) <- Invoicing[.]amount\(b\)/);
  assert.match(nativeSalesFixtureSource, /Invoicing[.]paid\(b, p\) <- Invoicing[.]amount\(b\)/);
  assert.match(nativeSalesFixtureSource, /rubrovaOverReturnRejected = DATA BOOLEAN/);
  assert.match(nativeSalesFixtureSource, /rubrovaOverReturnRejectedLocal = DATA LOCAL NESTED BOOLEAN/);
  assert.match(nativeSalesFixtureSource, /rubrovaOverReturnRejected\(\) <- NULL/);
  assert.match(nativeSalesFixtureSource, /IF canceled\(\) THEN rubrovaOverReturnRejectedLocal\(\) <- TRUE/);
  assert.match(nativeSalesFixtureSource, /IF rubrovaOverReturnRejectedLocal\(\) THEN/);
  assert.match(nativeSalesFixtureSource, /rubrovaCIReturnCount\(\) = OVERRIDE Retail[.]countBills/);
  assert.match(nativeSalesFixtureSource, /rubrovaCIReturnAmount\(\) = OVERRIDE Retail[.]totalAmountBill/);
  assert.match(nativeSalesFixtureSource, /rubrovaCIReturnedQuantity\(\) = OVERRIDE Invoicing[.]returned/);
  assert.match(nativeSalesFixtureSource, /rubrovaCIReturnCashPaymentCount\(\) = OVERRIDE/);
  assert.match(nativeSalesFixtureSource, /rubrovaCIReturnCashPaymentAmount\(\) = OVERRIDE/);
  assert.match(nativeSalesFixtureSource, /sourceInvoiceFound = CASE WHEN rubrovaCITestInvoice\(\) THEN 1 ELSE 0/);
  assert.match(nativeSalesFixtureSource, /sourceInvoiceLineFound = CASE WHEN rubrovaCITestInvoiceLine\(\) THEN 1 ELSE 0/);
  assert.match(nativeSalesFixtureSource, /rubrovaCIReturnedQuantity\(\)/);
  assert.match(nativeSalesFixtureSource, /rubrovaPartialReturnsReconciliationApi/);
  assert.match(uiSmokeSource, /verify_partial_returns\(context, url\)/);
  assert.match(uiSmokeSource, /UI_PARTIAL_RETURNS_RECONCILED=true/);
  assert.match(nativeSmokeSource, /UI_PARTIAL_RETURNS_RECONCILED=true/);
  assert.match(uiSmokeSource, /UI_RESTART_PERSISTENCE_PARTIAL_RETURNS=true/);
  assert.match(nativeSmokeSource, /UI_RESTART_PERSISTENCE_PARTIAL_RETURNS=true/);
});

test("la fixture inicializa todos los booleanos con NULL y el smoke extrae ubicaciones sin confundir timestamps", () => {
  assert.match(nativeSalesFixtureSource, /rubrovaCIMixedOverLimitRejected = DATA BOOLEAN/);
  assert.match(nativeSalesFixtureSource, /rubrovaCIMixedOverLimitRejected\(\) <- NULL/);
  assert.match(nativeSalesFixtureSource, /rubrovaCIMixedOverLimitRejectedLocal = DATA LOCAL NESTED BOOLEAN/);
  assert.match(nativeSalesFixtureSource, /rubrovaCIMixedOverLimitRejectedLocal\(\) <- NULL/);
  assert.match(nativeSalesFixtureSource, /rubrovaCIMixedRaceAAccepted = DATA LOCAL NESTED BOOLEAN/);
  assert.match(nativeSalesFixtureSource, /rubrovaCIMixedRaceAAccepted\(\) <- NULL/);
  assert.match(nativeSalesFixtureSource, /rubrovaCIMixedRaceBAccepted = DATA LOCAL NESTED BOOLEAN/);
  assert.match(nativeSalesFixtureSource, /rubrovaCIMixedRaceBAccepted\(\) <- NULL/);
  assert.match(nativeSalesFixtureSource, /rubrovaCIMixedBillCancelRejectedLocal = DATA LOCAL NESTED BOOLEAN/);
  assert.match(nativeSalesFixtureSource, /rubrovaCIMixedBillCancelRejectedLocal\(\) <- NULL/);
  assert.doesNotMatch(nativeSalesFixtureSource, /<-\s*FALSE\s*;/,
    "Las fixtures lsFusion deben limpiar los booleanos con NULL y no asignar FALSE.");
  assert.match(nativeSmokeSource, /report_native_startup_failure\(\)/);
  assert.match(nativeSmokeSource, /record_failed_native_supervisor_exit\(\)/);
  assert.match(nativeSmokeSource, /RUBROVA_NATIVE_FAILURE_KIND=lsfusion_logic_initialization/);
  assert.match(nativeSmokeSource, /RUBROVA_NATIVE_SOURCE_LOCATION=/);
  assert.match(nativeSmokeSource, /RUBROVA_NATIVE_SUPERVISOR_EXIT_CODE=/);
  assert.ok(nativeSmokeSource.includes("grep -Eo '[[:alpha:]_][[:alnum:]_]*:[0-9]+:[0-9]+'"),
    "La extracción de módulo:línea:columna no debe aceptar horas HH:MM:SS.");
  assert.match(nativeSmokeSource, /Exception while starting logics instance/);
});
