import json
import subprocess
import unittest
from tests.support import ROOT

class ReferenceTests(unittest.TestCase):
    def test_native_navigation_index_and_rebuild_after_insertion(self):
        out=ROOT/'build/navigation'
        out.mkdir(parents=True,exist_ok=True)
        source=out/'navigation.tex'
        original=r'''\documentclass{m20book}\makeindex\title{Navigation}\author{Template}
\begin{document}\tableofcontents\chapter{First}\label{ch:first}
SORTTERM\index{Zed}\index{alpha@Álpha!child}\index{range|(}
\m20newpage RANGEEND\index{range|)}
\section[Energy]{Energy $E=mc^2$}\label{energy}
\chapter{Second}\label{ch:second}TARGET \ref{energy}; print page \pageref{ch:second}.
\printindex\end{document}'''
        source.write_text(original)
        command=['python3','scripts/build.py','--target','pdf','--source',str(source),'--out',str(out/'result')]
        p=subprocess.run(command,cwd=ROOT,text=True,capture_output=True,timeout=240)
        self.assertEqual(p.returncode,0,p.stdout[-4000:]+p.stderr)
        aux=(out/'result/pdf/navigation.aux').read_text()
        ind=(out/'result/pdf/navigation.ind').read_text()
        self.assertLess(ind.index('Álpha'),ind.index('Zed'))
        self.assertIn('child',ind)
        self.assertIn('--',ind)
        source.write_text(original.replace('SORTTERM',r'\m20newpage INSERTED \m20newpage SORTTERM'))
        p=subprocess.run(command,cwd=ROOT,text=True,capture_output=True,timeout=240)
        self.assertEqual(p.returncode,0,p.stdout[-4000:]+p.stderr)
        changed=(out/'result/pdf/navigation.aux').read_text()
        self.assertNotEqual(aux,changed)
        self.assertNotEqual(ind,(out/'result/pdf/navigation.ind').read_text())
