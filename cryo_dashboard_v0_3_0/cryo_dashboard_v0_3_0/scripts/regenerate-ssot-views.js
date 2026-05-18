import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT = path.resolve(__dirname, "..");

function withTrailingNewline(text) {
  return text.endsWith("\n") ? text : `${text}\n`;
}

function ensureVersionPrefix(version) {
  return version.startsWith("v") ? version : `v${version}`;
}

function serializeYamlValue(value, indentLevel = 0) {
  const indent = "  ".repeat(indentLevel);

  if (Array.isArray(value)) {
    return value.flatMap(item => {
      if (item && typeof item === "object") {
        const entries = Object.entries(item);
        if (entries.length === 0) {
          return [`${indent}- {}`];
        }

        const [[firstKey, firstValue], ...rest] = entries;
        const firstLineValue = isScalar(firstValue) ? formatScalar(firstValue) : "";
        const lines = [`${indent}- ${firstKey}:${firstLineValue ? ` ${firstLineValue}` : ""}`];
        if (!isScalar(firstValue)) {
          lines.push(...serializeYamlValue(firstValue, indentLevel + 2));
        }
        for (const [key, nestedValue] of rest) {
          if (isScalar(nestedValue)) {
            lines.push(`${indent}  ${key}: ${formatScalar(nestedValue)}`);
          } else {
            lines.push(`${indent}  ${key}:`);
            lines.push(...serializeYamlValue(nestedValue, indentLevel + 2));
          }
        }
        return lines;
      }

      return [`${indent}- ${formatScalar(item)}`];
    });
  }

  if (value && typeof value === "object") {
    return Object.entries(value).flatMap(([key, nestedValue]) => {
      if (isScalar(nestedValue)) {
        return [`${indent}${key}: ${formatScalar(nestedValue)}`];
      }
      return [`${indent}${key}:`, ...serializeYamlValue(nestedValue, indentLevel + 1)];
    });
  }

  return [`${indent}${formatScalar(value)}`];
}

function isScalar(value) {
  return value == null || ["string", "number", "boolean"].includes(typeof value);
}

function formatScalar(value) {
  if (typeof value === "string") {
    return value;
  }
  if (value == null) {
    return "null";
  }
  return String(value);
}

