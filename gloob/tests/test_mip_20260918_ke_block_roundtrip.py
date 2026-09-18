import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
PACK = ROOT / "mip" / "2026-09-18-ke-block-roundtrip"

class TestKEBlockRoundTripControl(unittest.TestCase):
    def test_required_control_files_exist(self):
        for name in [
            "00_3PSTAR_MIP_EXECUTIVE.md",
            "01_3PSTAR_MIP_CONTROL.yaml",
            "02_cd.yml",
            "03_artefact_index.json",
            "04_ASCII_workflows.txt",
            "05_ranking_index.json",
        ]:
            self.assertTrue((PACK / name).exists(), name)

    def test_candidate_is_not_silently_promoted(self):
        control = (PACK / "01_3PSTAR_MIP_CONTROL.yaml").read_text(encoding="utf-8")
        self.assertIn("WITHHELD_PENDING_OFFICE_BINARY_BUILD_AND_RENDER_QA", control)
        self.assertIn("candidate_ne_baseline: true", control)
        self.assertIn("generated_ne_source_authoritative: true", control)

    def test_index_and_rank_first_red_agree(self):
        index = json.loads((PACK / "03_artefact_index.json").read_text(encoding="utf-8"))
        ranking = json.loads((PACK / "05_ranking_index.json").read_text(encoding="utf-8"))
        self.assertEqual(index["promotion_state"], "WITHHELD_PENDING_OFFICE_BINARY_BUILD_AND_RENDER_QA")
        self.assertEqual(ranking["ranked"][0]["id"], "OFFICE_BINARY_BUILD_AND_RENDER_QA")

    def test_cd_requires_user_approval_and_visual_qa(self):
        cd = (PACK / "02_cd.yml").read_text(encoding="utf-8")
        self.assertIn("OFFICE_BINARY_RENDER_QA_PASS", cd)
        self.assertIn("USER_APPROVAL", cd)

if __name__ == "__main__":
    unittest.main()
