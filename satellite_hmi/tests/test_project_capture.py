"""Source capture adversarial tests."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from project_capture import receipt_for_file, main, MAX_BYTES

class ProjectCaptureTests(unittest.TestCase):
    def test_hash_selected_file_but_not_full_chat(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"private-content.txt";p.write_bytes(b"original selection")
            r=receipt_for_file(p,"P1","HANDOVER_ONLY")
            self.assertEqual(r["sha256_actual_bytes"],"67236815880eae3c28528a2814c17396a4b55ceb4f2cf9fee3c0908451a7bedc")
            self.assertEqual(r["original_chat_byte_completeness"],"UNKNOWN")
            self.assertNotIn("private-content",json.dumps(r))

    def test_alias_and_kind_validation(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"a";p.write_text("A")
            for alias,kind in (("X1","SOURCE_FILE"),("P1","UNKNOWN")):
                with self.assertRaises(ValueError): receipt_for_file(p,alias,kind)

    def test_reject_missing(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,"existing regular file"):
                receipt_for_file(Path(d)/"missing","P1","HANDOVER_ONLY")

    def test_reject_symlink(self):
        with tempfile.TemporaryDirectory() as d:
            base=Path(d);p=base/"origin";p.write_text("bytes")
            s=base/"link";s.symlink_to(p)
            with self.assertRaisesRegex(ValueError,"Symlink"):
                receipt_for_file(s,"P1","SOURCE_FILE")

    def test_reject_overlarge(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"huge"
            with p.open("wb") as stream:stream.truncate(MAX_BYTES+1)
            with self.assertRaisesRegex(ValueError,"too large"):
                receipt_for_file(p,"P1","SOURCE_FILE")

if __name__=="__main__":unittest.main()