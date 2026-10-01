import importlib.util
import tempfile
import unittest
from pathlib import Path
from tests.support import ROOT, IDML

class ProfileTests(unittest.TestCase):
    def test_import_requires_only_original_input_tree(self):
        profile = self.module().resolve_profile(IDML)
        self.assertEqual(profile['geometry']['body_height'], 657)
        self.assertEqual(profile['opener']['body_top'], 355.5)

    def module(self):
        self.assertTrue((ROOT / 'scripts/prepare_assets.py').exists(), 'profile resolver required')
        spec = importlib.util.spec_from_file_location('m20assets', ROOT / 'scripts/prepare_assets.py')
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        return m

    def test_profile_units_and_inheritance(self):
        p = self.module().resolve_profile(IDML)
        self.assertEqual(p['units'], 'bp')
        self.assertEqual(p['page'], [612, 792])
        self.assertEqual(p['geometry']['gutter'], 12)
        self.assertAlmostEqual(p['geometry']['body_width'], 490.4496)
        n = p['styles']['ParagraphStyle/n']['active']
        self.assertEqual(float(n['FirstLineIndent']), 18)
        self.assertEqual(float(n['VerticalScale']), 98)
        self.assertEqual(n['AppliedFont'], 'Goudy Old Style')
        self.assertEqual(float(n['Leading']), 12)
        self.assertEqual(p['styles']['ParagraphStyle/2']['active']['AppliedFont'], 'Abbess')

    def test_unindented_style_does_not_inherit_98_percent_scale(self):
        p = self.module().resolve_profile(IDML)
        first = p['styles']['ParagraphStyle/n (no indent)']
        self.assertEqual(float(first['active']['FirstLineIndent']), 0)
        self.assertEqual(float(first['active']['VerticalScale']), 100)
        self.assertNotEqual(float(first['active']['VerticalScale']), float(p['styles']['ParagraphStyle/n']['active']['VerticalScale']))
        self.assertIn('ParagraphStyle/$ID/[No paragraph style]', first['inheritance'])

    def test_real_font_faces_and_glyphs(self):
        p = self.module().resolve_profile(IDML)
        fonts = {f['id']: f for f in p['fonts']}
        self.assertEqual(fonts['body_regular']['postscript'], 'GoudyOldStyleT-Regular')
        self.assertTrue(fonts['body_bold']['bold'])
        self.assertTrue(fonts['body_italic']['italic'])
        self.assertEqual(fonts['sidebar_regular']['postscript'], 'FuturaPT-Book')
        self.assertTrue(fonts['heading_regular']['glyph_coverage']['M20'])
        self.assertTrue(fonts['script_fallback']['glyph_coverage']['greek_cyrillic'])
        self.assertFalse(any(f.get('synthetic', False) for f in fonts.values()))

    def test_generated_profile_preserves_its_heading_font_selection(self):
        module = self.module()
        profile = module.resolve_profile(IDML)
        with tempfile.TemporaryDirectory(dir=ROOT / 'build') as directory:
            path = Path(directory) / 'profile.tex'
            module.write_profile_tex(profile, path)
            self.assertIn(r'\def\mTwentyHeadingFontFile{abbess-regular.ttf}', path.read_text())
            # Authoring configuration follows the profile's genuine heading
            # font record instead of hardcoding M20's face into shared code.
            for face in profile['fonts']:
                if face['id'] == 'heading_regular':
                    face['file'] = 'configured-heading.ttf'
            module.write_profile_tex(profile, path)
            self.assertIn(r'\def\mTwentyHeadingFontFile{configured-heading.ttf}', path.read_text())
