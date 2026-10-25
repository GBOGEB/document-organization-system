/**
 * ssot_contract.test.js — dependency-free contract validation for ssot.json.
 * =========================================================================
 * Validates ssot.json against contracts/ssot.schema.json using ONLY Node
 * built-ins (node:test, node:assert, node:fs). No external validator is
 * required, so this runs in the same zero-dependency harness as the rest of
 * the suite. It enforces a minimal, intentionally non-brittle subset of the
 * JSON Schema (required keys, types, and version/source patterns) plus a
 * version-coherence invariant that guards against the stale-version class of
 * regressions.
 */
import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, "..");
const ssot = JSON.parse(readFileSync(path.join(root, "ssot.json"), "utf8"));
const schema = JSON.parse(readFileSync(path.join(root, "contracts", "ssot.schema.json"), "utf8"));

const SEMVER = /^\d+\.\d+\.\d+$/;
const VSEMVER = /^v\d+\.\d+\.\d+$/;

test("ssot.json: top-level required keys present (per contract)", () => {
  for (const key of schema.required) {
    assert.ok(key in ssot, `missing required top-level key: ${key}`);
  }
});

test("ssot_meta: shape and canonical-source contract", () => {
  const m = ssot.ssot_meta;
  assert.match(m.schema_version, SEMVER, "schema_version must be semver");
  assert.match(m.dashboard_version, VSEMVER, "dashboard_version must be vSemVer");
  assert.match(m.canonical_source, /^GBOGEB\//, "canonical_source must be a GBOGEB repo");
  assert.ok(typeof m.subtree === "string" && m.subtree.length > 0, "subtree must be non-empty");
});

test("materials: count matches catalog length", () => {
  const mats = ssot.materials;
  assert.ok(Array.isArray(mats.catalog) && mats.catalog.length >= 1, "catalog must be a non-empty array");
  assert.equal(mats.count, mats.catalog.length, "materials.count must equal catalog length");
});

test("version coherence: dashboard_version is the max of version_history", () => {
  const dash = ssot.ssot_meta.dashboard_version;
  const hist = (ssot.project?.version_lineage ?? [])
    .map((e) => e.version)
    .filter((v) => VSEMVER.test(v));
  assert.ok(hist.length > 0, "version_history must contain at least one versioned entry");
  const toNum = (v) => v.slice(1).split(".").map(Number);
  const cmp = (a, b) => {
    const [a1, a2, a3] = toNum(a), [b1, b2, b3] = toNum(b);
    return a1 - b1 || a2 - b2 || a3 - b3;
  };
  const max = hist.reduce((acc, v) => (cmp(v, acc) > 0 ? v : acc), hist[0]);
  assert.equal(max, dash, `dashboard_version (${dash}) must equal the max version in history (${max})`);
  // No stale pre-release labels should outrank the declared version.
  for (const v of hist) {
    assert.ok(cmp(v, dash) <= 0, `version_history entry ${v} is newer than dashboard_version ${dash}`);
  }
});

test("version-history has no duplicate version entries", () => {
  const hist = (ssot.project?.version_lineage ?? []).map((e) => e.version);
  const seen = new Set();
  for (const v of hist) {
    assert.ok(!seen.has(v), `duplicate version_history entry: ${v}`);
    seen.add(v);
  }
});
