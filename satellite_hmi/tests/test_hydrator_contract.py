"""Exercise the notebook's actual code cells with a synthetic payload, not a parallel implementation."""
import base64
import hashlib
import json
import re
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / 'notebooks' / '01_WORKTREE_HYDRATOR.ipynb'
BUNDLE = ROOT / 'fixtures' / 'synthetic_bundle.json'


def notebook_namespace():
    cells = json.loads(NOTEBOOK.read_text(encoding='utf-8'))['cells']
    source = ''.join(cells[3]['source'])
    source = source[:source.rfind('print(hydrate_bundle(')]
    ns = {'Path':Path,'base64':base64,'hashlib':hashlib,'json':json,'re':re}
    exec(compile(source,'notebook_hydrator.py','exec'),ns)
    return ns


class TestNotebookContract(unittest.TestCase):
    def test_notebook_dry_run(self):
        ns=notebook_namespace()
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'hydrated'
            result=ns['hydrate_bundle'](BUNDLE,out,execute=False)
            self.assertEqual(result['files_checked'],2)
            self.assertFalse(out.exists())

    def test_explicit_hydration_and_no_overwrite(self):
        ns=notebook_namespace()
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'hydrated'
            result=ns['hydrate_bundle'](BUNDLE,out,execute=True)
            self.assertEqual(result['files_checked'],2)
            self.assertTrue((out/'docs'/'README.md').is_file())
            with self.assertRaises(ValueError): ns['hydrate_bundle'](BUNDLE,out,execute=True)

    def test_reject_path_traversal(self):
        ns=notebook_namespace()
        for s in ['../x','/root/secret','folder/../../x','folder\\evil','C:drive','x//y']:
            with self.subTest(s=s):
                with self.assertRaises(ValueError): ns['safe_relative_path'](s)

    def test_reject_tamper(self):
        ns=notebook_namespace()
        with tempfile.TemporaryDirectory() as td:
            data=json.loads(BUNDLE.read_text())
            data['files'][0]['sha256']='0'*64
            p=Path(td)/'tampered.json';p.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'Digest mismatch'):
                ns['hydrate_bundle'](p,Path(td)/'out',execute=True)
            self.assertFalse((Path(td)/'out').exists())

    def test_reject_duplicate_path(self):
        ns=notebook_namespace()
        with tempfile.TemporaryDirectory() as td:
            data=json.loads(BUNDLE.read_text())
            data['files'].append(data['files'][0].copy())
            p=Path(td)/'duplicate.json';p.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'Duplicate path'):
                ns['hydrate_bundle'](p,Path(td)/'out',execute=False)

    def test_reject_oversize_raw_bundle_before_json_parse(self):
        ns=notebook_namespace()
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'oversized.json'
            # Intentionally invalid JSON; the size gate must fire before parsing.
            p.write_bytes(b'x'*16_000_001)
            out=Path(td)/'out'
            with self.assertRaisesRegex(ValueError,'Bundle too large'):
                ns['hydrate_bundle'](p,out,execute=False)
            self.assertFalse(out.exists())

    def test_reject_oversize_encoded_file_before_base64_decode(self):
        ns=notebook_namespace()
        with tempfile.TemporaryDirectory() as td:
            bundle={'files':[{'path':'oversized.bin','encoding':'base64',
                               'data':'x'*(4*((2_000_000+2)//3)+1),
                               'sha256':'0'*64}]}
            p=Path(td)/'oversized.json'
            p.write_text(json.dumps(bundle),encoding='utf-8')
            out=Path(td)/'out'
            with self.assertRaisesRegex(ValueError,'Encoded file too large'):
                ns['hydrate_bundle'](p,out,execute=False)
            self.assertFalse(out.exists())

    def test_no_git_push_or_execution_cells(self):
        contents=NOTEBOOK.read_text(encoding='utf-8')
        self.assertNotIn('subprocess.',contents)
        self.assertNotIn('!git push',contents)
        self.assertNotIn('drive.mount(', '\n'.join([line for line in contents.splitlines() if not line.strip().startswith('"#')]))

if __name__=='__main__': unittest.main()
