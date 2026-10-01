"""PDF-local art reservations must use page edges and preserve text flow."""
import unittest
import fitz
from tests.test_layout_proof import compile_source, positions

class ArtEdgeTests(unittest.TestCase):
    def test_horizontal_top_reserve_is_at_page_top_with_body(self):
        prose = ('This is narrative beside an illustration reserve. The text must continue naturally across the page. ' * 8 + '\\par\n')
        source = (r'\documentclass{m20book}\begin{document}' + prose * 2
                  + r'\m20artreserve[kind=horizontal,position=top]{edge-horizontal}' + prose * 12
                  + r'\end{document}')
        _, path = compile_source(source, 'edge-horizontal-proof')
        art = next(p for p in positions(path) if p['id'] == 'edge-horizontal')
        self.assertLess(art['y'], 85, art)
        with fitz.open(path.with_suffix('.pdf')) as pdf:
            self.assertGreater(pdf[art['page'] - 1].get_text().count('narrative'), 3)

if __name__ == '__main__': unittest.main()
