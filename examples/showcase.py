#!/usr/bin/env python3
"""Render one shared manuscript with every registered class; outputs stay in build/.

Run: python examples/showcase.py [--latex C:/path/to/lualatex.exe]
Requires the prepared X20 inputs documented in docs/X20-Class-Reference.md.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from install import install
from prepare_profile import verify_resources
from profile_registry import load_profiles

MANUSCRIPT = r"""\documentclass{@CLASS@}
\title{Lantern House}
\subtitle{One manuscript, seventeen book styles}
\author{Example Author}
\writtenby{Example Author}
\editedby{Example Editor}
\specialthanks{The night shift}
\copyrightyear{2026}
\makeindex
\begin{document}
\frontmatter
\maketitle
\makecredits
\tableofcontents
\mainmatter
\chapter{Arrival}
\label{arrival}
\section{After Midnight}
The last tram stops beside Lantern House\index{Lantern House}. Its windows
are dark except for a single lamp above the door. Rain gathers on the steps,
and the brass bell rings before anyone touches it.

The visitor carries a \textbf{sealed letter}, an \emph{unanswered question},
and a \textbf{\emph{very inconvenient promise}}. Ordinary paragraphs, genuine
font faces, and the two body columns all follow the selected book class.
\begin{itemize}
\item Follow the light into the reception hall.
\item Ask who signed the letter.
\item Remember the sound of the bell.
\end{itemize}
\begin{sidebar}[id=field-note]{Field Notes}
The clock has stopped, but its shadow still moves. This narrow sidebar uses
the same manuscript in every output profile.
\end{sidebar}
\begin{sidebarwide}[id=rumours]{Rumours}
Three guests arrived yesterday. Only two names appear in the ledger.
The missing guest left a key beneath the reception desk.
\end{sidebarwide}
\begin{tablelead}The reception ledger records the evening's visitors.\end{tablelead}
\begin{booktable}[id=ledger,head-rows=1]{ll}
Visitor & Arrival \\
The courier & Midnight \\
The caretaker & Before dawn \\
The stranger & Unrecorded \\
\end{booktable}
\begin{statblock}
\statentry{Caretaker: patient, observant, and unwilling to leave.}
\statentry{Clues: a brass key, a wet coat, and a broken clock.}
\end{statblock}
\artreserve[image={../scene.png},alt={A geometric scene},caption={The light in the window},credit={Example illustration}]{window}
\chapter{Departure}
The bell from Chapter~\ref{arrival} rings again. The visitor leaves by a
different door, with the letter still unopened. The ledger now contains a
fourth name.
\backmatter
\printindex
\end{document}
"""


def make_comparison(output, results):
    """Collect a body page per class, with profile names in PDF bookmarks."""
    import fitz
    with fitz.open() as comparison:
        bookmarks = []
        for style, result in results.items():
            with fitz.open(output / (style + '.pdf')) as document:
                page = next(i for i, p in enumerate(document)
                            if 'sealedletter' in ''.join(p.get_text().casefold().split()))
                comparison.insert_pdf(document, from_page=page, to_page=page)
            bookmarks.append([1, style + ' (' + result['class'] + ')', len(comparison)])
        comparison.set_toc(bookmarks)
        comparison.save(output / 'showcase-comparison.pdf')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--latex', default=os.environ.get('WODTEX_LUALATEX') or shutil.which('lualatex'))
    args = parser.parse_args()
    command = args.latex
    if not command and os.name == 'nt':
        candidate = Path(os.environ.get('LOCALAPPDATA', '')) / 'Programs/MiKTeX/miktex/bin/x64/lualatex.exe'
        if candidate.is_file():
            command = str(candidate)
    if not command:
        parser.error('Put LuaLaTeX on PATH or supply --latex')
    output = ROOT / 'build/showcase'
    output.mkdir(parents=True, exist_ok=True)
    profiles = load_profiles(ROOT)
    for style in profiles:
        if style != 'm20':
            verify_resources(style, ROOT / 'inputs/profiles')
    _, target, config = install(output / 'texmf', 'corrected', profile_root=ROOT / 'inputs/profiles')
    shutil.copy2(ROOT / 'examples/art/scene.png', output / 'scene.png')
    env = dict(os.environ)
    env['PATH'] = str(Path(command).parent) + os.pathsep + env.get('PATH', '')
    env['TEXINPUTS'] = os.pathsep.join((str(target), str(config.parent), ''))
    native_options = ['--disable-installer'] if 'miktex' in command.lower() else []
    import fitz
    results = {}
    for style, profile in profiles.items():
        work = output / style
        work.mkdir(exist_ok=True)
        (work / 'showcase.tex').write_text(MANUSCRIPT.replace('@CLASS@', profile['class']), encoding='utf-8')
        previous = None
        for number in range(1, 7):
            run = subprocess.run([command, *native_options, '-no-shell-escape', '-interaction=nonstopmode',
                                  '-halt-on-error', 'showcase.tex'], cwd=work, env=env, capture_output=True, timeout=180)
            (work / ('pass-' + str(number) + '.stdout')).write_bytes(run.stdout + run.stderr)
            if run.returncode:
                raise RuntimeError(style + ': see ' + str(work / ('pass-' + str(number) + '.stdout')))
            index = subprocess.run([shutil.which('makeindex', path=env['PATH']), 'showcase.idx'], cwd=work, env=env, capture_output=True, timeout=60)
            if index.returncode:
                raise RuntimeError(style + ': makeindex failed')
            state = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in work.iterdir() if p.suffix in ('.aux', '.toc', '.out', '.ind')}
            if state == previous:
                break
            previous = state
        else:
            raise RuntimeError(style + ': references did not converge')
        log = (work / 'showcase.log').read_text(errors='replace')
        if 'Missing character:' in log or 'undefined references' in log:
            raise RuntimeError(style + ': missing glyph or unresolved reference')
        pdf = output / (style + '.pdf')
        shutil.copy2(work / 'showcase.pdf', pdf)
        with fitz.open(pdf) as document:
            text = ' '.join(' '.join(page.get_text().split()) for page in document)
            compact_text = ''.join(text.casefold().split())
            for phrase in ('sealed letter', 'Field Notes', 'Rumours', 'The courier', 'Caretaker:', 'The light in the window', 'fourth name', 'Index'):
                if ''.join(phrase.casefold().split()) not in compact_text:
                    raise RuntimeError(style + ': missing example content: ' + phrase)
            results[style] = {'class': profile['class'], 'pages': len(document), 'passes': number, 'pdf': str(pdf)}
        print(style + ': ' + str(results[style]['pages']) + ' pages', flush=True)
    (output / 'report.json').write_text(json.dumps(results, indent=2) + '\n')
    make_comparison(output, results)
    print('Rendered ' + str(len(results)) + ' profiles in ' + str(output))


if __name__ == '__main__':
    main()
