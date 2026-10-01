#!/usr/bin/env python3
"""Install/update wodtex in a private user TEXMF tree; never copy licensed inputs."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = '.wodtex-installed.json'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical_text(data):
    # Git's Windows checkout conversion may use CRLF. Manifests describe LF
    # text: normalize only CRLF pairs, preserving all other bytes (including
    # bare CRs, trailing whitespace, BOMs and actual source modifications).
    return data.replace(b'\r\n', b'\n')


def payload(layout):
    files = {'m20book.cls': canonical_text((ROOT / 'm20book.cls').read_bytes())}
    for path in sorted((ROOT / 'tex').glob('*')):
        if path.suffix in ('.sty', '.lua'):
            files[path.name] = canonical_text(path.read_bytes())
    for path in sorted((ROOT / 'profiles').glob('*.tex')):
        files['wodtex-profile-' + path.name] = canonical_text(path.read_bytes())
    if layout == 'corrected':
        patch = ROOT / 'contrib/original-m20-layout'
        manifest = json.loads((patch / 'manifest.json').read_text())
        for entry in manifest['files']:
            relative = Path(entry['path'])
            if relative.is_absolute() or '..' in relative.parts:
                raise ValueError('Unsafe correction path: ' + str(relative))
            if relative.parts[0] not in ('tex', 'profiles'):
                continue
            path = patch / 'overrides' / relative
            data = canonical_text(path.read_bytes())
            if path.is_symlink() or digest(data) != entry['sha256']:
                raise ValueError('Correction checksum mismatch: ' + str(relative))
            name = relative.name if relative.parts[0] == 'tex' else 'wodtex-profile-' + relative.name
            files[name] = data
    # Keep the source build and its checked correction manifest intact. Installed
    # resources use unique kpathsea names rather than repository-relative paths.
    for name, data in list(files.items()):
        if name.endswith(('.cls', '.sty', '.tex')):
            data = data.replace(b'tex/m20-', b'm20-')
            data = data.replace(b'profiles/m20.tex', b'wodtex-profile-m20.tex')
            data = data.replace(b'profiles/\\mTwentyProfile.tex', b'wodtex-profile-\\mTwentyProfile.tex')
        if name == 'm20book.cls':
            data = data.replace(b'\\RequirePackage{m20-core}',
                                b'\\InputIfFileExists{wodtex-local.tex}{}{}\n\\RequirePackage{m20-core}')
        files[name] = data
    return files


def tex_path(path):
    value = path.expanduser().resolve().as_posix()
    # Generated TeX must never interpret a path as commands or a comment.
    if any(char in value for char in '{}%#\\\n\r~^&$'):
        raise ValueError('Path contains unsupported TeX characters: ' + value)
    if not path.expanduser().is_dir():
        raise ValueError('Input directory does not exist: ' + value)
    return value.rstrip('/') + '/'


def install(tree, layout, font_dir=None, asset_dir=None, configure=False):
    tree = tree.expanduser().resolve()
    target = tree / 'tex/latex/wodtex'
    config_dir = tree / 'tex/latex/wodtex-local'
    config = config_dir / 'wodtex-local.tex'
    for path in (tree / 'tex', tree / 'tex/latex', target, config_dir, config):
        if path.is_symlink():
            raise ValueError('Refusing symlink in installation: ' + str(path))
    if (font_dir is None) != (asset_dir is None):
        raise ValueError('Supply both --font-dir and --asset-dir')
    if not config.exists() and font_dir is None:
        raise ValueError('First install requires --font-dir and --asset-dir')
    if config.exists() and font_dir is not None and not configure:
        raise ValueError('Configuration exists; use --configure to explicitly replace it')
    config_data = None
    if font_dir is not None:
        config_data = ('% Private local paths; preserved by wodtex updates.\n'
                       '\\def\\mTwentyBuildFontPath{' + tex_path(font_dir) + '}\n'
                       '\\def\\mTwentyBuildAssetPath{' + tex_path(asset_dir) + '}\n')
    files = payload(layout)
    # Refuse unowned trees and locally edited managed files, rather than silently
    # deleting user data. Only this dedicated directory is replaced on update.
    if target.exists():
        marker = target / MANIFEST
        if target.is_symlink() or not marker.is_file():
            raise ValueError('Refusing unmanaged installation: ' + str(target))
        old = json.loads(marker.read_text())
        expected = old['files']
        actual = {p.name for p in target.iterdir() if p.name != MANIFEST}
        if actual != set(expected):
            raise ValueError('Managed directory contains added/missing files; back up and reconcile first')
        for name, sha in expected.items():
            path = target / name
            if Path(name).name != name or path.is_symlink() or not path.is_file() or digest(path.read_bytes()) != sha:
                raise ValueError('Managed file was locally edited: ' + name)
    target.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix='.wodtex-stage-', dir=target.parent))
    backup = None
    try:
        for name, data in files.items():
            (staging / name).write_bytes(data)
        (staging / MANIFEST).write_text(json.dumps({'schema': 1, 'layout': layout,
             'files': {name: digest(data) for name, data in files.items()}}, indent=2) + '\n')
        if target.exists():
            backup = Path(tempfile.mkdtemp(prefix='.wodtex-backup-', dir=target.parent))
            backup.rmdir()
            target.rename(backup)
        try:
            staging.rename(target)
        except OSError:
            if backup is not None:
                backup.rename(target)
                backup = None
            raise
        if config_data is not None:
            config_dir.mkdir(parents=True, exist_ok=True)
            config.write_text(config_data, encoding='utf-8')
    finally:
        if staging.exists():
            shutil.rmtree(staging)
        if backup is not None:
            shutil.rmtree(backup)
    return tree, target, config


def main():
    default = Path(os.environ.get('LOCALAPPDATA', str(Path.home()))) / 'wodtex/texmf' if os.name == 'nt' else Path.home() / 'texmf'
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tree', type=Path, default=default)
    parser.add_argument('--layout', choices=('corrected', 'base'), default='corrected')
    parser.add_argument('--font-dir', type=Path)
    parser.add_argument('--asset-dir', type=Path)
    parser.add_argument('--configure', action='store_true', help='Explicitly replace private path configuration')
    parser.add_argument('--miktex', action='store_true', help='Register root in MiKTeX user mode and refresh FNDB')
    args = parser.parse_args()
    if args.miktex:
        for command in ('initexmf', 'miktex'):
            if shutil.which(command) is None:
                parser.error(command + ' must be on PATH before installation')
    try:
        tree, target, config = install(args.tree, args.layout, args.font_dir, args.asset_dir, args.configure)
        print('Installed ' + args.layout + ' layout: ' + str(target))
        print('Private configuration: ' + str(config))
        if args.miktex:
            subprocess.run(['initexmf', '--register-root=' + str(tree)], check=True)
            subprocess.run(['miktex', 'fndb', 'refresh'], check=True)
            print('MiKTeX user root registered and FNDB refreshed')
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, str(error) + '\n')


if __name__ == '__main__':
    main()
