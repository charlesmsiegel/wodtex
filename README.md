# wodtex

Native LaTeX authoring for M20 books, with LuaLaTeX PDF and reflowable EPUB 3
from the same editable manuscript. The implementation follows the approved
specification in [docs/design](docs/design).
The corrected native PDF installation implements generic class-selected commands and explicit M20 style overrides.
See the [Crossover Style Architecture guide](docs/design/Crossover-Style-Architecture.md) for implemented behavior and extension hooks.
WoD/MSC renderers and generic EPUB acceptance remain future work.

## Install and update (Windows / Git Bash)

From your checkout on `main`, first install and repeat updates use the same commands:

```sh
git pull --ff-only origin main
bash install.sh
```

For a new checkout:

```sh
git clone https://github.com/charlesmsiegel/wodtex.git
cd wodtex
bash install.sh
```

Python 3.9+, MiKTeX and LuaLaTeX must already be installed and on `PATH`.
The launcher tries `python`, `py -3`, then `python3`, checks the Python version,
and automatically registers a MiKTeX user tree when using Windows Python.
It forwards arguments safely and installs no Python/TeX dependencies or global
settings. MiKTeX 24.1 / LuaHBTeX 1.17.1 is the intended Windows target; actual
Windows execution has not been tested here. Linux native compilation is tested.

The private repository now includes the user-authorized, original eight-page
M20 reference PDF in `template-source/`, nine required unmodified font files
in `fonts/`, and prepared corrected-layout decorations in `assets/`. All
required original and public faces are present. Ordinary installation requires
no font/art flags, archive download, PDF extraction, PyMuPDF, or pinned Linux
runtime. See [input provenance](template-source/README.md) and
[font notices](fonts/NOTICES.txt). The repository owner asserts permission for
this private STV workflow; licensing has not been independently verified.
Unused InDesign/PSD material and private manuscripts are not included.

A fresh default installation verifies `bundle-manifest.json` hashes before
writing and points the local configuration to the checkout's `fonts/` and
`assets/` directories. Missing/changed inputs fail with the affected filename.
Keep the checkout in place. A moved checkout can be relinked explicitly with
`bash install.sh --configure` from its new location.

The corrected M20 PDF layout is installed by default. Create `book.tex` in a
separate book folder:

```tex
\documentclass{m20book}
\title{My Book}
\subtitle{My Subtitle}
\bookdescription{A supplement description}
\author{My Name}
\writtenby{My Name}
\begin{document}
\frontmatter
\maketitle
\makecredits
\tableofcontents
\mainmatter
\chapter{First Chapter}
Book prose.
\end{document}
```

```sh
cd "C:/Private/My Book"
kpsewhich m20book.cls
kpsewhich wodtex-local.tex
lualatex -interaction=nonstopmode -halt-on-error book.tex
lualatex -interaction=nonstopmode -halt-on-error book.tex
```

Native `\title{...}` supplies the default running title and PDF title. Explicit
`\m20setup{running-title={...}}` and `\hypersetup{pdftitle={...}}` remain overrides.
`profile=m20` is already the class default. A short TOC goes directly to its
required facing illustration and recto chapter opener; a longer TOC receives
only the single parity spacer when necessary. The first main chapter is Arabic
page 1.

Run LuaLaTeX again when references/contents request it. For an index, run
`makeindex book` and LuaLaTeX again. Enable MiKTeX's missing-package installation
or install requested public packages through MiKTeX Console. The two
`kpsewhich` commands should point to the user tree. An obsolete local
`m20book.cls` or `tex/` directory beside the manuscript can shadow installed
resources; back up edits and remove that obsolete copy.

### Generic author interface

The corrected installed class provides `booksetup`, `subtitle`, `bookdescription`, `writtenby`, `developedby`, `editedby`, `specialthanks` and `copyrightyear`.
Native `title` and `author` remain the primary book metadata.
`maketitle` and `makecredits` render the M20 interior title and credits without repeating metadata strings.
Generic `sidebar`, `sidebarwide`, `sidebarbreak`, `booktable`, `tablelead`, `statblock`, `statentry` and `artreserve` use the class default.
Their options match the corresponding existing M20 command or environment.
Nested generic tables and continuation/entry commands retain the enclosing element's style.
Explicit M20-prefixed commands retain M20 meaning, and metadata setters share the same stored values.

