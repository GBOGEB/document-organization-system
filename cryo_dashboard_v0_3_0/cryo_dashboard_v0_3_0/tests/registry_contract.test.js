/**
 * registry_contract.test.js — dependency-free contract validation for the
 * repo-local federation registry (federation/registry.json).
 * =========================================================================
 * Uses ONLY Node built-ins (node:test, node:assert, node:fs) — same
 * zero-dependency harness as ssot_contract.test.js. It enforces a minimal,
 * non-brittle subset of contracts/registry.schema.json (required keys,
 * types, patterns) plus cross-field coherence:
 *   - no duplicate repos,
 *   - exactly one self repo (is_self) and it is this repository,
 *   - every LOCAL artifact/entry-point path (self repo only) that is a
 *     concrete file path actually exists on disk.
 * External repo artifacts are reference-only and intentionally NOT disk-checked.
 *
 * The registry and its schema live at the REPOSITORY ROOT; this test runs from
 * the dashboard subtree, so it resolves three levels up to the repo root.
 */
import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync, existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
// tests -> (1) subtree root -> (2) cryo_dashboard_v0_3_0 -> (3) repo root
const repoRoot = path.resolve(__dirname, "..", "..", "..");
const registryPath = path.join(repoRoot, "federation", "registry.json");
const schemaPath = path.join(repoRoot, "contracts", "registry.schema.json");

const registry = JSON.parse(readFileSync(registryPath, "utf8"));
const schema = JSON.parse(readFileSync(schemaPath, "utf8"));

const SCHEMA_VER = /^federation-registry\/\d+\.\d+$/;
const REPO_RE = /^GBOGEB\/[A-Za-z0-9._-]+$/;
const VSEMVER = /^v\d+\.\d+\.\d+$/;

test("registry: top-level required keys present (per contract)", () => {
  for (const key of schema.required) {
    assert.ok(key in registry, `missing required top-level key: ${key}`);
  }
});

test("registry: schema_version, owner and registry_of_record patterns", () => {
  assert.match(registry.schema_version, SCHEMA_VER, "schema_version must be federation-registry/x.y");
  assert.equal(registry.owner, "GBOGEB", "owner must be GBOGEB");
  assert.match(registry.registry_of_record, /^GBOGEB\//, "registry_of_record must be a GBOGEB ref");
  assert.ok(
    typeof registry.local_ssot_pointer === "string" && registry.local_ssot_pointer.length > 0,
    "local_ssot_pointer must be a non-empty string"
  );
});

test("registry: local_ssot_pointer resolves to an existing file", () => {
  const p = path.join(repoRoot, registry.local_ssot_pointer);
  assert.ok(existsSync(p), `local_ssot_pointer not found on disk: ${registry.local_ssot_pointer}`);
});

test("registry: repos is a non-empty array of well-formed entries", () => {
  assert.ok(Array.isArray(registry.repos) && registry.repos.length >= 1, "repos must be a non-empty array");
  for (const r of registry.repos) {
    assert.match(r.repo, REPO_RE, `repo must match GBOGEB/<name>: ${r.repo}`);
    assert.ok(typeof r.role === "string" && r.role.length > 0, `role required for ${r.repo}`);
    assert.ok(typeof r.default_branch === "string" && r.default_branch.length > 0, `default_branch required for ${r.repo}`);
    assert.equal(typeof r.reference_only, "boolean", `reference_only must be boolean for ${r.repo}`);
    assert.ok(
      r.authoritative_artifacts && typeof r.authoritative_artifacts === "object",
      `authoritative_artifacts required for ${r.repo}`
    );
    if (r.dashboard_version !== undefined) {
      assert.match(r.dashboard_version, VSEMVER, `dashboard_version must be vSemVer for ${r.repo}`);
    }
  }
});

test("registry: no duplicate repo entries", () => {
  const seen = new Set();
  for (const r of registry.repos) {
    assert.ok(!seen.has(r.repo), `duplicate repo entry: ${r.repo}`);
    seen.add(r.repo);
  }
});

test("registry: exactly one self repo and it is this repository", () => {
  const selves = registry.repos.filter((r) => r.is_self === true);
  assert.equal(selves.length, 1, "exactly one repo must be marked is_self:true");
  assert.equal(selves[0].repo, "GBOGEB/document-organization-system", "self repo must be document-organization-system");
  assert.equal(selves[0].reference_only, false, "self repo must not be reference_only");
});

test("registry: all LOCAL (self-repo) artifact/entry-point file paths exist on disk", () => {
  const self = registry.repos.find((r) => r.is_self === true);
  const looksLikePath = (v) =>
    typeof v === "string" &&
    v.includes("/") &&
    /\.[A-Za-z0-9]+$/.test(v) &&          // has a file extension
    !v.includes("*") &&                    // not a glob
    !v.startsWith("GBOGEB/") &&            // not a repo ref
    !/\{.*\}/.test(v);                     // not a brace-expansion ref
  const candidates = [];
  for (const v of Object.values(self.authoritative_artifacts ?? {})) candidates.push(v);
  for (const v of Object.values(self.entry_points ?? {})) candidates.push(v);
  const checked = candidates.filter(looksLikePath);
  assert.ok(checked.length > 0, "expected at least one concrete local path to verify");
  for (const rel of checked) {
    assert.ok(existsSync(path.join(repoRoot, rel)), `self-repo path missing on disk: ${rel}`);
  }
});

test("registry: external repos are reference_only (no accidental self-mutation claims)", () => {
  for (const r of registry.repos) {
    if (r.repo === "GBOGEB/document-organization-system") continue;
    assert.equal(r.reference_only, true, `external repo must be reference_only: ${r.repo}`);
  }
});
