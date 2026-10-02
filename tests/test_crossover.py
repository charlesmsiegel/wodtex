"""PDF component crossover: public routing and installed rendering behavior."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
STYLES = {
    'm20': 'm20', 'm20-dark-ages': 'm20darkages', 'msc': 'msc',
    'v20-clanbook': 'v20clanbook', 'vva20': 'vva20',
    'vva20-clanbook': 'vva20clanbook', 'w20': 'w20',
    'w20-dark-ages': 'w20darkages', 'w20-wyld-west': 'w20wyldwest',
    'c20': 'c20', 'dark-ages-fae': 'darkagesfae', 'd20': 'd20',
    'wr20': 'wr20', 'kote20-dharmabook': 'kote20dharmabook',
    'kotek20': 'kotek20', 'kotek20-legacybook': 'kotek20legacybook',
    'wod': 'wod',
}


@unittest.skipUnless(shutil.which('pdflatex'), 'pdfLaTeX required')
class PrefixRoutingTests(unittest.TestCase):
    def compile(self, body, extra='', error=None):
        with tempfile.TemporaryDirectory(prefix='crossover-routing-') as directory:
            work = Path(directory)
            source = r'''\documentclass{article}
\usepackage{tex/wodtex-registry}
\newcommand\fixtureSidebar[3]{\typeout{ROUTE:\wodtexActiveStyle:#2}#3}
\newcommand\fixtureTable[3]{\typeout{TABLE:\wodtexActiveStyle:#2}#3}
\newcommand\fixtureBreak[1]{\typeout{BREAK:\wodtexActiveStyle:#1}}
\newcommand\fixtureEntry[1]{\typeout{ENTRY:\wodtexActiveStyle:#1}}
\newcommand\fixtureArt[2]{\typeout{ART:\wodtexActiveStyle:#1}}
\newcommand\fixtureBody[1]{#1}
\newcommand\fixtureNoop{}
'''
            for style in STYLES:
                for capability, command in {
                    'sidebar': 'fixtureSidebar', 'sidebarwide': 'fixtureSidebar',
                    'booktable': 'fixtureTable', 'sidebarbreak': 'fixtureBreak',
                    'statentry': 'fixtureEntry', 'artreserve': 'fixtureArt',
                    'tablelead': 'fixtureBody', 'statblock': 'fixtureBody',
                }.items():
                    source += '\\wodtexRegisterRenderer{' + style + '}{' + capability + '}{' + command + '}\n'
                for env in ('sidebar', 'sidebarwide', 'booktable', 'tablelead', 'statblock'):
                    for hook in ('before', 'after'):
                        source += '\\wodtexRegisterRenderer{' + style + '}{' + env + '-' + hook + '}{fixtureNoop}\n'
            source += r'\wodtexSetClassStyle{w20}' + extra + r'\usepackage{tex/wodtex-prefixes}'
            # Generic dispatch uses the same public nesting contract as the classes.
            source += r'''\NewDocumentEnvironment{booktable}{O{}m+b}{\wodtexSelectElement\wodtexDispatch{booktable}{#1}{#2}{#3}}{}
\begin{document}''' + body + r'\end{document}'
            (work / 'probe.tex').write_text(source)
            env = dict(os.environ, TEXINPUTS=str(ROOT) + '//:' + os.environ.get('TEXINPUTS', ''))
            result = subprocess.run(['pdflatex', '-interaction=nonstopmode', '-halt-on-error', 'probe.tex'],
                                    cwd=work, env=env, text=True, capture_output=True, timeout=60)
            if error:
                self.assertNotEqual(0, result.returncode)
                self.assertIn(error, result.stdout)
            else:
                self.assertEqual(0, result.returncode, result.stdout[-5000:])
            return result.stdout

    def test_all_prefixes_select_the_named_style_and_restore_host(self):
        body = ''
        for style, prefix in STYLES.items():
            body += ('\\begin{' + prefix + 'sidebar}{' + style + '}'
                     '\\begin{booktable}{ll}cell\\end{booktable}'
                     '\\' + prefix + 'sidebarbreak[column]'
                     '\\' + prefix + 'statentry{entry}'
                     '\\end{' + prefix + 'sidebar}\n')
        body += r'\wodtexSelectElement\wodtexDispatch{sidebar}{}{host}{host text}'
        log = self.compile(body)
        for style in STYLES:
            self.assertIn('ROUTE:' + style + ':' + style, log)
            self.assertIn('TABLE:' + style + ':ll', log)
            self.assertIn('BREAK:' + style + ':column', log)
            self.assertIn('ENTRY:' + style + ':entry', log)
        self.assertIn('ROUTE:w20:host', log)

    def test_latex_accents_and_legacy_m20_commands_survive(self):
        extra = r'\ExplSyntaxOn\cs_new_protected:cpn{mTwentyPublicnote}#1{\typeout{LEGACY:#1}}\cs_new_protected:Npn\m20{}\ExplSyntaxOff'
        log = self.compile(r'\c{c} \d{d} \v{s} \c c \v s \m20note{kept}\c20statentry{changeling}\v20clanbookstatentry{vampire}', extra)
        self.assertIn('LEGACY:kept', log)
        self.assertIn('ENTRY:c20:changeling', log)
        self.assertIn('ENTRY:v20-clanbook:vampire', log)

    def test_command_selection_is_local_even_inside_another_style(self):
        log = self.compile(r'\begin{m20sidebar}{Mage}\w20statentry{wolf}\statentryprobe\end{m20sidebar}',
                           r'\newcommand\statentryprobe{\wodtexDispatch{statentry}{mage}}')
        self.assertIn('ENTRY:w20:wolf', log)
        self.assertIn('ENTRY:m20:mage', log)

    def test_unknown_numeric_command_has_a_clear_error(self):
        self.compile(r'\w20unknown{value}', error='WODTEX_E_UNKNOWN_COMMAND')

    def test_prefixed_environment_collisions_are_not_silently_accepted(self):
        self.compile('text', extra=r'\newenvironment{mscsidebar}{}{}', error='WODTEX_E_NAME_COLLISION')


@unittest.skipUnless(os.environ.get('WODTEX_CROSSOVER_RENDER'),
                     'Set WODTEX_CROSSOVER_RENDER=1 for installed LuaLaTeX proofs')
class InstalledCrossoverTests(unittest.TestCase):
    """Synthetic host resources verify isolation, not original profile fidelity."""
    @classmethod
    def setUpClass(cls):
        from scripts import install
        import fitz
        cls.temp = tempfile.TemporaryDirectory(prefix='wodtex-crossover-')
        cls.base = Path(cls.temp.name)
        cls.tree = cls.base / 'user texmf'
        cls.resources = cls.base / 'profile resources'
        fonts = Path(os.environ.get('WODTEX_TEST_PROFILE_FONTS', str(ROOT / 'fonts')))
        otf_fonts = Path(os.environ.get('WODTEX_TEST_OTF_FONTS', '/usr/share/texmf/fonts/opentype/public/lm'))
        for style in STYLES:
            if style == 'm20':
                continue
            destination = cls.resources / style
            destination.mkdir(parents=True)
            for target, origin in {
                'body.ttf': 'DejaVuSans.ttf', 'bold.ttf': 'DejaVuSans-Bold.ttf',
                'italic.ttf': 'DejaVuSans-Oblique.ttf', 'bolditalic.ttf': 'DejaVuSans-BoldOblique.ttf',
                'heading.ttf': 'DejaVuSans.ttf', 'chapter.ttf': 'DejaVuSans.ttf',
            }.items():
                shutil.copy2(fonts / origin, destination / target)
            # Prepared profiles retain source font formats; use genuine OTF
            # fixtures for the profiles whose measured faces are OpenType.
            for target, origin in {
                'body.otf': 'lmroman10-regular.otf', 'bold.otf': 'lmroman10-bold.otf',
                'italic.otf': 'lmroman10-italic.otf', 'bolditalic.otf': 'lmroman10-bolditalic.otf',
                'heading.otf': 'lmsans10-regular.otf', 'chapter.otf': 'lmsans10-regular.otf',
            }.items():
                shutil.copy2(otf_fonts / origin, destination / target)
            for side in ('left', 'right'):
                with fitz.open() as pdf:
                    pdf.new_page(width=612, height=792)
                    pdf.save(destination / ('body-' + side + '.pdf'))
        install.install(cls.tree, 'corrected',
                        font_dir=Path(os.environ.get('WODTEX_TEST_M20_FONTS', str(ROOT / 'fonts'))),
                        asset_dir=Path(os.environ.get('WODTEX_TEST_M20_ASSETS', str(ROOT / 'assets'))),
                        profile_root=cls.resources)
        cls.env = dict(os.environ)
        # Font-loader caches record absolute filenames. Keep synthetic copies
        # isolated from earlier temporary fixtures with identical file times.
        cache = cls.base / 'font cache'
        cache.mkdir()
        cls.env['TEXMFCACHE'] = str(cache)
        # An existing TEXMFHOME can supply a minimal distribution's font loader.
        cls.env['TEXINPUTS'] = str(cls.tree) + '//:' + cls.env.get('TEXINPUTS', '')
        cls.env['LUAINPUTS'] = str(cls.tree) + '//:' + cls.env.get('LUAINPUTS', '')

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def compile(self, source, name, error=None):
        work = self.base / name
        work.mkdir()
        (work / 'book.tex').write_text('\\errorcontextlines=120\n' + source)
        for _ in range(1 if error else 2):
            result = subprocess.run(['lualatex', '-interaction=nonstopmode', '-halt-on-error', 'book.tex'],
                                    cwd=work, env=self.env, text=True, capture_output=True, timeout=90)
            if error:
                self.assertNotEqual(0, result.returncode)
                self.assertIn(error, result.stdout[-8000:])
            else:
                self.assertEqual(0, result.returncode, result.stdout[-8000:])
        evidence = ROOT / 'build/crossover' / name
        evidence.mkdir(parents=True, exist_ok=True)
        for path in work.glob('book.*'):
            shutil.copy2(path, evidence / path.name)
        return work

    def test_m20_sidebar_in_w20_keeps_fonts_nested_content_and_host_layout(self):
        import fitz
        source = r'''\documentclass{w20book}
\title{HostRunner}
\begin{document}\mainmatter\chapter{Mixtures}
HostBefore.\typeout{HOST-BEFORE:\the\textwidth,\the\columnsep}
\begin{m20sidebarwide}[id=mage-note]{MageAside}
MageFirst.\footnote{ConservedFootnote.}
\begin{booktable}[id=mage-table]{ll}Key & Value \\ CellToken & Detail \\\end{booktable}
\begin{w20table}{ll}WolfCell & Host styled \\\end{w20table}
\sidebarbreak[page]
MageSecond.
\end{m20sidebarwide}
\typeout{HOST-AFTER:\the\textwidth,\the\columnsep}
HostAfter.
\begin{sidebarwide}[id=wolf-note]{WolfAside}WolfBody.\end{sidebarwide}
\end{document}'''
        work = self.compile(source, 'mage-in-wolf')
        with fitz.open(work / 'book.pdf') as pdf:
            text = ''.join(page.get_text() for page in pdf)
            for token in ('HostBefore.', 'MageFirst.', 'CellToken', 'ConservedFootnote.', 'MageSecond.', 'HostAfter.', 'WolfBody.'):
                self.assertEqual(1, text.count(token), token)
            self.assertIn('(continued)', text)
            spans = [span for page in pdf for block in page.get_text('dict')['blocks']
                     for line in block.get('lines', []) for span in line['spans']]
            def matching(token):
                return [span for span in spans if token in span['text']]
            for token in ('MageFirst.', 'MageSecond.', 'CellToken'):
                self.assertTrue(any('Goudy' in span['font'] for span in matching(token)), matching(token))
            self.assertTrue(any('Abbess' in span['font'] for span in matching('MageAside')))
            for token in ('HostBefore.', 'HostAfter.', 'WolfBody.', 'HostRunner', 'WolfCell'):
                self.assertTrue(all('DejaVuSans' in span['font'] for span in matching(token)), matching(token))
            for page in pdf:
                self.assertAlmostEqual(612, page.rect.width, places=1)
                self.assertAlmostEqual(792, page.rect.height, places=1)
        log = (work / 'book.log').read_text()
        import re
        self.assertEqual(re.search(r'HOST-BEFORE:(.*)', log).group(1),
                         re.search(r'HOST-AFTER:(.*)', log).group(1))
        aux = (work / 'book.aux').read_text()
        self.assertIn(r'\newlabel{mage-note}', aux)
        self.assertIn(r'\newlabel{mage-table}', aux)

    def test_foreign_profile_sidebar_in_m20_restores_body(self):
        import fitz
        source = r'''\documentclass{m20book}
\title{MageHost}
\begin{document}\mainmatter\chapter{Mixtures}
MageHostBefore.
\begin{w20sidebarwide}[id=wolf-note]{WolfAside}
WolfForeign.\begin{booktable}{ll}ForeignCell & Detail \\\end{booktable}
\begin{m20table}{ll}MageNestedCell & Mage styled \\\end{m20table}
\end{w20sidebarwide}
MageHostAfter.
\end{document}'''
        work = self.compile(source, 'wolf-in-mage')
        with fitz.open(work / 'book.pdf') as pdf:
            spans = [span for page in pdf for block in page.get_text('dict')['blocks']
                     for line in block.get('lines', []) for span in line['spans']]
            for token, font in (('WolfForeign.', 'DejaVuSans'), ('ForeignCell', 'DejaVuSans'),
                                ('MageHostBefore.', 'Goudy'), ('MageHostAfter.', 'Goudy'), ('MageNestedCell', 'Goudy')):
                matching = [span for span in spans if token in span['text']]
                self.assertTrue(matching, token)
                self.assertTrue(all(font in span['font'] for span in matching), matching)

    def test_foreign_missing_resource_and_invalid_break_are_actionable(self):
        source = r'\documentclass{w20book}\begin{document}'
        self.compile(source + r'\m20sidebarbreak\end{document}', 'outside-break', 'WODTEX_E_BREAK_OUTSIDE_SIDEBAR')
        self.compile(source + r'\begin{m20sidebar}[breakable=false]{Atomic}First.\sidebarbreak Second.\end{m20sidebar}\end{document}',
                     'atomic-break', 'WODTEX_E_ATOMIC_SIDEBAR_BREAK')
        source = (r'\documentclass{w20book}\def\mTwentyBuildFontPath{missing/}\begin{document}'
                  r'\begin{m20sidebar}{Missing}Body.\end{m20sidebar}\end{document}')
        self.compile(source, 'missing-foreign-font', 'WODTEX_E_RESOURCE_MISSING')

    def test_long_foreign_sidebar_and_table_conserve_content(self):
        import fitz
        paragraphs = '\n\n'.join('NarrativeToken' + str(i) + '. ' +
                                  'Measured component prose in the host page area. ' * 14 for i in range(28))
        rows = '\n'.join('RowToken' + str(i) + '.' + (r'\footnote{TableNoteToken.}' if i == 0 else '') + ' & Value \\\\' for i in range(120))
        source = (r'\documentclass{w20book}\begin{document}\mainmatter\chapter{Long Components}'
                  r'\begin{m20sidebarwide}[id=long-mage]{LongMageTitle}' + paragraphs + r'\end{m20sidebarwide}'
                  r'\begin{msctable}[head-rows=1]{ll}RepeatedHeader\footnote{HeaderNoteToken.} & Value \\' + rows + r'\end{msctable}'
                  r'\end{document}')
        work = self.compile(source, 'long-components')
        with fitz.open(work / 'book.pdf') as pdf:
            text = ''.join(page.get_text() for page in pdf)
            self.assertGreater(len(pdf), 4)
            self.assertGreater(text.count('LongMageTitle'), 1)
            self.assertGreater(text.count('RepeatedHeader'), 1)
            self.assertEqual(1, text.count('HeaderNoteToken.'))
            self.assertEqual(1, text.count('TableNoteToken.'))
            for i in range(28):
                self.assertEqual(1, text.count('NarrativeToken' + str(i) + '.'), i)
            for i in range(120):
                self.assertEqual(1, text.count('RowToken' + str(i) + '.'), i)

    def test_all_style_prefixes_render_from_installed_tree(self):
        import fitz
        body = ''
        for style, prefix in STYLES.items():
            body += ('\\begin{' + prefix + 'sidebarwide}{' + prefix + 'Title}'
                     + prefix + 'Body.\\end{' + prefix + 'sidebarwide}\n'
                     '\\begin{' + prefix + 'statblock}\\' + prefix + 'statentry{'
                     + prefix + 'Entry.}\\end{' + prefix + 'statblock}\n')
        work = self.compile(r'\documentclass{w20book}\begin{document}' + body + r'\end{document}', 'all-prefixes')
        with fitz.open(work / 'book.pdf') as pdf:
            text = ''.join(page.get_text() for page in pdf)
            for prefix in STYLES.values():
                self.assertEqual(1, text.count(prefix + 'Body.'), prefix)
                self.assertEqual(1, text.count(prefix + 'Entry.'), prefix)

    def test_foreign_placement_ids_and_host_only_capabilities_fail_clearly(self):
        source = r'\documentclass{w20book}\begin{document}'
        for name, body, error in (
            ('duplicate-mixed-id', r'\begin{sidebar}[id=same]{Host}A\end{sidebar}\begin{m20sidebar}[id=same]{Mage}B\end{m20sidebar}', 'WODTEX_E_DUPLICATE_ID'),
            ('invalid-foreign-id', r'\begin{m20sidebar}[id=bad id]{Mage}A\end{m20sidebar}', 'WODTEX_E_INVALID_ID'),
            ('foreign-page-policy', r'\wodtexDispatchStyle{m20}{maketitle}', 'WODTEX_E_CAPABILITY'),
            ('nested-sidebars', r'\begin{m20sidebarwide}{Mage}\begin{mscsidebar}{Companion}A\end{mscsidebar}\end{m20sidebarwide}', 'WODTEX_E_UNSUPPORTED_NESTING'),
            ('anchored-foreign-art', r'\mscartreserve[position=outer]', 'WODTEX_E_POSITION_UNSUPPORTED'),
            ('contained-next-page', r'\begin{mscsidebarwide}{Parent}\begin{msctable}[place=next-page]{ll}Cell & Value \\\end{msctable}\end{mscsidebarwide}', 'WODTEX_E_CONTAINED_PLACEMENT'),
            ('sidebar-art-option', r'\begin{mscsidebarwide}[image=unused.png]{Parent}Body.\end{mscsidebarwide}', 'WODTEX_E_OPTION'),
            ('table-columns-option', r'\begin{msctable}[columns=2]{ll}Cell & Value \\\end{msctable}', 'WODTEX_E_OPTION'),
            ('art-here-option', r'\mscartreserve[place=here]', 'WODTEX_E_POSITION_UNSUPPORTED'),
            ('duplicate-art-id', r'\mscartreserve{same}\mscartreserve{same}', 'WODTEX_E_DUPLICATE_ID'),
            ('invalid-art-id', r'\mscartreserve{bad id}', 'WODTEX_E_INVALID_ID'),
            ('duplicate-art-alias', r'\mscartreserve[id=first]{same}\mscartreserve[id=second]{same}', 'WODTEX_E_DUPLICATE_ID'),
        ):
            with self.subTest(name=name):
                self.compile(source + body + r'\end{document}', name, error)

    def test_foreign_m20_art_uses_its_frame_and_restores_host(self):
        import fitz
        image = self.base / 'scene.png'
        with fitz.open() as pdf:
            page = pdf.new_page(width=64, height=32)
            page.draw_rect(page.rect, fill=(.5, .2, .1))
            page.get_pixmap().save(image)
        source = (r'\documentclass{w20book}\begin{document}\mainmatter\chapter{Artwork}'
                  r'\m20artreserve[kind=horizontal,image={' + image.as_posix() +
                  r'},caption={MageCaption.},credit={MageCredit.},id=mage-art]{mage-art-alias}'
                  r'ArtHostAfter.\end{document}')
        work = self.compile(source, 'mage-art-in-wolf')
        log = (work / 'book.log').read_text()
        self.assertTrue('art-horizontal.original-template.pdf' in log, 'M20 reference art frame must be included')
        with fitz.open(work / 'book.pdf') as pdf:
            text = ''.join(page.get_text() for page in pdf)
            for token in ('MageCaption.', 'MageCredit.', 'ArtHostAfter.'):
                self.assertEqual(1, text.count(token), token)
        self.assertIn(r'\newlabel{mage-art-alias}', (work / 'book.aux').read_text())

    def test_two_column_foreign_sidebar_breaks_keep_content(self):
        source = (r'\documentclass{w20book}\begin{document}'
                  r'\begin{m20sidebarwide}[columns=2]{Columns}'
                  r'LeftMarker.\sidebarbreak[column]RightMarker.\sidebarbreak[page]NextPageMarker.'
                  r'\end{m20sidebarwide}\end{document}')
        work = self.compile(source, 'two-column-mage')
        import fitz
        with fitz.open(work / 'book.pdf') as pdf:
            text = ''.join(page.get_text() for page in pdf)
            for token in ('LeftMarker.', 'RightMarker.', 'NextPageMarker.'):
                self.assertEqual(1, text.count(token), token)
            self.assertGreater(len(pdf), 1)

    def test_oversized_atomic_fragments_fail_instead_of_clipping(self):
        paragraphs = '\n\n'.join('OverflowToken' + str(i) + '. ' +
                                    'Long column prose fills a sidebar across many pages. ' * 14
                                    for i in range(40))
        for name, options in (('two-column-overflow', 'columns=2'),
                              ('atomic-overflow', 'breakable=false')):
            with self.subTest(name=name):
                source = (r'\documentclass{w20book}\begin{document}'
                          r'\begin{m20sidebarwide}[' + options + ']{Oversized}' +
                          paragraphs + r'\end{m20sidebarwide}\end{document}')
                self.compile(source, name, 'WODTEX_E_SIDEBAR_FRAGMENT_TOO_TALL')

    def test_automatic_placement_labels_follow_the_component(self):
        import fitz
        import re
        for name, body, token in (
            ('moved-sidebar', r'\begin{mscsidebarwide}[breakable=false,id=moved]{MovedTitle}MovedBody.\par\vspace{50bp}\end{mscsidebarwide}', 'MovedBody.'),
            ('moved-art', r'\mscartreserve[id=moved,caption=MovedCaption.]', 'Artwork reservation'),
            ('moved-table', r'\begin{msctable}[id=moved]{ll}MovedHeader & Value \\ MovedRow & Data \\\end{msctable}', 'MovedHeader'),
        ):
            with self.subTest(name=name):
                source = (r'\documentclass{w20book}\begin{document}Before.\par\vspace*{.99\textheight}' +
                          body + r'See \pageref{moved}.\end{document}')
                work = self.compile(source, name)
                with fitz.open(work / 'book.pdf') as pdf:
                    pages = [i + 1 for i, page in enumerate(pdf) if token in page.get_text()]
                    self.assertTrue(pages, token)
                    self.assertGreater(pages[0], 1)
                    if name == 'moved-art':
                        frame_page = pdf[pages[0] - 1]
                        frames = frame_page.get_drawings()
                        self.assertTrue(frames, 'Art frame must be visible')
                        self.assertTrue(all(drawing['rect'].y1 <= frame_page.rect.height for drawing in frames),
                                        [drawing['rect'] for drawing in frames])
                aux = (work / 'book.aux').read_text()
                page = int(re.search(r'\\newlabel\{moved\}\{\{[^}]*\}\{(\d+)\}', aux).group(1))
                self.assertEqual(pages[0], page, aux)

    def test_nested_table_and_native_m20_lead_keep_column_ownership(self):
        import fitz
        cases = (
            ('nested-stat-table', r'\documentclass{w20book}\begin{document}\mainmatter\chapter{Nested}'
             r'Before.\begin{mscstatblock}StatBefore.\begin{msctable}{ll}ContainedCell & Value \\\end{msctable}StatAfter.\end{mscstatblock}HostReturn.\end{document}',
             ('StatBefore.', 'ContainedCell', 'StatAfter.', 'HostReturn.')),
            ('native-lead-contained', r'\documentclass{m20book}\begin{document}\mainmatter\chapter{Nested}'
             r'Before.\begin{w20sidebarwide}{Wolf}\begin{m20tablelead}MageLead.\begin{m20table}{ll}LeadCell & Value \\\end{m20table}\end{m20tablelead}WolfAfter.\end{w20sidebarwide}HostReturn.\end{document}',
             ('MageLead.', 'LeadCell', 'WolfAfter.', 'HostReturn.')),
        )
        for name, source, tokens in cases:
            with self.subTest(name=name):
                work = self.compile(source, name)
                with fitz.open(work / 'book.pdf') as pdf:
                    text = ''.join(page.get_text() for page in pdf)
                    for token in tokens:
                        self.assertEqual(1, text.count(token), token)

    def test_repeated_headers_replay_grouped_and_explicit_note_marks(self):
        import fitz
        import re
        rows = '\n'.join('Row' + str(i) + '. & Value \\\\' for i in range(140))
        source = (r'\documentclass{w20book}\begin{document}'
                  r'\begin{msctable}{ll}\textbf{GroupedHeader\footnote[5]{FirstHeaderNote.}\footnote{SecondHeaderNote.}} & Value \\' +
                  rows + r'\end{msctable}\end{document}')
        work = self.compile(source, 'grouped-header-notes')
        with fitz.open(work / 'book.pdf') as pdf:
            text = ''.join(page.get_text() for page in pdf)
            marks = re.findall(r'GroupedHeader\s*(\d+)\s*(\d+)', text)
            self.assertGreater(len(marks), 1, text[:1200])
            self.assertTrue(all(first + second == '56' for first, second in marks), marks)
            self.assertEqual(1, text.count('FirstHeaderNote.'))
            self.assertEqual(1, text.count('SecondHeaderNote.'))

    def test_documented_crossover_example_compiles(self):
        import fitz
        work = self.compile((ROOT / 'examples/crossover.tex').read_text(), 'documented-example')
        with fitz.open(work / 'book.pdf') as pdf:
            text = ''.join(page.get_text() for page in pdf)
            for token in ('An Awakened Perspective', 'A Garou Perspective', 'Crossover character',
                          'A local sidebar note.', 'Arete', 'Gnosis'):
                self.assertIn(token, text)

    def test_native_m20_pixels_are_unchanged_when_crossover_is_loaded(self):
        import fitz
        import hashlib
        source = r'''\documentclass{m20book}
\title{Native Compatibility}\m20writtenby{Legacy Author}
\begin{document}\mainmatter\chapter{Native}
NativeBefore.
\begin{m20sidebarwide}[id=native-aside,columns=2]{NativeAside}
FirstNative.\begin{booktable}{ll}NativeCell & Value \\\end{booktable}
\sidebarbreak[page]SecondNative.
\end{m20sidebarwide}
\begin{m20tablelead}NativeLead.
\begin{booktable}{ll}LeadCell & Value \\\end{booktable}\end{m20tablelead}
\begin{m20statblock}\statentry{NativeEntry.|Willpower: 6}\end{m20statblock}
NativeAfter.\end{document}'''
        api = self.tree / 'tex/latex/wodtex/wodtex-api.sty'
        original = api.read_bytes()
        try:
            enabled = self.compile(source, 'native-crossover-loaded')
            # Disable only the automatic opt-in, retaining the same installed
            # native classes/resources and original dispatcher behavior.
            api.write_bytes(original.split(b'% PDF classes opt into scoped foreign components')[0] +
                            b'\\endinput\n')
            disabled = self.compile(source, 'native-crossover-disabled')
        finally:
            api.write_bytes(original)
        fingerprints = []
        for work in (enabled, disabled):
            with fitz.open(work / 'book.pdf') as pdf:
                fingerprints.append([hashlib.sha256(page.get_pixmap().samples).hexdigest() for page in pdf])
                text = ''.join(page.get_text() for page in pdf)
                for token in ('NativeBefore.', 'FirstNative.', 'NativeCell', 'SecondNative.',
                              'NativeLead.', 'LeadCell', 'NativeEntry.', 'NativeAfter.'):
                    self.assertEqual(1, text.count(token), token)
        self.assertEqual(fingerprints[0], fingerprints[1])


if __name__ == '__main__':
    unittest.main()
