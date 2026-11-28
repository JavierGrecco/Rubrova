#!/usr/bin/env node
/**
 * Catálogo estructural de las fuentes LSF fijadas en Rubrova.
 *
 * Identifica módulos, dependencias y declaraciones visibles. No interpreta la
 * semántica del lenguaje ni reemplaza la auditoría funcional o las pruebas.
 */
import { readdirSync, readFileSync, mkdirSync, writeFileSync } from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const ROOT = path.resolve(process.env.GITHUB_WORKSPACE || process.cwd());
const MYCOMPANY_PROJECT_ROOT = "vendor/mycompany";
const MYCOMPANY_ROOT = "vendor/mycompany/src/main/lsfusion";
const PLATFORM_ROOT = "vendor/platform";
const RUBROVA_EXTENSIONS_ROOT = "extensions/lsfusion";
const APPLICATION_ROOT_MODULE = "RubrovaCustom";
const SOURCE_LOCK_PATH = "platform/source-lock.json";
const DOCUMENTATION_IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg", ".gif", ".svg"];

function walkFiles(directory, extension) {
  const result = [];
  for (const entry of readdirSync(directory, { withFileTypes: true })) {
    const absolute = path.join(directory, entry.name);
    if (entry.isDirectory()) result.push(...walkFiles(absolute, extension));
    else if (entry.isFile() && entry.name.endsWith(extension)) {
      result.push(path.relative(ROOT, absolute).split(path.sep).join("/"));
    }
  }
  return result.sort();
}

function walkAllFiles(directory) {
  const result = [];
  for (const entry of readdirSync(directory, { withFileTypes: true })) {
    const absolute = path.join(directory, entry.name);
    if (entry.isDirectory()) result.push(...walkAllFiles(absolute));
    else if (entry.isFile()) result.push(path.relative(ROOT, absolute).split(path.sep).join("/"));
  }
  return result.sort();
}

function extensionOf(filePath) {
  return path.extname(filePath).toLowerCase() || "(sin extensión)";
}

function classifyMyCompanyProjectFile(filePath) {
  const extension = extensionOf(filePath);
  if (extension === ".lsf") return "Módulo LSF";
  if (extension === ".jrxml") return "Plantilla JasperReports";
  if (extension === ".java") return "Extensión Java";
  if (extension === ".js") return "Componente JavaScript";
  if (extension === ".css") return "Hoja de estilos";
  if (extension === ".properties") return "Configuración o traducción";
  if (extension === ".sql") return "Script SQL";
  if ([".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"].includes(extension)) return "Imagen o recurso gráfico";
  if (extension === ".md") return "Documentación Markdown";
  if ([".xml", ".json", ".yml", ".yaml"].includes(extension)) return "Metadatos o configuración estructurada";
  return "Otro recurso";
}

export function parseJavaSource(source, filePath = "") {
  const packageName = source.match(/^package\s+([A-Za-z0-9_.]+)\s*;/m)?.[1] || "(paquete raíz)";
  const types = [...source.matchAll(/^(?:(?:public|protected|private|abstract|final|static|sealed|non-sealed|strictfp)\s+)*(class|interface|enum|record|@interface)\s+([A-Za-z_$][A-Za-z0-9_$]*)/gm)]
    .map((match) => ({
      kind: match[1],
      name: match[2],
      line: source.slice(0, match.index).split("\n").length,
    }));
  return {
    path: filePath,
    packageName,
    lineCount: source.split("\n").length,
    importCount: [...source.matchAll(/^import\s+(?:static\s+)?[^;]+;/gm)].length,
    topLevelTypes: types,
  };
}

function walkFilesByExtensions(directory, extensions) {
  const accepted = new Set(extensions.map((extension) => extension.toLowerCase()));
  const result = [];
  for (const entry of readdirSync(directory, { withFileTypes: true })) {
    const absolute = path.join(directory, entry.name);
    if (entry.isDirectory()) result.push(...walkFilesByExtensions(absolute, extensions));
    else if (entry.isFile() && accepted.has(path.extname(entry.name).toLowerCase())) {
      result.push(path.relative(ROOT, absolute).split(path.sep).join("/"));
    }
  }
  return result.sort();
}

/** Enmascara comentarios y literales, preservando los saltos de línea. */
export function maskLsfNonCode(source) {
  const chars = source.split("");
  let state = "code";
  let quote = "";
  for (let i = 0; i < chars.length; i += 1) {
    const current = chars[i];
    const next = chars[i + 1];

    if (state === "line-comment") {
      if (current === "\n") state = "code";
      else chars[i] = " ";
      continue;
    }
    if (state === "block-comment") {
      if (current === "*" && next === "/") {
        chars[i] = " ";
        chars[i + 1] = " ";
        i += 1;
        state = "code";
      } else if (current !== "\n") chars[i] = " ";
      continue;
    }
    if (state === "string") {
      if (current === "\\" && i + 1 < chars.length) {
        if (current !== "\n") chars[i] = " ";
        if (chars[i + 1] !== "\n") chars[i + 1] = " ";
        i += 1;
        continue;
      }
      if (current === quote) {
        chars[i] = " ";
        state = "code";
      } else if (current !== "\n") chars[i] = " ";
      continue;
    }

    if (current === "/" && next === "/") {
      chars[i] = " ";
      chars[i + 1] = " ";
      i += 1;
      state = "line-comment";
    } else if (current === "/" && next === "*") {
      chars[i] = " ";
      chars[i + 1] = " ";
      i += 1;
      state = "block-comment";
    } else if (current === "'" || current === '"' || current === "\`") {
      quote = current;
      chars[i] = " ";
      state = "string";
    }
  }
  return chars.join("");
}

