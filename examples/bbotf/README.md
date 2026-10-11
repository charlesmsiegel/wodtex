# BBotF research templates — WodTeX M20 specimen

This example demonstrates how to **typeset Markdown research templates** from
`tellurium-games/better-book-of-the-fallen/templates/` using `wodtex`'s
`m20book` document class. It is **not a manuscript generator** and is not
intended for publication without human-authored content.

WodTeX is a **LaTeX-based authoring system**. A preamble alone cannot read
Markdown. The `prepare.py`/Pandoc step converts Markdown to LaTeX fragments;
`pandoc-wodtex.lua` maps Markdown pipe tables to the native **full-width
`booktable` environment** rather than an incompatible raw `longtable`.
The output also uses normal headings, emphasis, lists, links and (optionally)
`statblock` environments. The `preamble.tex` is an ordinary M20 WodTeX preamble
and `reference.tex` combines the converted entries into one layout specimen.

## Prerequisites

- `wodtex` installed as described in the repository root `README.md`
- LuaLaTeX and the M20 fonts/layout assets installed/configured
- Pandoc 3.x on `PATH` (this is an **optional extra dependency** for this example)
- Python 3.9+
- Access to your separate `better-book-of-the-fallen` checkout

## Build the specimen

Assuming the two repositories are siblings:

```sh
# In the wodtex repository root:
python3 examples/bbotf/prepare.py ../better-book-of-the-fallen/templates
cd examples/bbotf
lualatex -interaction=nonstopmode -halt-on-error reference.tex
lualatex -interaction=nonstopmode -halt-on-error reference.tex
```

The result is `examples/bbotf/reference.pdf`. To include all **21 templates**, use
`python3 examples/bbotf/prepare.py ../better-book-of-the-fallen/templates --all`
from the repository root before running LuaLaTeX. The script generates a
`contents.tex` manifest consumed by `reference.tex`, so it does not require
editing `\input` statements for additional research templates.

The source files under
`examples/bbotf/generated/` are generated; they are intentionally ignored.
You may also open a single converted fragment to see exactly which TeX
constructs Pandoc produced.

## Mapping

| Source | Native LaTeX target |
| --- | --- |
| `#` headings and `##` subheadings | `\section`, `\subsection`, etc., under specimen `\chapter` |
| Bold field labels (`**Spheres:**`) | `\textbf{Spheres:}` |
| Markdown pipe tables | WodTeX `booktable[head-rows=1,width=container]` |
| `-` bullet lists | Standard `itemize` |
| `::: statblock` fenced block (optional) | WodTeX `statblock` + `\statentry` |
| Markdown links | LaTeX links; internal `.md` targets remain research links |

### Optional statblock convention

Markdown writers can add a fenced div to a **working research document**:

```markdown
::: statblock
**Rank:** 4

**Spheres:** Entropy 3, Spirit 4
:::
```

The filter converts each paragraph to a `\statentry` line.
Existing templates work without this syntax; it is entirely optional.

## Limitations and authoring rules

- This adapter is intentionally **narrow**: it supports simple pipe tables
  without merged cells. It does not promise to render every Markdown extension.
- Tables use unique IDs derived from their input filename so multiple
  templates can be combined without duplicate-anchor errors.
- The PDF shows **placeholders** literally. Fill in or replace the research
  scaffolding before attempting a publication layout.
- Links to `.md` files are research references. Replace with normal WodTeX
  `\label`/`\ref` links (or verified external URLs) in the human-authored book.
- `wodtex` offers PDF styling and typesetting, not a copyright, licensing, or
  Storytellers Vault compliance check.
- Neither this example nor its converted output belongs in the BBotF
  `manuscript/` directory. The author writes that material independently.
- Re-run `prepare.py` after changes to template structure or the Markdown
  source; it never edits or commits the original Markdown.