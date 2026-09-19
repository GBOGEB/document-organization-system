# Governed DOCX style candidate receipt — 2026-09-19

The existing user-approved DOCX/PDF pair remains the immutable visual regression baseline.

A new **style-only candidate** is ready for review:

- style: `QPS_TECH_GRAPHITE_TEAL_COPPER_V1`
- body: graphite
- headings: deep teal
- heading numbers / requirement IDs / metadata labels / caption numbers: copper
- caption text: restrained neutral gray
- legacy Word-blue title rule: removed
- font sizes: governed at Word-native 0.5 pt increments
- fonts: user/system-installed font names only; no font files embedded or committed

Proof is bound to `GBOGEB/DOCX_RTM_Automation#71`, merge
`78de18967bae343b68f6e757c610262b2b385112`, exact render head
`92468c5fb9210144901729d5385c48cc858b1099`.

Semantic source and Markdown projection hashes are unchanged from the accepted
baseline. Final DOCX/PDF rendering is two pages, split-free, and passed
independent visual QA.

This receipt does **not** replace the accepted baseline. The next gate is
explicit user style review.
