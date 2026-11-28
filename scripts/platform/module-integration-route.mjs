#!/usr/bin/env node
/**
 * Busca un MODULE exacto en los snapshots fijados y devuelve la ruta de
 * integración: fuente, REQUIRE, consumidores, dossier y lecturas cruzadas.
 * El catálogo es estructural; no sustituye la ficha funcional ni runtime.
 */
import path from "node:path";
import { pathToFileURL } from "node:url";
import { buildSourceCatalog } from "./audit-lsf-source.mjs";

export const DOMAIN_GUIDES = {
  inventory: {
    path: "docs/platform-audit/MYCOMPANY_6_2_INVENTORY_LEDGER_MAP.md",
    title: "Inventario, reservas y costos",
    coverage: "Análisis de fuentes parcial; pruebas de runtime y conciliación pendientes.",
  },
  retail: {
    path: "docs/platform-audit/MYCOMPANY_6_2_RETAIL_POS_SESSIONS_MAP.md",
    title: "Retail, POS, sesiones y devoluciones",
    coverage: "Lectura de las 30 fuentes LSF retail; aceptación de runtime, hardware/fiscal y conciliación pendientes.",
  },
  sales: {
    path: "docs/platform-audit/MYCOMPANY_6_2_SALES_PRICING_LEDGER_MAP.md",
    title: "Ventas, precios y ledger comercial",
    coverage: "Análisis profundo parcial; pruebas de runtime y conciliación pendientes.",
  },
  purchase: {
    path: "docs/platform-audit/MYCOMPANY_6_2_PURCHASE_REPLENISHMENT_MAP.md",
    title: "Compras, proveedores y reposición",
    coverage: "Lectura profunda parcial; pruebas de runtime y conciliación pendientes.",
  },
  invoicing: {
    path: "docs/platform-audit/MYCOMPANY_6_2_INVOICING_LEDGER_MAP.md",
    title: "Facturación, deuda, pagos y cuentas",
    coverage: "Fuentes de ledgers, documentos/pagos e impuestos revisadas; runtime y conciliación pendientes.",
  },
  masterdata: {
    path: "docs/platform-audit/MYCOMPANY_6_2_MASTERDATA_RELATIONSHIPS_MAP.md",
    title: "Datos maestros y relaciones transversales",
    coverage: "84 módulos inventariados y fuentes principales leídas; runtime, extensiones y adecuación argentina pendientes.",
  },
  crm: {
    path: "docs/platform-audit/MYCOMPANY_6_2_CRM_LEADS_MAP.md",
    title: "CRM y leads",
    coverage: "Mapa de dominio disponible; ciclos, permisos y pruebas de runtime parciales.",
  },
  humanResources: {
    path: "docs/platform-audit/MYCOMPANY_6_2_HR_ATTENDANCE_PAYROLL_MAP.md",
    title: "RR. HH., asistencia y payroll",
    coverage: "Mapa de dominio disponible; flujos y aceptación pendientes.",
  },
  utils: {
    path: "docs/platform-audit/MYCOMPANY_6_2_UTILITY_MODULES.md",
    title: "Utilidades compartidas",
    coverage: "Lectura inicial de 21 módulos; runtime y validación de cada integración pendientes.",
  },
  region: {
    path: "docs/platform-audit/MYCOMPANY_6_2_REGIONAL_MODULES.md",
    title: "Módulos regionales",
    coverage: "Inventario inicial; revisión individual y adecuación argentina pendientes.",
  },
  projectManagement: {
    path: "docs/platform-audit/MYCOMPANY_6_2_PROJECT_MANAGEMENT_INTEGRATIONS_MAP.md",
    title: "Proyectos, tareas e integraciones",
    coverage: "Mapa de dominio disponible; flujos y aceptación pendientes.",
  },
  fleet: {
    path: "docs/platform-audit/MYCOMPANY_6_2_FLEET_VEHICLE_COSTS_MAP.md",
    title: "Flota, vehículos y costos",
    coverage: "Mapa de dominio disponible; flujos y aceptación pendientes.",
  },
  manufacturing: {
    path: "docs/platform-audit/MYCOMPANY_6_2_FUNCTIONAL_MAP.md",
    title: "Mapa funcional general — dominio Manufacturing",
    coverage: "No existe todavía un dossier de integración de fabricación dedicado; fuente E2E pendiente.",
  },
  "(raíz)": {
    path: "docs/platform-audit/MYCOMPANY_6_2_FUNCTIONAL_MAP.md",
    title: "Mapa funcional general y composición de módulos",
    coverage: "Dossier de entrada; consultar composición y mapa de dominio.",
  },
};

