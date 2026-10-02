# Mixing template components

PDF documents can use a component from another template by naming its prefix.
The document class still owns paper size, margins, body columns, page backgrounds,
chapter pages, running heads, and front matter. A prefixed element owns its fonts,
colors, frame, and internal spacing. Returning from that element restores the
surrounding style.

For example, install the corrected M20 resources and prepare the W20 resources,
then compile this with LuaLaTeX:

```latex
\documentclass{w20book}
\begin{document}
\mainmatter
\chapter{Crossover}
This is W20 body text.

\begin{m20sidebarwide}[id=mage-note]{An Awakened Perspective}
This note uses M20's Goudy prose, Abbess heading, textured dark frame,
gold rules, and shadow.
\begin{booktable}[id=mage-traits,head-rows=1]{ll}
Trait & Rating \\
Arete & 3 \\
\end{booktable}
\begin{w20table}[id=wolf-traits]{ll}
Trait & Rating \\
Gnosis & 4 \\
\end{w20table}
\sidebarbreak[page]
The M20 note continues here.
\end{m20sidebarwide}

\begin{sidebar}{A Garou Perspective}
This unprefixed note uses W20 again.
\end{sidebar}
\end{document}
```

The generic `booktable` inherits M20 from its enclosing sidebar. The explicit
`w20table` selects W20 even there. No additional class or native style package
should be loaded. See [the complete example](../examples/crossover.tex).

## Prefixes

| Style ID | Prefix |
| --- | --- |
| `m20` | `m20` |
| `m20-dark-ages` | `m20darkages` |
| `msc` | `msc` |
| `v20-clanbook` | `v20clanbook` |
| `vva20` | `vva20` |
| `vva20-clanbook` | `vva20clanbook` |
| `w20` | `w20` |
| `w20-dark-ages` | `w20darkages` |
| `w20-wyld-west` | `w20wyldwest` |
| `c20` | `c20` |
| `dark-ages-fae` | `darkagesfae` |
| `d20` | `d20` |
| `wr20` | `wr20` |
| `kote20-dharmabook` | `kote20dharmabook` |
| `kotek20` | `kotek20` |
| `kotek20-legacybook` | `kotek20legacybook` |
| `wod` | `wod` |

Append the following component names to any prefix:

| Generic interface | Prefixed spelling, using M20 |
| --- | --- |
| `sidebar[KEYS]{TITLE}` environment | `m20sidebar[KEYS]{TITLE}` |
| `sidebarwide[KEYS]{TITLE}` environment | `m20sidebarwide[KEYS]{TITLE}` |
| `booktable[KEYS]{COLSPEC}` environment | `m20table[KEYS]{COLSPEC}` |
| `tablelead` environment | `m20tablelead` |
| `statblock` environment | `m20statblock` |
| `\statentry{TEXT}` | `\m20statentry{TEXT}` |
| `\sidebarbreak[page]` | `\m20sidebarbreak[page]` |
| `\artreserve[KEYS]{ID}` | `\m20artreserve[KEYS]{ID}` |

Literal numeric command spellings work without catcode changes. Normal LaTeX
accents such as `\c{c}`, `\d{d}`, and `\v{s}` keep their meaning. Existing native
M20 environments and legacy commands remain available in M20 books.

## Resources and compilation

Update the installed classes/packages using `scripts/install.py`; crossover is
loaded automatically by PDF classes. Prepare each additional profile that you
actually use with `scripts/prepare_profile.py`, and configure its parent resource
directory with `--profile-root` as described in [the README](../README.md).

M20 foreign components use the corrected Goudy/Abbess fonts and extracted M20
component artwork configured in `wodtex-local.tex`. M20 hosts also respect their
existing `font-path` and `asset-path` setup. Resources are resolved when a style
is first used and then retained for that document; configure paths in the
preamble. Registering all prefixes does not require preparing every profile.
Missing selected fonts or M20 component artwork produces
`WODTEX_E_RESOURCE_MISSING`.

