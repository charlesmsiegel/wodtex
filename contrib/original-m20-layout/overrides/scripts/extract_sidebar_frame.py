#!/usr/bin/env python3
"""Privately extract the licensed sidebar texture and fixed-scale shadow tiles.

No artwork bytes belong in the public correction package. Supply the pinned
original template PDF, then run this script to restore the local assets.
"""
import argparse
import hashlib
from pathlib import Path
import fitz

EXPECTED = '4c876e07b17f4a85877213d557b3f0236004bf6baa48d0bef708a68745e93df5'
FRAME = fitz.Rect(67.5504, 63.0, 558.0, 167.04)
SHADOW = fitz.Rect(66.6104, 62.06, 568.09, 176.90)


def isolate(original, stream, crop, destination):
    doc = fitz.open()
    doc.insert_pdf(original, from_page=5, to_page=5)
    page = doc[0]
    doc.update_stream(page.get_contents()[0], stream)
    # Do not retain unrelated template artwork, fonts or page resources.
    gs, xobject = ('GS1', 'Fm1') if b'/Fm1 Do' in stream else ('GS0', 'Im0')
    gsref = doc.xref_get_key(page.xref, f'Resources/ExtGState/{gs}')[1]
    xref = doc.xref_get_key(page.xref, f'Resources/XObject/{xobject}')[1]
    doc.xref_set_key(page.xref, 'Resources',
                     f'<< /ExtGState << /{gs} {gsref} >> '
                     f'/XObject << /{xobject} {xref} >> >>')
    page.set_cropbox(crop)
    if page.get_text().strip():
        raise RuntimeError('Sidebar decorative extraction unexpectedly contains text')
    doc.save(destination, garbage=4, deflate=True)
    doc.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('template', type=Path)
    parser.add_argument('--out', type=Path, default=Path('assets'))
    args = parser.parse_args()
    if hashlib.sha256(args.template.read_bytes()).hexdigest() != EXPECTED:
        raise SystemExit('Authoritative original template hash mismatch')
    args.out.mkdir(parents=True, exist_ok=True)
    original = fitz.open(args.template)
    texture = (b'q\n/GS0 gs\n492.479989 0 0 106.3199976 '
               b'66.5352367 623.8199788 cm\n/Im0 Do\nQ\n')
    isolate(original, texture, FRAME,
            args.out / 'sidebar-texture.reference-template.pdf')
    # Twelve-point corners preserve the original blur, displacement and CMYK
    # Multiply ink. Stretch only flat edge middles, never blur radii.
    xs = (SHADOW.x0, SHADOW.x0+12, SHADOW.x1-12, SHADOW.x1)
    ys = (SHADOW.y0, SHADOW.y0+12, SHADOW.y1-12, SHADOW.y1)
    for row, vertical in enumerate(('top', 'middle', 'bottom')):
        for col, horizontal in enumerate(('left', 'middle', 'right')):
            crop = fitz.Rect(xs[col], ys[row], xs[col+1], ys[row+1])
            isolate(original, b'q\n/GS1 gs\n/Fm1 Do\nQ\n', crop,
                    args.out / f'sidebar-shadow-{vertical}-{horizontal}.reference-template.pdf')
    original.close()
    for path in sorted(args.out.glob('sidebar-*.reference-template.pdf')):
        print(path, hashlib.sha256(path.read_bytes()).hexdigest())


if __name__ == '__main__':
    main()