const LSFUSION_GUIDE = {
  path: "docs/platform-audit/LSFUSION_6_2_CAPABILITY_MAP.md",
  title: "Capacidades de lsFusion 6.2",
  coverage: "Relevamiento incompleto; puerta 9.7 abierta.",
};

const RUBROVA_GUIDE = {
  path: "docs/ARCHITECTURE.md",
  title: "Arquitectura y extensiones Rubrova",
  coverage: "Consultar también Module Composition y Source Ownership.",
};

const PASSPORT_OVERRIDES = {
  Inventory: "Composición del dominio; no es propietario único de todos los datos que requiere.",
  InvLedger: "§1.1 — movimientos físicos por producto/ubicación; no equivale a reserva ni costo.",
  ResLedger: "§1.2 — reserva, esperado y disponible; respetar signo y skipAvailable.",
  CostLedger: "§1.3 — valoración/costo; FIFO, AVCO y costo planificado tienen reglas distintas.",
  Receipt: "§2.1 — documento de recepción; seguir sus módulos de estado y ledgers.",
  ReceiptReady: "§2.2 — transición a listo y esperado/reserva.",
  ReceiptDone: "§2.3 — cantidad efectivamente recibida.",
  ReceiptInv: "§2.3 — contabilización del movimiento físico de recepción.",
  ReceiptRes: "§2.2 — reserva negativa de recepción/esperado.",
  ReceiptCost: "§2.5 — costo derivado de la recepción.",
  ReceiptPutAway: "§2.4 — distribución interna; evitar doble conteo entre ubicación principal y destino.",
  Shipment: "§3.1 — documento de despacho/traslado.",
  ShipmentReady: "§3.2 — disponibilidad y reserva.",
  ShipmentDone: "§3.4 — ejecución/cantidad efectiva.",
  ShipmentInv: "§3.4 — movimiento físico de salida/traslado.",
  ShipmentRes: "§3.2 — reserva asociada al despacho.",
  ShipmentAcceptance: "§3.5 — aceptación de movimiento en destino y permisos.",
  Adjustment: "§4 — conteo, diferencia y ajuste.",
  AdjustmentDone: "§4 — confirmación del ajuste y efecto físico.",
  Scrap: "§§1 y 5 — merma/baja; ficha E2E todavía pendiente.",
  Location: "§§1.1, 1.3 y 5 — jerarquía, acceso y ubicación de costo.",
  SalesOrder: "§2 — pedido de venta y documento origen.",
  SalesOrderConfirmed: "§2.2 — confirmación y restricciones.",
  SalesOrderCanceled: "§2.2 — cancelación y dependencias de documentos derivados.",
  SalesOrderShipment: "§2.3 — pedido a despacho, reserva y parcialidad.",
  SalesOrderInvoice: "§2.4 — pedido a factura y facturación parcial.",
  SalesOrderPurchase: "§2.5 — compra vinculada a demanda de venta.",
  SalesOrderManufacturing: "§2.6 — pedido a fabricación/BOM.",
  PurchaseOrder: "§2 — pedido de compra y líneas.",
  PurchaseOrderReceipt: "§3 — pedido a recepción.",
  PurchaseOrderBill: "§4 — pedido a factura de proveedor.",
  PurchaseOrderShipmentAuto: "§6 — reposición automática nativa por proveedor/periodo.",
  Invoice: "§2.1 — factura de venta y su relación con deuda/pagos.",
  Bill: "§2.2 — factura de proveedor y su relación con costo/deuda/pagos.",
  Debt: "§3 — ledger de deuda e imputaciones parciales.",
  Payment: "§§4–5 — ledger de cuentas y movimientos de pago.",
  IncomingPayment: "§5.1 — cobro entrante y aplicación.",
  OutgoingPayment: "§5.2 — pago/salida y aplicación.",
  Pos: "§2 — caja lógica y configuración de empresa/computadora.",
  PosPaymentMethod: "§2 — medios habilitados y cuentas por caja.",
  PaymentMethod: "§4 — tipo de cobro entrante y tipo de pago saliente para reintegros.",
  Session: "§3 — turno, apertura/cierre y hooks.",
  SessionInvoice: "§3 — relación sesión↔factura/nota y totales.",
  SessionPayment: "§4 — conciliación de importes por medio.",
  SessionShipment: "§3 — asociación de despachos con sesión.",
  PosDashboard: "§6 — pantalla operativa y contexto de caja/sesión.",
  PosDashboardPayment: "§4 — cobro mixto, vuelto y generación de cobros.",
  PosDashboardReturn: "§8 — devolución, nota de crédito y reintegro.",
  Product: "Datos maestros §§4–6 — producto físico, unidades, variantes y barcode.",
  Item: "Datos maestros §§4–6 — maestro abstracto de artículo.",
  Partner: "Datos maestros §§2–3 — identidad común y especializaciones.",
  Company: "Datos maestros §3 — empresa propia/titular de documentos y cuentas.",
  Employee: "Datos maestros §3 — empleado/usuario y relaciones.",
  ProductSku: "Datos maestros §6 + inventario §5 — SKU, unidades y códigos.",
  Bom: "Manufacturing: mapa funcional y ventas §2.6; análisis E2E dedicado pendiente.",
  ManufacturingOrder: "Manufacturing: mapa funcional, ventas §2.6 y compras §7; análisis E2E dedicado pendiente.",
  WorkOrder: "Manufacturing: mapa funcional; análisis de operaciones/tiempos/consumo pendiente.",
};

