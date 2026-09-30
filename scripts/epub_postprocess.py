"""Finish source-native TeX4ht semantics; never extract content from the PDF."""
from copy import deepcopy
import json
import hashlib
import mimetypes
import posixpath
from pathlib import Path
import re
import subprocess
import zipfile
from lxml import etree as E

X='http://www.w3.org/1999/xhtml'; M='http://www.w3.org/1998/Math/MathML'
S='http://www.w3.org/2000/svg'; OPF='http://www.idpf.org/2007/opf'; EPUB='http://www.idpf.org/2007/ops'
ROOT=Path(__file__).resolve().parents[1]
def local(e): return E.QName(e).localname if isinstance(e.tag,str) else ''
def text(e): return ' '.join(''.join(e.itertext()).split())
def element(tag,**attrs): return E.Element('{'+X+'}'+tag,attrs)
def closest(e,tag):
    return next((p for p in e.iterancestors() if local(p)==tag),None)
def cells(row): return [c for c in row if local(c) in ('td','th')]

def adapt_table(wrapper):
    table=next((e for e in wrapper.iter() if local(e)=='table'),None)
    if table is None: raise ValueError('M20_E_TABLE_STRUCTURE: semantic table was not converted')
    rows=[e for e in table.iter() if local(e)=='tr' and closest(e,'table') is table]
    count=int(wrapper.get('data-head-rows','0'))
    if count<0 or count>len(rows): raise ValueError('M20_E_TABLE_HEADERS: invalid heading row count')
    labels={}; columns={}; occupancy={}; associations={}
    for rownum,row in enumerate(rows):
        column=0
        for cell in cells(row):
            while occupancy.get((rownum,column)): column+=1
            span=int(cell.get('colspan','1')); rowspan=int(cell.get('rowspan','1'))
            indexes=list(range(column,column+span))
            for y in range(rownum,rownum+rowspan):
                for x in indexes: occupancy[(y,x)]=True
            if rownum<count:
                cell.tag='{'+X+'}th';cell.set('scope','col')
                ident=cell.get('id') or wrapper.get('id')+'-head-'+str(rownum)+'-'+str(column)
                cell.set('id',ident);labels[ident]=text(cell)
                for c in indexes: columns.setdefault(c,[]).append(ident)
            else:
                headings=list(dict.fromkeys(h for c in indexes for h in columns.get(c,[])))
                associations[cell]=headings
                if headings: cell.set('headers',' '.join(headings))
            column+=span
    for cell in table.iter():
        if cell.get('style'): cell.set('style',re.sub(r'(?:white-space|width|font-size)\s*:[^;]+;?','',cell.get('style')))
    if wrapper.get('data-mode')=='records':
        if not count: raise ValueError('M20_E_TABLE_HEADERS: records require explicit head-rows')
        records=element('div',**{'class':'m20-records'})
        header=element('div',**{'class':'m20-record-headings'})
        for row in rows[:count]:
            for cell in cells(row):
                cell.tag='{'+X+'}span';cell.attrib.pop('scope',None)
                header.append(cell)
        records.append(header)
        for row in rows[count:]:
            record=element('dl',**{'class':'m20-record'})
            for cell in cells(row):
                headings=associations[cell]
                term=element('dt');term.text=' / '.join(labels[h] for h in headings)
                cell.tag='{'+X+'}dd';cell.attrib.pop('headers',None)
                cell.attrib.pop('colspan',None);cell.attrib.pop('rowspan',None)
                cell.set('data-header-ids',' '.join(headings))
                record.extend([term,cell])
            records.append(record)
        table.getparent().replace(table,records)
    wrapper.attrib.pop('data-head-rows',None);wrapper.attrib.pop('data-mode',None)

def math_text(e):
    children=[c for c in e if isinstance(c.tag,str)]
    values=[math_text(c) for c in children]
    tag=local(e)
    if tag=='mfrac' and len(values)==2: return '('+values[0]+')/('+values[1]+')'
    if tag in ('msup','msub') and len(values)==2: return values[0]+('^' if tag=='msup' else '_')+'('+values[1]+')'
    if tag=='msubsup' and len(values)==3: return values[0]+'_('+values[1]+')^('+values[2]+')'
    if tag=='msqrt': return 'sqrt('+''.join(values)+')'
    if tag=='mroot' and len(values)==2: return 'root('+values[1]+', '+values[0]+')'
    if tag in ('mi','mn','mo','mtext'): return text(e)
    return ''.join(values) if children else (e.text or '').strip()

