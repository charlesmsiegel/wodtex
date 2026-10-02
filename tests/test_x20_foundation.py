"""Contracts for independent template ingestion and profile selection."""
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name + '.py'))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


class FoundationTests(unittest.TestCase):
    def test_embedded_image_contents_are_provenance_not_copied_artwork(self):
        import hashlib
        import xml.etree.ElementTree as ET
        payload = 'encoded-image-data' * 10000
        image = ET.fromstring('<Image ItemTransform="1 0 0 1 20 30"><Properties><Contents>' + payload + '</Contents></Properties></Image>')
        record = module('template_reader').properties(image)
        self.assertTrue(isinstance(record['Contents'], dict), 'Embedded artwork must become compact provenance')
        self.assertEqual(hashlib.sha256(payload.encode()).hexdigest(), record['Contents']['sha256'])
        self.assertEqual(len(payload), record['Contents']['encoded_characters'])
        self.assertEqual('1 0 0 1 20 30', record['ItemTransform'])
        self.assertLess(len(json.dumps(record)), 500)

    def test_registry_discovers_only_descriptors_and_rejects_duplicate_classes(self):
        registry = module('profile_registry')
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'profiles').mkdir()
            record = {'kind': 'wodtex-output-profile', 'schema_version': 1,
                      'style_id': 'demo', 'class': 'demobook', 'outputs': ['pdf']}
            (root / 'profiles/demo.json').write_text(json.dumps(record))
            (root / 'profiles/measurements.json').write_text('{"page": [612,792]}')
            self.assertEqual(['demo'], list(registry.load_profiles(root)))
            self.assertEqual('demo', registry.profile_for_class(root, 'demobook')['style_id'])
            with self.assertRaisesRegex(ValueError, 'UNKNOWN_CLASS'):
                registry.profile_for_class(root, 'missingbook')
            record['style_id'] = 'other'
            (root / 'profiles/other.json').write_text(json.dumps(record))
            with self.assertRaisesRegex(ValueError, 'DUPLICATE'):
                registry.load_profiles(root)

    def test_reader_resolves_inheritance_without_m20_defaults(self):
        reader = module('template_reader')
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / 'demo.idml'
            with ZipFile(source, 'w') as archive:
                archive.writestr('Resources/Preferences.xml', '<Root><DocumentPreference PageWidth="500" PageHeight="700"/></Root>')
                archive.writestr('Resources/Styles.xml', '<Root><ParagraphStyle Self="base" PointSize="11"><Properties><AppliedFont>Demo</AppliedFont></Properties></ParagraphStyle><ParagraphStyle Self="child" FirstLineIndent="5"><Properties><BasedOn>base</BasedOn></Properties></ParagraphStyle></Root>')
            data = reader.read_idml(source)
            self.assertEqual([500, 700], data['page'])
            self.assertEqual('Demo', data['styles']['child']['resolved']['AppliedFont'])
            self.assertEqual('11', data['styles']['child']['resolved']['PointSize'])
            self.assertNotIn('Goudy', json.dumps(data))
            with ZipFile(source, 'w') as archive:
                archive.writestr('Resources/Styles.xml', '<Root><ParagraphStyle Self="a"><Properties><BasedOn>b</BasedOn></Properties></ParagraphStyle><ParagraphStyle Self="b"><Properties><BasedOn>a</BasedOn></Properties></ParagraphStyle></Root>')
            with self.assertRaisesRegex(ValueError, 'inheritance'):
                reader.read_idml(source)

    def test_empty_sources_and_unsafe_archive_members_are_rejected(self):
        reader = module('template_reader')
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / 'empty.idml'
            source.touch()
            with self.assertRaisesRegex(ValueError, 'IDML'):
                reader.read_idml(source)
            with self.assertRaisesRegex(ValueError, 'member'):
                reader.read_idml(source, '../bad.idml')

    def test_class_selection_ignores_comments_and_supports_options(self):
        registry = module('profile_registry')
        self.assertEqual('c20book', registry.document_class('% \\documentclass{wrong}\n\\documentclass[twoside]{c20book}\n'))
        with self.assertRaisesRegex(ValueError, 'CLASS'):
            registry.document_class('\\documentclass{a}\\documentclass{b}')

    def test_installer_includes_registered_classes_and_output_descriptors(self):
        installer = module('install')
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name in ('profiles', 'tex'):
                (root / name).mkdir()
            (root / 'm20book.cls').write_text('M20')
            (root / 'demobook.cls').write_text('Demo')
            (root / 'profiles/demo.json').write_text(json.dumps({
                'kind': 'wodtex-output-profile', 'schema_version': 1,
                'style_id': 'demo', 'class': 'demobook', 'outputs': ['pdf']}))
            previous = installer.ROOT
            installer.ROOT = root
            try:
                files = installer.payload('base')
                self.assertIn('demobook.cls', files)
                self.assertIn('wodtex-output-demo.json', files)
            finally:
                installer.ROOT = previous


if __name__ == '__main__':
    unittest.main()