export function getReleaseMetadata(root = ROOT) {
  const version = ensureVersionPrefix(fs.readFileSync(path.join(root, "VERSION"), "utf8").trim());
  const bareVersion = version.slice(1);
  const packageJson = JSON.parse(fs.readFileSync(path.join(root, "package.json"), "utf8"));
  const changelogText = fs.readFileSync(path.join(root, "docs", "CHANGELOG.md"), "utf8");
  const dateMatch = changelogText.match(/## v0\.4\.9[\s\S]*?\*\*Date:\*\*\s*([0-9-]+)/);

  return {
    root,
    version,
    bareVersion,
    updated: dateMatch?.[1] ?? new Date().toISOString().slice(0, 10),
    packageVersion: packageJson.version,
    currentSessionHandover: `docs/CRYO_DASHBOARD_SESSION_HANDOVER_${version}.md`,
    nistReport: `docs/NIST_PARITY_TEST_REPORT_${version}.md`,
    deploymentChecklist: "docs/GITHUB_PAGES_DEPLOYMENT_CHECKLIST.md",
    ssotPipeline: `docs/SSOT_REGENERATION_PIPELINE_${version}.md`,
    fileIndexSnapshot: `FILE_INDEX_${version}.md`
  };
}

export function buildFileIndexData(metadata = getReleaseMetadata()) {
  return {
    version: metadata.version,
    updated: metadata.updated,
    project: "cryogenic-material-dashboard",
    repository: "GBOGEB/document-organization-system",
    subtree: "cryo_dashboard_v0_3_0/cryo_dashboard_v0_3_0",
    human_start_here: [
      "index.html",
      "files.html",
      "README.md",
      "dashboard_modular.html"
    ],
    machine_readable_note: "Use files.html for human navigation and this file or file_index.yaml for scripted intake.",
    primary_runtime: {
      file: "dashboard_modular.html",
      access: "github-pages-or-localhost"
    },
    legacy_fallback: {
      file: "material_properties_dashboard_v1_10.html",
      access: "file-double-click-supported"
    },
    minimum_artifacts: [
      "index.html",
      "files.html",
      "dashboard_modular.html",
      "data/materials.json",
      "js/app_modular.js",
      "js/materials.js",
      "README.md",
      "FINAL_HANDOVER.md",
      "SESSION_SUMMARY.md",
      "docs/CHANGELOG.md",
      metadata.currentSessionHandover,
      metadata.nistReport,
      metadata.deploymentChecklist,
      metadata.ssotPipeline,
      metadata.fileIndexSnapshot,
      "VERSION"
    ],
    canonical_docs: [
      "README.md",
      "FINAL_HANDOVER.md",
      "SESSION_SUMMARY.md",
      "docs/CHANGELOG.md",
      metadata.currentSessionHandover,
      metadata.nistReport,
      metadata.deploymentChecklist,
      metadata.ssotPipeline,
      metadata.fileIndexSnapshot,
      "DASHBOARD_TESTING_GUIDE.md",
      "GIT_TRACKING_MANIFEST.md"
    ],
    companion_indexes: [
      "file_index.yaml",
      "file_index.json"
    ],
    runtime_files: [
      "index.html",
      "files.html",
      "dashboard_modular.html",
      "html_preview_hub.html",
      "ssot_launcher.html",
      "index_slides.html",
      "material_properties_dashboard_v1_10.html",
      "data/materials.json"
    ]
  };
}

export function buildFileIndexMarkdown(metadata = getReleaseMetadata(), fileIndexData = buildFileIndexData(metadata)) {
  const docLines = fileIndexData.canonical_docs.map(file => `- \`${file}\``).join("\n");

  return withTrailingNewline(`<!-- markdownlint-disable MD022 MD032 MD036 -->

# FILE INDEX ${metadata.version}
**Updated:** ${metadata.updated}  
**Purpose:** Canonical navigation index for the ${metadata.version} package.  
**Source:** Generated from \`VERSION\` and \`scripts/regenerate-ssot-views.js\`.

## 1) Dashboard UI

- \`index.html\` — landing page and version selector
- \`dashboard_modular.html\` — modular dashboard (${metadata.version})
- \`files.html\` — file browser and documentation hub
- \`html_preview_hub.html\` — visual preview hub for HTML entry points
- \`ssot_launcher.html\` — SSOT launcher view
- \`index_slides.html\` — SSOT presentation deck
- \`material_properties_dashboard_v1_10.html\` — legacy single-file dashboard
- \`style.css\` — shared styling

## 2) JavaScript Modules

- \`js/app_modular.js\` — modular dashboard controller
- \`js/materials.js\` — NIST property evaluators
- \`js/numerics.js\` — Trapezoid, Simpson, Romberg, Gauss-Legendre
- \`js/plots.js\` — Plotly rendering and PNG export
- \`js/export.js\` — CSV/JSON export

## 3) Data, Schema, Tests

- \`data/materials.json\` — material database
- \`schemas/materials.schema.json\` — materials schema
- \`tests/numerics.test.js\` — Node numerics tests
- \`tests/export.test.js\` — CSV/JSON export consistency checks
- \`tests/materials.validate.js\` — materials validation tests
- \`tests/file_index_integrity.test.js\` — generated file-index integrity checks
- \`tests/static_entrypoints.test.js\` — static entrypoint and reference checks
- \`tests/nist_parity.test.js\` — NIST parity regression suite

## 4) Canonical Documentation

${docLines}

## 5) Scripts and Metadata

- \`VERSION\` — source-of-truth release version
- \`package.json\` — scripts and metadata
- \`scripts/regenerate-ssot-views.js\` — deterministic generator for file-index artifacts
- \`scripts/version-coherence-check.js\` — active version consistency validation
- \`file_index.yaml\`, \`file_index.json\` — generated machine-readable intake indexes

## Summary

- Active version: **${metadata.version}**
- Machine-readable indexes: **file_index.yaml, file_index.json**
- Primary start page: \`index.html\`

*End of generated file index*
`);
}

export function buildReleaseArtifacts(metadata = getReleaseMetadata()) {
  const fileIndexData = buildFileIndexData(metadata);
  return {
    metadata,
    fileIndexData,
    fileIndexJson: withTrailingNewline(JSON.stringify(fileIndexData, null, 2)),
    fileIndexYaml: withTrailingNewline(serializeYamlValue(fileIndexData).join("\n")),
    fileIndexMarkdown: buildFileIndexMarkdown(metadata, fileIndexData)
  };
}

function compareFile(expectedText, filePath) {
  const actualText = fs.readFileSync(filePath, "utf8");
  if (actualText !== expectedText) {
    throw new Error(`Generated artifact is stale: ${path.relative(ROOT, filePath)}`);
  }
}

function ensureReferencedFilesExist(metadata, fileIndexData, { allowGeneratedTargets = false } = {}) {
  const generatedTargets = new Set([
    metadata.fileIndexSnapshot,
    ...fileIndexData.companion_indexes
  ]);
  const referencedPaths = new Set([
    ...fileIndexData.human_start_here,
    fileIndexData.primary_runtime.file,
    fileIndexData.legacy_fallback.file,
    ...fileIndexData.minimum_artifacts,
    ...fileIndexData.canonical_docs,
    ...fileIndexData.companion_indexes,
    ...fileIndexData.runtime_files,
    metadata.fileIndexSnapshot
  ]);

  for (const relativePath of referencedPaths) {
    if (allowGeneratedTargets && generatedTargets.has(relativePath)) {
      continue;
    }
    const absolutePath = path.join(ROOT, relativePath);
    if (!fs.existsSync(absolutePath)) {
      throw new Error(`Referenced artifact does not exist: ${relativePath}`);
    }
  }
}

function writeArtifacts(artifacts) {
  fs.writeFileSync(path.join(ROOT, "file_index.json"), artifacts.fileIndexJson);
  fs.writeFileSync(path.join(ROOT, "file_index.yaml"), artifacts.fileIndexYaml);
  fs.writeFileSync(path.join(ROOT, artifacts.metadata.fileIndexSnapshot), artifacts.fileIndexMarkdown);
}

function printPlan(artifacts) {
  const { metadata, fileIndexData } = artifacts;
  console.log(`Release metadata plan for ${metadata.version}`);
  console.log(`- update file_index.json`);
  console.log(`- update file_index.yaml`);
  console.log(`- update ${metadata.fileIndexSnapshot}`);
  console.log(`- current session handover: ${metadata.currentSessionHandover}`);
  console.log(`- current parity report: ${metadata.nistReport}`);
  console.log(`- minimum artifacts: ${fileIndexData.minimum_artifacts.length}`);
  console.log(`- canonical docs: ${fileIndexData.canonical_docs.length}`);
}

function checkArtifacts(artifacts) {
  compareFile(artifacts.fileIndexJson, path.join(ROOT, "file_index.json"));
  compareFile(artifacts.fileIndexYaml, path.join(ROOT, "file_index.yaml"));
  compareFile(artifacts.fileIndexMarkdown, path.join(ROOT, artifacts.metadata.fileIndexSnapshot));
  ensureReferencedFilesExist(artifacts.metadata, artifacts.fileIndexData);
}

function runCli() {
  const artifacts = buildReleaseArtifacts();
  const arg = process.argv[2];

  if (arg === "--plan") {
    printPlan(artifacts);
    return;
  }

  if (arg === "--check") {
    checkArtifacts(artifacts);
    console.log(`SSOT views are up to date for ${artifacts.metadata.version}.`);
    return;
  }

  if (arg && arg !== "--write") {
    throw new Error(`Unsupported option: ${arg}`);
  }

  ensureReferencedFilesExist(artifacts.metadata, artifacts.fileIndexData, { allowGeneratedTargets: true });
  writeArtifacts(artifacts);
  console.log(`Regenerated SSOT views for ${artifacts.metadata.version}.`);
}

if (process.argv[1] === __filename) {
  runCli();
}
