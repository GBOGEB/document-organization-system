# Graph Export Handling and Fallback Guide (v0.4.7)

## Scope

This note explains how B1/B2 graph exports behave, which theme/colors to expect,
and what fallback path to use when a browser print dialog does not open.

## Export Paths

1. Direct PNG button (main dashboard): uses theme-aware export from
   `js/plots.js`.
2. Intermediate render popup (Landscape View / PDF): generates a PNG in a popup
   and offers print/download.
3. Dashboard page export (A4) and slide export (16:9): uses SVG vector exports
   generated from Plotly clones.
4. B1/B2 full-page exports are dedicated to B1+B2 only.
5. B3 has its own dedicated A4 landscape page export (`B3 Rate Plot Page`).
6. B1/B2/B3 popup SVG buttons: direct data-URL SVG downloads.

## Style Impact Pictograms

The export panel includes quick visual hints:

- `🌓 Theme preview`: output follows current light/dark mode at click-time.
- `📐 Preset`: changes B1/B2 panel proportion (Golden, Fibonacci, Equal 1:1).
- `📊 Scale mode`: controls B1 y-axis behavior (linear or auto-log when valid).

## Theme Retention Rules

Theme is resolved at export generation time from
`document.documentElement.getAttribute("data-theme")`.

- If theme is `dark` at click time:
  - Background: `#0d1117`
  - Text/axes: light ink (`#e6edf3` or equivalent)
  - Grid: darker blue-gray (`#2a3550`)
- If theme is `light` at click time:
  - Background: light/white (`#f6f7f9` or `#ffffff`, depending on export layout)
  - Text/axes: dark ink (`#1e293b`/`#20242a`)
  - Grid: light gray (`#d8dde6`)

Important:

- The export does not auto-follow theme changes after it has already been
  generated.
- If you toggle theme, regenerate export to get matching colors.

## Why Intermediate Render Could Look Different

The intermediate popup is a separate document. If the image capture path does
not force explicit export colors, contrast can look off versus the live
dashboard.

Current behavior:

- Intermediate popup now uses the same controlled export pipeline as other
  exports.
- It renders a theme-aware PNG first, then shows it in the popup.
- Full-page and slide popups include `Open Browser Tab` as a print fallback in
  embedded preview environments.

## Print / Save PDF Behavior and Fallback

Some embedded/preview browser contexts (including IDE-hosted preview shells) may
ignore or suppress `window.print()`.

Use this order:

1. Click `Print / Save PDF` in the popup.
2. If nothing happens, click `Open Image Tab`.
3. Print/save PDF from the new tab using the browser menu (`Ctrl+P`).
4. If needed, use `Download PNG` and print from a system image viewer.

For B1/B2/B3 page exports:

1. Click `Print / Save PDF`.
2. If no dialog opens, click `Open Browser Tab`.
3. Print from that browser tab (`Ctrl+P`).

## B4 Normalized Benchmark (New)

B4 is a normalized equal-scale panel intended for quick shape comparison.

- Traces shown for selected material:
  - normalized `|actual value|`
  - normalized `|cumulative integral|`
  - normalized `|rate of change|`
- Reference overlays (when available for selected property):
  - Stainless Steel (`AISI316`)
  - Aluminum (`Al6061T6`)
  - Titanium (`Ti64`)
  - Copper (`CuRRR100`)
  - Composite (`G10Normal`)
- All normalized traces use equal y-scale (`0..1`) for direct visual comparison.

## B1 Comparison View Modes (v0.4.7)

The B1 comparison selector now supports three view modes:

- `Raw values`: default engineering-value view.
- `Normalized values`: each visible curve uses `y / max(|y|)` over the current
  range.
- `Split view: raw + normalized`: keeps B1 raw and shows B1N normalized panel.

Comparison selection policy:

- Maximum overlays is `4` (primary selected material is always included as solid
  line and not duplicated in dashed overlays).
- Materials without data for the active property are visible but disabled in the
  comparison selector (`no <property> data`).

## Recommended Workflow for PowerPoint

1. Prefer SVG from B1/B2 export buttons for PPT decks (vector quality, zoom-safe
   labels).
2. If PPT/SVG handling is inconsistent on a target machine, use PDF fallback.
3. If PDF import is constrained, use PNG fallback at high resolution.

## Quick Verification Checklist

- Set theme to dark, calculate, export PNG: axes and labels must remain
  readable.
- Set theme to light, repeat export: no low-contrast labels on white background.
- Open B2 SVG download directly in browser: no XML parse errors.
- Popup `Print / Save PDF`: works directly or via `Open Image Tab` fallback.
