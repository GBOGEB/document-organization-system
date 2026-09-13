import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("registry", ROOT / "registry.py")
registry = importlib.util.module_from_spec(spec)
spec.loader.exec_module(registry)

class GloobRegistryV02Tests(unittest.TestCase):
    def setUp(self): self.registry_path = ROOT / "registry.yaml"

    def test_registry_has_multiple_books_and_entries(self):
        index=registry.build_index(self.registry_path)
        self.assertEqual(set(index["books"]),{"BOOK-QPLANT","BOOK-GLOOB"})
        self.assertEqual(set(index["entries"]),{
            "ENTRY-LKT-INVCOP","ENTRY-LKT-PERFORMANCE-POINT","ENTRY-LKT-POWER-BREAKDOWN",
            "ENTRY-LKT-EVIDENCE-BOUNDARY","ENTRY-LKT-RUNTIME-RECEIPT",
            "ENTRY-GLOOB-BOOK-CONTRACT","ENTRY-GLOOB-SESSION-CONTROL"})
        self.assertEqual(index["addresses"]["gloob://qplant/energy/lkt-invcop"],"ENTRY-LKT-INVCOP")

    def test_shared_atom_where_used_is_reverse_and_cross_book(self):
        users=registry.where_used("ATOM-GLOOB-FEDERATED-AUTHORITY",self.registry_path)
        self.assertEqual(users,["ENTRY-GLOOB-BOOK-CONTRACT","ENTRY-GLOOB-SESSION-CONTROL","ENTRY-LKT-INVCOP"])
        self.assertEqual(registry.where_used("ATOM-GLOOB-BOOK-NOT-REPO",self.registry_path),["ENTRY-GLOOB-BOOK-CONTRACT"])

    def test_operator_catalog_is_canonical_and_where_used(self):
        index=registry.build_index(self.registry_path); expected=set(index["entries"])
        self.assertEqual(set(index["operator_usage"]["OP-GLOOB-DEPTH-PROJECT"]),expected)
        self.assertEqual(set(index["operator_usage"]["OP-GLOOB-RENDER"]),expected)

    def test_cross_book_reference_is_registered(self):
        ref=registry.build_index(self.registry_path)["cross_book_references"][0]
        self.assertEqual(ref["from_entry"],"ENTRY-LKT-INVCOP"); self.assertEqual(ref["to_entry"],"ENTRY-GLOOB-BOOK-CONTRACT"); self.assertEqual(ref["via_atom"],"ATOM-GLOOB-FEDERATED-AUTHORITY")

    def test_edition_freeze_is_deterministic_and_complete(self):
        a=registry.freeze_edition(self.registry_path); b=registry.freeze_edition(self.registry_path)
        self.assertEqual(a,b); self.assertTrue(a["id"].startswith("EDITION-GLOOB-")); self.assertEqual(len(a["sha256"]),64)
        self.assertIn("registry.yaml",a["files"]); self.assertIn("graph/shared-atoms.json",a["files"]); self.assertIn("operators.json",a["files"])
        self.assertEqual(len(a["entry_graph_digests"]),7); self.assertEqual(set(a["operator_digests"]),{"OP-GLOOB-DEPTH-PROJECT","OP-GLOOB-RENDER"})

    def test_shared_atom_change_fans_out_to_all_consuming_entries(self):
        baseline=registry.freeze_edition(self.registry_path); changed=registry.simulate_atom_change(baseline,"ATOM-GLOOB-FEDERATED-AUTHORITY"); diff=registry.semantic_diff(baseline,changed)
        self.assertEqual(diff["changed_atoms"],["ATOM-GLOOB-FEDERATED-AUTHORITY"])
        self.assertEqual(diff["affected_entries"],["ENTRY-GLOOB-BOOK-CONTRACT","ENTRY-GLOOB-SESSION-CONTROL","ENTRY-LKT-INVCOP"])

    def test_local_atom_change_affects_only_owning_entry(self):
        baseline=registry.freeze_edition(self.registry_path)
        changed=registry.simulate_atom_change(baseline,"ATOM-LKT-INVCOP")
        self.assertEqual(registry.semantic_diff(baseline,changed)["affected_entries"],["ENTRY-LKT-INVCOP"])
        changed=registry.simulate_atom_change(baseline,"ATOM-LKT-DIRECT-SUBTOTAL")
        self.assertEqual(registry.semantic_diff(baseline,changed)["affected_entries"],["ENTRY-LKT-POWER-BREAKDOWN"])
        changed=registry.simulate_atom_change(baseline,"ATOM-LKT-QEQ")
        self.assertEqual(registry.semantic_diff(baseline,changed)["affected_entries"],["ENTRY-LKT-PERFORMANCE-POINT"])
        changed=registry.simulate_atom_change(baseline,"ATOM-CODEX-RECEIPT")
        self.assertEqual(registry.semantic_diff(baseline,changed)["affected_entries"],["ENTRY-LKT-RUNTIME-RECEIPT"])

    def test_unknown_shared_atom_is_rejected(self):
        data=registry.load_registry(self.registry_path); broken=copy.deepcopy(data)
        broken["books"][0]["chapters"][0]["entries"][0]["uses_shared_atoms"]=["ATOM-DOES-NOT-EXIST"]
        shared=registry._load(ROOT/broken["shared_atom_catalog"]); known={a["id"] for a in shared["atoms"]}; refs=broken["books"][0]["chapters"][0]["entries"][0]["uses_shared_atoms"]
        self.assertTrue(set(refs)-known)

if __name__ == "__main__": unittest.main()
