import { loadMaterialDatabase } from "./materials.js";
import { propertyValue, rangeStatus, getPropertyRange, equationText } from "./materials.js";
import { linspace, trapezoidIntegral, simpsonIntegralUniform, rombergIntegration, gaussLegendre4 } from "./numerics.js";
import { downloadMainPlotPng } from "./plots.js";
import {
  buildModularCsvText,
  buildModularJsonData,
  formatModularIntegralValue,
  formatModularPercent,
  formatModularPropertyValue,
  formatModularTemperature,
  getModularDeltaSummaryValues
} from "./export.js";

let materialDatabase = null;
let currentState = null;
let resultMode = "single";
let cursorPins = [];
let lastPinContext = null;

function formatTemperature(value) {
  return formatModularTemperature(value);
}

function formatPropertyValue(value) {
  return formatModularPropertyValue(value);
}

function formatIntegralValue(value) {
  return formatModularIntegralValue(value);
}

function formatPercent(value) {
  return formatModularPercent(value);
}

function getMethodLabel(method) {
  if (method === "trapezoid") return "Trapezoid";
  if (method === "simpson") return "Simpson fixed";
  if (method === "romberg") return "Romberg";
  return "Gauss-Legendre 4-pt";
}

function methodEquationNote(method) {
  if (method === "trapezoid") return "\u222b dT \u2248 \u03a3 ((y\u1d62 + y\u1d62\u208a\u2081) / 2) \u00b7 \u0394T";
  if (method === "simpson") return "\u222b dT \u2248 (h/3) [y\u2080 + y\u2099 + 4\u03a3y\u2092dd + 2\u03a3y\u2091v\u2099] — odd point count enforced";
  if (method === "romberg") return "Richardson extrapolation on trapezoidal sequence";
  return "4-point Gauss-Legendre quadrature";
}

function getPropertyPresentation(property) {
  if (property === "k") {
    return {
      name: "thermal conductivity",
      symbol: "k",
      functionLabel: "k(T)",
      valueUnits: "W/(m·K)",
      integralUnits: "W/m"
    };
  }

  if (property === "tc") {
    return {
      name: "thermal contraction",
      symbol: "Y",
      functionLabel: "Y(T)",
      valueUnits: "x1e-5",
      integralUnits: "x1e-5·K"
    };
  }

  return {
    name: "specific heat",
    symbol: "cp",
    functionLabel: "cp(T)",
    valueUnits: "J/(kg·K)",
    integralUnits: "J/kg"
  };
}

function clamp01(value) {
  return Math.max(0, Math.min(1, value));
}

function getLegendBounds(candidate, width, height) {
  let left = candidate.x;
  if (candidate.xanchor === "center") left -= width / 2;
  if (candidate.xanchor === "right") left -= width;

  let bottom = candidate.y;
  if (candidate.yanchor === "middle") bottom -= height / 2;
  if (candidate.yanchor === "top") bottom -= height;

  left = clamp01(left);
  bottom = clamp01(bottom);

  return {
    left,
    right: clamp01(left + width),
    bottom,
    top: clamp01(bottom + height)
  };
}

function chooseAdaptiveLegendPlacement(plotT, plotValues, legendItems) {
  const finitePoints = plotT
    .map((x, index) => ({ x, y: plotValues[index] }))
    .filter((point) => Number.isFinite(point.x) && Number.isFinite(point.y));

  if (finitePoints.length < 2) {
    return { x: 0.02, y: 0.98, xanchor: "left", yanchor: "top", legendSlot: "A1" };
  }

  const xMin = Math.min(...finitePoints.map((point) => point.x));
  const xMax = Math.max(...finitePoints.map((point) => point.x));
  const yMin = Math.min(...finitePoints.map((point) => point.y));
  const yMax = Math.max(...finitePoints.map((point) => point.y));
  const xSpan = xMax - xMin || 1;
  const ySpan = yMax - yMin || 1;

  const normalized = finitePoints.map((point) => ({
    x: (point.x - xMin) / xSpan,
    y: (point.y - yMin) / ySpan
  }));

  const width = Math.min(0.34, 0.19 + legendItems * 0.035);
  const height = Math.min(0.32, 0.08 + legendItems * 0.05);
  const paddedWidth = Math.min(0.38, width + 0.04);
  const paddedHeight = Math.min(0.36, height + 0.05);

  const candidates = [
    { legendSlot: "A1", x: 0.02, y: 0.98, xanchor: "left", yanchor: "top" },
    { legendSlot: "A2", x: 0.5, y: 0.98, xanchor: "center", yanchor: "top" },
    { legendSlot: "A3", x: 0.98, y: 0.98, xanchor: "right", yanchor: "top" },
    { legendSlot: "B1", x: 0.02, y: 0.5, xanchor: "left", yanchor: "middle" },
    { legendSlot: "B3", x: 0.98, y: 0.5, xanchor: "right", yanchor: "middle" },
    { legendSlot: "B2", x: 0.5, y: 0.5, xanchor: "center", yanchor: "middle" },
    { legendSlot: "C1", x: 0.02, y: 0.02, xanchor: "left", yanchor: "bottom" },
    { legendSlot: "C2", x: 0.5, y: 0.02, xanchor: "center", yanchor: "bottom" },
    { legendSlot: "C3", x: 0.98, y: 0.02, xanchor: "right", yanchor: "bottom" }
  ];

  const ranked = candidates.map((candidate, preferenceIndex) => {
    const bounds = getLegendBounds(candidate, width, height);
    const paddedBounds = getLegendBounds(candidate, paddedWidth, paddedHeight);

    let overlapScore = 0;
    normalized.forEach((point) => {
      const insideLegend = point.x >= bounds.left && point.x <= bounds.right && point.y >= bounds.bottom && point.y <= bounds.top;
      if (insideLegend) {
        overlapScore += 5;
        return;
      }

      const insidePadding = point.x >= paddedBounds.left && point.x <= paddedBounds.right && point.y >= paddedBounds.bottom && point.y <= paddedBounds.top;
      if (insidePadding) {
        overlapScore += 1;
      }
    });

    const centerPenalty = candidate.legendSlot === "B2" ? 2 : 0;
    const bottomPenalty = candidate.legendSlot.startsWith("C") ? 1.5 : 0;
    return { candidate, score: overlapScore + centerPenalty + bottomPenalty, preferenceIndex };
  });

  ranked.sort((left, right) => {
    if (left.score !== right.score) return left.score - right.score;
    return left.preferenceIndex - right.preferenceIndex;
  });

  return ranked[0].candidate;
}

function getTextBoxBounds(point, textPosition, width, height) {
  let left = point.xNorm - width / 2;
  let right = point.xNorm + width / 2;
  let bottom = point.yNorm - height / 2;
  let top = point.yNorm + height / 2;

  if (textPosition.includes("left")) {
    right = point.xNorm - 0.02;
    left = right - width;
  } else if (textPosition.includes("right")) {
    left = point.xNorm + 0.02;
    right = left + width;
  }

  if (textPosition.startsWith("top")) {
    bottom = point.yNorm + 0.03;
    top = bottom + height;
  } else if (textPosition.startsWith("bottom")) {
    top = point.yNorm - 0.03;
    bottom = top - height;
  }

  return { left, right, bottom, top };
}

function boundsOverlap(a, b) {
  return !(a.right < b.left || a.left > b.right || a.top < b.bottom || a.bottom > b.top);
}

function normalizePlotPoints(plotT, plotValues) {
  const finitePoints = plotT
    .map((x, index) => ({ x, y: plotValues[index] }))
    .filter((point) => Number.isFinite(point.x) && Number.isFinite(point.y));

  if (finitePoints.length < 2) {
    return null;
  }

  const xMin = Math.min(...finitePoints.map((point) => point.x));
  const xMax = Math.max(...finitePoints.map((point) => point.x));
  const yMin = Math.min(...finitePoints.map((point) => point.y));
  const yMax = Math.max(...finitePoints.map((point) => point.y));
  const xSpan = xMax - xMin || 1;
  const ySpan = yMax - yMin || 1;

  return {
    normalizedCurve: finitePoints.map((point) => ({
      xNorm: (point.x - xMin) / xSpan,
      yNorm: (point.y - yMin) / ySpan
    })),
    normalizePoint(point) {
      return {
        ...point,
        xNorm: (point.x - xMin) / xSpan,
        yNorm: (point.y - yMin) / ySpan
      };
    }
  };
}

