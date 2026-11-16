/**
 * master_transmittal.zod.ts — Zod mirror of transmittal.schema.json.
 *
 * Convention (same as cryo_dashboard .../contracts/ssot.zod.ts): the
 * authoritative, dependency-free contract is transmittal.schema.json plus
 * validate_transmittal.py (Python stdlib). This mirror exists for parity with
 * the triad's TypeScript tooling and is validated only in projects that
 * already depend on `zod`. tests/test_validate_transmittal.py checks that the
 * field names and patterns here stay in step with the JSON Schema.
 */
import { z } from "zod";

export const PREFIX_PATTERN = /^\[AD_\d{2}\]$/;
export const FUNCTIONAL_NAME_PATTERN = /^AD_\d{2}_[A-Z][A-Za-z0-9]*(_[A-Za-z0-9]+)*$/;
export const ALX_PATTERN = /^\d{8}$/;
export const DATE_PATTERN = /^\d{4}-\d{2}-\d{2}$/;
export const VERSION_PATTERN = /^v\d{2}$/;

const PLACEHOLDERS = ["TBD", "tbd", "N/A", "-", "?"];

export const TransmittalRow = z
  .object({
    Prefix: z.string().regex(PREFIX_PATTERN),
    Functional_Name: z.string().regex(FUNCTIONAL_NAME_PATTERN),
    MIN: z
      .string()
      .min(1)
      .refine((v) => !PLACEHOLDERS.includes(v.trim()), "placeholder MIN not allowed; use null")
      .nullable(),
    ALX_ID: z.string().regex(ALX_PATTERN).nullable(),
    Date: z.string().regex(DATE_PATTERN).nullable(),
    Version: z.string().regex(VERSION_PATTERN),
    Approved_PDF_Flag: z.boolean(),
    Note: z.string().optional(),
  })
  .strict()
  .refine(
    (r) => !r.Approved_PDF_Flag || (r.MIN !== null && r.ALX_ID !== null && r.Date !== null),
    "Approved_PDF_Flag=true requires MIN, ALX_ID and Date",
  );

export const MasterTransmittal = z
  .object({
    schema_version: z.string().regex(/^\d+\.\d+\.\d+$/),
    alx_folder: z.string().regex(ALX_PATTERN),
    registry: z.record(z.string().regex(PREFIX_PATTERN), z.string().regex(FUNCTIONAL_NAME_PATTERN)),
    rows: z.array(TransmittalRow).min(1),
  })
  .strict()
  .superRefine((t, ctx) => {
    t.rows.forEach((row, i) => {
      const locked = t.registry[row.Prefix];
      if (locked === undefined || locked !== row.Functional_Name) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          path: ["rows", i, "Functional_Name"],
          message: `must equal locked registry name ${locked ?? "(prefix not registered)"}`,
        });
      }
    });
  });

export type TransmittalRowT = z.infer<typeof TransmittalRow>;
export type MasterTransmittalT = z.infer<typeof MasterTransmittal>;
