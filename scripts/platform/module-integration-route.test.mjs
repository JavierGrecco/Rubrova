import test from "node:test";
import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import {
  resolveModuleIntegrationRoute,
  renderModuleIntegrationRoute,
  renderModuleIntegrationRouteJson,
  parseArgs,
} from "./module-integration-route.mjs";
import { buildSourceCatalog } from "./audit-lsf-source.mjs";

const root = process.cwd();
const read = (file) => readFileSync(path.join(root, file), "utf8");

function makeModule(moduleName, options = {}) {
  return {
    moduleName,
    path: options.path || `vendor/mycompany/src/main/lsfusion/inventory/${moduleName}.lsf`,
    namespace: options.namespace || null,
    domain: options.domain || "inventory",
    requires: options.requires || [],
    reachableFromApplicationRoot: options.active ?? true,
    counts: {
      classes: 1,
      properties: 3,
      actions: 2,
      forms: 1,
      constraints: 0,
      whenEvents: 1,
      onEvents: 0,
      apiAnnotations: 0,
      actionDeclarationsAreHeuristic: true,
    },
    declarations: {
      classes: [{ name: `${moduleName}Record`, line: 3 }],
      properties: [{ name: `${moduleName.toLowerCase()}Total`, line: 8 }],
      actions: [{ name: `confirm${moduleName}`, line: 14 }],
      forms: [{ name: `${moduleName.toLowerCase()}Form`, line: 20 }],
      constraints: [],
      whenEvents: [{ name: null, line: 29 }],
      onEvents: [],
      apiAnnotations: [],
    },
    ...options.overrides,
  };
}

const fixtureCatalog = {
  sources: {
    myCompany: { tag: "6.2", commit: "mycompany-sha" },
    lsFusion: { tag: "6.2", commit: "lsfusion-sha" },
  },
  myCompany: {
    modules: [
      makeModule("InvLedger", { requires: ["Product", "Location"] }),
      makeModule("Product", { domain: "masterdata", path: "vendor/mycompany/src/main/lsfusion/masterdata/items/products/Product.lsf", requires: ["Item"] }),
      makeModule("Item", { domain: "masterdata", path: "vendor/mycompany/src/main/lsfusion/masterdata/items/Item.lsf" }),
      makeModule("Location", { domain: "inventory", path: "vendor/mycompany/src/main/lsfusion/inventory/locations/Location.lsf" }),
      makeModule("GeoUtils", { domain: "utils", path: "vendor/mycompany/src/main/lsfusion/utils/GeoUtils.lsf" }),
      makeModule("RegionalTax", { domain: "region", path: "vendor/mycompany/src/main/lsfusion/region/RegionalTax.lsf" }),
      makeModule("Inventory", { requires: ["InvLedger", "Receipt"] }),
      makeModule("Receipt", { requires: ["InvLedger", "ResLedger"] }),
      makeModule("ResLedger", { requires: ["InvLedger"] }),
      makeModule("InventoryDashboard", { domain: "retail", requires: ["Inventory"] }),
      makeModule("InventoryDashboardExport", { domain: "retail", requires: ["InventoryDashboard"] }),
      makeModule("OptionalModule", { active: false }),
      makeModule("SalesOrder", { domain: "sales", path: "vendor/mycompany/src/main/lsfusion/sales/orders/SalesOrder.lsf" }),
      makeModule("Invoice", { domain: "invoicing", path: "vendor/mycompany/src/main/lsfusion/invoicing/invoices/Invoice.lsf" }),
      makeModule("Bill", { domain: "invoicing", path: "vendor/mycompany/src/main/lsfusion/invoicing/bills/Bill.lsf" }),
      makeModule("Pos", { domain: "retail", path: "vendor/mycompany/src/main/lsfusion/retail/pos/Pos.lsf" }),
      makeModule("Partner", { domain: "masterdata", path: "vendor/mycompany/src/main/lsfusion/masterdata/partners/Partner.lsf" }),
      makeModule("PurchaseOrderReceipt", { domain: "purchase", path: "vendor/mycompany/src/main/lsfusion/purchase/inventory/receipts/orders/PurchaseOrderReceipt.lsf" }),
      makeModule("PurchaseOrder", { domain: "purchase", path: "vendor/mycompany/src/main/lsfusion/purchase/orders/PurchaseOrder.lsf" }),
      makeModule("Bom", { domain: "manufacturing", path: "vendor/mycompany/src/main/lsfusion/manufacturing/bom/Bom.lsf" }),
      makeModule("ManufacturingOrder", { domain: "manufacturing", path: "vendor/mycompany/src/main/lsfusion/manufacturing/orders/ManufacturingOrder.lsf" }),
      makeModule("WorkCenter", { domain: "manufacturing", path: "vendor/mycompany/src/main/lsfusion/manufacturing/workOrders/WorkCenter.lsf" }),
      makeModule("WorkOrder", { domain: "manufacturing", path: "vendor/mycompany/src/main/lsfusion/manufacturing/workOrders/WorkOrder.lsf" }),
      makeModule("Project", { domain: "projectManagement", path: "vendor/mycompany/src/main/lsfusion/projectManagement/projects/Project.lsf" }),
      makeModule("ProjectAssignment", { domain: "projectManagement", path: "vendor/mycompany/src/main/lsfusion/projectManagement/projects/ProjectAssignment.lsf" }),
      makeModule("TimeEntry", { domain: "projectManagement", path: "vendor/mycompany/src/main/lsfusion/projectManagement/timeEntries/TimeEntry.lsf" }),
      makeModule("ProjectTimeEntry", { domain: "projectManagement", path: "vendor/mycompany/src/main/lsfusion/projectManagement/projects/timeentries/ProjectTimeEntry.lsf" }),
      makeModule("ProjectManufacturingOrder", { domain: "projectManagement", path: "vendor/mycompany/src/main/lsfusion/projectManagement/manufacturing/orders/ProjectManufacturingOrder.lsf" }),
      makeModule("ProjectManufacturingOrderTimeEntry", { domain: "projectManagement", path: "vendor/mycompany/src/main/lsfusion/projectManagement/manufacturing/orders/ProjectManufacturingOrderTimeEntry.lsf" }),
    ],
  },
  lsFusion: { modules: [] },
  rubrovaExtensions: { modules: [] },
};

