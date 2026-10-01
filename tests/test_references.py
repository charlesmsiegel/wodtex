import json
import subprocess
import unittest
from tests.support import ROOT
from tests.test_layout_proof import compile_source
import importlib.util
import fitz
import re

class ReferenceTests(unittest.TestCase):
    def test_matter_transitions_preserve_native_chapter_numbering(self):
        _,path=compile_source(r'''\documentclass{m20book}\begin{document}
\frontmatter\chapter{Preface}FRONT-COUNTER-\arabic{chapter}
\mainmatter\chapter{Main}MAIN-COUNTER-\arabic{chapter}
\backmatter\chapter{Afterword}BACK-COUNTER-\arabic{chapter}
\end{document}''','matter-counters')
        with fitz.open(path.with_suffix('.pdf')) as pdf:
            text='\n'.join(page.get_text() for page in pdf)
        self.assertIn('FRONT-COUNTER-0',text)
        self.assertIn('MAIN-COUNTER-1',text)
        self.assertIn('BACK-COUNTER-1',text)

    def test_position_evidence_uses_physical_pages_with_frontmatter(self):
        _,path=compile_source(r'''\documentclass{m20book}\begin{document}
\frontmatter\m20anchor{front}FRONTMARK
\mainmatter\chapter{Main}\m20anchor{main}MAINMARK
\end{document}''','physical-pages')
        spec=importlib.util.spec_from_file_location('physicalverify',ROOT/'scripts/verify.py')
        v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
        records=v.shipped_positions(path.with_suffix('.m20pos'))
        with fitz.open(path.with_suffix('.pdf')) as pdf:
            for ident,token in [('front','FRONTMARK'),('main','MAINMARK')]:
                p=next(r for r in records if r['id']==ident)
                self.assertIn(token,pdf[p['page']-1].get_text())
        self.assertEqual(next(r for r in records if r['id']=='front')['page_label'],'i')
        self.assertEqual(next(r for r in records if r['id']=='main')['page_label'],'3')

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
        source.write_text(re.sub(r'\\index\{[^{}]*\}','',original))
        p=subprocess.run(command,cwd=ROOT,text=True,capture_output=True,timeout=240)
        self.assertEqual(p.returncode,0,p.stdout[-4000:]+p.stderr)
        self.assertFalse((out/'result/pdf/navigation.ind').exists(),'Deleting every index term must clear the old generated index')
