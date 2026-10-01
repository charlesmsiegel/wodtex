"""Prove intentional aspect distortion and optional caption space in installed art."""
import struct
import zlib
import shutil
import subprocess
import unittest
from tests import test_native_frontmatter as frontmatter
from tests.test_install import ROOT


def write_fixture(path, width, height):
    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff)
    rows = b''.join(b'\0' + bytes((40, 110, 190) if y < height // 2 else (180, 140, 45)) * width for y in range(height))
    path.write_bytes(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(rows)) + chunk(b'IEND', b''))


@unittest.skipUnless(shutil.which('lualatex'), 'LuaLaTeX required')
class NativeArtFitTests(unittest.TestCase):
    setUp = frontmatter.NativeFrontmatterTests.setUp

    def render(self, kind, caption, explicit=False, decorative=False):
        name = '-'.join((kind, caption or 'none', 'explicit' if explicit else 'generic', 'decorative' if decorative else 'meaningful'))
        work = self.base / name
        work.mkdir()
        dimensions = (197, 613) if kind == 'horizontal' else (641, 103)
        write_fixture(work / 'fixture.png', *dimensions)
        options = 'kind=' + kind + ',image={fixture.png},'
        options += 'role=decorative' if decorative else 'alt={Labeled geometric test fixture}'
        if caption == 'caption':
            options += ',caption={FIT CAPTION},credit={FIT CREDIT}'
        elif caption == 'credit':
            options += ',credit={FIT CREDIT}'
        command = r'\m20artreserve' if explicit else r'\artreserve'
        source = r'\documentclass{m20book}\title{Art Stretch Proof}\begin{document}' + command + '[' + options + r']{fit-proof}\end{document}'
        (work / 'book.tex').write_text(source)
        result = subprocess.run(['lualatex', '-interaction=nonstopmode', '-halt-on-error', 'book.tex'], cwd=work, env=self.env, capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stdout[-7000:])
        import fitz
        with fitz.open(work / 'book.pdf') as doc:
            images = [(p,item) for p in doc for item in p.get_image_info() if (item['width'],item['height']) == dimensions]
            self.assertEqual(1, len(images))
            bbox = fitz.Rect(images[0][1]['bbox'])
            if kind == 'horizontal':
                frame = next(v['rect'] for v in images[0][0].get_drawings() if v['fill'] and v['rect'].width > 450 and v['fill'][0] < .2)
                self.assertLessEqual(bbox.y1, frame.y1, 'image must not cover the gold lower frame edge')
            outer_width = 490.4496 if kind == 'horizontal' else 239.2248
            outer_height = 341.28 if kind == 'horizontal' else 657
            self.assertAlmostEqual(outer_width - 14, bbox.width, delta=.12)
            self.assertAlmostEqual(outer_height - (40 if caption else (21 if kind == 'horizontal' else 14)), bbox.height, delta=.12)
            self.assertNotAlmostEqual(dimensions[0]/dimensions[1], bbox.width/bbox.height, places=1)
            text = ''.join(p.get_text() for p in doc)
            self.assertEqual(int(caption == 'caption'), text.count('FIT CAPTION'))
            self.assertEqual(int(bool(caption)), text.count('FIT CREDIT'))
        evidence = ROOT / 'build/native-art-fit' / name
        evidence.mkdir(parents=True, exist_ok=True)
        for p in work.iterdir():
            shutil.copy2(p,evidence / p.name)
        return bbox.width, bbox.height

    def test_horizontal_and_vertical_fill_without_caption_strip(self):
        for kind in ('horizontal','vertical'):
            with self.subTest(kind=kind):
                generic = self.render(kind,'')
                explicit = self.render(kind,'',explicit=True)
                decorative = self.render(kind,'',decorative=True)
                self.assertEqual(generic,explicit)
                self.assertEqual(generic,decorative)

    def test_caption_and_credit_reserve_only_their_existing_band(self):
        for kind in ('horizontal','vertical'):
            for caption in ('caption','credit'):
                with self.subTest(kind=kind,caption=caption):
                    generic = self.render(kind,caption)
                    explicit = self.render(kind,caption,explicit=True)
                    self.assertEqual(generic,explicit)

    def test_path_only_calls_allow_missing_alt_and_generate_optional_ids(self):
        for kind in ('horizontal','vertical'):
            for explicit in (False,True):
                work = self.base / ('path-only-' + kind + ('-explicit' if explicit else '-generic'))
                work.mkdir()
                write_fixture(work / 'fixture.png',197,613)
                command = r'\m20artreserve' if explicit else r'\artreserve'
                options = 'image={fixture.png}' + (',kind=vertical' if kind == 'vertical' else '')
                source = r'\documentclass{m20book}\begin{document}' + command + '[' + options + r']{m20-art-auto-1}' + command + '[' + options + r']\end{document}'
                (work / 'book.tex').write_text(source)
                result = subprocess.run(['lualatex', '-interaction=nonstopmode','-halt-on-error','book.tex'],cwd=work,env=self.env,capture_output=True,text=True)
                self.assertEqual(0,result.returncode,result.stdout[-7000:])
                self.assertIn('M20_W_ART_ALT',result.stdout)
                positions = (work / 'book.m20pos').read_text()
                self.assertIn('m20-art-auto-1|',positions)
                self.assertIn('m20-art-auto-2|',positions)
                self.assertNotIn('M20_E_ART_ALT',result.stdout)

    def test_explicit_meaningful_missing_alt_warns_without_invented_text(self):
        work = self.base / 'explicit-meaningful'
        work.mkdir()
        write_fixture(work / 'fixture.png',197,613)
        (work / 'book.tex').write_text(r'\documentclass{m20book}\begin{document}\artreserve[image={fixture.png},role=meaningful]{no-alt}\end{document}')
        result = subprocess.run(['lualatex', '-interaction=nonstopmode','-halt-on-error','book.tex'],cwd=work,env=self.env,capture_output=True,text=True)
        self.assertEqual(0,result.returncode,result.stdout[-7000:])
        self.assertIn('M20_W_ART_ALT',result.stdout)