function choosePointLabelPosition(plotT, plotValues, point, options = {}) {
  const normalized = normalizePlotPoints(plotT, plotValues);
  if (!normalized) {
    return "top center";
  }

  const normalizedPoint = normalized.normalizePoint(point);
  const candidates = options.candidates || [
    "top left",
    "top center",
    "top right",
    "middle left",
    "middle right",
    "bottom left",
    "bottom center",
    "bottom right"
  ];
  const boxWidth = options.boxWidth || 0.23;
  const boxHeight = options.boxHeight || 0.09;
  const avoidBoxes = options.avoidBoxes || [];

  let best = { score: Infinity, position: candidates[0] || "top center" };
  candidates.forEach((position, preferenceIndex) => {
    const box = getTextBoxBounds(normalizedPoint, position, boxWidth, boxHeight);
    let score = 0;

    const overflow = [
      Math.max(0, -box.left),
      Math.max(0, box.right - 1),
      Math.max(0, -box.bottom),
      Math.max(0, box.top - 1)
    ].reduce((sum, value) => sum + value, 0);
    score += overflow * 50;

    normalized.normalizedCurve.forEach((curvePoint) => {
      const inside = curvePoint.xNorm >= box.left && curvePoint.xNorm <= box.right && curvePoint.yNorm >= box.bottom && curvePoint.yNorm <= box.top;
      if (inside) score += 1;
    });

    avoidBoxes.forEach((avoidBox) => {
      if (boundsOverlap(box, avoidBox)) score += 30;
    });

    if (score < best.score || (score === best.score && preferenceIndex < candidates.indexOf(best.position))) {
      best = { score, position };
    }
  });

  return best.position;
}

function chooseEndpointLabelPositions(plotT, plotValues, endpoints) {
  const normalized = normalizePlotPoints(plotT, plotValues);
  if (!normalized || endpoints.length !== 2) {
    return ["top left", "top right"];
  }

  const normalizedEndpoints = endpoints.map((point) => normalized.normalizePoint(point));
  const candidates = [
    "top left",
    "top center",
    "top right",
    "middle left",
    "middle right",
    "bottom left",
    "bottom center",
    "bottom right"
  ];

  const boxWidth = 0.23;
  const boxHeight = 0.09;
  let best = { score: Infinity, positions: ["top left", "top right"] };

  candidates.forEach((firstPosition) => {
    candidates.forEach((secondPosition) => {
      const positions = [firstPosition, secondPosition];
      const boxes = normalizedEndpoints.map((endpoint, index) => getTextBoxBounds(endpoint, positions[index], boxWidth, boxHeight));

      let score = 0;
      boxes.forEach((box, index) => {
        const overflow = [
          Math.max(0, -box.left),
          Math.max(0, box.right - 1),
          Math.max(0, -box.bottom),
          Math.max(0, box.top - 1)
        ].reduce((sum, value) => sum + value, 0);
        score += overflow * 50;

        normalized.normalizedCurve.forEach((point) => {
          const inside = point.xNorm >= box.left && point.xNorm <= box.right && point.yNorm >= box.bottom && point.yNorm <= box.top;
          if (inside) score += 1;
        });

        normalizedEndpoints.forEach((endpoint, endpointIndex) => {
          if (endpointIndex === index) return;
          const pointInside = endpoint.xNorm >= box.left && endpoint.xNorm <= box.right && endpoint.yNorm >= box.bottom && endpoint.yNorm <= box.top;
          if (pointInside) score += 20;
        });
      });

      if (boundsOverlap(boxes[0], boxes[1])) score += 40;
      if (positions[0] === positions[1]) score += 2;

      if (score < best.score) {
        best = { score, positions };
      }
    });
  });

  return best.positions;
}

function getThermalContractionBranch(material, T) {
  const def = material?.properties?.tc;
  if (!def || def.type !== "thermal-contraction") {
    return "n/a";
  }
  return (def.tlow != null && def.f != null && T < def.tlow) ? "low-T constant branch" : "polynomial branch";
}

function getThermalContractionMetrics() {
  const { material, Tmin, Tmax } = currentState;
  const lengthKnown = parseFloat(document.getElementById("knownLengthInput")?.value) || NaN;
  const lengthRef = document.getElementById("lengthReferenceSelect")?.value || "L293";

  const y1 = propertyValue(material, "tc", Tmin);
  const y2 = propertyValue(material, "tc", Tmax);
  const strain1 = Number.isFinite(y1) ? y1 * 1e-5 : NaN;
  const strain2 = Number.isFinite(y2) ? y2 * 1e-5 : NaN;

  let L1 = NaN;
  let L2 = NaN;
  if (lengthKnown > 0 && Number.isFinite(strain1) && Number.isFinite(strain2)) {
    if (lengthRef === "L293") {
      L1 = lengthKnown * (1 + strain1);
      L2 = lengthKnown * (1 + strain2);
    } else {
      L1 = lengthKnown;
      L2 = lengthKnown * (1 + strain2) / (1 + strain1);
    }
  }

  return {
    y1,
    y2,
    strain1,
    strain2,
    deltaStrain: (Number.isFinite(strain1) && Number.isFinite(strain2)) ? (strain2 - strain1) : NaN,
    L1,
    L2,
    deltaL: (Number.isFinite(L1) && Number.isFinite(L2)) ? (L2 - L1) : NaN,
    lengthRef,
    branchT1: getThermalContractionBranch(material, Tmin),
    branchT2: getThermalContractionBranch(material, Tmax)
  };
}

function getDeltaSummaryValues() {
  return getModularDeltaSummaryValues(currentState);
}

function getSelectedIntegralFromState() {
  if (!currentState) {
    return 0;
  }
  if (currentState.method === "trapezoid") {
    return currentState.methodResults.trapezoid;
  }
  if (currentState.method === "simpson") {
    return currentState.methodResults.simpson;
  }
  if (currentState.method === "romberg") {
    return currentState.methodResults.romberg;
  }
  return currentState.methodResults.gauss;
}

function updateDeltaSummary() {
  if (!currentState) {
    return;
  }
  const deltaSummary = document.getElementById("deltaSummary");
  if (!deltaSummary) {
    return;
  }
  const deltaSummaryValues = getDeltaSummaryValues();
  const propertyPresentation = getPropertyPresentation(currentState.property);
  const rs = rangeStatus(currentState.material, currentState.property, currentState.Tmin, currentState.Tmax);
  const rsClass = rs === "PASS" ? "ok" : "warning";
  const [rangeLo, rangeHi] = getPropertyRange(currentState.material, currentState.property);
  const selectedLo = Math.min(currentState.Tmin, currentState.Tmax);
  const selectedHi = Math.max(currentState.Tmin, currentState.Tmax);
  const extrapolationNote = rs === "PASS"
    ? `Inside NIST validity range ${formatTemperature(rangeLo)}-${formatTemperature(rangeHi)} K; no extrapolation used.`
    : `Selected range ${formatTemperature(selectedLo)}-${formatTemperature(selectedHi)} K exceeds NIST validity range ${formatTemperature(rangeLo)}-${formatTemperature(rangeHi)} K; extrapolation risk.`;

  const integ = deltaSummaryValues.integralK;
  let derivedLine = "";
  if (currentState.property === "k") {
    const A = parseFloat(document.getElementById("areaInput")?.value) || NaN;
    const L = parseFloat(document.getElementById("lengthInput")?.value) || NaN;
    const qdot = (A > 0 && L > 0) ? (A / L) * integ : NaN;
    derivedLine = `<p title="Conduction heat load: Qdot = (A/L) × ∫k dT. Uses area and length inputs from controls.">Conduction Qdot = ${Number.isFinite(qdot) ? qdot.toExponential(4) + " W" : "n/a — set A and L > 0"}</p>`;
  } else if (currentState.property === "cp") {
    const m = parseFloat(document.getElementById("massInput")?.value) || NaN;
    const energy = (m > 0) ? m * integ : NaN;
    derivedLine = `<p title="Cooldown/warmup energy: E = m × ∫cp dT.">Cooldown energy = ${Number.isFinite(energy) ? energy.toExponential(4) + " J" : "n/a — set mass > 0"}</p>`;
  } else {
    const tc = getThermalContractionMetrics();
    derivedLine = `
      <p title="Thermal contraction uses Y(T) relative to 293 K. Primary engineering value is length change between selected temperatures.">Δstrain(T1→T2) = ${Number.isFinite(tc.deltaStrain) ? tc.deltaStrain.toExponential(4) + " m/m" : "n/a"}</p>
      <p title="Length change between selected temperatures. Sign: negative = contraction, positive = expansion.">ΔL(T1→T2) = ${Number.isFinite(tc.deltaL) ? tc.deltaL.toExponential(4) + " m (" + (tc.deltaL * 1e3).toExponential(4) + " mm)" : "n/a — set Known Length > 0"}</p>
      <p title="Branch used in NIST thermal contraction model.">Branch: T1 uses ${tc.branchT1}; T2 uses ${tc.branchT2}</p>
      <p><em>Integral is shown for numerical transparency only; length-change calculations are based on Y(T) values and ratio formulas.</em></p>`;
  }

  deltaSummary.innerHTML = `
    <p title="Endpoint change in the selected property across the current temperature range.">Δ${propertyPresentation.symbol} = ${propertyPresentation.functionLabel.replace("(T)", "(T2)")} - ${propertyPresentation.functionLabel.replace("(T)", "(T1)")} = ${formatPropertyValue(deltaSummaryValues.deltaK)} ${propertyPresentation.valueUnits}</p>
    <p title="Integral of the selected property over the current temperature range using the active integration method.">∫${propertyPresentation.symbol} dT [T1→T2] = ${formatIntegralValue(integ)} ${propertyPresentation.integralUnits} (active method)</p>
    ${derivedLine}
    <p title="Published NIST temperature validity range for the selected material and property.">NIST validity range: ${formatTemperature(rangeLo)} K to ${formatTemperature(rangeHi)} K</p>
    <p title="Indicates whether the selected temperature range lies within the NIST equation validity range for this material and property.">Range check: <span class="${rsClass}">${rs === "PASS" ? "PASS - inside NIST range" : "OUT OF RANGE - extrapolation warning"}</span></p>
    <p title="Explains whether the current evaluation stays inside published validity limits or requires extrapolation."><em>${extrapolationNote}</em></p>
  `;
}

