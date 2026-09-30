import json
import subprocess
import unittest
import zipfile
from pathlib import Path
from lxml import etree
from PIL import Image,ImageDraw
from tests.support import ROOT

class EpubTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out=ROOT/'build/epub-semantics';cls.out.mkdir(parents=True,exist_ok=True)
        img=Image.new('RGB',(240,100),'white');d=ImageDraw.Draw(img)
        d.rectangle((10,10,75,90),fill='#395a8e');d.rectangle((90,10,150,90),fill='#b7892f');d.rectangle((165,10,230,90),fill='#5b784a')
        cls.image=cls.out/'diagram.png';img.save(cls.image)
        cls.source=cls.out/'semantics.tex'
        cls.source.write_text(r'''\documentclass{m20book}\makeindex\title{Semantic proof}\author{Template}
\begin{document}\maketitle\tableofcontents\chapter{Meaning}\label{meaning}
BODY-MARKER\footnote{BODY-NOTE} \index{semantic@Semantic!destination}
\begin{m20sidebarwide}[columns=2,id=aside]{Semantic aside}ASIDE-BEFORE
\begin{m20table}[id=cells,head-rows=1]{ll}HEAD-A & HEAD-B \\ CELL-A & CELL-B \\ \end{m20table}
ASIDE-AFTER\m20note{SIDE-NOTE}\end{m20sidebarwide}
\begin{m20table}[id=records,head-rows=1,epub=records]{ll}NAME & VALUE \\ ROW-NAME & ROW-VALUE \\ \end{m20table}
\m20artreserve[image={'''+cls.image.as_posix()+r'''},alt={Three colored panels},caption={ART-CAPTION},credit={ART-CREDIT}]{art}
\m20artreserve{print-only-empty}
FORMULA-ONE $x^2+\frac12$ and \begin{equation}a^2+b^2=c^2\end{equation}
Reference \ref{meaning}; location \pageref{meaning}.\printindex\end{document}''')
        cls.result=subprocess.run(['python3','scripts/build.py','--target','epub','--source',str(cls.source),'--out',str(cls.out/'result')],cwd=ROOT,text=True,capture_output=True,timeout=240)
        cls.epub=cls.out/'result/epub/semantics.epub'

    def roots(self):
        self.assertEqual(self.result.returncode,0,self.result.stdout[-5000:]+self.result.stderr)
        with zipfile.ZipFile(self.epub) as z:
            return [etree.fromstring(z.read(n)) for n in z.namelist() if n.endswith(('.xhtml','.html'))]

    def test_reading_order_table_headers_and_records(self):
        roots=self.roots();text=''.join(''.join(r.itertext()) for r in roots)
        self.assertLess(text.index('ASIDE-BEFORE'),text.index('CELL-A'))
        self.assertLess(text.index('CELL-B'),text.index('ASIDE-AFTER'))
        table=next(e for r in roots for e in r.iter() if e.get('id')=='cells')
        self.assertEqual(len(table.xpath('.//*[local-name()="th"]')),2)
        self.assertTrue(table.xpath('.//*[local-name()="td" and @headers]'))
        record=next(e for r in roots for e in r.iter() if e.get('id')=='records')
        self.assertTrue(record.xpath('.//*[local-name()="dt"]'))
        for token in ['HEAD-A','HEAD-B','CELL-A','CELL-B','ROW-NAME','ROW-VALUE']:
            self.assertEqual(text.count(token),1,token)
        self.assertTrue(record.xpath('.//*[local-name()="dd" and @data-header-ids]'))

    def test_art_metadata_and_no_print_decoration(self):
        roots=self.roots();text=''.join(''.join(r.itertext()) for r in roots)
        images=[e for r in roots for e in r.iter() if isinstance(e.tag,str) and etree.QName(e).localname=='img']
        self.assertTrue(any(e.get('alt')=='Three colored panels' for e in images))
        self.assertIn('ART-CAPTION',text);self.assertIn('ART-CREDIT',text)
        with zipfile.ZipFile(self.epub) as z:
            self.assertFalse(any('texture' in n or 'page_border' in n for n in z.namelist()))

    def test_math_notes_and_index_links(self):
        roots=self.roots();text=''.join(''.join(r.itertext()) for r in roots)
        self.assertEqual(sum(len(r.xpath('//*[local-name()="math"]')) for r in roots),2)
        for token in ['BODY-NOTE','SIDE-NOTE']:self.assertEqual(text.count(token),1)
        self.assertTrue(any(r.xpath('//*[local-name()="a" and contains(@href,"#")]') for r in roots))
        self.assertIn('destination',text)

    def test_unknown_environment_and_command_fail(self):
        for body in [r'\newenvironment{mystery}{}{}\begin{document}\begin{mystery}CONTENT\end{mystery}',r'\newcommand{\mystery}{CONTENT}\begin{document}\mystery']:
            source=self.out/'unknown.tex';source.write_text(r'\documentclass{m20book}'+body+r'\end{document}')
            p=subprocess.run(['python3','scripts/build.py','--target','epub','--source',str(source),'--out',str(self.out/'unknown-result')],cwd=ROOT,text=True,capture_output=True,timeout=60)
            self.assertNotEqual(p.returncode,0)
            self.assertIn('M20_E_EPUB_UNMAPPED_CONTENT',p.stdout)
