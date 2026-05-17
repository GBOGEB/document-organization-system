#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

const ROOT = process.cwd();
const EXPECTED_VERSION = 'v0.4.9';
const EXPECTED_PACKAGE_VERSION = '0.4.9';

const activeChecks = [
  { path: 'VERSION', mustInclude: [EXPECTED_VERSION] },
  { path: 'README.md', mustInclude: ['Cryogenic Material Property Dashboard — v0.4.9'] },
  { path: 'package.json', json: true, field: 'version', equals: EXPECTED_PACKAGE_VERSION },
  { path: 'data/materials.json', json: true, field: 'version', equals: EXPECTED_VERSION },
  { path: 'ssot.json', json: true, field: 'ssot_meta.dashboard_version', equals: EXPECTED_VERSION },
];

function readText(relPath) {
  return fs.readFileSync(path.join(ROOT, relPath), 'utf8');
}

function getField(obj, dotted) {
  return dotted.split('.').reduce((acc, key) => (acc == null ? acc : acc[key]), obj);
}

const failures = [];

for (const check of activeChecks) {
  const abs = path.join(ROOT, check.path);
  if (!fs.existsSync(abs)) {
    failures.push(`${check.path}: missing active file`);
    continue;
  }
  const text = readText(check.path);
  if (check.json) {
    const parsed = JSON.parse(text);
    const value = getField(parsed, check.field);
    if (value !== check.equals) failures.push(`${check.path}: ${check.field}=${value}; expected ${check.equals}`);
  }
  for (const marker of check.mustInclude || []) {
    if (!text.includes(marker)) failures.push(`${check.path}: missing marker ${marker}`);
  }
}

if (failures.length) {
  console.error('Version coherence check failed:');
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log(`Version coherence check passed for ${EXPECTED_VERSION}.`);
