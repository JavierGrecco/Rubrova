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

export function parseLsfSource(source, filePath = "") {
  const code = maskLsfNonCode(source);
  const moduleName = code.match(/^\s*MODULE\s+([A-Za-z_][A-Za-z0-9_]*)\s*;/m)?.[1] || null;
  const namespace = code.match(/^\s*NAMESPACE\s+([A-Za-z_][A-Za-z0-9_.]*)\s*;/m)?.[1] || null;
  const requireBody = code.match(/^\s*REQUIRE\b([\s\S]*?);/m)?.[1] || "";
  const requires = requireBody.split(",").map((part) => part.trim()).filter(Boolean);

  const declarations = {
    classes: declarationMatches(code, /^(?:EXTEND\s+)?CLASS\s+(?:ABSTRACT\s+)?([A-Za-z_][A-Za-z0-9_]*)/gm),
    forms: declarationMatches(code, /^(?:EXTEND\s+)?FORM\s+([A-Za-z_][A-Za-z0-9_]*)/gm),
    navigators: declarationMatches(code, /^(?:EXTEND\s+)?NAVIGATOR\b/gm).map((x) => ({ ...x, name: null })),
    tables: declarationMatches(code, /^TABLE\s+([A-Za-z_][A-Za-z0-9_]*)/gm),
    constraints: declarationMatches(code, /^CONSTRAINT\b/gm).map((x) => ({ ...x, name: null })),
    indexes: declarationMatches(code, /^INDEX\s+([A-Za-z_][A-Za-z0-9_]*)/gim),
    whenEvents: declarationMatches(code, /^WHEN\b/gm).map((x) => ({ ...x, name: null })),
    onEvents: declarationMatches(code, /^ON\b/gm).map((x) => ({ ...x, name: null })),
    apiAnnotations: declarationMatches(code, /@@api\b/gm).map((x) => ({ ...x, name: null })),
    noAuthAnnotations: declarationMatches(code, /@@noauth\b/gm).map((x) => ({ ...x, name: null })),
  };

  const counts = Object.fromEntries(
    Object.entries(declarations).map(([key, values]) => [key, values.length]),
  );

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

  const myFiles = walkFiles(myRoot, ".lsf");
  const platformFiles = walkFiles(platformRoot, ".lsf");
  const extensionFiles = walkFiles(extensionsRoot, ".lsf");
  const myModules = myFiles.map((file) => parseLsfSource(readFileSync(path.join(root, file), "utf8"), file));
  const platformModules = platformFiles.map((file) => parseLsfSource(readFileSync(path.join(root, file), "utf8"), file));
  const extensionModules = extensionFiles.map((file) => parseLsfSource(readFileSync(path.join(root, file), "utf8"), file));
  const myJavaFiles = walkFiles(platformRoot, ".java");

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
    method: "Inventario estático de archivos y declaraciones LSF; no interpreta la semántica ni valida la ejecución.",
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
    lsFusion: {
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

function runCli() {
  const args = process.argv.slice(2);
  let outputPath = null;
  for (let i = 0; i < args.length; i += 1) {
    if (args[i] === "--json-output") {
      outputPath = args[i + 1];
      if (!outputPath) throw new Error("Falta la ruta después de --json-output.");
      i += 1;
    } else if (args[i] === "--help" || args[i] === "-h") {
      console.log("Uso: node scripts/platform/audit-lsf-source.mjs [--json-output archivo.json]");
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
  console.log("lsFusion 6.2: " + catalog.lsFusion.lsfFileCount + " archivos LSF, " + catalog.lsFusion.javaSourceFileCount + " fuentes Java.");
  console.log("Documentación: inglés " + catalog.lsFusion.documentationAssets.en.markdown + " Markdown + " + catalog.lsFusion.documentationAssets.en.images + " imágenes; ruso " + catalog.lsFusion.documentationAssets.ru.markdown + " Markdown + " + catalog.lsFusion.documentationAssets.ru.images + " imágenes.");

  if (outputPath) {
    const absolute = path.resolve(outputPath);
    mkdirSync(path.dirname(absolute), { recursive: true });
    writeFileSync(absolute, JSON.stringify(catalog, null, 2) + "\n", "utf8");
    console.log("Informe JSON: " + absolute);
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
