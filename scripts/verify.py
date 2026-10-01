"""Independent checks of rendered bounds, embedded fonts and live EPUB semantics."""
from __future__ import annotations
from collections import Counter
import json
from pathlib import Path
import posixpath
import re
import subprocess
import unicodedata
import hashlib
from urllib.parse import unquote,urlsplit
import zipfile
from lxml import etree as E
import fitz

ROOT=Path(__file__).resolve().parents[1]
def normalized(text):
    for old,new in {'\ufb00':'ff','\ufb01':'fi','\ufb02':'fl','\ufb03':'ffi','\ufb04':'ffl','\u00ad':''}.items():text=text.replace(old,new)
    return ' '.join(unicodedata.normalize('NFC',text).replace('\u00a0',' ').split())
def math_signature(element):
    def meaning(e):
        return [E.QName(e).localname,normalized(e.text or ''),
                sorted((k,v) for k,v in e.attrib.items() if k not in ('id','class','style','display')),
                [meaning(c) for c in e if isinstance(c.tag,str)]]
    return hashlib.sha256(json.dumps(meaning(element),ensure_ascii=False,separators=(',',':')).encode()).hexdigest()

def has_passage(result,passage):
    # Allow only source-confirmed line-end hyphenation within a known word.
    # An authored hyphen still must match a hyphen in the expected passage.
    raw=result.get('raw_text',result['text'])
    for old,new in {'\ufb00':'ff','\ufb01':'fi','\ufb02':'fl','\ufb03':'ffi','\ufb04':'ffl','\u00ad':''}.items():raw=raw.replace(old,new)
    raw=unicodedata.normalize('NFC',raw).replace('\u00a0',' ')
    pattern=''
    for index,char in enumerate(passage):
        if char.isspace():pattern+=r'\s+'
        else:
            if index and char.isalpha() and passage[index-1].isalpha():pattern+=r'(?:-\s*\n\s*)?'
            pattern+=re.escape(char)
    return bool(re.search(pattern,raw))
def shipped_positions(path):
    records=[]
    for line in path.read_text().splitlines():
        p=line.split('|')
        if len(p)<11:continue
        unit=65536*1.00375
        records.append(dict(id=p[0],page=int(p[1]),x=int(p[2])/unit,y=792-int(p[3])/unit,
                            width=int(p[4])/unit,usable=int(p[5])/unit,columns=int(p[6]),
                            kind=p[7],segment=int(p[8]),place=p[9],height=int(p[10])/unit,
                            page_label=p[11] if len(p)>11 else p[1],
                            layout_page=int(p[12]) if len(p)>12 else int(p[1])))
    return records
def verify_pdf(path):
    errors=[];text=[];prose=[]
    with fitz.open(path) as pdf:
        for number,page in enumerate(pdf,1):
            if abs(page.rect.width-612)>.02 or abs(page.rect.height-792)>.02:errors.append(f'Page {number}: incorrect media size')
            text.append(page.get_text())
            for block in page.get_text('dict',flags=fitz.TEXTFLAGS_DICT & ~fitz.TEXT_PRESERVE_IMAGES)['blocks']:
                for line in block.get('lines',[]):
                    passage_line=[]
                    for span in line['spans']:
                        r=fitz.Rect(span['bbox'])
                        if r.x0<0 or r.y0<0 or r.x1>612.1 or r.y1>792.1:errors.append(f'Page {number}: text clipped at page edge: {span["text"][:50]}')
                        if r.y0>=61 and r.y1<=722 and 'abbess' not in span['font'].lower():passage_line.append(span['text'])
                    if passage_line:prose.append(''.join(passage_line))
        pages=len(pdf)
    fonts=subprocess.check_output(['pdffonts',str(path)],text=True)
    for line in fonts.splitlines()[2:]:
        match=re.search(r'\s(yes|no)\s+(yes|no)\s+(yes|no)\s+\d+\s+\d+\s*$',line)
        if match and match.group(1)!='yes':errors.append('Unembedded font: '+line.split()[0])
        if 'Type 3' in line:errors.append('Rasterized font: '+line.split()[0])
    posfile=path.with_suffix('.m20pos');positions=shipped_positions(posfile) if posfile.exists() else []
    for p in positions:
        if p['kind'] not in ('art','sidebar','table-segment'):continue
        margin=54 if p['layout_page']%2 else 67.5504
        if p['x']<margin-2 or p['x']+p['width']>margin+490.4496+2 or p['y']<61 or p['y']+p['height']>722:
            errors.append('Region outside body bounds: '+str(p))
    log=path.with_suffix('.log').read_text(errors='replace')
    warnings=[l.strip() for l in log.splitlines() if l.startswith(('Overfull','Underfull'))]
    for line in warnings:
        if line.startswith('Overfull'):errors.append('Unreviewed layout overflow: '+line)
    return dict(errors=errors,warnings=warnings,pages=pages,fonts_embedded=not any('font' in e.lower() for e in errors),positions=positions,text=normalized('\n'.join(text)),raw_text='\n'.join(prose))
