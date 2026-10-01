"""Real shipout/pixel regressions for horizontal art's float and column boundaries."""
import unittest

import fitz

from tests.test_layout_proof import compile_source, positions


def queued_table_source(following_prose):
    """A compact native lead/table is queued ahead of a top-edge art float."""
    paragraph = (
        'The survey team records each measurement before returning to the central office. '
        'A careful account preserves the evidence and gives the next team a useful starting point. '
        'Every route has a reference marker, and every report includes enough detail for an independent review. '
    ) + r'\par' + '\n'
    lead = r'''\begin{m20tablelead}
\subsection{Survey reference}
The following entries summarize the five routes in the sample survey.\par
\begin{m20table}[id=queued-table,width=container,head-rows=1]{llll}
Route & Team & Distance & Notes \\
North & Alpha & Short & First record \\
South & Beta & Medium & Second record \\
East & Gamma & Long & Third record \\
West & Delta & Short & Fourth record \\
Central & Epsilon & Medium & Fifth record \\
\end{m20table}
\end{m20tablelead}'''
    return (r'\documentclass{m20book}\begin{document}\chapter{Survey Records}'
            + paragraph * 3 + lead + paragraph * 3
            + r'\m20artreserve[kind=horizontal,position=top]{top-art}'
            + (paragraph * 20 if following_prose else 'End of sample prose.')
            + r'\end{document}')


class HorizontalArtFloatEdgeTests(unittest.TestCase):
    def test_forced_float_page_keeps_art_as_its_first_float(self):
        _, path = compile_source(queued_table_source(following_prose=False),
                                 'horizontal-art-clearpage-proof')
        records = positions(path)
        art = next(p for p in records if p['id'] == 'top-art')
        table = next(p for p in records if p['id'] == 'queued-table')
        self.assertLess(table['page'], art['page'])
        self.assertAlmostEqual(art['y'], 63, delta=.1, msg=art)

    def test_later_bottom_float_cannot_lift_horizontal_art_from_page_bottom(self):
        prose = 'Continuous narrative filling the live columns before and after art. ' * 40 + '\\par\n'
        source = (r'\documentclass{m20book}\begin{document}' + prose
                  + r'\m20artreserve[kind=horizontal,position=bottom]{bottom-art}'
                  + r'\begin{table*}[!b]\noindent\rule{100bp}{45bp}\par\end{table*}'
                  + prose * 12 + r'\end{document}')
        _, path = compile_source(source, 'horizontal-art-bottom-proof')
        art = next(p for p in positions(path) if p['id'] == 'bottom-art')
        self.assertAlmostEqual(art['y'] + art['height'], 720, delta=.1, msg=art)

    def test_art_waits_for_top_edge_after_an_earlier_table_float(self):
        _, path = compile_source(queued_table_source(following_prose=True),
                                 'horizontal-art-after-table-proof')
        records = positions(path)
        art = next(p for p in records if p['id'] == 'top-art')
        table = next(p for p in records if p['id'] == 'queued-table')
        self.assertLess(table['page'], art['page'])
        self.assertAlmostEqual(art['y'], 63, delta=.1, msg=art)
        self.assertAlmostEqual(art['width'], 490.4496, places=2)
        self.assertAlmostEqual(art['height'], 341.28, places=2)
        with fitz.open(path.with_suffix('.pdf')) as pdf:
            page = pdf[art['page'] - 1]
            # The visible dark panel must really occupy the top reserve, not
            # merely report a corrected metadata coordinate.
            pixels = page.get_pixmap(dpi=72, alpha=False)
            for y in range(85, 110):
                self.assertTrue(all(c < 80 for c in pixels.pixel(300, y)), (y, pixels.pixel(300, y)))

    def test_horizontal_enqueue_keeps_heading_stats_and_prose_in_live_column(self):
        # A nearly full left column and a forced right-column heading recreate
        # a generic device entry without depending on upstream chapter pagination.
        source = (r'\documentclass{m20book}\begin{document}'
                  r'\noindent\rule{1bp}{590bp}\par\columnbreak'
                  r'\subsection{Survey Device}\m20anchor{device-heading}'
                  r'\begin{m20statblock}'
                  r'\mTwentyStatEntry{\textbf{Type}: Instrument | \textbf{Range}: 3 | '
                  r'\textbf{Capacity}: 6 | \textbf{Cost}: 2}'
                  r'\end{m20statblock}'
                  r'\m20artreserve[kind=horizontal,position=top]{device-horizontal}'
                  r'\m20anchor{device-prose}A compact measuring instrument, stored in a padded case. '
                  + 'Its narrative continues in the same live column. ' * 90
                  + r'\end{document}')
        _, path = compile_source(source, 'horizontal-art-live-column-proof')
        records = positions(path)
        heading = next(p for p in records if p['id'] == 'device-heading')
        prose = next(p for p in records if p['id'] == 'device-prose')
        self.assertEqual(prose['page'], heading['page'])
        self.assertAlmostEqual(prose['x'], heading['x'], delta=1)
        with fitz.open(path.with_suffix('.pdf')) as pdf:
            page = pdf[heading['page'] - 1]
            last_stat = page.search_for('Cost: 2')[0]
            first_prose = page.search_for('A compact measuring instrument')[0]
            self.assertLess(first_prose.y0 - last_stat.y1, 28)


if __name__ == '__main__':
    unittest.main()
