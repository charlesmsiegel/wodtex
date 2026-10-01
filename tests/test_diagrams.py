import json
import subprocess
import unittest
import zipfile
from lxml import etree as E
import fitz
from tests.support import ROOT

class DiagramTests(unittest.TestCase):
    def test_native_tikz_is_visible_vector_content_in_both_outputs(self):
        out=ROOT/'build/native-diagram';out.mkdir(parents=True,exist_ok=True)
        source=out/'diagram.tex'
        source.write_text(r'''\documentclass{m20book}\usepackage{tikz}\begin{document}
Before.\begin{figure}\centering
\m20diagramalt{An arrow from Start to Finish}
\begin{tikzpicture}\node[draw,circle] (a) at (0,0) {Start};
\node[draw,circle] (b) at (3,0) {Finish};\draw[->] (a)--(b);\end{tikzpicture}
\caption{NATIVE-DIAGRAM-CAPTION}\end{figure}After.\end{document}''')
        p=subprocess.run(['python3','scripts/build.py','--target','all','--source',str(source),'--out',str(out/'result'),'--verify'],cwd=ROOT,text=True,capture_output=True,timeout=240)
        self.assertEqual(p.returncode,0,p.stdout[-4000:]+p.stderr)
        report=json.loads((out/'result/build-report.json').read_text())
        with fitz.open(report['targets']['pdf']['output']) as pdf:
            text=''.join(p.get_text() for p in pdf)
            for token in ('Start','Finish','NATIVE-DIAGRAM-CAPTION'):self.assertEqual(text.count(token),1)
        with zipfile.ZipFile(report['targets']['epub']['output']) as z:
            svgs=[n for n in z.namelist() if n.endswith('.svg')]
            self.assertEqual(len(svgs),1)
            svg=E.fromstring(z.read(svgs[0]));ids=set(svg.xpath('//@id'))
            for ref in svg.xpath('//@*[local-name()="href"]'):
                if ref.startswith('#'):self.assertIn(ref[1:],ids)
            self.assertTrue(svg.xpath('//*[local-name()="path"]'))
            roots=[E.fromstring(z.read(n)) for n in z.namelist() if n.endswith('.xhtml')]
            self.assertTrue(any(r.xpath('//*[local-name()="img" and @alt="An arrow from Start to Finish"]') for r in roots))
