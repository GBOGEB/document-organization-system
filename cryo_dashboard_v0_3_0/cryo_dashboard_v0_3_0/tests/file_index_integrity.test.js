import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { buildReleaseArtifacts, getReleaseMetadata } from "../scripts/regenerate-ssot-views.js";

function escapeRegexLiteral(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function parseYamlList(yamlText, key) {
  const escapedKey = escapeRegexLiteral(key);
  const pattern = new RegExp(`^${escapedKey}:\\n((?:  - .+\\n)+)`, "m");
  const match = yamlText.match(pattern);
  assert.ok(match, `Missing YAML list for key: ${key}`);
  return match[1]
    .trimEnd()
    .split("\n")
    .map(line => line.replace(/^  -\s*/, ""));
}

function parseYamlNestedScalar(yamlText, parentKey, childKey) {
  const escapedParentKey = escapeRegexLiteral(parentKey);
  const escapedChildKey = escapeRegexLiteral(childKey);
  const pattern = new RegExp(`^${escapedParentKey}:\\n(?:  .+\\n)*?  ${escapedChildKey}:\\s*(.+)$`, "m");
  const match = yamlText.match(pattern);
  assert.ok(match, `Missing YAML nested scalar: ${parentKey}.${childKey}`);
  return match[1].trim();
}

function parseYamlNestedList(yamlText, parentKey, childKey) {
  const escapedParentKey = escapeRegexLiteral(parentKey);
  const escapedChildKey = escapeRegexLiteral(childKey);
  const pattern = new RegExp(`^${escapedParentKey}:\\n(?:  .+\\n)*?  ${escapedChildKey}:\\n((?:    - .+\\n)+)`, "m");
  const match = yamlText.match(pattern);
  assert.ok(match, `Missing YAML nested list: ${parentKey}.${childKey}`);
  return match[1]
    .trimEnd()
    .split("\n")
    .map(line => line.replace(/^    -\s*/, ""));
}

function collectFolderBuckets(paths) {
  const buckets = new Set();
  for (const relativePath of paths) {
    const slashIndex = relativePath.indexOf("/");
    if (slashIndex === -1) {
      buckets.add(".");
      continue;
    }
    buckets.add(relativePath.slice(0, slashIndex));
  }
  return buckets;
}

function assertRelativePathsExist(paths) {
  for (const relativePath of paths) {
    assert.ok(fs.existsSync(relativePath), `Missing referenced artifact: ${relativePath}`);
  }
}

const metadata = getReleaseMetadata();
const artifacts = buildReleaseArtifacts(metadata);
const yamlText = fs.readFileSync("./file_index.yaml", "utf8");
const jsonText = fs.readFileSync("./file_index.json", "utf8");
const jsonIndex = JSON.parse(jsonText);
const markdownSnapshotPath = path.join(".", metadata.fileIndexSnapshot);
const markdownSnapshotText = fs.readFileSync(markdownSnapshotPath, "utf8");

console.log("Running file index integrity checks...");

assert.equal(jsonText, artifacts.fileIndexJson, "file_index.json must match generated SSOT output");
assert.equal(yamlText, artifacts.fileIndexYaml, "file_index.yaml must match generated SSOT output");
assert.equal(markdownSnapshotText, artifacts.fileIndexMarkdown, `${metadata.fileIndexSnapshot} must match generated SSOT output`);
assert.equal(jsonIndex.version, metadata.version, "file_index.json version must match VERSION");
assert.match(markdownSnapshotText, new RegExp(escapeRegexLiteral(`# FILE INDEX ${metadata.version}`)));

const yamlMinimumArtifacts = parseYamlList(yamlText, "minimum_artifacts");
const yamlCompanionIndexes = parseYamlList(yamlText, "companion_indexes");
const yamlCanonicalDocs = parseYamlList(yamlText, "canonical_docs");
const yamlRuntimeFiles = parseYamlList(yamlText, "runtime_files");
const yamlHumanStartHere = parseYamlList(yamlText, "human_start_here");
const yamlVersion = yamlText.match(/^version:\s*(.+)$/m)?.[1]?.trim();
const yamlLegacyFallbackFile = parseYamlNestedScalar(yamlText, "legacy_fallback", "file");
const yamlBridgeContractDoc = parseYamlNestedScalar(yamlText, "bridge_artifacts", "contract_doc");
const yamlBridgeManifest = parseYamlNestedScalar(yamlText, "bridge_artifacts", "manifest");
const yamlBridgeConsumers = parseYamlNestedList(yamlText, "bridge_artifacts", "consumers");
const releaseVersion = fs.readFileSync("./VERSION", "utf8").trim();

assert.deepEqual(yamlMinimumArtifacts, jsonIndex.minimum_artifacts);
assert.deepEqual(yamlCompanionIndexes, jsonIndex.companion_indexes);
assert.deepEqual(yamlCanonicalDocs, jsonIndex.canonical_docs);
assert.deepEqual(yamlRuntimeFiles, jsonIndex.runtime_files);
assert.deepEqual(yamlHumanStartHere, jsonIndex.human_start_here);
assert.equal(yamlVersion, jsonIndex.version);
assert.equal(jsonIndex.version, releaseVersion);
assert.equal(yamlLegacyFallbackFile, jsonIndex.legacy_fallback.file);
assert.equal(yamlBridgeContractDoc, jsonIndex.bridge_artifacts.contract_doc);
assert.equal(yamlBridgeManifest, jsonIndex.bridge_artifacts.manifest);
assert.deepEqual(yamlBridgeConsumers, jsonIndex.bridge_artifacts.consumers);

const primaryRuntimeFile = jsonIndex.primary_runtime.file;
assert.notEqual(primaryRuntimeFile, yamlLegacyFallbackFile);
assert.ok(yamlMinimumArtifacts.includes(primaryRuntimeFile));
assert.ok(yamlRuntimeFiles.includes(primaryRuntimeFile));
assert.ok(yamlCanonicalDocs.includes(metadata.currentSessionHandover));
assert.ok(yamlCanonicalDocs.includes(metadata.nistReport));
assert.ok(yamlCanonicalDocs.includes(metadata.deploymentChecklist));
assert.ok(yamlCanonicalDocs.includes(metadata.ssotPipeline));
assert.ok(yamlCanonicalDocs.includes(metadata.fileIndexSnapshot));

const nonFallbackArtifacts = yamlMinimumArtifacts.filter(artifactPath => artifactPath !== yamlLegacyFallbackFile);
assert.ok(nonFallbackArtifacts.length > 0, "Fallback-only artifact set is not allowed");

const folderBuckets = collectFolderBuckets(yamlMinimumArtifacts);
assert.ok(folderBuckets.has("."), "Expected root-level artifacts");
assert.ok(folderBuckets.has("data"), "Expected data/ artifacts in consolidation");
assert.ok(folderBuckets.has("js"), "Expected js/ artifacts in consolidation");
assert.ok(folderBuckets.has("docs"), "Expected docs/ artifacts in consolidation");

assertRelativePathsExist([
  ...yamlHumanStartHere,
  primaryRuntimeFile,
  yamlLegacyFallbackFile,
  ...yamlMinimumArtifacts,
  ...yamlCanonicalDocs,
  ...jsonIndex.companion_indexes,
  ...yamlRuntimeFiles,
  metadata.fileIndexSnapshot
]);

console.log("File index integrity checks passed.");
