import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from render import render

BASE = {"worktree_id":"SYNTHETIC_WORKTREE", "entries":[{"id":"a", "title":"Sample", "group":"Docs", "url":"https://github.com/example/repository", "status":"UNVERIFIED", "detail":"A source document"}]}

class TestSatellite(unittest.TestCase):
    def test_smoke(self):
        out=render(BASE)
        self.assertIn("Sample",out)
        self.assertIn("Content-Security-Policy",out)
        self.assertIn("Open source link",out)
    def test_search_includes_detail(self):
        self.assertIn("a source document", render(BASE))
    def test_duplicate_id(self):
        with self.assertRaises(ValueError): render({"entries":BASE["entries"]*2})
    def test_non_dict_entry(self):
        with self.assertRaises(ValueError): render({"entries":["broken"]})
    def test_javascript_url(self):
        with self.assertRaises(ValueError): render({"entries":[{"id":"x","url":"javascript:alert(1)"}]})
    def test_http_url(self):
        with self.assertRaises(ValueError): render({"entries":[{"id":"x","url":"http://example.com"}]})
    def test_newline_url(self):
        with self.assertRaises(ValueError): render({"entries":[{"id":"x","url":"https://example.com/\nscript"}]})
    def test_backslash_url(self):
        with self.assertRaises(ValueError): render({"entries":[{"id":"x","url":"https://example.com\\evil.tld"}]})
    def test_embedded_credentials(self):
        with self.assertRaises(ValueError): render({"entries":[{"id":"x","url":"https://user:secret@example.com/a"}]})
    def test_untrusted_markup_escaped(self):
        out=render({"entries":[{"id":"x","title":"<script>alert(1)</script>", "detail":"<img src=x onerror=alert(1)>"}]})
        self.assertNotIn("<script>alert(1)</script>",out)
        self.assertNotIn("<img src=x onerror=alert(1)>",out)
    def test_unknown_status(self):
        with self.assertRaises(ValueError): render({"entries":[{"id":"x","status":"APPROVED"}]})
    def test_missing_entries(self):
        with self.assertRaises(ValueError): render({})
    def test_empty_valid(self):
        out=render({"entries":[]})
        self.assertIn("Google Drive Satellite Worktree",out)
    def test_entry_cap(self):
        with self.assertRaises(ValueError): render({"entries":[{"id":str(i)} for i in range(5001)]})

if __name__ == "__main__": unittest.main()
