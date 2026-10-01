"""Native installed-payload proofs for matter transitions and title defaults."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import fitz
from tests.test_install import ROOT, installer

USER_SOURCE = r'''\documentclass{m20book}
\m20setup{running-title={Test Book},profile=m20}
\title{Test Book}
\author{Charles Siegel}
\setcounter{secnumdepth}{0}
\setcounter{tocdepth}{2}
\m20writtenby{Charles Siegel}
\m20developedby{Charles Siegel}
\m20editedby{Charles Siegel}
\m20specialthanks{Special Thanks}
\date{}
\renewcommand{\contentsname}{Table of Contents}
\hypersetup{pdfpagelayout=TwoPageRight,pdftitle={Test Book}}
\begin{document}
\frontmatter
\m20bodyend
\phantomsection\label{test-book}\label{exploring-the-ruins-of-the-awakened-world}
\mTwentyInteriorTitle{Test Book}{Exploring the Ruins of the Awakened World\par\smallskip\emph{A supplement for Mage: The Ascension 20th Anniversary Edition}}
\mTwentyInteriorCredits{}
\tableofcontents
\label{table-of-contents}
\mainmatter
\chapter{Test Chapter}\label{first-chapter}
This is a test of the installed M20 layout.
\end{document}
'''


@unittest.skipUnless(shutil.which('lualatex'), 'LuaLaTeX required')
class NativeFrontmatterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='wodtex-frontmatter-')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.tree = self.base / 'user tree'
        installer.install(self.tree, 'corrected')
        self.env = dict(os.environ, TEXMFHOME=str(self.tree))

    def render(self, source, name, toc_entries=0):
        work = self.base / name
        work.mkdir()
        (work / 'book.tex').write_text(source)
        for _ in range(2):
            if toc_entries:
                (work / 'book.toc').write_text(''.join(
                    r'\contentsline {section}{TOC-ENTRY-' + f'{i:03d}' + r'}{1}{chapter.1}' + '\n'
                    for i in range(toc_entries)))
            result = subprocess.run(['lualatex', '-interaction=nonstopmode', '-halt-on-error', 'book.tex'], cwd=work, env=self.env, text=True, capture_output=True)
            self.assertEqual(0, result.returncode, result.stdout[-7000:])
        self.assertNotIn('undefined references', (work / 'book.log').read_text())
        evidence = ROOT / 'build/native-frontmatter' / name
        evidence.mkdir(parents=True, exist_ok=True)
        for path in work.glob('book.*'):
            shutil.copy2(path, evidence / path.name)
        return fitz.open(work / 'book.pdf')

    def assert_facing_transition(self, document, toc_last):
        body = next(i for i, page in enumerate(document) if 'This is a test of the installed' in page.get_text())
        facing = body - 1
        self.assertIn('Place illustration here', document[facing].get_text())
        self.assertEqual(0, (facing + 1) % 2, 'illustration must be a physical verso')
        self.assertEqual(1, (body + 1) % 2, 'chapter must be a physical recto')
        expected_spacers = 0 if (toc_last + 1) % 2 else 1
        self.assertEqual(expected_spacers, facing - toc_last - 1, 'extra blank spread after TOC')
        spans = [s for b in document[body].get_text('dict')['blocks'] for l in b.get('lines', []) for s in l['spans']]
        footers = [s['text'] for s in spans if abs(s['origin'][1] - 736.81) < .2]
        self.assertIn('1', footers, 'first chapter must begin Arabic page 1')

    def test_short_toc_uses_next_verso_for_illustration(self):
        with self.render(USER_SOURCE, 'short-toc') as doc:
            self.assert_facing_transition(doc, 2)
            self.assertEqual(5, len(doc))

    def test_multi_page_toc_preserves_only_required_parity(self):
        parities = set()
        for count in (110, 220):
            with self.subTest(entries=count), self.render(USER_SOURCE, 'long-toc-' + str(count), count) as doc:
                pages = [i for i, page in enumerate(doc) if 'TOC-ENTRY-' in page.get_text()]
                self.assertGreater(len(pages), 1)
                parities.add((pages[-1] + 1) % 2)
                self.assert_facing_transition(doc, pages[-1])
        self.assertEqual({0, 1}, parities, 'fixtures must exercise both TOC-ending parities')

    def test_later_chapter_keeps_its_facing_leaf(self):
        source = USER_SOURCE.replace(r'\end{document}', r'\chapter{Second Chapter}SECOND-CHAPTER-BODY.\end{document}')
        with self.render(source, 'second-chapter') as doc:
            self.assert_facing_transition(doc, 2)
            second = next(i for i, page in enumerate(doc) if 'SECOND-CHAPTER-BODY.' in page.get_text())
            self.assertEqual(1, (second + 1) % 2)
            self.assertIn('Place illustration here', doc[second - 1].get_text())

    def test_content_between_mainmatter_and_chapter_gets_its_own_facing_leaf(self):
        source = USER_SOURCE.replace(r'\mainmatter', r'\mainmatter INTERLUDE-CONTENT.\m20newpage')
        with self.render(source, 'intervening-mainmatter-text') as doc:
            interlude = next(i for i, page in enumerate(doc) if 'INTERLUDE-CONTENT.' in page.get_text())
            body = next(i for i, page in enumerate(doc) if 'This is a test of the installed' in page.get_text())
            self.assertLess(interlude, body)
            self.assertIn('Place illustration here', doc[body - 1].get_text())
            self.assertEqual(1, (body + 1) % 2)

    def title_document(self, preamble):
        return r'\documentclass{m20book}' + preamble + r'''\begin{document}
\chapter{Content}BODY-FIRST.\m20newpage BODY-SECOND.
\end{document}'''

    def test_native_title_defaults_to_pdf_metadata_and_even_footer(self):
        with self.render(self.title_document(r'\title{Single Title}'), 'title-inheritance') as doc:
            self.assertEqual('Single Title', doc.metadata['title'])
            self.assertIn('Single Title', doc[-1].get_text())

    def test_explicit_title_overrides_work_in_either_order(self):
        title = r'\title{Native Title}'
        overrides = r'\m20setup{running-title={Runner Override}}\hypersetup{pdftitle={PDF Override}}'
        for i, preamble in enumerate((overrides + title, title + overrides)):
            with self.subTest(order=i), self.render(self.title_document(preamble), 'title-overrides-' + str(i)) as doc:
                self.assertEqual('PDF Override', doc.metadata['title'])
                self.assertIn('Runner Override', doc[-1].get_text())
                self.assertNotIn('Native Title', doc[-1].get_text())

    def test_interior_title_preserves_explicit_pdf_title(self):
        source = self.title_document(r'\title{Native Title}\hypersetup{pdftitle={PDF Override}}')
        source = source.replace(r'\chapter{Content}', r'\mTwentyInteriorTitle{Print Title}{Subtitle}\chapter{Content}')
        with self.render(source, 'interior-title-override') as doc:
            self.assertEqual('PDF Override', doc.metadata['title'])

    def test_explicit_empty_running_title_is_preserved(self):
        source = self.title_document(r'\m20setup{running-title={}}\title{Native Title}')
        with self.render(source, 'empty-running-title') as doc:
            self.assertNotIn('Native Title', doc[-1].get_text())

    def test_formatted_native_title_has_pdf_safe_metadata(self):
        with self.render(self.title_document(r'\title{A \textbf{Formatted} Book}'), 'formatted-title') as doc:
            self.assertEqual('A Formatted Book', doc.metadata['title'])
            self.assertIn('A Formatted Book', doc[-1].get_text())

    def test_no_title_remains_valid(self):
        with self.render(self.title_document(''), 'no-title') as doc:
            self.assertEqual('', doc.metadata['title'])
