#!/usr/bin/env python3
"""Resolve source IDML inheritance and prepare byte-audited M20 resources."""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET
import zipfile
from fontTools.ttLib import TTFont
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / 'indesign-sample/template/M20/InDesign/M20 Template Interior'

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def node_record(element):
    return {'type':element.tag,'attributes':dict(element.attrib),'text':(element.text or '').strip(),'children':[node_record(c) for c in element]}

def geometry_records(xml):
    tree = ET.fromstring(xml); records=[]
    selected = {'Page','MarginPreference','TextFrame','Rectangle','Image','PDF','Polygon','GraphicLine','Oval','TextFramePreference','TextFrameBaselineOption','TransparencySetting','DropShadowSetting','InnerShadowSetting','GradientFeatherSetting','FrameFittingOption','AnchoredObjectSetting','PathPointType'}
    def walk(node,parent=None):
        identifier = node.get('Self',parent)
        if node.tag in selected:
            records.append({'type':node.tag,'parent':parent,'attributes':dict(node.attrib),'properties':properties(node)})
        for child in node:
            walk(child,identifier)
    walk(tree)
    return records

def properties(element):
    values = dict(element.attrib)
    prop = element.find('Properties')
    for child in prop if prop is not None else []:
        values[child.tag] = child.text.strip() if child.text and child.text.strip() else {'attributes':dict(child.attrib),'children':[ET.tostring(c,encoding='unicode') for c in child]}
    for child in element:
        if child.tag != 'Properties':
            values[child.tag] = node_record(child)
    return values

def active_properties(resolved):
    """Exclude stored effect parameters whose controlling feature is inactive."""
    active = dict(resolved)
    metadata = ('Self','Imported','StyleUniqueId','KeyboardShortcut','NextStyle','PreviewColor','BasedOn','EmptyNestedStyles','EmptyLineStyles','EmptyGrepStyles','SplitDocument','EmitCss')
    for key in metadata:
        active.pop(key,None)
    for prefix, switch in [('RuleAbove','RuleAbove'),('RuleBelow','RuleBelow'),('Underline','Underline'),('StrikeThrough','StrikeThru'),('Ruby','RubyFlag'),('Kenten','KentenKind'),('Warichu','Warichu'),('ParagraphShading','ParagraphShadingOn')]:
        if resolved.get(switch,'false') in ('false','None'):
            for key in list(active):
                if key.startswith(prefix) and key != switch:
                    active.pop(key)
    if resolved.get('StrokeColor') == 'Swatch/None':
        for key in list(active):
            if key.startswith('Stroke') and key != 'StrokeColor':
                active.pop(key)
    for kind in ('Fill','Stroke'):
        if not str(resolved.get(kind+'Color','')).startswith('Gradient/'):
            for key in list(active):
                if key.startswith('Gradient'+kind):active.pop(key)
    if resolved.get('DropCapLines','0') == '0':
        active.pop('DropCapCharacters',None)
    if resolved.get('BulletsAndNumberingListType','NoList') == 'NoList':
        for key in list(active):
            if key.startswith(('Bullet','Numbering')) and key != 'BulletsAndNumberingListType':active.pop(key)
    if resolved.get('SpanColumnType') != 'SpanColumns':
        for key in list(active):
            if key.startswith('SpanColumn') and key != 'SpanColumnType':active.pop(key)
    return active

def font_record(identifier, path, role, supplemental=False):
    path = Path(path); font = TTFont(path); cmap = font.getBestCmap(); names = font['name']
    def name(n):
        record = names.getDebugName(n); return record or ''
    family = name(16) or name(1); style = name(17) or name(2)
    flags = font['OS/2'].fsSelection if 'OS/2' in font else 0
    return {'id':identifier,'file':path.name,'source':str(path.relative_to(ROOT.parent)) if path.is_relative_to(ROOT.parent) else str(path),
            'sha256':digest(path),'bytes':path.stat().st_size,'family':family,'style':style,'postscript':name(6),
            'bold':bool(flags & 32),'italic':bool(flags & 1),'synthetic':False,'role':role,'supplemental':supplemental,
            'fsType':font['OS/2'].fsType if 'OS/2' in font else None,
            'license':name(13) or name(0),'license_url':name(14),
            'glyph_coverage':{'M20':all(ord(c) in cmap for c in 'M20 Mage The Ascension'),
                              'latin':all(ord(c) in cmap for c in 'abcXYZ012éäñ'),
                              'greek_cyrillic':all(ord(c) in cmap for c in 'ΕλληνικάРусский')},
            'glyph_count':len(cmap),'embedding_note':'Source license and fsType retained; this audit does not grant redistribution rights'}

