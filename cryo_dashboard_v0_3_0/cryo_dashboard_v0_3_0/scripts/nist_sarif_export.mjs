/**
 * nist_sarif_export.mjs — emit SARIF 2.1.0 for the NIST parity + SSOT contract suites.
 * ===================================================================================
 * Convention alignment:
 *   The GBOGEB triad (ABACUS, CODEX) standardises on SARIF for code-scanning
 *   uploads (bandit.yml, codeql.yml, osv-scanner.yml -> upload-sarif). This
 *   script lets the dashboard's test evidence plug into that same convention:
 *   it runs the zero-dependency Node test suites, parses their TAP-ish output,
 *   and writes a SARIF file consumable by GitHub code scanning
 *   (actions/upload-sarif) or any SARIF viewer.
 *
 * Usage:
 *   node scripts/nist_sarif_export.mjs            # writes nist-parity.sarif
 *   node scripts/nist_sarif_export.mjs out.sarif  # custom output path
 *
 * Exit code mirrors the test outcome (0 = all green, 1 = any failure), so it is
 * safe to gate CI on it while still always producing the SARIF artifact.
 */
import { spawnSync } from "node:child_process";
import { writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, "..");
const outPath = process.argv[2] ?? path.join(root, "nist-parity.sarif");

const SUITES = [
  { id: "nist-parity", file: "tests/nist_parity.test.js" },
  { id: "ssot-contract", file: "tests/ssot_contract.test.js" },
];

const results = [];
let anyFail = false;

for (const suite of SUITES) {
  const run = spawnSync("node", [suite.file], { cwd: root, encoding: "utf8" });
  const output = `${run.stdout ?? ""}\n${run.stderr ?? ""}`;
  const failed = run.status !== 0;
  if (failed) {
    anyFail = true;
    // Capture failing-assertion lines as SARIF results.
    const lines = output.split("\n").filter((l) => /not ok|AssertionError|✗|Error:/i.test(l));
    const sample = lines.length ? lines : [`${suite.id}: suite exited with status ${run.status}`];
    for (const [idx, msg] of sample.entries()) {
      results.push({
        ruleId: `${suite.id}/failure`,
        level: "error",
        message: { text: msg.trim().slice(0, 1000) },
        locations: [{
          physicalLocation: {
            artifactLocation: { uri: suite.file },
            region: { startLine: 1 + idx },
          },
        }],
      });
    }
  }
}

if (results.length === 0) {
  // Clean run: emit a single informational "pass" note so the artifact is never empty.
  results.push({
    ruleId: "nist-parity/all-green",
    level: "note",
    message: { text: "All NIST parity and SSOT contract tests passed (0 failures)." },
    locations: [{ physicalLocation: { artifactLocation: { uri: "tests/nist_parity.test.js" }, region: { startLine: 1 } } }],
  });
}

const sarif = {
  $schema: "https://json.schemastore.org/sarif-2.1.0.json",
  version: "2.1.0",
  runs: [{
    tool: {
      driver: {
        name: "cryo-dashboard-nist-parity",
        informationUri: "https://github.com/GBOGEB/document-organization-system",
        version: "0.4.9",
        rules: [
          { id: "nist-parity/failure", shortDescription: { text: "NIST parity regression failed" } },
          { id: "ssot-contract/failure", shortDescription: { text: "SSOT contract validation failed" } },
          { id: "nist-parity/all-green", shortDescription: { text: "All parity/contract tests passed" } },
        ],
      },
    },
    results,
  }],
};

writeFileSync(outPath, `${JSON.stringify(sarif, null, 2)}\n`);
console.log(`SARIF written to ${outPath} (${results.length} result(s), ${anyFail ? "FAIL" : "PASS"})`);
process.exit(anyFail ? 1 : 0);
