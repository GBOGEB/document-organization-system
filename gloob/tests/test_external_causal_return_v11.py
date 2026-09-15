import copy, json, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
import causal_routing, control_surveillance, external_causal_return, federate_external_returns, telemetry

class ExternalCausalReturnV11Tests(unittest.TestCase):
    def setUp(self):
        self.policy=json.loads((ROOT/"control"/"surveillance-policy.json").read_text(encoding="utf-8"))
        self.return_policy=json.loads((ROOT/"control"/"external-return-policy.json").read_text(encoding="utf-8"))
        self.routes=json.loads((ROOT/"control"/"causal-route-registry.json").read_text(encoding="utf-8"))
        self.base_t=telemetry.snapshot(); self.base_c=causal_routing.causal_snapshot()

    def snap(self,n,t=None,c=None):
        return {"receipt":{"source_commit":str(n).zfill(40),"run_id":str(n)},"telemetry":copy.deepcopy(t or self.base_t),"causal":copy.deepcopy(c or self.base_c)}

    def route(self):
        t=copy.deepcopy(self.base_t); next(r for r in t["rows"] if r["entity_id"]=="ENTRY-LKT-INVCOP")["source_count"]=0
        c=copy.deepcopy(self.base_c); e=c["entities"]["ENTRY-LKT-INVCOP"]; e["causes"]["SOURCE"]["items"]=[]; c["entities"]["ENTRY-LKT-INVCOP"]=causal_routing.recompute_entity(e)
        h={"snapshots":[self.snap(i) for i in range(1,4)]+[self.snap(i,t,c) for i in range(4,7)]}
        s=control_surveillance.surveil(h,self.policy); a=causal_routing.attribute(h,s,self.routes,self.policy)
        return causal_routing.route_plan(a)["assignments"][0]

    def valid_return(self,route):
        return {"schema":"gloob-causal-return/0.1","route_id":route["route_id"],"assignment_digest":route["assignment_digest"],"repo":"GBOGEB/cryoplant-project","crew":"SOURCE_EVIDENCE_CREW","outcome":"RESOLVED","evidence":{"source_commit":"a"*40,"runner_commit":"a"*40,"run_id":"991","steps":8,"conclusion":"success"}}

    def test_route_emits_deterministic_handshake(self):
        route=self.route(); hp=external_causal_return.handshakes({"assignments":[route]}); hs=hp["handshakes"][0]
        self.assertTrue(route["route_id"].startswith("ROUTE-")); self.assertEqual(len(route["assignment_digest"]),64)
        self.assertEqual(hs["target_repos"],["GBOGEB/cryoplant-project"])

    def test_valid_exact_sha_return_closes_external_route_but_only_requalifies_local(self):
        route=self.route(); _,ledger,closure=external_causal_return.process({"assignments":[route]},[self.valid_return(route)],self.return_policy)
        self.assertEqual(ledger["counts"]["RETURN_ACCEPTED_REQUALIFY"],1)
        self.assertFalse(ledger["closures"][0]["control_credit"])
        self.assertEqual(closure["mode"],"EXTERNAL_RETURN_DOES_NOT_GRANT_CONTROL")
        self.assertEqual(closure["requalify"][0]["entity_id"],"ENTRY-LKT-INVCOP")

    def test_stale_or_zero_step_return_is_rejected_and_route_stays_open(self):
        route=self.route(); ret=self.valid_return(route); ret["assignment_digest"]="0"*64; ret["evidence"]["steps"]=0
        _,ledger,closure=external_causal_return.process({"assignments":[route]},[ret],self.return_policy)
        self.assertEqual(ledger["counts"]["REJECT_RETURN"],1)
        self.assertIn("ASSIGNMENT_DIGEST_MISMATCH",ledger["closures"][0]["errors"])
        self.assertIn("ZERO_STEP_RETURN",ledger["closures"][0]["errors"])
        self.assertEqual(len(closure["keep_open"]),1)

    def test_no_open_routes_causes_no_cross_repo_federation(self):
        hp=external_causal_return.handshakes({"assignments":[]}); out=federate_external_returns.federate(hp,None)
        self.assertEqual(out["state"],"NO_OPEN_HANDSHAKES"); self.assertEqual(out["repos"],[])

if __name__=="__main__": unittest.main()
