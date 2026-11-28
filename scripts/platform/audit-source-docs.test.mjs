import test from "node:test";
import assert from "node:assert/strict";
import { parseMarkdownDocument, renderDocumentationRegisterMarkdown } from "./audit-source-docs.mjs";

test("extrae título y encabezados sin confundir el front matter con contenido", () => {
  const markdown = [
    "---",
    "title: Metadatos",
    "---",
    "# Inventario",
    "",
    "## Recepciones",
    "Texto.",
    "### Control de cantidades",
  ].join("\n");
  const parsed = parseMarkdownDocument(markdown, "inventory/receipts.md");
  assert.equal(parsed.title, "Inventario");
  assert.equal(parsed.titleSource, "h1");
  assert.equal(parsed.headingCount, 3);
  assert.deepEqual(parsed.headings.map((heading) => [heading.level, heading.text]), [
    [1, "Inventario"],
    [2, "Recepciones"],
    [3, "Control de cantidades"],
  ]);
});

test("usa el primer encabezado cuando no hay H1", () => {
  const parsed = parseMarkdownDocument("Texto introductorio\n\n### Parámetros\n", "settings.md");
  assert.equal(parsed.title, "Parámetros");
  assert.equal(parsed.titleSource, "heading");
  assert.equal(parsed.hasHeading, true);
});

test("marca documentos sin encabezados y usa su primera línea como título", () => {
  const parsed = parseMarkdownDocument("Guía de operación\n\nContenido.", "guide.md");
  assert.equal(parsed.title, "Guía de operación");
  assert.equal(parsed.titleSource, "first-content-line");
  assert.equal(parsed.hasHeading, false);
});

test("genera un registro con páginas e imágenes de todos los idiomas", () => {
  const markdown = renderDocumentationRegisterMarkdown({
    locales: [{
      product: "MyCompany",
      locale: "en",
      markdownCount: 1,
      imageCount: 1,
      pages: [{
        title: "Inventario",
        titleSource: "h1",
        domain: "inventory",
        headingCount: 1,
        headings: [{ level: 1, text: "Inventario", line: 1 }],
        path: "vendor/mycompany/docs/en/inventory.md",
        hasHeading: true,
      }],
      images: ["vendor/mycompany/docs/en/stock.png"],
    }],
    quality: { totalMarkdownPages: 1, totalImages: 1, pagesWithoutHeadings: 0 },
    absentLocales: [],
  });
  assert.match(markdown, /Inventario/);
  assert.match(markdown, /inventory\\.md/);
  assert.match(markdown, /stock\\.png/);
});
