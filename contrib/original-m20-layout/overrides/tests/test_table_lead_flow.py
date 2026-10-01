"""A table caption must remain in its wide float without balancing prose."""
import unittest
import fitz
from tests.test_layout_proof import compile_source

class TableLeadFlowTests(unittest.TestCase):
    def test_caption_and_table_remain_together_inside_live_columns(self):
        prose = ('A continuous narrative should fill both columns while a compact table waits for a page edge. ' * 10 + '\\par\n')
        source = (r'\documentclass{m20book}\begin{document}' + prose * 4
                  + r'\begin{m20tablelead}\subsection{Levels for the Example}'
                  + r'\label{lead-caption}\m20anchor{lead-caption}'
                  + r'\begin{m20table}[id=lead-table,head-rows=1]{ll}'
                  + r'Rating & Description \\ One & FIRST-ROW-SENTINEL \\ Two & SECOND-ROW-SENTINEL \\'
                  + r'\end{m20table}\end{m20tablelead}' + prose * 10
                  + r'\end{document}')
        _, path = compile_source(source, 'table-lead-flow-proof')
        with fitz.open(path.with_suffix('.pdf')) as pdf:
            title_pages = [i for i,p in enumerate(pdf) if 'Levels for the Example' in p.get_text()]
            row_pages = [i for i,p in enumerate(pdf) if 'FIRST-ROW-SENTINEL' in p.get_text()]
            self.assertEqual(title_pages, row_pages)
            self.assertEqual(len(title_pages), 1)
            page = pdf[title_pages[0]]
            self.assertLess(page.search_for('Levels for the Example')[0].y0,
                            page.search_for('FIRST-ROW-SENTINEL')[0].y0)
            self.assertGreater(page.get_text().count('continuous narrative'), 3)

if __name__ == '__main__': unittest.main()
