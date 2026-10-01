"""Real-page proofs for the opt-in reference-matched front matter."""
import unittest
import fitz
from tests.test_layout_proof import compile_source
from tests.support import ROOT

SOURCE = r'''\documentclass{m20book}
\m20setup{running-title={Reference Proof}}
\m20writtenby{[Writer Name]}
\m20developedby{[Developer Name]}
\m20editedby{[Editor Name]}
\m20specialthanks{[Special Thanks]}
\AtBeginDocument{\renewcommand{\contentsname}{Table of Contents}}
\makeatletter
\begin{document}\frontmatter
\typeout{REFERENCE-FRONT=\if@mainmatter TRUE\else FALSE\fi}
\mTwentyInteriorTitle{Reference Proof}{Subtitle}
\mTwentyInteriorCredits{\section{Credits and Attributions}SOURCE-ATTRIBUTION.}
\tableofcontents\mainmatter
\typeout{REFERENCE-MAIN=\if@mainmatter TRUE\else FALSE\fi}
\chapter{First Title}\section{First Section}BODY-ONE.
\chapter{A Longer Second Chapter Title}BODY-TWO.
\appendix\chapter{Appendix Title}BODY-APPENDIX.
\end{document}'''

class FrontMatterReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.process, cls.path = compile_source(SOURCE, 'frontmatter-regression')

    def test_credit_header_commands_and_direct_contents(self):
        with fitz.open(self.path.with_suffix('.pdf')) as d:
            credit=d[1].get_text();toc=d[2].get_text()
            for text in ['Credits','Written By: [Writer Name]','Developed By: [Developer Name]',
                         'Edited By: [Editor Name]','Special Thanks to:','[Special Thanks]',
                         'SOURCE-ATTRIBUTION.','White Wolf Entertainment AB','www.storytellersvault.com']:
                self.assertIn(text, credit)
            legal=[sp for b in d[1].get_text('dict')['blocks'] for l in b.get('lines',[]) for sp in l['spans'] if abs(sp['origin'][1]-639.7725)<.1]
            line=''.join(sp['text'] for sp in sorted(legal,key=lambda sp:sp['bbox'][0]))
            self.assertIn('2026 White Wolf Entertainment AB',' '.join(line.split()))
            self.assertIn('Contents',toc)
            self.assertNotIn('Credits and Attributions',toc)
            self.assertIn('REFERENCE-FRONT=FALSE',self.process.stdout)
            self.assertIn('REFERENCE-MAIN=TRUE',self.process.stdout)

    def test_word_chapter_toc_uses_purple_abbess_without_numeral_column(self):
        with fitz.open(self.path.with_suffix('.pdf')) as d:
            toc=d[2];text=toc.get_text()
            for label in ['Chapter One: First Title','Chapter Two: A Longer Second Chapter Title','Appendix A: Appendix Title']:
                self.assertIn(label,' '.join(text.split()))
            spans=[s for b in toc.get_text('dict')['blocks'] for l in b.get('lines',[]) for s in l['spans']]
            chapter=next(s for s in spans if 'Chapter One:' in s['text'])
            self.assertIn('Abbess',chapter['font']);self.assertNotIn(chapter['color'],[0,0xffffff])
            self.assertAlmostEqual(chapter['size'],12,places=2)
            self.assertNotIn('\\contentsline {section}{Credits',self.path.with_suffix('.toc').read_text())

    def test_contents_uses_the_ordinary_spread_border(self):
        with fitz.open(self.path.with_suffix('.pdf')) as d, fitz.open(ROOT/'assets/spread-border.original-template.pdf') as ref:
            actual=d[2].get_pixmap(dpi=72,alpha=False).samples
            wanted=ref[1].get_pixmap(dpi=72,alpha=False).samples
            stride=612*3
            for y in range(792):
                a=actual[y*stride:(y+1)*stride];b=wanted[y*stride:(y+1)*stride]
                if y<40 or y>=760:
                    self.assertEqual(a,b)
                elif y<740:
                    self.assertEqual(a[:40*3],b[:40*3]);self.assertEqual(a[-40*3:],b[-40*3:])

    def test_parity_spacers_have_border_and_footer(self):
        with fitz.open(self.path.with_suffix('.pdf')) as d:
            for page in d:
                self.assertTrue(page.get_text().strip() or page.get_images() or page.get_xobjects())
                text=page.get_text().strip()
                if text and not any(label in text for label in ['BODY-','Contents','Credits','Reference Proof','illustration']):
                    self.assertTrue(page.get_xobjects())
                    footer=[s for b in page.get_text('dict')['blocks'] for l in b.get('lines',[]) for s in l['spans'] if abs(s['origin'][1]-736.81)<.1]
                    self.assertTrue(footer)

    def test_copyright_year_header_override(self):
        _,path=compile_source(SOURCE.replace(r'\begin{document}',r'\m20copyrightyear{2042}\begin{document}'),'copyright-year-override')
        with fitz.open(path.with_suffix('.pdf')) as d:
            sp=[s for b in d[1].get_text('dict')['blocks'] for l in b.get('lines',[]) for s in l['spans'] if abs(s['origin'][1]-639.7725)<.1]
            line=''.join(s['text'] for s in sorted(sp,key=lambda s:s['bbox'][0]))
            self.assertIn('2042 White Wolf Entertainment AB',' '.join(line.split()))
            self.assertNotIn('2018',line)

    def test_each_chapter_faces_exact_fullpage_placeholder(self):
        with fitz.open(self.path.with_suffix('.pdf')) as d, fitz.open(ROOT/'assets/art-fullpage.original-template.pdf') as art:
            expected=art[0].get_pixmap(dpi=72,alpha=False).samples
            for marker in ['BODY-ONE.','BODY-TWO.','BODY-APPENDIX.']:
                i=next(i for i,p in enumerate(d) if marker in p.get_text())
                self.assertEqual((i+1)%2,1)
                actual=d[i-1].get_pixmap(dpi=72,alpha=False).samples
                self.assertEqual(actual[:280*612*3],expected[:280*612*3])
                self.assertEqual(actual[420*612*3:],expected[420*612*3:])
                self.assertEqual(' '.join(d[i-1].get_text().split()),'Place illustration here (recomended full colour)')
                font_spans=[s for b in d[i-1].get_text('dict')['blocks'] for l in b.get('lines',[]) for s in l['spans']]
                self.assertTrue(all('Goudy' in s['font'] for s in font_spans))
