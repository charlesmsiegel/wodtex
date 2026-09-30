# Implementation ledger

The approved design and eight-task plan in this directory govern this work.
The handoff branch starts at `4f71fc5c0d289edcb845bcb096ae8f0c8b2da7ce`.

Pre-flight interfaces: Task 1 measured geometry/fonts feed Task 2 composition;
Task 2 ordered segment/shipout records feed Task 3 long flow and Task 4 art;
Task 2 semantics feed Tasks 5 and 6 navigation/conversion; Tasks 5/6 build
reports feed Task 7 verification; passing outputs feed Task 8 packaging.

Baseline: 13 tests ran; 7 failed and 3 errored. Missing prepared LuaLaTeX
format and an importer requiring absent external profile/audit files block it.

Ruling: recover the exact branch through GitHub Git objects because ordinary
git authentication is unavailable. Preserve the original commit and history;
publish fast-forward commits through the GitHub plugin. Cost if wrong: no
loss of existing history; an unsuccessful ref update leaves the branch intact.

Ruling: regenerate asset/profile metadata directly from the supplied IDML and
font/art input tree rather than requiring another untracked project's JSON.
The original IDML remains authoritative. Cost if wrong: decoration measurements
need correction during visual calibration; original inputs remain unchanged.

Initial runtime/profile checkpoint (superseded below): official pinned dependencies and supplied original
font/art files recovered; eight runtime/profile tests pass. Actual LuaLaTeX
font smoke compiled twice, rendered, and visually inspected. Tiny EPUB runtime
smoke still requires a missing transitive TeX4ht dependency. Task 1 is therefore
not claimed complete yet. No licensed inputs are committed.

## Working implementation checkpoint (2026-09-30)

Native PDF layout, long sidebars and tables, chapter openings, art reservations,
references/indexing, semantic EPUB conversion, bounded builds, and independent
output verification are implemented. The branch includes their integration
tests and a shared stress specimen. PDF layout proof: 20 pages. EPUB conversion
and EPUBCheck run successfully on the specimen.

Known nonblocking issue, deferred at the user's direction: changing from the
independent first-paragraph font back to the normal body font can prevent
Babel's automatic Greek, Cyrillic, Hebrew, and Arabic font selection. The
multilingual test failed at this checkpoint and the specimen's PDF build reported
`M20_E_MISSING_GLYPH`; the build does not silently bless missing characters.
Explicit script fonts remain available. Preserve this regression test.

Remaining work at that checkpoint: clean package/setup verification, final source/output checks,
reader rendering, documentation, and review before opening the PR to main.
Exact visual calibration against an original exported reference PDF remains
unverified because that reference was not supplied. This checkpoint is not a
claim that every design acceptance criterion has passed.

## Functional build and review follow-up

The multilingual issue remains deferred, with its original expected-failure
test intact. The specimen now uses explicit genuine script fonts and builds
both outputs successfully. It produces a 31-page PDF and valid EPUB. Stronger
conservation checks cover complete passages and reading order as well as IDs,
occurrence counts and the four fixed specimen MathML signatures.

An independent read-only review identified eight correctness/verification
issues. Fixes and regressions cover physical versus displayed folios, deletion
of the last index term, table-note ownership, collision-safe backlink IDs,
records-mode rowspan diagnostics, actual native table width/bounds, misspelled
public commands, and complete-passage/order conservation. The follow-up found
no residual critical or important issue. Consecutive table rules also account
for their native additional spacing.

Native TikZ diagrams now pass actual PDF/EPUB builds: the official pinned
dvisvgm runtime resolves standard vector font maps; EPUB labels use a genuine
mapped Latin Modern face, retain glyph definitions, and accept explicit alt
text. Arbitrary OpenType diagram-font fidelity is not claimed.

Review dispositions: basic first-paragraph scale and explicit script faces are
tested; automatic Babel switching stays deferred. Exact source-reference visual
equivalence stays open without the reference PDF. Mandatory placement and local
notes are covered by native integration fixtures. Repeated table headers have
one label, index write and note despite multiple renderings. Custom content and
image handling are scoped to documented adapters, with unknown content errors;
exhaustive TeX/package grammar is outside this authoring interface. Software
reader views are inspected and documented; reader-app interaction, physical
e-ink, language-specific xindy collation and universal math equivalence remain
unverified. Fresh-unpack setup and license/path/hash exclusions are tested.

Final navigation regression: native front/main/back matter state was local to
the live multicols group and disappeared at a chapter boundary. The native
commands now run after ending that group, then resume body flow. A failing
counter proof (1/2/3) now passes with the native book counters (0/1/1); all
three reference/index/physical-folio tests pass. The narrow independent review
found no residual issue in this change.

Final verification inventory: 57 cases, 56 passing and one expected failure
for the user-deferred automatic multilingual selection issue. All original
56 cases passed in six module groups (including licensed fresh-unpack setup),
then the affected three-test navigation module passed with the added regression.
The shared specimen verifies both outputs: 31-page PDF, EPUBCheck-valid EPUB,
and no independent output-verifier errors. Default and Unicode math plus
native TikZ paths build both formats. All 31 PDF pages and the documented five
software EPUB reader configurations were rendered and inspected.
