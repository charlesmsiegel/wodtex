"""Native install tests use public substitute fixtures, never licensed artwork."""
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('wodtex_install', ROOT / 'scripts/install.py')
installer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(installer)


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='wodtex-install-')
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.tree = self.base / 'user tree'
        self.fonts = self.base / 'private fonts'
        self.assets = self.base / 'private art'
        self.fonts.mkdir()
        self.assets.mkdir()

    def install(self, layout='corrected', **kwargs):
        return installer.install(self.tree, layout, **kwargs)

    def first(self, layout='corrected'):
        return self.install(layout, font_dir=self.fonts, asset_dir=self.assets)

    def test_repeat_update_preserves_private_config_and_unrelated_files(self):
        _, target, config = self.first()
        config.write_text(config.read_text() + '% user customization\n')
        before = config.read_bytes()
        managed_before = {path.name: path.read_bytes() for path in target.iterdir()}
        unrelated = self.tree / 'unrelated.txt'
        unrelated.write_text('keep')
        self.install()
        self.assertEqual(before, config.read_bytes())
        self.assertEqual(managed_before, {path.name: path.read_bytes() for path in target.iterdir()})
        self.assertEqual('keep', unrelated.read_text())
        self.assertEqual('corrected', json.loads((target / installer.MANIFEST).read_text())['layout'])
        self.assertIn('m20-local-text-styles.sty', [p.name for p in target.iterdir()])

    def test_refuses_modified_added_and_unmanaged_files(self):
        _, target, _ = self.first()
        original = (target / 'm20book.cls').read_bytes()
        (target / 'm20book.cls').write_text('local edit')
        with self.assertRaisesRegex(ValueError, 'locally edited'):
            self.install()
        self.assertEqual('local edit', (target / 'm20book.cls').read_text())
        (target / 'm20book.cls').write_bytes(original)
        (target / 'user.tex').write_text('private')
        with self.assertRaisesRegex(ValueError, 'added/missing'):
            self.install()
        (target / 'user.tex').unlink()
        (target / installer.MANIFEST).unlink()
        with self.assertRaisesRegex(ValueError, 'unmanaged'):
            self.install()

    def test_first_install_and_reconfigure_are_explicit(self):
        with self.assertRaisesRegex(ValueError, 'First install'):
            self.install()
        _, _, config = self.first()
        with self.assertRaisesRegex(ValueError, 'Configuration exists'):
            self.first()
        alternate = self.base / 'other fonts'
        alternate.mkdir()
        self.install(font_dir=alternate, asset_dir=self.assets, configure=True)
        self.assertIn(alternate.as_posix(), config.read_text())

    def test_rejects_tex_path_injection(self):
        bad = self.base / 'font%bad'
        bad.mkdir()
        with self.assertRaisesRegex(ValueError, 'unsupported TeX'):
            self.install(font_dir=bad, asset_dir=self.assets)
        self.assertFalse(self.tree.exists())

    def test_layout_switch_removes_old_managed_files_only(self):
        _, target, config = self.first()
        before = config.read_bytes()
        self.install('base')
        self.assertFalse((target / 'm20-local-text-styles.sty').exists())
        self.assertEqual(before, config.read_bytes())
        self.install()
        self.assertTrue((target / 'm20-local-text-styles.sty').exists())

    def test_all_existing_profile_sources_are_installed(self):
        files = installer.payload('corrected')
        for path in (ROOT / 'profiles').glob('*.tex'):
            self.assertIn('wodtex-profile-' + path.name, files)
        for name, data in files.items():
            if name.endswith(('.cls', '.sty')):
                self.assertNotIn(b'tex/m20-', data)
                self.assertNotIn(b'profiles/', data)

    def test_symlinked_config_and_managed_parent_are_refused(self):
        if os.name == 'nt':
            self.skipTest('symlink privileges vary on Windows')
        _, _, config = self.first()
        private = self.base / 'do-not-overwrite.tex'
        private.write_text('private')
        config.unlink()
        config.symlink_to(private)
        with self.assertRaisesRegex(ValueError, 'symlink'):
            self.install(font_dir=self.fonts, asset_dir=self.assets, configure=True)
        self.assertEqual('private', private.read_text())
        second = self.base / 'second-tree'
        second.mkdir()
        (second / 'tex').symlink_to(self.tree / 'tex', target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'symlink'):
            installer.install(second, 'corrected', self.fonts, self.assets)

    def test_miktex_registration_refresh_and_failure_reporting(self):
        args = ['install.py', '--tree', str(self.tree), '--miktex',
                '--font-dir', str(self.fonts), '--asset-dir', str(self.assets)]
        with patch.object(sys, 'argv', args), patch.object(installer.shutil, 'which', return_value='tool'), patch.object(installer.subprocess, 'run') as run:
            installer.main()
        self.assertEqual(run.call_args_list[0].args[0], ['initexmf', '--register-root=' + str(self.tree)])
        self.assertEqual(run.call_args_list[1].args[0], ['miktex', 'fndb', 'refresh'])
        self.assertTrue(all(call.kwargs['check'] for call in run.call_args_list))
        args = ['install.py', '--tree', str(self.tree), '--miktex']
        with patch.object(sys, 'argv', args), patch.object(installer.shutil, 'which', return_value='tool'), patch.object(installer.subprocess, 'run', side_effect=subprocess.CalledProcessError(1, 'initexmf')):
            with self.assertRaises(SystemExit) as error:
                installer.main()
            self.assertEqual(1, error.exception.code)
        self.assertTrue((self.tree / 'tex/latex/wodtex-local/wodtex-local.tex').exists())

    def test_missing_miktex_tools_fail_before_writes(self):
        with patch.object(sys, 'argv', ['install.py', '--tree', str(self.tree), '--miktex']), patch.object(installer.shutil, 'which', return_value=None):
            with self.assertRaises(SystemExit) as error:
                installer.main()
            self.assertEqual(2, error.exception.code)
        self.assertFalse(self.tree.exists())

    def test_windows_crlf_checkout_installs_updates_and_rejects_real_edits(self):
        source = self.base / 'windows-source'
        source.mkdir()
        shutil.copy2(ROOT / 'm20book.cls', source / 'm20book.cls')
        for name in ('tex', 'profiles', 'contrib'):
            shutil.copytree(ROOT / name, source / name)
        for path in source.rglob('*'):
            if path.is_file() and path.suffix in ('.cls', '.sty', '.tex', '.lua', '.json', '.py', '.md', '.patch'):
                path.write_bytes(path.read_bytes().replace(b'\r\n', b'\n').replace(b'\n', b'\r\n'))
        expected = installer.payload('corrected')
        expected_base = installer.payload('base')
        with patch.object(installer, 'ROOT', source):
            self.assertEqual(expected, installer.payload('corrected'))
            self.assertEqual(expected_base, installer.payload('base'))
            _, target, config = self.first()
            before = config.read_bytes()
            self.install()
            self.assertEqual(before, config.read_bytes())
            for path in target.iterdir():
                self.assertNotIn(b'\r\n', path.read_bytes())
            changed = source / 'contrib/original-m20-layout/overrides/profiles/m20.tex'
            original = changed.read_bytes()
            for altered in (original.replace(b'612.0bp', b'613.0bp'), original.replace(b'\r\n', b'\r'), original + b' '):
                changed.write_bytes(altered)
                with self.assertRaisesRegex(ValueError, 'Correction checksum mismatch'):
                    self.install()
                self.assertEqual(before, config.read_bytes())
            changed.write_bytes(original)
            self.install()

    def test_source_archive_contains_complete_native_installer_payload(self):
        archive = ROOT / 'build/native-install-package-test/source.zip'
        subprocess.run([sys.executable, str(ROOT / 'scripts/package.py'), '--out', str(archive)], check=True, stdout=subprocess.DEVNULL)
        with zipfile.ZipFile(archive) as zipped:
            zipped.extractall(self.base / 'unpack')
        unpacked = self.base / 'unpack/wodtex-m20'
        self.assertEqual((ROOT / '.gitattributes').read_bytes(), (unpacked / '.gitattributes').read_bytes())
        self.assertEqual((ROOT / 'install.sh').read_bytes(), (unpacked / 'install.sh').read_bytes())
        expected = installer.payload('corrected')
        with patch.object(installer, 'ROOT', unpacked):
            self.assertEqual(expected, installer.payload('corrected'))
        subprocess.run([sys.executable, str(unpacked / 'scripts/install.py'), '--tree', str(self.tree), '--font-dir', str(self.fonts), '--asset-dir', str(self.assets)], check=True, stdout=subprocess.DEVNULL)
        self.assertTrue((self.tree / 'tex/latex/wodtex/m20book.cls').is_file())

    @unittest.skipUnless(shutil.which('lualatex') and shutil.which('pdftotext'), 'LuaLaTeX and Poppler required')
    def test_outside_repository_native_compile_before_and_after_update(self):
        # Public DejaVu faces stand in for licensed font filenames solely here.
        public = Path('/usr/share/fonts/truetype/dejavu')
        if not public.exists():
            self.skipTest('public DejaVu fixture fonts not available')
        names = {'GOUDOS.TTF': 'DejaVuSerif.ttf', 'GOUDOSB_0.TTF': 'DejaVuSerif-Bold.ttf',
                 'GOUDOSI_0.TTF': 'DejaVuSerif-Italic.ttf', 'abbess-regular.ttf': 'DejaVuSansCondensed.ttf',
                 'FuturaPTBook.otf': 'DejaVuSans.ttf', 'NotoSerif-BoldItalic.ttf': 'DejaVuSerif-BoldItalic.ttf',
                 'NotoSans-Bold.ttf': 'DejaVuSans-Bold.ttf', 'NotoSans-Italic.ttf': 'DejaVuSans-Oblique.ttf',
                 'NotoSans-BoldItalic.ttf': 'DejaVuSans-BoldOblique.ttf'}
        for path in public.glob('DejaVuSans*.ttf'):
            shutil.copy2(path, self.fonts / path.name)
        from fontTools.ttLib import TTFont
        # Give aliased substitute faces unique identities: duplicate PostScript
        # names otherwise confuse the font loader during PDF embedding.
        for index, (name, source) in enumerate(names.items()):
            face = TTFont(public / source)
            for record in face['name'].names:
                if record.nameID in (1, 3, 4, 6, 16):
                    record.string = ('WodtexFixture' + str(index)).encode(record.getEncoding())
            face.save(self.fonts / name)
            face.close()
        work = self.base / 'book outside repo'
        work.mkdir()
        (work / 'fixture.tex').write_text(r'\documentclass{article}\pagestyle{empty}\begin{document}Public art fixture\newpage Public art fixture page two\end{document}')
        subprocess.run(['lualatex', '-interaction=nonstopmode', '-halt-on-error', 'fixture.tex'], cwd=work, check=True, stdout=subprocess.DEVNULL)
        # Every referenced corrected decoration is a clearly synthetic fixture.
        resources = installer.payload('corrected')
        art_names = set()
        for data in resources.values():
            art_names.update(re.findall(rb'([a-z-]+\.original-template\.pdf)', data))
        for name in art_names:
            shutil.copy2(work / 'fixture.pdf', self.assets / name.decode())
        shutil.copy2(ROOT / 'examples/content/diagram.png', self.assets / 'page_border.png')
        shutil.copy2(work / 'fixture.pdf', work / 'art.pdf')
        (work / 'book.tex').write_text(r'''\documentclass{m20book}
\m20setup{running-title={Portable smoke}}
\begin{document}
\chapter{Portable install}\label{ch:portable}
BODY-SMOKE with \textbf{bold} and \textit{italic}.
\begin{m20sidebar}[id=portable-sidebar]{Portable sidebar}SIDEBAR-SMOKE\end{m20sidebar}
\begin{m20table}[id=portable-table,head-rows=1,width=column]{lr}
TABLE-SMOKE & Value \\ Row & 42 \\
\end{m20table}
\m20artreserve[kind=horizontal,position=bottom,place=next-page,image=art.pdf,alt={Public test fixture},caption={ART-SMOKE}]{portable-art}
Reference page \pageref{ch:portable}. END-SMOKE.
\end{document}
''')
        _, target, config = self.first()
        env = dict(os.environ, TEXMFHOME=str(self.tree))
        for layout in ('corrected', 'corrected', 'base'):
            self.install(layout)
            for _ in range(2):
                result = subprocess.run(['lualatex', '-recorder', '-interaction=nonstopmode', '-halt-on-error', 'book.tex'], cwd=work, env=env, capture_output=True, text=True)
                self.assertEqual(0, result.returncode, result.stdout[-7000:])
            text = subprocess.check_output(['pdftotext', 'book.pdf', '-'], cwd=work, text=True)
            for token in ('BODY-SMOKE', 'SIDEBAR-SMOKE', 'TABLE-SMOKE', 'ART-SMOKE', 'END-SMOKE'):
                self.assertIn(token, text)
            log = (work / 'book.log').read_text()
            self.assertNotIn('undefined references', log)
            self.assertIn(str(config), (work / 'book.fls').read_text())
            self.assertIn(str(self.fonts), log)
            self.assertIn(str(self.assets), (work / 'book.fls').read_text())
            self.assertIn(str(target / 'wodtex-profile-m20.tex'), (work / 'book.fls').read_text())
            if layout == 'corrected':
                self.assertIn(str(target / 'm20-local-text-styles.sty'), (work / 'book.fls').read_text())


if __name__ == '__main__':
    unittest.main()
