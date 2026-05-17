#!/usr/bin/env node
import fs from 'node:fs';

const entrypoints = [
  'index.html',
  'files.html',
  'dashboard_modular.html',
  'ssot_launcher.html',
  'index_slides.html',
];

const requiredLocalAssets = [
  'data/materials.json',
  'js/app_modular.js',
  'js/materials.js',
  'js/numerics.js',
  'js/plots.js',
  'js/export.js',
  'style.css',
  'ssot.json',
];

for (const file of entrypoints) {
  if (!fs.existsSync(file)) throw new Error(`Missing static entrypoint: ${file}`);
  const text = fs.readFileSync(file, 'utf8');
  if (!text.includes('<!doctype html') && !text.includes('<!DOCTYPE html')) {
    throw new Error(`${file} does not look like a standalone HTML document`);
  }
}

for (const file of requiredLocalAssets) {
  if (!fs.existsSync(file)) throw new Error(`Missing local asset required by static entrypoints: ${file}`);
}

console.log('Static entrypoint validation passed.');
