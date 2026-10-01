"""Real pixels for the authoritative double-rule sidebar frame; no source mocks."""
import unittest
import fitz
from tests.test_layout_proof import compile_source


class SidebarFramePaintTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, cls.path = compile_source(
            r'\documentclass{m20book}\begin{document}'
            r'\begin{m20sidebarwide}[id=frame-paint,columns=1]{Frame proof}'
            r'First line.\par Second line.\par Third line.'
            r'\end{m20sidebarwide}\end{document}', 'sidebar-frame-paint')

    def test_gradient_double_gold_rules_and_clear_gap(self):
        with fitz.open(self.path.with_suffix('.pdf')) as doc:
            page = doc[0]
            frame = next(d['rect'] for d in page.get_drawings()
                         if d['type'] == 'f' and d.get('fill')
                         and abs(d['fill'][0] - .2918898) < .002)
            pix = page.get_pixmap(matrix=fitz.Matrix(8, 8), alpha=False)
            def sample(x, y):
                return pix.pixel(round(x * 8), round(y * 8))[:3]
            outer = sample(frame.x0 + 1.75, frame.y0 + frame.height / 2)
            gap = sample(frame.x0 + 4.7, frame.y0 + frame.height / 2)
            inner = sample(frame.x0 + 6.4155, frame.y0 + frame.height / 2)
            self.assertLess(max(gap), 100, 'A 2.331 bp dark gap must separate gold rules')
            self.assertGreater(min(inner[:2]), 140, 'The inset 1.169 bp rule must be gold')
            self.assertLess(max(abs(a-b) for a,b in zip(outer, inner)), 5)
            top = sample(frame.x0 + 1.75, frame.y0 + 2)
            bottom = sample(frame.x0 + 1.75, frame.y1 - 2)
            self.assertGreater(top[1] - bottom[1], 60, 'Gold must fade from pale top to dark bottom')
            self.assertLess(max(abs(a-b) for a,b in zip(outer, (203,175,102))), 8)
            shadow = sample(frame.x1 + 4, frame.y0 + frame.height/2)
            self.assertLess(min(shadow), 252, 'Authentic lower-right drop shadow must remain visible')
            self.assertGreater(min(shadow), 220, 'Shadow must remain subtle')


if __name__ == '__main__':
    unittest.main()
