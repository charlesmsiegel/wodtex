import json
import subprocess
import sys
import unittest
from pathlib import Path
from tests.support import ROOT

class BuildTests(unittest.TestCase):
    def test_missing_source_fails_with_a_report(self):
        out = ROOT / 'build/test-missing-source'
        p = subprocess.run([sys.executable, str(ROOT/'scripts/build.py'), '--target','pdf',
                            '--source','missing-manuscript.tex','--out',str(out)],
                           cwd=ROOT, capture_output=True, text=True)
        self.assertNotEqual(p.returncode, 0)
        self.assertTrue((out/'build-report.json').is_file(), p.stderr)
        report = json.loads((out/'build-report.json').read_text())
        self.assertEqual(report['status'], 'failed')
        self.assertIn('M20_E_SOURCE_MISSING', [d['code'] for d in report['diagnostics']])
