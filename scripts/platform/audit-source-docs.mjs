#!/usr/bin/env node
/**
 * Índice de documentación incluida con los snapshots fijados de MyCompany y
 * lsFusion. Registra páginas, títulos, encabezados, idiomas y recursos gráficos.
 * No interpreta ni certifica el contenido funcional de cada página.
 */
import { existsSync, readFileSync, readdirSync, mkdirSync, writeFileSync } from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const ROOT = path.resolve(process.env.GITHUB_WORKSPACE || process.cwd());
const IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"];
const SOURCE_ROOTS = [
  { product: "MyCompany", locale: "en", relativeRoot: "vendor/mycompany/src/main/resources/docs/en" },
  { product: "MyCompany", locale: "pl", relativeRoot: "vendor/mycompany/src/main/resources/docs/pl" },
  { product: "MyCompany", locale: "ru", relativeRoot: "vendor/mycompany/src/main/resources/docs/ru" },
  { product: "lsFusion", locale: "en", relativeRoot: "vendor/platform/docs/en" },
  { product: "lsFusion", locale: "ru", relativeRoot: "vendor/platform/docs/ru" },
];

function walkFiles(directory, root, extensions) {
  const accepted = new Set(extensions.map((extension) => extension.toLowerCase()));
  const result = [];
  for (const entry of readdirSync(directory, { withFileTypes: true })) {
    const absolute = path.join(directory, entry.name);
    if (entry.isDirectory()) result.push(...walkFiles(absolute, root, extensions));
    else if (entry.isFile() && accepted.has(path.extname(entry.name).toLowerCase())) {
      result.push(path.relative(root, absolute).split(path.sep).join("/"));
    }
  }
  return result.sort();
}

function firstNonEmptyLine(source) {
  return source.split(/\r?\n/).find((line) => line.trim().length > 0)?.trim() || "";
}

