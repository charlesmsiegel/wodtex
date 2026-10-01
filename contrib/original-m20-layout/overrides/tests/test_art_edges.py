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

    def test_vertical_reserve_is_full_height_with_single_column_section(self):
        prose = ('The section text flows beside a full-height column illustration. Its heading must not shorten the art. ' * 8 + '\\par\n')
        source = (r'\documentclass{m20book}\begin{document}' + prose * 2
                  + r'\m20artreserve[kind=vertical,position=outer]{edge-vertical}'
                  + r'\section{A Section Beside Art}' + prose * 12
                  + r'\end{document}')
        _, path = compile_source(source, 'edge-vertical-proof')
        records = positions(path)
        art = next(p for p in records if p['id'] == 'edge-vertical')
        heading = next(p for p in records if p['kind'] == 'heading')
        self.assertAlmostEqual(art['height'], 657, places=2)
        self.assertLess(art['y'], 85, art)
        self.assertAlmostEqual(art['x'], 305.2248 if art['page'] % 2 else 67.5504, places=2)
        self.assertEqual(heading['page'], art['page'])
        self.assertEqual(heading['columns'], 1)
        self.assertAlmostEqual(heading['width'], 239.2248, places=2)

if __name__ == '__main__': unittest.main()