function updateQuickOutputs() {
  if (!currentState) {
    return;
  }
  const quickOutputs = document.getElementById("quickOutputs");
  if (!quickOutputs) {
    return;
  }

  const { property, material, Tmin, Tmax, mass } = currentState;
  const deltaSummaryValues = getDeltaSummaryValues();
  const propertyPresentation = getPropertyPresentation(property);
  const rs = rangeStatus(material, property, Tmin, Tmax);
  const rsClass = rs === "PASS" ? "ok" : "warning";
  const integral = deltaSummaryValues.integralK;
  const avg = integral / Math.abs(Tmax - Tmin);
  const v1 = propertyValue(material, property, Tmin) || 0;
  const v2 = propertyValue(material, property, Tmax) || 0;

  const A = parseFloat(document.getElementById("areaInput")?.value) || NaN;
  const L = parseFloat(document.getElementById("lengthInput")?.value) || NaN;
  const qdot = (A > 0 && L > 0) ? (A / L) * integral : NaN;
  const energy = (mass > 0) ? mass * integral : NaN;
  const tc = property === "tc" ? getThermalContractionMetrics() : null;

  const fmt = (value, unit) => Number.isFinite(value) ? `${Number(value).toPrecision(5)} ${unit}` : "n/a";

  if (property === "tc") {
    quickOutputs.innerHTML = `
      <div class="quick-kpi"><span class="kpi-label">Y(T1) at ${formatTemperature(Tmin)} K</span><span class="kpi-value">${fmt(tc.y1, "x1e-5")}</span></div>
      <div class="quick-kpi"><span class="kpi-label">Y(T2) at ${formatTemperature(Tmax)} K</span><span class="kpi-value">${fmt(tc.y2, "x1e-5")}</span></div>
      <div class="quick-kpi"><span class="kpi-label">Strain(T1)</span><span class="kpi-value">${fmt(tc.strain1, "m/m")}</span></div>
      <div class="quick-kpi"><span class="kpi-label">Strain(T2)</span><span class="kpi-value">${fmt(tc.strain2, "m/m")}</span></div>
      <div class="quick-kpi"><span class="kpi-label">Delta strain (T1→T2)</span><span class="kpi-value">${fmt(tc.deltaStrain, "m/m")}</span></div>
      <div class="quick-kpi"><span class="kpi-label">Delta length</span><span class="kpi-value">${Number.isFinite(tc.deltaL) ? `${tc.deltaL.toExponential(4)} m` : "n/a"}</span></div>
      <div class="quick-kpi"><span class="kpi-label">Delta length</span><span class="kpi-value">${Number.isFinite(tc.deltaL) ? `${(tc.deltaL * 1e3).toExponential(4)} mm` : "n/a"}</span></div>
      <div class="quick-kpi"><span class="kpi-label">Validation</span><span class="kpi-value ${rsClass}">${rs}</span></div>
    `;
    return;
  }

  quickOutputs.innerHTML = `
    <div class="quick-kpi"><span class="kpi-label">${propertyPresentation.functionLabel.replace("(T)", "(T1)")} at ${formatTemperature(Tmin)} K</span><span class="kpi-value">${fmt(v1, propertyPresentation.valueUnits)}</span></div>
    <div class="quick-kpi"><span class="kpi-label">${propertyPresentation.functionLabel.replace("(T)", "(T2)")} at ${formatTemperature(Tmax)} K</span><span class="kpi-value">${fmt(v2, propertyPresentation.valueUnits)}</span></div>
    <div class="quick-kpi"><span class="kpi-label">∫${propertyPresentation.symbol}(T)dT</span><span class="kpi-value">${fmt(integral, propertyPresentation.integralUnits)}</span></div>
    <div class="quick-kpi"><span class="kpi-label">Average ${propertyPresentation.symbol}</span><span class="kpi-value">${fmt(avg, propertyPresentation.valueUnits)}</span></div>
    <div class="quick-kpi"><span class="kpi-label">Delta</span><span class="kpi-value">${fmt(deltaSummaryValues.deltaK, propertyPresentation.valueUnits)}</span></div>
    <div class="quick-kpi"><span class="kpi-label">Conduction Qdot</span><span class="kpi-value">${property === "k" ? fmt(qdot, "W") : "n/a"}</span></div>
    <div class="quick-kpi"><span class="kpi-label">Cooldown/Warmup Energy</span><span class="kpi-value">${property === "cp" ? fmt(energy, "J") : "n/a"}</span></div>
    <div class="quick-kpi"><span class="kpi-label">Validation</span><span class="kpi-value ${rsClass}">${rs}</span></div>
  `;
}

function syncSelectedMethodFromControl() {
  if (!currentState) {
    return;
  }
  const selectedMethod = document.getElementById("integrationMethod").value;
  currentState.method = selectedMethod;
  currentState.integral = getSelectedIntegralFromState();
  updateResults();
  updateDeltaSummary();
  updateQuickOutputs();
  updateDebug();
}

function getCurrentResultMode() {
  const checked = document.querySelector('input[name="resultMode"]:checked');
  if (!checked) {
    return resultMode;
  }
  return checked.value;
}

function applyResultModeVisibility() {
  const integrationResults = document.getElementById("integrationResults");
  const methodComparisonPanel = document.getElementById("methodComparisonPanel");
  const mode = getCurrentResultMode();
  resultMode = mode;

  if (integrationResults) {
    integrationResults.style.display = mode === "single" ? "block" : "none";
  }
  if (methodComparisonPanel) {
    methodComparisonPanel.style.display = mode === "compare" ? "block" : "none";
  }
}

function setupResultModeToggle() {
  const toggles = document.querySelectorAll('input[name="resultMode"]');
  toggles.forEach(toggle => {
    toggle.addEventListener("change", () => {
      applyResultModeVisibility();
    });
  });
  const methodSelect = document.getElementById("integrationMethod");
  if (methodSelect) {
    methodSelect.addEventListener("change", () => {
      syncSelectedMethodFromControl();
    });
  }
  applyResultModeVisibility();
}

