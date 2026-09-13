import copy, json, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
import causal_routing, control_surveillance, telemetry

class CausalRoutingV10Tests(unittest.TestCase):
    def setUp(self):
        self.policy=json.loads((ROOT/"control"/"surveillance-policy.json").read_text(encoding="utf-8"))
        self.routes=json.loads((ROOT/"control"/"causal-route-registry.json").read_text(encoding="utf-8"))
        self.base_t=telemetry.snapshot()
        self.base_c=causal_routing.causal_snapshot()

    def snap(self,n,t=None,c=None):
        return {"receipt":{"source_commit":str(n).zfill(40),"run_id":str(n)},"telemetry":copy.deepcopy(t or self.base_t),"causal":copy.deepcopy(c or self.base_c)}

    def changed_pair(self):
        t=copy.deepcopy(self.base_t)
        row=next(r for r in t["rows"] if r["entity_id"]=="ENTRY-LKT-INVCOP")
        row["source_count"]=0
        c=copy.deepcopy(self.base_c)
        e=c["entities"]["ENTRY-LKT-INVCOP"]
        e["causes"]["SOURCE"]["items"]=[]
        c["entities"]["ENTRY-LKT-INVCOP"]=causal_routing.recompute_entity(e)
        return t,c

    def test_snapshot_binds_entry_to_source_book_and_repo(self):
        e=self.base_c["entities"]["ENTRY-LKT-INVCOP"]
        self.assertEqual(e["books"],["BOOK-QPLANT"])
        repos={x.get("repo") for x in e["causes"]["SOURCE"]["items"]}
        self.assertIn("GBOGEB/cryoplant-project",repos)

    def test_no_change_is_silent(self):
        history={"snapshots":[self.snap(i) for i in range(1,4)]}
        surveillance=control_surveillance.surveil(history,self.policy)
        out=causal_routing.attribute(history,surveillance,self.routes,self.policy)
        target=next(e for e in out["entities"] if e["entity_id"]=="ENTRY-LKT-INVCOP")
        self.assertEqual(target["state"],"UNCHANGED_CONTROL")
        self.assertEqual(causal_routing.route_plan(out)["assignments"],[])

    def test_real_change_is_attributed_but_held_during_requalification(self):
        t,c=self.changed_pair()
        history={"snapshots":[self.snap(i) for i in range(1,4)]+[self.snap(4,t,c)]}
        surveillance=control_surveillance.surveil(history,self.policy)
        out=causal_routing.attribute(history,surveillance,self.routes,self.policy)
        target=next(e for e in out["entities"] if e["entity_id"]=="ENTRY-LKT-INVCOP")
        self.assertEqual(target["state"],"CAUSAL_REQUALIFY")
        self.assertEqual(target["changed_causes"],["SOURCE"])
        self.assertEqual(causal_routing.route_plan(out)["assignments"],[])

    def test_failed_causal_epoch_routes_only_source_owner_surface(self):
        t,c=self.changed_pair()
        history={"snapshots":[self.snap(i) for i in range(1,4)]+[self.snap(i,t,c) for i in range(4,7)]}
        surveillance=control_surveillance.surveil(history,self.policy)
        out=causal_routing.attribute(history,surveillance,self.routes,self.policy)
        target=next(e for e in out["entities"] if e["entity_id"]=="ENTRY-LKT-INVCOP")
        self.assertEqual(target["state"],"CAUSAL_ESCALATE")
        self.assertEqual(target["changed_causes"],["SOURCE"])
        plan=causal_routing.route_plan(out)
        assignments=[a for a in plan["assignments"] if a["entity_id"]=="ENTRY-LKT-INVCOP"]
        self.assertEqual(len(assignments),1)
        self.assertEqual(assignments[0]["crew"],"SOURCE_EVIDENCE_CREW")
        self.assertEqual(assignments[0]["repos"],["GBOGEB/cryoplant-project"])
        self.assertEqual(assignments[0]["books"],["BOOK-QPLANT"])

if __name__=="__main__": unittest.main()
