import test from "node:test";
import assert from "node:assert/strict";
import { existsSync, readFileSync, readdirSync } from "node:fs";
import path from "node:path";

const root = process.cwd();
const read = (file) => readFileSync(path.join(root, file), "utf8");
const requiredDossiers = [
  "MYCOMPANY_6_2_FUNCTIONAL_MAP.md",
  "MYCOMPANY_6_2_RETAIL_POS_SESSIONS_MAP.md",
  "MYCOMPANY_6_2_SALES_PRICING_LEDGER_MAP.md",
  "MYCOMPANY_6_2_INVENTORY_LEDGER_MAP.md",
  "MYCOMPANY_6_2_PURCHASE_REPLENISHMENT_MAP.md",
  "MYCOMPANY_6_2_INVOICING_LEDGER_MAP.md",
  "MYCOMPANY_6_2_MASTERDATA_RELATIONSHIPS_MAP.md",
  "MYCOMPANY_6_2_CRM_LEADS_MAP.md",
  "MYCOMPANY_6_2_HR_ATTENDANCE_PAYROLL_MAP.md",
  "MYCOMPANY_6_2_PROJECT_MANAGEMENT_INTEGRATIONS_MAP.md",
  "MYCOMPANY_6_2_FLEET_VEHICLE_COSTS_MAP.md",
  "MYCOMPANY_6_2_UTILITY_MODULES.md",
  "MYCOMPANY_6_2_REGIONAL_MODULES.md",
  "LSFUSION_6_2_CAPABILITY_MAP.md",
];

test("el índice visible de mapeo existe y cubre todos los dossiers", () => {
  const indexPath = "docs/platform-audit/README.md";
  assert.ok(existsSync(path.join(root, indexPath)), "Falta el índice obligatorio de mapeo.");
  const index = read(indexPath);

  for (const dossier of requiredDossiers) {
    assert.ok(
      existsSync(path.join(root, "docs/platform-audit", dossier)),
      `Falta el dossier requerido: ${dossier}`,
    );
    assert.ok(index.includes(dossier), `El índice no enlaza ${dossier}.`);
  }

  const mapFiles = readdirSync(path.join(root, "docs/platform-audit"))
    .filter((name) => /^(MYCOMPANY_6_2_.*_(?:MAP|MODULES)\.md|LSFUSION_6_2_CAPABILITY_MAP\.md)$/.test(name));
  for (const file of mapFiles) {
    assert.ok(index.includes(file), `Se agregó un dossier sin incorporarlo al índice: ${file}`);
  }
});

test("el índice conserva los límites del relevamiento y el inventario base", () => {
  const index = read("docs/platform-audit/README.md");
  assert.match(index, /Estado del relevamiento: EN CURSO/);
  assert.match(index, /800 módulos LSF/);
  assert.match(index, /112 módulos MyCompany/);
  assert.match(index, /347 archivos Markdown/);
  assert.match(index, /684 páginas Markdown/);
  assert.match(index, /No se debe escribir.*completamente analizado/s);
});

test("README, agentes y flujo de trabajo hacen visible y obligatorio el mapeo", () => {
  const readme = read("README.md");
  const agents = read("AGENTS.md");
  const workflow = read("docs/WORKFLOW.md");
  const template = read(".github/pull_request_template.md");

  assert.ok(readme.includes("docs/platform-audit/README.md"));
  assert.ok(agents.includes("docs/platform-audit/README.md"));
  assert.ok(agents.includes("Regla reuse-first obligatoria"));
  assert.ok(workflow.includes("Puerta obligatoria de mapeo"));
  assert.ok(template.includes("Revisión obligatoria del mapeo"));
});

