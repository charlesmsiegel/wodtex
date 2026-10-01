"""Real PDF ink proofs for the global stat-block emphasis role."""
import unittest

import fitz
import numpy as np

from tests.test_layout_proof import compile_source


SOURCE = r'''\documentclass{m20book}
\begin{document}\m20bodyend
Body before \textbf{BODY BOLD}.\par
\begin{minipage}{239.2248bp}
\begin{m20statblock}
\mTwentyStatEntry{H \textbf{H}}
\mTwentyStatEntry{x \textbf{x}}
\mTwentyStatEntry{\textbf{Ruin Type}: Feral Realm | \textbf{Structural Integrity}: 4}
\mTwentyStatEntry{\textbf{Primary Hazards}: Inhabitants (the realm's biological defenses are continuous and sophisticated), Spiritual Contamination (the life Resonance triggers magical responses in visitors that are not entirely under visitor control)}
\end{m20statblock}
\end{minipage}\par
Body after \textbf{BODY BOLD}.\par
{\mTwentySidebarFont SIDEBAR REGULAR \textbf{SIDEBAR BOLD}}\par
\clearpage
\section{SECTION HEADING}
\subsection{SUBSECTION HEADING}
\subsubsection{SUBSUBSECTION HEADING}
\begin{itemize}\item LIST REGULAR \textbf{LIST BOLD} \textit{LIST ITALIC}\end{itemize}
\begin{m20sidebar}[id=font-role-sidebar]{SIDEBAR HEADING}
SIDEBAR PROSE \textbf{SIDEBAR PROSE BOLD} \textit{SIDEBAR PROSE ITALIC}
\end{m20sidebar}
\m20bodyend
\begin{m20table}[head-rows=1,id=font-role-table]{ll}
TABLE LABEL A & TABLE LABEL B \\
TABLE CELL & \textit{TABLE ITALIC} \\
\end{m20table}
\end{document}'''


def spans(page, kind='dict'):
    return [span for block in page.get_text(kind)['blocks']
            for line in block.get('lines', []) for span in line['spans']]


def glyph_ink(page, char):
    # PDF span boxes describe font ascenders, not visible ink. Rasterize the
    # actual shipped glyph at 1200dpi and count ink inside its isolated cell.
    pixmap = page.get_pixmap(matrix=fitz.Matrix(1200 / 72, 1200 / 72),
                            clip=fitz.Rect(char['bbox']), alpha=False,
                            colorspace=fitz.csRGB)
    pixels = np.frombuffer(pixmap.samples, dtype=np.uint8).reshape(
        pixmap.height, pixmap.width, 3)
    # Ignore any black body ink in an overlapping font-metric box: all proof
    # glyphs are purple, which has blue > red > green channels.
    rgb = pixels.astype(np.int16)
    ink = ((rgb.min(axis=2) < 160) & (rgb[:, :, 2] > rgb[:, :, 0] + 10)
           & (rgb[:, :, 0] > rgb[:, :, 1] + 10))
    rows = np.flatnonzero(ink.any(axis=1))
    return (rows[-1] - rows[0] + 1) * 72 / 1200, int(ink.sum())


class StatFontHeightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.process, cls.path = compile_source(SOURCE, 'stat-font-height')

    def test_bold_and_regular_stat_glyphs_have_matching_visible_height(self):
        with fitz.open(self.path.with_suffix('.pdf')) as document:
            page = document[0]
            stat_spans = [span for span in spans(page, 'rawdict') if span['color']]
            # Each initial proof row contains exactly one regular and one
            # emphasized instance, without relying on PDF font bold flags.
            for letter in ('H', 'x'):
                chars = [(span, char) for span in stat_spans
                         for char in span['chars'] if char['c'] == letter][:2]
                self.assertEqual(len(chars), 2, letter)
                regular, bold = [glyph_ink(page, char) for _, char in chars]
                self.assertLessEqual(abs(bold[0] - regular[0]), .18,
                                     f'{letter}: regular {regular[0]:.2f}bp, bold {bold[0]:.2f}bp')
                self.assertGreater(bold[1], regular[1] * 1.10,
                                   'Emphasis must increase ink weight visibly')
                self.assertAlmostEqual(chars[0][0]['size'], chars[1][0]['size'], places=3)
                self.assertAlmostEqual(chars[0][1]['origin'][1], chars[1][1]['origin'][1], places=3)

    def test_all_prose_roles_use_genuine_goudy_old_style_faces(self):
        self.assertNotIn('Missing character:', self.process.stdout)
        self.assertNotIn('Some font shapes were not available', self.process.stdout)
        with fitz.open(self.path.with_suffix('.pdf')) as document:
            page_spans = spans(document[0])
            body = [span for span in page_spans if 'BODY BOLD' in span['text']]
            self.assertEqual(len(body), 2)
            self.assertTrue(all(span['font'] == 'GoudyOldStyleT-Bold' for span in body))
            sidebar = next(span for span in page_spans if 'SIDEBAR BOLD' in span['text'])
            self.assertEqual(sidebar['font'], 'GoudyOldStyleT-Bold')
            stat = [span for span in page_spans if span['color']]
            self.assertTrue(stat)
            self.assertTrue(all(abs(span['size'] - 10) < .001 for span in stat))
            regular = [span for span in stat if 'Feral Realm' in span['text']]
            self.assertTrue(regular)
            self.assertTrue(all(span['font'] == 'GoudyOldStyleT-Regular' for span in regular))
            self.assertTrue(all(span['font'].startswith('GoudyOldStyleT-') for span in stat))
            text = document[0].get_text()
            self.assertEqual(text.count('Ruin Type'), 1)
            self.assertEqual(text.count('Primary Hazards'), 1)

    def test_rendered_list_sidebar_and_table_fonts_follow_their_roles(self):
        with fitz.open(self.path.with_suffix('.pdf')) as document:
            all_spans = [span for page in document for span in spans(page)]
            for marker, face in [('SECTION HEADING', 'Abbess'),
                                 ('SUBSECTION HEADING', 'Abbess'),
                                 ('SUBSUBSECTION HEADING', 'Abbess'),
                                 ('SIDEBAR HEADING', 'Abbess'),
                                 ('LIST REGULAR', 'GoudyOldStyleT-Regular'),
                                 ('LIST BOLD', 'GoudyOldStyleT-Bold'),
                                 ('LIST ITALIC', 'GoudyOldStyleT-Italic'),
                                 ('SIDEBAR PROSE BOLD', 'GoudyOldStyleT-Bold'),
                                 ('SIDEBAR PROSE ITALIC', 'GoudyOldStyleT-Italic'),
                                 ('TABLE LABEL A', 'GoudyOldStyleT-Bold'),
                                 ('TABLE CELL', 'GoudyOldStyleT-Regular'),
                                 ('TABLE ITALIC', 'GoudyOldStyleT-Italic')]:
                matches = [span for span in all_spans if marker in span['text']]
                self.assertTrue(matches, marker)
                self.assertTrue(all(span['font'] == face for span in matches), (marker, matches))
