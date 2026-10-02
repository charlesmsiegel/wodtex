"""Prepare and install every family from the actual source-only release archive."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from tests.test_x20_foundation import ROOT, module


@unittest.skipUnless(os.environ.get('WODTEX_X20_ARCHIVE'), 'Set WODTEX_X20_ARCHIVE=1 for fresh archive proofs')
class FreshArchiveTests(unittest.TestCase):
    def test_all_families_prepare_install_compile_and_update_from_fresh_archive(self):
        import fitz
        evidence = ROOT / 'build/x20/archive-proof'
        evidence.mkdir(parents=True, exist_ok=True)
        command = module('profile_build').latex_command()
        source_root = Path(os.environ.get('WODTEX_X20_SOURCE', 'C:/Users/charl/Downloads/templates/WOD/X20'))
        subprocess.run([sys.executable, str(ROOT / 'scripts/package.py'), '--out', str(evidence / 'source.zip')], check=True, capture_output=True)
        with tempfile.TemporaryDirectory(prefix='fresh archive ', dir=ROOT / 'build/x20') as temporary:
            base = Path(temporary)
            with zipfile.ZipFile(evidence / 'source.zip') as archive:
                archive.extractall(base)
            project = base / 'wodtex-m20'
            resources = base / 'prepared inputs'
            prepared = subprocess.run([sys.executable, 'scripts/prepare_profile.py', '--profile', 'all', '--source-root', str(source_root), '--out', str(resources)], cwd=project, capture_output=True, timeout=240)
            (evidence / 'prepare.stdout').write_bytes(prepared.stdout + prepared.stderr)
            self.assertEqual(0, prepared.returncode, prepared.stderr.decode(errors='replace'))
            tree = base / 'user tree'
            # Source archives intentionally exclude licensed M20 inputs. Supply
            # those separately, exactly as documented for archive installations.
            install = [sys.executable, 'scripts/install.py', '--tree', str(tree)]
            result = subprocess.run(install + ['--font-dir', str(ROOT / 'fonts'), '--asset-dir', str(ROOT / 'assets'), '--profile-root', str(resources)], cwd=project, capture_output=True)
            self.assertEqual(0, result.returncode, result.stderr.decode(errors='replace'))
            target = tree / 'tex/latex/wodtex'
            config = tree / 'tex/latex/wodtex-local'
            before = {p.relative_to(tree).as_posix(): p.read_bytes() for p in tree.rglob('*') if p.is_file()}
            env = dict(os.environ)
            env['PATH'] = str(Path(command).parent) + os.pathsep + env.get('PATH', '')
            env['TEXINPUTS'] = os.pathsep.join((str(target), str(config), ''))
            profiles = module('profile_registry').load_profiles(project)
            results = {}
            for style, profile in profiles.items():
                with self.subTest(style=style):
                    work = base / ('external manuscript ' + style)
                    work.mkdir()
                    if style == 'm20':
                        source = (r'\documentclass{m20book}\title{Archive M20}\begin{document}'
                                  r'\mainmatter\chapter{Archive Chapter}ConservedArchiveMarker.'
                                  r'\begin{sidebar}{Archive Note}ConservedArchiveSidebar.\end{sidebar}\end{document}')
                    else:
                        source = (project / 'examples/profiles' / (style + '.tex')).read_text()
                    (work / 'book.tex').write_text(source, encoding='utf-8')
                    art = base / 'art'
                    art.mkdir(exist_ok=True)
                    shutil.copy2(project / 'examples/art/scene.png', art / 'scene.png')
                    for number in range(3):
                        result = subprocess.run([command, '--disable-installer', '-no-shell-escape', '-interaction=nonstopmode', '-halt-on-error', 'book.tex'], cwd=work, env=env, capture_output=True, timeout=180)
                        (evidence / (style + '-pass-' + str(number) + '.stdout')).write_bytes(result.stdout + result.stderr)
                        self.assertEqual(0, result.returncode, result.stdout.decode(errors='replace')[-2500:])
                        idx = work / 'book.idx'
                        if idx.exists() and idx.stat().st_size:
                            indexed = subprocess.run([shutil.which('makeindex', path=env['PATH']), 'book.idx'], cwd=work, env=env, capture_output=True)
                            self.assertEqual(0, indexed.returncode)
                    log = (work / 'book.log').read_text(errors='replace')
                    self.assertNotIn('Missing character:', log)
                    self.assertNotIn('undefined references', log)
                    shutil.copy2(work / 'book.pdf', evidence / (style + '.pdf'))
                    with fitz.open(work / 'book.pdf') as pdf:
                        text = ''.join(page.get_text() for page in pdf)
                        self.assertIn('ConservedArchiveSidebar.' if style == 'm20' else 'Conserved sidebar', text)
                        results[style] = {'class': profile['class'], 'pages': len(pdf)}
            result = subprocess.run(install, cwd=project, capture_output=True)
            self.assertEqual(0, result.returncode, result.stderr.decode(errors='replace'))
            self.assertEqual(before, {p.relative_to(tree).as_posix(): p.read_bytes() for p in tree.rglob('*') if p.is_file()})
            (evidence / 'report.json').write_text(json.dumps(results, indent=2) + '\n')


if __name__ == '__main__':
    unittest.main()