function populateMaterialSelect(preferredKey) {
  const select = document.getElementById("materialSelect");
  const requestedProperty = document.getElementById("propertySelect")?.value;
  const property = ["k", "cp", "tc"].includes(requestedProperty) ? requestedProperty : "k";
  const currentValue = preferredKey || select.value;
  select.innerHTML = "";

  let available = Object.entries(materialDatabase.materials).filter(
    ([, material]) => material.properties && material.properties[property]
  );

  // Safety fallback: never leave the material list empty in case of stale/invalid property value.
  if (available.length === 0) {
    available = Object.entries(materialDatabase.materials).filter(
      ([, material]) => material.properties && material.properties.k
    );
  }

  available.forEach(([key, material]) => {
    const opt = document.createElement("option");
    opt.value = key;
    opt.textContent = material.name || key;
    select.appendChild(opt);
  });

  if (available.length === 0) {
    const opt = document.createElement("option");
    opt.value = "";
    opt.textContent = "No material data available";
    select.appendChild(opt);
    select.value = "";
    return;
  }

  const stillAvailable = available.some(([key]) => key === currentValue);
  select.value = stillAvailable ? currentValue : available[0][0];
}

function populateLayerSelects() {
  const kMaterials = Object.entries(materialDatabase.materials).filter(
    ([, mat]) => mat.properties && mat.properties.k
  );
  [1, 2, 3].forEach((i) => {
    const sel = document.getElementById("layMat" + i);
    if (!sel) return;
    sel.innerHTML = "";
    kMaterials.forEach(([key, mat]) => {
      const opt = document.createElement("option");
      opt.value = key;
      opt.textContent = mat.name;
      sel.appendChild(opt);
    });
  });
}

function calcLayersPanel() {
  const T1 = parseFloat(document.getElementById("Tmin").value);
  const T2 = parseFloat(document.getElementById("Tmax").value);
  if (!Number.isFinite(T1) || !Number.isFinite(T2) || T1 >= T2) {
    document.getElementById("layerRows").textContent = "Set valid T₁ < T₂ in main controls first.";
    return;
  }

  const pts = 201;
  const Tvec = linspace(T1, T2, pts);
  const rows = [];
  let Rtot = 0;

  for (let i = 1; i <= 3; i++) {
    const matKey = document.getElementById("layMat" + i).value;
    const L = parseFloat(document.getElementById("layL" + i).value);
    const A = parseFloat(document.getElementById("layA" + i).value);
    if (!(L > 0) || !(A > 0)) continue;

    const mat = materialDatabase.materials[matKey];
    if (!mat) continue;

    const kVec = Tvec.map((T) => propertyValue(mat, "k", T));
    const integral = trapezoidIntegral(Tvec, kVec);
    const kavg = integral / (T2 - T1);
    const R = L / (A * kavg);
    Rtot += R;
    rows.push(
      `Layer ${i}: ${mat.name};  k_avg = ${kavg.toExponential(4)} W/(m·K);  R = ${R.toExponential(4)} K/W`
    );
  }

  const Q = Rtot > 0 ? Math.abs(T2 - T1) / Rtot : NaN;
  const fmtN = (v, d) => Number.isFinite(v) ? v.toExponential(d) : "n/a";

  document.getElementById("layerQ").textContent = fmtN(Q, 4) + (Number.isFinite(Q) ? " W" : "");
  document.getElementById("layerR").textContent = fmtN(Rtot, 4) + (Rtot > 0 ? " K/W" : "");
  const statusEl = document.getElementById("layerStatus");
  const pass = rows.length > 0 && Number.isFinite(Q);
  statusEl.textContent = pass ? "PASS" : "CHECK";
  statusEl.className = pass ? "ok" : "warning";
  document.getElementById("layerRows").textContent =
    rows.length ? rows.join("\n") : "No active layers (set L > 0).";
}

function calculate() {
  const materialKey = document.getElementById("materialSelect").value;
  const material = materialDatabase.materials[materialKey];
  const property = document.getElementById("propertySelect").value;
  const Tmin = parseFloat(document.getElementById("Tmin").value);
  const Tmax = parseFloat(document.getElementById("Tmax").value);
  const nsteps = parseInt(document.getElementById("nsteps").value);
  const method = document.getElementById("integrationMethod").value;
  const mass = parseFloat(document.getElementById("massInput").value) || 1;
  const knownLength = parseFloat(document.getElementById("knownLengthInput")?.value) || 1;
  const lengthReference = document.getElementById("lengthReferenceSelect")?.value || "L293";

  if (!material?.properties?.[property]) {
    const errDiv = document.getElementById("calcError");
    if (errDiv) errDiv.textContent = `No ${property} data for ${material?.name || materialKey || "(none selected)"}. Select a different material or property.`;
    return;
  }
  const errDiv = document.getElementById("calcError");
  if (errDiv) errDiv.textContent = "";

  // Clear cursor pins if material/property/range context changed
  const pinContext = `${materialKey}_${property}_${Tmin}_${Tmax}`;
  if (lastPinContext !== null && lastPinContext !== pinContext) {
    cursorPins = [];
    updatePinsUI();
  }
  lastPinContext = pinContext;

  const T = linspace(Tmin, Tmax, nsteps);
  const values = T.map(t => propertyValue(material, property, t) || 0);

  const plotPoints = parseInt(document.getElementById("plotPoints")?.value) || 200;
  const plotT = linspace(Tmin, Tmax, plotPoints);
  const plotValues = plotT.map(t => propertyValue(material, property, t) || 0);

  const evaluator = t => propertyValue(material, property, t) || 0;
  const methodResults = {
    trapezoid: trapezoidIntegral(T, values),
    simpson: simpsonIntegralUniform(T, values),
    romberg: rombergIntegration(evaluator, Tmin, Tmax, 8),
    gauss: gaussLegendre4(evaluator, Tmin, Tmax, nsteps - 1)
  };

  const rombergRef = methodResults.romberg;
  const methodDeltasPct = {
    trapezoid: rombergRef === 0 ? 0 : ((methodResults.trapezoid - rombergRef) / rombergRef) * 100,
    simpson: rombergRef === 0 ? 0 : ((methodResults.simpson - rombergRef) / rombergRef) * 100,
    romberg: 0,
    gauss: rombergRef === 0 ? 0 : ((methodResults.gauss - rombergRef) / rombergRef) * 100
  };

  let integral = 0;
  if (method === "trapezoid") {
    integral = methodResults.trapezoid;
  } else if (method === "simpson") {
    integral = methodResults.simpson;
  } else if (method === "romberg") {
    integral = methodResults.romberg;
  } else if (method === "gauss") {
    integral = methodResults.gauss;
  }

  currentState = {
    materialKey,
    material,
    property,
    Tmin,
    Tmax,
    nsteps,
    method,
    mass,
    knownLength,
    lengthReference,
    T,
    values,
    plotT,
    plotValues,
    cumulativeIntegral: [],
    dydT: [],
    integral,
    methodResults,
    methodDeltasPct
  };

  updatePlot();
  updateTable();
  updateResults();
  updateDeltaSummary();
  updateQuickOutputs();
  updateMethodComparison();
  updateEquationPanel();
  updateDebug();
  applyResultModeVisibility();
}

function updateEquationPanel() {
  if (!currentState) {
    return;
  }
  const panel = document.getElementById("equationPanel");
  if (!panel) {
    return;
  }
  panel.textContent = equationText(currentState.material, currentState.property);
}

