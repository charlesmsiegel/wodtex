"""Native PDF builds for measured X20 classes, independent of M20's EPUB runtime."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
try:
    from profile_registry import ROOT, document_class, profile_for_class
    from prepare_profile import verify_resources
except ImportError:
    from scripts.profile_registry import ROOT, document_class, profile_for_class
    from scripts.prepare_profile import verify_resources


def latex_command():
    command = os.environ.get('WODTEX_LUALATEX') or shutil.which('lualatex')
    if not command:
        raise ValueError('WODTEX_E_RUNTIME_MISSING: put LuaLaTeX on PATH or set WODTEX_LUALATEX')
    return command


def build_profile(args, root=ROOT):
    out = Path(args.out).resolve()
    if not out.is_relative_to(root / 'build'):
        raise ValueError('Profile build outputs must remain under workspace build/')
    out.mkdir(parents=True, exist_ok=True)
    report = {'schema_version': 1, 'status': 'failed', 'targets': {}, 'diagnostics': []}
    try:
        source = Path(args.source).resolve()
        profile = profile_for_class(root, document_class(source.read_text(encoding='utf-8')))
        report['style_id'] = profile['style_id']
        targets = ('pdf', 'epub') if args.target == 'all' else (args.target,)
        if any(target not in profile['outputs'] for target in targets):
            raise ValueError('WODTEX_E_OUTPUT_UNSUPPORTED: ' + profile['style_id'] + ' supports ' + ', '.join(profile['outputs']))
        resources = Path(os.environ.get('WODTEX_PROFILE_ROOT', root / 'inputs/profiles')).resolve()
        manifest = verify_resources(profile['style_id'], resources)
        report['resources'] = manifest
        work = out / 'pdf'
        work.mkdir(exist_ok=True)
        resource_path = resources.as_posix()
        if any(c in resource_path for c in '{}%#~^&$\n\r'):
            raise ValueError('WODTEX_E_RESOURCE_PATH: unsupported TeX path characters')
        driver = work / 'driver.tex'
        driver.write_text('\\PassOptionsToClass{output=pdf}{' + profile['class'] + '}\n'
                          '\\def\\wodtexResourceRoot{' + resource_path + '/}\n'
                          '\\input{\\detokenize{' + source.as_posix() + '}}\n', encoding='utf-8')
        command = latex_command()
        env = dict(os.environ)
        env['PATH'] = str(Path(command).parent) + os.pathsep + env.get('PATH', '')
        env['TEXINPUTS'] = os.pathsep.join((str(source.parent), str(root), ''))
        previous = None
        for number in range(1, args.max_runs + 1):
            native_options = ['--disable-installer'] if os.name == 'nt' and 'miktex' in command.lower() else []
            result = subprocess.run([command, *native_options, '-no-shell-escape', '-interaction=nonstopmode', '-halt-on-error',
                                     '-jobname=' + source.stem, '-output-directory=' + str(work), str(driver)],
                                    cwd=source.parent, env=env, capture_output=True, timeout=240)
            (work / ('pass-' + str(number) + '.stdout')).write_bytes(result.stdout + result.stderr)
            if result.returncode:
                raise ValueError('WODTEX_E_COMPILE: see ' + str(work / ('pass-' + str(number) + '.stdout')))
            index = work / (source.stem + '.idx')
            if index.exists() and index.stat().st_size:
                makeindex = shutil.which('makeindex', path=env['PATH'])
                if not makeindex:
                    raise ValueError('WODTEX_E_INDEX_RUNTIME: makeindex required')
                indexed = subprocess.run([makeindex, index.name], cwd=work, env=env, capture_output=True, timeout=60)
                if indexed.returncode:
                    raise ValueError('WODTEX_E_INDEX: ' + indexed.stderr.decode(errors='replace'))
            state = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in work.iterdir()
                     if p.suffix in ('.aux', '.toc', '.out', '.ind')}
            if state == previous:
                break
            previous = state
        else:
            raise ValueError('WODTEX_E_NONCONVERGING')
        log = (work / (source.stem + '.log')).read_text(errors='replace')
        if re.search('Missing character:|undefined references|Font shape .* undefined|Some font shapes were not available', log):
            raise ValueError('WODTEX_E_PDF_CONTENT: missing glyph, font face or reference; inspect log')
        pdf = work / (source.stem + '.pdf')
        entry = {'status': 'passed', 'output': str(pdf), 'passes': number,
                 'sha256': hashlib.sha256(pdf.read_bytes()).hexdigest()}
        if args.verify:
            import fitz
            with fitz.open(pdf) as doc:
                expected = profile['page']
                if any(abs(p.rect.width - expected[0]) > .2 or abs(p.rect.height - expected[1]) > .2 for p in doc):
                    raise ValueError('WODTEX_E_PAGE_DIMENSIONS')
                entry['verification'] = {'pages': len(doc), 'page_dimensions': expected, 'missing_glyphs': False}
        report['targets']['pdf'] = entry
        report['status'] = 'passed'
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        report['diagnostics'].append({'code': str(error).split(':')[0], 'message': str(error)})
    (out / 'build-report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    return report
