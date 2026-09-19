# User-approved DOCX/PDF visual baseline — 2026-09-19

The corrected DOCX and PDF are now explicitly approved by the user and promoted as the immutable **visual regression baseline**.

Approval quote: `Approve docx and pdf !`

Bound hashes:
- DOCX: `e936ffcb89eb7da13b8be8d447c8453b5b4499a4907390816846f5c8ec94a6b9`
- PDF: `654e74630861b5b398ab577d55da5f692bf4549b0af480498822428109353b02`
- artifact bundle: `sha256:ce9c806aebcce0cc9f15eaaf728c4e2bb30e4e93cb2db26b80c9e8c3ce8db8f0`

This promotion is visual/render-only. JSON remains the semantic SSOT.

The next development slice is deliberately separate: a governed style layer for font families, sizes, palette, heading/number treatment, captions, requirement styling, tables, callouts and spacing. Every style change must generate a new candidate and render-diff against this accepted baseline.
