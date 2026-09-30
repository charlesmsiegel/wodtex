#!/usr/bin/env python3
"""Extract verified original template decorative forms without redesign."""
import argparse,hashlib
from pathlib import Path
import fitz
p=argparse.ArgumentParser();p.add_argument('template',type=Path);p.add_argument('--out',type=Path,default=Path('assets'));a=p.parse_args()
expected='4c876e07b17f4a85877213d557b3f0236004bf6baa48d0bef708a68745e93df5'
if hashlib.sha256(a.template.read_bytes()).hexdigest()!=expected:raise SystemExit('Original template PDF hash mismatch')
a.out.mkdir(parents=True,exist_ok=True);original=fitz.open(a.template)
for form,filename in [('Fm0','page_border.png'),('Fm1','chapter-opener.original-template.pdf')]:
 doc=fitz.open();doc.insert_pdf(original,from_page=4,to_page=4);page=doc[0]
 doc.update_stream(page.get_contents()[0],('q\n/GS0 gs\n0 TL/'+form+' Do\nQ\n').encode())
 if page.get_text().strip():raise SystemExit('Decorative extraction unexpectedly contains text')
 target=a.out/filename
 if target.suffix=='.png':page.get_pixmap(dpi=300,alpha=False).save(target)
 else:doc.save(target)
 print(target,hashlib.sha256(target.read_bytes()).hexdigest())
