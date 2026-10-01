# Crossover styles and template ingestion

This is an extension design for review and for agents ingesting additional
licensed templates. It records the owner's direction; the dispatch layer and
WoD/MSC renderers described here are **planned**, not implemented. Do not turn
this guide into an unrequested framework rewrite.

## Current implementation

`m20book` selects the corrected installed M20 PDF renderer. The repository
builder retains its separate base/explicit-correction workflow. Native `title`
and `author` collect book metadata; the native title supplies running-title and
PDF-title defaults unless explicitly overridden. `profile=m20` is already the
class default and is unnecessary in an ordinary M20 preamble.

Existing `m20setup`, metadata setters, environments, tables, art reservations and
interior-title/credits helpers remain supported. Only M20 has an implemented
class/renderer. There is no generic visual dispatch API, no `wodbook` class and
no implemented MSC design. Setting a profile name is not proof that its fonts,
artwork, geometry or rendering have been implemented.

## Required behavior

Generic author commands select the document class's style. Explicitly prefixed
**rendering** commands select their named style for that element, even in a book
whose surrounding style differs. For example, a future generic `sidebar` in
`wodbook` uses WoD, while `m20sidebar` in the same book must use M20. Do not make
`m20sidebar` an alias that silently changes meaning with the document class.

A style is a stable ID with explicit resources and rendering capabilities.
Examples of future IDs are `m20`, `wod` and `msc`; the IDs alone do not authorize
inventing their designs. A class owns the default ID. Element construction
records either the class default or an explicit ID, and retains that selection
through measurement, page breaking, continuation, output painting and EPUB
conversion. Resolve style once per semantic element, not from mutable global
state whenever a fragment is drawn.

## Metadata and candidate preamble names

Keep metadata storage separate from rendering. `title`, `author`, credited
writers, developers, editors, acknowledgments and copyright year are values,
not page geometry or font families. A credits renderer consumes those values.
Changing the renderer must not duplicate or discard their semantic data.

Candidate generic spellings are `booksetup`, `writtenby`, `developedby`,
`editedby`, `specialthanks` and a book copyright-year setter. These names are
**provisional**. Short setters can collide with another class or package;
`bookwrittenby`, `bookdevelopedby`, etc. are possible safer alternatives. Audit
loaded packages and fail clearly on a collision rather than using `def` to
silently replace another public command. Standard `title`/`author` remain the
primary metadata API. Existing `m20...` setters remain compatible.

The current prefixed metadata setters only collect values; they do not render
an independent element. Before adding crossover classes, explicitly settle
whether a prefixed setter also records a style hint for that specific credit
entry. Do not infer a whole-book style change from it. An explicit prefixed
credits/title/sidebar **renderer** must select its named style locally. This
metadata-only naming decision is open; the required explicit visual overrides
above are not open.

A future preamble should need the class and shared metadata, not repeated title
strings in setup and PDF metadata. Existing explicit running/PDF-title overrides
must continue to take precedence. Preserve the explicit interior-title API;
a user can define one title macro and reuse it for native title and the helper.

## Page policies versus element styles

The document class owns paper size, inner/outer margins, columns, baseline
regions, running headers/folios, page backgrounds and frontmatter/mainmatter
transitions. A foreign-style sidebar cannot call global `geometry`, change the
host output routine, reset page numbering or repaint a whole page. Intentional
verso illustrations, recto chapter openers and necessary parity spacers are
page policies, not side effects of element selection.

An element style owns its font roles, colors, borders, textures, shadows,
internal insets and supported layouts. Fit the element into the host's available
width/height using an explicit, documented policy. Do not silently scale type
or clip a foreign template to make it fit. Unsupported host/style combinations
must return a clear capability error until an approved adaptation exists.

A page-level foreign title/opener is a separate capability requiring an explicit
page policy, not something obtained by embedding a foreign sidebar or heading.

## Resource and renderer ownership

Use profile-scoped font roles, art resources and component metrics. Namespace
control sequences, font-family identities, Lua tables/callbacks and cached
measurements by style. Do not reuse one style's package name or hard-coded art
filename for another. Resolve files through TeX/Lua search paths, not the current
working directory. Shared semantic IDs, notes, labels, references and index data
remain independent of style.