def adapt_math(roots):
    maths=[e for root in roots.values() for e in root.iter() if local(e)=='math']
    inputs=[]
    for math in maths:
        for e in math.iter():
            if isinstance(e.tag,str): e.tag='{'+M+'}'+local(e)
        def plain(e):
            if not isinstance(e.tag,str): return deepcopy(e)
            clone=E.Element(local(e),dict(e.attrib));clone.text=e.text;clone.tail=e.tail
            for child in e:clone.append(plain(child))
            return clone
        standalone=plain(math);standalone.set('xmlns',M)
        inputs.append({'mathml':E.tostring(standalone,encoding='unicode',with_tail=False),'display':math.get('display')=='block'})
    if not inputs: return 0
    node=__import__('shutil').which('node')
    if not node or not (ROOT/'.runtime/node/mathjax-full/js/mathjax.js').exists():
        raise ValueError('M20_E_MATH_FALLBACK: run preflight --prepare to install pinned MathJax and provide Node.js')
    result=subprocess.run([node,str(ROOT/'scripts/mathml_to_svg.cjs')],input=json.dumps(inputs),text=True,capture_output=True,timeout=120,check=True)
    outputs=json.loads(result.stdout)
    if len(outputs)!=len(maths): raise ValueError('M20_E_MATH_FALLBACK: incomplete formula output')
    for math,output in zip(maths,outputs):
        converted=E.fromstring(output.encode())
        svg=next((e for e in converted.iter() if local(e)=='svg'),None)
        if svg is None or any(e.get('data-mml-node')=='merror' for e in svg.iter()): raise ValueError('M20_E_MATH_FALLBACK: formula could not be faithfully rendered')
        svg.set('class','m20-math-svg');svg.set('aria-label',math_text(math))
        description=E.Element('{'+S+'}title');description.text=math_text(math);svg.insert(0,description)
        wrapper=element('span',**{'class':'m20-math'})
        native=element('span',**{'class':'m20-math-native'})
        parent=math.getparent();tail=math.tail;math.tail=None
        parent.replace(math,wrapper)
        for e in math.iter():
            if e.get('id'):
                anchor=element('span',id=e.get('id'));wrapper.append(anchor);e.attrib.pop('id')
        for e in svg.iter():e.attrib.pop('id',None)
        native.append(math);wrapper.extend([svg,native]);wrapper.tail=tail
    return len(maths)

def adapt_notes(roots):
    references={}
    for name,root in roots.items():
        for index,ref in enumerate(root.xpath('//*[local-name()="a" and @epub:type="noteref"]',namespaces={'epub':EPUB})):
            href=ref.get('href');file,_,fragment=href.partition('#')
            target=posixpath.normpath(posixpath.join(posixpath.dirname(name),file)) if file else name
            ident=ref.get('id') or 'm20-note-ref-'+str(index+1);ref.set('id',ident)
            owner=next((p for p in ref.iterancestors() if 'm20-sidebar' in p.get('class','').split()),root.find('{'+X+'}body'))
            references.setdefault((target,fragment),[]).append((name,ident,owner))
    for name,root in roots.items():
        body=root.find('{'+X+'}body')
        for note in list(root.xpath('//*[@epub:type="footnote"]',namespaces={'epub':EPUB})):
            refs=references.get((name,note.get('id')),[])
            if not refs: raise ValueError('M20_E_NOTE_TARGET: a note has no live reference')
            owner=refs[0][2]
            if owner is not None: owner.append(note)
            for source,ident,_ in refs:
                backlink=element('a',**{'class':'m20-backlink','href':posixpath.relpath(source,posixpath.dirname(name))+'#'+ident})
                backlink.set('{'+EPUB+'}type','backlink');backlink.text='Return to text';note.append(backlink)
        for section in list(root.xpath('//*[contains(concat(" ",@class," ")," footnotes ")]')):
            if not any(local(e)=='aside' for e in section): section.getparent().remove(section)

