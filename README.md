# wodtex

Native LaTeX authoring for M20 books, with LuaLaTeX PDF and reflowable EPUB 3
from the same editable manuscript. The implementation follows the approved
specification in [docs/design](docs/design).

## Per-user native LuaLaTeX installation (Windows / Git Bash)

For an already configured installation, update from your checkout on `main`:

```sh
git pull --ff-only origin main
bash install.sh
```

`install.sh` is a thin launcher for `scripts/install.py`. It finds Python 3.9+
using `python`, `py -3`, then `python3`; native Windows Python automatically
selects MiKTeX user-root registration and FNDB refresh. It resolves the checkout
relative to the script, quotes paths and forwards all arguments unchanged. It
installs no Python/TeX dependencies and makes no administrator changes. On
Unix it leaves TeX distribution selection to you; pass `--miktex` for MiKTeX.
First installation currently requires the private font/art paths described
below; fonts/PDFs and prepared decorations are not yet bundled in this checkout.

The same committed source inputs produce the same normalized managed TeX/Lua
payload bytes and hash manifest on repeated installs. Private configuration is
preserved; its absolute paths depend on your machine. PDF bytes are not promised
to be reproducible across TeX engines, package versions, fonts or build dates.

This workflow installs the reviewed **corrected M20 PDF layout** by default.
Use `\documentclass{m20book}` and ordinary `lualatex book.tex` from your book's
folder afterward. It does not apply patches to your checkout, copy licensed
inputs, or require the pinned Linux builder. Python 3.9+ and MiKTeX with
LuaLaTeX and its required packages must already be installed and on `PATH`.
MiKTeX 24.1 / LuaHBTeX 1.17.1 is the intended Windows target; Windows execution
has not been tested here. Linux portability is tested separately below.

Clone once, or update an existing clean checkout on `main`:

```sh
git clone https://github.com/charlesmsiegel/wodtex.git
cd wodtex
git switch main
git pull --ff-only origin main
python --version
lualatex --version
initexmf --version
miktex --version
```

Use `python` in Git Bash with Windows Python; `py -3` can replace it if needed.
Supply Windows paths such as `C:/Users/YourName/...` to Python, especially
inside quotes. Keep licensed inputs in a permanent private directory outside
the checkout. Reuse your already prepared `fonts` and `assets` directories if
available. Otherwise, prepare them once:

