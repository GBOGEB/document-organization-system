import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  linspace,
  gradient,
  trapezoidIntegral,
  simpsonIntegralUniform,
  adaptiveSimpson,
  normalize,
  nearestIndex,
  gaussLegendre4,
  rombergIntegration
} from "../js/numerics.js";
import { propertyValue } from "../js/materials.js";

function approx(actual, expected, tolerance = 1e-8) {
  assert.ok(
    Math.abs(actual - expected) <= tolerance,
    `Expected ${actual} ≈ ${expected} within ${tolerance}`
  );
}

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const materialDatabase = JSON.parse(
  readFileSync(path.join(__dirname, "..", "data", "materials.json"), "utf8")
);

function computeMethodResults(materialKey, property, Tmin, Tmax, nsteps) {
  const material = materialDatabase.materials[materialKey];
  const temperatures = linspace(Tmin, Tmax, nsteps);
  const evaluator = temperature => propertyValue(material, property, temperature) || 0;
  const values = temperatures.map(evaluator);

  return {
    trapezoid: trapezoidIntegral(temperatures, values),
    simpson: simpsonIntegralUniform(temperatures, values),
    romberg: rombergIntegration(evaluator, Tmin, Tmax, 8),
    gauss: gaussLegendre4(evaluator, Tmin, Tmax, nsteps - 1)
  };
}

function assertMethodFixture(name, actual, expected, tolerance = 1e-8) {
  for (const [method, expectedValue] of Object.entries(expected)) {
    approx(actual[method], expectedValue, tolerance);
  }
  console.log(`Verified regression fixture: ${name}`);
}

console.log("Running numerics tests...");

const xs = linspace(0, 4, 5);
assert.deepEqual(xs, [0, 1, 2, 3, 4]);

const yLinear = xs.map(x => 2 * x + 1);
approx(trapezoidIntegral(xs, yLinear), 20, 1e-12);

const yQuad = xs.map(x => x * x);
approx(simpsonIntegralUniform(xs, yQuad), 64 / 3, 1e-12);

approx(gaussLegendre4(x => x * x, 0, 4), 64 / 3, 1e-12);
approx(gaussLegendre4(x => x * x, 0, 4, 4), 64 / 3, 1e-12);

approx(adaptiveSimpson(x => x * x, 0, 4, 1e-10, 20), 64 / 3, 1e-8);

const g = gradient(yLinear, xs);
g.forEach(value => approx(value, 2, 1e-12));

assert.deepEqual(normalize([0, 2, 4]), [0, 0.5, 1]);
assert.equal(nearestIndex([0, 10, 20], 12), 1);

assertMethodFixture(
  "AISI316 k 20-300K 100 steps",
  computeMethodResults("AISI316", "k", 20, 300, 100),
  {
    trapezoid: 3012.07974446,
    simpson: 3012.14986534,
    romberg: 3012.14980568,
    gauss: 3012.14980570
  }
);

assertMethodFixture(
  "AISI316 cp 20-300K 100 steps",
  computeMethodResults("AISI316", "cp", 20, 300, 100),
  {
    trapezoid: 93189.94859257,
    simpson: 93190.23539085,
    romberg: 93190.18638001,
    gauss: 93190.28911180
  }
);

assertMethodFixture(
  "CuRRR100 k 4-300K 100 steps",
  computeMethodResults("CuRRR100", "k", 4, 300, 100),
  {
    trapezoid: 194228.84485906,
    simpson: 194331.91282443,
    romberg: 194330.56784481,
    gauss: 194330.63341523
  }
);

console.log("All numerics tests passed.");