const UTILITY_MODULES = new Set([
  "Audio", "BarCodeReader", "Call", "Color", "Comments", "Crypto", "DateUtils",
  "Doc", "DocTemplate", "Documentation", "EmailTemplate", "EmailUtils",
  "FileUtils", "GeoUtils", "Initial", "Input", "MarkdownViewer", "MetaNumerator",
  "NumericUtils", "ObjectUtils", "Selection",
]);

function sourceCollections(catalog) {
  return [
    { product: "MyCompany 6.2", key: "MyCompany", source: catalog.sources?.myCompany, modules: catalog.myCompany?.modules || [], root: "RubrovaCustom" },
    { product: "lsFusion 6.2", key: "lsFusion", source: catalog.sources?.lsFusion, modules: catalog.lsFusion?.modules || [], root: "RubrovaCustom" },
    { product: "Extensiones Rubrova", key: "Rubrova", source: null, modules: catalog.rubrovaExtensions?.modules || [], root: "RubrovaCustom" },
  ];
}

function flattenModules(catalog) {
  return sourceCollections(catalog).flatMap(collection =>
    collection.modules.map(module => ({ ...module, product: collection.product, source: collection.source })),
  );
}

function domainGuideFor(module) {
  if (module.product === "lsFusion 6.2") return LSFUSION_GUIDE;
  if (module.product === "Extensiones Rubrova") return RUBROVA_GUIDE;
  return DOMAIN_GUIDES[module.domain] || DOMAIN_GUIDES["(raíz)"];
}

function declarationSummary(module) {
  const counts = module.counts || {};
  const declarations = module.declarations || {};
  const keys = [
    ["clases", "classes"],
    ["propiedades", "properties"],
    ["acciones", "actions"],
    ["formularios", "forms"],
    ["restricciones", "constraints"],
    ["eventos WHEN", "whenEvents"],
    ["eventos ON", "onEvents"],
    ["anotaciones API", "apiAnnotations"],
  ];
  return keys.map(([label, key]) => ({
    label,
    count: counts[key] || 0,
    names: (declarations[key] || []).map(item => item.name || `línea ${item.line}`).filter(Boolean),
  }));
}