function declarationMatches(source, expression) {
  return [...source.matchAll(expression)].map((match) => ({
    name: match[1] || null,
    line: source.slice(0, match.index).split("\n").length,
  }));
}

/**
 * Conserva únicamente sentencias de nivel superior.
 * Evita contar referencias a formularios dentro de NAVIGATOR o bloques DESIGN
 * como si fueran nuevas declaraciones. El cuerpo META se registra aparte:
 * sus sentencias son plantillas y no se ejecutan hasta expandir el metacódigo.
 */
export function topLevelLsfSource(source) {
  const code = maskLsfNonCode(source);
  const lines = code.split("\n");
  const visible = [];
  let braceDepth = 0;
  let inMeta = false;

  for (const line of lines) {
    const trimmed = line.trim();
    const startsMeta = braceDepth === 0 && !inMeta && /^META\b/.test(trimmed);
    const endsMeta = inMeta && /^END\b/.test(trimmed);
    const isVisible = braceDepth === 0 && !inMeta;

    visible.push(isVisible ? line : " ".repeat(line.length));

    if (startsMeta) inMeta = true;
    else if (endsMeta) inMeta = false;

    for (const character of line) {
      if (character === "{") braceDepth += 1;
      else if (character === "}") braceDepth = Math.max(0, braceDepth - 1);
    }
  }

  return visible.join("\n");
}

const NON_ACTION_BLOCK_KEYWORDS = new Set([
  "ACTION", "AFTER", "BEFORE", "CLASS", "CONSTRAINT", "DESIGN", "FORM", "GROUP",
  "META", "MODULE", "NAVIGATOR", "NAMESPACE", "ON", "REQUIRE", "TABLE",
  "WHEN", "WINDOW",
]);

export function parseLsfSource(source, filePath = "") {
  const code = maskLsfNonCode(source);
  const topLevel = topLevelLsfSource(source);
  const moduleName = topLevel.match(/^MODULE\s+([A-Za-z_][A-Za-z0-9_]*)\s*;/m)?.[1] || null;
  const namespace = topLevel.match(/^NAMESPACE\s+([A-Za-z_][A-Za-z0-9_.]*)\s*;/m)?.[1] || null;
  const requireBody = topLevel.match(/^REQUIRE\b([\s\S]*?);/m)?.[1] || "";
  const requires = requireBody.split(",").map((part) => part.trim()).filter(Boolean);

  const explicitActions = declarationMatches(
    topLevel,
    /^ACTION\s+([A-Za-z_][A-Za-z0-9_]*)\b/gm,
  );
  const implicitActions = declarationMatches(
    topLevel,
    /^([A-Za-z_][A-Za-z0-9_]*)\s*(?:'[^'\n]*'\s*)?(?:\([^)\n]*\)\s*)?\{/gm,
  ).filter((entry) => !NON_ACTION_BLOCK_KEYWORDS.has(entry.name.toUpperCase()));

  const propertyDeclarations = declarationMatches(
    topLevel,
    /^([A-Za-z_][A-Za-z0-9_]*)(?:\s+'[^'\n]*')?(?:\s*\([^)\n]*\))?\s*=(?!=|>)/gm,
  );
  const propertyExtensions = declarationMatches(
    topLevel,
    /^([A-Za-z_][A-Za-z0-9_]*)(?:\s*\[[^\]\n]+\])?\s*\([^)\n]*\)\s*\+=/gm,
  );
  const actionExtensions = declarationMatches(
    topLevel,
    /^(?:ACTION\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*\([^)\n]*\)\s*\+(?![=])/gm,
  );

  const declarations = {
    classes: declarationMatches(topLevel, /^CLASS\s+(?:ABSTRACT\s+)?([A-Za-z_][A-Za-z0-9_]*)/gm),
    classExtensions: declarationMatches(topLevel, /^EXTEND\s+CLASS\s+([A-Za-z_][A-Za-z0-9_]*)/gm),
    forms: declarationMatches(topLevel, /^FORM\s+([A-Za-z_][A-Za-z0-9_]*)/gm),
    formExtensions: declarationMatches(topLevel, /^EXTEND\s+FORM\s+([A-Za-z_][A-Za-z0-9_]*)/gm),
    navigators: declarationMatches(topLevel, /^NAVIGATOR\b/gm).map((x) => ({ ...x, name: null })),
    navigatorExtensions: declarationMatches(topLevel, /^EXTEND\s+NAVIGATOR\b/gm).map((x) => ({ ...x, name: null })),
    properties: propertyDeclarations,
    propertyExtensions,
    actions: [...explicitActions, ...implicitActions].sort((a, b) => a.line - b.line),
    actionExtensions,
    groups: declarationMatches(topLevel, /^GROUP\s+(?:NATIVE\s+)?([A-Za-z_][A-Za-z0-9_]*)/gm),
    designs: declarationMatches(topLevel, /^DESIGN\s+([A-Za-z_][A-Za-z0-9_]*)/gm),
    windows: declarationMatches(topLevel, /^WINDOW\s+([A-Za-z_][A-Za-z0-9_]*)/gm),
    metaStatements: declarationMatches(topLevel, /^META\s+([A-Za-z_][A-Za-z0-9_]*)/gm),
    tables: declarationMatches(topLevel, /^TABLE\s+([A-Za-z_][A-Za-z0-9_]*)/gm),
    constraints: declarationMatches(topLevel, /^CONSTRAINT\b/gm).map((x) => ({ ...x, name: null })),
    indexes: declarationMatches(topLevel, /^INDEX\b/gm).map((x) => ({ ...x, name: null })),
    whenEvents: declarationMatches(topLevel, /^WHEN\b/gm).map((x) => ({ ...x, name: null })),
    onEvents: declarationMatches(topLevel, /^ON\b/gm).map((x) => ({ ...x, name: null })),
    beforeStatements: declarationMatches(topLevel, /^BEFORE\b/gm).map((x) => ({ ...x, name: null })),
    afterStatements: declarationMatches(topLevel, /^AFTER\b/gm).map((x) => ({ ...x, name: null })),
    apiAnnotations: declarationMatches(code, /@@api\b/gm).map((x) => ({ ...x, name: null })),
    noAuthAnnotations: declarationMatches(code, /@@noauth\b/gm).map((x) => ({ ...x, name: null })),
    macroInvocations: declarationMatches(code, /^@[A-Za-z_][A-Za-z0-9_]*/gm),
  };

  const counts = Object.fromEntries(
    Object.entries(declarations).map(([key, values]) => [key, values.length]),
  );
  counts.actionDeclarationsAreHeuristic = true;
  counts.propertyDeclarationsAreTopLevelEqualsStatements = true;
  counts.macroExpansionIsNotIncluded = true;

  return {
    path: filePath,
    moduleName,
    namespace,
    requires,
    lineCount: source.split("\n").length,
    counts,
    declarations,
  };
}