function updatePlot() {
  const { plotT, plotValues, property, material, Tmin, Tmax, mass } = currentState;
  const propertyPresentation = getPropertyPresentation(property);

  const yAxisTitle = property === "k"
    ? "Thermal Conductivity k(T) [W/(m\u00b7K)]"
    : property === "cp"
      ? "Specific Heat cp(T) [J/(kg\u00b7K)]"
      : "Thermal Contraction Y(T) [x1e-5]";
  const yMinVal = document.getElementById("yAxisMin")?.value;
  const yMaxVal = document.getElementById("yAxisMax")?.value;
  const yMin = yMinVal !== "" ? parseFloat(yMinVal) : null;
  const yMax = yMaxVal !== "" ? parseFloat(yMaxVal) : null;
  const yRange = (yMin !== null && yMax !== null && !isNaN(yMin) && !isNaN(yMax)) ? [yMin, yMax] : undefined;

  const isDark = document.documentElement.getAttribute("data-theme") === "dark";
  const fontColor = isDark ? "#e0e0e0" : "#20242a";
  const gridColor = isDark ? "#2a3550" : "#d8dde6";

  const trace = {
    x: plotT,
    y: plotValues,
    type: "scatter",
    mode: "lines",
    name: material.name,
    line: { color: "#60a5fa", width: 2 }
  };

  const mainLegend = chooseAdaptiveLegendPlacement(plotT, plotValues, 1 + cursorPins.length);

  const layout = {
    xaxis: { title: "Temperature [K]", color: fontColor, gridcolor: gridColor },
    yaxis: { title: yAxisTitle, color: fontColor, gridcolor: gridColor, ...(yRange ? { range: yRange } : {}) },
    legend: {
      ...mainLegend,
      bgcolor: isDark ? "rgba(15,17,23,0.58)" : "rgba(255,255,255,0.72)",
      bordercolor: gridColor,
      borderwidth: 1,
      font: { size: 10, color: fontColor }
    },
    font: { color: fontColor },
    margin: { l: 60, r: 40, t: 40, b: 50 },
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)"
  };

  Plotly.newPlot("mainPlot", [trace], layout, { responsive: true });
  attachCursorPinHandler();

  const cumulativeIntegral = [0];
  for (let i = 1; i < plotT.length; i++) {
    const dT = plotT[i] - plotT[i - 1];
    const area = 0.5 * (plotValues[i] + plotValues[i - 1]) * dT;
    cumulativeIntegral.push(cumulativeIntegral[i - 1] + area);
  }
  currentState.cumulativeIntegral = cumulativeIntegral;

  const integrationTrace = {
    x: plotT,
    y: plotValues,
    type: "scatter",
    mode: "lines",
    fill: "tozeroy",
    name: `${propertyPresentation.functionLabel}`,
    line: { color: "#4ade80", width: 2 },
    yaxis: "y"
  };

  const cumulativeTrace = {
    x: plotT,
    y: cumulativeIntegral,
    type: "scatter",
    mode: "lines",
    name: "Cumulative integral",
    line: { color: "#f59e0b", width: 2, dash: "dot" },
    yaxis: "y2"
  };

  const endpointY1 = propertyValue(material, property, Tmin) || 0;
  const endpointY2 = propertyValue(material, property, Tmax) || 0;
  const endpointLabelPrefix = property === "k" ? "k" : property === "cp" ? "cp" : "Y";
  const [endpointT1Position, endpointT2Position] = chooseEndpointLabelPositions(
    plotT,
    plotValues,
    [
      { x: Tmin, y: endpointY1 },
      { x: Tmax, y: endpointY2 }
    ]
  );
  const endpointT1Trace = {
    x: [Tmin],
    y: [endpointY1],
    type: "scatter",
    mode: "markers+text",
    name: "Endpoint values",
    marker: { color: "#ef4444", size: 10, symbol: "diamond" },
    text: [`${endpointLabelPrefix}(T1)=${formatPropertyValue(endpointY1)}`],
    textposition: endpointT1Position,
    textfont: { size: 12 },
    showlegend: false
  };

  const endpointT2Trace = {
    x: [Tmax],
    y: [endpointY2],
    type: "scatter",
    mode: "markers+text",
    name: "Endpoint values",
    marker: { color: "#22c55e", size: 10, symbol: "diamond" },
    text: [`${endpointLabelPrefix}(T2)=${formatPropertyValue(endpointY2)}`],
    textposition: endpointT2Position,
    textfont: { size: 12 },
    showlegend: false
  };

  const endpointLegendTrace = {
    x: [null],
    y: [null],
    type: "scatter",
    mode: "markers",
    name: "Endpoints (diamonds)",
    marker: { color: "#64748b", size: 10, symbol: "diamond" },
    hoverinfo: "skip",
    showlegend: true
  };

  const integralExpr = `I(T) = ∫[Tmin→T] ${propertyPresentation.functionLabel} dT`;
  const endpointUnits = property === "k" ? "W/(m·K)" : property === "cp" ? "J/(kg·K)" : "x1e-5";
  const endpointExpr = `<span style=\"color:#ef4444;\">${endpointLabelPrefix}(T1)=${formatPropertyValue(endpointY1)} ${endpointUnits}</span> · <span style=\"color:#22c55e;\">${endpointLabelPrefix}(T2)=${formatPropertyValue(endpointY2)} ${endpointUnits}</span>`;

  const integrationLayout = {
    title: {
      text: `${integralExpr}<br><span style="font-size:12px;">${endpointExpr}</span>`
    },
    xaxis: { title: "Temperature [K]", color: fontColor, gridcolor: gridColor },
    yaxis: {
      title: property === "k"
        ? "Property value: k(T) [W/(m\u00b7K)]"
        : property === "cp"
          ? "Property value: cp(T) [J/(kg\u00b7K)]"
          : "Property value: Y(T) [x1e-5]",
      color: fontColor,
      gridcolor: gridColor
    },
    yaxis2: {
      title: property === "k" ? "Cumulative integral [W/m]" : property === "cp" ? "Cumulative integral [J/kg]" : "Cumulative integral [x1e-5·K]",
      color: fontColor,
      overlaying: "y",
      side: "right",
      showgrid: false
    },
    legend: {
      x: 0.02,
      y: 0.98,
      xanchor: "left",
      yanchor: "top",
      orientation: "h",
      bgcolor: isDark ? "rgba(15,17,23,0.55)" : "rgba(255,255,255,0.65)",
      bordercolor: gridColor,
      borderwidth: 1
    },
    font: { color: fontColor },
    margin: { l: 70, r: 70, t: 72, b: 50 },
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)"
  };

  Plotly.newPlot("integrationPlot", [integrationTrace, cumulativeTrace, endpointT1Trace, endpointT2Trace, endpointLegendTrace], integrationLayout, { responsive: true });

  // B3 plot: local rate-of-change with knee indicator
  const dydT = [];
  for (let i = 0; i < plotT.length; i++) {
    if (i === 0) {
      dydT.push((plotValues[i + 1] - plotValues[i]) / (plotT[i + 1] - plotT[i]));
    } else if (i === plotT.length - 1) {
      dydT.push((plotValues[i] - plotValues[i - 1]) / (plotT[i] - plotT[i - 1]));
    } else {
      dydT.push((plotValues[i + 1] - plotValues[i - 1]) / (plotT[i + 1] - plotT[i - 1]));
    }
  }
  currentState.dydT = dydT;

  let kneeIdx = 1;
  let maxCurvature = -Infinity;
  for (let i = 1; i < dydT.length - 1; i++) {
    const dSlope = Math.abs(dydT[i + 1] - dydT[i - 1]);
    if (dSlope > maxCurvature) {
      maxCurvature = dSlope;
      kneeIdx = i;
    }
  }

  const kneeT = plotT[kneeIdx];
  const kneeSlope = dydT[kneeIdx];
  const derivLabel = property === "k" ? "dk/dT" : property === "cp" ? "dcp/dT" : "dY/dT";
  const derivUnits = property === "k" ? "W/(m·K²)" : property === "cp" ? "J/(kg·K²)" : "x1e-5/K";
  const b3LegendBox = getLegendBounds({ x: 0.98, y: 0.98, xanchor: "right", yanchor: "top" }, 0.2, 0.1);
  const kneeTextPosition = choosePointLabelPosition(plotT, dydT, { x: kneeT, y: kneeSlope }, {
    candidates: ["top left", "bottom left", "middle left", "bottom center", "top center", "bottom right", "top right"],
    boxWidth: 0.2,
    boxHeight: 0.08,
    avoidBoxes: [b3LegendBox]
  });

  Plotly.newPlot("ratePlot", [
    {
      x: plotT,
      y: dydT,
      type: "scatter",
      mode: "lines",
      name: derivLabel,
      line: { color: "#8b5cf6", width: 2 }
    },
    {
      x: [kneeT],
      y: [kneeSlope],
      type: "scatter",
      mode: "markers+text",
      name: "Knee indicator",
      marker: { color: "#ef4444", size: 10, symbol: "diamond" },
      text: [`Knee @ ${formatTemperature(kneeT)} K`],
      textposition: kneeTextPosition,
      textfont: {
        size: 12,
        color: isDark ? "#f8fafc" : "#111827"
      }
    }
  ], {
    title: `${derivLabel} vs Temperature<br><span style="font-size:12px;color:${fontColor};">Knee estimate where slope change is strongest</span>`,
    xaxis: { title: "Temperature [K]", color: fontColor, gridcolor: gridColor },
    yaxis: { title: `${derivLabel} [${derivUnits}]`, color: fontColor, gridcolor: gridColor },
    legend: {
      x: 0.98,
      y: 0.98,
      xanchor: "right",
      yanchor: "top",
      bgcolor: isDark ? "rgba(15,17,23,0.58)" : "rgba(255,255,255,0.72)",
      bordercolor: gridColor,
      borderwidth: 1
    },
    font: { color: fontColor },
    margin: { l: 70, r: 30, t: 72, b: 50 },
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)"
  }, { responsive: true });
}

