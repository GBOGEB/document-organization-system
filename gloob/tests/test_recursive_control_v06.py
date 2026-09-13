import sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
import telemetry, pca_priority, recursive_control

class RecursiveControlV06Tests(unittest.TestCase):
    def history(self,n=3):
        snap=telemetry.snapshot()
        return {"schema":"gloob-federated-control-history/0.1","snapshots":[{"receipt":{"source_commit":str(i).zfill(40),"run_id":str(100+i)},"telemetry":snap} for i in range(n)]}

    def test_pca_exposes_residual_components(self):
        r=pca_priority.report()
        self.assertEqual([c["name"] for c in r["components"]],["PC1","PC2","PC3","PC4"])
        self.assertGreater(sum(c["explained_variance_ratio"] for c in r["components"][1:]),0)

    def test_three_snapshots_required_for_control(self):
        out=recursive_control.analyze(self.history(2))
        self.assertEqual(out["state"],"INSUFFICIENT_HISTORY"); self.assertEqual(out["required"],3)

    def test_flat_pc1_plateau_promotes_only_bounded_residuals(self):
        out=recursive_control.analyze(self.history(3)); self.assertEqual(out["state"],"CLASSIFIED")
        self.assertTrue(all(x["pc1_saturated"] for x in out["entities"]))
        for x in out["entities"]:
            expected="CONTROL" if x["residual_pc2_plus"]<=out["residual_ceiling"] else "IMPROVE"
            self.assertEqual(x["state"],expected)

    def test_residual_workers_only_receive_improve_entities(self):
        control=recursive_control.analyze(self.history(3)); plan=recursive_control.residual_worker_plan(control,2)
        improve={x["entity_id"] for x in control["entities"] if x["state"]=="IMPROVE"}; assigned={x["entity_id"] for x in plan["assignments"]}
        self.assertEqual(plan["mode"],"PLAN_ONLY"); self.assertEqual(assigned,improve)
        self.assertTrue(all(x["focus"]=="PC2_PLUS_RESIDUAL" for x in plan["assignments"]))

if __name__=="__main__": unittest.main()
