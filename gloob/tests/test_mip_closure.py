import hashlib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MIP = ROOT / "mip" / "2026-09-12-session-close"


class GloobMipClosureTests(unittest.TestCase):
    def test_manifest_covers_and_verifies_closure_payload(self):
        manifest = MIP / "MIP_MANIFEST.sha256"
        self.assertTrue(manifest.exists())

        records = []
        for line in manifest.read_text().splitlines():
            digest, name = line.split("  ", 1)
            records.append((digest, name))

        self.assertEqual(len(records), 11)
        self.assertEqual(len({name for _, name in records}), 11)

        for expected, name in records:
            path = MIP / name
            self.assertTrue(path.is_file(), name)
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(actual, expected, name)

    def test_resume_prompt_is_standalone_and_points_to_control_baseline(self):
        prompt = (MIP / "09_RESUME_PROMPT.md").read_text()
        self.assertIn("913f577ae63ef53da71633fad2bbbeb1c646c58a", prompt)
        self.assertIn("Book Registry v0.2", prompt)
        self.assertIn("Do not redesign controlled Book v0.1 semantics", prompt)

    def test_delete_safe_gate_is_runtime_conditional(self):
        status = (MIP / "10_3P5_STATUS.yaml").read_text()
        self.assertIn("unclassified_todos: 0", status)
        self.assertIn("unclassified_opportunities: 0", status)
        self.assertIn("PASS_IF_MANIFEST_TEST_GREEN", status)
        self.assertIn("DELETE_SAFE_IF_MIP_PR_HEAD_GREEN", status)


if __name__ == "__main__":
    unittest.main()
