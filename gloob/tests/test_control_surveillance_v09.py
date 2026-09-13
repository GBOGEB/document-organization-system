import copy, json, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
import telemetry, control_surveillance

class ControlSurveillanceV09Tests(unittest.TestCase):
    def setUp(self):
        self.policy=json.loads((ROOT/"control"/"surveillance-policy.json").read_text(encoding="utf-8"))
        self.base=telemetry.snapshot()

    def snap(self,sha,telemetry_snapshot=None):
        return {"receipt":{"source_commit":sha,"run_id":sha[-6:]},"telemetry":copy.deepcopy(telemetry_snapshot or self.base)}

    def changed(self):
        out=copy.deepcopy(self.base)
        target=next(r for r in out["rows"] if r["entity_id"]=="ENTRY-LKT-INVCOP")
        target["source_count"]=0
        return out

    def test_unchanged_qualifying_epoch_stays_control_without_work(self):
        history={"snapshots":[self.snap(str(i).zfill(40)) for i in range(1,4)]}
        out=control_surveillance.surveil(history,self.policy)
        target=next(e for e in out["entities"] if e["entity_id"]=="ENTRY-LKT-INVCOP")
        self.assertEqual(target["surveillance_state"],"STABLE_CONTROL")
        self.assertFalse(target["reopen_work"])

    def test_real_change_requalifies_before_reopening_work(self):
        history={"snapshots":[self.snap(str(i).zfill(40)) for i in range(1,4)] + [self.snap("4".zfill(40),self.changed())]}
        out=control_surveillance.surveil(history,self.policy)
        target=next(e for e in out["entities"] if e["entity_id"]=="ENTRY-LKT-INVCOP")
        self.assertEqual(target["surveillance_state"],"REQUALIFY")
        self.assertEqual(target["telemetry_epoch_snapshots"],1)
        self.assertFalse(target["reopen_work"])

    def test_failed_changed_epoch_requires_causal_attribution_before_work(self):
        changed=self.changed()
        history={"snapshots":[self.snap(str(i).zfill(40)) for i in range(1,4)] + [self.snap(str(i).zfill(40),changed) for i in range(4,7)]}
        out=control_surveillance.surveil(history,self.policy)
        target=next(e for e in out["entities"] if e["entity_id"]=="ENTRY-LKT-INVCOP")
        self.assertEqual(target["surveillance_state"],"ESCALATE")
        self.assertTrue(target["statistical_escalation"])
        self.assertFalse(target["reopen_work"])
        self.assertEqual(target["routing_gate"],"CAUSAL_ATTRIBUTION_REQUIRED")
        self.assertGreater(target["residual_pc2_plus"],self.policy["qualification"]["pc2_plus_residual_ceiling"])
        discoveries=[d for d in out["discoveries"] if d["entity_id"]=="ENTRY-LKT-INVCOP"]
        self.assertIn("PC4",{d["component"] for d in discoveries})
        plan=control_surveillance.escalation_plan(out,2)
        self.assertEqual(plan["assignments"],[])
        self.assertIn("ENTRY-LKT-INVCOP",plan["pending_causal_attribution"])

    def test_prior_stable_control_is_carried_across_sliding_window_when_telemetry_is_unchanged(self):
        snaps=[self.snap(str(i).zfill(40)) for i in range(1,4)]
        eid="ENTRY-GLOOB-BOOK-CONTRACT"
        snaps[0]["surveillance"]={"entities":[{"entity_id":eid,"surveillance_state":"STABLE_CONTROL","control_established_in_epoch":True}]}
        out=control_surveillance.surveil({"snapshots":snaps},self.policy)
        target=next(e for e in out["entities"] if e["entity_id"]==eid)
        self.assertGreater(target["residual_pc2_plus"],self.policy["qualification"]["pc2_plus_residual_ceiling"])
        self.assertEqual(target["surveillance_state"],"STABLE_CONTROL")
        self.assertTrue(target["control_carried_forward"])

if __name__=="__main__": unittest.main()
