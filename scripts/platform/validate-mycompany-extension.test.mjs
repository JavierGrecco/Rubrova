import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const read = (relative) => readFileSync(path.join(root, relative), "utf8");

const lock = JSON.parse(read("platform/mycompany-6.2.lock.json"));
const entrypointSource = read("extensions/lsfusion/RubrovaCustom.lsf");
const moduleSource = read("extensions/lsfusion/RubrovaPOSLocalization.lsf");
const bundle = read("extensions/lsfusion/MyCompanyResourceBundle_es_AR.properties");
const preparerSource = read("scripts/platform/prepare-mycompany-6.2.sh");
const runtimeSmokeSource = read("scripts/platform/test-runtime-smoke.sh");

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
  assert.match(runtimeSmokeSource, /JAVA_OPTS: "-Dlogics\.topModule=RubrovaCustom"/);
  assert.match(runtimeSmokeSource, /USER_SETLANGUAGE: "es"/);
  assert.match(runtimeSmokeSource, /USER_SETCOUNTRY: "AR"/);
  assert.match(runtimeSmokeSource, /JAVA_OPTS=-Dlogics\.topModule=RubrovaCustom/);
  assert.match(runtimeSmokeSource, /Argumento Java activo/);
  assert.match(runtimeSmokeSource, /RUBROVA_CUSTOM_LOG_EVIDENCE/);
  assert.match(runtimeSmokeSource, /RUBROVA_LOCALIZATION_LOG_EVIDENCE/);
  assert.match(runtimeSmokeSource, /Los registros confirman RubrovaPOSLocalization y RubrovaCustom/);
  assert.match(runtimeSmokeSource, /docker inspect/);
  assert.match(runtimeSmokeSource, /docker exec/);
  assert.match(runtimeSmokeSource, /logics\\\\\.\(topModule\|includePaths\|excludePaths\)/);
  assert.match(runtimeSmokeSource, /EXPECTED_UPSTREAM_MODULES=712/);
  assert.match(runtimeSmokeSource, /EXPECTED_TOTAL_MODULES/);
  assert.match(runtimeSmokeSource, /MODULE_PROGRESS_CHANGED_AT/);
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
  assert.match(runtimeSmokeSource, /docker-server\/logs/);
  assert.match(runtimeSmokeSource, /compose logs --no-color --tail=180 server/);
  assert.match(runtimeSmokeSource, /tail -n 80/);
  assert.match(runtimeSmokeSource, /successfully started/);
  assert.match(runtimeSmokeSource, /RubrovaPOSLocalization/);
});

test("la extensión superior requiere MyCompany sin copiar sus módulos", () => {
  assert.match(entrypointSource, /^MODULE RubrovaCustom;/m);
  assert.match(entrypointSource, /^REQUIRE MyCompany, RubrovaPOSLocalization;/m);
  assert.match(moduleSource, /^MODULE RubrovaPOSLocalization;/m);
  assert.match(moduleSource, /^REQUIRE MyCompany;/m);
  assert.equal(lock.extension.topModule, "RubrovaCustom");
  assert.match(moduleSource, /^NAMESPACE Retail;/m);
  assert.match(moduleSource, /DESIGN posDashboard/);
  assert.match(moduleSource, /DESIGN posPayment/);
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
    "rubrova.payment.method_title"
  ];
  for (const key of required) assert.ok(entries.has(key), "Falta traducción obligatoria: " + key);
  assert.ok(entries.size >= 70, "Glosario inicial demasiado pequeño: " + entries.size);
  const customIds = [...moduleSource.matchAll(/\{(rubrova\.[^}]+)\}/g)].map((match) => match[1]);
  for (const id of customIds) assert.ok(entries.has(id), "Falta traducción del caption Rubrova: " + id);
  assert.equal(lock.extension.locale, "es_AR");
  assert.match(lock.extension.translationStatus, /partial/);
});

test("los scripts de despliegue configuran el módulo y conservan backups", () => {
  const shell = read("scripts/platform/deploy-mycompany-6.2.sh");
  const powershell = read("scripts/platform/deploy-mycompany-6.2.ps1");
  assert.match(shell, /logics\.topModule = RubrovaCustom/);
  assert.match(shell, /user\.setLanguage = es/);
  assert.match(shell, /user\.setCountry = AR/);
  assert.match(shell, /docker-server/);
  assert.match(shell, /RubrovaPOSLocalization\.lsf/);
  assert.match(shell, /systemctl restart lsfusion6-server|systemctl start lsfusion6-server/);
  assert.match(powershell, /logics\.topModule = RubrovaCustom/);
  assert.match(powershell, /user\.setLanguage = es/);
  assert.match(powershell, /user\.setCountry = AR/);
  assert.match(powershell, /RubrovaPOSLocalization\.lsf/);
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