def adapt_epub(path,source_dir=None):
    with zipfile.ZipFile(path) as z:
        items={n:z.read(n) for n in z.namelist()}
    roots={n:E.fromstring(data) for n,data in items.items() if n.endswith(('.xhtml','.html'))}
    opfname=next(n for n in items if n.endswith('.opf'));package_base=posixpath.dirname(opfname)
    image_resources={};old_image_targets=set()
    for name,root in roots.items():
        for wrapper in root.xpath('//*[contains(concat(" ",@class," ")," m20-table ")]'): adapt_table(wrapper)
        for figure in root.xpath('//*[contains(concat(" ",@class," ")," m20-art ")]'):
            alt=figure.xpath('.//*[contains(concat(" ",@class," ")," m20-art-alt ")]')
            images=figure.xpath('.//*[local-name()="img"]')
            if not alt or not images: raise ValueError('M20_E_IMAGE_MISSING: meaningful art did not convert')
            images[0].set('alt',text(alt[0]));alt[0].getparent().remove(alt[0])
        for img in root.xpath('//*[local-name()="img"]'):
            source=img.get('src','')
            target=posixpath.normpath(posixpath.join(posixpath.dirname(name),source.lstrip('/')))
            data=items.get(target)
            if data is None:
                candidates=[Path(source),ROOT/source]
                if source_dir:candidates.append(Path(source_dir)/source)
                disk=next((p for p in candidates if p.is_file()),None)
                if disk is None:raise ValueError('M20_E_IMAGE_MISSING: '+source)
                data=disk.read_bytes()
            filename=hashlib.sha256(data).hexdigest()[:20]+Path(source).suffix.lower()
            resource=posixpath.join(package_base,'images',filename)
            items[resource]=data;image_resources[resource]=mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            img.set('src',posixpath.relpath(resource,posixpath.dirname(name)))
            old_image_targets.add(target)
    formulas=adapt_math(roots);adapt_notes(roots)
    destinations={}
    for name,root in roots.items():
        for e in root.iter():
            if e.get('id'):destinations.setdefault(e.get('id'),[]).append(name)
    for name,root in roots.items():
        own={e.get('id') for e in root.iter() if e.get('id')}
        for link in root.xpath('//*[local-name()="a" and @href]'):
            href=link.get('href')
            if href.startswith('#') and href[1:] not in own:
                targets=destinations.get(href[1:],[])
                if len(targets)!=1:raise ValueError('M20_E_LINK_TARGET: ambiguous or missing destination '+href)
                link.set('href',posixpath.relpath(targets[0],posixpath.dirname(name))+href)
    for name,root in roots.items(): items[name]=E.tostring(root,encoding='utf-8',xml_declaration=True)
    for name,data in list(items.items()):
        if name.endswith('.css'):
            css=re.sub(r'(?:font-size|font-family|line-height|background-color|color)\s*:[^;}]+;?','',data.decode())
            css+='\n.m20-math-native {display:none;}\n.m20-math-svg {max-width:100%; color:inherit;}\n@supports (math-style: normal) {.m20-math-native {display:inline;} .m20-math-svg {display:none;}}\n.m20-record dt {font-weight:bold;} .m20-record dd {margin-bottom:.5em;}\n'
            items[name]=css.encode()
        if name.endswith('.opf'):
            opf=E.fromstring(data)
            for meta in list(opf.xpath('//*[local-name()="meta" and (@property="dcterms:conformsTo" or @property="schema:accessibilitySummary" or @property="schema:accessModeSufficient")]')): meta.getparent().remove(meta)
            manifest=opf.xpath('//*[local-name()="manifest"]')[0]
            for entry in list(manifest):
                if entry.get('media-type','').startswith('image/'):manifest.remove(entry)
            for index,(resource,mime) in enumerate(sorted(image_resources.items())):
                entry=E.Element('{'+OPF+'}item',id='m20-image-'+str(index+1),href=posixpath.relpath(resource,posixpath.dirname(name)),**{'media-type':mime});manifest.append(entry)
            for entry in opf.xpath('//*[local-name()="manifest"]/*'):
                target=posixpath.normpath(posixpath.join(posixpath.dirname(name),entry.get('href','')))
                if target in roots:
                    props=set(entry.get('properties','').split())-{'svg','mathml'}
                    if any(local(e)=='math' for e in roots[target].iter()):props.add('mathml')
                    if any(local(e)=='svg' for e in roots[target].iter()):props.add('svg')
                    if props:entry.set('properties',' '.join(sorted(props)))
                    else:entry.attrib.pop('properties',None)
            items[name]=E.tostring(opf,encoding='utf-8',xml_declaration=True)
    for old in old_image_targets:
        if old not in image_resources:items.pop(old,None)
    temp=Path(str(path)+'.tmp')
    with zipfile.ZipFile(temp,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for name in ['mimetype']+sorted(n for n in items if n!='mimetype'):
            info=zipfile.ZipInfo(name,(2026,9,30,0,0,0));info.compress_type=zipfile.ZIP_STORED if name=='mimetype' else zipfile.ZIP_DEFLATED
            z.writestr(info,items[name])
    temp.replace(path)
    return {'formulas':formulas}