function domainOf(filePath, root) {
  const normalizedRoot = root.replace(/\/$/, "");
  const relative = filePath.slice(normalizedRoot.length + 1);
  return relative.includes("/") ? relative.split("/")[0] : "(raíz)";
}

function countBy(items, keyFor) {
  const counts = {};
  for (const item of items) {
    const key = keyFor(item);
    counts[key] = (counts[key] || 0) + 1;
  }
  return Object.fromEntries(Object.entries(counts).sort(([a], [b]) => a.localeCompare(b)));
}

export function closureFrom(rootName, moduleMap) {
  const found = new Set();
  const unresolved = new Set();
  const queue = [rootName];
  while (queue.length) {
    const name = queue.shift();
    if (found.has(name)) continue;
    found.add(name);
    const module = moduleMap.get(name);
    if (!module) {
      unresolved.add(name);
      continue;
    }
    for (const required of module.requires) {
      if (moduleMap.has(required)) {
        if (!found.has(required)) queue.push(required);
      } else unresolved.add(required);
    }
  }
  return {
    moduleNames: [...found].filter((name) => moduleMap.has(name)).sort(),
    unresolvedRequirements: [...unresolved].sort(),
  };
}

function classifyPlatformDoc(filePath) {
  const name = path.basename(filePath).toLowerCase();
  if (/(class|property|action|operator|statement|expression|formula|aggregation|metaprogram|module|namespace|extension)/.test(name)) return "Lenguaje, lógica y modularidad";
  if (/(form|view|navigator|design|gui|interface|input|filter|search|tree|report|print)/.test(name)) return "Interfaz, navegación y reportes";
  if (/(session|apply|cancel|event|execution|transaction|change|when|thread|process)/.test(name)) return "Ejecución, sesiones y eventos";
  if (/(external|integration|http|json|api|import|export|sql|database|jdbc|file)/.test(name)) return "Integración y acceso a datos";
  if (/(security|permission|authentication|user)/.test(name)) return "Identidad y seguridad";
  if (/(install|docker|scheduler|profiler|monitor|log|migration|backup|management|system)/.test(name)) return "Administración y operación";
  if (/(international|language|localization|resource)/.test(name)) return "Idiomas y localización";
  return "Otros temas";
}

function packageBucket(filePath) {
  const marker = "/src/main/java/";
  const index = filePath.indexOf(marker);
  if (index < 0) return "(fuera de Java)";
  const parts = filePath.slice(index + marker.length).split("/");
  const packageParts = parts.slice(0, -1);
  return packageParts.length ? packageParts.slice(0, 3).join("/") : "(paquete raíz)";
}

