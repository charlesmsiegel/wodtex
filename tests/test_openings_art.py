import unittest
import fitz
from tests.test_layout_proof import compile_source, positions

class OpeningArtTests(unittest.TestCase):
    def test_meaningful_art_options_survive_leaving_active_body(self):
        source=r'''\documentclass{m20book}\begin{document}BEFORE
\m20artreserve[image=examples/content/diagram.png,alt={Three panels},caption={ACTIVECAPTION},credit={ACTIVECREDIT},place=next-page]{active-art}
AFTER\end{document}'''
        p,path=compile_source(source,'active-art')
        self.assertNotIn('Undefined control sequence',p.stdout)
        with fitz.open(path.with_suffix('.pdf')) as pdf:
            text=''.join(p.get_text() for p in pdf)
            self.assertIn('ACTIVECAPTION',text)
            self.assertIn('ACTIVECREDIT',text)
            self.assertIn('AFTER',text)
            art=next(r for r in positions(path) if r['id']=='active-art')
            self.assertGreaterEqual(len(pdf[art['page']-1].get_images()),2)

    def test_chapter_has_fresh_blank_verso_after_either_parity(self):
        for pages in [1,2]:
            ending=''.join(r'\m20newpage ENDING' for _ in range(pages-1))
            _,path=compile_source(r'\documentclass{m20book}\begin{document}ENDING'+ending+r'\chapter{Opener}\m20anchor{opener-body}BODY\end{document}',f'opener-{pages}')
            marker=next(p for p in positions(path) if p['id']=='opener-body')
            self.assertEqual(marker['page']%2,1)
            self.assertGreaterEqual(marker['page'],pages+2)
            self.assertAlmostEqual(marker['y'],355.5,delta=18)
            with fitz.open(path.with_suffix('.pdf')) as pdf:
                self.assertEqual(pdf[marker['page']-2].get_text().strip(),'')

    def test_oversized_title_requires_explicit_override(self):
        title=' '.join(['This is an excessively long chapter title']*18)
        p,_=compile_source(r'\documentclass{m20book}\begin{document}\chapter{'+title+r'}Text.\end{document}','long-title',False)
        self.assertNotEqual(p.returncode,0)
        self.assertIn('M20_E_CHAPTER_TITLE_TOO_TALL',p.stdout)

    def test_art_shapes_positions_and_body_clearance(self):
        for kind,positions_ in [('horizontal',['top','bottom']),('vertical',['inner','outer'])]:
            for parity in [1,2]:
                for position in positions_:
                    prefix=r'\m20bodyend'
                    if parity==2: prefix+=r'\null\newpage'
                    source=r'\documentclass{m20book}\begin{document}'+prefix+r'\m20artreserve[kind='+kind+',position='+position+r',place=here]{art}AFTER-ART '+('Clear body text flows beside or below reserved artwork. '*35)+r'\end{document}'
                    _,path=compile_source(source,f'art-{kind}-{parity}-{position}')
                    art=next(p for p in positions(path) if p['kind']=='art')
                    self.assertEqual(art['page'],parity)
                    self.assertAlmostEqual(art['width'],490.4496 if kind=='horizontal' else 239.2248,places=2)
                    with fitz.open(path.with_suffix('.pdf')) as pdf:
                        rect=fitz.Rect(art['x']+2,art['y']+2,art['x']+art['width']-2,art['y']+art['height']-2)
                        self.assertEqual(pdf[art['page']-1].get_textbox(rect).strip(),'')
                        self.assertIn('AFTER-ART',''.join(p.get_text() for p in pdf))

    def test_impossible_forced_art_errors(self):
        source=r'\documentclass{m20book}\begin{document}\m20bodyend\null\vspace*{500bp}\m20artreserve[kind=horizontal,place=here]{impossible}\end{document}'
        p,_=compile_source(source,'art-impossible',False)
        self.assertNotEqual(p.returncode,0)
        self.assertIn('M20_E_PLACEMENT_UNAVAILABLE',p.stdout)

    def test_missing_meaningful_image_errors(self):
        p,_=compile_source(r'\documentclass{m20book}\begin{document}\m20artreserve[image=missing.png,alt={Missing image}]{missing}\end{document}','art-missing',False)
        self.assertNotEqual(p.returncode,0)
        self.assertIn('M20_E_IMAGE_MISSING',p.stdout)
