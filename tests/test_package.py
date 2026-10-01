"""Verify actual unpack/setup/build using separately supplied licensed inputs."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
import zipfile
from tests.support import ROOT

class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out=ROOT/'build/package-test';cls.out.mkdir(parents=True,exist_ok=True)
        cls.archive=cls.out/'wodtex-m20.zip'
        p=subprocess.run([sys.executable,'scripts/package.py','--out',str(cls.archive)],cwd=ROOT,text=True,capture_output=True)
        if p.returncode:raise RuntimeError(p.stdout+p.stderr)

    def test_package_hashes_paths_and_licensed_exclusions(self):
        with zipfile.ZipFile(self.archive) as z:
            hashes=json.loads(z.read('wodtex-m20/PACKAGE-HASHES.json'))
            self.assertIn('m20book.cls',hashes)
            self.assertIn('docs/README.txt',hashes)
            for name in z.namelist():
                p=Path(name)
                self.assertFalse(p.is_absolute() or '..' in p.parts)
                self.assertFalse(set(p.parts)&{'fonts','assets','inputs','.runtime','build'})
                data=z.read(name)
                self.assertNotIn(ROOT.as_posix().encode(),data,name)
                relative=p.relative_to('wodtex-m20').as_posix()
                if relative in hashes:self.assertEqual(hashlib.sha256(data).hexdigest(),hashes[relative])
        second=self.out/'second.zip'
        p=subprocess.run([sys.executable,'scripts/package.py','--out',str(second)],cwd=ROOT,capture_output=True)
        self.assertEqual(p.returncode,0)
        self.assertEqual(self.archive.read_bytes(),second.read_bytes())

    def test_fresh_unpack_builds_both_targets(self):
        template=Path(os.environ.get('WODTEX_TEMPLATE_ZIP',ROOT.parent/'mage-templates.zip'))
        if not template.is_file():self.skipTest('Supply WODTEX_TEMPLATE_ZIP to run licensed fresh-setup integration')
        unpack=self.out/'fresh'
        if unpack.exists():shutil.rmtree(unpack)
        with zipfile.ZipFile(self.archive) as z:z.extractall(unpack)
        project=unpack/'wodtex-m20'
        # Download-cache reuse avoids redundant network transfers. No generated
        # formats, installed TeX tree or proprietary prepared art is reused.
        for subdir in ('downloads','fonts'):
            shutil.copytree(ROOT/'.runtime'/subdir,project/'.runtime'/subdir)
        commands=[
            [sys.executable,'scripts/preflight.py','--prepare'],
            [sys.executable,'scripts/prepare_assets.py','--template-zip',str(template)],
            [sys.executable,'scripts/build.py','--target','all','--source','examples/book.tex','--out','build/book','--verify']]
        for index,command in enumerate(commands):
            with (self.out/f'fresh-{index}.log').open('w') as stream:
                p=subprocess.run(command,cwd=project,stdout=stream,stderr=subprocess.STDOUT,timeout=480)
            self.assertEqual(p.returncode,0,(self.out/f'fresh-{index}.log').read_text()[-5000:])
        report=json.loads((project/'build/book/build-report.json').read_text())
        self.assertEqual(report['status'],'passed')
        for target in ('pdf','epub'):
            entry=report['targets'][target]
            self.assertEqual(entry['verification']['errors'],[])
            self.assertEqual(hashlib.sha256(Path(entry['output']).read_bytes()).hexdigest(),entry['sha256'])