export function buildSourceCatalog(root = ROOT) {
  const myRoot = path.join(root, MYCOMPANY_ROOT);
  const platformRoot = path.join(root, PLATFORM_ROOT);
  const extensionsRoot = path.join(root, RUBROVA_EXTENSIONS_ROOT);
  const myCompanyProjectRoot = path.join(root, MYCOMPANY_PROJECT_ROOT);

  const myFiles = walkFiles(myRoot, ".lsf");
  const platformFiles = walkFiles(platformRoot, ".lsf");
  const extensionFiles = walkFiles(extensionsRoot, ".lsf");
  const myModules = myFiles.map((file) => parseLsfSource(readFileSync(path.join(root, file), "utf8"), file));
  const platformModules = platformFiles.map((file) => parseLsfSource(readFileSync(path.join(root, file), "utf8"), file));
  const extensionModules = extensionFiles.map((file) => parseLsfSource(readFileSync(path.join(root, file), "utf8"), file));
  const myJavaFiles = walkFiles(platformRoot, ".java");
  const myCompanyProjectFiles = walkAllFiles(myCompanyProjectRoot);
  const platformProjectFiles = walkAllFiles(platformRoot);
  const myCompanyJavaFiles = walkFiles(myCompanyProjectRoot, ".java");
  const myCompanyJavaCatalog = myCompanyJavaFiles.map((file) =>
    parseJavaSource(readFileSync(path.join(root, file), "utf8"), file),
  );
  const platformJavaCatalog = myJavaFiles.map((file) =>
    parseJavaSource(readFileSync(path.join(root, file), "utf8"), file),
  );


  const enDocsRoot = path.join(platformRoot, "docs/en");
  const ruDocsRoot = path.join(platformRoot, "docs/ru");
  const enDocs = walkFiles(enDocsRoot, ".md");
  const ruDocs = walkFiles(ruDocsRoot, ".md");
  const enImages = walkFilesByExtensions(enDocsRoot, DOCUMENTATION_IMAGE_EXTENSIONS);
  const ruImages = walkFilesByExtensions(ruDocsRoot, DOCUMENTATION_IMAGE_EXTENSIONS);

  const allModules = [...platformModules, ...myModules, ...extensionModules];
  const nameCounts = countBy(allModules, (module) => module.moduleName || "(sin MODULE)");
  const duplicateNames = Object.entries(nameCounts)
    .filter(([name, count]) => name !== "(sin MODULE)" && count > 1)
    .map(([name, count]) => ({ name, count }));
  const moduleMap = new Map();
  for (const module of allModules) {
    if (module.moduleName && !moduleMap.has(module.moduleName)) moduleMap.set(module.moduleName, module);
  }

  const myCompanyClosure = closureFrom("MyCompany", moduleMap);
  const applicationClosure = closureFrom(APPLICATION_ROOT_MODULE, moduleMap);
  const myCompanyRootNames = new Set(myCompanyClosure.moduleNames);
  const applicationNames = new Set(applicationClosure.moduleNames);
  const applicationModules = applicationClosure.moduleNames.map((name) => moduleMap.get(name));
  const unclassifiedFiles = allModules.filter((module) => !module.moduleName).map((module) => module.path);

  const lock = JSON.parse(readFileSync(path.join(root, SOURCE_LOCK_PATH), "utf8"));
  const mySourceLock = lock.sources.find((source) => source.name === "MyCompany");
  const platformSourceLock = lock.sources.find((source) => source.name === "lsFusion platform");

  const myCompanyEntries = myModules.map((module) => ({
    ...module,
    domain: domainOf(module.path, MYCOMPANY_ROOT),
    reachableFromMyCompanyRoot: myCompanyRootNames.has(module.moduleName),
    reachableFromApplicationRoot: applicationNames.has(module.moduleName),
  }));
  const platformEntries = platformModules.map((module) => ({
    ...module,
    domain: domainOf(module.path, PLATFORM_ROOT),
    reachableFromApplicationRoot: applicationNames.has(module.moduleName),
  }));
  const extensionEntries = extensionModules.map((module) => ({
    ...module,
    domain: domainOf(module.path, RUBROVA_EXTENSIONS_ROOT),
    reachableFromApplicationRoot: applicationNames.has(module.moduleName),
  }));

  const applicationSourceCounts = {
    myCompany: applicationModules.filter((module) => module.path.startsWith(MYCOMPANY_ROOT + "/")).length,
    lsFusion: applicationModules.filter((module) => module.path.startsWith(PLATFORM_ROOT + "/")).length,
    rubrova: applicationModules.filter((module) => module.path.startsWith(RUBROVA_EXTENSIONS_ROOT + "/")).length,
  };

  return {
    schemaVersion: 2,
    method: "Inventario estático de archivos y declaraciones LSF de nivel superior; las acciones sin palabra clave se detectan por patrón y las expansiones META/macros no se interpretan. No valida la semántica ni la ejecución.",
    sources: {
      myCompany: { tag: mySourceLock.tag, commit: mySourceLock.commit, license: mySourceLock.license },
      lsFusion: { tag: platformSourceLock.tag, commit: platformSourceLock.commit, license: platformSourceLock.license },
    },
    applicationComposition: {
      rootModule: APPLICATION_ROOT_MODULE,
      resolvedModuleCount: applicationClosure.moduleNames.length,
      sourceModuleCounts: applicationSourceCounts,
      unresolvedRequirements: applicationClosure.unresolvedRequirements,
      modulesOutsideApplicationClosure: {
        myCompany: myCompanyEntries.filter((module) => !module.reachableFromApplicationRoot).map((module) => module.moduleName).sort(),
        lsFusion: platformEntries.filter((module) => !module.reachableFromApplicationRoot).map((module) => module.moduleName).sort(),
        rubrova: extensionEntries.filter((module) => !module.reachableFromApplicationRoot).map((module) => module.moduleName).sort(),
      },
    },
    myCompany: {
      lsfFileCount: myModules.length,
      lockedLsfFileCount: mySourceLock.observedLsfModules,
      domainCounts: countBy(myCompanyEntries, (module) => module.domain),
      reachableFromMyCompanyRootCount: myCompanyEntries.filter((module) => module.reachableFromMyCompanyRoot).length,
      outsideMyCompanyRootClosureCount: myCompanyEntries.filter((module) => !module.reachableFromMyCompanyRoot).length,
      reachableFromApplicationRootCount: myCompanyEntries.filter((module) => module.reachableFromApplicationRoot).length,
      outsideApplicationClosureCount: myCompanyEntries.filter((module) => !module.reachableFromApplicationRoot).length,
      myCompanyRootUnresolvedRequirements: myCompanyClosure.unresolvedRequirements,
      duplicateModuleNames: duplicateNames.filter((entry) => myModules.some((module) => module.moduleName === entry.name)),
      modules: myCompanyEntries,
    },
    rubrovaExtensions: {
      lsfFileCount: extensionModules.length,
      modules: extensionEntries,
    },
    myCompanyProject: {
      fileCount: myCompanyProjectFiles.length,
      extensionCounts: countBy(myCompanyProjectFiles, extensionOf),
      categoryCounts: countBy(myCompanyProjectFiles, classifyMyCompanyProjectFile),
      javaSourceCount: myCompanyJavaFiles.length,
      javaSources: myCompanyJavaCatalog,
      reportTemplates: myCompanyProjectFiles.filter((file) => extensionOf(file) === ".jrxml"),
      webAssets: myCompanyProjectFiles.filter((file) => [".js", ".css"].includes(extensionOf(file))),
      propertyFiles: myCompanyProjectFiles.filter((file) => extensionOf(file) === ".properties"),
      sqlScripts: myCompanyProjectFiles.filter((file) => extensionOf(file) === ".sql"),
      imageAssets: myCompanyProjectFiles.filter((file) => [".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"].includes(extensionOf(file))),
      files: myCompanyProjectFiles.map((file) => ({
        path: file,
        extension: extensionOf(file),
        category: classifyMyCompanyProjectFile(file),
      })),
    },

    lsFusion: {
      projectFileCount: platformProjectFiles.length,
      projectExtensionCounts: countBy(platformProjectFiles, extensionOf),
      mavenModuleFileCounts: countBy(platformProjectFiles, (file) => file.slice(PLATFORM_ROOT.length + 1).split("/")[0]),
      projectFiles: platformProjectFiles,
      javaSourceCatalog: platformJavaCatalog,
      lsfFileCount: platformModules.length,
      javaSourceFileCount: myJavaFiles.length,
      lockedJavaSourceFileCount: platformSourceLock.observedJavaFiles,
      documentationMarkdown: { en: enDocs.length, ru: ruDocs.length },
      documentationImages: { en: enImages.length, ru: ruImages.length },
      documentationAssets: {
        en: { markdown: enDocs.length, images: enImages.length, total: enDocs.length + enImages.length },
        ru: { markdown: ruDocs.length, images: ruImages.length, total: ruDocs.length + ruImages.length },
      },
      documentationTopicCounts: countBy(enDocs, classifyPlatformDoc),
      javaPackageCounts: countBy(myJavaFiles, packageBucket),
      modules: platformEntries,
    },
    quality: {
      filesWithoutModuleHeader: unclassifiedFiles,
      duplicateModuleNamesAcrossSnapshots: duplicateNames,
      myCompanyCountMatchesLock: myModules.length === mySourceLock.observedLsfModules,
      platformJavaCountMatchesLock: myJavaFiles.length === platformSourceLock.observedJavaFiles,
      applicationDependenciesResolved: applicationClosure.unresolvedRequirements.length === 0,
    },
  };
}

