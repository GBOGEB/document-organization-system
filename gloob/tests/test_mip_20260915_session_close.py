import hashlib, json, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "mip" / "2026-09-15-session-close"


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


class Mip20260915SessionCloseTests(unittest.TestCase):
    def test_manifest_is_lossless_for_declared_handover_files(self):
        manifest = json.loads((PKG / "MIP_MANIFEST.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["schema"], "gloob.mip.integrity_manifest.v1.1")
        self.assertTrue(manifest["manifest_excludes_itself"])
        self.assertGreaterEqual(len(manifest["files"]), 13)
        for item in manifest["files"]:
            path = PKG / item["path"]
            self.assertTrue(path.is_file(), item["path"])
            raw = path.read_bytes()
            self.assertEqual(len(raw), item["size"], item["path"])
            self.assertEqual(git_blob_sha(raw), item["blob"], item["path"])

    def test_restart_and_frontier_are_explicit(self):
        resume = (PKG / "09_RESUME_PROMPT.md").read_text(encoding="utf-8")
        backlog = (PKG / "05_BACKLOG_AND_FIRST_RED.yaml").read_text(encoding="utf-8")
        mip = (PKG / "11_MIP_STATUS.yaml").read_text(encoding="utf-8")
        self.assertIn("c831758a247d928220e4b85efc13e3e74ba7da51", resume)
        self.assertIn("v1.2", resume)
        self.assertIn("V1.2_OUTBOUND_ACTUATION", backlog)
        self.assertIn("Modernize", mip)
        self.assertIn("Innovate", mip)
        self.assertIn("Perpetuate", mip)


if __name__ == "__main__":
    unittest.main()
