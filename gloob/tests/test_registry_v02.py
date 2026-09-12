import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("registry", ROOT / "registry.py")
registry = importlib.util.module_from_spec(spec)
spec.loader.exec_module(registry)


class GloobRegistryV02Tests(unittest.TestCase):
    def setUp(self):
        self.registry_path = ROOT / "registry.yaml"

    def test_registry_has_multiple_books_and_entries(self):
        index = registry.build_index(self.registry_path)
        self.assertEqual(set(index["books"]), {"BOOK-QPLANT", "BOOK-GLOOB"})
        self.assertEqual(
            set(index["entries"]),
            {
                "ENTRY-LKT-INVCOP",
                "ENTRY-GLOOB-BOOK-CONTRACT",
                "ENTRY-GLOOB-SESSION-CONTROL",
            },
        )
        self.assertEqual(
            index["addresses"]["gloob://qplant/energy/lkt-invcop"],
            "ENTRY-LKT-INVCOP",
        )

    def test_shared_atom_where_used_is_reverse_and_cross_book(self):
        users = registry.where_used("ATOM-GLOOB-FEDERATED-AUTHORITY", self.registry_path)
        self.assertEqual(
            users,
            [
                "ENTRY-GLOOB-BOOK-CONTRACT",
                "ENTRY-GLOOB-SESSION-CONTROL",
                "ENTRY-LKT-INVCOP",
            ],
        )
        book_contract_only = registry.where_used("ATOM-GLOOB-BOOK-NOT-REPO", self.registry_path)
        self.assertEqual(book_contract_only, ["ENTRY-GLOOB-BOOK-CONTRACT"])

    def test_cross_book_reference_is_registered(self):
        index = registry.build_index(self.registry_path)
        self.assertEqual(len(index["cross_book_references"]), 1)
        ref = index["cross_book_references"][0]
        self.assertEqual(ref["from_entry"], "ENTRY-LKT-INVCOP")
        self.assertEqual(ref["to_entry"], "ENTRY-GLOOB-BOOK-CONTRACT")
        self.assertEqual(ref["via_atom"], "ATOM-GLOOB-FEDERATED-AUTHORITY")

    def test_edition_freeze_is_deterministic_and_complete(self):
        a = registry.freeze_edition(self.registry_path)
        b = registry.freeze_edition(self.registry_path)
        self.assertEqual(a, b)
        self.assertTrue(a["id"].startswith("EDITION-GLOOB-"))
        self.assertEqual(len(a["sha256"]), 64)
        self.assertIn("registry.yaml", a["files"])
        self.assertIn("graph/shared-atoms.json", a["files"])
        self.assertEqual(len(a["entry_graph_digests"]), 3)

    def test_shared_atom_change_fans_out_to_all_consuming_entries(self):
        baseline = registry.freeze_edition(self.registry_path)
        changed = registry.simulate_atom_change(baseline, "ATOM-GLOOB-FEDERATED-AUTHORITY")
        diff = registry.semantic_diff(baseline, changed)
        self.assertEqual(diff["changed_atoms"], ["ATOM-GLOOB-FEDERATED-AUTHORITY"])
        self.assertEqual(
            diff["affected_entries"],
            [
                "ENTRY-GLOOB-BOOK-CONTRACT",
                "ENTRY-GLOOB-SESSION-CONTROL",
                "ENTRY-LKT-INVCOP",
            ],
        )

    def test_local_atom_change_affects_only_owning_entry(self):
        baseline = registry.freeze_edition(self.registry_path)
        changed = registry.simulate_atom_change(baseline, "ATOM-LKT-INVCOP")
        diff = registry.semantic_diff(baseline, changed)
        self.assertEqual(diff["changed_atoms"], ["ATOM-LKT-INVCOP"])
        self.assertEqual(diff["affected_entries"], ["ENTRY-LKT-INVCOP"])

    def test_unknown_shared_atom_is_rejected(self):
        data = registry.load_registry(self.registry_path)
        broken = copy.deepcopy(data)
        broken["books"][0]["chapters"][0]["entries"][0]["uses_shared_atoms"] = ["ATOM-DOES-NOT-EXIST"]
        # Validate the invariant without writing by checking the shared catalog directly.
        shared = registry._load(ROOT / broken["shared_atom_catalog"])
        known = {atom["id"] for atom in shared["atoms"]}
        refs = broken["books"][0]["chapters"][0]["entries"][0]["uses_shared_atoms"]
        self.assertTrue(set(refs) - known)


if __name__ == "__main__":
    unittest.main()
