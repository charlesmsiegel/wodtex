#!/usr/bin/env python3
"""Build one native manuscript with bounded PDF and EPUB adapters."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from preflight import ROOT, preflight, runtime_environment, workspace_path

class BuildError(RuntimeError):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def execute(command, cwd, env, logfile, timeout=240):
    with logfile.open('w') as stream:
        try:
            result = subprocess.run(command, cwd=cwd, env=env, stdout=stream,
                                    stderr=subprocess.STDOUT, timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            raise BuildError('M20_E_TIMEOUT', f'Command timed out; see {logfile}') from exc
    if result.returncode:
        text = logfile.read_text(errors='replace')
        codes = re.findall(r'M20_E_[A-Z_]+', text)
        raise BuildError(codes[-1] if codes else 'M20_E_BUILD', f'Command failed; see {logfile}')

def wrapper(source, work, target):
    name = source.stem
    path = work / 'driver.tex'
    path.write_text(
        '\\PassOptionsToClass{output='+target+'}{m20book}\n'
        '\\def\\mTwentyBuildFontPath{'+ROOT.as_posix()+'/fonts/}\n'
        '\\def\\mTwentyBuildAssetPath{'+ROOT.as_posix()+'/assets/}\n'
        '\\input{\\detokenize{'+source.as_posix()+'}}\n')
    return name, path

def aux_state(work, name):
    return {suffix:sha(p) for suffix in ('.aux','.toc','.out','.ind')
            if (p := work/(name+suffix)).exists()}

def build_pdf(source, work, env, max_runs=8):
    name, driver = wrapper(source, work, 'pdf')
    # An old index is not an input manuscript. Recreate its source on each build.
    (work/(name+'.idx')).unlink(missing_ok=True)
    previous = None
    indexed = None
    for run in range(1, max_runs+1):
        execute(['lualatex','-no-shell-escape','-interaction=nonstopmode','-halt-on-error',
                 '-jobname='+name,'-output-directory='+str(work),str(driver)], ROOT, env,
                work/f'pass-{run}.stdout')
        idx = work/(name+'.idx')
        if idx.exists() and idx.stat().st_size and sha(idx) != indexed:
            execute(['makeindex','-o',name+'.ind','-t',name+'.ilg',idx.name],
                    work, env, work/f'index-{run}.stdout')
            indexed = sha(idx)
        elif not idx.exists() or not idx.stat().st_size:
            for suffix in ('.ind','.ilg'):
                (work/(name+suffix)).unlink(missing_ok=True)
        state = aux_state(work, name)
        if state == previous:
            text = (work/(name+'.log')).read_text(errors='replace')
            if re.search(r'undefined references|Citation .* undefined|Reference .* undefined',text):
                raise BuildError('M20_E_UNRESOLVED_REFERENCE','References remain unresolved after convergence')
            if 'Missing character:' in text:
                raise BuildError('M20_E_MISSING_GLYPH','Missing glyph; declare a genuine script font')
            if re.search(r'Font shape .* undefined|Some font shapes were not available',text):
                raise BuildError('M20_E_FONT_SUBSTITUTION','An undeclared font face was substituted')
            return work/(name+'.pdf'), run
        previous = state
    raise BuildError('M20_E_NONCONVERGING',f'Auxiliary files did not settle after {max_runs} passes')

def check_epub_content(source,enforce=True):
    supported = json.loads((ROOT/'epub/supported-content.json').read_text())
    seen = set()
    declared = set()
    definitions = set()
    environments = set()
    def visit(path):
        path = path.resolve()
        if path in seen: return
        seen.add(path)
        text = re.sub(r'(?<!\\)%[^\n]*','',path.read_text())
        for names in re.findall(r'\\m20epubsafe\s*\{([^}]+)\}',text): declared.update(n.strip().lstrip('\\') for n in names.split(','))
        definitions.update(re.findall(r'\\(?:newcommand|renewcommand|providecommand|DeclareRobustCommand)\*?\s*\{?\\([A-Za-z@]+)',text))
        definitions.update(re.findall(r'\\(?:gdef|edef|def)\s*\\([A-Za-z@]+)',text))
        definitions.update(re.findall(r'\\(?:NewDocumentCommand|RenewDocumentCommand)\s*\\([A-Za-z@]+)',text))
        definitions.update(re.findall(r'\\(?:newenvironment|NewDocumentEnvironment)\s*\{([^}]+)\}',text))
        for name in re.findall(r'\\begin\s*\{([^}]+)\}', text):
            environments.add(name)
        for name in re.findall(r'\\(?:input|include)\s*\{([^}]+)\}',text):
            if '\\' in name: continue
            candidate = path.parent/name
            if not candidate.suffix: candidate = candidate.with_suffix('.tex')
            if not candidate.exists(): candidate = ROOT/name
            if not candidate.suffix: candidate = candidate.with_suffix('.tex')
            if not candidate.is_file(): raise BuildError('M20_E_SOURCE_MISSING',f'Included source missing: {name}')
            visit(candidate)
    visit(source)
    unknown=(definitions | (environments-set(supported['environments'])))-declared
    if unknown and enforce: raise BuildError('M20_E_EPUB_UNMAPPED_CONTENT','Declare safe semantic expansion with \\m20epubsafe{...} or supply an adapter: '+', '.join(sorted(unknown)))
    return [{'path':str(p),'sha256':sha(p)} for p in sorted(seen)]

def build_epub(source, work, env):
    check_epub_content(source)
    name, driver = wrapper(source, work, 'epub')
    output = work/(name+'.epub')
    output.unlink(missing_ok=True)
    execute(['tex4ebook','-l','-f','epub3','-e',str(ROOT/'epub/m20.mk4'),'-c',str(ROOT/'epub/m20.cfg'),
             '-j',name,str(driver),'mathml,charset=utf-8'],work,env,work/'conversion.stdout')
    if not output.is_file():
        raise BuildError('M20_E_EPUB_MISSING','Converter returned without an EPUB')
    from epub_postprocess import adapt_epub
    try: adapt_epub(output,source.parent)
    except (ValueError,subprocess.SubprocessError) as exc: raise BuildError('M20_E_EPUB_SEMANTICS',str(exc)) from exc
    execute(['epubcheck',str(output)],work,env,work/'epubcheck.stdout')
    return output

def build(args):
    report = {'schema_version':1,'status':'building','target':args.target,'diagnostics':[], 'targets':{}}
    out = ROOT/'build/failed-build'
    try:
        out = workspace_path(args.out)
        out.mkdir(parents=True,exist_ok=True)
        source = Path(args.source).resolve()
        if not source.is_file(): raise BuildError('M20_E_SOURCE_MISSING',f'Manuscript missing: {args.source}')
        report['source'] = {'path':str(source),'sha256':sha(source)}
        report['sources'] = check_epub_content(source,enforce=False)
        report['profile_sha256'] = sha(ROOT/'profiles/m20.json')
        runtime = preflight(ROOT/'.runtime',prepare=args.prepare)
        report['engines'] = runtime['engines']
        report['converters'] = runtime['converters']
        env = runtime_environment(ROOT/'.runtime')
        # Recursive ROOT lookup includes other builds' .tmp/.xref files and
        # contaminates same-name jobs. Search manuscript and package roots only.
        env['TEXINPUTS'] = str(source.parent)+':'+str(ROOT)+':'+str(ROOT/'epub')+':'
        targets = ('pdf','epub') if args.target == 'all' else (args.target,)
        for target in targets:
            entry = report['targets'][target] = {'status':'building'}
            work = out/target; work.mkdir(exist_ok=True)
            try:
                if not runtime[target+'_ready']:
                    raise BuildError('M20_E_RUNTIME_MISSING',f'{target} runtime unavailable; run scripts/preflight.py --prepare')
                if target == 'pdf':
                    output, passes = build_pdf(source,work,env,args.max_runs)
                    entry['passes'] = passes
                else: output = build_epub(source,work,env)
                entry.update(status='passed',output=str(output),sha256=sha(output))
                if args.verify:
                    from verify import verify_output
                    entry['verification'] = verify_output(output,target)
                    if entry['verification']['errors']:
                        raise BuildError('M20_E_VERIFICATION',str(entry['verification']['errors']))
            except (RuntimeError,OSError,ValueError,subprocess.SubprocessError) as exc:
                entry['status'] = 'failed'
                report['diagnostics'].append({'code':getattr(exc,'code','M20_E_BUILD'),'target':target,'severity':'error','message':str(exc)})
        report['status'] = 'passed' if all(t['status']=='passed' for t in report['targets'].values()) else 'failed'
    except (RuntimeError,OSError,ValueError,subprocess.SubprocessError) as exc:
        report['status']='failed'
        report['diagnostics'].append({'code':getattr(exc,'code','M20_E_BUILD'),'severity':'error','message':str(exc)})
    finally:
        out.mkdir(parents=True,exist_ok=True)
        (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--target',choices=['pdf','epub','all'],default='all')
    p.add_argument('--source',default='examples/specimen.tex')
    p.add_argument('--out',default=str(ROOT/'build/specimen'))
    p.add_argument('--verify',action='store_true')
    p.add_argument('--prepare',action='store_true')
    p.add_argument('--max-runs',type=int,default=8)
    args=p.parse_args()
    report=build(args)
    summary={k:report[k] for k in ['status','targets','diagnostics']}
    summary['targets']={k:{a:b for a,b in v.items() if a!='verification'} |
        ({'verification':{a:b for a,b in v['verification'].items() if a not in ('text','raw_text','positions')}} if 'verification' in v else {}) for k,v in report['targets'].items()}
    print(json.dumps(summary,indent=2))
    return 0 if report['status']=='passed' else 1

if __name__=='__main__': sys.exit(main())
