#!/usr/bin/env python3
"""Render actual PDF pages and selected EPUB reflow cases with MuPDF for QA."""
import argparse
import json
from pathlib import Path
import fitz
from PIL import Image,ImageDraw
from preflight import ROOT,workspace_path

def contact(paths,output):
    width=240;height=340;columns=4
    sheet=Image.new('RGB',(columns*width,((len(paths)+columns-1)//columns)*height),'#dddddd')
    draw=ImageDraw.Draw(sheet)
    for index,path in enumerate(paths):
        with Image.open(path) as img:
            img.thumbnail((width-12,height-30));x=(index%columns)*width+6;y=(index//columns)*height+22
            sheet.paste(img,(x,y));draw.text((x,y-17),path.stem,fill='black')
    sheet.save(output)

def review(pdf,epub,out):
    out=workspace_path(out);out.mkdir(parents=True,exist_ok=True)
    report={'renderer':'PyMuPDF '+fitz.VersionBind+' / MuPDF '+fitz.VersionFitz,'pdf':{},'epub_views':[],'limits':['Software reflow preview, not a hardware e-reader or reader application compatibility certification.','Navigation and note backlinks are checked independently in build verification.']}
    with fitz.open(pdf) as document:
        paths=[]
        for index,page in enumerate(document,1):
            path=out/f'pdf-{index:03d}.png';page.get_pixmap(matrix=fitz.Matrix(1.2,1.2),alpha=False).save(path);paths.append(path)
        contact(paths,out/'pdf-contact.png');report['pdf']={'pages':len(document),'all_pages_rendered':True}
    needles=['SEM-N-001','SEM-N-055','SEM-W-001','SEM-D-001','SEM-D-026','SEM-CELL-001','SEM-CELL-070','SEM-ART-CAPTION','SEM-RECORD-NAME','SEM-TABLE-NOTE','SEM-LAST']
    for name,width,height,size,css,gray in [('narrow',360,640,16,'',False),('wide',800,1000,16,'',False),('enlarged',360,640,24,'',False),('grayscale',360,640,18,'',True),('dark',360,640,18,'body {color: #eeeeee; background-color: #161616;} a {color: #9ecbff;}',False)]:
        fitz.mupdf.fz_set_user_css(css)
        with fitz.open(epub) as document:
            document.layout(width=width,height=height,fontsize=size)
            texts=[p.get_text() for p in document];token_texts=[''.join(t.split()) for t in texts];selected={0,len(document)-1}
            for token in needles:
                selected.update(i for i,text in enumerate(token_texts) if token in text)
            paths=[]
            for index in sorted(selected):
                path=out/f'epub-{name}-{index+1:03d}.png'
                pix=document[index].get_pixmap(alpha=False);pix.save(path)
                if gray:
                    with Image.open(path) as img:img.convert('L').convert('RGB').save(path)
                paths.append(path)
            contact(paths,out/f'epub-{name}-contact.png')
            report['epub_views'].append({'name':name,'viewport':[width,height],'font_size':size,'reflow_pages':len(document),'review_pages':[i+1 for i in sorted(selected)],'cases_found':[t for t in needles if any(t in s for s in token_texts)]})
    fitz.mupdf.fz_set_user_css('')
    (out/'reader-review.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--pdf',default='build/specimen/pdf/specimen.pdf');p.add_argument('--epub',default='build/specimen/epub/specimen.epub');p.add_argument('--out',default='build/review')
    a=p.parse_args();print(json.dumps(review(Path(a.pdf),Path(a.epub),a.out),indent=2))
