"""Prepare one explicitly mapped profile from immutable local template sources.

Only selected font faces and reference border strips are retained. Profiles own
their mapping and source hashes; adding another template requires a descriptor,
not a new importer or a silent substitution in this preparer.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import io
import fitz
from pypdf.generic import ContentStream, DecodedStreamObject
try:
    from profile_registry import ROOT, load_profiles
    from template_reader import source_bytes
except ImportError:
    from scripts.profile_registry import ROOT, load_profiles
    from scripts.template_reader import source_bytes


def checked_source(root, record):
    relative = Path(record['path'])
    if relative.is_absolute() or '..' in relative.parts:
        raise ValueError('WODTEX_E_SOURCE_PATH: ' + str(relative))
    data = source_bytes(root / relative, record.get('member'))
    if hashlib.sha256(data).hexdigest() != record['sha256']:
        raise ValueError('WODTEX_E_SOURCE_HASH: ' + str(relative))
    return data


def remove_template_text(pdf):
    """Remove text-show operations in page streams and nested Form XObjects.

    Rectangle redaction misses template running matter stored in reusable Forms.
    Parse PDF operators rather than matching byte patterns inside encoded strings.
    Keep graphics, transforms, font state and images intact.
    """
    streams = set()
    for page in pdf:
        streams.update(page.get_contents())
        streams.update(record[0] for record in page.get_xobjects())
    for xref in streams:
        stream = DecodedStreamObject()
        stream.set_data(pdf.xref_stream(xref))
        content = ContentStream(stream, None)
        content.operations = [(operands, operator) for operands, operator in content.operations
                              if operator not in (b'Tj', b'TJ', b"'", b'"')]
        pdf.update_stream(xref, content.get_data())


def prepare_profile(profile_id, source_root, output_root, root=ROOT):
    profile = load_profiles(root)[profile_id]
    if profile_id == 'm20':
        raise ValueError('M20 uses the existing bundled preparation workflow')
    source_root, output_root = Path(source_root).resolve(), Path(output_root).resolve()
    if output_root == source_root or output_root.is_relative_to(source_root):
        raise ValueError('Prepared outputs must not modify the source template tree')
    dest = output_root / profile_id
    dest.mkdir(parents=True, exist_ok=True)
    resources = {}
    for role, record in profile['fonts'].items():
        data = checked_source(source_root, record)
        name = role + Path(record.get('member') or record['path']).suffix.lower()
        (dest / name).write_bytes(data)
        resources[name] = hashlib.sha256(data).hexdigest()
    data = checked_source(source_root, profile['reference'])
    with fitz.open(stream=data, filetype='pdf') as original:
        remove_template_text(original)
        for role, number in profile['border_pages'].items():
            src = original[number - 1]
            width, height = src.rect.width, src.rect.height
            margins = profile['geometry']
            left, right = margins['inner'], margins['outer']
            if role == 'body-left':
                left, right = right, left
            # Keep only outer decoration bands: sample artwork, sidebar boxes,
            # colored placeholder panels and text must not become book content.
            strips = [(0, 0, width, margins['top'] * .7),
                      (0, height - margins['bottom'] * .7, width, height),
                      (0, 0, left * .7, height), (width - right * .7, 0, width, height)]
            with fitz.open() as output:
                page = output.new_page(width=width, height=height)
                for bounds in strips:
                    rect = fitz.Rect(bounds)
                    page.show_pdf_page(rect, original, number - 1, clip=rect)
                name = role + '.pdf'
                output.save(dest / name, garbage=4, deflate=True)
                resources[name] = hashlib.sha256((dest / name).read_bytes()).hexdigest()
    manifest = {'schema_version': 1, 'style_id': profile_id,
                'reference_sha256': profile['reference']['sha256'], 'files': resources,
                'notes': profile.get('limitations', [])}
    (dest / 'resources.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    return manifest


def verify_resources(profile_id, output_root):
    base = Path(output_root) / profile_id
    manifest = json.loads((base / 'resources.json').read_text(encoding='utf-8'))
    for name, expected in manifest['files'].items():
        if Path(name).name != name or hashlib.sha256((base / name).read_bytes()).hexdigest() != expected:
            raise ValueError('WODTEX_E_RESOURCE_HASH: ' + profile_id + '/' + name)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', action='append', required=True)
    parser.add_argument('--source-root', type=Path, required=True)
    parser.add_argument('--out', type=Path, default=ROOT / 'inputs/profiles')
    args = parser.parse_args()
    profiles = load_profiles()
    selected = [s for s in profiles if s != 'm20'] if 'all' in args.profile else args.profile
    for style in selected:
        result = prepare_profile(style, args.source_root, args.out)
        print(style + ': ' + str(len(result['files'])) + ' checked resources')


if __name__ == '__main__':
    main()
