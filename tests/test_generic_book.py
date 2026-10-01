"""Installed native proofs for the approved generic interface."""
import hashlib
import re
import subprocess
from pathlib import Path
import shutil
import unittest
from tests import test_native_frontmatter as frontmatter
from tests.test_install import ROOT, installer


@unittest.skipUnless(shutil.which('lualatex'), 'LuaLaTeX required')
class GenericBookTests(unittest.TestCase):
    setUp = frontmatter.NativeFrontmatterTests.setUp
    render = frontmatter.NativeFrontmatterTests.render

    def test_exact_approved_example(self):
        work = self.base / 'generic-example'
        work.mkdir()
        shutil.copytree(ROOT / 'examples/art', work / 'art')
        source = (ROOT / 'examples/generic-book.tex').read_text()
        fingerprints = self.render_source(source, work)
        config = self.tree / 'tex/latex/wodtex-local/wodtex-local.tex'
        before = config.read_bytes()
        installer.install(self.tree, 'corrected')
        self.assertEqual(before, config.read_bytes())
        self.assertEqual(fingerprints, self.render_source(source, work))

    def render_source(self, source, work):
        import subprocess
        import fitz
        (work / 'book.tex').write_text(source)
        for _ in range(2):
            result = subprocess.run(['lualatex', '-interaction=nonstopmode', '-halt-on-error', 'book.tex'], cwd=work, env=self.env, text=True, capture_output=True)
            self.assertEqual(0, result.returncode, result.stdout[-7000:])
        evidence = ROOT / 'build/generic-book' / work.name
        evidence.mkdir(parents=True, exist_ok=True)
        for p in work.glob('book.*'):
            shutil.copy2(p, evidence / p.name)
        with fitz.open(work / 'book.pdf') as doc:
            text = ''.join(p.get_text() for p in doc)
            self.assertEqual('Test Book', doc.metadata['title'])
            self.assertEqual('Charles Siegel', doc.metadata['author'])
            for item in ('Exploring the Ruins of the Awakened World', 'genuine bold', 'An explicit author-requested continuation.', 'A wrapped cell.', 'Another value.', 'Existing introductory prose that must travel with this table.', 'Feral Realm', 'Scene caption', 'Artist credit'):
                self.assertEqual(1, text.count(item), item)
            self.assertTrue(any(p.get_links() for p in doc), 'TOC must retain links')
            fonts = {s['font'] for p in doc for b in p.get_text('dict')['blocks'] for line in b.get('lines', []) for s in line['spans']}
            self.assertTrue(any('Abbess' in f for f in fonts), fonts)
            self.assertTrue(any('Goudy' in f for f in fonts), fonts)
            fingerprints = [hashlib.sha256(p.get_pixmap().samples).hexdigest() for p in doc]
            self.assertNotIn('Missing character:', (work / 'book.log').read_text())
        self.assertNotIn('undefined references', (work / 'book.log').read_text())
        return fingerprints

    def test_old_and_generic_api_have_identical_page_pixels(self):
        generic = (ROOT / 'examples/generic-book.tex').read_text()
        old = generic
        old = re.sub(r'\\(?:subtitle|bookdescription)\{[^\n]*\}\n', '', old)
        old = old.replace(r'\maketitle', r'\mTwentyInteriorTitle{Test Book}{Exploring the Ruins of the Awakened World\par\smallskip\emph{A supplement for Mage: The Ascension 20th Anniversary Edition}}')
        old = old.replace(r'\makecredits', r'\mTwentyInteriorCredits{}')
        for generic_name, old_name in [('writtenby','m20writtenby'),('developedby','m20developedby'),('editedby','m20editedby'),('specialthanks','m20specialthanks'),('sidebarbreak','m20sidebarbreak'),('statentry','mTwentyStatEntry'),('artreserve','m20artreserve')]:
            old = old.replace('\\' + generic_name, '\\' + old_name)
        for name in ('sidebarwide','sidebar','booktable','tablelead','statblock'):
            target = 'm20table' if name == 'booktable' else 'm20' + name
            old = old.replace('{' + name + '}', '{' + target + '}')
        outputs = []
        for name, source in [('comparison-generic',generic),('comparison-old',old)]:
            work = self.base / name
            work.mkdir()
            shutil.copytree(ROOT / 'examples/art', work / 'art')
            outputs.append(self.render_source(source, work))
        self.assertEqual(outputs[0], outputs[1])

    def compile_probe(self, source, name, error=None):
        work = self.base / name
        work.mkdir()
        (work / 'book.tex').write_text(source)
        result = subprocess.run(['lualatex','-interaction=nonstopmode','-halt-on-error','book.tex'], cwd=work, env=self.env, capture_output=True, text=True)
        if error:
            self.assertNotEqual(0, result.returncode)
            self.assertIn(error, result.stdout[-9000:])
        else:
            self.assertEqual(0, result.returncode, result.stdout[-9000:])
        return work

    def test_preamble_and_later_api_collisions_are_actionable(self):
        for i, source in enumerate([
            r'\def\subtitle#1{}\documentclass{m20book}\begin{document}x\end{document}',
            r'\documentclass{m20book}\renewcommand\subtitle[1]{}\begin{document}x\end{document}',
            r'\documentclass{m20book}\RenewDocumentCommand\subtitle{m}{}\begin{document}x\end{document}',
            r'\documentclass{m20book}\RenewDocumentEnvironment{sidebar}{O{}m+b}{}{}\begin{document}x\end{document}',
            r'\documentclass{m20book}\begin{document}\renewcommand\subtitle[1]{}x\end{document}',
        ]):
            with self.subTest(i=i):
                self.compile_probe(source,'collision-'+str(i),'WODTEX_E_NAME_COLLISION')

    def test_registry_rejects_unknown_and_mutable_body_style(self):
        self.compile_probe(r'\documentclass{m20book}\wodtexSetClassStyle{missing}\begin{document}x\end{document}', 'unknown-style', 'WODTEX_E_STYLE_UNKNOWN')
        self.compile_probe(r'\documentclass{m20book}\wodtexRegisterRenderer{m20}{setup}{wodtexMageSetup}\begin{document}x\end{document}', 'duplicate-style', 'WODTEX_E_DUPLICATE_RENDERER')
        self.compile_probe(r'\documentclass{m20book}\begin{document}\wodtexSetClassStyle{m20}\end{document}', 'body-style', 'Can be used only in preamble')

    def test_missing_meaningful_art_stays_an_error(self):
        self.compile_probe(r'\documentclass{m20book}\begin{document}\artreserve[image={missing.png},alt={Missing scene}]{missing-scene}\end{document}', 'missing-art', 'M20_E_IMAGE_MISSING')

    def test_nested_generic_tables_keep_explicit_m20_context(self):
        source = r'''\documentclass{m20book}
\title{Nested Compatibility}
\begin{document}
\chapter{Nested}
\begin{m20sidebarwide}[id=nested-aside,columns=2,place=next-page]{Ordered Note}
Before the ordered table.
\begin{booktable}[id=nested-table,head-rows=1]{ll}
Key & Value \\
Nested & Conserved cell \\
\end{booktable}
\sidebarbreak[page]
After the requested continuation.
\end{m20sidebarwide}
\end{document}'''
        work = self.compile_probe(source,'nested-table')
        import fitz
        with fitz.open(work / 'book.pdf') as doc:
            text = ''.join(p.get_text() for p in doc)
            for content in ('Before the ordered table.', 'Conserved cell', 'After the requested continuation.'):
                self.assertEqual(1,text.count(content),content)
            self.assertIn('(continued)',text)

    def test_mixed_test_style_keeps_continuations_and_deferred_boxes_local(self):
        source = r'''\documentclass{m20book}
\title{Mixed Dispatch Probe}
\newcommand\fixtureSidebar[3]{\par\begingroup\color{blue}\fontsize{9bp}{11bp}\selectfont\parindent=37bp\parskip=7bp\linewidth=120bp\textbf{FIXTURE #2}\par#3\par\endgroup}
\newcommand\fixtureBreak[1]{\par\newpage\textbf{FIXTURE CONTINUATION}\par}
\newcommand\fixtureTable[3]{\begingroup\let\mTwentyBodyBegin\relax\begin{table}[tbp]\color{blue}\textbf{FIXTURE FLOAT}\par\begin{tabular}{#2}#3\end{tabular}\end{table}\endgroup}
\wodtexRegisterRenderer{fixture}{sidebar}{fixtureSidebar}
\wodtexRegisterRenderer{fixture}{sidebar-before}{wodtexMageNoop}
\wodtexRegisterRenderer{fixture}{sidebar-after}{wodtexMageNoop}
\wodtexRegisterRenderer{fixture}{sidebarwide}{fixtureSidebar}
\wodtexRegisterRenderer{fixture}{sidebarwide-before}{wodtexMageBeforeWide}
\wodtexRegisterRenderer{fixture}{sidebarwide-after}{wodtexMageAfter}
\wodtexRegisterRenderer{fixture}{sidebarbreak}{fixtureBreak}
\wodtexRegisterRenderer{fixture}{booktable}{fixtureTable}
\wodtexRegisterRenderer{fixture}{booktable-before}{wodtexMageBeforeTable}
\wodtexRegisterRenderer{fixture}{booktable-after}{wodtexMageAfter}
\wodtexSetClassStyle{fixture}
% Registration snapshots the definition before this deliberate later edit.
\renewcommand\fixtureSidebar[3]{\errmessage{Mutable fixture renderer was called}}
\begin{document}
\chapter{Dispatch}
\makeatletter
\xdef\savedHostFamily{\f@family}\xdef\savedHostSize{\f@size}
\newcommand\checkHost{\edef\currentHostFamily{\f@family}\edef\currentHostSize{\f@size}\ifx\savedHostFamily\currentHostFamily\else\errmessage{Host font leaked}\fi\ifx\savedHostSize\currentHostSize\else\errmessage{Host font size leaked}\fi\edef\currentHostWidth{\the\linewidth}\ifx\savedHostWidth\currentHostWidth\else\errmessage{Host width leaked}\fi\edef\currentHostIndent{\the\parindent}\ifx\savedHostIndent\currentHostIndent\else\errmessage{Host indent leaked}\fi\edef\currentHostSkip{\the\parskip}\ifx\savedHostSkip\currentHostSkip\else\errmessage{Host paragraph skip leaked}\fi}
\global\let\checkHost\checkHost
\makeatother
\xdef\savedHostWidth{\the\linewidth}\xdef\savedHostIndent{\the\parindent}\xdef\savedHostSkip{\the\parskip}
BODY BEFORE.
\begin{sidebarwide}{Alternate}
FIXTURE FIRST SEGMENT.
\sidebarbreak[page]
FIXTURE SECOND SEGMENT.
\end{sidebarwide}
\checkHost BODY BETWEEN.
\begin{m20sidebarwide}[id=explicit-note,columns=2,place=next-page]{Explicit Mage}
MAGE FIRST SEGMENT.
\begin{booktable}[id=explicit-nested,head-rows=1]{ll}
Nested & MAGE TABLE \\
\end{booktable}
\sidebarbreak[page]
MAGE SECOND SEGMENT.
\end{m20sidebarwide}
\begin{booktable}{ll}
Float & Payload \\
Deferred & Conserved \\
\end{booktable}
\begin{sidebar}{Following}
FIXTURE AFTER MAGE.
\end{sidebar}
\checkHost BODY AFTER.
\end{document}'''
        work = self.compile_probe(source,'mixed-fixture')
        import fitz
        with fitz.open(work / 'book.pdf') as doc:
            text = ''.join(p.get_text() for p in doc)
            for content in ('FIXTURE FIRST SEGMENT.', 'FIXTURE SECOND SEGMENT.', 'MAGE FIRST SEGMENT.', 'MAGE SECOND SEGMENT.', 'FIXTURE AFTER MAGE.', 'FIXTURE FLOAT', 'Deferred', 'Conserved', 'MAGE TABLE'):
                self.assertEqual(1,text.count(content),content)
            self.assertEqual(1,text.count('FIXTURE CONTINUATION'))
            self.assertIn('Explicit Mage(continued)',text)
            spans = [s for p in doc for b in p.get_text('dict')['blocks'] for l in b.get('lines',[]) for s in l['spans']]
            for span in spans:
                if 'BODY ' in span['text']:
                    self.assertEqual(0,span['color'],span)
                if 'FIXTURE ' in span['text']:
                    self.assertEqual(255,span['color'],span)
                if 'MAGE ' in span['text']:
                    self.assertNotEqual(255,span['color'],span)

    def test_unimplemented_style_capability_fails_clearly(self):
        source = r'\documentclass{m20book}\newcommand\fixtureNoop{}\wodtexRegisterRenderer{fixture}{noop}{fixtureNoop}\wodtexSetClassStyle{fixture}\begin{document}\maketitle\end{document}'
        self.compile_probe(source,'missing-capability','WODTEX_E_CAPABILITY')

    def test_xparse_renderer_registration_snapshots_internal_code(self):
        source = r'''\documentclass{m20book}
\NewDocumentCommand\fixtureRenderer{O{DEFAULT}m}{ORIGINAL #1 #2}
\wodtexRegisterRenderer{fixture}{probe}{fixtureRenderer}
\RenewDocumentCommand\fixtureRenderer{O{CHANGED}m}{MUTATED #1 #2}
\begin{document}
\wodtexDispatchStyle{fixture}{probe}{PAYLOAD}
\end{document}'''
        work = self.compile_probe(source,'xparse-snapshot')
        import fitz
        with fitz.open(work / 'book.pdf') as doc:
            text = ''.join(p.get_text() for p in doc)
            self.assertIn('ORIGINAL DEFAULT PAYLOAD',text)
            self.assertNotIn('MUTATED',text)

    def test_legacy_epub_mode_retains_native_maketitle(self):
        source = r'''\documentclass[output=epub]{m20book}
\title{Legacy Title}
\author{Legacy Author}
\begin{document}
\maketitle
LEGACY BODY.
\end{document}'''
        work = self.compile_probe(source,'legacy-epub-title')
        import fitz
        with fitz.open(work / 'book.pdf') as doc:
            text = ''.join(p.get_text() for p in doc)
            self.assertIn('Legacy Title',text)
            self.assertIn('Legacy Author',text)
            self.assertIn('LEGACY BODY.',text)

    def test_legacy_base_mode_retains_native_maketitle(self):
        installer.install(self.tree, 'base', font_dir=ROOT / 'fonts', asset_dir=ROOT / 'assets', configure=True)
        # This route probe uses public test typography because the legacy base
        # renderer requires additional fonts outside the corrected bundle.
        source = r'''\documentclass{m20book}
\renewcommand\mTwentyLoadFonts{\setmainfont{DejaVuSans.ttf}[Path=\mTwentyFontPath]\newfontfamily\mTwentyFirstFont{DejaVuSans.ttf}[Path=\mTwentyFontPath]\newfontfamily\mTwentyHeadingFont{DejaVuSans.ttf}[Path=\mTwentyFontPath]\newfontfamily\mTwentyHeadingNarrowFont{DejaVuSans.ttf}[Path=\mTwentyFontPath]\newfontfamily\mTwentySidebarFont{DejaVuSans.ttf}[Path=\mTwentyFontPath]}
\title{Legacy Base Title}
\author{Legacy Base Author}
\begin{document}
\maketitle
LEGACY BASE BODY.
\end{document}'''
        work = self.compile_probe(source,'legacy-base-title')
        import fitz
        with fitz.open(work / 'book.pdf') as doc:
            text = ''.join(p.get_text() for p in doc)
            self.assertIn('Legacy Base Title',text)
            self.assertIn('Legacy Base Author',text)
            self.assertIn('LEGACY BASE BODY.',text)
