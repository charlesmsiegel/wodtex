"""Read IDML structure without imposing a gameline's typography or geometry.

The source model retains inherited properties and master/page frames. Role mapping
is an explicit profile decision; future templates reuse parsing, not Mage defaults.
"""
import hashlib
import io
from pathlib import Path, PurePosixPath
from zipfile import ZipFile, BadZipFile
import xml.etree.ElementTree as ET


def source_bytes(path, member=None):
    if member is not None:
        parts = PurePosixPath(member).parts
        if not parts or '..' in parts or PurePosixPath(member).is_absolute() or '\\' in member:
            raise ValueError('Unsafe archive member: ' + member)
        with ZipFile(path) as archive:
            info = archive.getinfo(member)
            if info.file_size > 256 * 1024 * 1024:
                raise ValueError('Archive member exceeds template size limit')
            return archive.read(info)
    return Path(path).read_bytes()


def content_provenance(text):
    """Keep an identity for embedded IDML artwork without copying its payload."""
    return {'sha256': hashlib.sha256(text.encode('utf-8')).hexdigest(),
            'encoded_characters': len(text), 'representation': 'IDML Contents text',
            'external_input': True}


def properties(element):
    result = dict(element.attrib)
    props = element.find('Properties')
    if props is not None:
        for child in props:
            value = (child.text or '').strip() or ET.tostring(child, encoding='unicode')
            result[child.tag] = content_provenance(value) if element.tag in ('Image', 'PDF') and child.tag == 'Contents' else value
    return result


def read_idml(path, member=None):
    data = source_bytes(path, member)
    try:
        archive = ZipFile(io.BytesIO(data))
    except BadZipFile as error:
        raise ValueError('WODTEX_E_IDML_INVALID: ' + str(path)) from error
    with archive:
        raw = {e.get('Self'): properties(e) for e in ET.fromstring(archive.read('Resources/Styles.xml')).iter()
               if e.tag in ('ParagraphStyle', 'CharacterStyle', 'ObjectStyle', 'TableStyle', 'CellStyle')}
        resolved = {}

        def resolve(key, chain=()):
            if key in chain:
                raise ValueError('Cyclic IDML style inheritance: ' + key)
            if key in resolved:
                return resolved[key]
            own = raw[key]
            parent = own.get('BasedOn')
            result = dict(resolve(parent, chain + (key,))) if parent in raw else {}
            result.update(own)
            resolved[key] = result
            return result

        for key in raw:
            resolve(key)
        pref = ET.fromstring(archive.read('Resources/Preferences.xml')) if 'Resources/Preferences.xml' in archive.namelist() else ET.Element('Root')
        page = next(pref.iter('DocumentPreference'), None)
        geometry = []
        for name in archive.namelist():
            if name.startswith(('Spreads/', 'MasterSpreads/')) and name.endswith('.xml'):
                tree = ET.fromstring(archive.read(name))
                geometry.append({'member': name, 'records': [{'type': e.tag, **properties(e)} for e in tree.iter()
                    if e.tag in ('Page', 'MarginPreference', 'TextFrame', 'TextFramePreference', 'Rectangle', 'Image', 'PDF')]})
        return {'source_sha256': hashlib.sha256(data).hexdigest(), 'units': 'bp',
                'page': [float(page.get('PageWidth')), float(page.get('PageHeight'))] if page is not None else None,
                'styles': {k: {'raw': raw[k], 'resolved': resolved[k]} for k in raw}, 'geometry': geometry}
