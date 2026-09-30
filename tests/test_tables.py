import subprocess
import unittest
import fitz
from tests.test_layout_proof import compile_source, positions

def document(body):
    return r'\documentclass{m20book}\makeindex\begin{document}'+body+r'\end{document}'

class TableTests(unittest.TestCase):
    def test_long_spanning_table_is_framed_and_conserved(self):
        rows = 'Heading A & Heading B \\\\ '+''.join(f'CELL-{i:03d} & Descriptive text in row {i}. \\\\ ' for i in range(85))
        _,path = compile_source(document(r'\begin{m20sidebarwide}[columns=2,id=table-flow]{Table flow}Before the table.\begin{m20table}[head-rows=1,id=long-table]{ll}'+rows+r'\end{m20table}After the table.\end{m20sidebarwide}'),'long-table')
        with fitz.open(path.with_suffix('.pdf')) as pdf:
            text='\n'.join(p.get_text() for p in pdf)
            spans=[s for p in pdf for b in p.get_text('dict',flags=fitz.TEXTFLAGS_DICT & ~fitz.TEXT_PRESERVE_IMAGES)['blocks'] if 'lines' in b for l in b['lines'] for s in l['spans']]
        for i in range(85): self.assertEqual(text.count(f'CELL-{i:03d}'),1)
        self.assertGreaterEqual(text.count('Heading A'),2)
        self.assertTrue(all(s['color']==0xffffff for s in spans if 'CELL-' in s['text']))

    def test_native_nested_cells_and_multicolumn_are_conserved(self):
        body=r'\m20bodyend\begin{m20table}[id=nested]{ll}A & B \\ \multicolumn{2}{l}{SPANNED-CELL} \\ Outer & \begin{tabular}{ll}INNER-A & INNER-B \\ INNER-C & INNER-D\end{tabular} \\ \end{m20table}'
        _,path=compile_source(document(body),'nested-table')
        text=subprocess.check_output(['pdftotext',str(path.with_suffix('.pdf')),'-'],text=True)
        for marker in ['SPANNED-CELL','INNER-A','INNER-B','INNER-C','INNER-D']:
            self.assertEqual(text.count(marker),1)

    def test_overheight_row_errors(self):
        p,_=compile_source(document(r'\begin{m20table}{ll}A & \rule{1bp}{750bp} \\ \end{m20table}'),'row-overheight',False)
        self.assertNotEqual(p.returncode,0)
        self.assertIn('M20_E_ROW_TOO_TALL',p.stdout)

    def test_unbreakable_sidebar_rejects_overheight_content(self):
        p,_=compile_source(document(r'\begin{m20sidebar}[breakable=false]{Atomic}\rule{1bp}{750bp}\end{m20sidebar}'),'atomic-sidebar',False)
        self.assertNotEqual(p.returncode,0)
        self.assertIn('M20_E_SIDEBAR_TOO_TALL',p.stdout)

    def test_column_width_and_local_notes_survive_spanning_blocks(self):
        body=r'\begin{m20sidebarwide}[columns=2,id=notes]{Notes}First note\m20note{SIDEBAR-ONE}.\begin{m20table}[width=column,scale=.5,align=right,id=half]{ll}A & B\m20note{TABLE-NOTE} \\ \end{m20table}Second note\m20note{SIDEBAR-TWO}.\end{m20sidebarwide}'
        _,path=compile_source(document(body),'width-notes')
        text=subprocess.check_output(['pdftotext',str(path.with_suffix('.pdf')),'-'],text=True)
        for marker in ['SIDEBAR-ONE','SIDEBAR-TWO','TABLE-NOTE']:
            self.assertEqual(text.count(marker),1)
        self.assertLess(text.index('TABLE-NOTE'),text.index('SIDEBAR-ONE'))
        p=next(p for p in positions(path) if p['id']=='half')
        self.assertAlmostEqual(p['width'],107.1124,places=2)

    def test_forced_first_atomic_row_needs_actual_space(self):
        body=r'\m20bodyend\null\vspace*{500bp}\begin{m20sidebarwide}[place=here]{At this anchor}\begin{m20table}{ll}A & \rule{1bp}{200bp} \\ \end{m20table}\end{m20sidebarwide}'
        p,_=compile_source(document(body),'row-at-anchor',False)
        self.assertNotEqual(p.returncode,0)
        self.assertIn('M20_E_PLACEMENT_UNAVAILABLE',p.stdout)

    def test_unbreakable_sidebar_counts_all_ordered_blocks(self):
        body=r'\begin{m20sidebarwide}[breakable=false]{Atomic blocks}\rule{1bp}{90bp}\begin{m20table}{ll}A & \rule{1bp}{500bp} \\ \end{m20table}\rule{1bp}{90bp}\end{m20sidebarwide}'
        p,_=compile_source(document(body),'atomic-blocks',False)
        self.assertNotEqual(p.returncode,0)
        self.assertIn('M20_E_SIDEBAR_TOO_TALL',p.stdout)

    def test_manual_page_break_advances_page(self):
        body=r'\begin{m20sidebar}[id=manual]{Manual}Before.\m20sidebarbreak[page]After.\end{m20sidebar}'
        _,path=compile_source(document(body),'manual-page')
        p=[p for p in positions(path) if p['id']=='manual']
        self.assertEqual(p[1]['page'],p[0]['page']+1)

    def test_full_width_passage_repeats_headers_without_leaking_into_aside(self):
        rows='PASSAGE-HEADING & Description \\\\ '+''.join(f'PASSAGE-{i:03d} & A native table row. \\\\ ' for i in range(90))
        _,path=compile_source(document(r'\begin{m20table}[head-rows=1]{ll}'+rows+r'\end{m20table}\begin{m20sidebar}{After table}'+('ASIDE-LINE. '+r'\par ')*90+r'\end{m20sidebar}'),'passage-table')
        with fitz.open(path.with_suffix('.pdf')) as pdf:
            text='\n'.join(p.get_text() for p in pdf)
            heading_pages=[i for i,p in enumerate(pdf) if 'PASSAGE-HEADING' in p.get_text()]
            aside_pages=[i for i,p in enumerate(pdf) if 'ASIDE-LINE' in p.get_text()]
        self.assertGreaterEqual(len(heading_pages),2)
        self.assertLessEqual(max(heading_pages),min(aside_pages))
        for i in range(90):self.assertEqual(text.count(f'PASSAGE-{i:03d}'),1)