const MYCOMPANY_DOCUMENTATION_FOLDERS = {
  crm: ["crm"],
  fleet: ["transport"],
  humanResources: ["humanResources"],
  inventory: ["inventory"],
  invoicing: ["invoicing"],
  manufacturing: ["manufacturing"],
  masterdata: ["masterdata"],
  projectManagement: ["projectManagement"],
  purchase: ["purchase"],
  retail: ["retail"],
  sales: ["sales"],
};

function declarationNames(module, key) {
  return (module.declarations[key] || []).map((entry) =>
    entry.name ? entry.name + " (L" + entry.line + ")" : "L" + entry.line,
  );
}

function escapeMarkdownCell(value) {
  return String(value ?? "").replace(/\|/g, "\\|").replace(/\r?\n/g, " ").trim();
}

export function renderModuleRegisterMarkdown(catalog) {
  const docRoot = path.join(ROOT, "vendor/mycompany/src/main/resources/docs/en");
  const docPaths = walkFiles(docRoot, ".md");
  const docsByFolder = new Map();
  for (const relativePath of docPaths) {
    const folder = relativePath.split("/")[0] || "(raíz)";
    if (!docsByFolder.has(folder)) docsByFolder.set(folder, []);
    docsByFolder.get(folder).push("vendor/mycompany/src/main/resources/docs/en/" + relativePath);
  }

  const lines = [
    "# Registro estructural de módulos LSF — Rubrova",
    "",
    "**Alcance:** snapshots fijados de MyCompany 6.2, lsFusion 6.2 y extensiones LSF propias.",
    "",
    "**Método:** declaraciones de nivel superior detectadas estáticamente. Las acciones sin palabra clave se detectan por patrón. Las expansiones META y macros no se interpretan. Este registro no constituye una ficha funcional ni prueba de runtime.",
    "",
    "## Resumen de composición",
    "",
    "| Origen | Archivos LSF | En el cierre de RubrovaCustom |",
    "|---|---:|---:|",
    "| MyCompany 6.2 | " + catalog.myCompany.lsfFileCount + " | " + catalog.applicationComposition.sourceModuleCounts.myCompany + " |",
    "| lsFusion 6.2 | " + catalog.lsFusion.lsfFileCount + " | " + catalog.applicationComposition.sourceModuleCounts.lsFusion + " |",
    "| Extensiones Rubrova | " + catalog.rubrovaExtensions.lsfFileCount + " | " + catalog.applicationComposition.sourceModuleCounts.rubrova + " |",
    "",
    "Dependencias sin resolver desde RubrovaCustom: **" + catalog.applicationComposition.unresolvedRequirements.length + "**.",
    "",
    "## MyCompany 6.2 — los 800 módulos",
    "",
    "| Módulo | Dominio | En RubrovaCustom | Namespace | REQUIRE | Clases | Propiedades | Acciones | Formularios | Restricciones | Eventos | API |",
    "|---|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|",
  ];

  const myModules = [...catalog.myCompany.modules].sort((a, b) =>
    a.domain.localeCompare(b.domain) || a.moduleName.localeCompare(b.moduleName),
  );
  for (const module of myModules) {
    const c = module.counts;
    lines.push("| " + [
      escapeMarkdownCell(module.moduleName),
      escapeMarkdownCell(module.domain),
      module.reachableFromApplicationRoot ? "Sí" : "No",
      escapeMarkdownCell(module.namespace || "—"),
      escapeMarkdownCell(module.requires.join(", ") || "—"),
      c.classes + c.classExtensions,
      c.properties,
      c.actions,
      c.forms + c.formExtensions,
      c.constraints,
      c.whenEvents + c.onEvents,
      c.apiAnnotations,
    ].join(" | ") + " |");
  }

  lines.push("", "## Fichas estructurales por módulo MyCompany", "");
  for (const module of myModules) {
    const folders = MYCOMPANY_DOCUMENTATION_FOLDERS[module.domain] || [];
    const candidates = folders.flatMap((folder) => docsByFolder.get(folder) || []);
    lines.push("### " + module.moduleName);
    lines.push("");
    lines.push("- **Archivo:** " + module.path);
    lines.push("- **Namespace:** " + (module.namespace || "—"));
    lines.push("- **En cierre RubrovaCustom:** " + (module.reachableFromApplicationRoot ? "Sí" : "No; requiere evaluación antes de activarlo"));
    lines.push("- **Dependencias REQUIRE:** " + (module.requires.join(", ") || "Ninguna declarada"));
    lines.push("- **Líneas:** " + module.lineCount);
    lines.push("- **Candidatos de documentación por dominio (no asociación confirmada):** " + (candidates.length ? candidates.join(", ") : "No se encontró carpeta documental homónima; revisar documentación transversal o regional"));
    const groups = [
      ["Clases", "classes"], ["Extensiones de clase", "classExtensions"],
      ["Propiedades", "properties"], ["Extensiones de propiedades", "propertyExtensions"],
      ["Acciones detectadas", "actions"], ["Extensiones de acciones", "actionExtensions"],
      ["Formularios", "forms"], ["Extensiones de formularios", "formExtensions"],
      ["Bloques de navegación", "navigators"], ["Grupos de propiedades", "groups"],
      ["Diseños", "designs"], ["Ventanas", "windows"], ["Metacódigo", "metaStatements"],
      ["Tablas", "tables"], ["Restricciones", "constraints"], ["Índices", "indexes"],
      ["Eventos WHEN", "whenEvents"], ["Eventos ON", "onEvents"],
      ["Eventos BEFORE", "beforeStatements"], ["Eventos AFTER", "afterStatements"],
      ["Marcas API", "apiAnnotations"], ["Marcas no-auth", "noAuthAnnotations"],
      ["Invocaciones de macros", "macroInvocations"],
    ];
    for (const [label, key] of groups) {
      const names = declarationNames(module, key);
      lines.push("- **" + label + " (" + names.length + "):** " + (names.join(", ") || "—"));
    }
    lines.push("");
  }

  lines.push("## lsFusion 6.2 — módulos LSF del servidor", "");
  lines.push("| Módulo | Ruta | Namespace | REQUIRE | Clases | Propiedades | Acciones | Formularios | Eventos | API | En RubrovaCustom |");
  lines.push("|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|");
  for (const module of [...catalog.lsFusion.modules].sort((a, b) => a.moduleName.localeCompare(b.moduleName))) {
    const c = module.counts;
    lines.push("| " + [
      escapeMarkdownCell(module.moduleName), escapeMarkdownCell(module.path),
      escapeMarkdownCell(module.namespace || "—"), escapeMarkdownCell(module.requires.join(", ") || "—"),
      c.classes + c.classExtensions, c.properties, c.actions, c.forms + c.formExtensions,
      c.whenEvents + c.onEvents, c.apiAnnotations, module.reachableFromApplicationRoot ? "Sí" : "No",
    ].join(" | ") + " |");
  }

  lines.push("", "## Extensiones propias de Rubrova", "");
  lines.push("| Módulo | Ruta | Namespace | REQUIRE | Clases | Propiedades | Acciones | Formularios | API |");
  lines.push("|---|---|---|---|---:|---:|---:|---:|---:|");
  for (const module of [...catalog.rubrovaExtensions.modules].sort((a, b) => a.moduleName.localeCompare(b.moduleName))) {
    const c = module.counts;
    lines.push("| " + [
      escapeMarkdownCell(module.moduleName), escapeMarkdownCell(module.path),
      escapeMarkdownCell(module.namespace || "—"), escapeMarkdownCell(module.requires.join(", ") || "—"),
      c.classes + c.classExtensions, c.properties, c.actions, c.forms + c.formExtensions, c.apiAnnotations,
    ].join(" | ") + " |");
  }

  lines.push("", "## MyCompany 6.2 — recursos que complementan los módulos LSF", "");
  lines.push("| Tipo de recurso | Cantidad |");
  lines.push("|---|---:|");
  for (const [category, count] of Object.entries(catalog.myCompanyProject.categoryCounts).sort(([a], [b]) => a.localeCompare(b))) {
    lines.push("| " + escapeMarkdownCell(category) + " | " + count + " |");
  }

  lines.push("", "### Plantillas de reportes e impresión JRXML", "");
  for (const file of catalog.myCompanyProject.reportTemplates) lines.push("- " + file);
  lines.push("", "### JavaScript y CSS", "");
  for (const file of catalog.myCompanyProject.webAssets) lines.push("- " + file);
  lines.push("", "### Extensiones Java propias", "");
  for (const item of catalog.myCompanyProject.javaSources) {
    const types = item.topLevelTypes.map((type) => type.kind + " " + type.name + " (L" + type.line + ")").join(", ") || "sin tipo público detectado";
    lines.push("- " + item.path + " — paquete " + item.packageName + "; " + types + "; imports: " + item.importCount);
  }
  lines.push("", "### Bundles, configuración y SQL", "");
  for (const file of catalog.myCompanyProject.propertyFiles) lines.push("- " + file);
  for (const file of catalog.myCompanyProject.sqlScripts) lines.push("- " + file);
  lines.push("", "### Imágenes y otros recursos", "");
  for (const file of catalog.myCompanyProject.imageAssets) lines.push("- " + file);
  const listedMyCompany = new Set([
    ...catalog.myCompanyProject.reportTemplates,
    ...catalog.myCompanyProject.webAssets,
    ...catalog.myCompanyProject.javaSources.map((item) => item.path),
    ...catalog.myCompanyProject.propertyFiles,
    ...catalog.myCompanyProject.sqlScripts,
    ...catalog.myCompanyProject.imageAssets,
  ]);
  for (const item of catalog.myCompanyProject.files) {
    if (item.extension !== ".lsf" && item.extension !== ".md" && !listedMyCompany.has(item.path)) {
      lines.push("- " + item.path + " — " + item.category);
    }
  }

  lines.push("", "## lsFusion 6.2 — registro de las 3.330 fuentes Java", "");
  lines.push("| Módulo Maven | Paquete Java | Tipos de nivel superior detectados | Imports | Líneas | Archivo |");
  lines.push("|---|---|---|---:|---:|---|");
  for (const item of catalog.lsFusion.javaSourceCatalog) {
    const mavenModule = item.path.slice(PLATFORM_ROOT.length + 1).split("/")[0];
    const types = item.topLevelTypes.map((type) => type.kind + " " + type.name).join(", ") || "No detectado";
    lines.push("| " + [
      escapeMarkdownCell(mavenModule),
      escapeMarkdownCell(item.packageName),
      escapeMarkdownCell(types),
      item.importCount,
      item.lineCount,
      escapeMarkdownCell(item.path),
    ].join(" | ") + " |");
  }

  lines.push("", "## lsFusion — demás recursos del proyecto", "");
  lines.push("| Extensión | Cantidad |");
  lines.push("|---|---:|");
  for (const [extension, count] of Object.entries(catalog.lsFusion.projectExtensionCounts).sort(([a], [b]) => a.localeCompare(b))) {
    lines.push("| " + escapeMarkdownCell(extension) + " | " + count + " |");
  }
  lines.push("");
  const listedPlatformCode = new Set([
    ...catalog.lsFusion.javaSourceCatalog.map((item) => item.path),
    ...catalog.lsFusion.modules.map((item) => item.path),
  ]);
  for (const file of catalog.lsFusion.projectFiles) {
    if (!listedPlatformCode.has(file) && !file.endsWith(".md")) lines.push("- " + file);
  }

  lines.push("", "## Advertencias de interpretación", "");
  lines.push("- Los módulos fuera del cierre de RubrovaCustom no se consideran descartados.");
  lines.push("- Los documentos indicados por carpeta son candidatos; la relación módulo-documento debe confirmarse leyendo el contenido.");
  lines.push("- Las clases, formularios, propiedades y acciones generadas por metacódigo o macros pueden no aparecer en los conteos estáticos.");
  lines.push("- La cantidad de acciones sin palabra clave es heurística y se debe revisar en los casos ambiguos.");
  lines.push("- Este registro no describe reglas de negocio, estados, transacciones, permisos, integraciones externas ni efectos en ledgers. Eso requiere la ficha funcional y evidencia definidas en el manual de ingeniería.");
  return lines.join("\n") + "\n";
}