def verify_epub(path):
    errors=[];ids={};links=[];text=[];asides=[];art=[];tables=[];formulas=0;fallbacks=0;backlinks=0;formula_signatures=[]
    with zipfile.ZipFile(path) as z:
        names=set(z.namelist())
        container=E.fromstring(z.read('META-INF/container.xml'))
        opfname=container.xpath('//*[local-name()="rootfile"]')[0].get('full-path')
        opf=E.fromstring(z.read(opfname));base=posixpath.dirname(opfname)
        manifest={e.get('id'):posixpath.normpath(posixpath.join(base,e.get('href'))) for e in opf.xpath('//*[local-name()="manifest"]/*')}
        order=[manifest[e.get('idref')] for e in opf.xpath('//*[local-name()="spine"]/*')]
        for name in sorted(names):
            if not name.endswith(('.xhtml','.html')):continue
            try:root=E.fromstring(z.read(name))
            except E.XMLSyntaxError as exc:errors.append('Invalid XHTML '+name+': '+str(exc));continue
            own_ids=[e.get('id') for e in root.iter() if e.get('id')]
            duplicate=[k for k,v in Counter(own_ids).items() if v>1]
            if duplicate:errors.append('Duplicate IDs in '+name+': '+str(duplicate))
            ids[name]=set(own_ids)
            if name in order:text.append((order.index(name),normalized(''.join(root.itertext()))))
            for e in root.iter():
                if not isinstance(e.tag,str):continue
                tag=E.QName(e).localname
                for key in ('href','src'):
                    if e.get(key):links.append((name,e.get(key)))
                if tag=='aside' and 'm20-sidebar' in e.get('class','').split():asides.append(e.get('id'))
                if tag=='figure' and 'm20-art' in e.get('class','').split():art.append(e.get('id'))
                if 'm20-table' in e.get('class','').split():tables.append(e.get('id'))
                if tag=='img' and not e.get('alt'):errors.append('Image missing alternative text: '+e.get('src',''))
                if tag=='math':
                    formulas+=1
                    formula_signatures.append(math_signature(e))
                    if E.QName(e).namespace!='http://www.w3.org/1998/Math/MathML':errors.append('Formula lacks MathML namespace')
                if tag=='svg' and 'm20-math-svg' in e.get('class','').split():fallbacks+=1
                if e.get('{http://www.idpf.org/2007/ops}type')=='backlink':backlinks+=1
        for source,url in links:
            parsed=urlsplit(url)
            if parsed.scheme or parsed.netloc:continue
            target=posixpath.normpath(posixpath.join(posixpath.dirname(source),unquote(parsed.path))) if parsed.path else source
            if target not in names:errors.append('Missing resource: '+source+' -> '+url)
            elif parsed.fragment and target in ids and unquote(parsed.fragment) not in ids[target]:errors.append('Missing link target: '+source+' -> '+url)
        for item,target in manifest.items():
            if target not in names:errors.append('Missing manifest resource: '+target)
    if formulas!=fallbacks:errors.append('MathML/SVG formula inventory differs')
    return dict(errors=errors,warnings=[],asides=asides,art=art,tables=tables,formulas=formulas,formula_signatures=formula_signatures,svg_fallbacks=fallbacks,note_backlinks=backlinks,text=' '.join(v for _,v in sorted(text)))
def verify_output(path,target):
    return verify_pdf(Path(path)) if target=='pdf' else verify_epub(Path(path))
def reconcile(pdf,epub,inventory):
    errors=[]
    for token in inventory['unique_tokens']:
        for name,result in [('pdf',pdf),('epub',epub)]:
            count=result['text'].count(token)
            if count!=1:errors.append(f'{name}: expected one {token}, found {count}')
    for kind in ['asides','art','tables']:
        if set(epub[kind])!=set(inventory[kind]):errors.append('EPUB '+kind+' inventory differs')
    if epub['formulas']!=inventory['formulas']:errors.append('Formula inventory differs')
    for name,result in [('pdf',pdf),('epub',epub)]:
        offsets=[result['text'].find(token) for token in inventory.get('ordered_tokens',[])]
        if offsets!=sorted(offsets) or any(offset<0 for offset in offsets):errors.append(name+': reading order differs')
        for passage in inventory.get('passages',[]):
            if not has_passage(result,passage):errors.append(name+': complete passage missing: '+passage[:80])
    if 'formula_signatures' in inventory and epub.get('formula_signatures')!=inventory['formula_signatures']:
        errors.append('EPUB native formula meaning/signature differs')
    return {'errors':errors,'equivalences':['Unicode NFC','nonbreaking/layout whitespace','standard Latin presentation ligatures','discretionary soft hyphens','source-confirmed line-end hyphenation inside known passage words','PDF prose extraction excludes running furniture and Abbess continuation titles'],
            'checked_unique_tokens':len(inventory['unique_tokens']),'checked_passages':len(inventory.get('passages',[])),
            'ordered_tokens':len(inventory.get('ordered_tokens',[])),'formula_signatures':len(inventory.get('formula_signatures',[]))}
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('output');p.add_argument('--target',choices=['pdf','epub'],required=True);args=p.parse_args()
    report=verify_output(args.output,args.target);report.pop('text',None);report.pop('raw_text',None)
    print(json.dumps(report,indent=2));raise SystemExit(bool(report['errors']))
