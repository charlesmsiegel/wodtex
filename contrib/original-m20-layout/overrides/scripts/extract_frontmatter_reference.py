#!/usr/bin/env python3
"""Extract exact original user-provided legal block and full-page placeholder."""
from pathlib import Path
import argparse,hashlib,json,re,fitz
p=argparse.ArgumentParser();p.add_argument('template',type=Path);p.add_argument('--out',type=Path,default=Path('assets'));a=p.parse_args()
sha=hashlib.sha256(a.template.read_bytes()).hexdigest()
assert sha=='4c876e07b17f4a85877213d557b3f0236004bf6baa48d0bef708a68745e93df5'
a.out.mkdir(parents=True,exist_ok=True);src=fitz.open(a.template);outputs=[]
legal=fitz.open();legal.insert_pdf(src,from_page=1,to_page=1)
page=legal[0];ids=page.get_contents();stream=b''.join(legal.xref_stream(x) for x in ids)
start=re.search(rb'/Span <<[^>]*?/MCID 16 >>BDC',stream).start()
tail=stream[start:]
# The retained legal text originally inherits TT2/GS1 from the thanks paragraph.
# Reestablish that exact text state, without retaining any other page content.
stream=b'q\n/GS1 gs\n0 0 0 1 k\nBT\n/TT2 1 Tf\nET\n'+tail+b'\nQ\n'
legal.update_stream(ids[0],stream)
for x in ids[1:]:legal.update_stream(x,b'')
page.clean_contents()
# Only the four historical date glyphs become a dynamic document-header field.
# Redaction is transparent and limited to text; all remaining logo/legal ink stays.
page.add_redact_annot(fitz.Rect(291.78,631.19,309.64,642.37),fill=False)
page.apply_redactions(images=0,graphics=0,text=0)
fn=a.out/'credits-legal.original-template.pdf';legal.save(fn,garbage=4,deflate=True)
outputs.append({'file':str(fn),'sha256':hashlib.sha256(fn.read_bytes()).hexdigest(),'source_page':2,'elements':'original copyright with date glyphs left for dynamic field, links, White Wolf vector logo and address; no original title/footer/border'})
assert 'White Wolf Entertainment AB' in legal[0].get_text()
assert '2018' not in legal[0].get_text()
assert 'Credits' not in legal[0].get_text()
art=fitz.open();art.insert_pdf(src,from_page=3,to_page=3)
# Keep exact full-bleed pink art; label now uses the shared Goudy text role.
for xref,name,inv,bbox in art[0].get_xobjects():
    stream=art.xref_stream(xref)
    stream=re.sub(rb'/Span <<.*?>>BDC\s*BT\b.*?ET\s*EMC',b'',stream,flags=re.S)
    art.update_stream(xref,stream)
    art.xref_set_key(xref,'Resources/Font','null')
art[0].clean_contents()
assert not art[0].get_text().strip()
fn=a.out/'art-fullpage.original-template.pdf';art.save(fn,garbage=4,deflate=True)
outputs.append({'file':str(fn),'sha256':hashlib.sha256(fn.read_bytes()).hexdigest(),'source_page':4,'elements':'exact original CMYK pink background; dynamic shared-font label; no folio or decorative border'})
(a.out/'frontmatter-reference.provenance.json').write_text(json.dumps({'source_sha256':sha,'outputs':outputs},indent=2)+'\n')
print(json.dumps(outputs,indent=2))