export function resolveModuleIntegrationRoute(catalog, query) {
  const value = String(query || "").trim();
  if (!value) throw new Error("Indicar un módulo con --module NombreExacto.");

  const allModules = flattenModules(catalog);
  const normalized = value.toLowerCase();
  const exact = allModules.filter(module =>
    String(module.moduleName || "").toLowerCase() === normalized ||
    path.basename(module.path || "", ".lsf").toLowerCase() === normalized ||
    String(module.path || "").toLowerCase() === normalized
  );

  if (exact.length === 0) {
    const suggestions = allModules
      .filter(module => String(module.moduleName || "").toLowerCase().includes(normalized))
      .slice(0, 12)
      .map(module => ({ moduleName: module.moduleName, path: module.path, product: module.product }));
    return { found: false, query: value, suggestions };
  }
  if (exact.length > 1) {
    return {
      found: false,
      ambiguous: true,
      query: value,
      matches: exact.map(module => ({ moduleName: module.moduleName, path: module.path, product: module.product })),
    };
  }

  const module = exact[0];
  const guide = domainGuideFor(module);
  const consumers = allModules
    .filter(candidate => (candidate.requires || []).includes(module.moduleName))
    .map(candidate => ({ moduleName: candidate.moduleName, path: candidate.path, product: candidate.product }))
    .sort((a, b) => a.moduleName.localeCompare(b.moduleName, "en"));

  const utilities = (module.requires || []).filter(name => UTILITY_MODULES.has(name));
  const related = [
    { path: guide.path, title: guide.title, reason: "Dossier funcional principal del dominio/tema." },
  ];
  if (module.product === "MyCompany 6.2" && module.domain !== "masterdata") {
    related.push({
      path: "docs/platform-audit/MYCOMPANY_6_2_MASTERDATA_RELATIONSHIPS_MAP.md",
      title: "Datos maestros y relaciones transversales",
      reason: "Obligatorio cuando el módulo maneja producto, socio, empresa, empleado, unidad, ubicación o identidad.",
    });
  }
  if (utilities.length > 0 || module.product === "MyCompany 6.2") {
    related.push({
      path: "docs/platform-audit/MYCOMPANY_6_2_UTILITY_MODULES.md",
      title: "Utilidades compartidas",
      reason: utilities.length > 0 ? `REQUIRE incluye utilidades compartidas: ${utilities.join(", ")}.` : "Revisar macros y mecanismos transversales antes de crear una alternativa propia.",
    });
  }
  related.push({
    path: "docs/platform-audit/LSFUSION_6_2_CAPABILITY_MAP.md",
    title: "Capacidades lsFusion 6.2",
    reason: "Obligatorio si se cambia un hook, formulario, acción, evento, sesión, transacción o API.",
  });
  related.push({
    path: "docs/ENGINEERING_MASTER.md#b-integration",
    title: "Guía de integración lsFusion/MyCompany 6.2",
    reason: "Contratos de módulos, extensión, sesiones, transacciones y frontera de autoridad.",
  });

  const passportNote = PASSPORT_OVERRIDES[module.moduleName] || null;
  const inApplication = module.reachableFromApplicationRoot === true;
  const compositionState = inApplication
    ? "INCLUIDO EN EL CIERRE DE RubrovaCustom"
    : "FUERA DEL CIERRE DE RubrovaCustom — NO ASUMIR ACTIVO";

  return {
    found: true,
    moduleName: module.moduleName,
    product: module.product,
    path: module.path,
    namespace: module.namespace || null,
    domain: module.domain,
    compositionState,
    sourceCommit: module.source?.commit || null,
    sourceTag: module.source?.tag || null,
    requires: module.requires || [],
    consumers,
    guide,
    passportNote,
    declarations: declarationSummary(module),
    related,
    parserLimits: module.counts?.actionDeclarationsAreHeuristic
      ? "Los conteos/nombres se extraen estáticamente; detección de acciones heurística, sin expansión META/macros. No demuestra visibilidad ni semántica runtime."
      : "El catálogo es estructural y no demuestra visibilidad, semántica ni ejecución runtime.",
  };
}

