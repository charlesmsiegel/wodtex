"""Real sidebar splits must respect paragraph endpoints without stretching."""
import re
import unittest

import fitz

from tests.test_layout_proof import compile_source, positions


class SidebarParagraphBreakTests(unittest.TestCase):
    def compile_paragraph(self, name, available, lines, first_available=None):
        paragraph = r"\newline ".join(f"PARA-{i:02d}" for i in range(lines))
        first_available = available if first_available is None else first_available
        source = (
            r"\documentclass{m20book}\makeatletter"
            r"\newcount\sidebarTestRegion"
            r"\renewcommand\mTwentyRemaining{"
            r"\ifnum\sidebarTestRegion=0 "
            f"\\mTwentyAvailable={first_available}bp "
            r"\else "
            f"\\mTwentyAvailable={available}bp "
            r"\fi}"
            r"\renewcommand\mTwentyAdvance{\advance\sidebarTestRegion1\newpage}"
            r"\makeatother\begin{document}\m20bodyend"
            # Neutralize inherited body policy: the galley needs its own policy.
            r"\clubpenalty=0\widowpenalty=0\displaywidowpenalty=0"
            r"\begin{m20sidebar}[id=paragraph-break]{Endpoint proof}"
            r"\typeout{SIDEBAR-POLICY:\the\clubpenalty,\the\widowpenalty,\the\displaywidowpenalty}"
            + paragraph
            + r"\par\end{m20sidebar}"
            r"\typeout{OUTSIDE-POLICY:\the\clubpenalty,\the\widowpenalty,\the\displaywidowpenalty}"
            r"\end{document}"
        )
        _, path = compile_source(source, name)
        with fitz.open(path.with_suffix(".pdf")) as pdf:
            chunks = [re.findall(r"PARA-\d\d", p.get_text()) for p in pdf]
        return path, [chunk for chunk in chunks if chunk]

    def test_sidebar_galley_sets_local_endpoint_penalties(self):
        path, _ = self.compile_paragraph("sidebar-local-penalties", 110, 4)
        log = path.with_suffix(".log").read_text()
        self.assertEqual(re.findall(r"SIDEBAR-POLICY:([^\n]+)", log),
                         ["10000,10000,10000"])
        self.assertEqual(re.findall(r"OUTSIDE-POLICY:([^\n]+)", log), ["0,0,0"])

    def test_sidebar_avoids_single_initial_line_in_short_region(self):
        path, chunks = self.compile_paragraph("sidebar-club", 126, 9, 84)
        self.assertEqual([x for chunk in chunks for x in chunk],
                         [f"PARA-{i:02d}" for i in range(9)])
        self.assertTrue(all(len(chunk) >= 2 for chunk in chunks), chunks)
        self.assertTrue(all(p["height"] <= 126 for p in positions(path)
                            if p["kind"] == "sidebar"))

    def test_sidebar_avoids_single_final_line(self):
        path, chunks = self.compile_paragraph("sidebar-widow", 103, 4)
        self.assertEqual([x for chunk in chunks for x in chunk],
                         [f"PARA-{i:02d}" for i in range(4)])
        self.assertGreaterEqual(len(chunks), 2, chunks)
        self.assertTrue(all(len(chunk) >= 2 for chunk in chunks), chunks)
        self.assertTrue(all(p["height"] <= 103 for p in positions(path)
                            if p["kind"] == "sidebar"))


if __name__ == "__main__":
    unittest.main()
