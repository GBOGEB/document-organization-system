/**
 * ssot.zod.ts — Zod contract mirror for the Cryogenic Material Dashboard SSOT.
 *
 * Convention alignment:
 *   This file mirrors the `.zod.ts` contract convention used across the GBOGEB
 *   triad (e.g. CODEX federation/mip/W110_CANONICAL_SSOT_REGISTRY.zod.ts and
 *   cryoplant-project ocd-adr/contracts/*.zod.ts). The authoritative, runtime,
 *   dependency-free contract for this repo is contracts/ssot.schema.json
 *   (JSON Schema draft-07) which is enforced by tests/ssot_contract.test.js
 *   using only Node built-ins. This Zod mirror is provided for parity with the
 *   triad's TypeScript tooling and is validated only in projects that already
 *   depend on `zod` (install with: npm i -D zod).
 */
import { z } from "zod";

export const SsotMeta = z.object({
  schema_version: z.string().regex(/^\d+\.\d+\.\d+$/),
  dashboard_version: z.string().regex(/^v\d+\.\d+\.\d+$/),
  generated: z.string().datetime().optional(),
  canonical_source: z.string().regex(/^GBOGEB\//),
  subtree: z.string().min(1),
  idempotency_key: z.string().min(1).optional(),
  description: z.string().optional(),
}).passthrough();

export const Materials = z.object({
  count: z.number().int().positive(),
  catalog: z.array(z.unknown()).min(1),
}).passthrough();

export const CryoDashboardSsot = z.object({
  ssot_meta: SsotMeta,
  project: z.unknown(),
  architecture: z.object({ primary_runtime: z.string().min(1) }).passthrough(),
  materials: Materials,
  validation: z.record(z.string(), z.unknown()),
}).passthrough();

export type CryoDashboardSsotPayload = z.infer<typeof CryoDashboardSsot>;