function updateTable() {
  const { T, values, property } = currentState;
  const unit = property === "k" ? "W/(m·K)" : property === "cp" ? "J/(kg·K)" : "x1e-5";
  const last = Math.max(0, T.length - 1);
  const desiredRows = 10;
  const isDark = document.body.classList.contains("dark");
  const sampled = [];

  if (last === 0) {
    sampled.push(0);
  } else {
    // Force endpoints, then distribute interior points for consistent readability.
    sampled.push(0);
    for (let i = 1; i < desiredRows - 1; i += 1) {
      sampled.push(Math.round((i * last) / (desiredRows - 1)));
    }
    sampled.push(last);
  }

  const indices = Array.from(new Set(sampled)).sort((a, b) => a - b);
  const rows = indices.map((idx, listPos) => {
    const isP1 = idx === 0;
    const isP2 = idx === last;
    const pointLabel = idx === 0
      ? "Point 1 (T1)"
      : idx === last
        ? "Point 2 (T2)"
        : `Sample ${listPos}`;
    const rowStyle = isP1
      ? `background:${isDark ? "rgba(254,226,226,0.92)" : "rgba(254,226,226,0.95)"}; color:${isDark ? "#111827" : "inherit"}; box-shadow: inset 4px 0 0 #ef4444;`
      : isP2
        ? `background:${isDark ? "rgba(220,252,231,0.92)" : "rgba(220,252,231,0.95)"}; color:${isDark ? "#111827" : "inherit"}; box-shadow: inset 4px 0 0 #22c55e;`
        : "";
    const labelStyle = isP1
      ? `color:#b91c1c; font-weight:700;`
      : isP2
        ? `color:#166534; font-weight:700;`
        : "font-weight:600;";
    return `<tr style="${rowStyle}"><td style="${labelStyle}">${pointLabel}</td><td>${formatTemperature(T[idx])}</td><td>${formatPropertyValue(values[idx])}</td><td>${unit}</td></tr>`;
  });

  document.getElementById("evalTable").innerHTML = `
    <table>
      <thead><tr><th>Point</th><th>Temperature [K]</th><th>Value</th><th>Unit</th></tr></thead>
      <tbody>${rows.join("")}</tbody>
    </table>
  `;
}

function updateResults() {
  const { integral, property, mass, Tmin, Tmax, method } = currentState;
  const selectedMethodLabel = getMethodLabel(method);
  const propertyPresentation = getPropertyPresentation(property);

  if (property === "k") {
    document.getElementById("integrationResults").innerHTML = `
      <p><strong>Selected Method:</strong> ${selectedMethodLabel}</p>
      <p title="Formula used by the active integration method."><em>${methodEquationNote(method)}</em></p>
      <p title="Integral of the selected property over the chosen temperature range."><strong>Integral of ${propertyPresentation.functionLabel} dT:</strong> ${formatIntegralValue(integral)} ${propertyPresentation.integralUnits}</p>
      <p title="Average property value defined as integral divided by temperature span, not the arithmetic mean of endpoint values."><strong>Average k:</strong> ${formatPropertyValue(integral / Math.abs(Tmax - Tmin))} ${propertyPresentation.valueUnits} (= \u222bk dT / |T2\u2212T1|, not endpoint mean)</p>
      <p><strong>Temperature range:</strong> ${formatTemperature(Tmin)} K to ${formatTemperature(Tmax)} K</p>
      <p><em>Note: This integral is the selected property over the chosen temperature range. For heat-load use, combine k(T) results with the applicable area/length ratio.</em></p>
    `;

    document.getElementById("energyResults").innerHTML = `
      <p><em>Energy calculation is not derived from thermal conductivity k(T) alone. Use cp(T) to obtain mass-based energy over the temperature range.</em></p>
    `;
  } else if (property === "cp") {
    const energy = mass * integral;
    document.getElementById("integrationResults").innerHTML = `
      <p><strong>Selected Method:</strong> ${selectedMethodLabel}</p>
      <p title="Formula used by the active integration method."><em>${methodEquationNote(method)}</em></p>
      <p title="Integral of the selected property over the chosen temperature range."><strong>Integral of ${propertyPresentation.functionLabel} dT:</strong> ${formatIntegralValue(integral)} ${propertyPresentation.integralUnits}</p>
      <p title="Average property value defined as integral divided by temperature span, not the arithmetic mean of endpoint values."><strong>Average cp:</strong> ${formatPropertyValue(integral / Math.abs(Tmax - Tmin))} ${propertyPresentation.valueUnits} (= \u222bcp dT / |T2\u2212T1|, not endpoint mean)</p>
      <p><strong>Temperature range:</strong> ${formatTemperature(Tmin)} K to ${formatTemperature(Tmax)} K</p>
      <p><em>This integral represents the selected specific-heat curve over the chosen temperature range.</em></p>
    `;

    document.getElementById("energyResults").innerHTML = `
      <p><strong>Mass:</strong> ${mass} kg</p>
      <p><strong>Total Energy:</strong> ${formatIntegralValue(energy)} J</p>
      <p><strong>Total Energy:</strong> ${formatIntegralValue(energy / 1000)} kJ</p>
      <p><em>Energy required for cooldown/warmup between ${formatTemperature(Tmin)}K and ${formatTemperature(Tmax)}K.</em></p>
    `;
  } else {
    const tc = getThermalContractionMetrics();
    document.getElementById("integrationResults").innerHTML = `
      <p><strong>Selected Method:</strong> ${selectedMethodLabel}</p>
      <p title="Formula used by the active integration method."><em>${methodEquationNote(method)}</em></p>
      <p><strong>Primary model:</strong> Y(T) = [(L(T) - L293) / L293] × 1e5</p>
      <p><strong>Y(T1):</strong> ${Number.isFinite(tc.y1) ? tc.y1.toFixed(6) : "n/a"} x1e-5; <strong>Y(T2):</strong> ${Number.isFinite(tc.y2) ? tc.y2.toFixed(6) : "n/a"} x1e-5</p>
      <p><strong>Δstrain (T1→T2):</strong> ${Number.isFinite(tc.deltaStrain) ? tc.deltaStrain.toExponential(6) : "n/a"} m/m</p>
      <p><strong>Temperature range:</strong> ${formatTemperature(Tmin)} K to ${formatTemperature(Tmax)} K</p>
      <p><em>Integral values are shown for numerical transparency only. Engineering length change is computed from Y(T) values and length reference mode.</em></p>
    `;

    document.getElementById("energyResults").innerHTML = `
      <p><strong>Known Length Reference:</strong> ${tc.lengthRef === "L293" ? "L293" : "Length at T1"}</p>
      <p><strong>L(T1):</strong> ${Number.isFinite(tc.L1) ? tc.L1.toExponential(6) + " m" : "n/a"}</p>
      <p><strong>L(T2):</strong> ${Number.isFinite(tc.L2) ? tc.L2.toExponential(6) + " m" : "n/a"}</p>
      <p><strong>Delta Length:</strong> ${Number.isFinite(tc.deltaL) ? tc.deltaL.toExponential(6) + " m" : "n/a"}</p>
      <p><strong>Delta Length:</strong> ${Number.isFinite(tc.deltaL) ? (tc.deltaL * 1000).toExponential(6) + " mm" : "n/a"}</p>
      <p><em>Sign convention: negative = contraction, positive = expansion.</em></p>
    `;
  }
}