def resolve_profile(idml_path):
    path = Path(idml_path).resolve()
    with zipfile.ZipFile(path) as archive:
        tree = ET.fromstring(archive.read('Resources/Styles.xml'))
        raw = {e.attrib['Self']:properties(e) for e in tree.iter() if e.tag in ('ParagraphStyle','CharacterStyle','ObjectStyle','TableStyle','CellStyle')}
        memo = {}
        def resolve(key, chain=()):
            if key in chain:raise ValueError('Cyclic IDML style inheritance: '+key)
            if key in memo:return memo[key]
            local = raw[key]; based = local.get('BasedOn'); parent = based
            if isinstance(parent,str) and not parent.startswith(('ParagraphStyle/','CharacterStyle/','ObjectStyle/','TableStyle/','CellStyle/')):
                parent = key.split('/')[0]+'/'+parent
            inherited = {}; inheritance = []
            if parent in raw:
                inherited = copy.deepcopy(resolve(parent,chain+(key,))['resolved'])
                inheritance = resolve(parent,chain+(key,))['inheritance']+[parent]
            inherited.update(local)
            memo[key] = {'local':local,'resolved':inherited,'active':active_properties(inherited),'inheritance':inheritance}
            return memo[key]
        styles = {key:resolve(key) for key in raw}
        resources = ET.fromstring(archive.read('Resources/Graphic.xml'))
        swatches = {e.get('Self'):ET.tostring(e,encoding='unicode') for e in resources.iter() if e.tag in ('Color','Gradient','StrokeStyle') and e.get('Self')}
        preferences = ET.fromstring(archive.read('Resources/Preferences.xml'))
        document_pref = next(preferences.iter('DocumentPreference'))
        page = [float(document_pref.get('PageWidth')),float(document_pref.get('PageHeight'))]
        masters = {name:geometry_records(archive.read(name)) for name in archive.namelist() if name.startswith('MasterSpreads/') and name.endswith('.xml')}
        spreads = {name:geometry_records(archive.read(name)) for name in archive.namelist() if name.startswith('Spreads/') and name.endswith('.xml')}
    margin = next(r['attributes'] for name, records in masters.items() for r in records if name.endswith('MasterSpread_ud3.xml') and r['type'] == 'MarginPreference')
    top, bottom, inner, outer, gutter = (float(margin[k]) for k in ('Top','Bottom','Left','Right','ColumnGutter'))
    body_width = page[0]-inner-outer; body_height=page[1]-top-bottom
    geometry={'body_width':round(body_width,4),'body_height':body_height,'top':top,'inner':inner,'outer':outer,'columns':2,'column_width':round((body_width-gutter)/2,4),'gutter':gutter,'source':'A-master margins, native two-column credits frame u50cc; source master ColumnCount=1 is not the body-column count'}
    fonts=[]
    originals={'heading_regular':'abbess-regular.ttf','body_regular':'GOUDOS.TTF','body_bold':'GOUDOSB_0.TTF','body_italic':'GOUDOSI_0.TTF','sidebar_regular':'FuturaPTBook.otf'}
    for key, filename in originals.items():fonts.append(font_record(key,path.parent/'Document fonts'/filename,key))
    selected = {p.name:p for base in (Path('/usr/share/fonts'), ROOT/'.runtime/fonts') if base.exists() for p in base.rglob('*.ttf')}
    supplements={'script_fallback':'NotoSerif-Regular.ttf','body_bold_italic':'NotoSerif-BoldItalic.ttf','sidebar_bold':'NotoSans-Bold.ttf','sidebar_italic':'NotoSans-Italic.ttf','sidebar_bold_italic':'NotoSans-BoldItalic.ttf','mono_regular':'DejaVuSansMono.ttf','script_sans':'NotoSans-Regular.ttf','rtl_regular':'DejaVuSans.ttf','rtl_bold':'DejaVuSans-Bold.ttf','rtl_italic':'DejaVuSans-Oblique.ttf','rtl_bold_italic':'DejaVuSans-BoldOblique.ttf'}
    for key, filename in supplements.items():fonts.append(font_record(key,selected[filename],key,True))
    return {'schema_version':1,'profile':'m20','units':'bp','page':page,'page_size_pt':page,
            'source':{'idml':str(path),'sha256':digest(path),'authority':'Original supplied IDML; inherited/local styles resolve independently'},
            'geometry':geometry,
            'style_roles':{'body':'ParagraphStyle/n','first':'ParagraphStyle/n (no indent)','heading1':'ParagraphStyle/1','heading2':'ParagraphStyle/2','heading3':'ParagraphStyle/3'},
            'styles':styles,'resolved_styles':{k:v['resolved'] for k,v in styles.items()},
            'opener':{'body_top':355.5},'sidebar':{'border':7,'inset':25,'gutter':12},
            'art_reserves':{'horizontal':[body_width,body_height/2],'vertical':[(body_width-gutter)/2,body_height]},
            'swatches':swatches,'source_master_geometry':masters,'source_spread_geometry':spreads,
            'composition':{'kerning':'metrics','tracking':0,'optical_margin_alignment':False,'generic_protrusion':False,'generic_expansion':False,
                           'paragraph_gap_policy':'Measure composition; do not add inactive/inherited span gaps blindly'},
            'fonts':fonts,'assets':[{'sourceRelative':str(p.relative_to(path.parent)),'sha256':digest(p)} for p in sorted((path.parent/'Links').iterdir()) if p.is_file()],
            'source_asset_base':str(path.parent),
            'notes':['First paragraph is independently based on the no-paragraph-style base and resolves vertical scale to 100 percent.',
                     'Complete raw/resolved effects are retained separately from active properties.',
                     'Missing bold italic and sidebar emphasis use explicit genuine audited Noto faces; never synthetic styling.']}

