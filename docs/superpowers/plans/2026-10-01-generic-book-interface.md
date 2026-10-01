# Generic Book Interface Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement this approved plan in the existing main checkout.

**Goal:** Compile the approved generic manuscript through an installed M20 class while preserving old M20 APIs.

**Architecture:** Store metadata independently of rendering and register immutable style/capability callbacks.
Resolve the class default once per element and carry the selected context into nested tables, continuation commands and boxed deferred output.
Only the M20 adapter is a production style.

**Tech Stack:** LaTeX/expl3, LuaLaTeX, Python unittest and PyMuPDF.

**Spec:** `docs/design/Crossover-Style-Architecture.md` and the owner's explicitly approved generic source.

## Global Constraints

Work on main and push without force after reconciling remote changes.
Preserve licensed inputs, existing configuration bytes and M20 title/frontmatter visuals.
Do not invent WoD or MSC rendering or claim unverified EPUB or Windows support.
Use one sentence per prose source line and blank lines between paragraphs.

## Review Focus

- Existing or later command collisions must fail clearly instead of replacing another package's API.
- Nested generic tables in explicit M20 sidebars must retain M20 parsing and continuation behavior.
- Deferred floats must retain captured style and content after surrounding state changes.
- Unknown styles or capabilities must produce an actionable error.
- Metadata, font faces, PDF links, title overrides and parity must survive old/new API comparison.

## Task 1: Metadata, registry and generic M20 adapter

Files: `tex/wodtex-metadata.sty`, `tex/wodtex-registry.sty`, `tex/wodtex-m20.sty`, `tex/wodtex-api.sty`, `m20book.cls`, shared/corrected M20 core and sidebar sources.

Interfaces: `wodtexRegisterRenderer{style}{capability}{control-sequence-name}`, `wodtexSetClassStyle{style}`, generic commands and the existing M20 commands.
The registry snapshots renderer definitions and rejects duplicate registrations.
Class selection is preamble-only and cannot be mutated after document start.
Metadata-only M20 setters write the same shared fields without selecting a visual style.

- [x] Add the exact generic example with a clearly labeled meaningful-art fixture and failing installed-native test.
- [x] Verify the failure identifies the absent generic API.
- [x] Implement neutral metadata and checked generic names, registry, M20 callbacks and context-safe environment hooks.
- [x] Add old/new visual comparison, mixed test-only style, nested/continued/deferred content and collision tests.
- [x] Run the native regression and compatibility tests.

## Task 2: Distribution and publication

Files: installer, source-package manifest, correction manifest/review patch, README and architecture guide.

- [x] Install all new discoverable packages and ship the runnable example/fixture in the source archive.
- [x] Refresh correction hashes and preserve base/override reviewability.
- [x] Run installer, launcher, frontmatter, table compatibility and generic native tests.
- [x] Inspect PDF pixels/font spans/links and upload PDF, runnable source and fixture to Library.
- [x] Update implemented versus planned documentation, commit, reconcile and push main.

## Verification record

The initial exact example failed at undefined `subtitle` before implementation.
The generic and legacy complete examples now render identical page pixels.
The final full-project run executed 103 tests, including 46 passing native-install/interface regressions.
The broader pinned framework retained 40 failures and four errors from missing runtime formats, EPUB prerequisites and the original IDML input.
One test was skipped and one failure was expected.
Actual Windows/MiKTeX and complete generic EPUB acceptance were not run.

The independent review found mutable xparse callback internals and an unconditional native-title replacement.
Both findings were reproduced with failing tests and fixed in one pass.
An EPUB-mode native route probe and a base-mode route probe now pass without claiming EPUB conversion acceptance.
A previously skipped undefined conditional in reference initialization was moved outside the PDF-only branch so EPUB-mode loading remains balanced.
A manual sidebar break immediately after a table now handles the empty preceding Lua node list safely.
The mixed test-only style checks fonts, colors, width, indentation, paragraph skip, nested M20 tables, continuations and a deferred float.
No WoD or MSC renderer is included.