test("resuelve un módulo por nombre MODULE exacto y devuelve su dossier principal", () => {
  const route = resolveModuleIntegrationRoute(fixtureCatalog, "InvLedger");
  assert.equal(route.found, true);
  assert.equal(route.moduleName, "InvLedger");
  assert.equal(route.product, "MyCompany 6.2");
  assert.equal(route.domain, "inventory");
  assert.equal(route.guide.path, "docs/platform-audit/MYCOMPANY_6_2_INVENTORY_LEDGER_MAP.md");
  assert.equal(route.sourceCommit, "mycompany-sha");
  assert.equal(route.passport.path, "docs/platform-audit/modules/InvLedger.md");
});

test("identifica REQUIRE directos y consumidores directos sin confundirlos", () => {
  const route = resolveModuleIntegrationRoute(fixtureCatalog, "InvLedger");
  assert.deepEqual(route.requires, ["Product", "Location"]);
  assert.deepEqual(route.requireDetails.map(item => item.path), [
    "vendor/mycompany/src/main/lsfusion/masterdata/items/products/Product.lsf",
    "vendor/mycompany/src/main/lsfusion/inventory/locations/Location.lsf",
  ]);
  assert.deepEqual(route.consumers.map(item => item.moduleName), ["Inventory", "Receipt", "ResLedger"]);
  assert.ok(route.consumers.every(item => item.path.endsWith(".lsf")));
});

test("calcula dependencias y consumidores transitivos con profundidad mínima", () => {
  const route = resolveModuleIntegrationRoute(fixtureCatalog, "InvLedger");
  const requirements = route.transitiveRequires.map(item => [item.moduleName, item.depth]);
  assert.deepEqual(requirements, [["Location", 1], ["Product", 1], ["Item", 2]]);

  const consumers = route.transitiveConsumers.map(item => [item.moduleName, item.depth]);
  assert.deepEqual(consumers, [
    ["Inventory", 1],
    ["Receipt", 1],
    ["ResLedger", 1],
    ["InventoryDashboard", 2],
    ["InventoryDashboardExport", 3],
  ]);
});

test("el recorrido transitivo tolera ciclos y no vuelve a incluir el módulo inicial", () => {
  const cyclicCatalog = {
    sources: fixtureCatalog.sources,
    myCompany: {
      modules: [
        makeModule("CycleA", { requires: ["CycleB"] }),
        makeModule("CycleB", { requires: ["CycleA"] }),
      ],
    },
    lsFusion: { modules: [] },
    rubrovaExtensions: { modules: [] },
  };
  const route = resolveModuleIntegrationRoute(cyclicCatalog, "CycleA");
  assert.deepEqual(route.transitiveRequires.map(item => item.moduleName), ["CycleB"]);
  assert.deepEqual(route.transitiveConsumers.map(item => item.moduleName), ["CycleB"]);
});