export function renderModuleIntegrationRoute(route) {
  if (!route.found) {
    const lines = [`# No se encontró el módulo: ${route.query}`, ""];
    if (route.ambiguous) {
      lines.push("La consulta coincide con más de un módulo. Usar el nombre completo o la ruta exacta.", "");
      for (const match of route.matches) lines.push(`- ${match.product}: \`${match.moduleName}\` — \`${match.path}\``);
    } else {
      lines.push("No hay coincidencia exacta en los snapshots. Posibles nombres:", "");
      for (const match of route.suggestions || []) lines.push(`- \`${match.moduleName}\` — \`${match.path}\``);
      lines.push("", "No asumir que un nombre de archivo es el nombre del MODULE. Consultar el encabezado `MODULE` en la fuente.");
    }
    return lines.join("\n");
  }

  const lines = [
    `# Ruta de integración: ${route.moduleName}`,
    "",
    `- **Origen:** ${route.product}`,
    `- **Estado:** ${route.compositionState}`,
    `- **Dominio de archivo:** ${route.domain}`,
    `- **Namespace:** ${route.namespace || "(sin namespace declarado)"}`,
    `- **Fuente exacta:** \`${route.path}\``,
    `- **Commit de origen:** ${route.sourceCommit || "(ver source-lock)" }`,
    `- **REQUIRE directos (${route.requires.length}):** ${route.requires.length ? route.requires.map(name => \`${name}\`).join(", ") : "(ninguno)" }`,
    `- **Consumidores directos detectados (${route.consumers.length}):** ${route.consumers.length ? route.consumers.map(item => \`${item.moduleName}\`).join(", ") : "(ninguno en el catálogo estructural)" }`,
    "",
    "## Primera lectura obligatoria",
    `- **Dossier primario:** ${route.guide.path} — ${route.guide.title}`,
    `- **Cobertura conocida:** ${route.guide.coverage}`,
    route.passportNote ? `- **Nota de integración:** ${route.passportNote}` : "- **Nota de integración:** no hay override funcional específico registrado; seguir el dossier de dominio y completar la ficha del módulo si el cambio lo requiere.",
    "",
    "## Siguiente lectura",
    ...route.related.map(item => `- **${item.title}:** ${item.path} — ${item.reason}`),
    "",
    "## Declaraciones detectadas en fuente",
    ...route.declarations.map(item => `- **${item.label}:** ${item.count}${item.names.length ? ` — ${item.names.join(", ")}` : ""}`),
    "",
    "## Límite de la salida",
    route.parserLimits,
    "Esta ruta acelera la localización, pero no sustituye una ficha de integración aceptada. Antes de modificar, verificar la implementación exacta, estados, transacciones, permisos, efectos en documentos/ledgers, consumidores y pruebas runtime.",
  ];
  return lines.join("\n");
}

function parseArgs(args) {
  let moduleName = null;
  for (let i = 0; i < args.length; i += 1) {
    if (args[i] === "--module" || args[i] === "-m") {
      moduleName = args[i + 1];
      if (!moduleName) throw new Error("Falta el nombre después de --module.");
      i += 1;
    } else if (args[i] === "--help" || args[i] === "-h") {
      return { help: true };
    } else {
      throw new Error(`Argumento no reconocido: ${args[i]}`);
    }
  }
  if (!moduleName) throw new Error("Uso: node scripts/platform/module-integration-route.mjs --module NombreExacto");
  return { moduleName };
}

export function runModuleRouteCli(args = process.argv.slice(2)) {
  const options = parseArgs(args);
  if (options.help) {
    console.log("Uso: node scripts/platform/module-integration-route.mjs --module NombreExacto");
    console.log("También acepta la ruta exacta o el nombre del archivo .lsf.");
    return;
  }
  const catalog = buildSourceCatalog();
  const route = resolveModuleIntegrationRoute(catalog, options.moduleName);
  console.log(renderModuleIntegrationRoute(route));
  if (!route.found) process.exitCode = 2;
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  try {
    runModuleRouteCli();
  } catch (error) {
    console.error("ERROR: " + (error instanceof Error ? error.message : String(error)));
    process.exitCode = 1;
  }
}
