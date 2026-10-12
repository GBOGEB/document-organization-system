import fs from "node:fs";
import assert from "node:assert/strict";
import { getReleaseMetadata } from "./regenerate-ssot-views.js";

function escapeRegexLiteral(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

const metadata = getReleaseMetadata();
const expectedVersion = metadata.version;
const expectedBareVersion = metadata.bareVersion;

const fileExpectations = [
  {
    file: "README.md",
    checks: [expectedVersion]
  },
  {
    file: "VERSION",
    checks: [expectedVersion]
  },
  {
    file: "package.json",
    checks: [`\"version\": \"${expectedBareVersion}\"`]
  }
];

for (const { file, checks } of fileExpectations) {
  const text = fs.readFileSync(file, "utf8");
  for (const expectedSnippet of checks) {
    assert.match(
      text,
      new RegExp(escapeRegexLiteral(expectedSnippet)),
      `Version coherence failure in ${file}. Expected ${expectedSnippet}`
    );
  }
}

console.log(`Version coherence check passed for ${expectedVersion}.`);
