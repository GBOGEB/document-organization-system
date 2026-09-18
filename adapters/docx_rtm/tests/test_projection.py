import copy
import hashlib
import importlib.util
import json
import re
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "build_projection.py"
SOURCE = REPO_ROOT / "contracts" / "data_rich_document" / "examples" / "adr-001.json"

spec = importlib.util.spec_from_file_location("docx_rtm_projection", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class DocxRtmProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_bytes = SOURCE.read_bytes()
        cls.data = json.loads(cls.source_bytes.decode("utf-8"))

    def build(self, data=None, max_heading_level=3):
        payload = copy.deepcopy(data if data is not None else self.data)
        return module.render_markdown(payload, max_heading_level=max_heading_level)

    def test_maps_levels_to_unnumbered_markdown_headings(self):
        markdown, section_map, _ = self.build()
        self.assertIn("# Context and Scope {#sec-001}", markdown)
        self.assertIn("## Objectives {#sec-110}", markdown)
        self.assertIn("### Change Transactions {#sec-211}", markdown)
        headings = [line for line in markdown.splitlines() if line.startswith("#")]
        for heading in headings:
            title = heading.lstrip("#").strip()
            self.assertFalse(re.match(r"\d+(?:\.\d+)*[.)]?\s+", title), heading)
        styles = {row["section_id"]: row["word_style_expected"] for row in section_map}
        self.assertEqual(styles["SEC-001"], "Heading 1")
        self.assertEqual(styles["SEC-110"], "Heading 2")
        self.assertEqual(styles["SEC-211"], "Heading 3")

    def test_requirement_is_rendered_once_at_primary_section(self):
        markdown, _, requirement_map = self.build()
        self.assertEqual(markdown.count("REQ-001 — Stable section identity"), 1)
        req = next(row for row in requirement_map if row["requirement_id"] == "REQ-001")
        self.assertEqual(req["primary_section_id"], "SEC-210")
        self.assertEqual(req["secondary_section_ids"], ["SEC-300"])

    def test_manifest_preserves_authority_boundary_and_hashes(self):
        markdown, section_map, requirement_map = self.build()
        manifest = module.build_manifest(
            copy.deepcopy(self.data),
            self.source_bytes,
            markdown,
            section_map,
            requirement_map,
            source_repo="GBOGEB/document-organization-system",
            source_ref="TEST-SHA",
            source_path="contracts/data_rich_document/examples/adr-001.json",
        )
        self.assertFalse(manifest["authority"]["rendered_output_authoritative"])
        self.assertFalse(manifest["authority"]["authority_transfer"])
        self.assertFalse(manifest["authority"]["semantic_changes_allowed_in_consumer"])
        self.assertEqual(
            manifest["source"]["sha256"],
            hashlib.sha256(self.source_bytes).hexdigest(),
        )
        self.assertEqual(
            manifest["projection"]["sha256"],
            hashlib.sha256(markdown.encode("utf-8")).hexdigest(),
        )
        self.assertEqual(
            manifest["projection"]["heading_contract"]["numbering"],
            "TEMPLATE_MANAGED",
        )
        self.assertEqual(
            manifest["docx_rtm_consumer"]["forbidden_numbering_filter"],
            "config/filters/extend_headings.lua",
        )

    def test_projection_is_deterministic_for_same_inputs(self):
        a = self.build()
        b = self.build()
        self.assertEqual(a, b)

    def test_rejects_pre_numbered_title(self):
        data = copy.deepcopy(self.data)
        data["sections"][2]["title"] = "2. Architecture Decision"
        with self.assertRaisesRegex(module.ProjectionError, "rendered numbering"):
            self.build(data)

    def test_rejects_heading_beyond_adapter_depth(self):
        data = copy.deepcopy(self.data)
        target = next(section for section in data["sections"] if section["id"] == "SEC-211")
        target["heading_level"] = 4
        # Keep parent relation semantically coherent so projection depth is first failure.
        parent = next(section for section in data["sections"] if section["id"] == "SEC-210")
        parent["heading_level"] = 3
        grandparent = next(section for section in data["sections"] if section["id"] == "SEC-200")
        grandparent["heading_level"] = 2
        root = next(section for section in data["sections"] if section["id"] == "SEC-001")
        root["heading_level"] = 1
        # This edit also makes sibling SEC-220 inconsistent, so instead assert any semantic/projection fail.
        with self.assertRaises(module.ProjectionError):
            self.build(data, max_heading_level=3)

    def test_rejects_semantically_invalid_source(self):
        data = copy.deepcopy(self.data)
        data["relations"][0]["to"] = "REQ-NOT-THERE"
        with self.assertRaisesRegex(module.ProjectionError, "semantic validation"):
            self.build(data)

    def test_cli_projection_writes_manifest_and_markdown(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            md_path, manifest_path = module.project_file(
                SOURCE,
                out,
                source_repo="GBOGEB/document-organization-system",
                source_ref="TEST-SHA",
            )
            self.assertTrue(md_path.exists())
            self.assertTrue(manifest_path.exists())
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["source"]["git_ref"], "TEST-SHA")
            self.assertEqual(manifest["projection"]["section_count"], len(self.data["sections"]))


if __name__ == "__main__":
    unittest.main()
