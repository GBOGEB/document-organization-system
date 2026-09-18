# Gloob v1.2 — 3P* control receipt

This receipt closes the post-v1.2 3P* pass from fresh repository authority at main `220f612bc7d0975a592c587817059428b826c6b6`.

## Result

**Gloob v1.2 — Federated Mission Dispatch + Responder Runtime = CONTROL.**

This is a product/runtime control claim only. It creates no QPLANT engineering, negotiation, commercial, release, or source-authority credit.

## Proof chain

- v1.2 exact head: `6214d5f1a2235099a6ed23d142f694994b003ca4`
- exact-head contract: run `34936179068` — PASS
- v1.2 product merge: `9649677831a93bf519cb045bd2d16fab8a01c9da`
- fresh-main contract: run `34936608687` — PASS
- fresh-main control artifact: `10383532189`
- artifact digest: `sha256:f6fa3c567078347bdd3441cdade9a132f5a9c1826e4e1f046edc8e6e9553af86`
- fresh-main Pages: run `34936607875` — build/deploy/report PASS
- ABACUS runtime canary: run `34936014830` — PASS with real steps
- ABACUS fresh-main responder: run `34936427348` — PASS, no ticket replay on main

## 3P*

1. Preserve — PASS.
2. Parse / Normalize — PASS.
3. Propagate — PASS.
4. Prove — PASS.
5. Prune / Rank — PASS.

The ranked next first-red is limited to QPLANT responder-runtime hardening: suppress main replay, retain fresh-main self-test, force-add only governed receipt paths, and fail closed when no receipt is staged.

No v1.3 fan-out is authorized by this receipt.
