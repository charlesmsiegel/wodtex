"""Failure contracts found by review of profile preparation and build routing."""
import hashlib
import json
from pathlib import Path
import tempfile
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from tests.test_x20_foundation import ROOT, module


class ReviewRegressionTests(unittest.TestCase):
    def test_rebuild_removes_index_files_before_first_tex_pass(self):
        builder = module('profile_build')
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / 'book.tex'
            source.write_text(r'\documentclass{demobook}')
            out = root / 'build/proof'
            work = out / 'pdf'
            work.mkdir(parents=True)
            for suffix in ('.idx', '.ind', '.ilg'):
                (work / ('book' + suffix)).write_text('stale index')
            def render(*args, **kwargs):
                self.assertFalse((work / 'book.ind').exists())
                self.assertFalse((work / 'book.idx').exists())
                (work / 'book.log').write_text('successful rendering')
                (work / 'book.pdf').write_bytes(b'proof')
                return SimpleNamespace(returncode=0, stdout=b'', stderr=b'')
            profile = {'style_id': 'demo', 'class': 'demobook', 'outputs': ['pdf']}
            args = SimpleNamespace(source=source, out=out, target='pdf', verify=False, max_runs=3)
            with patch.object(builder, 'profile_for_class', return_value=profile), patch.object(builder, 'verify_resources', return_value={}), patch.object(builder, 'latex_command', return_value='lualatex'), patch.object(builder.subprocess, 'run', side_effect=render):
                self.assertEqual('passed', builder.build_profile(args, root)['status'])

    def test_resource_manifest_cannot_omit_or_replace_required_fonts(self):
        preparer = module('prepare_profile')
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'profiles').mkdir()
            data = b'genuine font bytes'
            expected = hashlib.sha256(data).hexdigest()
            profile = {'kind': 'wodtex-output-profile', 'schema_version': 1,
                       'style_id': 'demo', 'class': 'demobook', 'outputs': ['pdf'],
                       'fonts': {'body': {'path': 'font.ttf', 'sha256': expected}},
                       'reference': {'sha256': 'source'}, 'border_pages': {}}
            (root / 'profiles/demo.json').write_text(json.dumps(profile))
            base = root / 'resources/demo'
            base.mkdir(parents=True)
            (base / 'body.ttf').write_bytes(data)
            manifest = {'schema_version': 1, 'style_id': 'demo',
                        'preparation_sha256': preparer.preparation_hash(profile),
                        'reference_sha256': 'source', 'files': {'body.ttf': expected}}
            def save():
                (base / 'resources.json').write_text(json.dumps(manifest))
            save()
            preparer.verify_resources('demo', root / 'resources', root)
            changed = dict(profile, border_exclusions={'body-left': [[0, 0, 1, 1]]})
            (root / 'profiles/demo.json').write_text(json.dumps(changed))
            with self.assertRaisesRegex(ValueError, 'RESOURCE_MANIFEST'):
                preparer.verify_resources('demo', root / 'resources', root)
            (root / 'profiles/demo.json').write_text(json.dumps(profile))
            manifest['files'] = {}
            save()
            with self.assertRaisesRegex(ValueError, 'RESOURCE_MANIFEST'):
                preparer.verify_resources('demo', root / 'resources', root)
            substitute = b'replacement font'
            (base / 'body.ttf').write_bytes(substitute)
            manifest['files'] = {'body.ttf': hashlib.sha256(substitute).hexdigest()}
            save()
            with self.assertRaisesRegex(ValueError, 'RESOURCE_FONT'):
                preparer.verify_resources('demo', root / 'resources', root)

    def test_invalid_class_never_falls_through_to_m20_preflight(self):
        with patch.object(sys, 'path', [str(ROOT / 'scripts'), *sys.path]):
            builder = module('build')
        with tempfile.TemporaryDirectory(dir=ROOT / 'build') as temporary:
            base = Path(temporary)
            source = base / 'book.tex'
            args = SimpleNamespace(source=source, out=base / 'out', target='pdf')
            for content, code in [(r'\documentclass{unknownbook}', 'UNKNOWN_CLASS'),
                                  (r'\documentclass{wodbook}\documentclass{wodbook}', 'DOCUMENT_CLASS')]:
                source.write_text(content)
                with patch.object(sys, 'path', [str(ROOT / 'scripts'), *sys.path]), patch.object(builder, 'preflight', side_effect=AssertionError('M20 fallback')):
                    result = builder.build(args)
                self.assertEqual('failed', result['status'])
                self.assertIn(code, result['diagnostics'][0]['code'])


if __name__ == '__main__':
    unittest.main()
