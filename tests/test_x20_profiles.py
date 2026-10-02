"""Descriptor, installed-tree and real-font proofs for every present X20 family."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from tests.test_x20_foundation import ROOT, module


class X20ProfileTests(unittest.TestCase):
    def test_prepared_frames_have_no_template_text(self):
        import fitz
        for style in module('profile_registry').load_profiles(ROOT):
            if style == 'm20':
                continue
            for name in ('body-left', 'body-right'):
                frame = ROOT / 'inputs/profiles' / style / (name + '.pdf')
                if frame.exists():
                    with fitz.open(frame) as pdf:
                        self.assertFalse(''.join(p.get_text() for p in pdf).strip(), (style, name))

    def test_descriptors_have_distinct_classes_and_reference_backed_resources(self):
        profiles = module('profile_registry').load_profiles(ROOT)
        for style, profile in profiles.items():
            if style == 'm20':
                continue
            with self.subTest(style=style):
                source = (ROOT / (profile['class'] + '.cls')).read_text()
                self.assertIn('\\def\\wodtexProfileId{' + style + '}', source)
                self.assertNotIn('\\LoadClass{m20book}', source)
                self.assertEqual(['pdf'], profile['outputs'])
                self.assertTrue(profile['source_measurements'])
                self.assertEqual(64, len(profile['reference']['sha256']))
                self.assertTrue(all(len(f['sha256']) == 64 for f in profile['fonts'].values()))
                self.assertTrue((ROOT / 'examples/profiles' / (style + '.tex')).exists())
        files = module('install').payload('corrected')
        for profile in profiles.values():
            self.assertIn(profile['class'] + '.cls', files)

    @unittest.skipUnless(os.environ.get('WODTEX_X20_RENDER'), 'Set WODTEX_X20_RENDER=1 with LuaLaTeX to run native proofs')
    def test_each_profile_compiles_with_genuine_fonts_and_conserved_content(self):
        import fitz
        from types import SimpleNamespace
        build = module('profile_build')
        profiles = module('profile_registry').load_profiles(ROOT)
        selected = os.environ.get('WODTEX_X20_STYLES', '').split(',')
        for style, profile in profiles.items():
            if style == 'm20' or selected != [''] and style not in selected:
                continue
            with self.subTest(style=style):
                args = SimpleNamespace(source=ROOT / 'examples/profiles' / (style + '.tex'),
                                       out=ROOT / 'build/x20/proofs' / style, target='pdf', max_runs=8, verify=True)
                result = build.build_profile(args)
                self.assertEqual('passed', result['status'], result['diagnostics'])
                pdf_path = Path(result['targets']['pdf']['output'])
                with fitz.open(pdf_path) as pdf:
                    text = ''.join(p.get_text() for p in pdf)
                    for sentence in ('Conserved sidebar text', 'After the explicit continuation.', 'Conserved cell', 'Later body text', 'Scene caption', 'Artist credit'):
                        self.assertEqual(1, text.count(sentence), (style, sentence))
                    self.assertTrue(any(p.get_links() for p in pdf), 'TOC/reference links must survive')
                    self.assertEqual(style + ' Specimen', pdf.metadata['title'])
                    spans = [s for p in pdf for b in p.get_text('dict')['blocks'] for line in b.get('lines', []) for s in line['spans']]
                    normalize = lambda x: ''.join(c.lower() for c in x if c.isalnum())
                    expected = normalize(profile['fonts']['body']['postscript'])
                    self.assertTrue(any(expected == normalize(s['font']) for s in spans), (style, {s['font'] for s in spans}))
                    for i, page in enumerate(pdf):
                        page.get_pixmap(matrix=fitz.Matrix(.6,.6)).save(pdf_path.parent / ('page-' + str(i + 1) + '.png'))


if __name__ == '__main__':
    unittest.main()
