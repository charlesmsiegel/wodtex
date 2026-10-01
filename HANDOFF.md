# Incomplete implementation handoff

Stopped at the owner's request on 2026-09-30. This is a checkpoint, not a working finished template.

## Verified
- Approved design and implementation plan are in docs/design/.
- Actual LuaLaTeX font smoke rendered; ten genuine fonts embedded and inspected.
- Canonical Graveyards of Hope source is in private repo charlesmsiegel/agentic_wod_books, projects/graveyards-of-hope, commit fea0d9fb4ce637aecb220e303c6c97d8a81c6c96. Source SHA-256: 7ea3e1738eb9a4e542a6f84765a1c2b89e75f4e64cee6a5b3062d25adb09a37a.
- Inventory: ten chapters, two appendices, nine sidebars, 21 tables, 565 table cells.

## Known failures and remaining work
- Astra visually reviewed the first 20-page layout proof and found invisible body text, overlapping sidebar columns, a missing heading, and page-region overruns. Fix before treating the layout as usable.
- Runtime font smoke passing does not mean the page layout passes.
- EPUB structural/runtime work exists but actual reader visual verification was blocked by environment socket/network restrictions. No reader pass claimed.
- Full Graveyards PDF/EPUB has not been delivered or approved.
- Complete remaining approved plan tasks, full-book rendering, content conservation, index/TOC checks, visual checks, tests and final documentation.

## Assets and provenance
Proprietary fonts, original template artwork, IDML and reference PDFs are deliberately excluded. Obtain them from the owner's original template ZIP and use the asset preparation tooling; do not relicense or redistribute them. Large generated profile data and private manuscript conversion artifacts are not included in this initial checkpoint; recreate from original inputs using the scripts. The original M20 template link is https://www.dropbox.com/scl/fi/wumkcj1cftojpqsylzzrd/Mage_The_Ascension_4th_Edition_Templates.zip?rlkey=sb4scik22r8w1d00q6cab2o54&dl=0 .

## Architecture and acceptance
Keep semantic source separate from output format and visual profiles. PDF fidelity should match InDesign as closely as possible. Reflowable EPUB preserves content and meaningful art, with e-ink-friendly styling. All three sidebar variants, forced placement, and dedicated blank-verso/recto chapter spreads remain required. See the approved documents for the full contract.
