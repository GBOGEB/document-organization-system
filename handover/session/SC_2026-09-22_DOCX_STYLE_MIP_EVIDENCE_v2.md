# DOCX style MIP evidence receipt — 2026-09-22

The existing user-approved DOCX/PDF baseline remains unchanged.

The style candidate `QPS_TECH_GRAPHITE_TEAL_COPPER_V1` has now gained two additional proof layers:

1. **Deterministic render-host font resolution**
   - Aptos -> Liberation Sans
   - Aptos Display -> Liberation Sans
   - Aptos Mono -> Liberation Mono

2. **Visible token coverage specimen**
   - Title / Heading 1-3
   - special heading numbers
   - requirement ID
   - metadata labels
   - caption number
   - table header/borders
   - callout fill/accent

Bound consumer lineage:
- feature PR `GBOGEB/DOCX_RTM_Automation#74` -> `fbb931d28b551f33f6988882c9a983dc69dcde42`
- control PR `#75` -> `f7620c308be6fb4288b19f6dcd59e2a27df57d6a`
- render run `35730488674`, job `106754547718`
- artifact digest `sha256:f791e91b39604f5761e316ced3ef0c4cda6fcb39ef10c71aa3edd92d74516b00`

The source style hash remains `9338e9634185c5ae9184533ddc77541badd7ba84ea6bf7c9fb576c5c01a02df8`.

The first-red `STYLE_FONT_RESOLUTION_AND_VISIBLE_TOKEN_COVERAGE` is closed.

The remaining gate is still `USER_STYLE_REVIEW`. No style candidate replaces the accepted baseline without explicit user approval.
