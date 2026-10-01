"""A short flow sidebar should move intact instead of creating continuations."""
import re
import unittest

import fitz

from tests.test_layout_proof import compile_source, positions


class SidebarKeepTogetherTests(unittest.TestCase):
    def compile_sidebar(self, name, lines=20, environment="m20sidebar", options=""):
        paragraph = r"\newline ".join(f"KEEP-{i:03d}" for i in range(lines))
        source = (
            r"\documentclass{m20book}\makeatletter"
            r"\newcount\sidebarTestRegion"
            r"\renewcommand\mTwentyRemaining{"
            r"\ifnum\sidebarTestRegion=0 \mTwentyAvailable=200bp "
            r"\else\mTwentyAvailable=650bp\fi}"
            r"\renewcommand\mTwentyAdvance{\advance\sidebarTestRegion1\newpage}"
            r"\makeatother\begin{document}\m20bodyend"
            r"\null\par\m20anchor{keep-before}"
            + "\\begin{" + environment + "}[id=keep," + options + "]{Keep proof}"
            + paragraph
            + "\\par\\end{" + environment + "}\\end{document}"
        )
        _, path = compile_source(source, name)
        with fitz.open(path.with_suffix(".pdf")) as pdf:
            markers = [m for page in pdf for m in re.findall(r"KEEP-\d\d\d", page.get_text())]
        self.assertEqual(markers, [f"KEEP-{i:03d}" for i in range(lines)])
        return path, positions(path)

    def test_short_flow_sidebar_moves_intact_to_next_region(self):
        _, p = self.compile_sidebar("sidebar-keep-narrow")
        frames = [row for row in p if row["id"] == "keep"]
        anchor = next(row for row in p if row["id"] == "keep-before")
        self.assertEqual(len(frames), 1, frames)
        self.assertEqual(frames[0]["page"], anchor["page"] + 1)
        self.assertLessEqual(frames[0]["height"], 650)

    def test_short_wide_one_column_sidebar_keeps_requested_columns(self):
        _, p = self.compile_sidebar("sidebar-keep-wide1", environment="m20sidebarwide",
                                    options="columns=1,")
        frames = [row for row in p if row["id"] == "keep"]
        self.assertEqual(len(frames), 1, frames)
        self.assertEqual(frames[0]["columns"], 1)

    def test_short_wide_two_column_sidebar_moves_as_one_frame(self):
        _, p = self.compile_sidebar("sidebar-keep-wide2", lines=40,
                                    environment="m20sidebarwide", options="columns=2,")
        frames = [row for row in p if row["id"] == "keep"]
        self.assertEqual(len(frames), 1, frames)
        self.assertEqual(frames[0]["columns"], 2)
        self.assertLessEqual(frames[0]["height"], 650)

    def test_explicit_here_placement_retains_its_anchor(self):
        _, p = self.compile_sidebar("sidebar-keep-here", options="place=here,")
        frames = [row for row in p if row["id"] == "keep"]
        anchor = next(row for row in p if row["id"] == "keep-before")
        self.assertGreaterEqual(len(frames), 2, frames)
        self.assertEqual(frames[0]["page"], anchor["page"])

    def test_sidebar_taller_than_whole_region_remains_breakable(self):
        _, p = self.compile_sidebar("sidebar-keep-long", lines=80)
        frames = [row for row in p if row["id"] == "keep"]
        self.assertGreaterEqual(len(frames), 2, frames)
        self.assertTrue(all(row["height"] <= 650 for row in frames))

    def test_narrow_sidebar_moves_to_next_native_body_column(self):
        preceding = r"\newline ".join(f"PRE-{i:02d}" for i in range(40))
        paragraph = r"\newline ".join(f"KEEP-{i:03d}" for i in range(20))
        source = (r"\documentclass{m20book}\begin{document}" + preceding
                  + r"\par\m20anchor{native-before}"
                  + r"\begin{m20sidebar}[id=native-keep]{Keep proof}"
                  + paragraph + r"\par\end{m20sidebar}\end{document}")
        _, path = compile_source(source, "sidebar-keep-native-column")
        p = positions(path)
        frames = [row for row in p if row["id"] == "native-keep"]
        anchor = next(row for row in p if row["id"] == "native-before")
        self.assertEqual(len(frames), 1, frames)
        self.assertEqual(frames[0]["page"], anchor["page"])
        self.assertGreater(frames[0]["x"], 300)


if __name__ == "__main__":
    unittest.main()