test("no elige arbitrariamente un módulo cuando REQUIRE tiene más de un candidato", () => {
  const ambiguousCatalog = {
    sources: fixtureCatalog.sources,
    myCompany: {
      modules: [
        makeModule("Caller", { requires: ["SharedModule"] }),
        makeModule("SharedModule"),
      ],
    },
    lsFusion: {
      modules: [
        makeModule("SharedModule", {
          path: "vendor/platform/src/main/lsfusion/SharedModule.lsf",
        }),
      ],
    },
    rubrovaExtensions: { modules: [] },
  };
  const route = resolveModuleIntegrationRoute(ambiguousCatalog, "Caller");
  assert.equal(route.requireDetails[0].ambiguous, true);
  assert.equal(route.requireDetails[0].candidates.length, 2);
  assert.deepEqual(route.transitiveRequires, []);
  assert.equal(route.ambiguousTransitiveRequires[0].moduleName, "SharedModule");
});

test("informa dependencias transitivas que no existen en los snapshots", () => {
  const missingCatalog = {
    sources: fixtureCatalog.sources,
    myCompany: { modules: [makeModule("ModuleWithGap", { requires: ["MissingDependency"] })] },
    lsFusion: { modules: [] },
    rubrovaExtensions: { modules: [] },
  };
  const route = resolveModuleIntegrationRoute(missingCatalog, "ModuleWithGap");
  assert.deepEqual(route.transitiveRequires, []);
  assert.deepEqual(route.unresolvedTransitiveRequires, [
    { moduleName: "MissingDependency", requiredBy: "ModuleWithGap", depth: 1 },
  ]);
});

test("permite solicitar salida JSON sin mezclar texto de presentación", () => {
  const route = resolveModuleIntegrationRoute(fixtureCatalog, "InvLedger");
  const parsed = JSON.parse(renderModuleIntegrationRouteJson(route));
  assert.equal(parsed.moduleName, "InvLedger");
  assert.equal(parsed.transitiveConsumers[0].moduleName, "Inventory");
  assert.equal(parsed.transitiveConsumers[0].depth, 1);
  assert.equal(parseArgs(["--module", "InvLedger", "--json"]).json, true);
  assert.equal(parseArgs(["-m", "InvLedger"]).moduleName, "InvLedger");
});

test("resuelve también el nombre exacto del archivo fuente", () => {
  const route = resolveModuleIntegrationRoute(fixtureCatalog, "SalesOrder.lsf");
  assert.equal(route.found, true);
  assert.equal(route.moduleName, "SalesOrder");
  assert.equal(route.guide.path, "docs/platform-audit/MYCOMPANY_6_2_SALES_PRICING_LEDGER_MAP.md");
});

test("resuelve el nombre base y el nombre de archivo LSF", () => {
  const route = resolveModuleIntegrationRoute(fixtureCatalog, "SalesOrder.lsf");
  assert.equal(route.found, true);
  assert.equal(route.moduleName, "SalesOrder");
});

test("envía utilidades y módulos regionales a sus dossiers específicos", () => {
  const utility = resolveModuleIntegrationRoute(fixtureCatalog, "GeoUtils");
  const regional = resolveModuleIntegrationRoute(fixtureCatalog, "RegionalTax");
  assert.equal(utility.guide.path, "docs/platform-audit/MYCOMPANY_6_2_UTILITY_MODULES.md");
  assert.equal(regional.guide.path, "docs/platform-audit/MYCOMPANY_6_2_REGIONAL_MODULES.md");
});

test("un módulo sin pasaporte individual lo declara y conserva el dossier de dominio", () => {
  const route = resolveModuleIntegrationRoute(fixtureCatalog, "PurchaseOrderReceipt");
  assert.equal(route.found, true);
  assert.equal(route.passport, null);
  assert.equal(route.guide.path, "docs/platform-audit/MYCOMPANY_6_2_PURCHASE_REPLENISHMENT_MAP.md");
  assert.ok(route.related.some(item => item.path === "docs/platform-audit/MODULE_INTEGRATION_PASSPORT_TEMPLATE.md"));
});

test("prioriza pasaportes de compra, facturación, POS y entidades maestras", () => {
  const expected = {
    PurchaseOrder: "docs/platform-audit/modules/PurchaseOrder.md",
    Invoice: "docs/platform-audit/modules/Invoice.md",
    Bill: "docs/platform-audit/modules/Bill.md",
    Pos: "docs/platform-audit/modules/Pos.md",
    Product: "docs/platform-audit/modules/Product.md",
    Partner: "docs/platform-audit/modules/Partner.md",
  };
  for (const [moduleName, passportPath] of Object.entries(expected)) {
    const route = resolveModuleIntegrationRoute(fixtureCatalog, moduleName);
    assert.equal(route.found, true);
    assert.equal(route.passport.path, passportPath);
  }
});

