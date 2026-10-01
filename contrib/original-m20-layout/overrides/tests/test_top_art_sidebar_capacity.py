"""Settled native top floats reduce the outside-body sidebar split capacity."""
import unittest

import fitz

from tests.support import ROOT
from tests.test_layout_proof import compile_source, positions


def top_art_sidebar_source():
    """Admit a native top reserve before a long, table-bearing wide sidebar."""
    paragraph = (
        'The survey team records each measurement before returning to the central office. '
        'A careful account preserves the evidence and gives the next team a useful starting point. '
        'Every route has a reference marker, and every report includes enough detail for an independent review. '
    ) + r'\par' + '\n'
    table = r'''\begin{m20table}[id=sidebar-table,width=container,head-rows=1]{lll}
Record & Category & Result \\
Sample one & Short route & Verified \\
Sample two & Long route & Pending \\
Sample three & Central route & Verified \\
\end{m20table}'''
    return (r'\documentclass{m20book}\begin{document}'
            r'\m20artreserve[kind=horizontal,position=top]{sidebar-top-art}'
            + paragraph * 14
            + r'\begin{m20sidebarwide}[id=sample-sidebar,place=flow,breakable=true,columns=2]{Extended Survey Notes}'
            + paragraph * 8 + table + paragraph * 20
            + r'\end{m20sidebarwide}\end{document}')


class TopArtSidebarCapacityTests(unittest.TestCase):
    def test_long_wide_sidebar_splits_within_native_top_art_page_room(self):
        # Body prose admits the pending native reserve before the sidebar
        # closes the live columns. Its split budget must retain that reserve.
        _, path = compile_source(top_art_sidebar_source(),
                                 'top-art-wide-sidebar-capacity-proof')
        records = positions(path)
        art = next(p for p in records if p['id'] == 'sidebar-top-art')
        frames = [p for p in records if p['kind'] in ('sidebar', 'table-segment')]
        self.assertGreaterEqual(len(frames), 2)
        self.assertTrue(all(frame['columns'] == 2 for frame in frames))
        table = next(p for p in records if p['id'] == 'sidebar-table')
        self.assertGreater(table['usable'], 400, 'The table must span both internal columns')
        shared = [p for p in frames if p['page'] == art['page']]
        self.assertTrue(shared, 'A blanket page clear must not isolate the illustration')
        for frame in frames:
            self.assertLessEqual(frame['y'] + frame['height'], 720.1, frame)
        for frame in shared:
            self.assertGreaterEqual(frame['y'], art['y'] + art['height'], frame)
        with fitz.open(path.with_suffix('.pdf')) as pdf:
            art_page = pdf[art['page'] - 1]
            self.assertIn('Extended Survey Notes', art_page.get_text())
            # Inspect a real raster rather than trusting a corrected m20pos
            # number alone: the frame must not darken the outer folio region.
            pixels = art_page.get_pixmap(dpi=72, alpha=False)
            with fitz.open(ROOT / 'assets/spread-border.original-template.pdf') as border:
                reference = border[0 if art['page'] % 2 == 0 else 1].get_pixmap(dpi=72, alpha=False)
                for x in range(180, 440):
                    self.assertLess(sum(abs(a - b) for a, b in zip(
                        pixels.pixel(x, 745), reference.pixel(x, 745))), 6)


if __name__ == '__main__':
    unittest.main()