export function parseMarkdownDocument(source, relativePath = "") {
  const withoutBom = source.replace(/^\uFEFF/, "");
  const withoutFrontMatter = withoutBom.replace(/^---\r?\n[\s\S]*?\r?\n---\r?\n/, "");
  const headings = [...withoutFrontMatter.matchAll(/^(#{1,6})\s+(.+?)\s*#*\s*$/gm)]
    .map((match) => ({
      level: match[1].length,
      text: match[2].trim(),
      line: withoutFrontMatter.slice(0, match.index).split(/\r?\n/).length,
    }));
  const h1 = headings.find((heading) => heading.level === 1);
  const firstHeading = headings[0];
  const fallback = firstNonEmptyLine(withoutFrontMatter).replace(/^[-*]\s+/, "");
  const title = h1?.text || firstHeading?.text || fallback || path.basename(relativePath, ".md");

  return {
    relativePath,
    title,
    titleSource: h1 ? "h1" : firstHeading ? "heading" : fallback ? "first-content-line" : "filename",
    hasHeading: headings.length > 0,
    headingCount: headings.length,
    headings,
    lineCount: source.split(/\r?\n/).length,
  };
}

function domainOf(relativePath) {
  const parts = relativePath.split("/");
  return parts.length > 1 ? parts[0] : "(raíz)";
}

function countBy(items, keyFor) {
  const counts = {};
  for (const item of items) {
    const key = keyFor(item);
    counts[key] = (counts[key] || 0) + 1;
  }
  return Object.fromEntries(Object.entries(counts).sort(([a], [b]) => a.localeCompare(b)));
}

export function buildDocumentationCatalog(root = ROOT) {
  const locales = [];
  const absentLocales = [];
  for (const specification of SOURCE_ROOTS) {
    const absoluteRoot = path.join(root, specification.relativeRoot);
    if (!existsSync(absoluteRoot)) {
      absentLocales.push({
        product: specification.product,
        locale: specification.locale,
        path: specification.relativeRoot,
      });
      continue;
    }

    const markdownFiles = walkFiles(absoluteRoot, absoluteRoot, [".md"]);
    const imageFiles = walkFiles(absoluteRoot, absoluteRoot, IMAGE_EXTENSIONS);
    const pages = markdownFiles.map((relativePath) => {
      const absolute = path.join(absoluteRoot, relativePath);
      return {
        ...parseMarkdownDocument(readFileSync(absolute, "utf8"), relativePath),
        path: path.relative(root, absolute).split(path.sep).join("/"),
        domain: domainOf(relativePath),
      };
    });

    locales.push({
      product: specification.product,
      locale: specification.locale,
      sourceRoot: specification.relativeRoot,
      markdownCount: markdownFiles.length,
      imageCount: imageFiles.length,
      pagesWithoutHeadings: pages.filter((page) => !page.hasHeading).map((page) => page.path),
      domainCounts: countBy(pages, (page) => page.domain),
      pages,
      images: imageFiles.map((file) => path.join(specification.relativeRoot, file).split(path.sep).join("/")),
    });
  }

  const localeCounts = {};
  for (const locale of locales) {
    localeCounts[locale.product] ??= {};
    localeCounts[locale.product][locale.locale] = {
      markdown: locale.markdownCount,
      images: locale.imageCount,
    };
  }

  return {
    schemaVersion: 1,
    method: "Índice de archivos Markdown e imágenes de los snapshots; no constituye lectura ni validación funcional del contenido.",
    products: localeCounts,
    locales,
    absentLocales,
    quality: {
      totalMarkdownPages: locales.reduce((sum, locale) => sum + locale.markdownCount, 0),
      totalImages: locales.reduce((sum, locale) => sum + locale.imageCount, 0),
      pagesWithoutHeadings: locales.reduce((sum, locale) => sum + locale.pagesWithoutHeadings.length, 0),
      expectedMyCompanyLocalesPresent: ["en", "pl", "ru"].every((locale) =>
        locales.some((entry) => entry.product === "MyCompany" && entry.locale === locale),
      ),
      expectedPlatformLocalesPresent: ["en", "ru"].every((locale) =>
        locales.some((entry) => entry.product === "lsFusion" && entry.locale === locale),
      ),
    },
  };
}

function escapeMarkdownCell(value) {
  return String(value ?? "").replace(/\|/g, "\\|").replace(/\r?\n/g, " ").trim();
}

export function renderDocumentationRegisterMarkdown(catalog) {
  const lines = [
    "# Registro de documentación — MyCompany 6.2 y lsFusion 6.2",
    "",
    "**Alcance:** páginas Markdown y recursos gráficos que vienen incluidos en los snapshots fijados.",
    "",
    "**Método:** índice de título, ruta, idioma, encabezados y recursos. No reemplaza la lectura funcional ni confirma que cada página describa exactamente el runtime de Rubrova.",
    "",
    "## Resumen de recursos",
    "",
    "| Producto | Idioma | Páginas Markdown | Imágenes |",
    "|---|---|---:|---:|",
  ];

  for (const locale of catalog.locales) {
    lines.push("| " + [
      escapeMarkdownCell(locale.product),
      escapeMarkdownCell(locale.locale),
      locale.markdownCount,
      locale.imageCount,
    ].join(" | ") + " |");
  }

  lines.push("", "Total: **" + catalog.quality.totalMarkdownPages + " páginas Markdown** y **" + catalog.quality.totalImages + " imágenes**.", "");
  lines.push("Páginas sin encabezados Markdown: **" + catalog.quality.pagesWithoutHeadings + "**. No se omiten; se listan con su título de respaldo.", "");

  for (const locale of catalog.locales) {
    lines.push("## " + locale.product + " — " + locale.locale);
    lines.push("");
    lines.push("| Título | Dominio | Encabezados | Fuente del título | Archivo |");
    lines.push("|---|---|---:|---|---|");
    for (const page of locale.pages) {
      const headingSummary = page.headings.map((heading) =>
        "H" + heading.level + " " + heading.text + " (L" + heading.line + ")",
      ).join("; ") || "Sin encabezados";
      lines.push("| " + [
        escapeMarkdownCell(page.title),
        escapeMarkdownCell(page.domain),
        page.headingCount,
        escapeMarkdownCell(page.titleSource),
        escapeMarkdownCell(page.path),
      ].join(" | ") + " |");
      if (!page.hasHeading) {
        // El título de respaldo y la ruta quedan registrados; no se descarta la página.
      }
    }
    lines.push("");
    lines.push("### Recursos gráficos — " + locale.locale);
    lines.push("");
    for (const imagePath of locale.images) lines.push("- " + imagePath);
    if (!locale.images.length) lines.push("- No hay imágenes en esta carpeta.");
    lines.push("");
  }

  lines.push("## Carpetas de idioma ausentes", "");
  if (catalog.absentLocales.length) {
    for (const locale of catalog.absentLocales) {
      lines.push("- " + locale.product + " " + locale.locale + ": " + locale.path);
    }
  } else {
    lines.push("No hay carpetas ausentes entre los idiomas esperados por este inventario.");
  }
  lines.push("", "## Advertencias", "");
  lines.push("- La clasificación de dominio se basa en la carpeta del archivo, no en una interpretación automática de su contenido.");
  lines.push("- Una página indexada no está necesariamente leída, traducida ni contrastada con las fuentes.");
  lines.push("- Los 33 documentos de plataforma sin encabezados por idioma siguen incluidos; su estructura se debe revisar individualmente.");
  lines.push("- MyCompany trae documentación en inglés, polaco y ruso. No se encontró carpeta documental española en el snapshot.");
  return lines.join("\n") + "\n";
}

function runCli() {
  const args = process.argv.slice(2);
  let outputPath = null;
  let markdownOutputPath = null;
  for (let index = 0; index < args.length; index += 1) {
    if (args[index] === "--json-output") {
      outputPath = args[index + 1];
      if (!outputPath) throw new Error("Falta la ruta después de --json-output.");
      index += 1;
    } else if (args[index] === "--markdown-output") {
      markdownOutputPath = args[index + 1];
      if (!markdownOutputPath) throw new Error("Falta la ruta después de --markdown-output.");
      index += 1;
    } else if (args[index] === "--help" || args[index] === "-h") {
      console.log("Uso: node scripts/platform/audit-source-docs.mjs [--json-output archivo.json] [--markdown-output registro.md]");
      return;
    } else {
      throw new Error("Argumento no reconocido: " + args[index]);
    }
  }

  const catalog = buildDocumentationCatalog();
  for (const locale of catalog.locales) {
    console.log(locale.product + " " + locale.locale + ": " + locale.markdownCount + " páginas Markdown, " + locale.imageCount + " imágenes.");
  }
  console.log("Total: " + catalog.quality.totalMarkdownPages + " páginas y " + catalog.quality.totalImages + " imágenes.");
  console.log("Páginas sin encabezados: " + catalog.quality.pagesWithoutHeadings + ".");
  console.log("El índice identifica recursos; no valida la lectura ni el contenido funcional.");

  if (!catalog.quality.expectedMyCompanyLocalesPresent || !catalog.quality.expectedPlatformLocalesPresent) {
    throw new Error("Falta alguna carpeta documental esperada del snapshot.");
  }

  if (outputPath) {
    const absolute = path.resolve(outputPath);
    mkdirSync(path.dirname(absolute), { recursive: true });
    writeFileSync(absolute, JSON.stringify(catalog, null, 2) + "\n", "utf8");
    console.log("Informe JSON: " + absolute);
  }
  if (markdownOutputPath) {
    const absolute = path.resolve(markdownOutputPath);
    mkdirSync(path.dirname(absolute), { recursive: true });
    writeFileSync(absolute, renderDocumentationRegisterMarkdown(catalog), "utf8");
    console.log("Registro Markdown: " + absolute);
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  try {
    runCli();
  } catch (error) {
    console.error("ERROR: " + (error instanceof Error ? error.message : String(error)));
    process.exitCode = 1;
  }
}
