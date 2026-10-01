"""Prove paragraph-cell compatibility with array's pre-tagging interface."""
import unittest
import shutil
import subprocess
from pathlib import Path
from tests import test_native_frontmatter as frontmatter

USER_SOURCE = frontmatter.USER_SOURCE


@unittest.skipUnless(shutil.which('lualatex'), 'LuaLaTeX required')
class NativeTableCompatibilityTests(unittest.TestCase):
    setUp = frontmatter.NativeFrontmatterTests.setUp
    render = frontmatter.NativeFrontmatterTests.render

    def test_current_packages_full_sidebar_table_flow(self):
        source = USER_SOURCE.replace(r"\documentclass{m20book}", r"\RequirePackage{array}\makeatletter\let\savedpcolumn\insert@pcolumn\makeatother\documentclass{m20book}\makeatletter\ifx\savedpcolumn\insert@pcolumn\else\errmessage{Modern paragraph insertion was overwritten}\fi\makeatother")
        source = source.replace(r"\end{document}", r"""
\begin{m20sidebar}[id=field-note,place=flow]{Field Note}
One-column sidebar prose with \textbf{genuine bold} and \emph{italic}.
\end{m20sidebar}
\begin{m20sidebarwide}[id=wide-note,columns=2,place=next-page]{A Wide Note}
Two internal columns. Long content continues with a repeated heading.
\m20sidebarbreak[page]
An explicit author-requested continuation.
\end{m20sidebarwide}
\begin{m20table}[id=example-table,head-rows=1,width=container]{ll}
Name & Description \\
First & A wrapped cell. \\
Second & Another value. \\
\end{m20table}
\begin{m20statblock}
\mTwentyStatEntry{\textbf{Ruin Type}: Feral Realm | \textbf{Structural Integrity}: 4}
\mTwentyStatEntry{\textbf{Primary Hazards}: Existing descriptive text.}
\end{m20statblock}
\end{document}""")
        with self.render(source, "table-sidebar-current") as doc:
            text = "".join(p.get_text() for p in doc)
            for content in ("genuine bold", "italic", "An explicit author-requested continuation.", "A wrapped cell.", "Another value.", "Feral Realm", "Existing descriptive text."):
                self.assertEqual(1, text.count(content), content)

    def test_legacy_array_paragraph_cell_api(self):
        old = subprocess.check_output(['kpsewhich', 'array-2023-11-01.sty'], text=True).strip()
        color = subprocess.check_output(['kpsewhich', 'colortbl.sty'], text=True).strip()
        if not old or not color:
            self.skipTest('array 2.5g rollback and colortbl required')
        work = self.base / 'legacy-api'
        work.mkdir()
        shutil.copy2(old, work / 'array.sty')
        # Model the paragraph-cell API change introduced by colortbl 1.0k.
        # This is an isolated test fixture, not a shipped package replacement.
        text = Path(color).read_text()
        if r'\insert@pcolumn' not in text:
            text = text.replace(r'\insert@column', r'\insert@pcolumn')
        (work / 'colortbl.sty').write_text(text)
        source = USER_SOURCE.replace(r'\end{document}', r'''
\begin{m20table}[id=compat-table,head-rows=1,width=container]{ll}
Name & Description \\
First & A wrapped cell. \\
Second & Another value. \\
\end{m20table}
\end{document}''')
        (work / 'book.tex').write_text(source)
        for _ in range(2):
            result = subprocess.run(['lualatex', '-interaction=nonstopmode', '-halt-on-error', 'book.tex'], cwd=work, env=self.env, text=True, capture_output=True)
            self.assertEqual(0, result.returncode, result.stdout[-5000:])
        import fitz
        with fitz.open(work / 'book.pdf') as doc:
            text = ''.join(p.get_text() for p in doc)
            for cell in ('Name', 'Description', 'First', 'A wrapped cell.', 'Second', 'Another value.'):
                self.assertEqual(1, text.count(cell), cell)

