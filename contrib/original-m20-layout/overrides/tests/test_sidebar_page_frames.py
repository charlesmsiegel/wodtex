"""One continuous frame per physical page, including spanning table bands."""
import collections
import re
import unittest

import fitz

from tests.test_layout_proof import compile_source, positions


class SidebarPageFrameTests(unittest.TestCase):
    def verify(self, path, ident, expected):
        frames = [r for r in positions(path) if r["id"] == ident
                  and r["kind"] in ("sidebar", "table-segment")]
        self.assertTrue(frames)
        counts = collections.Counter(r["page"] for r in frames)
        self.assertTrue(all(n == 1 for n in counts.values()), frames)
        self.assertTrue(all(r["height"] <= 657 for r in frames), frames)
        with fitz.open(path.with_suffix(".pdf")) as pdf:
            text = "\n".join(p.get_text() for p in pdf)
        for marker in expected:
            self.assertEqual(text.count(marker), 1, marker)
        return frames

    def test_text_table_text_share_one_frame_per_page(self):
        before = r"\newline ".join(f"PRE-{i:03d}" for i in range(20))
        after = r"\newline ".join(f"POST-{i:03d}" for i in range(140))
        table = "HEAD-A & HEAD-B \\\\ " + "".join(
            f"CELL-{i:03d} & Description {i} \\\\ " for i in range(7))
        source = (r"\documentclass{m20book}\begin{document}"
                  r"\begin{m20sidebarwide}[id=composite,columns=2]{Composite proof}"
                  + before + r"\par\begin{m20table}[head-rows=1,id=composite-table]{ll}"
                  + table + r"\end{m20table}" + after
                  + r"\par\end{m20sidebarwide}\end{document}")
        _, path = compile_source(source, "sidebar-composite-pages")
        markers = ([f"PRE-{i:03d}" for i in range(20)]
                   + [f"CELL-{i:03d}" for i in range(7)]
                   + [f"POST-{i:03d}" for i in range(140)])
        frames = self.verify(path, "composite", markers)
        self.assertGreaterEqual(len(frames), 2)
        self.assertTrue(all(r["columns"] == 2 for r in frames))
        table_position = next(r for r in positions(path) if r["id"] == "composite-table")
        frame = next(r for r in frames if r["page"] == table_position["page"])
        self.assertGreaterEqual(table_position["y"], frame["y"])
        self.assertLessEqual(table_position["y"], frame["y"] + frame["height"])

    def test_long_narrow_sidebar_continues_on_distinct_pages(self):
        body = r"\newline ".join(f"NARROW-{i:03d}" for i in range(120))
        source = (r"\documentclass{m20book}\begin{document}"
                  r"\begin{m20sidebar}[id=narrow-pages]{Narrow proof}" + body
                  + r"\par\end{m20sidebar}\end{document}")
        _, path = compile_source(source, "sidebar-narrow-pages")
        frames = self.verify(path, "narrow-pages", [f"NARROW-{i:03d}" for i in range(120)])
        self.assertGreaterEqual(len(frames), 2)


if __name__ == "__main__":
    unittest.main()
