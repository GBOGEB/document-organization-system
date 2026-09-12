import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("render_book", ROOT / "render_book.py")
rb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rb)


class GloobBookTests(unittest.TestCase):
    def setUp(self):
        self.graph_path = ROOT / "graph" / "qplant-energy.json"
        self.graph, self.graph_sha = rb.load_graph(self.graph_path)

    def test_depth_projection_is_monotonic(self):
        counts = [len(rb.project(self.graph, depth)["atoms"]) for depth in (1, 3, 5)]
        self.assertLess(counts[0], counts[1])
        self.assertLess(counts[1], counts[2])

    def test_slug_and_address_contract(self):
        self.assertEqual(self.graph["entry"]["slug"], "lkt-invcop")
        self.assertEqual(self.graph["entry"]["address"], "gloob://qplant/energy/lkt-invcop")
        self.assertTrue(rb.SLUG_RE.fullmatch(self.graph["entry"]["slug"]))

    def test_same_graph_renders_three_formats_and_receipt(self):
        with tempfile.TemporaryDirectory() as td:
            receipt = rb.render_all(self.graph_path, Path(td), "deep")
            self.assertEqual(receipt["input"]["sha256"], self.graph_sha)
            self.assertEqual(set(receipt["outputs"]), {"html", "md", "pdf"})
            for record in receipt["outputs"].values():
                self.assertTrue(Path(record["path"]).exists())
            pdf_path = Path(receipt["outputs"]["pdf"]["path"])
            self.assertTrue(pdf_path.read_bytes().startswith(b"%PDF-1.4"))
            md_path = Path(receipt["outputs"]["md"]["path"])
            md = md_path.read_text()
            self.assertIn("### LKT invCOP offered point", md)
            self.assertIn("GBOGEB/cryoplant-project@a9cb3241", md)
            self.assertIn("GBOGEB/CODEX@631bc364", md)


if __name__ == "__main__":
    unittest.main()
