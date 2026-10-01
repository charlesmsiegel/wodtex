WodTeX M20: setup and normal use

Prerequisites
Python 3.12+, LuaLaTeX/TeX Live 2023 or later, Java 17+, Node.js 18+,
makeindex, and Poppler (pdffonts). Install the Python packages with:
  python3 -m pip install -r requirements.txt
The system TeX installation supplies LaTeX, Babel, geometry, graphics, amsmath,
multicol, xcolor, TikZ, hyperref, and the standard math fonts. The preparation
script supplies the pinned missing runtime packages, converters, fallbacks,
and local LuaLaTeX/DVI formats. It never installs system files or enables shell
escape. Network access to the official sources in runtime.lock.json is needed
for initial preparation. Later preparation can use the cached downloads.
The tested runtime is Linux x86-64. A pinned dvisvgm binary is prepared there;
other platforms require an installed dvisvgm and compatible TeX search paths.

Licensed inputs
Supply your original M20 template ZIP or the original IDML with its sibling
Document fonts and Links directories. Do not copy original proprietary fonts
or decorative images into Git. Preparation checks source/resource hashes and
records font embedding/license metadata; it does not grant redistribution
rights. The example diagram is an original repository fixture.

Prepare and build, from the repository root
  python3 scripts/preflight.py --prepare
  python3 scripts/prepare_assets.py --template-zip /path/to/Mage_Templates.zip
Or instead of --template-zip:
  python3 scripts/prepare_assets.py --idml "/path/to/M20 Template Interior.idml"
  python3 scripts/build.py --target all --source examples/book.tex --out build/book --verify
  python3 scripts/build.py --target all --source examples/specimen.tex --out build/specimen --verify

Edit examples/book.tex or a copy. Keep ordinary native LaTeX book structure,
lists, mathematics, labels, references, footnotes, contents and index commands.
The driver chooses output through a wrapper; the manuscript does not change.
Use --target pdf or --target epub for a single format. Use --prepare on the
build command to prepare the pinned runtime first; assets are a separate step.
Writable caches and build output must be under .runtime or build in this tree.

Results and failures
Outputs are in <out>/pdf/<name>.pdf and <out>/epub/<name>.epub. Every invocation
writes <out>/build-report.json, exits nonzero on failed targets, and records
engine versions, hashes, diagnostics, and independent checks. --verify checks
actual PDF bounds/embedding/overflow and EPUB resources, links and semantics.
The specimen also has tests for content inventory and mandatory placement.
Detailed conversion/compiler logs remain in the target output directory.

Regression tests and source package
  python3 -m unittest discover -s tests -t . -v
  python3 scripts/package.py --out build/packages/wodtex-m20.zip
The archive contains editable source, docs, tests, pins and the original demo
diagram, plus file hashes. It excludes fonts/artwork from the original template,
private manuscripts, downloaded dependencies and compiled outputs. Supply your
licensed template after unpacking. The fresh-unpack integration test reuses
authorized local inputs and pinned download caches; neither is in the archive.

Read Command-Reference.txt for recipes, Supported-Content.txt for scope, and
Validation.txt for verified behavior and the remaining fidelity/reader limits.