function updateMethodComparison() {
  const { property, methodResults, methodDeltasPct } = currentState;
  const unit = property === "k" ? "W/m" : property === "cp" ? "J/kg" : "x1e-5·K";

  const methods = [
    { name: "Trapezoid", key: "trapezoid" },
    { name: "Simpson fixed", key: "simpson" },
    { name: "Romberg", key: "romberg" },
    { name: "Gauss-Legendre 4-pt", key: "gauss" }
  ].map(item => {
    const value = formatIntegralValue(methodResults[item.key]);
    const delta = item.key === "romberg" ? "0.000000" : formatPercent(methodDeltasPct[item.key]);
    return {
      ...item,
      value,
      delta,
      rawValue: Number(methodResults[item.key]),
      rawDelta: item.key === "romberg" ? 0 : Number(methodDeltasPct[item.key])
    };
  });

  const rows = methods.map(item => `<tr><td>${item.name}</td><td>${item.value}</td><td>${unit}</td><td>${item.delta}</td></tr>`);
  const nonRomberg = methods.filter(m => m.key !== "romberg");
  const maxAbsDelta = Math.max(...nonRomberg.map(m => Math.abs(m.rawDelta)), 0);
  const spread = Math.max(...methods.map(m => m.rawValue)) - Math.min(...methods.map(m => m.rawValue));
  const best = nonRomberg.reduce((a, b) => Math.abs(a.rawDelta) <= Math.abs(b.rawDelta) ? a : b, nonRomberg[0]);
  const worst = nonRomberg.reduce((a, b) => Math.abs(a.rawDelta) >= Math.abs(b.rawDelta) ? a : b, nonRomberg[0]);

  const bars = methods.map(m => {
    const width = maxAbsDelta > 0 ? Math.max(2, (Math.abs(m.rawDelta) / maxAbsDelta) * 100) : 2;
    const cls = m.rawDelta > 0 ? "pos" : m.rawDelta < 0 ? "neg" : "ref";
    return `<div class="cmp-bar-row"><span>${m.name}</span><div class="cmp-bar-track"><div class="cmp-bar ${cls}" style="width:${width}%;"></div></div><b>${m.delta}%</b></div>`;
  }).join("");

  document.getElementById("methodComparisonResults").innerHTML = `
    <div class="cmp-summary">
      <div><strong>Best agreement vs Romberg:</strong> ${best.name} (${formatPercent(best.rawDelta)}%)</div>
      <div><strong>Largest deviation:</strong> ${worst.name} (${formatPercent(worst.rawDelta)}%)</div>
      <div><strong>Integral spread:</strong> ${formatIntegralValue(spread)} ${unit}</div>
    </div>
    <div class="cmp-bars">${bars}</div>
    <table>
      <thead><tr><th>Method</th><th>Integral</th><th>Unit</th><th>% vs Romberg</th></tr></thead>
      <tbody>${rows.join("")}</tbody>
    </table>
  `;
}

function updateDebug() {
  const panel = document.getElementById("debugPanel");
  const auditPanel = document.getElementById("vbaAuditPanel");
  const debugEnabled = !!document.getElementById("debugMode")?.checked;

  if (auditPanel) {
    auditPanel.style.display = debugEnabled ? "" : "none";
  }

  if (!debugEnabled) {
    panel.innerHTML = "";
    return;
  }
  const { materialKey, material, property, Tmin, Tmax, nsteps, method, integral } = currentState;
  
  panel.innerHTML = `
    <pre>Material: ${materialKey} - ${material.name}
Property: ${property}
Temperature Range: ${Tmin} K to ${Tmax} K
Number of Steps: ${nsteps}
Integration Method: ${method}
Integral Result: ${integral.toFixed(12)}

Material Source: ${material.source || "NIST"}
</pre>
  `;
}

function computeCumIntAtIndex(idx) {
  if (Array.isArray(currentState?.cumulativeIntegral) && Number.isFinite(currentState.cumulativeIntegral[idx])) {
    return currentState.cumulativeIntegral[idx];
  }
  const { plotT, plotValues } = currentState;
  let acc = 0;
  for (let i = 1; i <= idx; i++) {
    acc += 0.5 * (plotValues[i] + plotValues[i - 1]) * (plotT[i] - plotT[i - 1]);
  }
  return acc;
}

function computeRateAtIndex(idx) {
  if (Array.isArray(currentState?.dydT) && Number.isFinite(currentState.dydT[idx])) {
    return currentState.dydT[idx];
  }
  const { plotT, plotValues } = currentState;
  if (idx <= 0) {
    return (plotValues[1] - plotValues[0]) / (plotT[1] - plotT[0]);
  }
  if (idx >= plotT.length - 1) {
    return (plotValues[idx] - plotValues[idx - 1]) / (plotT[idx] - plotT[idx - 1]);
  }
  return (plotValues[idx + 1] - plotValues[idx - 1]) / (plotT[idx + 1] - plotT[idx - 1]);
}

function attachCursorPinHandler() {
  const mainPlotEl = document.getElementById("mainPlot");
  if (!mainPlotEl || !currentState) return;

  // Transparent hit-area trace makes the line surface clickable
  Plotly.addTraces("mainPlot", [{
    x: currentState.plotT,
    y: currentState.plotValues,
    type: "scatter",
    mode: "markers",
    marker: { size: 10, opacity: 0 },
    showlegend: false,
    hoverinfo: "skip",
    name: "_hit"
  }]);

  // Re-render surviving pins (same context re-calculate)
  renderPinMarkers();

  mainPlotEl.on("plotly_click", (eventData) => {
    if (!currentState || !eventData.points.length) return;
    const clickedT = eventData.points[0].x;
    const idx = currentState.plotT.reduce(
      (best, t, i) => Math.abs(t - clickedT) < Math.abs(currentState.plotT[best] - clickedT) ? i : best,
      0
    );
    const pin = {
      idx,
      T: currentState.plotT[idx],
      value: currentState.plotValues[idx],
      cumulativeIntegral: computeCumIntAtIndex(idx),
      rate: computeRateAtIndex(idx)
    };
    if (cursorPins.length >= 3) cursorPins.shift();
    cursorPins.push(pin);
    renderPinMarkers();
    updatePinsUI();
  });
}

function renderPinMarkers() {
  const plotEl = document.getElementById("mainPlot");
  if (!plotEl || !plotEl.data) return;
  // Remove all traces beyond index 1 (line + hit-area)
  while (plotEl.data.length > 2) {
    Plotly.deleteTraces("mainPlot", -1);
  }
  const pinColors = ["#f87171", "#fbbf24", "#a78bfa"];
  cursorPins.forEach((pin, i) => {
    Plotly.addTraces("mainPlot", [{
      x: [pin.T],
      y: [pin.value],
      mode: "markers",
      type: "scatter",
      marker: { size: 14, color: pinColors[i], symbol: "diamond" },
      name: `Pin ${i + 1}: T=${pin.T.toFixed(2)} K, Value=${pin.value.toFixed(6)}`,
      showlegend: true,
      hovertemplate: `T=%{x:.2f} K<br>Value=%{y:.6f}<extra>Pin ${i + 1}</extra>`
    }]);
  });

  const integrationPlotEl = document.getElementById("integrationPlot");
  if (integrationPlotEl && integrationPlotEl.data) {
    while (integrationPlotEl.data.length > 5) {
      Plotly.deleteTraces("integrationPlot", -1);
    }
    cursorPins.forEach((pin, i) => {
      Plotly.addTraces("integrationPlot", [
        {
          x: [pin.T],
          y: [pin.value],
          type: "scatter",
          mode: "markers",
          marker: { size: 12, color: pinColors[i], symbol: "diamond" },
          showlegend: false,
          hovertemplate: `T=%{x:.2f} K<br>Value=%{y:.6f}<extra>B2 property Pin ${i + 1}</extra>`
        },
        {
          x: [pin.T],
          y: [pin.cumulativeIntegral],
          type: "scatter",
          mode: "markers",
          yaxis: "y2",
          marker: { size: 11, color: pinColors[i], symbol: "circle-open", line: { width: 2, color: pinColors[i] } },
          showlegend: false,
          hovertemplate: `T=%{x:.2f} K<br>Cumulative integral=%{y:.6f}<extra>B2 integral Pin ${i + 1}</extra>`
        }
      ]);
    });
  }

  const ratePlotEl = document.getElementById("ratePlot");
  if (ratePlotEl && ratePlotEl.data) {
    while (ratePlotEl.data.length > 2) {
      Plotly.deleteTraces("ratePlot", -1);
    }
    cursorPins.forEach((pin, i) => {
      Plotly.addTraces("ratePlot", [{
        x: [pin.T],
        y: [pin.rate],
        type: "scatter",
        mode: "markers",
        marker: { size: 12, color: pinColors[i], symbol: "diamond" },
        showlegend: false,
        hovertemplate: `T=%{x:.2f} K<br>Rate=%{y:.6f}<extra>B3 rate Pin ${i + 1}</extra>`
      }]);
    });
  }
}

