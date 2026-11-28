import test from "node:test";
import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import {
  resolveModuleIntegrationRoute,
  renderModuleIntegrationRoute,
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
      makeModule("Product", { domain: "masterdata", path: "vendor/mycompany/src/main/lsfusion/masterdata/items/products/Product.lsf" }),
      makeModule("Location", { domain: "inventory", path: "vendor/mycompany/src/main/lsfusion/inventory/locations/Location.lsf" }),
      makeModule("GeoUtils", { domain: "utils", path: "vendor/mycompany/src/main/lsfusion/utils/GeoUtils.lsf" }),
      makeModule("RegionalTax", { domain: "region", path: "vendor/mycompany/src/main/lsfusion/region/RegionalTax.lsf" }),
      makeModule("Inventory", { requires: ["InvLedger", "Receipt"] }),
      makeModule("Receipt", { requires: ["InvLedger", "ResLedger"] }),
      makeModule("ResLedger", { requires: ["InvLedger"] }),
      makeModule("OptionalModule", { active: false }),
      makeModule("SalesOrder", { domain: "sales", path: "vendor/mycompany/src/main/lsfusion/sales/orders/SalesOrder.lsf" }),
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
  const route = resolveModuleIntegrationRoute(fixtureCatalog, "PurchaseOrder");
  assert.equal(route.found, true);
  assert.equal(route.passport, null);
  assert.equal(route.guide.path, "docs/platform-audit/MYCOMPANY_6_2_INVENTORY_LEDGER_MAP.md");
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
  assert.match(output, /Ficha individual/);
  assert.match(output, /modules\/InvLedger\.md/);
  assert.match(output, /Datos maestros y relaciones transversales/);
  assert.match(output, /REQUIRE directos/);
  assert.match(output, /Consumidores directos detectados/);
  assert.match(output, /no sustituye una ficha de integración aceptada/i);
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
  for (const moduleName of ["InvLedger", "ResLedger", "CostLedger", "Receipt", "SalesOrder", "Session"]) {
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
