# Crossover styles and template ingestion

The generic author interface and M20 adapter described below are implemented.
WoD/MSC renderers and adaptation to foreign page policies remain planned.
Do not turn this guide into an unrequested framework rewrite.

## Current implementation

`m20book` owns the M20 page policy and selects the registered `m20` default.
The repository builder retains its separate base/explicit-correction workflow.
Native `title` and `author` collect metadata, and the native title supplies running-title and PDF-title defaults unless explicitly overridden.
The installed corrected layout supports `subtitle`, `bookdescription`, `writtenby`, `developedby`, `editedby`, `specialthanks` and `copyrightyear`.
Metadata-only M20 setters write the same shared values without attaching a visual-style hint.

`maketitle` consumes title, subtitle and description through the M20 interior-title renderer.
`makecredits` consumes credited writers, developers, editors and acknowledgments through the M20 credits renderer.
Generic `booksetup`, `sidebar`, `sidebarwide`, `sidebarbreak`, `booktable`, `tablelead`, `statblock`, `statentry` and `artreserve` are implemented.
Existing M20-prefixed commands remain supported and select M20 rendering independently of the class default.
Generic nested tables and continuation/entry commands inherit their enclosing element's selected style.
An ordinary top-level generic element selects the class default.

Only M20 has a production class/renderer, and only the corrected native PDF installation has the complete generic capability set.
There is no `wodbook` class or implemented MSC design.
Setting a legacy profile name is not proof that its fonts, artwork, geometry or rendering have been implemented.
Generic EPUB acceptance has not been performed, and corrected print-only capabilities produce a capability error in EPUB/base mode.
The legacy native `maketitle` route remains available in base and EPUB modes.
Existing builder/EPUB workflows remain separate.

## Extension interface and ownership

`wodtex-metadata.sty` stores shared values independently of the adapters.
`wodtex-registry.sty` provides `\wodtexRegisterRenderer{style}{capability}{control-sequence-name}` and `\wodtexSetClassStyle{style}`.
Both registration and class selection are preamble-only.
Registration snapshots the callback definition and rejects duplicate style/capability pairs.
Names use lowercase letters, digits and hyphens, beginning with a letter.
Unknown styles and unimplemented capabilities fail with `WODTEX_E_STYLE_UNKNOWN` and `WODTEX_E_CAPABILITY`.
Generic name collisions fail before definitions are installed or when later replacements are detected at document start/shipout.
The intentional replacement of the native book class's `maketitle` is part of this interface.

The M20 adapter registers the following callback signatures.
Environment callbacks consume captured bodies without re-reading the manuscript.

| Capability | Arguments |
| --- | --- |
| setup | setup key list |
| maketitle, makecredits | none; consume neutral/native metadata |
| sidebar, sidebarwide | option key list, title, body |
| booktable | option key list, column specification, body |
| tablelead, statblock | body |
| sidebarbreak | page or column |
| statentry | entry text |
| artreserve | option key list, semantic ID |
| environment-before, environment-after | none; replace environment with sidebar, sidebarwide, booktable, tablelead or statblock |

The environment-before callback executes outside the environment group and suspends host body regions when necessary.
The environment-after callback resumes the host region after the environment group closes.
Keep those callbacks consistent with the class's immutable default and the enclosing style context.
Do not open body columns inside a nested native float or inside the generic environment's closing group.
Adapters scope local typography and metrics and own continuation records and deferred boxes.
The dispatcher resolves the selected ID immediately; it must never be queued to choose a mutable style at shipout.
M20 frames and floats finish typesetting their captured content before deferred output, and continuations remain in the captured enclosing context.
A test-only alternate adapter proves snapshot registration, mixed dispatch, continuation styling, deferred float styling and body color restoration.
It is not a WoD or MSC renderer.

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

The approved generic spellings above are implemented with explicit collision checks.
Standard `title` and `author` remain the primary metadata API.
Existing `m20...` setters remain compatible.

The prefixed metadata setters collect shared values without changing the renderer.
Explicit prefixed credits/title/sidebar renderers select M20 locally.
A future adapter consumes the same stored metadata through its own rendering capability.
Existing explicit running/PDF-title overrides continue to take precedence.

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

## Implemented checkpoint and remaining work

The generic spellings, neutral metadata, registry, M20 adapter and installed native PDF regressions are implemented.
Fresh installation and repeat updates include all shared packages and preserve local configuration.
The exact approved source and its explicitly labeled public geometric fixture are `examples/generic-book.tex` and `examples/art/scene.png`.
The new/old API comparison checks identical rendered page pixels, genuine font roles, text conservation and PDF navigation.

The next checkpoint must ingest an authorized WoD or MSC template, add a real class/install hook and profile-scoped configuration, and implement only reference-backed capabilities.
Foreign page policies need approved adapters and capability restrictions before explicit M20 elements can be claimed to work in those real hosts.
Further style namespaces for Lua callbacks, caches and resources must be added when the second production renderer exists.
Generic EPUB mappings and acceptance remain a separate checkpoint.
