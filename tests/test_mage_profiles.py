"""Family-specific class inventory and native rendering contracts."""
import unittest
from tests.test_x20_foundation import ROOT,module
from tests.test_x20_profiles import X20ProfileTests

class FamilyInventoryTests(unittest.TestCase):
    def test_expected_family_classes_exist(self):
        profiles=module("profile_registry").load_profiles(ROOT)
        expected={'m20-dark-ages': 'm20darkagesbook', 'msc': 'mscbook'}
        for style,cls in expected.items():
            with self.subTest(style=style):
                self.assertIn(style,profiles)
                self.assertEqual(cls,profiles[style]["class"])
                self.assertTrue((ROOT/(cls+".cls")).exists())
