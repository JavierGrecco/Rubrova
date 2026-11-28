import test from "node:test";
import assert from "node:assert/strict";
import { existsSync, readFileSync, readdirSync } from "node:fs";
import path from "node:path";

const root = process.cwd();
const read = (file) => readFileSync(path.join(root, file), "utf8");
const indexPath = "docs/platform-audit/README.md";

function markdownFiles(directory, { excludeVendor = false } = {}) {
  const result = [];
  for (const entry of readdirSync(path.join(root, directory), { withFileTypes: true })) {
    if (excludeVendor && directory === "." && entry.name === "vendor") continue;
    const absolute = path.join(directory, entry.name);
    if (entry.isDirectory()) result.push(...markdownFiles(absolute, { excludeVendor }));
    else if (entry.isFile() && entry.name.toLowerCase().endsWith(".md")) {
      result.push(absolute.split(path.sep).join("/"));
    }
  }
  return result.sort();
}

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

const mandatoryToolPaths = [
  "AGENTS.md",
  "README.md",
  "docs/ENGINEERING_MASTER.md",
  "docs/WORKFLOW.md",
  ".github/pull_request_template.md",
  "platform/source-lock.json",
  "platform/mycompany-6.2.lock.json",
  "extensions/lsfusion/RubrovaCustom.lsf",
  "scripts/platform/audit-lsf-source.mjs",
  "scripts/platform/audit-lsf-source.test.mjs",
  "scripts/platform/audit-source-docs.mjs",
  "scripts/platform/audit-source-docs.test.mjs",
  "scripts/platform/local-preflight.sh",
  "scripts/platform/validate-vendored-sources.sh",
  "patches/lsfusion/README.md",
  "vendor/UPSTREAM_SOURCES.md",
  "vendor/mycompany/README.md",
  "vendor/mycompany/CHANGELOG.md",
  "vendor/platform/README.md",
  "vendor/platform/README_ru.md",
  "vendor/platform/CHANGELOG.md",
  "vendor/platform/server/src/main/resources/web/objects/multiselect/README.md",
];

test("el índice existe y contiene todos los documentos mantenidos por Rubrova fuera de vendor", () => {
  assert.ok(existsSync(path.join(root, indexPath)), "Falta el índice obligatorio de conocimiento.");
  const index = read(indexPath);
  const files = markdownFiles(".", { excludeVendor: true });
  const docsFiles = markdownFiles("docs");

  assert.equal(docsFiles.length, 69, "Cambió el inventario de docs/: actualizar el catálogo.");
  assert.equal(files.length, 73, "Cambió el inventario Markdown fuera de vendor/: clasificar cada alta o baja.");
  for (const file of files) {
    assert.ok(index.includes(file), `Documento fuera de vendor sin clasificar en el índice integral: ${file}`);
  }
});

test("los siete documentos Markdown auxiliares de vendor quedan identificados", () => {
  const index = read(indexPath);
  const supportFiles = [
    "vendor/UPSTREAM_SOURCES.md",
    "vendor/mycompany/README.md",
    "vendor/mycompany/CHANGELOG.md",
    "vendor/platform/README.md",
    "vendor/platform/README_ru.md",
    "vendor/platform/CHANGELOG.md",
    "vendor/platform/server/src/main/resources/web/objects/multiselect/README.md",
  ];
  for (const file of supportFiles) {
    assert.ok(existsSync(path.join(root, file)), `Falta el documento auxiliar de vendor: ${file}`);
    assert.ok(index.includes(file), `El índice no menciona el documento auxiliar de vendor: ${file}`);
  }
});

test("todos los dossiers especializados están presentes y enlazados", () => {
  const index = read(indexPath);
  for (const dossier of requiredDossiers) {
    const file = `docs/platform-audit/${dossier}`;
    assert.ok(existsSync(path.join(root, file)), `Falta el dossier obligatorio: ${file}`);
    assert.ok(index.includes(file), `El índice no contiene la ruta completa de ${file}`);
  }
});

test("las herramientas, locks y fuentes de composición forman parte del recorrido documentado", () => {
  const index = read(indexPath);
  for (const file of mandatoryToolPaths) {
    assert.ok(existsSync(path.join(root, file)), `Falta una pieza de la cadena de auditoría: ${file}`);
    assert.ok(index.includes(file), `La cadena de auditoría no está documentada en el índice: ${file}`);
  }
});

test("el índice mantiene las rutas de lectura, relaciones cruzadas y anexos históricos", () => {
  const index = read(indexPath);
  for (const marker of [
    "Orden recomendado de lectura",
    "Rutas de lectura por tipo de trabajo",
    "Mapa de relaciones entre los documentos de dominio",
    "Auditoría reuse-first de MyCompany y lsFusion",
    "Guía de integración lsFusion 6.2 y MyCompany 6.2",
    "Inventario, stock, depósitos, conteos y costos",
    "Facturación, impuestos, deuda, pagos y contabilidad argentina",
    "800 módulos LSF",
    "69 documentos Markdown en",
    "1.111 archivos Markdown",
    "73 documentos mantenidos por Rubrova",
    "1.038 archivos Markdown",
    "1.031 páginas de documentación upstream",
    "retención de 30 días",
    "puerta 9.7",
  ]) {
    assert.ok(index.toLowerCase().includes(marker.toLowerCase()), `Falta una ruta o regla obligatoria: ${marker}`);
  }
});

test("README, AGENTS, workflow y plantilla mantienen visible la obligación de consultar el mapeo", () => {
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
