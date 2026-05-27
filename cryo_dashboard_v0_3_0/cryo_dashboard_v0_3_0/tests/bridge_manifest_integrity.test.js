import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { buildBridgeManifest } from "../scripts/generate-bridge-manifest.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.join(__dirname, "..");

function readJson(relativePath) {
  return JSON.parse(fs.readFileSync(path.join(projectRoot, relativePath), "utf8"));
}

function readText(relativePath) {
  return fs.readFileSync(path.join(projectRoot, relativePath), "utf8").trim();
}

console.log("Running bridge manifest integrity checks...");

const committedManifest = readJson("bridge_manifest.json");
const generatedManifest = buildBridgeManifest();
const fileIndex = readJson("file_index.json");
const materials = readJson("data/materials.json");
const version = readText("VERSION");

assert.deepEqual(committedManifest, generatedManifest);
assert.equal(committedManifest.release.version, version);
assert.equal(committedManifest.materials_dataset.version, materials.version);
assert.equal(
  committedManifest.materials_dataset.material_count,
  Object.keys(materials.materials || {}).length
);
assert.deepEqual(
  committedManifest.artifact_paths.minimum_artifacts,
  fileIndex.minimum_artifacts
);

for (const relativePath of [
  committedManifest.producer.primary_runtime.html,
  committedManifest.producer.primary_runtime.orchestrator,
  committedManifest.materials_dataset.path,
  committedManifest.producer.bridge_contract_doc,
  ...committedManifest.producer.artifact_index_files,
  committedManifest.artifact_paths.bridge_manifest
]) {
  assert.ok(fs.existsSync(path.join(projectRoot, relativePath)), `Missing bridge artifact: ${relativePath}`);
}

assert.equal(committedManifest.validation.command, "npm test");
assert.equal(committedManifest.validation.working_directory, "cryo_dashboard_v0_3_0/cryo_dashboard_v0_3_0");
assert.equal(committedManifest.validation.status, "required-before-handoff");
assert.equal(committedManifest.consumers.CODEX.ingest_from[0], "file_index.json");
assert.equal(committedManifest.release.release_timestamp_utc, null);

console.log("Bridge manifest integrity checks passed.");