test("prioriza fichas individuales de fabricación y proyectos integrados", () => {
  const expected = {
    Bom: "docs/platform-audit/modules/Bom.md",
    ManufacturingOrder: "docs/platform-audit/modules/ManufacturingOrder.md",
    WorkCenter: "docs/platform-audit/modules/WorkCenter.md",
    WorkOrder: "docs/platform-audit/modules/WorkOrder.md",
    Project: "docs/platform-audit/modules/Project.md",
    ProjectAssignment: "docs/platform-audit/modules/ProjectAssignment.md",
    TimeEntry: "docs/platform-audit/modules/TimeEntry.md",
    ProjectTimeEntry: "docs/platform-audit/modules/ProjectTimeEntry.md",
    ProjectManufacturingOrder: "docs/platform-audit/modules/ProjectManufacturingOrder.md",
    ProjectManufacturingOrderTimeEntry: "docs/platform-audit/modules/ProjectManufacturingOrderTimeEntry.md",
  };
  for (const [moduleName, passportPath] of Object.entries(expected)) {
    const route = resolveModuleIntegrationRoute(fixtureCatalog, moduleName);
    assert.equal(route.found, true);
    assert.equal(route.passport.path, passportPath);
    assert.equal(route.guide.path, "docs/platform-audit/MYCOMPANY_6_2_MANUFACTURING_PROJECTS_INTEGRATION.md");
    assert.equal(route.mandatoryIntegration.required, true);
    assert.match(route.mandatoryIntegration.rules.join(" "), /no introducir HTTP o microservicios internos/);
    assert.match(route.mandatoryIntegration.rules.join(" "), /nunca escribirlos directamente/);
  }
});

test("advierte cuando un módulo existe pero queda fuera del cierre actual", () => {
  const route = resolveModuleIntegrationRoute(fixtureCatalog, "OptionalModule");
  assert.equal(route.found, true);
  assert.match(route.compositionState, /FUERA DEL CIERRE/);
});

test("devuelve sugerencias cuando no hay coincidencia exacta", () => {
  const route = resolveModuleIntegrationRoute(fixtureCatalog, "InvLed");
  assert.equal(route.found, false);
  assert.equal(route.suggestions[0].moduleName, "InvLedger");
});

test("renderiza una ruta que separa primera lectura, dependencias y límites del parser", () => {
  const route = resolveModuleIntegrationRoute(fixtureCatalog, "InvLedger");
  const output = renderModuleIntegrationRoute(route);
  assert.match(output, /Primera lectura obligatoria/);
  const manufacturingOutput = renderModuleIntegrationRoute(
    resolveModuleIntegrationRoute(fixtureCatalog, "ManufacturingOrder"),
  );
  assert.doesNotMatch(output, /Contrato obligatorio de integración/);
  assert.match(manufacturingOutput, /Contrato obligatorio de integración/);
  assert.match(manufacturingOutput, /no introducir HTTP o microservicios internos/);
  assert.match(output, /Ficha individual/);
  assert.match(output, /modules\/InvLedger\.md/);
  assert.match(output, /Datos maestros y relaciones transversales/);
  assert.match(output, /REQUIRE directos/);
  assert.match(output, /Consumidores directos detectados/);
  assert.match(output, /no sustituye una ficha de integración aceptada/i);
});

test("el preflight platform consulta módulos críticos de fabricación y proyectos", () => {
  const preflight = read("scripts/platform/local-preflight.sh");
  for (const moduleName of [
    "Bom",
    "ManufacturingOrder",
    "WorkCenter",
    "WorkOrder",
    "Project",
    "ProjectAssignment",
    "TimeEntry",
    "ProjectTimeEntry",
    "ProjectManufacturingOrder",
    "ProjectManufacturingOrderTimeEntry",
  ]) {
    assert.ok(preflight.includes(`--module ${moduleName}`), `El preflight no consulta ${moduleName}`);
  }
});

