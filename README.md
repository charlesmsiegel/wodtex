# wodtex

Native LaTeX authoring for M20 books, with LuaLaTeX PDF and reflowable EPUB 3
from the same editable manuscript. The implementation follows the approved
specification in [docs/design](docs/design).

## Build a book

Use Python 3.12+, a TeX Live/LuaLaTeX installation, Java 17+, Node.js 18+,
makeindex and Poppler. The tested environment is Linux x86-64; preparation
supplies a pinned dvisvgm binary there. Other platforms need their own dvisvgm
and compatible TeX paths.

```sh
python3 -m pip install -r requirements.txt
python3 scripts/preflight.py --prepare
python3 scripts/prepare_assets.py --template-zip /path/to/Mage_Templates.zip
python3 scripts/build.py --target all --source examples/book.tex --out build/book --verify
```

Instead of the ZIP, pass `--idml "/path/to/M20 Template Interior.idml"` with
the original `Document fonts` and `Links` directories beside it. Licensed
fonts/art, private manuscripts, caches and build outputs are excluded from Git.
Dependencies come from official sources with SHA256 pins and install locally;
original input files remain intact.

Edit [examples/book.tex](examples/book.tex). Use `--target pdf` or `--target epub`
for one format. Outputs and `build-report.json` are under the selected `build`
directory. Failed builds return nonzero with target-specific diagnostics.

## Implemented

- Native two-column PDF body and spanning headings; all three sidebar layouts
  with long continuations, mandatory placement and atomic-content diagnostics.
- Breakable native tables, repeated headings, nested tabular cells, local notes,
  fixed art reservations, fresh chapter versos, contents, references and index.
- Semantic EPUB asides, tables or labeled records, meaningful art with metadata,
  notes/backlinks, native MathML with vector SVG alternatives and live navigation.
- Pinned preparation, bounded build convergence, output verification, stress
  fixtures, and a deterministic source archive with a fresh-unpack build test.

The multilingual auto-selection regression is deferred at the user's request.
Use `\foreignlanguage{arabic}{\m20script{مرحبا}}` and the equivalent recipe for
other supported scripts. The regression remains an expected-failure test;
missing glyphs still fail a build. Exact InDesign decoration calibration and
physical e-reader validation remain open and are recorded in
[Validation.txt](docs/Validation.txt).

## Check and package

```sh
python3 scripts/build.py --target all --source examples/specimen.tex --out build/specimen --verify
python3 -m unittest discover -s tests -t . -v
python3 scripts/package.py --out build/packages/wodtex-m20.zip
```

The archive contains source, examples, tests, dependency pins and documentation;
supply your licensed inputs after unpacking. Set `WODTEX_TEMPLATE_ZIP` for the
fresh-setup integration test when the ZIP is outside the default local location.

See [setup](docs/README.txt), [command recipes](docs/Command-Reference.txt),
[supported content](docs/Supported-Content.txt), and [validation limits](docs/Validation.txt).
