"""Fail-closed tests for the Master Document Transmittal contract."""

from __future__ import annotations

import copy
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONTRACT = HERE.parent
sys.path.insert(0, str(CONTRACT))

from validate_transmittal import (  # noqa: E402
    check_filename,
    contractor_filename,
    validate_transmittal,
)

EXAMPLE = CONTRACT / "examples" / "transmittal_current.json"
SCHEMA = CONTRACT / "transmittal.schema.json"
ZOD = CONTRACT / "master_transmittal.zod.ts"


def load() -> dict:
    return json.loads(EXAMPLE.read_text(encoding="utf-8"))


def complete(data: dict) -> dict:
    d = copy.deepcopy(data)
    for i, row in enumerate(d["rows"]):
        row["MIN"] = f"MIN-{i:04d}"
        row["ALX_ID"] = f"{98684416 + i:08d}"
        row["Date"] = "2026-11-15"
    return d


class ExampleTests(unittest.TestCase):
    def test_example_is_valid_and_gate5_blocked(self):
        errors, gate5 = validate_transmittal(load())
        self.assertEqual(errors, [])
        self.assertEqual(gate5["status"], "BLOCKED_INPUT")
        self.assertEqual({g["prefix"] for g in gate5["missing"]}, {"[AD_03]", "[AD_06]", "[AD_11]", "[AD_13]"})

    def test_gate5_complete_when_all_values_present(self):
        errors, gate5 = validate_transmittal(complete(load()))
        self.assertEqual(errors, [])
        self.assertEqual(gate5["status"], "COMPLETE")


class InvariantTests(unittest.TestCase):
    def assertFails(self, data, fragment):
        errors, _ = validate_transmittal(data)
        self.assertTrue(any(fragment in e for e in errors), f"expected {fragment!r} in {errors}")

    def test_name_reversion_blocked(self):
        d = load()
        d["rows"][3]["Functional_Name"] = "AD_13_Author_Named_Catalogue"
        self.assertFails(d, "does not match locked name")

    def test_free_text_name_rejected_by_shape(self):
        d = load()
        d["rows"][3]["Functional_Name"] = "Some Person 13"
        self.assertFails(d, "is not AD_##_Name")

    def test_placeholder_min_rejected(self):
        d = load()
        d["rows"][0]["MIN"] = "TBD"
        self.assertFails(d, "placeholders")

    def test_bad_alx_rejected(self):
        d = load()
        d["rows"][0]["ALX_ID"] = "1234"
        self.assertFails(d, "8-digit")

    def test_approved_without_authority_rejected(self):
        d = load()
        d["rows"][0]["Approved_PDF_Flag"] = True
        self.assertFails(d, "Approved_PDF_Flag=true but missing")

    def test_duplicate_version_rejected(self):
        d = load()
        d["rows"].append(copy.deepcopy(d["rows"][0]))
        self.assertFails(d, "duplicate")

    def test_latest_alx_and_date_prevails(self):
        d = complete(load())
        newer = copy.deepcopy(d["rows"][0])
        newer["Version"] = "v02"
        newer["Date"] = "2026-10-01"  # older than v01 -> must fail
        d["rows"].append(newer)
        self.assertFails(d, "latest ALX + date must prevail")

    def test_unregistered_prefix_rejected(self):
        d = load()
        d["rows"][0]["Prefix"] = "[AD_99]"
        d["rows"][0]["Functional_Name"] = "AD_99_Unknown"
        self.assertFails(d, "prefix not in registry")

    def test_unknown_field_rejected(self):
        d = load()
        d["rows"][0]["Author"] = "someone"
        self.assertFails(d, "unexpected field")


class FilenameTests(unittest.TestCase):
    def setUp(self):
        self.registry = load()["registry"]

    def test_expected_name_passes(self):
        row = load()["rows"][3]
        name = contractor_filename(row)
        self.assertEqual(name, "[AD_13]_AD_13_MCS_Secondary_Interface_Catalogue_v01.pdf")
        self.assertIsNone(check_filename(name, self.registry))

    def test_author_style_name_fails(self):
        self.assertIsNotNone(check_filename("Surname Firstname 13.pdf", self.registry))

    def test_prefix_number_mismatch_fails(self):
        self.assertIsNotNone(
            check_filename("[AD_13]_AD_11_MCS_Primary_Interface_Catalogue_v01.pdf", self.registry)
        )


class CliTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, str(CONTRACT / "validate_transmittal.py"), str(EXAMPLE), *args],
            capture_output=True,
            text=True,
        )

    def test_cli_valid_exit0(self):
        self.assertEqual(self.run_cli().returncode, 0)

    def test_cli_require_gate5_exit2(self):
        self.assertEqual(self.run_cli("--require-gate5").returncode, 2)


class ZodParityTests(unittest.TestCase):
    """Keep the Zod mirror in step with the JSON Schema without needing node/zod."""

    def test_fields_and_patterns_match(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        zod = ZOD.read_text(encoding="utf-8")
        row = schema["definitions"]["row"]
        for field in row["properties"]:
            self.assertRegex(zod, rf"\b{re.escape(field)}:", f"Zod mirror missing field {field}")
        pairs = {
            "PREFIX_PATTERN": row["properties"]["Prefix"]["pattern"],
            "FUNCTIONAL_NAME_PATTERN": row["properties"]["Functional_Name"]["pattern"],
            "ALX_PATTERN": row["properties"]["ALX_ID"]["pattern"],
            "DATE_PATTERN": row["properties"]["Date"]["pattern"],
            "VERSION_PATTERN": row["properties"]["Version"]["pattern"],
        }
        for const, pattern in pairs.items():
            m = re.search(rf"export const {const} = /(.+)/;", zod)
            self.assertIsNotNone(m, f"{const} not found in Zod mirror")
            self.assertEqual(m.group(1), pattern, f"{const} differs from JSON Schema")


if __name__ == "__main__":
    unittest.main()