test("el directorio manual enlaza archivos LSF existentes y módulos del catálogo de 6.2", () => {
  const directoryPath = "docs/platform-audit/MYCOMPANY_6_2_MODULE_INTEGRATION_DIRECTORY.md";
  const directory = read(directoryPath);
  const vendorPaths = [...directory.matchAll(/\]\(\.\.\/\.\.\/(vendor\/[^)]+)\)/g)]
    .map(match => match[1]);
  assert.ok(vendorPaths.length >= 70, "El directorio debe contener rutas fuente exactas de los módulos prioritarios.");

  for (const sourcePath of vendorPaths) {
    assert.ok(existsSync(path.join(root, sourcePath)), `Ruta LSF inexistente en el directorio: ${sourcePath}`);
  }

  const linkedFiles = new Set(vendorPaths);
  for (const expected of [
    "vendor/mycompany/src/main/lsfusion/inventory/ledgers/inv/InvLedger.lsf",
    "vendor/mycompany/src/main/lsfusion/inventory/ledgers/res/ResLedger.lsf",
    "vendor/mycompany/src/main/lsfusion/inventory/ledgers/cost/CostLedger.lsf",
    "vendor/mycompany/src/main/lsfusion/inventory/receipts/Receipt.lsf",
    "vendor/mycompany/src/main/lsfusion/inventory/shipments/Shipment.lsf",
    "vendor/mycompany/src/main/lsfusion/sales/orders/SalesOrder.lsf",
    "vendor/mycompany/src/main/lsfusion/purchase/orders/PurchaseOrder.lsf",
    "vendor/mycompany/src/main/lsfusion/invoicing/ledgers/Debt.lsf",
    "vendor/mycompany/src/main/lsfusion/retail/sessions/Session.lsf",
    "vendor/mycompany/src/main/lsfusion/masterdata/partners/Partner.lsf",
  ]) {
    assert.ok(linkedFiles.has(expected), `Falta una ruta de módulo crítico: ${expected}`);
  }
});

test("cada módulo con pasaporte individual enlaza su ficha directamente en la fila rápida", () => {
  const directory = read("docs/platform-audit/MYCOMPANY_6_2_MODULE_INTEGRATION_DIRECTORY.md");
  const names = ["InvLedger", "ResLedger", "CostLedger", "Receipt", "SalesOrder", "Session", "PurchaseOrder", "Invoice", "Bill", "Pos", "Product", "Partner"];
  for (const name of names) {
    const row = directory.split("\n").find(line => line.startsWith("| `" + name + "` |"));
    assert.ok(row, "No existe ruta rápida para " + name);
    assert.ok(row.includes("[Ficha " + name + "](modules/" + name + ".md)"), "La fila de " + name + " no enlaza su pasaporte individual");
  }
});

test("los nombres del directorio coinciden con MODULE declarado en cada archivo LSF", () => {
  const directory = read("docs/platform-audit/MYCOMPANY_6_2_MODULE_INTEGRATION_DIRECTORY.md");
  const catalog = buildSourceCatalog();
  const byPath = new Map([
    ...catalog.myCompany.modules,
    ...catalog.lsFusion.modules,
    ...catalog.rubrovaExtensions.modules,
  ].map(module => [module.path, module]));

  const rows = [...directory.matchAll(/^\| `([^`]+)` \| \[[^\]]+\]\(\.\.\/\.\.\/(vendor\/[^)]+\.lsf)\)/gm)];
  assert.ok(rows.length >= 65, "El directorio debe enrutar al menos 65 módulos con nombre y fuente exactos.");

  for (const [, declaredName, sourcePath] of rows) {
    const module = byPath.get(sourcePath);
    assert.ok(module, `El archivo no está en el catálogo LSF: ${sourcePath}`);
    assert.equal(
      module.moduleName,
      declaredName,
      `El directorio debe usar MODULE declarado, no el nombre del archivo: ${sourcePath}`,
    );
  }
});

test("la plantilla de ficha conserva los controles mínimos de integración y aceptación", () => {
  const template = read("docs/platform-audit/MODULE_INTEGRATION_PASSPORT_TEMPLATE.md");
  for (const moduleName of ["InvLedger", "ResLedger", "CostLedger", "Receipt", "SalesOrder", "Session", "PurchaseOrder", "Invoice", "Bill", "Pos", "Product", "Partner"]) {
    const passportPath = `docs/platform-audit/modules/${moduleName}.md`;
    assert.ok(existsSync(path.join(root, passportPath)), `Falta ficha individual de ${moduleName}`);
    assert.ok(read(passportPath).includes(`Ficha de integración — ${moduleName}`));
  }
  for (const marker of [
    "Modelo de datos y relaciones",
    "Contratos de integración y comunicación",
    "Estados, transacciones y efectos secundarios",
    "Seguridad, permisos y auditoría",
    "Ledgers y efectos",
    "Matriz de pruebas y evidencia",
    "Decisión reuse-first",
    "No inferir",
  ]) {
    assert.ok(template.toLowerCase().includes(marker.toLowerCase()), `La ficha no cubre: ${marker}`);
  }
});
