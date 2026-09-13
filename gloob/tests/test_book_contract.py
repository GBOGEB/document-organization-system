import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("render_book",ROOT/"render_book.py")
rb=importlib.util.module_from_spec(spec); spec.loader.exec_module(rb)

class GloobBookTests(unittest.TestCase):
    def setUp(self):
        self.graph_path=ROOT/"graph"/"qplant-energy.json"
        self.power_path=ROOT/"graph"/"qplant-energy-power.json"
        self.evidence_path=ROOT/"graph"/"qplant-energy-evidence.json"
        self.graph,self.graph_sha=rb.load_graph(self.graph_path)

    def test_depth_projection_is_monotonic_across_decomposed_family(self):
        graphs=[rb.load_graph(p)[0] for p in (self.graph_path,self.power_path,self.evidence_path)]
        counts=[sum(len(rb.project(g,depth)["atoms"]) for g in graphs) for depth in (1,3,5)]
        self.assertLess(counts[0],counts[1]); self.assertLess(counts[1],counts[2])

    def test_slug_and_address_contract(self):
        self.assertEqual(self.graph["entry"]["slug"],"lkt-invcop")
        self.assertEqual(self.graph["entry"]["address"],"gloob://qplant/energy/lkt-invcop")
        self.assertTrue(rb.SLUG_RE.fullmatch(self.graph["entry"]["slug"]))

    def test_root_and_evidence_entries_render_without_atom_copying(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            receipt=rb.render_all(self.graph_path,root/"root","deep")
            self.assertEqual(receipt["input"]["sha256"],self.graph_sha); self.assertEqual(set(receipt["outputs"]),{"html","md","pdf"})
            md=Path(receipt["outputs"]["md"]["path"]).read_text()
            self.assertIn('<a id="lkt-invcop"></a>',md); self.assertIn('<a id="equivalent-load"></a>',md)
            self.assertNotIn('<a id="sat-metering-boundary"></a>',md)
            self.assertIn("### LKT invCOP offered point",md); self.assertIn("GBOGEB/cryoplant-project@a9cb3241",md)
            evidence=rb.render_all(self.evidence_path,root/"evidence","deep")
            evidence_md=Path(evidence["outputs"]["md"]["path"]).read_text()
            self.assertIn('<a id="sat-metering-boundary"></a>',evidence_md)
            self.assertIn("GBOGEB/CODEX@631bc364",evidence_md)
            root_atoms={a["id"] for a in self.graph["atoms"]}; evidence_atoms={a["id"] for a in rb.load_graph(self.evidence_path)[0]["atoms"]}
            self.assertTrue(root_atoms.isdisjoint(evidence_atoms))

    def test_canonical_atom_change_propagates_all_profiles_without_lineage_drift(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); baseline_dir=root/"baseline"; changed_dir=root/"changed"; changed_graph_path=root/"qplant-energy.changed.json"
            baseline={profile:rb.render_all(self.graph_path,baseline_dir/profile,profile) for profile in rb.PROFILES}
            changed_graph=json.loads(self.graph_path.read_text()); target=next(a for a in changed_graph["atoms"] if a["id"]=="ATOM-LKT-INVCOP"); target["value"]=311
            changed_graph_path.write_text(json.dumps(changed_graph,indent=2)+"\n"); changed_loaded,changed_sha=rb.load_graph(changed_graph_path)
            changed={profile:rb.render_all(changed_graph_path,changed_dir/profile,profile) for profile in rb.PROFILES}
            self.assertNotEqual(self.graph_sha,changed_sha); self.assertEqual(self.graph["entry"]["id"],changed_loaded["entry"]["id"]); self.assertEqual(self.graph["entry"]["slug"],changed_loaded["entry"]["slug"])
            self.assertEqual([(s["repo"],s["commit"],s["path"]) for s in self.graph["sources"]],[(s["repo"],s["commit"],s["path"]) for s in changed_loaded["sources"]])
            for profile in rb.PROFILES:
                self.assertNotEqual(baseline[profile]["input"]["sha256"],changed[profile]["input"]["sha256"])
                for ext in ("html","md","pdf"): self.assertNotEqual(baseline[profile]["outputs"][ext]["sha256"],changed[profile]["outputs"][ext]["sha256"])
                self.assertEqual(baseline[profile]["entry_id"],changed[profile]["entry_id"]); self.assertEqual(baseline[profile]["entry_slug"],changed[profile]["entry_slug"]); self.assertEqual(baseline[profile]["source_commits"],changed[profile]["source_commits"])

if __name__=="__main__": unittest.main()
