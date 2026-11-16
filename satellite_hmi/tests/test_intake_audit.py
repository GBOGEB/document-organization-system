"""Adversarial tests for external handover intake; no private Drive sources."""
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from intake_audit import audit, public_projection, safe_relative, verify_inventory


def synthetic():
    tranches = {f"Tranche_{x}": {"rows": 2, "unique": 2, "safe_to_delete": 1, "hold_or_keep": 1} for x in "ABCDEFGH"}
    tranches.update(total_sidebar_rows_inspected=16, unique_chats=16, safe_to_delete=8, keep_or_verify=8)
    return {"tranche_counts": tranches}


class IntakeTests(unittest.TestCase):
    def test_clean_count_not_lossless_or_approved(self):
        r = audit(synthetic(), inventory_issues=[])
        self.assertEqual(r["status"], "HOLD_SOURCE_PROOF")
        self.assertFalse(r["delete_authorized"])
        self.assertEqual(r["eligible_deletions"], 0)

    def test_tranche_disagreement_fail_closed(self):
        m = synthetic()
        m["tranche_counts"]["unique_chats"] = 14
        r = audit(m, inventory_issues=[])
        self.assertIn("TOTAL_CONFLICT:unique", r["issues"])
        self.assertEqual(r["status"], "HOLD_SOURCE_ACCOUNTING")

    def test_row_mismatch(self):
        m = synthetic()
        m["tranche_counts"]["Tranche_A"]["safe_to_delete"] = 2
        r = audit(m)
        self.assertIn("ROW_CONFLICT:Tranche_A", r["issues"])

    def test_yaml_mismatch(self):
        r = audit(synthetic(), "tranche_audit_summary:\n  total_sidebar_rows_inspected: 15\n", [])
        self.assertIn("YAML_CONFLICT:rows", r["issues"])
        self.assertIn("YAML_MISSING_OR_AMBIGUOUS:unique_chats_audited", r["issues"])

    def test_duplicate_yaml_scalar(self):
        s = "  unique_chats_audited: 16\n  unique_chats_audited: 16\n"
        r = audit(synthetic(), s, [])
        self.assertIn("YAML_MISSING_OR_AMBIGUOUS:unique_chats_audited", r["issues"])

    def test_bad_count_or_missing_tranche(self):
        m = synthetic()
        m["tranche_counts"]["Tranche_C"]["rows"] = True
        with self.assertRaises(ValueError): audit(m)
        del m["tranche_counts"]["Tranche_C"]
        with self.assertRaises(ValueError): audit(m)

    def test_inventory_positive_and_tamper(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "source.txt").write_text("source", encoding="utf-8")
            digest = hashlib.sha256(b"source").hexdigest()
            self.assertEqual(verify_inventory({"source.txt": digest}, root), [])
            self.assertEqual(verify_inventory({"source.txt": "0" * 64}, root), ["SHA_MISMATCH:source.txt"])

    def test_path_traversal_and_symlink(self):
        for p in ("../other", "/etc/passwd", "folder\\wrong", "C:drive", "a//b", "a/./b"):
            with self.subTest(p=p), self.assertRaises(ValueError): safe_relative(p)
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "real").write_text("ok")
            (root / "link").symlink_to(root / "real")
            with self.assertRaisesRegex(ValueError, "Symlink"):
                verify_inventory({"link": "0" * 64}, root)

    def test_inventory_reject_bad_hash(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError, "SHA-256"):
                verify_inventory({"a": "not a digest"}, Path(td))

    def test_projection_public_only(self):
        projection = public_projection(audit(synthetic()), "2026-11-16")
        self.assertEqual(projection["schema_version"], "satellite-hmi/1")
        self.assertNotIn("source_private", str(projection))
        self.assertEqual(len(projection["entries"]), 4)
        self.assertTrue(all("drive.google.com" not in str(x) for x in projection["entries"]))


if __name__ == "__main__":
    unittest.main()