See [the runnable generic example](examples/generic-book.tex) and [the extension contract](docs/design/Crossover-Style-Architecture.md).
Copy `generic-book.tex` and its `art/scene.png` into one document folder and run LuaLaTeX twice there.
`art/scene.png` is a public geometric test fixture supplied alongside the example; replace it with your own scene image at that path.
A missing meaningful image remains an error rather than being silently dropped.
The full generic interface is supported for the corrected native PDF installation; WoD/MSC rendering and generic EPUB acceptance remain future work.

### Configuration and advanced installation

The corrected layout supports older `array` package installations paired with
newer `colortbl`, including the paragraph-cell API mismatch reported with
MiKTeX 24.1. Update wodtex using the commands above and compile again; no edits
to your table source are needed. Current `array` implementations keep their
own paragraph-cell implementation.

Updates preserve the existing local config **byte for byte**, including custom
font/art locations. Existing installations are not silently switched to bundled
paths. To explicitly switch an existing config to the checkout's bundled paths:

```sh
bash install.sh --configure
```

To use other prepared directories, supply both paths on a fresh installation,
or add `--configure` to explicitly replace an existing config:

```sh
bash install.sh --configure --font-dir "C:/Private/fonts" --asset-dir "C:/Private/assets"
```

The default Windows root is `%LOCALAPPDATA%/wodtex/texmf`, falling back to
`%USERPROFILE%/wodtex/texmf`. `--tree "C:/Private/wodtex-texmf"` selects another
root; supply the same `--tree` on updates. The installer prints actual paths.
The single config is `TREE/tex/latex/wodtex-local/wodtex-local.tex`. You may edit
it directly using forward slashes and trailing slashes, or use the explicit
configuration commands above. Per-document `\m20setup{font-path={.../},
asset-path={.../}}` still overrides its defaults. Generated config rejects
`{ } % # ~ ^ & $`, backslashes and newlines in paths; spaces and drive letters
are supported. Pass Windows paths such as `C:/Users/YourName/...` to Windows
Python in Git Bash.

