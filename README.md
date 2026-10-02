# wodtex

wodtex is a native LaTeX authoring system for World of Darkness books. Write
ordinary LaTeX plus a small set of system-neutral commands, select a document
class, and compile with **LuaLaTeX**.

All **17 document classes** are implemented on `main` for PDF output. M20 uses
the corrected original-template layout; the other 16 profiles use their own
measured page geometry, genuine font faces, and extracted outer decorations
with shared native LaTeX composition. M20 also has a separate, existing
reflowable EPUB 3 workflow. The other profiles currently support PDF only.

## Contents

- [Install](#install)
- [Choose a document class](#choose-a-document-class)
- [Write and compile a book](#write-and-compile-a-book)
- [System-neutral commands](#system-neutral-commands)
- [System and layout overrides](#system-and-layout-overrides)
- [Repository builds and EPUB](#repository-builds-and-epub)
- [Current scope and troubleshooting](#current-scope-and-troubleshooting)

## Install

### Prerequisites

For the installed PDF system, you need:

- Git and access to this repository.
- **Python 3.9 or later** to run the installer.
- A TeX distribution with **LuaLaTeX** and its supporting LaTeX packages:
  MiKTeX on Windows, or TeX Live/MacTeX on Linux/macOS. The classes require
  LaTeX 2022-06-01 or newer. Select LuaLaTeX in your editor.
- `makeindex` if your book has an index; `latexmk` is an optional convenience.

The installer uses the Python standard library. It does not install Python
dependencies, TeX packages, or fonts into the operating system. On MiKTeX,
enable installation of missing packages or install the requested packages
through MiKTeX Console. The classes use packages such as `fontspec`, `geometry`,
`multicol`, `hyperref`, `longtable`, and `tcolorbox`/TikZ.

Clone the repository and keep the checkout in place:

```sh
git clone https://github.com/charlesmsiegel/wodtex.git
cd wodtex
```

### Windows: MiKTeX

From **Git Bash**:

```sh
bash install.sh
```

The launcher finds Python 3.9+ through `python`, `py -3`, or `python3`. When
using Windows Python, it registers the user tree with MiKTeX and refreshes its
file-name database. Both `initexmf` and `miktex` must be on `PATH`.

Alternatively, from **PowerShell**:

```powershell
py -3 scripts/install.py --miktex
```

The default Windows tree is `%LOCALAPPDATA%/wodtex/texmf`, falling back to
`%USERPROFILE%/wodtex/texmf`. No administrator installation is required.

### Linux/macOS: TeX Live or MacTeX

Install into the user tree reported by your TeX distribution:

```sh
python3 scripts/install.py --tree "$(kpsewhich -var-value=TEXMFHOME)"
```

This also handles MacTeX installations whose user tree differs from `~/texmf`.
On Unix, `bash install.sh` defaults to `~/texmf`; use it when that is your
distribution's `TEXMFHOME`.

For Windows TeX Live, use `py -3 scripts/install.py --tree "YOUR-TEXMFHOME"`
with the path reported by `kpsewhich -var-value=TEXMFHOME`, without `--miktex`.

### What the default installation provides

The installer installs the classes and supporting packages into
`TREE/tex/latex/wodtex/`. **The corrected M20 PDF layout is the default**;
no source patch needs to be applied for normal installed use.

This private checkout includes M20's fonts, prepared decorations, and original
reference PDF. A fresh default installation checks their hashes against
`bundle-manifest.json` and records the checkout's `fonts/` and `assets/`
locations in:

```text
TREE/tex/latex/wodtex-local/wodtex-local.tex
```

The rendering inputs remain in the checkout; keep it at that location.
See [input provenance](template-source/README.md) and
[font notices](fonts/NOTICES.txt) for the supplied resources.

**The other 16 classes need separately prepared template resources.**
Installing a class file alone does not supply those fonts or decorations.

### Prepare the other profiles

Use Python with the dependencies in `requirements.txt` installed; Python 3.12+
is the documented environment for the repository workflows. Supply the local
X20 template directory whose files match the selected profile descriptors.

On Windows, from PowerShell in the checkout:

```powershell
py -3 -m pip install -r requirements.txt
py -3 scripts/prepare_profile.py --profile all --source-root "C:/path/to/X20"
py -3 scripts/install.py --profile-root "$PWD/inputs/profiles" --miktex
```

On Linux/macOS:

```sh
python3 -m pip install -r requirements.txt
python3 scripts/prepare_profile.py --profile all --source-root "/path/to/X20"
python3 scripts/install.py --tree "$(kpsewhich -var-value=TEXMFHOME)" --profile-root "$PWD/inputs/profiles"
```

`--profile all` prepares the 16 additional profiles; M20 keeps its separate
bundled resources. To prepare a subset, repeat `--profile`, for example
`--profile w20 --profile msc`. The names are the style IDs in the class table
below. `--out DIR` changes the preparation destination; supply that same
directory as `--profile-root DIR` when installing.

Preparation checks the original source hashes and writes namespaced font/art
resources under `inputs/profiles/STYLE-ID/`. Keep the original source directory
structure intact. Prepared resources are local inputs and are not in Git.
The profile path is stored independently in:

```text
TREE/tex/latex/wodtex-local/wodtex-profiles-local.tex
```

See the [class reference](docs/X20-Class-Reference.md) and the
[profile source audits](docs/profiles) for exact input mappings and substitutions.

### Verify, update, and configure

From a manuscript directory outside the checkout:

```sh
kpsewhich m20book.cls
kpsewhich wodtex-local.tex
```

For another prepared class, also check its class and profile configuration:

```sh
kpsewhich w20book.cls
kpsewhich wodtex-profiles-local.tex
```

The returned paths should point to the installed user tree.

To update, return to the checkout, pull `main`, and repeat your installation
command. For Windows/MiKTeX in Git Bash:

```sh
git pull --ff-only origin main
bash install.sh
```

On Linux/macOS, repeat the `--tree "$(kpsewhich -var-value=TEXMFHOME)"` command.
If you selected a custom `--tree`, supply the same tree on every update.

Ordinary updates preserve both local configuration files. To explicitly
relink M20 to the bundled resources, including after moving the checkout:

```sh
bash install.sh --configure
```

To use other M20 rendering directories instead:

```sh
bash install.sh --configure --font-dir "C:/Private/fonts" --asset-dir "C:/Private/assets"
```

Supply **both** paths. These are the layout's font/decoration directories, not
the folder containing your manuscript illustrations. When calling
`scripts/install.py` directly, use the same options plus your usual `--tree`
and, for MiKTeX, `--miktex`.

To relink the additional profiles, explicitly supply `--profile-root DIR`.
Their configuration is independent of M20's `--configure` operation.
The installer refuses to overwrite locally edited managed package files;
put manuscript settings in the preamble or local configuration instead.

## Choose a document class

Change `\documentclass{...}` to select the book's default style. The generic
commands remain the same; supported option details can vary by renderer.

| Book style | Style ID | Document class |
| --- | --- | --- |
| Mage: The Ascension 20th Anniversary | `m20` | `m20book` |
| M20 Dark Ages | `m20-dark-ages` | `m20darkagesbook` |
| Mage: The Sorcerers Crusade | `msc` | `mscbook` |
| V20 clanbook | `v20-clanbook` | `v20clanbook` |
| Victorian Age V20 | `vva20` | `vva20book` |
| Victorian Age V20 clanbook | `vva20-clanbook` | `vva20clanbook` |
| Werewolf: The Apocalypse 20th Anniversary | `w20` | `w20book` |
| W20 Dark Ages | `w20-dark-ages` | `w20darkagesbook` |
| W20 Wyld West | `w20-wyld-west` | `w20wyldwestbook` |
| Changeling: The Dreaming 20th Anniversary | `c20` | `c20book` |
| Dark Ages Fae | `dark-ages-fae` | `darkagesfaebook` |
| Demon | `d20` | `d20book` |
| Wraith 20th Anniversary | `wr20` | `wr20book` |
| KotE20 dharmabook | `kote20-dharmabook` | `kote20dharmabook` |
| KotEK20 | `kotek20` | `kotek20book` |
| KotEK20 legacybook | `kotek20-legacybook` | `kotek20legacybook` |
| General World of Darkness sourcebook | `wod` | `wodbook` |

All classes support native PDF. Only `m20book` has an EPUB backend.
KotEK labels are retained as supplied; their expansion is unconfirmed.

## Write and compile a book

Create `book.tex` in your own book directory. This complete starter uses only
the shared author interface:

```latex
\documentclass{m20book}
\title{My Book}
\subtitle{A Supplement for the Awakened}
\bookdescription{Stories, places, and people for your chronicle.}
\author{My Name}
\writtenby{My Name}
\developedby{Developer Name}
\editedby{Editor Name}
\specialthanks{The playtesters.}
% Optional: otherwise the year is taken from the TeX engine at build time.
% \copyrightyear{2026}

\begin{document}
\frontmatter
\maketitle
\makecredits
\tableofcontents

\mainmatter
\chapter{First Chapter}
\label{chap:first}
\section{Getting Started}
Ordinary book prose, with \textbf{bold} and \emph{italic} text.

\begin{sidebar}[id=field-note]{Field Note}
A note in the selected book style.
\end{sidebar}

\begin{booktable}[id=sample-table,head-rows=1]{ll}
Name & Value \\
First & One \\
Second & Two \\
\end{booktable}

\begin{statblock}
\statentry{\textbf{Strength}: 3}
\statentry{\textbf{Resolve}: 4}
\end{statblock}

\appendix
\chapter{Reference Material}
See Chapter~\ref{chap:first}.
\end{document}
```

After preparing that class's resources, replace `m20book` with, for example,
`w20book` or `mscbook` to typeset the same source with that class's page policy,
fonts, and component styles.

From the directory containing `book.tex`:

```sh
lualatex -interaction=nonstopmode -halt-on-error book.tex
lualatex -interaction=nonstopmode -halt-on-error book.tex
```

The result is `book.pdf` beside the source. Run LuaLaTeX again if the log asks
for another pass to settle contents or cross-references. If installed,
`latexmk` can handle reruns:

```sh
latexmk -lualatex -interaction=nonstopmode -halt-on-error book.tex
```

For an index, add `\makeindex` in the preamble, use `\index{term}` in the text,
and place `\backmatter\printindex` at the end. Compile, run
`makeindex book`, then run LuaLaTeX again until references settle.

Use ordinary `\input{chapters/introduction.tex}`, `\include`, headings,
lists, mathematics, footnotes, `\label`, `\ref`, `\pageref`, and hyperlinks.
Keep your own illustrations next to the manuscript, for example
`art/scene.png`. Installed PDF compilation does not need the checkout on
`TEXINPUTS` or the repository's Python build driver.

## System-neutral commands

Unprefixed author commands use the document class's default renderer.
A nested generic element inherits its enclosing element's selected style.

| Command or environment | Purpose |
| --- | --- |
| `\title{TEXT}`, `\author{TEXT}` | Standard LaTeX title and author metadata |
| `\subtitle{TEXT}` | Subtitle consumed by the title renderer |
| `\bookdescription{TEXT}` | Description consumed by the title renderer |
| `\writtenby{TEXT}`, `\developedby{TEXT}`, `\editedby{TEXT}` | Credit-role values |
| `\specialthanks{TEXT}` | Acknowledgments |
| `\copyrightyear{YYYY}` | Override the build-year default |
| `\booksetup{KEY=VALUE,...}` | Settings supported by the selected renderer |
| `\maketitle`, `\makecredits` | Render title and credits from stored metadata |
| `sidebar[KEYS]{TITLE}` | One-column-width sidebar |
| `sidebarwide[KEYS]{TITLE}` | Full-width sidebar, optionally with two internal columns |
| `\sidebarbreak[page]` or `\sidebarbreak[column]` | Explicit continuation inside a sidebar |
| `booktable[KEYS]{COLUMN-SPEC}` | Table using native `&` and `\\` row syntax |
| `tablelead` | Table lead/group; behavior depends on the renderer |
| `statblock`, `\statentry{TEXT}` | Stat-block container and entries |
| `\artreserve[KEYS]{ID}` | Artwork or a placeholder; the braced ID is optional |

Environment names are used as `\begin{NAME}...\end{NAME}`. Credit fields are
empty until supplied; `\author` does not infer writers, editors, or developers.
M20's native title also supplies the default running title and PDF title.
Metadata setters store values independently of visual styling.

### Sidebars

```latex
\begin{sidebar}[id=short-note,place=flow,breakable=true]{A Short Note}
One-column sidebar text.
\end{sidebar}

\begin{sidebarwide}[id=wide-note,columns=2,place=next-page]{A Wide Note}
First part of the note.
\sidebarbreak[page]
The continuation.
\end{sidebarwide}
```

Common options are `id`, `place`, `columns`, and `breakable`.
Use `place=flow` for normal composition or `place=next-page` to start on a
fresh page. Use `columns=1` or `columns=2` inside a wide sidebar; keep narrow
sidebars at one internal column. Short atomic notes can use `breakable=false`.

M20 also enforces a strict first-segment placement for `place=here`; it can
error when the segment does not fit. The newer profiles accept `here` without
that strict placement guarantee, and both sidebar break modes use their native
box continuation. M20's `balance` option is accepted but does not select an
alternative balancing algorithm.

For sidebar/table IDs, start with a letter and use letters, digits, `-`,
`:`, `.`, or `_`. IDs must be unique within a document.

### Tables and associated prose

```latex
\begin{booktable}[id=costs,head-rows=1]{ll}
Item & Cost \\
Book & 10 \\
Map & 5 \\
\end{booktable}
```

The required column specification uses native LaTeX columns such as `l`, `c`,
`r`, and `p{DIMENSION}`. Use paragraph columns for wrapped prose.
Set `head-rows` explicitly for portable source: M20 defaults to `0`, while the
other profiles default to `1`.

M20 supports container/column/explicit table widths, scaling, alignment,
repeated headers, and owner pagination. Compact tables can float at page
edges; tables inside a sidebar stay with that owner. The other profiles use
`longtable` outside sidebars and atomic `tabular` inside them. M20-specific
`width`, `scale`, `align`, and `epub` keys are not implemented by the newer
profile renderer.

In **corrected M20 PDF**, wrap a title, lead, and one compact table to keep the
whole group together:

```latex
\begin{tablelead}
\subsection{Equipment}
Introductory prose that must travel with this table.
\begin{booktable}[id=equipment,head-rows=1]{ll}
Item & Cost \\
Book & 10 \\
\end{booktable}
\end{tablelead}
```

This M20 group must fit one page and sit outside sidebars. Leave multipage
tables in the ordinary table stream. The other profiles' `tablelead` renders
lead prose without M20's atomic keep-together/floating guarantee.

### Stat blocks

Use `\statentry{TEXT}` inside `statblock`, as in the starter book.
For M20, literal `|` separators in an entry become separate keyed lines.
The other profiles render each entry as authored; use separate
`\statentry` calls when sharing source across styles.

### Artwork

The simplest call needs only an image path:

```latex
\artreserve[image={art/scene.png}]
\artreserve[kind=vertical,image={art/portrait.png}]
```

The default kind is `horizontal`. A braced ID, caption, credit, alternative
text, and placement options are optional:

```latex
\artreserve[image={art/scene.png},
  alt={A ruined observatory beneath a red moon},
  caption={The abandoned observatory},
  credit={Artist Name}]{observatory}

\artreserve[kind=vertical]{reserved-portrait}
```

With no image, the command reserves a labeled placeholder. With an image,
the file must exist. Paths are relative to the manuscript for ordinary
installed compilation. Supply an explicit ID, or separate following grouped
prose with a blank paragraph, so that group is not consumed as an optional ID.

**Corrected M20 PDF:** images stretch to fill the entire frame interior,
including intentional aspect-ratio distortion. Caption/credit text reserves
its band only when supplied. Omitting both gives the image the full interior.
Horizontal art uses native top/bottom edge floats; vertical art occupies a
full-height text column on a fresh page. Artwork cannot be nested in sidebars.

M20 images are meaningful by default. Missing `alt` text gives a PDF
accessibility warning, but a path-only call still compiles. Use
`role=decorative` for ornaments; supply `alt` for meaningful accessible
content. Strict EPUB checking can reject meaningful images with empty
descriptions.

**Other PDF profiles:** images preserve aspect ratio within horizontal or
vertical reservations. Use `place=flow` or `place=next-page`; M20's anchored
`position` keys are unsupported and fail explicitly. Accepting `alt` and
`role` in the PDF interface does not imply an implemented EPUB adapter.

## System and layout overrides

### Explicit template components

PDF books can mix components from all 17 templates. Use a template prefix to
select the component style: `m20sidebar` in a `w20book`, `w20table` in an M20
sidebar, or `mscstatblock` in a WoD book. The host class keeps its page layout.
Generic commands select the class style. Existing explicit M20 commands retain
their M20 meaning. They are useful for M20-specific source and compatibility:

| Generic interface | Explicit M20 interface |
| --- | --- |
| `\booksetup{...}` | `\m20setup{...}` |
| `sidebar` | `m20sidebar` |
| `sidebarwide` | `m20sidebarwide` |
| `\sidebarbreak[page]` | `\m20sidebarbreak[page]` |
| `booktable` | `m20table` |
| `tablelead` | `m20tablelead` |
| `statblock` | `m20statblock` |
| `\statentry{TEXT}` | `\mTwentyStatEntry{TEXT}` |
| `\artreserve[KEYS]{ID}` | `\m20artreserve[KEYS]{ID}` |
| `\maketitle` | `\mTwentyInteriorTitle{TITLE}{LOWER-LINE}` |
| `\makecredits` | `\mTwentyInteriorCredits{CONTENT}` |

The explicit title and credits commands take their content arguments directly.
The `\m20writtenby`, `\m20developedby`, `\m20editedby`,
`\m20specialthanks`, and `\m20copyrightyear` setters share the same neutral
metadata; their prefix does not change the renderer.

For example, a generic table and continuation inside an explicit M20 sidebar
keep that sidebar's M20 context:

```latex
\begin{m20sidebarwide}[id=mage-note,place=next-page]{A Mage Note}
\begin{booktable}[id=mage-records,head-rows=1]{ll}
Trait & Rating \\
Arete & 3 \\
\end{booktable}
\sidebarbreak[page]
Further notes.
\end{m20sidebarwide}
```

This works in a W20 host as well as an M20 host. Nested generic elements
inherit the sidebar's selected style; an explicit prefix can override it again.
Body text and subsequent generic elements return to the surrounding style.

Every style provides prefixed `sidebar`, `sidebarwide`, `table`, `tablelead`,
and `statblock` environments, plus `sidebarbreak`, `statentry`, and `artreserve`
commands. For example, use `\m20statentry{TEXT}`, `\w20artreserve[KEYS]{ID}`,
or `\mscsidebarbreak[page]`. See [crossover usage and all prefixes](docs/Crossover.md)
and the [complete mixed-template example](examples/crossover.tex).

Install the updated packages and prepare the resources for each style you use.
Foreign component resources load on demand. These prefixes cover PDF components;
front matter, chapter pages, running heads, and page-policy setup stay with the
host. Foreign tables use portable `longtable`/`tabular` rendering, and foreign
art supports flow/next-page placement. Native M20's additional positioning and
floating options remain specific to its host renderer. Cross-template EPUB
support remains pending; the generic `style=...` option is not implemented.

The registry provides preamble-only extension hooks
`\wodtexRegisterRenderer{STYLE}{CAPABILITY}{COMMAND-NAME}` and
`\wodtexSetClassStyle{STYLE}`. These are adapter APIs, not replacements for
selecting the document's page policy through its class. See
[Crossover Style Architecture](docs/design/Crossover-Style-Architecture.md)
for the extension contract.

### Setup and page-policy overrides

For all PDF classes, a custom running title can be set in the preamble:

```latex
\booksetup{running-title={Short Book Title}}
```

The other 16 profiles currently support only `running-title` through
`\booksetup`. Their page sizes, geometry, and typography come from their
selected class/profile. M20 additionally supports:

| M20 setup key | Default | Purpose |
| --- | --- | --- |
| `running-title` | Native title | Override the running book title |
| `font-path` | Installed local configuration | Rendering fonts; trailing slash required |
| `asset-path` | Installed local configuration | Layout decorations; trailing slash required |
| `math` | `legacy` | Select `legacy` or explicit `unicode` mathematics |
| `chapter-title-size` | `60bp` | Initial chapter heading size |
| `chapter-title-leading` | `54bp` | Initial chapter heading line spacing |
| `chapter-body-gap` | `6bp` | Extra space below the chapter opener |
| `profile` | `m20` | Legacy M20 profile setting; use document classes to select other systems |

Examples for an M20 preamble:

```latex
\booksetup{chapter-body-gap=9bp}
\booksetup{chapter-title-size=48bp,chapter-title-leading=45bp}
% Optional document-specific paths, using forward slashes:
% \booksetup{font-path={C:/Private/fonts/},asset-path={C:/Private/assets/}}
% Optional PDF-title override; M20 otherwise uses \title:
% \hypersetup{pdftitle={A Separate PDF Title}}
```

`bp` is a PDF point, 72 per inch. These M20-only keys are rejected by the
other profile renderer.

For M20 artwork, `position=top`/`bottom` applies to horizontal reservations
and `position=inner`/`outer` to vertical reservations. Defaults are `top`
and `outer`, respectively:

```latex
\artreserve[position=bottom,image={art/scene.png}]
\artreserve[kind=vertical,position=outer,image={art/portrait.png}]
```

M20 `place=here` keeps edge-float behavior for horizontal art; it is not a
promise to put a rectangle inline in a prose column. Move explicit art calls
at paragraph/section seams to control an illustration schedule.

Use normal LaTeX counters for heading/contents depth, for example
`\setcounter{secnumdepth}{0}` and `\setcounter{tocdepth}{2}`.
The installed corrected M20 layout already suppresses printed section numbers.
M20-specific `\m20bodybegin`, `\m20bodyend`, `\m20newpage`,
`\m20anchor{ID}`, `\m20note{TEXT}`, and `\m20script{TEXT}` remain available
for advanced flow, stable anchors, local notes, and explicit script-font use;
they are not part of the shared cross-class command set.

## Repository builds and EPUB

Normal installed PDF compilation uses the LuaLaTeX commands above. The
repository driver is useful for profile verification, build reports, and the
separate M20 EPUB workflow. Run repository commands from the checkout root;
on Windows, use `py -3` in place of `python3`.

### Native builds for the additional profiles

After preparing resources and installing the Python dependencies:

```sh
python3 scripts/build.py --target pdf --source examples/profiles/w20.tex --out build/w20 --verify
```

The driver selects the profile from the source's literal `\documentclass`.
It uses LuaLaTeX on `PATH`, or `WODTEX_LUALATEX`, and the resource directory
`inputs/profiles/`, or `WODTEX_PROFILE_ROOT`. It checks resource hashes,
converges references/index, and rejects missing glyphs or unresolved references;
`--verify` also checks measured page dimensions.

Use **`--target pdf`** for these profiles: the driver's default is `all`,
which requests an unsupported EPUB output and fails.

### M20's separate repository workflow

The M20 repository source retains a base PDF/EPUB renderer. The installed
corrected PDF renderer is selected by the installer without modifying that
source tree. For corrected repository-source PDF builds, see the
[original-layout correction package](contrib/original-m20-layout/README.md);
its checked source patch is separate from normal installation.

The legacy M20 driver needs Python 3.12+, the packages in `requirements.txt`,
a compatible TeX installation, and the pinned tools/converters described by
`runtime.lock.json`. Its full preparation also uses Java, Node.js, and Poppler.
This toolchain is separate from the installed PDF prerequisites.

```sh
python3 -m pip install -r requirements.txt
python3 scripts/preflight.py --prepare
python3 scripts/build.py --target all --source examples/book.tex --out build/book --verify
```

Initial preflight preparation needs network access to its pinned sources.
Supply the layout's compatible M20 resources for the selected source renderer;
the default installed corrected resources do not by themselves establish a
working legacy base/EPUB build. See [repository setup](docs/README.txt) for
the separate `prepare_assets.py` template-import workflow.

The existing M20 EPUB adapter covers the supported legacy semantic interface.
**Generic-interface EPUB acceptance and complete mappings for corrected
print-only title/credits, `tablelead`, and `statblock` remain pending.**
A successful corrected PDF is not evidence that the same manuscript supports
EPUB. The other 16 classes reject `output=epub`, `--target epub`, and
`--target all`.

Common driver options:

| Option | Meaning |
| --- | --- |
| `--target pdf\|epub\|all` | Output target; default `all` |
| `--source FILE` | Native LaTeX entry file; default `examples/specimen.tex` |
| `--out DIR` | Output directory under the checkout's `build/` tree |
| `--verify` | Run the selected target's verification |
| `--prepare` | Prepare M20's pinned runtime; does not import template resources |
| `--max-runs N` | Maximum PDF convergence passes; default `8` |

Results are `OUT/pdf/NAME.pdf` and, where supported, `OUT/epub/NAME.epub`.
`OUT/build-report.json` and target logs record the actual result.

To render the comparison showcase after preparing all profiles:

```sh
python3 examples/showcase.py
```

It writes individual books and a bookmarked comparison PDF under
`build/showcase/`. Tests and source packaging are available through:

```sh
python3 -m unittest discover -s tests -t . -v
python3 scripts/package.py --out build/packages/wodtex-m20.zip
```

The historical ZIP filename is retained; the source package includes all
classes, examples, tests, and documentation. It excludes template rendering
inputs, prepared resources, private manuscripts, and downloaded runtimes.
A source ZIP therefore needs separately supplied rendering inputs after unpacking.

## Current scope and troubleshooting

Recorded acceptance covers native specimens for the 16 new profiles and
installation/compilation of all 17 classes from an unrelated manuscript
directory. See [the acceptance record](docs/profiles/Acceptance.md) for the
platform evidence, remaining legacy test failures, and reproducible checks.
It does not claim a clean full historical test suite.

The additional profiles are native adaptations of supplied templates, with
documented genuine-face substitutions and extracted outer frames. They do not
reproduce every illustrated clan, season, or chapter variant. Separate covers
and EPUB for these profiles remain open. PDF component mixing is supported
through the [prefixed crossover interface](docs/Crossover.md).

| Symptom | Check or action |
| --- | --- |
| Class/config not found | Check `kpsewhich`; register/refresh the MiKTeX user tree or install into TeX Live's actual `TEXMFHOME` |
| Old behavior after updating | A manuscript-local `m20book.cls` or obsolete `tex/` directory can shadow the installed packages |
| `luaotfload-main` missing or font-loading failure | Install the TeX distribution's LuaLaTeX font support; the engine binary alone is insufficient |
| Missing M20 font/decoration | Check `wodtex-local.tex`, keep the checkout in place, or explicitly relink with `--configure` |
| `WODTEX_E_RESOURCE_MISSING` | Prepare that profile and set `--profile-root`; class installation alone supplies no additional-profile artwork |
| Source/resource hash mismatch | Use the matching original templates or regenerate prepared resources with the current preparation recipe |
| `WODTEX_E_SETUP_OPTION` / unknown option | Use keys supported by the selected class; M20-only keys are not portable |
| `WODTEX_E_POSITION_UNSUPPORTED` | Anchored art is M20-specific; use `place=flow` or `place=next-page` in other profiles |
| `WODTEX_E_HOST_UNSUPPORTED` / `WODTEX_E_CAPABILITY` | The requested adapter/element is unavailable in that host or output |
| `WODTEX_E_NAME_COLLISION` | Another package replaced a generic author command or environment |
| Missing glyphs in M20 multilingual prose | Use explicit script selection, for example `\foreignlanguage{arabic}{\m20script{مرحبا}}`; automatic selection remains deferred |
| References/index unsettled | Repeat LuaLaTeX; run `makeindex book` for an index |

Further references: [runnable M20 generic example](examples/generic-book.tex),
[profile examples](examples/profiles/README.md),
[class reference](docs/X20-Class-Reference.md), and
[crossover extension contract](docs/design/Crossover-Style-Architecture.md).
