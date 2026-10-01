#!/usr/bin/env python3
"""Copy authentic decorative content from pinned original M20 PDF."""
from pathlib import Path
import argparse, hashlib, re, json
import fitz
p=argparse.ArgumentParser();p.add_argument('template',type=Path);p.add_argument('--out',type=Path,default=Path('assets'));a=p.parse_args()
assert hashlib.sha256(a.template.read_bytes()).hexdigest()=='4c876e07b17f4a85877213d557b3f0236004bf6baa48d0bef708a68745e93df5'
a.out.mkdir(parents=True,exist_ok=True)
original=fitz.open(a.template)
def page_only(index,stream):
 d=fitz.open();d.insert_pdf(original,from_page=index,to_page=index)
 pg=d[0];contents=pg.get_contents();d.update_stream(contents[0],stream)
 for x in contents[1:]:d.update_stream(x,b'')
 return d

def save_clean(d,filename):
 assert not ''.join(p.get_text() for p in d).strip(),filename+' retains text'
 for p in d:p.clean_contents()
 target=a.out/filename;d.save(target,garbage=4,deflate=True)
 print(target,hashlib.sha256(target.read_bytes()).hexdigest())
 return {'file':str(target),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'bytes':target.stat().st_size}
manifest=[]
spread=fitz.open()
for index in [5,6]:
 d=page_only(index,b'q\n/GS0 gs\n0 TL/Fm0 Do\nQ\n');spread.insert_pdf(d)
manifest.append(save_clean(spread,'spread-border.original-template.pdf'))
# Original standalone interior title recto: genuine full-page purple background
# and original translucent logo panel, excluding placeholder text/Author outlines.
first=b''.join(original.xref_stream(x) for x in original[0].get_contents())
background=first[:first.index(b'EMC')+3]+b'\nQ\n'
manifest.append(save_clean(page_only(0,background),'sidebar-background.original-template.pdf'))
d=page_only(0,background)
# The Fm0 logo panel's fill and stroke are preserved; its two text spans removed.
form=next(x for x,n,inv,bb in d[0].get_xobjects() if n=='Fm0' and inv==0)
s=d.xref_stream(form);s=re.sub(rb'/Span <<.*?BDC\s*BT\b.*?ET\s*EMC',b'',s,flags=re.S)
d.update_stream(form,s)
manifest.append(save_clean(d,'interior-title.original-template.pdf'))
for index,form,name,crop,pattern in [
 (5,'Fm3','art-horizontal.original-template.pdf',fitz.Rect(66.5504,377.615,571.27,718.8949),'P2'),
 (6,'Fm1','art-vertical.original-template.pdf',fitz.Rect(53,60.4601,312.2,731.5399),'P0')]:
 s=b''.join(original.xref_stream(x) for x in original[index].get_contents())
 pos=s.rfind(('0 TL/'+form+' Do').encode())
 start=s.rfind(b'q\n0 0 612 792 re',0,pos)
 end=s.index(b'/Span',pos)
 fragment=b'q\n/CS0 CS\n'+s[start:end]+b'\nQ\n'
 d=page_only(index,fragment)
 assert not d[0].get_text().strip()
 cropped=fitz.open();pg=cropped.new_page(width=crop.width,height=crop.height)
 pg.show_pdf_page(pg.rect,d,0,clip=crop)
 manifest.append(save_clean(cropped,name))
(a.out/'spread-page-types.provenance.json').write_text(json.dumps({'source':str(a.template),'source_sha256':hashlib.sha256(a.template.read_bytes()).hexdigest(),'spread_pages':[6,7],'spread_master':'A-Master ud3','spread_asset':'M20 Two Page Spread.tif','title_page':1,'horizontal_art_page':6,'vertical_art_page':7,'outputs':manifest},indent=2)+'\n')
