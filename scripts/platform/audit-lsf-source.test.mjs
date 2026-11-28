import test from "node:test";
import assert from "node:assert/strict";
import { closureFrom, maskLsfNonCode, parseLsfSource, topLevelLsfSource } from "./audit-lsf-source.mjs";

test("identifica encabezado, dependencias y declaraciones del módulo", () => {
  const source = [
    "// MODULE Comentario;",
    "MODULE ComprasDemo;",
    "REQUIRE Base, Proveedores;",
    "NAMESPACE Compras;",
    "CLASS ABSTRACT Pedido 'Pedido';",
    "EXTEND CLASS Pedido {",
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
