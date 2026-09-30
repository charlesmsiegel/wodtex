# wodtex

Reusable native-LaTeX authoring framework for World of Darkness books, with separate PDF and reflowable EPUB output adapters and extensible visual profiles.

## Implementation status

This development branch is an in-progress checkpoint, not a finished release. The approved M20 specification and all eight implementation tasks are in `docs/design/`. Runtime and layout code, tests, dependency pins, and measured profile work are being committed as they are implemented.

The first real LuaLaTeX font/runtime smoke PDF has been compiled and visually inspected. It embeds genuine supplied Abbess, Goudy Old Style, and Futura faces with explicitly declared genuine Noto fallbacks. The measured 98% vertical body-glyph scale preserves horizontal width. The two-column/sidebar composition proof and actual EPUB conversion are still in progress. Full acceptance, complete installation/usage documentation, and the full Graveyards of Hope book outputs are pending.

## Architecture

- One editable native-LaTeX manuscript with standard book commands, references, mathematics, and indexing
- Semantic core separated from PDF placement/decorative rendering and EPUB semantic conversion
- M20 as the first measured visual profile; other profiles can be added behind the same semantic interface
- All three sidebar layouts, mandatory placement, breakable tables, paired chapter versos, meaningful-art semantics, and reflowable EPUB conservation are required acceptance gates

## Licensed inputs

Original InDesign templates, proprietary fonts/art, and private book manuscripts are not redistributed in this repository. They remain private user-supplied inputs in ignored directories. The importer/preparation commands and measured profile manifest are being implemented so licensed users can reproduce the build with their own files.

## Intended build interface

Once implementation is complete:

`python3 scripts/build.py --target all --source examples/specimen.tex --out build/specimen --verify`

The current checkpoint may not yet support this complete command. Do not treat partial tests or the runtime smoke as proof that layout fidelity, EPUB readability, or full-book content preservation is finished.