Isolate each element's fonts, colors, lengths, local command definitions and
renderer state. Balanced groups are necessary but not sufficient for breakable
objects: deferred shipout and continuation fragments need an immutable style
record, and callbacks must use the record belonging to the active object.
After an M20 element in a WoD book, body fonts, line width, paragraph parameters,
colors, page policy and subsequent generic elements must still be WoD. Nested
objects inherit a documented style context unless explicitly overridden.

The same semantic model should feed PDF and EPUB adapters. Do not claim a new
style supports EPUB until its mappings, continuations, accessibility and
navigation tests exist; a PDF-only checkpoint must say so explicitly.

## Template ingestion checklist

1. Read this guide, the existing command reference, manifest and relevant tests.
   Confirm the requested class/profile and which page/component designs are
   authorized. Obtain approval before inventing missing typography or artwork.
2. Inventory the supplied reference PDFs/templates and genuine font faces.
   Record file SHA256, page dimensions, font names/styles, copyright/license
   notices and owner-asserted distribution scope. Verify private-repository
   status before pushing licensed bytes. Do not assume independent license
   verification or permission for unrelated files.
3. Inspect actual PDF pixels and extracted text/font spans for title, credits,
   TOC, chapter, spread, sidebar, table, list/stat block and art variants that
   will be supported. Preserve original units and measure against the reference.
   Record missing faces/glyphs and explicit substitutions; do not synthesize
   faces silently.
4. Extract only needed decorations using checked source hashes. Preserve
   provenance and notices. Keep private manuscripts, unused InDesign/PSD files,
   caches and rendered test outputs outside tracked input allowlists.
5. Define a profile's capabilities, resource roles, component metrics and page
   policy independently. Implement its class default hook and explicit element
   selection without changing another style's global defaults.
6. Register all new classes, namespaced packages, Lua helpers, profiles and
   resources in installation and source-package manifests. **The current
   installer explicitly copies `m20book.cls`; adding `wodbook.cls` alone does
   not install it.** Its current bundle validation is also M20-specific and
   must gain an explicit profile registry when a second renderer is approved.
7. Version private configuration carefully. Preserve current M20 font/art
   overrides and existing config bytes on ordinary updates. Add profile-specific
   paths without conflating different fonts with the same filename. Document
   explicit configuration migration and verify fresh install plus update.
8. Run the regression matrix below and publish measured acceptance/limitations.
   Keep correction override/base hashes and the review patch consistent with
   source changes. Test installation from an unrelated document directory.

## Required regression matrix

- Existing M20 manuscripts and prefixed APIs retain their rendering and metadata.
- Generic commands select each implemented class default without profile flags.
- M20 sidebar/table/art in a future WoD host selects M20 resources and styling;
  a following generic element and body text return to WoD. Test the reverse.
- Mixed style fonts/colors/lengths do not leak through nested, spanning,
  breakable, deferred and continued elements; test multi-page continuations.
- Foreign elements conserve text, IDs, notes, references, links and index data.
- Width/height restrictions give useful errors; no unreviewed clipping or silent
  type scaling. Page-level geometry and output routines remain the host's.
- Short and multi-page TOCs of both ending parities keep only required spacer
  leaves and the intended illustration/opener spread. Later chapters retain
  their own facing leaves; native title defaults and explicit overrides work.
- Fresh/install/update and Windows CRLF source checks preserve deterministic
  committed input payloads, notices and local configuration.
- Each claimed PDF/EPUB capability has actual adapter acceptance tests. Report
  platform checks that were not run; a Linux proof is not a Windows proof.

## Minimal implementation sequence

1. Approve generic spellings and settle metadata-only prefix semantics. Add
   collision checks and compatibility tests before changing public commands.
2. Extract a style-neutral metadata/semantic layer and a registry with only M20.
   Keep `m20book` output identical; keep M20-prefixed renderers explicitly M20.
3. Introduce generic rendering entry points that dispatch to the class default,
   plus immutable per-element explicit selection and scoped resources. Prove
   same-style behavior and state restoration before adding a foreign design.
4. Ingest the next authorized WoD or MSC template into the registry, extend its
   class/install hooks and config, and implement only the reference-backed
   capabilities. Run mixed-style tests before claiming crossover support.
5. Extend remaining components and EPUB adapters through separately reviewed
   checkpoints. Do not bundle new designs into unrelated pagination fixes.
