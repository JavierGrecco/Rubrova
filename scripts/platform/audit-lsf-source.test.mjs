import test from "node:test";
import assert from "node:assert/strict";
import { closureFrom, maskLsfNonCode, parseJavaSource, parseLsfSource, topLevelLsfSource } from "./audit-lsf-source.mjs";

test("identifica encabezado, dependencias y declaraciones del módulo", () => {
  const source = [
    "// MODULE Comentario;",
    "MODULE ComprasDemo;",
    "REQUIRE Base, Proveedores;",
    "NAMESPACE Compras;",
    "CLASS ABSTRACT Pedido 'Pedido';",
    "EXTEND CLASS Pedido { }",
    "FORM pedido 'Pedido';",
    "EXTEND FORM pedido PROPERTIES copiar;",
    "NAVIGATOR {",
    "    FORM pedido;",
    "}",
    "CONSTRAINT proveedor(p) MESSAGE 'Debe elegir proveedor';",
    "WHEN SET(pedido(Pedido p)) DO {",
    "    // acción de ejemplo",
    "}",
    "@@api",
    "pedidoApi() { }",
    "@@noauth",
  ].join("\n");

  const parsed = parseLsfSource(source, "vendor/mycompany/purchase/Demo.lsf");
  assert.equal(parsed.moduleName, "ComprasDemo");
  assert.equal(parsed.namespace, "Compras");
  assert.deepEqual(parsed.requires, ["Base", "Proveedores"]);
  assert.equal(parsed.counts.classes, 1);
  assert.equal(parsed.counts.classExtensions, 1);
  assert.equal(parsed.counts.forms, 1);
  assert.equal(parsed.counts.formExtensions, 1);
  assert.equal(parsed.counts.navigators, 1);
  assert.equal(parsed.counts.constraints, 1);
  assert.equal(parsed.counts.whenEvents, 1);
  assert.equal(parsed.counts.actions, 1);
  assert.equal(parsed.counts.apiAnnotations, 1);
  assert.equal(parsed.counts.noAuthAnnotations, 1);
});

test("detecta propiedades, extensiones de propiedades y acciones", () => {
  const source = [
    "MODULE Declaraciones;",
    "CLASS Pedido;",
    "numero 'Número' = DATA STRING[20] (Pedido);",
    "estado(Pedido p) = name(p);",
    "calcular = ABSTRACT NUMERIC[12,2] (Pedido);",
    "calcular(Pedido p) += precio(p);",
    "confirmar 'Confirmar' (Pedido p) {",
    "    estado(p) <- 'Confirmado';",
    "}",
    "ACTION enviar 'Enviar' (Pedido p) {",
    "    MESSAGE 'Enviado';",
    "}",
    "confirmar (Pedido p) + {",
    "    MESSAGE 'Extensión';",
    "}",
    "GROUP datos 'Datos';",
    "DESIGN pedido {",
    "    caption = 'Pedido';",
    "}",
    "META agregarCampo(tipo)",
    "    campo = DATA tipo ();",
    "END",
  ].join("\n");

  const parsed = parseLsfSource(source);
  assert.equal(parsed.counts.properties, 3);
  assert.equal(parsed.counts.propertyExtensions, 1);
  assert.equal(parsed.counts.actions, 2);
  assert.equal(parsed.counts.actionExtensions, 1);
  assert.equal(parsed.counts.groups, 1);
  assert.equal(parsed.counts.designs, 1);
  assert.equal(parsed.counts.metaStatements, 1);
  assert.equal(parsed.counts.macroExpansionIsNotIncluded, true);
});

test("no cuenta declaraciones dentro de navegación, diseño, acciones ni META", () => {
  const source = [
    "MODULE Bloques;",
    "NAVIGATOR {",
    "    FORM referencia;",
    "}",
    "DESIGN pedido {",
    "    caption = 'Diseño';",
    "}",
    "procesar (Pedido p) {",
    "    interno = DATA STRING (Pedido);",
    "    FORM noEsDeclaracion;",
    "}",
    "META plantilla(tipo)",
    "    generado = DATA tipo ();",
    "END",
    "real = DATA STRING ();",
  ].join("\n");
  const top = topLevelLsfSource(source);
  const parsed = parseLsfSource(source);
  assert.doesNotMatch(top, /FORM referencia/);
  assert.doesNotMatch(top, /interno = DATA/);
  assert.doesNotMatch(top, /generado = DATA/);
  assert.equal(parsed.counts.forms, 0);
  assert.equal(parsed.counts.properties, 1);
  assert.equal(parsed.counts.actions, 1);
  assert.equal(parsed.counts.metaStatements, 1);
});

test("no cuenta declaraciones escondidas en comentarios o literales", () => {
  const source = [
    "MODULE Texto;",
    "NAMESPACE Demo;",
    "/* FORM inventado; */",
    "mensaje = 'CLASS Falso; FORM Mentira;';",
    "// @@api",
    "FORM real;",
  ].join("\n");
  const masked = maskLsfNonCode(source);
  const parsed = parseLsfSource(source);
  assert.match(masked, /MODULE Texto;/);
  assert.equal(parsed.counts.forms, 1);
  assert.equal(parsed.counts.classes, 0);
  assert.equal(parsed.counts.apiAnnotations, 0);
});

