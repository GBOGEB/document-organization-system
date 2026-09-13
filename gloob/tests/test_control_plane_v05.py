import json, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
import telemetry, pca_priority, glob_runtime

class ControlPlaneV05Tests(unittest.TestCase):
    def test_capability_contract_is_fail_closed(self):
        c=json.loads((ROOT/"glob"/"capabilities.json").read_text(encoding="utf-8"))
        self.assertEqual(c["glob"]["default_act_mode"],"PLAN_ONLY")
        self.assertTrue(all(x["read_only"] for x in c["ask"]))
        self.assertTrue(all(not x["mutates"] for x in c["act"]))

    def test_telemetry_is_measured_and_covers_entity_classes(self):
        s=telemetry.snapshot(); self.assertFalse(s["expert_seeded_scores"])
        kinds={r["entity_type"] for r in s["rows"]}
        self.assertTrue({"BOOK","ENTRY","ATOM","SHARED_ATOM","EDGE_TYPE","OPERATOR"}.issubset(kinds))
        self.assertEqual(len([r for r in s["rows"] if r["entity_type"]=="ENTRY"]),3)

    def test_pca_has_pc1_pc2_and_measured_ranking(self):
        r=pca_priority.report()
        self.assertEqual(r["basis"],"MEASURED_REPOSITORY_TELEMETRY")
        self.assertEqual([c["name"] for c in r["components"][:2]],["PC1","PC2"])
        self.assertEqual(set(r["components"][0]["loadings"]),set(telemetry.FEATURES))
        self.assertTrue(all(0 <= x["priority"] <= 100 for x in r["ranking"]))
        self.assertEqual(r["ranking"],sorted(r["ranking"],key=lambda x:(-x["priority"],x["entity_type"],x["entity_id"])))

    def test_shared_and_local_rebuild_blast_radius(self):
        shared=glob_runtime.plan_rebuild(["ATOM-GLOOB-FEDERATED-AUTHORITY"])
        self.assertEqual(set(shared["affected_entries"]),{"ENTRY-LKT-INVCOP","ENTRY-GLOOB-BOOK-CONTRACT","ENTRY-GLOOB-SESSION-CONTROL"})
        local=glob_runtime.plan_rebuild(["ATOM-LKT-INVCOP"])
        self.assertEqual(local["affected_entries"],["ENTRY-LKT-INVCOP"])
        self.assertEqual(shared["mode"],"PLAN_ONLY")

    def test_worker_plan_uses_priority_and_measured_cost(self):
        p=glob_runtime.plan_workers(2,["ATOM-GLOOB-FEDERATED-AUTHORITY"])
        self.assertEqual(p["mode"],"PLAN_ONLY"); self.assertEqual(p["capacity"],2)
        self.assertEqual(len(p["assignments"]),3)
        self.assertEqual({a["lane"] for a in p["assignments"]}.issubset({"FAST","HEAVY"}),True)
        self.assertEqual({a["entry_id"] for a in p["assignments"]},set(glob_runtime.plan_rebuild(["ATOM-GLOOB-FEDERATED-AUTHORITY"])["affected_entries"]))

    def test_ask_runtime_reaches_current_control_chain(self):
        out=glob_runtime.ask_runtime("ENTRY-LKT-INVCOP")
        versions={e["version"] for e in out["proofs"]+out["promotions"]}
        self.assertIn("Synchronized Views v0.4",versions)
        self.assertTrue(all(len(e["sha"])==40 and e["run_id"]>0 for e in out["proofs"]+out["promotions"]))

    def test_provenance_expands_monotonically(self):
        a=glob_runtime.ask_provenance("ENTRY-LKT-INVCOP","summary")
        b=glob_runtime.ask_provenance("ENTRY-LKT-INVCOP","evidence")
        c=glob_runtime.ask_provenance("ENTRY-LKT-INVCOP","runtime")
        self.assertEqual(a["target"],b["target"]); self.assertEqual(b["target"],c["target"])
        self.assertIn("runtime",c); self.assertNotIn("runtime",a)

if __name__=="__main__": unittest.main()