function runCli() {
  const args = process.argv.slice(2);
  let outputPath = null;
  let markdownOutputPath = null;
  for (let i = 0; i < args.length; i += 1) {
    if (args[i] === "--json-output") {
      outputPath = args[i + 1];
      if (!outputPath) throw new Error("Falta la ruta después de --json-output.");
      i += 1;
    } else if (args[i] === "--markdown-output") {
      markdownOutputPath = args[i + 1];
      if (!markdownOutputPath) throw new Error("Falta la ruta después de --markdown-output.");
      i += 1;
    } else if (args[i] === "--help" || args[i] === "-h") {
      console.log("Uso: node scripts/platform/audit-lsf-source.mjs [--json-output archivo.json] [--markdown-output registro.md]");
      return;
    } else {
      throw new Error("Argumento no reconocido: " + args[i]);
    }
  }

  const catalog = buildSourceCatalog();
  console.log("Catálogo estructural de fuentes Rubrova");
  console.log("Raíz de aplicación: " + catalog.applicationComposition.rootModule + ".");
  console.log("Composición alcanzable: " + catalog.applicationComposition.resolvedModuleCount + " módulos; MyCompany " + catalog.applicationComposition.sourceModuleCounts.myCompany + ", plataforma " + catalog.applicationComposition.sourceModuleCounts.lsFusion + ", Rubrova " + catalog.applicationComposition.sourceModuleCounts.rubrova + ".");
  console.log("Dependencias sin resolver: " + catalog.applicationComposition.unresolvedRequirements.length + ".");
  console.log("MyCompany 6.2: " + catalog.myCompany.lsfFileCount + " módulos LSF (lock: " + catalog.myCompany.lockedLsfFileCount + "); fuera de la composición: " + catalog.myCompany.outsideApplicationClosureCount + ".");
  console.log("Extensiones propias: " + catalog.rubrovaExtensions.lsfFileCount + " módulos LSF.");
  const declarationTotals = [...catalog.myCompany.modules, ...catalog.lsFusion.modules, ...catalog.rubrovaExtensions.modules].reduce((total, module) => {
    for (const key of ["properties", "propertyExtensions", "actions", "actionExtensions", "classes", "classExtensions", "forms", "formExtensions", "navigators", "constraints", "whenEvents", "onEvents", "metaStatements", "macroInvocations"]) total[key] = (total[key] || 0) + (module.counts[key] || 0);
    return total;
  }, {});
  console.log("Declaraciones detectadas (fuente, sin expansión de macros): " + JSON.stringify(declarationTotals) + ".");
  console.log("MyCompany: " + catalog.myCompanyProject.fileCount + " archivos de proyecto, incluidos " + catalog.myCompanyProject.reportTemplates.length + " plantillas JRXML, " + catalog.myCompanyProject.webAssets.length + " recursos JS/CSS y " + catalog.myCompanyProject.javaSourceCount + " clases Java.");
  console.log("lsFusion 6.2: " + catalog.lsFusion.projectFileCount + " archivos de proyecto, " + catalog.lsFusion.lsfFileCount + " módulos LSF y " + catalog.lsFusion.javaSourceFileCount + " fuentes Java.");
  console.log("Documentación: inglés " + catalog.lsFusion.documentationAssets.en.markdown + " Markdown + " + catalog.lsFusion.documentationAssets.en.images + " imágenes; ruso " + catalog.lsFusion.documentationAssets.ru.markdown + " Markdown + " + catalog.lsFusion.documentationAssets.ru.images + " imágenes.");

  if (outputPath) {
    const absolute = path.resolve(outputPath);
    mkdirSync(path.dirname(absolute), { recursive: true });
    writeFileSync(absolute, JSON.stringify(catalog, null, 2) + "\n", "utf8");
    console.log("Informe JSON: " + absolute);
  }
  if (markdownOutputPath) {
    const absolute = path.resolve(markdownOutputPath);
    mkdirSync(path.dirname(absolute), { recursive: true });
    writeFileSync(absolute, renderModuleRegisterMarkdown(catalog), "utf8");
    console.log("Registro Markdown: " + absolute);
  }
  if (!catalog.quality.myCompanyCountMatchesLock || !catalog.quality.platformJavaCountMatchesLock) {
    throw new Error("Los conteos de fuentes no coinciden con los locks fijados.");
  }
  if (catalog.quality.filesWithoutModuleHeader.length > 0) {
    throw new Error("Hay archivos .lsf sin declaración MODULE; requieren clasificación.");
  }
  if (catalog.myCompany.duplicateModuleNames.length > 0) {
    throw new Error("Hay nombres de módulo MyCompany duplicados; revisar el catálogo.");
  }
  if (!catalog.quality.applicationDependenciesResolved) {
    throw new Error("La composición RubrovaCustom contiene dependencias sin resolver; revisar el grafo.");
  }
  if (catalog.rubrovaExtensions.lsfFileCount === 0) {
    throw new Error("No se encontraron las extensiones LSF de Rubrova.");
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