Windows installation invokes the officially documented
[`initexmf --register-root=DIR`](https://docs.miktex.org/manual/initexmf.html)
and [`miktex fndb refresh`](https://docs.miktex.org/manual/miktex-fndb.html),
both in default user mode. Both executables are checked before installation.
Registration/refresh failures are reported; installed files remain, so correct
the MiKTeX issue and rerun `bash install.sh`. No `--admin` option is used.
Direct Python remains available: `python scripts/install.py --miktex`.

Only `TREE/tex/latex/wodtex` is replaced on update. Staging and a hash manifest
protect managed files: local edits, added/missing files, unowned directories and
symlinked resources are refused. Back up/reconcile such changes before
reinstalling; keep custom settings in the local config or manuscript. Other
tree contents are preserved. Every tracked `profiles/*.tex` resource is
installed under a unique `wodtex-profile-*.tex` name; updates collect future
resources without inventing new WoD/MSC designs.

`--layout corrected` is the default. To intentionally select the older renderer,
use `--layout base` on every install/update with explicit prepared font/art
paths on first install; the bundle supplies the corrected renderer's faces,
not all additional legacy Noto/Futura requirements. Correction checksums use
canonical LF text, accepting existing Windows CRLF checkouts while rejecting
other source edits. Installed-file hashes and bundled binary hashes are exact.
`.gitattributes` preserves LF source and exact font/PDF/image bytes.

The same committed rendering inputs produce the same normalized managed
TeX/Lua bytes and hash manifest on repeated installation. Configuration paths
depend on your machine; updates preserve them. PDF bytes are not promised to
be identical across TeX engines, package versions, fonts or build dates.

On TeX Live, the launcher omits MiKTeX registration and defaults to `~/texmf`.
On Unix MiKTeX, pass `--miktex`. A nondefault TeX Live root needs configuration
in your distribution (for a temporary check, `TEXMFHOME=/path/to/tree lualatex
book.tex`). Repository builds and their exact-hash opt-in patch workflow below
remain separate and unchanged. The source-only archive intentionally excludes
licensed bundle bytes; archive consumers supply explicit prepared paths.

Run `python -m unittest tests.test_install tests.test_install_shell -v` for
installation checks. Tests cover the launcher, config preservation, input
corruption/missing files, CRLF source, source archives, deterministic updates,
and external-folder compilation with synthetic fixtures and the real bundle.
The bundled smoke checks genuine Abbess/Goudy faces, original decorations,
tables, sidebar, art and resolved references before/after updating. Actual
Windows/MiKTeX execution and complete licensed-layout acceptance remain separate.

## Repository build workflow

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
the original `Document fonts` and `Links` directories beside it. Unbundled
licensed inputs, private manuscripts, caches and build outputs are excluded from Git.
Dependencies come from official sources with SHA256 pins and install locally;
original input files remain intact. The explicitly authorized rendering bundle
is tracked in this private repository; unrelated local inputs remain ignored.

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

## Original-template PDF corrections: activation and authoring

This opt-in release is a reviewed PDF checkpoint, not full framework acceptance.
The last aggregate snapshot, before the final pagination changes, recorded
55 passes and 13 failures: seven runtime/mixed-script gates and six legacy
policy assertions. The final local PDF verifier exits 1 for five reviewed
vertical output-box warnings on four pages; pixel review found no clipping
or horizontal overflow. The exact-hash text-span font audit contains only
Abbess and genuine Goudy regular, bold and italic. Full merged framework
acceptance and EPUB validation remain pending.


For the repository build workflow, the original-template layout is an explicit opt-in source patch. It is not
activated by selecting `profile=m20` alone. Preserve any uncommitted work, read
`contrib/original-m20-layout/changes.patch`, and use a disposable checkout of
the correction checkpoint you want to activate, keeping its complete package.
The manifest records the tested base; the helper checks the actual base-file
hashes, so untouched defaults at this checkpoint can be safely patched:

```sh
python3 contrib/original-m20-layout/apply.py --check
python3 contrib/original-m20-layout/apply.py --apply
```

`--check` validates exact base/override checksums without changing files.
`--apply` performs that check, saves replaced files under a new
`build/original-m20-layout-backup-*` directory, and installs the source
replacements. If base files changed, the helper refuses the operation; merge
the patch with those changes instead. Neither mode downloads licensed inputs.
The default source tree is unchanged until the patch is applied. If you instead
check out the older base commit, copy the complete correction package from
your chosen checkpoint into it before running the helper; otherwise you will
activate that older commit's package.

Prepare dependencies, licensed fonts and reference artwork locally:

```sh
python3 -m pip install -r requirements.txt
python3 scripts/preflight.py --prepare
python3 scripts/prepare_assets.py --template-zip /path/to/Mage_Templates.zip
python3 scripts/extract_template_art.py /path/to/M20-Template-Interior.pdf --out assets
python3 scripts/extract_spread_and_page_types.py /path/to/M20-Template-Interior.pdf --out assets
python3 scripts/extract_frontmatter_reference.py /path/to/M20-Template-Interior.pdf --out assets
python3 scripts/extract_sidebar_frame.py /path/to/M20-Template-Interior.pdf --out assets
```

Use `--idml "/path/to/M20 Template Interior.idml"` instead of `--template-zip`
when its original `Document fonts` and `Links` directories are alongside it.
`--assets-out DIR` selects another prepared asset directory; set the matching
`asset-path` in your document header. The PDF extraction scripts require the
original eight-page reference with SHA256
`4c876e07b17f4a85877213d557b3f0236004bf6baa48d0bef708a68745e93df5`.
They produce the authentic borders/panels, title background, art frames,
copyright/logo artwork and sidebar texture/shadow assets. The full-page
placeholder keeps the original pink background while its text uses Goudy.
The authorized reference PDF, required fonts and extracted decorations are now
tracked in this private repository; private manuscripts remain excluded.

Build a native manuscript from the repository root:

```sh
python3 scripts/build.py --target pdf --source path/to/book.tex --out build/book --verify
```

- `--target`: `pdf`, `epub` or `all`; default `all`
- `--source`: native LaTeX entry file; default `examples/specimen.tex`
- `--out`: output directory; default `build/specimen`
- `--verify`: run the target verifier after compilation; off unless supplied
- `--prepare`: prepare pinned runtime dependencies through preflight; this
  does not replace the separate licensed-template/art extraction steps
- `--max-runs`: maximum PDF convergence passes; default `8`

PDF output is under `OUT/pdf/`; EPUB output is under `OUT/epub/`, with a
`build-report.json` at the output root. Missing glyphs, undeclared font
substitutions, unresolved references, failed convergence and unreviewed
layout overflows make the build fail. A visually reviewed warning is not a
clean strict-verifier pass. The PDF-local `m20statblock`, `m20tablelead` and
interior-frontmatter helpers still need complete EPUB mappings; do not infer
EPUB readiness from a successful corrected PDF.

### Document header and front matter

Place setup and metadata after `\documentclass{m20book}` and before
`\begin{document}`. Blank credit fields are the default; names are never inferred.

```tex
\documentclass{m20book}
\m20setup{chapter-body-gap=6bp}
\newcommand{\booktitle}{My Book}
\title{\booktitle}
\author{Author}
\m20writtenby{[Writer Name]}
\m20developedby{[Developer Name]}
\m20editedby{[Editor Name]}
\m20specialthanks{[Special Thanks]}
% Optional fixed year; omit to use the TeX engine's build year automatically.
\m20copyrightyear{2026}

\begin{document}
\frontmatter
\mTwentyInteriorTitle{\booktitle}{Subtitle or author line}
\mTwentyInteriorCredits{\input{frontmatter/credits.tex}}
\tableofcontents
\mainmatter
\chapter{First Chapter}
Ordinary prose.
\appendix
\chapter{Appendix Title}
\end{document}
```

The five metadata commands each take one braced value:

- `\m20writtenby{TEXT}`: Written By value; default empty
- `\m20developedby{TEXT}`: Developed By value; default empty
- `\m20editedby{TEXT}`: Edited By value; default empty
- `\m20specialthanks{TEXT}`: Special Thanks body; default empty
- `\m20copyrightyear{YYYY}`: four-digit year in the White Wolf notice;
  default `\number\year`, evaluated at build time. This replaces only the date;
  it does not add a separate book copyright notice or change the holder/copy

`\mTwentyInteriorTitle{TITLE}{LOWER-LINE}` draws the original standalone purple
interior title page. `\mTwentyInteriorCredits{CONTENT}` draws Credits and its
role fields/thanks, retaining your supplied attribution content and original
logo/address/legal material. Do not duplicate the copyright block in CONTENT.
A source `\section{Credits and Attributions}` inside CONTENT retains its anchor
but does not create another heading or TOC entry. Contents immediately follows
Credits in this frontmatter sequence.

The title and full-page chapter-facing illustration leaves have no folio.
Contents uses the ordinary parity-correct spread border on every leaf;
chapter openers retain their dedicated panel/frame. Necessary parity spacers
use ordinary spread borders and footers instead of fully blank pages. Chapter
TOC entries use the profile heading face, with `Chapter One: Title` rather
than a detached numeral. Numbers one through twelve have word forms;
appendix A/B entries use `Appendix A: Title` and `Appendix B: Title`.
Use native `\chapter[Short title]{Long title}`, `\section`, `\subsection`,
`\subsubsection`, `\label`, `\ref`, `\pageref` and `\hyperref` normally.

### Setup options and typography

`\m20setup{KEY=VALUE,...}` accepts:

| Key | Default | Use |
| --- | --- | --- |
| `profile` | `m20` | Select measured profile configuration; M20 is the supported profile in this checkpoint |
| `running-title` | empty | Book title for even-page footer runners |
| `asset-path` | `assets/` | Asset directory, including trailing slash; build drivers normally supply an absolute project path |
| `font-path` | `fonts/` | Licensed font directory, including trailing slash |
| `math` | `legacy` | `legacy` or explicitly `unicode`; Unicode mode requires its runtime packages |
| `chapter-title-size` | `60bp` | Initial chapter-panel heading size |
| `chapter-title-leading` | `54bp` | Initial chapter heading line spacing |
| `chapter-body-gap` | `6bp` | Extra space below the chapter opener before body text |

`bp` is a PDF point, 72 per inch. Examples:

```tex
\m20setup{chapter-body-gap=9bp}
\m20setup{chapter-title-size=48bp,chapter-title-leading=45bp}
\m20setup{asset-path={/my/assets/},font-path={/my/fonts/}}
```

The heading face comes from the profile's `heading_regular` record and the
emitted `\mTwentyHeadingFontFile` in `profiles/m20.tex`; asset preparation
preserves that selection. M20 selects Abbess. Goudy Old Style is the shared
nonheading default: body, stat values/keys, sidebar prose, table cells/column
labels, lists, credit body, footers and nonchapter TOC entries use genuine
regular/bold/italic faces. No Futura or Noto role substitution is selected by
this correction. A missing heading glyph alone can use Goudy, preserving all
other heading letters in the configured face; supplied Abbess lacks straight
double quotes. There is no supplied genuine Goudy bolditalic face: a combined
request uses the genuine italic face and emits an explicit warning when that
combination is actually used. Ordinary bold and italic use their genuine faces.

Heading hyphenation is disabled. Moderate oversized chapter titles reduce to
48/45bp, then 42/39bp; exceptionally long titles may still need an explicit
header-size override. Body paragraph fitting and heading/first-line no-break
rules apply automatically, including across zero-height semantic anchors.

### Body flow and stable anchors

- `\m20bodybegin` starts the live two-column body; redundant calls do not nest it
- `\m20bodyend` ends that live region before a full-width/custom block
- `\m20newpage` ends the region, clears the page and resumes body flow
- `\m20anchor{ID}` emits a zero-height stable source/placement marker; IDs
  must begin with a letter and use letters, digits, `-`, `:`, `.`, `_`
- `\m20note{TEXT}` is a footnote in ordinary prose, and a locally numbered
  note in a sidebar/table owner
- `\m20script{TEXT}` explicitly selects the supplied script fallback for
  characters unavailable in the regular family; use it with `\foreignlanguage`
- `\m20epubsafe{COMMAND-NAMES}` declares author-defined safe expansions to
  EPUB source validation; it does not implement a missing semantic adapter

Use unique IDs and native LaTeX paragraph breaks. Do not use blank lines or
manual breaks as a substitute for a chapter-gap setting or a heading keep rule.

### Sidebars and explicit sidebar breaks

```tex
\begin{m20sidebar}[id=field-note,place=flow]{Field Note}
One-column sidebar prose with \textbf{genuine bold} and \emph{italic}.
\end{m20sidebar}

\begin{m20sidebarwide}[id=wide-note,columns=2,place=next-page]{A Wide Note}
Two internal columns. Long content continues with a repeated heading.
\m20sidebarbreak[page]
An explicit author-requested continuation.
\end{m20sidebarwide}
```

Both environments take optional keys and one required braced title:

- `id`: unique stable ID; default `sidebar-N`
- `place`: `flow` (default), `here` or `next-page`. Flow can advance to a
  region that fits; here requires the first segment at that anchor and errors
  if unavailable; next-page begins on a fresh physical page
- `columns`: default `1`; `m20sidebar` only accepts `1`, while
  `m20sidebarwide` supports `1` or `2`
- `breakable`: default `true`; `false` makes an atomic block and diagnoses a
  block too tall for one region
- `balance`: accepted with default `true`; the correction's ordered,
  natural-height frame stream does not expose an alternative balancing policy

`\m20sidebarbreak` defaults to `[page]`; `[column]` requests a local column
break. It is only valid inside a sidebar. Short flow sidebars keep together
when they fit a full region; long sidebars paginate with protected paragraph
ends. Text and contained table bands on one physical page share a continuous
frame. The original double-gradient rules, square corners and source shadow
are painted without stretching the rune texture. Authored title emphasis
keeps the profile heading face instead of falling back to a body family.

### Tables, repeated heads and title/lead association

```tex
\begin{m20table}[id=example-table,head-rows=1,width=container]{ll}
Name & Description \\
First & A wrapped cell. \\
Second & Another value. \\
\end{m20table}

\begin{m20tablelead}
\subsection{Table Title}
Existing introductory prose that must travel with this table.
\begin{m20table}[id=associated-table,head-rows=1]{ll}
Name & Value \\
First & One \\
\end{m20table}
\end{m20tablelead}
```

`m20table` takes optional keys followed by its required native column
specification. Use `&` between cells and `\\` after rows. Keys:

- `id`: unique ID; default `table-N`
- `width`: `container` (default), `column` or an explicit dimension
- `scale`: default `1`; must be greater than `0` and at most `1`
- `align`: `left`, `center` (default) or `right` within the container
- `head-rows`: nonnegative repeated-header row count; default `0`
- `epub`: `table` or `records` for the EPUB adapter; it does not alter PDF rows

Column specifications use native `l`, `c`, `r` or `p` entries. Long tables use
owner pagination and repeated headers. Compact full-width tables float at page
edges; sidebar tables stay inside their owner frame. Native `\footnote` or
`\m20note` inside a table creates a local table note. Tables cannot contain a
nested breakable `m20table`; use an atomic native `tabular` inside a cell.

`m20tablelead` has no arguments. Wrap the existing title, lead and one compact
table so all their tokens/anchors are boxed once and float together. Use it
outside sidebars and keep the complete group below one-page capacity; it
errors if too tall. Leave multipage tables in their native owner stream.

### Stat blocks and lists

```tex
\begin{m20statblock}
\mTwentyStatEntry{\textbf{Ruin Type}: Feral Realm | \textbf{Structural Integrity}: 4}
\mTwentyStatEntry{\textbf{Primary Hazards}: Existing descriptive text.}
\end{m20statblock}
```

`m20statblock` has no arguments. `\mTwentyStatEntry{TEXT}` takes one braced
entry; literal `|` separators display as separate keyed lines without
rewriting your source content. Both keys and values use Goudy at the same
nominal 10bp size/baseline; weight provides emphasis. Existing `itemize`,
`enumerate` and `description` use compact hanging Goudy with the correction's
alternating bands. Standard native `\item` syntax and counters remain intact.

### Art reservations and manual cadence overrides

```tex
\m20artreserve[kind=horizontal,position=top,role=decorative]{art-one}
\m20artreserve[kind=horizontal,position=bottom,role=decorative]{art-two}
\m20artreserve[kind=vertical,position=outer,role=decorative]{art-three}
\m20artreserve[kind=horizontal,image={art/scene.png},alt={A concise image description},
 caption={Scene caption},credit={Artist credit}]{scene-one}
```

`\m20artreserve[KEYS]{ID}` accepts:

- `kind`: `horizontal` (default) or `vertical`
- `place`: `flow` (default), `here` or `next-page`
- `position`: `top`/`bottom` for horizontal, `inner`/`outer` for vertical;
  omitted position defaults to `top` or `outer` respectively
- `image`: image path; default empty, giving a labeled placeholder
- `role`: `decorative` by default for an empty placeholder; an actual image
  defaults to `meaningful`
- `alt`: required for meaningful images
- `caption`, `credit`: optional image-caption/credit text; default empty

Meaningful art requires an existing image and nonempty alternative text.
Art reservations cannot be nested in sidebars. Horizontal reservations are
half-page native edge floats, never a second stacked top float or an arbitrary
middle-page box. `here` retains edge-float behavior rather than promising an
inline rectangle in a live prose column; `next-page` first starts a new page.
Vertical reservations use one full-height live text-area column on a fresh
page, at the outside edge by default, with narrative in the other column.
The art frame dimensions/aspect and authentic border drawing stay fixed.

To override an authored image schedule, move/add/remove these explicit calls
at sensible paragraph/section seams, or change their valid position/place
keys. Do not insert one between a heading/stat block and its first prose
paragraph. The corrected book's approximate target is one image every two to
three spreads (about four to six pages), counting full-page chapter-facing
art. This is an authored schedule, not automatic image invention or a rigid
one-image-per-spread rule; both facing pages may contain artwork when their
text/table composition benefits. Check actual rendered art-page gaps after
changing prose, and avoid isolated art-only ending pages.
