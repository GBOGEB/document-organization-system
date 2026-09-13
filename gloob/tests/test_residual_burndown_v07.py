import json, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
import registry, telemetry, recursive_control, residual_burndown

class ResidualBurndownV07Tests(unittest.TestCase):
    def test_lkt_monolith_is_decomposed_without_atom_copying(self):
        idx=registry.build_index(ROOT/"registry.yaml")
        self.assertIn("ENTRY-LKT-POWER-BREAKDOWN",idx["entries"])
        self.assertIn("ENTRY-LKT-EVIDENCE-BOUNDARY",idx["entries"])
        root=json.loads((ROOT/"graph"/"qplant-energy.json").read_text(encoding="utf-8"))
        moved={"ATOM-LKT-DIRECT-SUBTOTAL","ATOM-LKT-CWS","ATOM-LKT-EXPECTED","ATOM-LKT-UNCERTAINTY","ATOM-LKT-SAT","ATOM-LKT-SOURCE","ATOM-CODEX-RECEIPT"}
        self.assertTrue(moved.isdisjoint({a["id"] for a in root["atoms"]}))
        self.assertEqual(sum(e["type"]=="DECOMPOSES_TO" for e in root["edges"]),2)

    def test_operator_catalog_is_reused_and_not_cardinality_duplicated(self):
        idx=registry.build_index(ROOT/"registry.yaml"); rows={r["entity_id"]:r for r in telemetry.measured_rows()}
        self.assertEqual(len(idx["operator_usage"]["OP-GLOOB-RENDER"]),5)
        self.assertEqual(rows["OP-GLOOB-RENDER"]["reuse_count"],5)
        self.assertEqual(rows["OP-GLOOB-RENDER"]["operator_count"],1)
        self.assertEqual(rows["OP-GLOOB-DEPTH-PROJECT"]["operator_count"],1)

    def test_publication_wildcards_are_global_not_entity_runtime(self):
        snap=telemetry.snapshot(); self.assertGreater(snap["global_control_events"],0)
        for r in snap["rows"]:
            if r["entity_type"] in {"ENTRY","BOOK","OPERATOR"}:
                self.assertEqual(r["runtime_proof_count"],0); self.assertEqual(r["promotion_count"],0)

    def test_reverse_load_maps_components_to_concrete_structures(self):
        snap=telemetry.snapshot(); history={"snapshots":[{"receipt":{"source_commit":str(i).zfill(40)},"telemetry":snap} for i in range(3)]}
        control=recursive_control.analyze(history)
        out=residual_burndown.decompose(control)
        self.assertEqual(out["schema"],"gloob-residual-burndown/0.1")
        for entity in out["entities"]:
            self.assertTrue(entity["components"])
            self.assertTrue(all(c["feature_contributions"] for c in entity["components"]))
            top=entity["components"][0]["feature_contributions"][0]
            self.assertIn("reverse_load",top)

if __name__=="__main__": unittest.main()
