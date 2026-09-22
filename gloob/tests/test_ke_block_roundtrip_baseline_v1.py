import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE = ROOT / "baselines" / "ke-block-roundtrip"
V1 = BASE / "v1"

class TestKEBlockRoundTripBaselineV1(unittest.TestCase):
    def test_current_points_to_v1(self):
        current = json.loads((BASE / "CURRENT.json").read_text(encoding="utf-8"))
        self.assertEqual(current["baseline_id"], "KE_BLOCK_ROUNDTRIP_BASELINE_V1")
        self.assertEqual(current["state"], "CONTROLLED")

    def test_promotion_is_explicit_and_source_authority_unchanged(self):
        receipt = json.loads((V1 / "BASELINE_PROMOTION_RECEIPT.json").read_text(encoding="utf-8"))
        self.assertTrue(receipt["proof"]["user_approval"])
        self.assertEqual(receipt["promotion"]["result"], "PASS_PROMOTED")
        self.assertEqual(receipt["source_authority"]["status"], "UNCHANGED_SOURCE_AUTHORITY")
        self.assertTrue(receipt["non_compensation"]["baseline_ne_source_master"])

    def test_hashes_are_pinned(self):
        manifest = json.loads((V1 / "BASELINE_MANIFEST.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["binary_hashes"]["KE_BLOCK_Roundtrip_Report_Baseline_v1.docx"], "27b37fd807234a24048dfee479dfad50c6293ff19d2a36913183f135f8ac9d2c")
        self.assertEqual(manifest["binary_hashes"]["KE_BLOCK_Roundtrip_KPI_Baseline_v1.xlsx"], "8cd51d1ac89fe21d39a1281a414659a92f5a93afcc812a30be86d29450502312")
        self.assertEqual(manifest["binary_hashes"]["KE_BLOCK_Roundtrip_Deck_Baseline_v1.pptx"], "bac54897883d55f8d1b9df0ef7628583204697eff89fa8c6eed9568a268298e9")
        self.assertEqual(manifest["binary_hashes"]["KE_BLOCK_Roundtrip_Baseline_v1.zip"], "179f130e442640025b67eae1d8f21cf18a92e24e47721458d4efd9506bf3afc9")

if __name__ == "__main__":
    unittest.main()
