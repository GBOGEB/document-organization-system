import assert from "node:assert/strict";
import fs from "node:fs";
import { getReleaseMetadata } from "../scripts/regenerate-ssot-views.js";

function escapeRegexLiteral(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

const metadata = getReleaseMetadata();
const requiredFiles = [
  "index.html",
  "files.html",
  "dashboard_modular.html",
  "html_preview_hub.html",
  "ssot_launcher.html",
  "index_slides.html",
  "data/materials.json",
  "js/app_modular.js",
  "js/materials.js",
  "VERSION",
  metadata.currentSessionHandover,
  metadata.nistReport,
  metadata.deploymentChecklist,
  metadata.ssotPipeline,
  metadata.fileIndexSnapshot
];

for (const file of requiredFiles) {
  assert.ok(fs.existsSync(file), `Missing required static entrypoint/artifact: ${file}`);
}

const indexHtml = fs.readFileSync("index.html", "utf8");
const filesHtml = fs.readFileSync("files.html", "utf8");
const dashboardHtml = fs.readFileSync("dashboard_modular.html", "utf8");
const previewHtml = fs.readFileSync("html_preview_hub.html", "utf8");

assert.match(indexHtml, /dashboard_modular\.html/, "index.html should link to modular dashboard");
assert.match(indexHtml, /files\.html/, "index.html should link to file navigator");
assert.match(filesHtml, /dashboard_modular\.html/, "files.html should link to modular dashboard");
assert.match(dashboardHtml, /type=["']module["']/, "dashboard_modular.html should load ES module entrypoint");
assert.match(dashboardHtml, /js\/app_modular\.js/, "dashboard_modular.html should load js/app_modular.js");

for (const htmlText of [indexHtml, filesHtml, dashboardHtml, previewHtml]) {
  assert.match(htmlText, new RegExp(escapeRegexLiteral(metadata.version)), `Active entrypoints should mention ${metadata.version}`);
}

assert.match(indexHtml, new RegExp(escapeRegexLiteral(metadata.currentSessionHandover)), "index.html should link to the active session handover");
assert.match(filesHtml, new RegExp(escapeRegexLiteral(metadata.currentSessionHandover)), "files.html should link to the active session handover");
assert.match(filesHtml, new RegExp(escapeRegexLiteral(metadata.nistReport)), "files.html should link to the active NIST report");
assert.match(filesHtml, new RegExp(escapeRegexLiteral(metadata.deploymentChecklist)), "files.html should link to the deployment checklist");
assert.match(filesHtml, new RegExp(escapeRegexLiteral(metadata.ssotPipeline)), "files.html should link to the SSOT regeneration pipeline");
assert.match(filesHtml, new RegExp(escapeRegexLiteral(metadata.fileIndexSnapshot)), "files.html should link to the active file-index snapshot");

console.log("Static entrypoint validation passed.");