function updatePinsUI() {
  const panel = document.getElementById("cursorPinsTable");
  if (!panel) return;
  const exportBtn = document.getElementById("exportPinsCsvBtn");
  if (exportBtn) exportBtn.disabled = cursorPins.length === 0;
  if (cursorPins.length === 0) {
    panel.innerHTML = "<p style='color:var(--muted);font-size:0.9rem;'>Click on the main plot curve to pin up to 3 reference points.</p>";
    return;
  }
  const prop = currentState?.property || "k";
  const unit = prop === "k" ? "W/(m\u00b7K)" : prop === "cp" ? "J/(kg\u00b7K)" : "x1e-5";
  const intUnit = prop === "k" ? "W/m" : prop === "cp" ? "J/kg" : "x1e-5\u00b7K";
  const rateUnit = prop === "k" ? "W/(m\u00b7K\u00b2)" : prop === "cp" ? "J/(kg\u00b7K\u00b2)" : "x1e-5/K";
  const pinColors = ["#f87171", "#fbbf24", "#a78bfa"];
  const rows = cursorPins.map((pin, i) => `
    <tr>
      <td style="color:${pinColors[i]};font-weight:600;">\uD83D\uDCCD ${i + 1}</td>
      <td>${pin.T.toFixed(3)}</td>
      <td>${pin.value.toFixed(6)}</td>
      <td style="color:var(--muted);">${unit}</td>
      <td>${pin.cumulativeIntegral.toFixed(6)}</td>
      <td style="color:var(--muted);">${intUnit}</td>
      <td>${Number.isFinite(pin.rate) ? pin.rate.toFixed(6) : "n/a"}</td>
      <td style="color:var(--muted);">${rateUnit}</td>
    </tr>`).join("");
  panel.innerHTML = `
    <table style="width:100%;border-collapse:collapse;font-size:0.9rem;">
      <thead><tr style="border-bottom:1px solid var(--border,#2a3550);">
        <th style="text-align:left;padding:4px 8px;">Pin</th>
        <th style="text-align:left;padding:4px 8px;">T [K]</th>
        <th style="text-align:left;padding:4px 8px;">Value</th>
        <th style="text-align:left;padding:4px 8px;">Unit</th>
        <th style="text-align:left;padding:4px 8px;">Cumul. Integral</th>
        <th style="text-align:left;padding:4px 8px;">Int. Unit</th>
        <th style="text-align:left;padding:4px 8px;">Rate</th>
        <th style="text-align:left;padding:4px 8px;">Rate Unit</th>
      </tr></thead>
      <tbody>${rows}</tbody>
    </table>
    <p style="margin-top:8px;color:var(--muted);font-size:0.85rem;">Pins are selected once on B1 and mirrored onto B2 (value + cumulative integral) and B3 (rate of change).</p>`;
}

function clearPins() {
  cursorPins = [];
  const plotEl = document.getElementById("mainPlot");
  if (plotEl && plotEl.data) {
    while (plotEl.data.length > 2) {
      Plotly.deleteTraces("mainPlot", -1);
    }
  }
  const integrationPlotEl = document.getElementById("integrationPlot");
  if (integrationPlotEl && integrationPlotEl.data) {
    while (integrationPlotEl.data.length > 5) {
      Plotly.deleteTraces("integrationPlot", -1);
    }
  }
  const ratePlotEl = document.getElementById("ratePlot");
  if (ratePlotEl && ratePlotEl.data) {
    while (ratePlotEl.data.length > 2) {
      Plotly.deleteTraces("ratePlot", -1);
    }
  }
  updatePinsUI();
}

function setupExport() {
  document.getElementById("exportCsvBtn").addEventListener("click", () => {
    if (!currentState) {
      alert("Please calculate first");
      return;
    }

    const mode = getCurrentResultMode();
    const blob = new Blob([buildModularCsvText(currentState, mode)], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${currentState.materialKey}_${currentState.property}_${currentState.Tmin}-${currentState.Tmax}K.csv`;
    a.click();
    URL.revokeObjectURL(url);
  });

  document.getElementById("exportJsonBtn").addEventListener("click", () => {
    if (!currentState) {
      alert("Please calculate first");
      return;
    }

    const jsonData = buildModularJsonData(currentState, getCurrentResultMode());

    const blob = new Blob([JSON.stringify(jsonData, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${currentState.materialKey}_${currentState.property}_${currentState.Tmin}-${currentState.Tmax}K.json`;
    a.click();
    URL.revokeObjectURL(url);
  });

  document.getElementById("downloadPlotBtn").addEventListener("click", async () => {
    await downloadMainPlotPng(document);
  });

  document.getElementById("exportPinsCsvBtn")?.addEventListener("click", () => {
    if (!currentState || cursorPins.length === 0) {
      alert("No pins set. Click on the main plot to pin up to 3 reference points first.");
      return;
    }
    const prop = currentState.property;
    const unit = prop === "k" ? "W_per_mK" : prop === "cp" ? "J_per_kgK" : "x1e-5";
    const intUnit = prop === "k" ? "W_per_m" : prop === "cp" ? "J_per_kg" : "x1e-5_K";
    let csv = `Material,${currentState.material.name}\nProperty,${prop}\nT_range,${currentState.Tmin}-${currentState.Tmax}K\n\n`;
    csv += `Pin,T_K,Value_${unit},Cumulative_Integral_${intUnit}\n`;
    cursorPins.forEach((pin, i) => {
      csv += `${i + 1},${pin.T.toFixed(6)},${pin.value.toFixed(9)},${pin.cumulativeIntegral.toFixed(9)}\n`;
    });
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `cursor_pins_${currentState.materialKey}_${prop}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  });

  document.getElementById("clearPinsBtn")?.addEventListener("click", clearPins);
}

export async function initApp() {
  try {
    materialDatabase = await loadMaterialDatabase();
    populateMaterialSelect();
    populateLayerSelects();
    setupResultModeToggle();

    document.getElementById("calculateBtn").addEventListener("click", calculate);
    setupExport();

    const debugToggle = document.getElementById("debugMode");
    if (debugToggle) {
      debugToggle.addEventListener("change", () => {
        if (currentState) updateDebug();
      });
    }

    const propertySelect = document.getElementById("propertySelect");
    if (propertySelect) {
      propertySelect.addEventListener("change", () => {
        const currentMaterial = document.getElementById("materialSelect")?.value;
        populateMaterialSelect(currentMaterial);
        const selectedMaterial = document.getElementById("materialSelect")?.value;
        if (selectedMaterial) {
          calculate();
        }
      });
    }

    const materialSelect = document.getElementById("materialSelect");
    if (materialSelect) {
      materialSelect.addEventListener("change", () => {
        calculate();
      });
    }

    const yAxisInputHandler = () => { if (currentState) updatePlot(); };
    ["yAxisMin", "yAxisMax"].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.addEventListener("input", yAxisInputHandler);
    });

    const derivedInputHandler = () => {
      if (currentState) {
        updateDeltaSummary();
        updateQuickOutputs();
      }
    };
    ["areaInput", "lengthInput", "massInput", "knownLengthInput"].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.addEventListener("input", derivedInputHandler);
    });
    const lengthRefSelect = document.getElementById("lengthReferenceSelect");
    if (lengthRefSelect) lengthRefSelect.addEventListener("change", derivedInputHandler);

    window._appRefreshPlot = () => { if (currentState) updatePlot(); };

    const calcLayersBtn = document.getElementById("calcLayersBtn");
    if (calcLayersBtn) calcLayersBtn.addEventListener("click", calcLayersPanel);

    calculate();
  } catch (error) {
    document.body.insertAdjacentHTML(
      "afterbegin",
      `<div style="background: #fbbf24; color: #000; padding: 20px; margin: 20px; border-radius: 8px;">
        <strong>Error loading dashboard:</strong> ${error.message}<br>
        Tip: v0.4.6 uses ES6 modules. Open via a local server: <code>python -m http.server</code>
      </div>`
    );
    console.error(error);
  }
}
