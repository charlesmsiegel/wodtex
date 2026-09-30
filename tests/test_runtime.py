import importlib.util
import tempfile
import unittest
from pathlib import Path
from tests.support import ROOT

class RuntimeTests(unittest.TestCase):
    def module(self):
        self.assertTrue((ROOT / 'scripts/preflight.py').exists(), 'preflight implementation required')
        spec = importlib.util.spec_from_file_location('m20preflight', ROOT / 'scripts/preflight.py')
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        return m

    def test_missing_luaotfload_is_blocking(self):
        m = self.module()
        report = m.evaluate_availability({'lualatex': {'available': True}}, {'luaotfload.sty': None})
        self.assertFalse(report['pdf_ready'])
        self.assertIn('M20_E_LUAOTFLOAD_MISSING', [d['code'] for d in report['diagnostics']])

    def test_writes_stay_in_workspace(self):
        m = self.module()
        with self.assertRaises(ValueError):
            m.runtime_environment(Path('/tmp/m20-outside-project'))
        env = m.runtime_environment(ROOT / '.runtime/test-cache')
        for key in m.WRITABLE_ENV:
            self.assertTrue(Path(env[key]).is_relative_to(ROOT / '.runtime'))
        self.assertEqual(env['shell_escape'], 'f')

    def test_preflight_reports_required_tools(self):
        m = self.module()
        report = m.preflight(ROOT / '.runtime', prepare=False)
        for key in ('engines', 'packages', 'fonts', 'index', 'converters', 'diagnostics', 'environment'):
            self.assertIn(key, report)
        self.assertTrue(report['engines']['lualatex']['available'])
