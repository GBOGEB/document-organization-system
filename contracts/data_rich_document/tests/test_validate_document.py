import copy
import json
import unittest
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "validate_document.py"
EXAMPLE = ROOT / "examples" / "adr-001.json"

spec = importlib.util.spec_from_file_location("validate_document", VALIDATOR)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class DataRichDocumentValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.example = json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def validate(self, data):
        return module.validate_document(data)

    def test_example_is_valid(self):
        self.assertEqual(self.validate(copy.deepcopy(self.example)), [])

    def test_rejects_duplicate_id(self):
        data = copy.deepcopy(self.example)
        data["requirements"][0]["id"] = "SEC-001"
        errors = self.validate(data)
        self.assertTrue(any("duplicate id" in e for e in errors), errors)

    def test_rejects_outline_parent_drift(self):
        data = copy.deepcopy(self.example)
        # Move SEC-211 in the outline without changing canonical placement.
        sec_210 = data["outline"][1]["children"][0]
        moved = sec_210["children"].pop()
        data["outline"][1]["children"].append(moved)
        errors = self.validate(data)
        self.assertTrue(any("outline parent" in e for e in errors), errors)

    def test_rejects_sibling_rank_collision(self):
        data = copy.deepcopy(self.example)
        data["sections"][2]["placement"]["rank"] = 1000
        errors = self.validate(data)
        self.assertTrue(any("sibling rank collision" in e for e in errors), errors)

    def test_rejects_unresolved_relation_endpoint(self):
        data = copy.deepcopy(self.example)
        data["relations"][0]["to"] = "REQ-DOES-NOT-EXIST"
        errors = self.validate(data)
        self.assertTrue(any("unresolved to endpoint" in e for e in errors), errors)

    def test_rejects_unknown_requirement_section(self):
        data = copy.deepcopy(self.example)
        data["requirements"][0]["section_ids"].append("SEC-MISSING")
        errors = self.validate(data)
        self.assertTrue(any("unknown section_id reference" in e for e in errors), errors)

    def test_rejects_applied_change_without_history_receipt(self):
        data = copy.deepcopy(self.example)
        data["history"][0]["change_set_ids"] = []
        errors = self.validate(data)
        self.assertTrue(any("no history event references it" in e for e in errors), errors)

    def test_rejects_current_version_missing_from_history(self):
        data = copy.deepcopy(self.example)
        data["document"]["version"] = "1.1.0"
        errors = self.validate(data)
        self.assertTrue(any("absent from history" in e for e in errors), errors)


if __name__ == "__main__":
    unittest.main()
