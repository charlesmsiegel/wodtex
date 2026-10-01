#!/usr/bin/env python3
"""Create a deterministic, source-only template archive from an explicit allowlist."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile
from preflight import ROOT, workspace_path

def package(output):
    manifest=json.loads((ROOT/'package-manifest.json').read_text())
    files=sorted({p for pattern in manifest['include'] for p in ROOT.glob(pattern) if p.is_file()})
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    output=workspace_path(output);output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for path in files:
            relative=path.relative_to(ROOT)
            if path.is_symlink() or any(part in manifest['excluded_inputs'] for part in relative.parts):
                raise ValueError('Unpermitted package input: '+str(relative))
            entry=zipfile.ZipInfo('wodtex-m20/'+relative.as_posix(),date_time=(2026,9,30,0,0,0))
            entry.compress_type=zipfile.ZIP_DEFLATED;entry.external_attr=0o100644<<16
            z.writestr(entry,path.read_bytes())
        entry=zipfile.ZipInfo('wodtex-m20/PACKAGE-HASHES.json',date_time=(2026,9,30,0,0,0))
        entry.compress_type=zipfile.ZIP_DEFLATED;entry.external_attr=0o100644<<16
        z.writestr(entry,json.dumps(hashes,indent=2)+'\n')
    return {'output':str(output),'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'source_files':len(files)}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',default='build/packages/wodtex-m20.zip')
    print(json.dumps(package(p.parse_args().out),indent=2))
