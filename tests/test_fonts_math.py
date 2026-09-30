import subprocess
import unittest
import fitz
from tests.test_layout_proof import compile_source

class FontMathTests(unittest.TestCase):
    def test_genuine_emphasis_scripts_and_legacy_math(self):
        source=r'''\documentclass{m20book}\begin{document}
\section{Languages}
Normal \textbf{BOLD} \textit{ITALIC} \textbf{\textit{BOLDITALIC}}.
\foreignlanguage{greek}{Ελληνικά} \foreignlanguage{russian}{Русский}
\foreignlanguage{hebrew}{שלום} \foreignlanguage{arabic}{مرحبا}
Combining \m20script{é} and $x_{i_j}^{2}+\frac{1}{1+x}$.
\begin{equation}\int_0^1 x^2\,dx=\frac13\end{equation}
\end{document}'''
        p,path=compile_source(source,'fonts-math')
        self.assertNotIn('Missing character:',p.stdout)
        self.assertNotIn('Some font shapes were not available',p.stdout)
        with fitz.open(path.with_suffix('.pdf')) as pdf:
            fonts={f[3] for page in pdf for f in page.get_fonts()}
        for face in ['GoudyOldStyleT-Regular','GoudyOldStyleT-Bold','GoudyOldStyleT-Italic','NotoSerif-BoldItalic']:
            self.assertTrue(any(face in f for f in fonts),face)

    def test_explicit_unicode_math(self):
        p,_=compile_source(r'\documentclass{m20book}\m20setup{math=unicode}\begin{document}$α+β=γ$\end{document}','unicode-math')
        self.assertNotIn('Missing character:',p.stdout)

    def test_unicode_math_cannot_be_preloaded_in_legacy_mode(self):
        p,_=compile_source(r'\documentclass{m20book}\usepackage{unicode-math}\begin{document}Mixed.\end{document}','mixed-math',False)
        self.assertNotEqual(p.returncode,0)
        self.assertIn('M20_E_MATH_MODE',p.stdout)
