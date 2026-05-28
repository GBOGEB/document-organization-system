import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, "..");

function readJson(relativePath) {
  return JSON.parse(fs.readFileSync(path.join(projectRoot, relativePath), "utf8"));
}

function readText(relativePath) {
  return fs.readFileSync(path.join(projectRoot, relativePath), "utf8").trim();
}

export function buildBridgeManifest() {
  const version = readText("VERSION");
  const fileIndex = readJson("file_index.json");
  const materials = readJson("data/materials.json");
  const materialKeys = Object.keys(materials.materials || {});

  return {
    contract_version: "1.0.0",
    producer: {
      repository: "GBOGEB/document-organization-system",
      subtree: "cryo_dashboard_v0_3_0/cryo_dashboard_v0_3_0",
      role: "canonical-dashboard-runtime-and-artifact-source",
      primary_runtime: {
        html: "dashboard_modular.html",
        orchestrator: "js/app_modular.js"
      },
      artifact_index_files: ["file_index.yaml", "file_index.json"],
      bridge_contract_doc: "docs/CODEX_ABACUS_BRIDGE_CONTRACT.md"
    },
    release: {
      version,
      release_timestamp_utc: null,
      source_of_truth: "VERSION"
    },
    artifact_paths: {
      minimum_artifacts: fileIndex.minimum_artifacts,
      companion_indexes: fileIndex.companion_indexes,
      bridge_manifest: "bridge_manifest.json"
    },
    materials_dataset: {
      path: "data/materials.json",
      version: materials.version,
      material_count: materialKeys.length,
      source_family: "NIST"
    },
    validation: {
      command: "npm test",
      working_directory: "cryo_dashboard_v0_3_0/cryo_dashboard_v0_3_0",
      status: "required-before-handoff"
    },
    consumers: {
      CODEX: {
        role: "integration-control-and-pr-lineage",
        ingest_from: ["file_index.json", "bridge_manifest.json"],
        must_receive: [
          "release.version",
          "artifact_paths.minimum_artifacts",
          "materials_dataset",
          "validation",
          "release.release_timestamp_utc"
        ],
        must_not: [
          "duplicate-dashboard-runtime-state",
          "become-source-of-truth-for-materials",
          "override-release-metadata"
        ]
      },
      ABACUS: {
        role: "downstream-analytics-consumer",
        consume_only: [
          "published-artifacts",
          "validation-evidence",
          "release-metadata"
        ],
        may_publish_back: [
          "analytics-summaries",
          "release-acknowledgements"
        ],
        must_not: [
          "mutate-runtime-files",
          "become-second-source-of-truth",
          "consume-unpublished-dashboard-structure"
        ]
      }
    },
    next_steps: [
      "refresh bridge_manifest.json after source-artifact changes",
      "run npm test before bridge handoff",
      "handoff published payload to CODEX before ABACUS consumption"
    ]
  };
}

export function writeBridgeManifest() {
  const manifest = buildBridgeManifest();
  const outputPath = path.join(projectRoot, "bridge_manifest.json");
  fs.writeFileSync(outputPath, `${JSON.stringify(manifest, null, 2)}\n`);
  return manifest;
}

if (process.argv[1] && path.resolve(process.argv[1]) === __filename) {
  writeBridgeManifest();
}
