#!/usr/bin/env python3
"""Pinned, workspace-only LuaLaTeX and TeX4ht runtime inspection/preparation."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DIST = Path('/usr/share/texlive/texmf-dist')
SECONDARY = Path('/usr/share/texmf')
WRITABLE_ENV = ('TEXMFVAR','TEXMFCONFIG','TEXMFCACHE','TEXMFHOME','TEXMFOUTPUT','VARTEXFONTS','XDG_CACHE_HOME','TMPDIR')
PDF_PACKAGES = ('luaotfload.sty','fontspec.sty','babel.sty','luatexbase.sty','geometry.sty','graphicx.sty','amsmath.sty')

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def workspace_path(path):
    p = Path(path).resolve()
    if not any(p.is_relative_to(ROOT / x) for x in ('.runtime','build')):
        raise ValueError('All writable caches/formats must be under project .runtime or build: ' + str(p))
    return p

def runtime_environment(cache_dir):
    cache = workspace_path(cache_dir)
    env = dict(os.environ)
    for key, sub in zip(WRITABLE_ENV, ('texmf-var','texmf-config','texmf-cache','texmf-home','output','fonts','cache','tmp')):
        p = cache if key == 'TEXMFOUTPUT' else cache / sub; p.mkdir(parents=True, exist_ok=True); env[key] = str(p)
    (cache / 'formats').mkdir(parents=True, exist_ok=True)
    trees = [ROOT / '.runtime/texmf', ROOT / '.runtime/texmf/texmf-dist', cache / 'texmf-home', DIST, SECONDARY]
    env.update(TEXMF='{'+','.join(map(str, trees))+'}', TEXMFCNF=str(cache / 'texmf-config')+':'+str(DIST / 'web2c'),
               TEXMFDBS='', TEXFORMATS=str(cache / 'formats')+'//',
               LUAINPUTS='.'+':'+':'.join(str(p)+'//' for p in trees),
               openin_any='a', openout_any='p', shell_escape='f', MKTEXFMT='0', MKTEXPK='0', MKTEXTFM='0', MKTEXMF='0',
               TEX4HTENV=str(ROOT / '.runtime/texmf/texmf-dist/tex4ht/base/unix/tex4ht.env'), TEX4HTFONTSET=str(ROOT / '.runtime/texmf/texmf-dist/tex4ht/ht-fonts'),
               SOURCE_DATE_EPOCH='1790784000', FORCE_SOURCE_DATE='1', TZ='UTC')
    env['PATH'] = str(ROOT / '.runtime/bin') + os.pathsep + env.get('PATH','')
    return env

def run(command, cwd, env, log, timeout=240):
    log = workspace_path(log); log.parent.mkdir(parents=True, exist_ok=True)
    with log.open('w') as f:
        result = subprocess.run(command, cwd=cwd, env=env, stdout=f, stderr=subprocess.STDOUT, timeout=timeout, check=False)
    if result.returncode:
        raise RuntimeError('Runtime command failed ('+str(result.returncode)+'): '+str(command)+'; see '+str(log))
    return result

def prepare_dependencies(cache):
    lock = json.loads((ROOT / 'runtime.lock.json').read_text())
    runtime = ROOT / '.runtime'; downloads = runtime / 'downloads'; downloads.mkdir(parents=True, exist_ok=True)
    sources = runtime / 'sources'; sources.mkdir(exist_ok=True)
    texmf = runtime / 'texmf'; texmf.mkdir(exist_ok=True)
    for item in lock['dependencies']:
        archive = downloads / item['archive']
        if not archive.exists():
            urllib.request.urlretrieve(item['url'], archive)
        if digest(archive) != item['sha256']:
            raise RuntimeError('M20_E_DEPENDENCY_HASH: '+item['name'])
        if archive.suffix == '.zip':
            with zipfile.ZipFile(archive) as z:
                for member in z.infolist():
                    p = Path(member.filename)
                    if p.is_absolute() or '..' in p.parts or ((member.external_attr >> 16) & 0o170000) == 0o120000:
                        raise ValueError('Unsafe dependency archive member: '+member.filename)
                z.extractall(runtime if item['name'] == 'epubcheck' else sources)
            if item['name'] != 'epubcheck':
                name = item['name']; src = sources / name
                dst = texmf / ('scripts/'+name if name in ('make4ht','tex4ebook') else 'tex/luatex/'+name)
                shutil.copytree(src, dst, dirs_exist_ok=True)
                if name == 'tex4ebook':
                    texdst = texmf / 'tex/latex/tex4ebook'; texdst.mkdir(parents=True, exist_ok=True)
                    for f in src.iterdir():
                        if f.suffix in ('.sty','.4ht','.conf'):
                            shutil.copyfile(f, texdst / f.name)
        else:
            with tarfile.open(archive) as z:
                z.extractall(texmf, filter='data')
    bindir = runtime / 'bin'; bindir.mkdir(exist_ok=True)
    for name in ('make4ht','tex4ebook'):
        (bindir / name).write_text('#!/bin/sh\nexec texlua "'+str(texmf / 'scripts' / name / name)+'" "$@"\n')
        (bindir / name).chmod(0o755)
    (bindir / 'epubcheck').write_text('#!/bin/sh\nexec java -jar "'+str(runtime / 'epubcheck-5.3.0/epubcheck.jar')+'" "$@"\n')
    (bindir / 'epubcheck').chmod(0o755)

def prepare_formats(cache_dir):
    cache = workspace_path(cache_dir); env = runtime_environment(cache)
    base = ROOT / '.runtime/sources/luatexbase'
    if not (ROOT / '.runtime/texmf/tex/luatex/lualibs/lualibs.lua').exists():
        work = cache / 'docstrip-lualibs'; work.mkdir(exist_ok=True)
        shutil.copyfile(ROOT / '.runtime/sources/lualibs/lualibs.dtx', work / 'lualibs.dtx')
        run(['pdftex','-ini','-no-shell-escape','-interaction=nonstopmode','-halt-on-error',r'\input plain \input lualibs.dtx'], work, env, work / 'docstrip.stdout')
        for p in work.glob('*.lua'):
            shutil.copyfile(p, ROOT / '.runtime/texmf/tex/luatex/lualibs' / p.name)
    if not (ROOT / '.runtime/texmf/tex/luatex/luatexbase/luatexbase.sty').exists():
        work = cache / 'docstrip'; work.mkdir(exist_ok=True)
        for name in ('luatexbase.ins','luatexbase.dtx'):
            shutil.copyfile(base / name, work / name)
        run(['pdftex','-ini','-no-shell-escape','-interaction=nonstopmode','-halt-on-error',r'\input plain \input luatexbase.ins'], work, env, work / 'docstrip.stdout')
        for p in work.iterdir():
            if p.suffix in ('.sty','.lua'):
                shutil.copyfile(p, ROOT / '.runtime/texmf/tex/luatex/luatexbase' / p.name)
    for name in ('lualatex','dvilualatex'):
        if not (cache / 'formats' / (name+'.fmt')).exists():
            run(['luahbtex' if name == 'lualatex' else 'luatex','-ini','-etex','-no-shell-escape','-interaction=nonstopmode',
                 '-halt-on-error','-jobname='+name,'-progname='+name,'-output-directory='+str(cache / 'formats'),name+'.ini'],
                cache / 'formats', env, cache / 'formats' / (name+'.stdout'))
    return env

def tool_info(name, env, args=('--version',)):
    path = shutil.which(name, path=env['PATH'])
    if not path:
        return {'available': False, 'path': None, 'version': None}
    try:
        p = subprocess.run([path, *args], env=env, text=True, capture_output=True, timeout=30)
        lines = (p.stdout+p.stderr).strip().splitlines()
        return {'available': p.returncode == 0, 'path': path, 'version': lines[0] if lines else '', 'exit_code': p.returncode}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {'available': False, 'path': path, 'version': None, 'error': str(exc)}

def evaluate_availability(engines, packages):
    diagnostics = []
    for name in PDF_PACKAGES:
        if not packages.get(name):
            diagnostics.append({'code': 'M20_E_LUAOTFLOAD_MISSING' if name == 'luaotfload.sty' else 'M20_E_PACKAGE_MISSING',
                                'severity': 'error', 'target': 'pdf', 'message': 'Required LuaLaTeX package unavailable: '+name})
    if not engines.get('lualatex', {}).get('available'):
        diagnostics.append({'code':'M20_E_ENGINE_MISSING','severity':'error','target':'pdf','message':'LuaLaTeX is required; no engine substitution permitted'})
    return {'pdf_ready': not diagnostics, 'diagnostics': diagnostics}

def preflight(cache_dir, prepare=False):
    cache = workspace_path(cache_dir)
    if prepare:
        prepare_dependencies(cache); env = prepare_formats(cache)
    else:
        env = runtime_environment(cache)
    engines = {name:tool_info(name, env) for name in ('lualatex','luatex')}
    packages = {}
    for name in (*PDF_PACKAGES, 'tex4ht.sty','tex4ebook.sty','paracol.sty','cuted.sty','tcolorbox.sty'):
        p = subprocess.run(['kpsewhich',name],env=env,text=True,capture_output=True)
        packages[name] = p.stdout.strip() or None
    result = evaluate_availability(engines, packages)
    result.update(engines=engines, packages=packages, environment=env,
                  index={'makeindex':tool_info('makeindex',env,args=('--help',))},
                  converters={name:tool_info(name,env,args=('-v',) if name == 'epubcheck' else ('--version',)) for name in ('tex4ebook','make4ht','tex4ht','epubcheck')},
                  fonts=json.loads((ROOT / 'profiles/m20.json').read_text())['fonts'] if (ROOT / 'profiles/m20.json').exists() else [],
                  formats={name:str(cache / 'formats' / (name+'.fmt')) for name in ('lualatex','dvilualatex')})
    result['pdf_ready'] = result['pdf_ready'] and (cache / 'formats/lualatex.fmt').exists()
    if not (cache / 'formats/lualatex.fmt').exists():
        result['diagnostics'].append({'code':'M20_E_FORMAT_MISSING','severity':'error','target':'pdf','message':'Run preflight with prepare=True to generate workspace LuaLaTeX format'})
    result['epub_ready'] = all(result['converters'][name]['available'] for name in ('tex4ebook','make4ht','epubcheck')) and bool(packages['tex4ht.sty']) and (cache / 'formats/dvilualatex.fmt').exists()
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--cache-dir', default=str(ROOT / '.runtime')); parser.add_argument('--prepare',action='store_true')
    args = parser.parse_args()
    report = preflight(args.cache_dir,args.prepare)
    report['environment'] = {k:v for k,v in report['environment'].items() if k in WRITABLE_ENV or k.startswith(('TEX','LUA','MKTEX')) or k in ('openin_any','openout_any','shell_escape','SOURCE_DATE_EPOCH','FORCE_SOURCE_DATE','TZ')}
    print(json.dumps(report,indent=2))
