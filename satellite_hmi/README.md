# Drive Satellite HMI / VFS (Issue #84)

A **read-only outward artifact projection**. The code does not provide a Drive synchronization bus, GitHub federation ledger, executable DAG scheduler, document authority, or QPS engineering admission. Existing Hub OID #1208 / PR #1209 and CODEX registry retain their owners.

## Local generation

```bash
python3 satellite_hmi/render.py satellite_hmi/fixtures/synthetic_manifest.json /tmp/satellite_hmi.html
python3 -m unittest discover -s satellite_hmi/tests -p 'test_*.py' -v
```

Open the generated HTML from disk; it is self-contained (no external JavaScript, network fetch or build). Only HTTPS source links are permitted. The HMI escapes all external strings and shows statuses without promoting them to approvals. Never embed sensitive Drive file IDs, ALX/MIN references, protected source documents or bearer tokens in public manifests or outputs.

The bundled `satellite_hmi/fixtures/synthetic_bundle.json` has two independently hashed demo text files. `notebooks/01_WORKTREE_HYDRATOR.ipynb` is a **separate Colab execution artifact**; inspect it in Colab, mount Drive manually, point `PILOT_DIR` to an authorized folder and run **dry-run validation first**. The notebook is not a skill-internal script, does not execute hydrated files, and does not sync GitHub automatically. A Colab runtime requires separate native evidence before release credit.

## Governance and acceptance (BSLN)

- [x] BSLN-01: Existing pilot inventory reconciled in owner issue #84; raw Drive details not copied here.
- [x] BSLN-02/03: Generic renderer with 20 HMI/hydration adversarial/smoke unit tests, pending exact-head CI qualification.
- [x] BSLN-04: Sanitized opt-in Colab notebook with bounded hydration and SHA-256 checks, **native Colab pending**.
- [x] BSLN-05/06: Owner reference boundary and engineering holds documented, not merged with source authority.
- [ ] BSLN-07: Native browser/mobile + Colab proof, required CI, independent exact-head review, explicit owner admission.

**Status:** DRAFT, no merge, no controlled publication, no engineering acceptance. `gdrive-worktree-hmi` remains a standalone declarative SKILL package and must be installed separately in a compatible runtime; a repository commit does not activate it.
