import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const read = (relative) => readFileSync(path.join(root, relative), "utf8");

const lock = JSON.parse(read("platform/mycompany-6.2.lock.json"));
const moduleSource = read("extensions/lsfusion/RubrovaCustom.lsf");
const bundle = read("extensions/lsfusion/MyCompanyResourceBundle_es_AR.properties");

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
  assert.equal(lock.artifacts.dockerCompose.sha256, null);
  assert.match(lock.artifacts.dockerCompose.url, /\/6\.2\/compose\.yaml$/);
});

test("la extensión superior requiere MyCompany sin copiar sus módulos", () => {
  assert.match(moduleSource, /^MODULE RubrovaCustom;/m);
  assert.match(moduleSource, /^REQUIRE MyCompany;/m);
  assert.equal(lock.extension.topModule, "RubrovaCustom");
  assert.match(moduleSource, /^NAMESPACE Retail;/m);
  assert.match(moduleSource, /DESIGN posDashboard/);
  assert.match(moduleSource, /DESIGN posPayment/);
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
  assert.match(shell, /docker-server/);
  assert.match(shell, /systemctl restart lsfusion6-server|systemctl start lsfusion6-server/);
  assert.match(powershell, /logics\.topModule = RubrovaCustom/);
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
