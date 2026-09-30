"""Actual LuaLaTeX shipout and tex4ebook smoke proofs, not source-shape tests."""
import importlib.util
import json
import os
import shutil
import subprocess
import unittest
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from tests.support import ROOT

OUT = ROOT / 'build/task2-proof'


def compile_source(source, name='layout-proof', success=True):
    assert (ROOT / 'm20book.cls').is_file(), 'shared class implementation required'
    spec = importlib.util.spec_from_file_location('m20proof_preflight', ROOT / 'scripts/preflight.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    env = os.environ.copy()
    env.update({k: str(v) for k, v in m.runtime_environment(ROOT / '.runtime').items() if k != 'shell_escape'})
    env['TEXINPUTS'] = str(ROOT) + ':' + str(ROOT/'epub') + ':'
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / (name + '.tex')
    path.write_text(source)
    command = [shutil.which('lualatex'), '-no-shell-escape', '-interaction=nonstopmode', '-halt-on-error', '-output-directory=' + str(OUT), str(path)]
    for _ in range(2 if success else 1):
        p = subprocess.run(command, cwd=ROOT, env=env, text=True, capture_output=True, timeout=120)
        if p.returncode:
            break
    if success:
        assert p.returncode == 0, p.stdout[-14000:] + p.stderr
    return p, OUT / name


def positions(path):
    result = []
    for line in path.with_suffix('.m20pos').read_text().splitlines():
        p = line.split('|')
        if len(p) >= 10:
            result.append(dict(id=p[0], page=int(p[1]), x=int(p[2])/65536/1.00375,
                               y=792-int(p[3])/65536/1.00375, width=int(p[4])/65536/1.00375,
                               usable=int(p[5])/65536/1.00375, columns=int(p[6]),
                               kind=p[7], segment=int(p[8]), placement=p[9],
                               height=float(p[10])/65536/1.00375 if len(p)>10 else 0))
    return result


class LayoutProofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.compile_error = None
        try:
            _, cls.path = compile_source((ROOT / 'examples/layout-proof.tex').read_text())
            conversion = subprocess.run(['python3',str(ROOT/'scripts/build.py'),'--target','epub',
                                         '--source',str(ROOT/'examples/layout-proof.tex'),
                                         '--out',str(OUT/'converted')],cwd=ROOT,text=True,capture_output=True,timeout=240)
            assert conversion.returncode == 0, conversion.stdout + conversion.stderr
            shutil.copyfile(OUT/'converted/epub/layout-proof.epub',OUT/'layout-proof.epub')
            cls.p = positions(cls.path)
            cls.text = subprocess.check_output(['pdftotext', '-layout', str(cls.path.with_suffix('.pdf')), '-'], text=True)
        except (AssertionError, FileNotFoundError) as exc:
            cls.compile_error = str(exc)

    def setUp(self):
        self.assertIsNone(self.compile_error, self.compile_error)

    def segments(self, id):
        return [p for p in self.p if p['id'] == id and p['kind'] == 'sidebar']

    def test_three_sidebar_layouts(self):
        for id, columns, width in [('long-narrow', 1, 239.2248), ('long-wide1', 1, 490.4496), ('long-wide2', 2, 490.4496)]:
            s = self.segments(id)
            self.assertGreaterEqual(len(s), 2, id + ' must genuinely continue')
            self.assertTrue(all(abs(p['width']-width) < .02 and p['columns'] == columns for p in s))
            self.assertIn(id.upper() + '-END', self.text)
        wide = self.segments('long-wide2')
        table = [p for p in self.p if p['id'] == 'wide2-table']
        self.assertEqual(len(table), 1)
        self.assertGreater(table[0]['usable'], 400)
        self.assertIn('TABLE-BETWEEN-SEGMENTS', self.text)

    def test_forced_here_all_variants(self):
        for id in ('here-narrow', 'here-wide1', 'here-wide2'):
            anchor = next(p for p in self.p if p['id'] == id + '-anchor')
            segment = self.segments(id)[0]
            self.assertEqual(segment['page'], anchor['page'], id)
            self.assertLess(abs(segment['y']-anchor['y']), 32, id)
            self.assertEqual(segment['placement'], 'here')

    def test_forced_next_page_all_variants(self):
        for id in ('next-narrow', 'next-wide1', 'next-wide2'):
            before = next(p for p in self.p if p['id'] == id + '-before')
            segment = self.segments(id)[0]
            self.assertEqual(segment['page'], before['page'] + 1, id)
            self.assertLess(segment['y'], 95, id)

    def test_first_segment_cannot_fit_errors(self):
        for env, opt in [('m20sidebar',''), ('m20sidebarwide','columns=1,'), ('m20sidebarwide','columns=2,')]:
            source = r'\documentclass{m20book}\begin{document}\m20bodyend\null\vspace*{640bp}' + '\\begin{' + env + '}[' + opt + 'place=here]{Impossible}Required first paragraph.\\end{' + env + '}\\end{document}'
            p, path = compile_source(source, 'error-' + env + opt.replace(',','').replace('=',''), False)
            self.assertNotEqual(p.returncode, 0)
            self.assertIn('M20_E_PLACEMENT_UNAVAILABLE', p.stdout)

    def test_spanning_heading(self):
        heading = next(p for p in self.p if p['id'] == 'span-heading')
        self.assertAlmostEqual(heading['width'], 490.4496, places=2)
        self.assertIn('A Heading Across Both Columns', self.text)

    def test_body_color_recovers_after_long_sidebar(self):
        import fitz
        with fitz.open(self.path.with_suffix('.pdf')) as document:
            spans = [s for page in document for b in page.get_text('dict',flags=fitz.TEXTFLAGS_DICT & ~fitz.TEXT_PRESERVE_IMAGES)['blocks'] if 'lines' in b
                     for line in b['lines'] for s in line['spans']]
        following = [s for s in spans if 'Wide-one preceding body' in s['text']]
        self.assertTrue(following)
        self.assertTrue(all(s['color'] == 0 for s in following), following)

    def test_measurement_is_side_effect_free(self):
        self.assertEqual(self.text.count('BODY-NOTE-ONCE'), 1)
        self.assertEqual(self.text.count('SIDEBAR-NOTE-ONCE'), 1)
        aux = self.path.with_suffix('.aux').read_text()
        self.assertEqual(aux.count(r'\newlabel{proof:once}'), 1)
        self.assertEqual(self.path.with_suffix('.idx').read_text().count('MEASURED-INDEX-ONCE'), 1)
        marker = next(p for p in self.p if p['id'] == 'right-column-note')
        self.assertGreater(marker['x'], 300)

    def test_epub_retains_aside_order_and_content(self):
        epub = OUT / 'layout-proof.epub'
        self.assertTrue(epub.exists(), 'real tex4ebook conversion required')
        with zipfile.ZipFile(epub) as z:
            html = '\n'.join(z.read(n).decode() for n in z.namelist() if n.endswith(('.xhtml','.html')))
            ids = {e.get('id') for n in z.namelist() if n.endswith(('.xhtml','.html'))
                   for e in ET.fromstring(z.read(n)).iter() if e.get('id')}
        for id in ('long-narrow', 'long-wide1', 'long-wide2'):
            self.assertIn(id.upper() + '-END', html)
            self.assertIn(id, ids)
        self.assertEqual(html.count('SIDEBAR-NOTE-ONCE'), 1)
        self.assertIn('<aside', html)
        self.assertIn('TABLE-BETWEEN-SEGMENTS', html)
