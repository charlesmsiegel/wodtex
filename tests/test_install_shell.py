"""Test the thin Bash launcher with controlled Python shims."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which('bash'), 'Bash required')
class InstallShellTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='wodtex-shell-')
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.repo = self.base / 'checkout with spaces'
        self.repo.mkdir()
        (self.repo / 'scripts').mkdir()
        shutil.copy2(ROOT / 'install.sh', self.repo / 'install.sh')
        (self.repo / 'scripts/install.py').write_text('# launcher test placeholder\n')
        self.bin = self.base / 'bin'
        self.bin.mkdir()
        self.work = self.base / 'unrelated work folder'
        self.work.mkdir()
        self.capture = self.base / 'args.json'
        self.env = dict(os.environ, PATH=str(self.bin), WODTEX_CAPTURE=str(self.capture))
        self.bash = shutil.which('bash')

    def shim(self, name, platform='posix', valid=True):
        # Absolute interpreter ensures the test does not accidentally find a
        # system Python when exercising an otherwise empty PATH.
        import sys
        source = '''#!{python}
import json, os, sys
args = sys.argv[1:]
if args and args[0] == '-3':
    args = args[1:]
if args and args[0] == '-c':
    if 'version_info' in args[1]:
        raise SystemExit({status})
    print({platform!r})
else:
    with open(os.environ['WODTEX_CAPTURE'], 'w') as capture:
        json.dump(args, capture)
    raise SystemExit(int(os.environ.get('WODTEX_TEST_EXIT', '0')))
'''.format(python=sys.executable, status=0 if valid else 1, platform=platform)
        path = self.bin / name
        path.write_text(source)
        path.chmod(0o755)

    def run_launcher(self, *args):
        return subprocess.run([self.bash, str(self.repo / 'install.sh'), *args], cwd=self.work, env=self.env, capture_output=True, text=True)

    def test_unrelated_directory_and_argument_boundaries(self):
        self.shim('python')
        args = ['--tree', str(self.base / 'user tree'), '--font-dir', 'C:/Private/fonts with spaces', '--asset-dir', 'C:/Private/art', '--layout', 'base']
        result = self.run_launcher(*args)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual([str(self.repo / 'scripts/install.py')] + args, json.loads(self.capture.read_text()))

    def test_windows_python_automatically_registers_miktex(self):
        self.shim('python', platform='nt')
        result = self.run_launcher('--tree', 'C:/Private/tree')
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual([str(self.repo / 'scripts/install.py'), '--miktex', '--tree', 'C:/Private/tree'], json.loads(self.capture.read_text()))

    def test_py_launcher_fallback_after_old_python(self):
        self.shim('python', valid=False)
        self.shim('py', platform='nt')
        result = self.run_launcher('--configure')
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual([str(self.repo / 'scripts/install.py'), '--miktex', '--configure'], json.loads(self.capture.read_text()))

    def test_python3_fallback(self):
        self.shim('python3')
        result = self.run_launcher('--miktex')
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual([str(self.repo / 'scripts/install.py'), '--miktex'], json.loads(self.capture.read_text()))

    def test_no_compatible_python_reports_error_without_installing(self):
        self.shim('python', valid=False)
        result = self.run_launcher()
        self.assertEqual(1, result.returncode)
        self.assertIn('Python 3.9+ is required', result.stderr)
        self.assertFalse(self.capture.exists())

    def test_completely_missing_python_reports_error(self):
        result = self.run_launcher()
        self.assertEqual(1, result.returncode)
        self.assertIn('Python 3.9+ is required', result.stderr)
        self.assertFalse(self.capture.exists())

    def test_installer_exit_status_is_preserved(self):
        self.shim('python')
        self.env['WODTEX_TEST_EXIT'] = '7'
        self.assertEqual(7, self.run_launcher().returncode)

    def test_git_checkout_policy_keeps_launcher_lf(self):
        self.assertNotIn(b'\r\n', (ROOT / 'install.sh').read_bytes())
        result = subprocess.run(['git', 'check-attr', 'text', 'eol', '--', 'install.sh'], cwd=ROOT, capture_output=True, text=True, check=True)
        self.assertIn('install.sh: text: set', result.stdout)
        self.assertIn('install.sh: eol: lf', result.stdout)


if __name__ == '__main__':
    unittest.main()
