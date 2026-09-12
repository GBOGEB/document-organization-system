import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class GatewayV03Tests(unittest.TestCase):
    def setUp(self):
        self.html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.registry = json.loads((ROOT / "registry.yaml").read_text(encoding="utf-8"))

    def test_gateway_is_registry_driven(self):
        self.assertIn("fetch('./registry.yaml'", self.html)
        self.assertIn('id="book"', self.html)
        self.assertIn('id="entry"', self.html)
        self.assertIn("record.entry.graph", self.html)

    def test_canonical_route_carries_book_entry_and_profile(self):
        self.assertIn("searchParams.set('book'", self.html)
        self.assertIn("searchParams.set('entry'", self.html)
        self.assertIn("searchParams.set('profile'", self.html)
        self.assertIn("graph?.entry?.slug", self.html)

    def test_all_registry_entries_are_routable(self):
        entries = []
        for book in self.registry["books"]:
            for chapter in book["chapters"]:
                for entry in chapter["entries"]:
                    entries.append((book["slug"], entry["slug"], ROOT / entry["graph"]))
        self.assertGreaterEqual(len(entries), 3)
        for book_slug, entry_slug, graph_path in entries:
            self.assertTrue(book_slug)
            self.assertTrue(entry_slug)
            self.assertTrue(graph_path.exists(), graph_path)

    def test_shared_atoms_and_cross_book_links_are_visible(self):
        self.assertIn("sharedCatalog", self.html)
        self.assertIn("shared_atom_refs", self.html)
        self.assertIn("cross_book_references", self.html)
        self.assertIn("Cross-Book references", self.html)

    def test_legacy_depth_and_source_controls_are_retained(self):
        self.assertIn("PROFILE_DEPTH", self.html)
        self.assertIn('id="profile"', self.html)
        self.assertIn('id="sourcesBtn"', self.html)
        self.assertIn('id="copyBtn"', self.html)


if __name__ == "__main__":
    unittest.main()