1. Copy your licensed `GOUDOS.TTF`, `GOUDOSB_0.TTF`, `GOUDOSI_0.TTF`, and
   `abbess-regular.ttf` from the template's `Document fonts` into your private
   fonts directory. Also supply the public `DejaVuSans.ttf`,
   `DejaVuSans-Bold.ttf`, `DejaVuSans-Oblique.ttf`,
   `DejaVuSans-BoldOblique.ttf`, and `DejaVuSansMono.ttf` there for script/mono
   roles (available from the [DejaVu project](https://dejavu-fonts.github.io/)).
   Preserve these exact filenames. These requirements describe the corrected
   M20 layout; the legacy base renderer has additional font requirements.
2. Extract private decorations using the original eight-page M20 reference
   PDF. These cross-platform Python extractors need PyMuPDF, not the pinned
   build runtime. They check the original PDF SHA256 listed below. Replace
   the example paths, and run all four commands:

```sh
python -m pip install PyMuPDF==1.26.6
python contrib/original-m20-layout/overrides/scripts/extract_template_art.py "C:/Private/M20-Template-Interior.pdf" --out "C:/Private/wodtex/assets"
python contrib/original-m20-layout/overrides/scripts/extract_spread_and_page_types.py "C:/Private/M20-Template-Interior.pdf" --out "C:/Private/wodtex/assets"
python contrib/original-m20-layout/overrides/scripts/extract_frontmatter_reference.py "C:/Private/M20-Template-Interior.pdf" --out "C:/Private/wodtex/assets"
python contrib/original-m20-layout/overrides/scripts/extract_sidebar_frame.py "C:/Private/M20-Template-Interior.pdf" --out "C:/Private/wodtex/assets"
```

Install and register the user tree (no administrator shell):

```sh
bash install.sh --font-dir "C:/Private/wodtex/fonts" --asset-dir "C:/Private/wodtex/assets"
```

On Windows the default tree is `%LOCALAPPDATA%/wodtex/texmf` (falling back to
`%USERPROFILE%/wodtex/texmf`). The installer prints the actual paths. `--tree
"C:/Private/wodtex-texmf"` selects another root; supply the same `--tree` on
updates. The installer runs the officially documented
[`initexmf --register-root=DIR`](https://docs.miktex.org/manual/initexmf.html)
and [`miktex fndb refresh`](https://docs.miktex.org/manual/miktex-fndb.html),
both in default user mode. It checks both executables before writing. If
registration/refresh fails, it reports failure; installed files remain, so
correct the MiKTeX error and repeat the update command below. No `--admin`
option, global root replacement, or shell environment search-path hack is used.

Create `book.tex` in a separate book folder:

```tex
\documentclass{m20book}
\m20setup{running-title={My Book}}
\begin{document}
\chapter{Beginning}\label{ch:beginning}
Your text here. See page \pageref{ch:beginning}.
\end{document}
```

```sh
cd "C:/Private/My Book"
kpsewhich m20book.cls
kpsewhich wodtex-local.tex
lualatex -interaction=nonstopmode -halt-on-error book.tex
lualatex -interaction=nonstopmode -halt-on-error book.tex
```

Run LuaLaTeX again when references/contents request it; use `makeindex book`
then LuaLaTeX again for an index. Enable MiKTeX's missing-package installation
or install requested public packages through MiKTeX Console. The two
`kpsewhich` commands should point to the new tree. An old `m20book.cls` or
`tex/` directory alongside the manuscript can shadow installed resources;
remove that obsolete local copy after backing up edits.

### Repeatable updates and private configuration

From your wodtex checkout, on `main`:

```sh
git pull --ff-only origin main
bash install.sh
```

No font/art flags are needed on updates. The single private config is
`TREE/tex/latex/wodtex-local/wodtex-local.tex`; it defines absolute font/art
paths with trailing slashes, and updates preserve its bytes. You may edit
that file directly (use forward slashes), or explicitly change both paths:

```sh
python scripts/install.py --miktex --configure --font-dir "C:/NewPrivate/fonts" --asset-dir "C:/NewPrivate/assets"
```

Per-document `\m20setup{font-path={.../},asset-path={.../}}` still overrides
these defaults. Path characters `{ } % # ~ ^ & $`, backslashes and newlines
are rejected when generating config; ordinary spaces and drive letters work.

Only the dedicated managed directory `TREE/tex/latex/wodtex` is replaced.
A staged replacement and hash manifest prevent accidental loss of local
managed-file edits: changed, added, missing, unowned, or symlinked resources
are refused. Back up/reconcile such edits before reinstalling; keep private
changes in the local config or manuscript. Existing unrelated tree contents
are preserved. The tree stores public class/packages/Lua and every tracked
`profiles/*.tex` under unique `wodtex-profile-*.tex` names. Updates collect new
profile resources automatically; they do not author new WoD/MSC designs or
promise support for a profile that is not present in the checkout.

`--layout corrected` is the default and remains so on updates; use
`--layout base` on **every** install/update to intentionally select the earlier
base renderer. Correction payload hashes are verified before installation against canonical LF
text. Existing Windows CRLF checkouts are accepted by converting only CRLF
pairs to LF; other source changes still fail verification. `.gitattributes`
keeps new source checkouts in LF form. Installed-file hashes remain byte-exact.
Repository-relative resource names are normalized only in installed copies;
the source build and exact-hash opt-in patch workflow below remain intact.
Source archives include the correction package needed by this installer.

For TeX Live, omit `--miktex`; the default root is `~/texmf`, which TeX Live
searches as `TEXMFHOME`. An explicit nondefault root needs registration in your
TeX distribution (for a temporary Linux check, `TEXMFHOME=/path/to/tree
lualatex book.tex`). The installer itself has no third-party Python dependency.

Native installation tests: `python -m unittest tests.test_install tests.test_install_shell -v`.
The Linux smoke test uses public DejaVu substitute faces and synthetic art,
compiles outside the repository twice before/after an update and with the base
renderer, and checks table/sidebar/art text, references, private paths and
installed profile loading. It requires LuaLaTeX, Poppler, fontTools and the
public DejaVu fonts. It proves resource portability, not authentic licensed
M20 appearance or an actual Windows/MiKTeX installation.

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
No original PDFs, fonts, images or private manuscript are shipped in Git.

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
\m20setup{profile=m20,running-title={My Book},chapter-body-gap=6bp}
\title{My Book}
\author{Author}
\m20writtenby{[Writer Name]}
\m20developedby{[Developer Name]}
\m20editedby{[Editor Name]}
\m20specialthanks{[Special Thanks]}
% Optional fixed year; omit to use the TeX engine's build year automatically.
\m20copyrightyear{2026}

\begin{document}
\frontmatter
\mTwentyInteriorTitle{My Book}{Subtitle or author line}
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