def prepare_assets(profile, output_dir):
    out = Path(output_dir).resolve()
    if not out.is_relative_to(ROOT) or out == ROOT:
        raise ValueError('Prepared resources must stay in the project workspace')
    out.mkdir(parents=True,exist_ok=True); resources=[]
    fonts = ROOT / 'fonts'; fonts.mkdir(exist_ok=True)
    for record in profile['fonts']:
        src = Path(record['source']); src = ROOT.parent/src if not src.is_absolute() else src
        if digest(src) != record['sha256']:raise ValueError('Font source changed: '+str(src))
        dst = fonts/record['file']; shutil.copyfile(src,dst)
        resources.append({'id':record['id'],'path':str(dst.relative_to(ROOT)),'sha256':digest(dst),'source_sha256':record['sha256'],'role':record['role'],'kind':'font','license':record['license'],'fsType':record['fsType']})
    base = ROOT.parent/profile['source_asset_base']
    art_roles={'Mage Gold.psd':'chapter_frame','Mage Silk v2.psd':'chapter_texture','sidebar v2.tif':'sidebar_texture','M20_SinglePage__0000_Border.psd':'page_border'}
    for record in profile['assets']:
        src=base/record['sourceRelative']
        if src.name not in art_roles:continue
        if digest(src) != record['sha256']:raise ValueError('Artwork source changed: '+str(src))
        role = art_roles[src.name]; dst=out/(role+'.png')
        with Image.open(src) as image:
            original_mode=image.mode; original_size=list(image.size); info=dict(image.info)
            if image.mode not in ('RGB','RGBA','L','LA','P'):image=image.convert('RGBA')
            image.save(dst,format='PNG',icc_profile=info.get('icc_profile'),dpi=info.get('dpi',(300,300)))
        resources.append({'id':role,'path':str(dst.relative_to(ROOT)),'sha256':digest(dst),'source_sha256':record['sha256'],'role':'decorative','kind':'artwork','source':str(src.relative_to(base)),'dimensions_px':original_size,'source_mode':original_mode,'color_note':'Lossless PNG; embedded source ICC retained where provided; CMYK source converted by Pillow must be visually calibrated','license':'Supplied proprietary artwork; no redistribution license granted'})
    (out/'resources.json').write_text(json.dumps(resources,ensure_ascii=False,indent=2)+'\n')
    return resources

