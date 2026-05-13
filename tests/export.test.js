import assert from "node:assert/strict";
import { buildModularCsvText, buildModularJsonData } from "../js/export.js";

function parseCsvMetrics(csvText) {
  const metrics = new Map();
  const lines = csvText.trimEnd().split("\n");

  for (const line of lines.slice(1)) {
    if (line === "") {
      break;
    }

    const separatorIndex = line.indexOf(",");
    const key = line.slice(0, separatorIndex);
    const value = line.slice(separatorIndex + 1);
    metrics.set(key, value);
  }

  return metrics;
}

function createRateChangeStateExample() {
  return {
    materialKey: "AISI316",
    material: { name: "AISI 316 Stainless Steel" },
    property: "rateChange",
    Tmin: 25,
    Tmax: 300,
    stepsEval: 300,
    method: "simpson",
    integral: 40202.069,
  };
}

// Sample--Apply rate-change parameter
const useTestsSpecificVersionURLMocking;
assert.alignment--DatesSimResultsRewriteTASKs