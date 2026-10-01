#!/usr/bin/env python3
"""Explicitly install the reconciled, opt-in original-template PDF source patch."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check', action='store_true', help='Check exact base files without changing them')
    mode.add_argument('--apply', action='store_true', help='Back up and install the checked source overrides')
    args = parser.parse_args()
    manifest = json.loads((HERE / 'manifest.json').read_text())
    entries = manifest['files']
    for entry in entries:
        relative = Path(entry['path'])
        if relative.is_absolute() or '..' in relative.parts or not (relative.parts[0] in ('tex', 'scripts', 'tests') or relative.as_posix() == 'profiles/m20.tex'):
            raise SystemExit('Unsafe patch path: ' + entry['path'])
        original, override = ROOT / relative, HERE / 'overrides' / relative
        if original.is_symlink() or override.is_symlink():
            raise SystemExit('Patch refuses symlinks: ' + entry['path'])
        if not override.is_file() or sha(override) != entry['sha256']:
            raise SystemExit('Override checksum mismatch: ' + entry['path'])
        expected = entry['base_sha256']
        if expected is None:
            if original.exists(): raise SystemExit('New path already exists: ' + entry['path'])
        elif not original.is_file() or sha(original) != expected:
            raise SystemExit('Base source changed; merge changes.patch instead: ' + entry['path'])
    print('Checked', len(entries), 'source files against', manifest['base_commit'])
    if args.check:
        return
    backup_parent = ROOT / 'build'
    backup_parent.mkdir(exist_ok=True)
    backup = Path(tempfile.mkdtemp(prefix='original-m20-layout-backup-', dir=backup_parent))
    for entry in entries:
        relative = Path(entry['path'])
        target = ROOT / relative
        if target.exists():
            saved = backup / relative
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, saved)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(HERE / 'overrides' / relative, target)
    print('Installed opt-in source patch; backups:', backup.relative_to(ROOT))
    print('Prepare the licensed original-template assets and run both output acceptance checks before use')

if __name__ == '__main__':
    main()