test("preserva líneas al enmascarar comentarios y cadenas", () => {
  const source = "MODULE X;\n// comentario\nFORM x;\n/*\n comentario\n*/\nCLASS X;";
  const masked = maskLsfNonCode(source);
  assert.equal(masked.split("\n").length, source.split("\n").length);
  assert.equal(masked.split("\n")[2].trim(), "FORM x;");
  assert.equal(masked.split("\n")[6].trim(), "CLASS X;");
});

test("calcula el cierre de dependencias desde la raíz real de Rubrova", () => {
  const modules = new Map([
    ["RubrovaCustom", { requires: ["MyCompany", "RubrovaExtension"] }],
    ["MyCompany", { requires: ["Ventas", "Inventario"] }],
    ["Ventas", { requires: [] }],
    ["Inventario", { requires: [] }],
    ["RubrovaExtension", { requires: ["Ventas"] }],
  ]);
  const closure = closureFrom("RubrovaCustom", modules);
  assert.deepEqual(closure.moduleNames, [
    "Inventario",
    "MyCompany",
    "RubrovaCustom",
    "RubrovaExtension",
    "Ventas",
  ]);
  assert.deepEqual(closure.unresolvedRequirements, []);
});

test("extrae el paquete y los tipos públicos principales de fuentes Java", () => {
  const java = [
    "package mycompany.utils.crypto;",
    "import java.security.KeyPair;",
    "import java.util.List;",
    "public final class GenerateCSRAction {",
    "}",
  ].join("\n");
  const parsed = parseJavaSource(java, "src/main/java/mycompany/utils/crypto/GenerateCSRAction.java");
  assert.equal(parsed.packageName, "mycompany.utils.crypto");
  assert.equal(parsed.importCount, 2);
  assert.deepEqual(parsed.topLevelTypes.map((type) => [type.kind, type.name]), [
    ["class", "GenerateCSRAction"],
  ]);
});


test("el registro estructural incorpora recursos MyCompany y fuentes Java de plataforma", async () => {
  const { renderModuleRegisterMarkdown } = await import("./audit-lsf-source.mjs");
  const module = {
    moduleName: "ComprasDemo",
    path: "vendor/mycompany/src/main/lsfusion/purchase/Demo.lsf",
    namespace: "Compras",
    requires: ["Base"],
    lineCount: 20,
    reachableFromApplicationRoot: true,
    domain: "purchase",
    counts: { classes: 1, classExtensions: 0, properties: 2, propertyExtensions: 0, actions: 1, actionExtensions: 0, forms: 1, formExtensions: 0, constraints: 0, whenEvents: 0, onEvents: 0, apiAnnotations: 0, navigators: 0 },
    declarations: { classes: [{ name: "Pedido", line: 2 }], properties: [{ name: "numero", line: 4 }, { name: "importe", line: 5 }], actions: [{ name: "confirmar", line: 6 }], classExtensions: [], propertyExtensions: [], actionExtensions: [], forms: [{ name: "pedido", line: 8 }], formExtensions: [], navigators: [], constraints: [], whenEvents: [], onEvents: [], apiAnnotations: [], noAuthAnnotations: [], groups: [], designs: [], windows: [], metaStatements: [], tables: [], indexes: [], beforeStatements: [], afterStatements: [], macroInvocations: [] },
  };
  const markdown = renderModuleRegisterMarkdown({
    applicationComposition: { rootModule: "RubrovaCustom", resolvedModuleCount: 3, sourceModuleCounts: { myCompany: 1, lsFusion: 1, rubrova: 1 }, unresolvedRequirements: [] },
    myCompany: { lsfFileCount: 1, modules: [module] },
    rubrovaExtensions: { lsfFileCount: 1, modules: [{ ...module, moduleName: "RubrovaExt", path: "extensions/lsfusion/RubrovaExt.lsf", counts: module.counts, declarations: module.declarations }] },
    myCompanyProject: {
      categoryCounts: { "Plantilla JasperReports": 1, "Componente JavaScript": 1, "Extensión Java": 1 },
      reportTemplates: ["vendor/mycompany/report.jrxml"],
      webAssets: ["vendor/mycompany/app.js"],
      javaSources: [{ path: "vendor/mycompany/Custom.java", packageName: "mycompany", topLevelTypes: [{ kind: "class", name: "Custom", line: 3 }], importCount: 1 }],
      propertyFiles: ["vendor/mycompany/messages.properties"],
      sqlScripts: ["vendor/mycompany/schema.sql"],
      imageAssets: ["vendor/mycompany/logo.png"],
      files: [],
      fileCount: 5,
    },
    lsFusion: {
      lsfFileCount: 1,
      modules: [{ ...module, moduleName: "System", path: "vendor/platform/server/src/main/lsfusion/system/System.lsf" }],
      projectExtensionCounts: { ".java": 1, ".lsf": 1 },
      javaSourceCatalog: [{ path: "vendor/platform/server/src/main/java/example/System.java", packageName: "example", importCount: 2, lineCount: 40, topLevelTypes: [{ kind: "class", name: "System", line: 5 }] }],
      projectFiles: ["vendor/platform/server/src/main/java/example/System.java", "vendor/platform/server/src/main/lsfusion/system/System.lsf"],
    },
  });
  assert.match(markdown, /report[.]jrxml/);
  assert.match(markdown, /Custom[.]java/);
  assert.match(markdown, /System[.]java/);
  assert.match(markdown, /messages[.]properties/);
});
