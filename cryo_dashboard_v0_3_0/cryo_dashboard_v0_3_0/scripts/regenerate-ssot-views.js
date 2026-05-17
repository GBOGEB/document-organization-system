#!/usr/bin/env node
import fs from 'node:fs';

const requiredArtifacts = [
  'ssot.json',
  'ssot_launcher.html',
  'index_slides.html',
  'files.html',
  'data/materials.json',
];

for (const artifact of requiredArtifacts) {
  if (!fs.existsSync(artifact)) {
    throw new Error(`Missing SSOT regeneration artifact: ${artifact}`);
  }
}

const ssot = JSON.parse(fs.readFileSync('ssot.json', 'utf8'));

if (!ssot?.ssot_meta?.dashboard_version) {
  throw new Error('Missing ssot_meta.dashboard_version');
}

const launcher = fs.readFileSync('ssot_launcher.html', 'utf8');
const slides = fs.readFileSync('index_slides.html', 'utf8');

const expectedVersion = ssot.ssot_meta.dashboard_version;

if (!launcher.includes(expectedVersion)) {
  console.warn(`Warning: ssot_launcher.html may not reflect ${expectedVersion}`);
}

if (!slides.includes(expectedVersion)) {
  console.warn(`Warning: index_slides.html may not reflect ${expectedVersion}`);
}

console.log(`SSOT regeneration plan validated for ${expectedVersion}.`);
console.log('Future implementation target: deterministic HTML regeneration from ssot.json templates.');