def write_profile_tex(profile, path):
    geometry=profile['geometry']
    heading_font = next(face['file'] for face in profile['fonts'] if face['id'] == 'heading_regular')
    values={'PageWidth':profile['page'][0],'PageHeight':profile['page'][1],'BodyWidth':geometry['body_width'],'BodyHeight':geometry['body_height'],'Top':geometry['top'],'Inner':geometry['inner'],'Outer':geometry['outer'],'ColumnWidth':geometry['column_width'],'Gutter':geometry['gutter']}
    text='% Source-resolved M20 geometry in bp (72 units/inch), not TeX pt.\n'
    text+='\\def\\mTwentyHeadingFontFile{'+heading_font+'}\n'
    for name,value in values.items():text+='\\def\\mTwenty'+name+'{'+str(value)+'bp}\n'
    text+='\\def\\mTwentyBodySize{10bp}\n\\def\\mTwentyBodyLeading{12bp}\n\\def\\mTwentyBodyIndent{18bp}\n\\def\\mTwentyBodyBefore{1.44bp}\n\\def\\mTwentyBodyAfter{1.44bp}\n\\def\\mTwentyBodyVerticalScale{98}\n\\def\\mTwentyFirstVerticalScale{100}\n'
    text+='\\def\\mTwentyOpenerBodyTop{'+str(profile['opener']['body_top'])+'bp}\n'
    text+='\\def\\mTwentySidebarInset{'+str(profile['sidebar']['inset'])+'bp}\n'
    Path(path).write_text(text)

def public_profile(profile):
    """Keep reusable measurements; local source/audit paths are build evidence."""
    result = {k:profile[k] for k in ('schema_version','profile','units','page','geometry','style_roles','opener','sidebar','art_reserves','composition','notes')}
    result['source'] = {**profile['source'], 'idml':Path(profile['source']['idml']).name}
    roles = set(profile['style_roles'].values()) | {'ParagraphStyle/sb 1','ParagraphStyle/sb 2'}
    result['styles'] = {k:{'active':v['active'],'inheritance':v['inheritance']} for k,v in profile['styles'].items() if k in roles}
    result['fonts'] = [{k:v for k,v in f.items() if k != 'source'} for f in profile['fonts']]
    return result

def import_template_zip(path):
    """Extract only the authorized interior input tree, leaving the ZIP intact."""
    dest=ROOT/'inputs/M20';dest.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(path) as z:
        matches=[n for n in z.namelist() if Path(n).name=='M20 Template Interior.idml']
        if len(matches)!=1:raise ValueError('Expected one original M20 Template Interior.idml in the template ZIP')
        parent=Path(matches[0]).parent
        for member in z.infolist():
            p=Path(member.filename)
            if p.is_absolute() or '..' in p.parts or ((member.external_attr>>16)&0o170000)==0o120000:raise ValueError('Unsafe template ZIP member')
            if not p.is_relative_to(parent) or member.is_dir():continue
            relative=p.relative_to(parent)
            if relative.name!='M20 Template Interior.idml' and relative.parts[0] not in ('Document fonts','Links'):continue
            target=dest/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(z.read(member))
    return dest/'M20 Template Interior.idml'

if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--idml');parser.add_argument('--template-zip');parser.add_argument('--assets-out',default=str(ROOT/'assets'));args=parser.parse_args()
    if args.idml and args.template_zip:parser.error('Choose --idml or --template-zip')
    idml=import_template_zip(args.template_zip) if args.template_zip else Path(args.idml) if args.idml else ROOT/'inputs/M20/M20 Template Interior.idml'
    if not idml.exists() and not (args.idml or args.template_zip):idml=SOURCE/'M20 Template Interior.idml'
    profile=resolve_profile(idml)
    (ROOT/'profiles/m20.json').write_text(json.dumps(public_profile(profile),ensure_ascii=False,indent=2)+'\n')
    write_profile_tex(profile,ROOT/'profiles/m20.tex')
    resources=prepare_assets(profile,args.assets_out)
    print(json.dumps({'fonts':sum(r['kind']=='font' for r in resources),'artwork':sum(r['kind']=='artwork' for r in resources),'resources':str(Path(args.assets_out)/'resources.json')}))
