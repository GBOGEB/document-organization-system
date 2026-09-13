import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("view_model", ROOT / "view_model.py")
view_model = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(view_model)


class SyncedViewsV04Tests(unittest.TestCase):
    def setUp(self):
        self.registry = json.loads((ROOT / "registry.yaml").read_text(encoding="utf-8"))
        self.shared = json.loads((ROOT / "graph/shared-atoms.json").read_text(encoding="utf-8"))
        self.timeline = json.loads((ROOT / "control/timeline.json").read_text(encoding="utf-8"))
        self.html = (ROOT / "views.html").read_text(encoding="utf-8")
        self.record = view_model.flatten_entries(self.registry)[0]
        self.graph = json.loads((ROOT / self.record["entry"]["graph"]).read_text(encoding="utf-8"))

    def test_book_and_graph_share_immutable_atom_ids(self):
        projection = view_model.graph_projection(self.record, self.graph, self.shared, depth=5)
        atom_ids = {a["id"] for a in projection["atoms"]}
        node_ids = {n["id"] for n in projection["nodes"]}
        self.assertTrue(atom_ids)
        self.assertTrue(atom_ids <= node_ids)
        self.assertIn("data-id", self.html)
        self.assertIn("selected", self.html)

    def test_shared_atom_remains_reference_not_copy(self):
        projection = view_model.graph_projection(self.record, self.graph, self.shared, depth=5)
        shared_ids = {a["id"] for a in projection["atoms"] if a["scope"] == "SHARED"}
        self.assertEqual(shared_ids, set(self.graph.get("shared_atom_refs", [])))
        local_ids = {a["id"] for a in self.graph.get("atoms", [])}
        self.assertTrue(shared_ids.isdisjoint(local_ids))

    def test_selective_provenance_levels_expand_monotonically(self):
        summary = view_model.provenance_projection(self.record, self.graph, self.shared, self.timeline, "summary")
        evidence = view_model.provenance_projection(self.record, self.graph, self.shared, self.timeline, "evidence")
        runtime = view_model.provenance_projection(self.record, self.graph, self.shared, self.timeline, "runtime")
        self.assertNotIn("commit", summary["sources"][0])
        self.assertIn("commit", evidence["sources"][0])
        self.assertIn("operators", runtime)
        self.assertIn("runtime", runtime)

    def test_timeline_is_ordered_and_exact_sha_bound(self):
        events = view_model.relevant_events(self.record, self.timeline)
        self.assertGreaterEqual(len(events), 6)
        self.assertEqual([e["sequence"] for e in events], sorted(e["sequence"] for e in events))
        for event in events:
            self.assertRegex(event["sha"], r"^[0-9a-f]{40}$")
            self.assertGreater(event["run_id"], 0)
            self.assertEqual(event["result"], "PASS")

    def test_runtime_separates_proofs_from_control_promotions(self):
        runtime = view_model.runtime_projection(self.record, self.timeline)
        self.assertTrue(runtime["proofs"])
        self.assertTrue(runtime["promotions"])
        self.assertTrue(all(e["kind"] == "RUNTIME_PROOF" for e in runtime["proofs"]))
        self.assertTrue(all(e["kind"] == "PROMOTION" for e in runtime["promotions"]))

    def test_user_surface_exposes_all_five_views(self):
        for label in ["Book", "Graph", "Selective provenance", "Timeline", "Runtime"]:
            self.assertIn(label, self.html)
        self.assertIn("do not confer engineering acceptance", self.html)


if __name__ == "__main__":
    unittest.main()