```sh
lualatex -interaction=nonstopmode -halt-on-error book.tex
lualatex -interaction=nonstopmode -halt-on-error book.tex
```

## Component behavior and limits

- Foreign sidebars support `id`, `place=flow|here|next-page`, `columns=1|2`, and
  `breakable=true|false`. Narrow sidebars have one internal column. Wide sidebars
  use the host's full text area; narrow ones use its column width. Foreign `here`
  follows normal box composition, without native M20's strict first-fragment
  placement guarantee.
- One-column sidebars paginate automatically. Two-column sidebars use atomic
  fragments: insert `\sidebarbreak[page]` to continue on another page. Each
  fragment, including its title and notes, must fit the host text height.
  Oversized two-column fragments and oversized `breakable=false` sidebars fail
  with `WODTEX_E_SIDEBAR_FRAGMENT_TOO_TALL` instead of clipping content.
- Generic breaks inherit the enclosing sidebar. `page` starts a continuation on
  a new page; `column` advances the internal column, or continues on a new page
  for a one-column sidebar. A manual break in an atomic sidebar is an error.
  Sidebar nesting is unsupported.
- Foreign tables accept `id`, `place`, and `head-rows` (default `1`). They use
  native LaTeX column specifications, repeated headers in `longtable` outside
  components, and contained `tabular` inside sidebars, statblocks, or leads.
  A contained table is atomic; it cannot independently paginate across its
  parent frames, and `place=next-page` produces
  `WODTEX_E_CONTAINED_PLACEMENT`. Use `p{DIMENSION}` for
  wrapped cells. Foreign tables do not expose native M20's scaling, floating,
  width, or alignment options.
- Sidebar and table footnotes are numbered locally and printed at the end of
  their component. Repeated table headings reuse note marks without duplicating
  the note text. Semantic IDs and labels remain available for cross-references
  and must be unique across native and foreign components. Page references and
  destinations travel with the first placed frame or table header.
- Foreign `tablelead` supplies styled introductory prose. It does not provide
  native M20's bounded lead/table float. Foreign M20 stat entries accept `|` to
  separate lines and use compact Goudy typography; its combined bold/italic face
  uses genuine Goudy italic, matching the corrected native font policy.
- Foreign art supports `kind=horizontal|vertical`, `image`, `caption`, `credit`,
  `alt`, `role`, `id`, and flow/next-page placement. It uses the selected frame
  and local caption font within the host page area. Images retain their aspect
  ratio. M20 uses its extracted horizontal/vertical frames. Anchored positions
  and full-page foreign artwork are unsupported. `alt` and `role` are accepted
  source metadata, without a claim of tagged-PDF accessibility.
- The positional argument to `\PREFIXartreserve[KEYS]{ID}` supplies its semantic
  ID when `id=` is absent. When both are supplied, a different positional ID is
  an additional label for the same artwork. Both names are validated and must
  be unique; supplying the same name twice for that one artwork is allowed.
- Options apply only to their documented component. For example, `columns=` on
  a table or `image=` on a sidebar produces `WODTEX_E_OPTION`.
- Titles, credits, chapter layout, covers, page-policy setup, metadata setters,
  and output mode belong to the host. Prefixes select components, rather than
  providing foreign page commands. The generic `style=...` option is not part
  of this interface. Cross-template EPUB rendering remains unsupported.

Foreign rendering shares the host's page area and uses portable component
pagination. It does not import the other class's output routine or reproduce
its native page-placement behavior.

## Verification

```sh
python3 -m unittest tests.test_crossover.PrefixRoutingTests -v
WODTEX_CROSSOVER_RENDER=1 python3 -m unittest tests.test_crossover -v
```

The installed rendering tests use genuine bundled M20 component resources and
synthetic font/background fixtures for the other profiles. They verify routing,
font and page-policy isolation, nested overrides, continuations, notes, labels,
art frames, content conservation, and identical native M20 page pixels with
crossover loaded or disabled. They do not establish visual acceptance
against every original X20 template. Those profiles' native acceptance records
remain separate.
