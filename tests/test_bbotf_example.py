"""Smoke tests for the optional BBotF Markdown specimen adapter.

Do not require the private BBotF repository or M20 font/layout resources.
"""

from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "bbotf"
CORE = (
    "rote", "wonder", "practice", "node", "grimoire-or-black-book", "labyrinth-chantry"
)


@unittest.skipUnless(shutil.which("pandoc"), "requires Pandoc")
class BbotfPandocSmokeTests(unittest.TestCase):
    def test_native_tables_unique_labels_and_optional_statblock(self):
        with tempfile.TemporaryDirectory() as td:
            temp = Path(td)
            source = temp / "templates" / "01-core"
            source.mkdir(parents=True)
            for name in CORE:
                (source / f"{name}.md").write_text(
                    f"# {name}\n\n## Systems\n\n| Trait | Value |\n| --- | --- |\n"
                    "| Rank | 3 |\n\n## Story Hooks\n\n- One hook.\n\n"
                    "::: statblock\n**Rank:** 3\n\n**Spheres:** Spirit 2\n:::\n",
                    encoding="utf-8",
                )
            out = temp / "tex"
            subprocess.run(
                [sys.executable, str(EXAMPLE / "prepare.py"), str(source.parent), "--out", str(out)],
                check=True, capture_output=True, text=True,
            )
            generated = [out / f"{name}.tex" for name in CORE]
            manifest = (out / "contents.tex").read_text(encoding="utf-8")
            for name in CORE:
                self.assertIn(f"\\input{{generated/{name}.tex}}", manifest)
            self.assertTrue(all(path.is_file() for path in generated))
            contents = [file.read_text(encoding="utf-8") for file in generated]
            combined = "\n".join(contents)
            self.assertEqual(combined.count("\\begin{booktable}"), 6)
            self.assertEqual(combined.count("\\begin{statblock}"), 6)
            self.assertNotIn("\\begin{longtable}", combined)
            for name, text in zip(CORE, contents):
                self.assertIn(f"id=bbotf-{name}-table-1", text)
                self.assertIn(f"\\label{{{name}-systems}}", text)
                self.assertIn("\\statentry{\\textbf{Rank:} 3}", text)


if __name__ == "__main__":
    unittest.main()