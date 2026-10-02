"""General WoD family class and source-backed output descriptor contract."""
import unittest
from tests.test_x20_foundation import ROOT, module


class FamilyInventoryTests(unittest.TestCase):
    def test_expected_family_classes_exist(self):
        profile = module('profile_registry').load_profiles(ROOT)['wod']
        self.assertEqual('wodbook', profile['class'])
        self.assertEqual(['pdf'], profile['outputs'])
        self.assertTrue((ROOT / 'wodbook.cls').is_file())
        self.assertTrue(profile['source_measurements'])


if __name__ == '__main__':
    unittest.main()
