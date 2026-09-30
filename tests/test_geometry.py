import unittest
import math
import fitz
from tests.test_layout_proof import compile_source

class GeometryTests(unittest.TestCase):
    def test_first_paragraph_uses_its_independent_glyph_scale(self):
        _,path=compile_source(r'\documentclass{m20book}\begin{document}\section{Scale}FIRSTPARAGRAPH regular text.\par SECONDPARAGRAPH regular text.\par\end{document}','paragraph-scale')
        with fitz.open(path.with_suffix('.pdf')) as pdf:
            spans=[s for p in pdf for b in p.get_text('dict',flags=fitz.TEXTFLAGS_DICT & ~fitz.TEXT_PRESERVE_IMAGES)['blocks'] for l in b.get('lines',[]) for s in l['spans']]
        first=next(s for s in spans if 'FIRSTPARAGRAPH' in s['text'])
        second=next(s for s in spans if 'SECONDPARAGRAPH' in s['text'])
        self.assertAlmostEqual(first['size'],10,places=2)
        # MuPDF reports the geometric mean of the glyph transform's axes.
        # Vertical .98 with preserved horizontal width reports sqrt(.98).
        self.assertAlmostEqual(second['size'],10*math.sqrt(.98),delta=.005)
