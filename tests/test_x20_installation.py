"""Complete-profile installation, outside-directory compilation and failure probes."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from tests.test_x20_foundation import ROOT, module


class AllProfileInventoryTests(unittest.TestCase):
    def test_all_17_classes_are_registered(self):
        catalogue = json.loads((ROOT / 'docs/design/X20-Template-Catalogue.json').read_text())
        expected = {p['style_id']: p['proposed_class'] for p in catalogue['profiles']}
        actual = {s: p['class'] for s, p in module('profile_registry').load_profiles(ROOT).items()}
        self.assertEqual(expected, actual)

    def test_new_profiles_reject_epub_before_running_conversion(self):
        from types import SimpleNamespace
        builder = module('profile_build')
        args = SimpleNamespace(source=ROOT / 'examples/profiles/c20.tex',
                               out=ROOT / 'build/x20/reject-epub', target='epub', max_runs=3, verify=True)
        report = builder.build_profile(args)
        self.assertEqual('failed', report['status'])
        self.assertIn('OUTPUT_UNSUPPORTED', report['diagnostics'][0]['code'])
        self.assertEqual({}, report['targets'])


@unittest.skipUnless(os.environ.get('WODTEX_X20_RENDER'), 'Set WODTEX_X20_RENDER=1 for installed LuaLaTeX proofs')
class InstalledProfileTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='installed-x20-', dir=ROOT / 'build/x20')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.tree = self.base / 'tree with spaces'
        self.installer = module('install')
        self.installer.install(self.tree, 'corrected', profile_root=ROOT / 'inputs/profiles')
        self.target = self.tree / 'tex/latex/wodtex'
        self.config = self.tree / 'tex/latex/wodtex-local'
        self.command = module('profile_build').latex_command()
        self.env = dict(os.environ)
        self.env['PATH'] = str(Path(self.command).parent) + os.pathsep + self.env.get('PATH', '')
        # Only installed packages/config plus normal distribution resources.
        # No repository package paths or TEXMF registration are involved.
        self.env['TEXINPUTS'] = os.pathsep.join((str(self.target), str(self.config), ''))

    def compile(self, style, source, error=None):
        work = self.base / ('external manuscript ' + style)
        work.mkdir(exist_ok=True)
        (work / 'book.tex').write_text(source, encoding='utf-8')
        result = subprocess.run([self.command, '--disable-installer', '-no-shell-escape', '-interaction=nonstopmode',
                                 '-halt-on-error', 'book.tex'], cwd=work, env=self.env, capture_output=True, timeout=180)
        evidence = ROOT / 'build/x20/installed-specimens'
        evidence.mkdir(exist_ok=True)
        (evidence / (style + '.stdout')).write_bytes(result.stdout + result.stderr)
        if error:
            self.assertNotEqual(0, result.returncode)
            self.assertIn(error, (result.stdout + result.stderr).decode(errors='replace'))
        else:
            self.assertEqual(0, result.returncode, (result.stdout + result.stderr).decode(errors='replace')[-2500:])
            shutil.copy2(work / 'book.pdf', evidence / (style + '.pdf'))
        return work

    def test_all_classes_compile_from_installed_tree_and_updates_preserve_configuration(self):
        import fitz
        configs = {p.name: p.read_bytes() for p in self.config.iterdir()}
        managed = {p.name: p.read_bytes() for p in self.target.iterdir()}
        profiles = module('profile_registry').load_profiles(ROOT)
        for style, profile in profiles.items():
            with self.subTest(style=style):
                source = ('\\documentclass{' + profile['class'] + '}\n\\title{Installed Specimen}\n'
                          '\\author{Author}\n\\begin{document}\n\\mainmatter\n'
                          '\\chapter{Installed Chapter}\nInstalledMarker-' + style + '\n'
                          '\\begin{sidebar}[id=installed-note]{Installed Note}Conserved installed sidebar.\\end{sidebar}\n'
                          '\\end{document}\n')
                work = self.compile(style, source)
                with fitz.open(work / 'book.pdf') as pdf:
                    text = ''.join(p.get_text() for p in pdf)
                    self.assertIn('Conserved installed sidebar.', text)
                    self.assertIn('InstalledMarker-', text)
                    self.assertEqual('Installed Specimen', pdf.metadata['title'])
                log = (work / 'book.log').read_text(errors='replace')
                self.assertNotIn('Missing character:', log)
        self.installer.install(self.tree, 'corrected')
        self.assertEqual(configs, {p.name: p.read_bytes() for p in self.config.iterdir()})
        self.assertEqual(managed, {p.name: p.read_bytes() for p in self.target.iterdir()})

    def test_invalid_ids_missing_art_and_unsupported_hosts_fail(self):
        prefix = '\\documentclass{wodbook}\\begin{document}\\mainmatter\\chapter{Probe}'
        probes = {
            'duplicate-id': ('\\begin{sidebar}[id=same]{One}A\\end{sidebar}\\begin{sidebar}[id=same]{Two}B\\end{sidebar}', 'WODTEX_E_DUPLICATE_ID'),
            'invalid-id': ('\\begin{sidebar}[id=bad id]{One}A\\end{sidebar}', 'WODTEX_E_INVALID_ID'),
            'missing-art': ('\\artreserve[image={missing.png}]', 'WODTEX_E_IMAGE_MISSING'),
            'unknown-style': ('\\wodtexDispatchStyle{missing}{sidebar}{}{Title}{Text}', 'WODTEX_E_CAPABILITY'),
            'anchored-art': ('\\artreserve[position=outer]', 'WODTEX_E_POSITION_UNSUPPORTED'),
        }
        for name, (body, error) in probes.items():
            with self.subTest(name=name):
                self.compile(name, prefix + body + '\\end{document}', error)

    def test_long_sidebar_and_table_conserve_rows_and_repeat_headers(self):
        import fitz
        paragraphs = '\n\n'.join('NarrativeToken' + str(i) + ' ' + 'A long sidebar paragraph with measured body typography. ' * 18 for i in range(40))
        rows = '\n'.join('RowToken' + str(i) + ' & Value \\\\' for i in range(150))
        source = ('\\documentclass{wodbook}\\begin{document}\\mainmatter\\chapter{Continuation Probe}'
                  '\\begin{sidebarwide}[id=long-note]{LongSidebarTitle}' + paragraphs + '\\end{sidebarwide}'
                  '\\begin{booktable}[id=long-records,head-rows=1]{ll}RepeatedHeader & Value \\\\' + rows + '\\end{booktable}'
                  '\\end{document}')
        work = self.compile('long-continuations', source)
        with fitz.open(work / 'book.pdf') as pdf:
            text = ''.join(p.get_text() for p in pdf)
            self.assertGreater(len(pdf), 5)
            self.assertGreater(text.count('LongSidebarTitle'), 1)
            self.assertGreater(text.count('RepeatedHeader'), 1)
            for token in ('NarrativeToken39', 'RowToken149'):
                self.assertEqual(1, text.count(token))

    def test_next_page_label_and_vertical_art(self):
        source = (r'\documentclass{wodbook}\begin{document}\mainmatter\chapter{Placement}'
                  r'Before placement.\begin{sidebarwide}[id=next-note,place=next-page]{Next Note}'
                  r'After placement.\end{sidebarwide}\artreserve[kind=vertical,id=portrait]'
                  r'\end{document}')
        work = self.compile('placement', source)
        self.assertIn(r'\newlabel{next-note}{{1}{2}', (work / 'book.aux').read_text())


if __name__ == '__main__':
    unittest.main()
