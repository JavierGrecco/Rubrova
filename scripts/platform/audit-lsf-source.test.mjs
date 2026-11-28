import test from "node:test";
import assert from "node:assert/strict";
import { maskLsfNonCode, parseLsfSource } from "./audit-lsf-source.mjs";

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
  assert.equal(parsed.counts.classes, 2);
  assert.equal(parsed.counts.forms, 2);
  assert.equal(parsed.counts.navigators, 1);
  assert.equal(parsed.counts.constraints, 1);
  assert.equal(parsed.counts.whenEvents, 1);
  assert.equal(parsed.counts.apiAnnotations, 1);
  assert.equal(parsed.counts.noAuthAnnotations, 1);
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
  assert.equal(masked.split("\n")[5].trim(), "CLASS X;");
});
