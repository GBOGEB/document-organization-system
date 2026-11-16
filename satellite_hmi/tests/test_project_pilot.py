"""Five-domain, one-source-selected ChatGPT Project cohort tests."""
import copy
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from project_pilot import assess, public_hmi, read_cohort

FIXTURE = Path(__file__).resolve().parents[1] / "pilots" / "PROJECT_5_COHORT_20261116.json"

class ProjectPilotTests(unittest.TestCase):
    def setUp(self):
        self.c = read_cohort(FIXTURE)

    def test_inception_one_selected_four_reserved(self):
        receipt = assess(self.c)
        self.assertEqual((receipt["pilot_count"],receipt["selected_count"],receipt["source_admitted"]),(5,1,0))
        self.assertEqual(receipt["results"][0]["state"],"SOURCE_SELECTED")
        self.assertFalse(receipt["merge_authorized"])
        self.assertFalse(receipt["delete_authorized"])

    def test_reject_missing_duplicate_or_extra_slots(self):
        for replacement in (self.c["projects"][:-1], self.c["projects"]+[self.c["projects"][0]], [self.c["projects"][0]]*5):
            x=copy.deepcopy(self.c);x["projects"]=replacement
            with self.assertRaises(ValueError):assess(x)

    def test_reject_unknown_repo(self):
        c=copy.deepcopy(self.c);c["projects"][0]["target_repo"]="GBOGEB/imaginary-repo"
        with self.assertRaises(ValueError):assess(c)

    def test_reject_auto_merge_delete_or_transfer(self):
        for k in ("auto_merge","auto_delete","authority_transfer"):
            c=copy.deepcopy(self.c);c[k]=True
            with self.assertRaises(ValueError):assess(c)

    def test_reject_fabricated_project_id_and_digest(self):
        c=copy.deepcopy(self.c);c["projects"][0]["source_id_verified"]=True
        with self.assertRaises(ValueError):assess(c)
        c=copy.deepcopy(self.c);c["projects"][0]["source_hashes"]=["hello"]
        with self.assertRaises(ValueError):assess(c)

    def test_hash_only_not_lossless_evidence(self):
        c=copy.deepcopy(self.c);c["projects"][0]["source_hashes"]=["f"*64];c["projects"][0]["capture_kind"]="HANDOVER_ONLY"
        receipt=assess(c)
        self.assertEqual(receipt["source_admitted"],0)
        self.assertEqual(receipt["results"][0]["source_status"],"SOURCE_PROOF_HOLD")

    def test_projection_is_generic_and_private_safe(self):
        manifest=public_hmi(assess(self.c))
        self.assertEqual(len(manifest["entries"]),5)
        s=json.dumps(manifest)
        self.assertNotIn("original_project_id",s)
        self.assertNotIn("drive.google.com",s)
        self.assertNotIn("USER_SCREENSHOT",s)

    def test_reserved_cannot_claim_source_evidence(self):
        c=copy.deepcopy(self.c);c["projects"][1]["original_project_id"]="fabricated"
        with self.assertRaises(ValueError):assess(c)

if __name__=="__main__": unittest.main()