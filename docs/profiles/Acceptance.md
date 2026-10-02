# X20 implementation acceptance

Completed 2026-10-02. All 17 classes are combined on `main`. Implementation
used eight separate family branches; those merged branches were removed at
the user's request. Their verified tips below remain in main's commit history.

| Original family branch | Preserved commit | Implemented styles |
| --- | --- | --- |
| `x20/mage` | `b6af5e8` | Existing M20, M20 Dark Ages, Mage: The Sorcerers Crusade |
| `x20/vampire` | `1889bc7` | V20 clanbook, Victorian Age V20, Victorian clanbook |
| `x20/werewolf` | `78d45f0` | W20, W20 Dark Ages, W20 Wyld West |
| `x20/changeling` | `7b360f8` | C20, Dark Ages Fae |
| `x20/demon` | `fb01578` | D20 |
| `x20/wraith` | `216e4c9` | Wr20 |
| `x20/eastern` | `c8b4217` | KotE20 dharmabook, KotEK20, KotEK20 legacybook |
| `x20/wod` | `220273c` | General World of Darkness sourcebook |

Every family started from `x20/foundation` and includes the final shared fixes.
Each preserved family commit contains its classes, descriptors, specimens and
source audits. Main also includes the combined inventory acceptance tests.
Class names are listed in [the examples index](../../examples/profiles/README.md).

## Validation

- All 16 new complete specimens compile with LuaLaTeX using genuine supplied
  fonts. Checks cover authored text, metadata, links, font identity, measured
  page sizes, references and index convergence.
- All 17 classes, including existing M20, compile from an isolated installed
  tree in an unrelated manuscript directory. No repository TeX search path is
  used. Ordinary updates preserve installed bytes and private configuration.
  The complete installed acceptance suite passes all six tests.
- Long sidebar and 150-row table proofs conserve final content and repeat
  continuation titles/table headers. Placement labels refer to their new page;
  vertical art compiles. Invalid/duplicate IDs, missing images, unsupported
  styles and anchored art fail explicitly.
- Foundation, resource/class routing regressions, inventory, build, installer
  and package checks pass: 28 tests, four environment-dependent skips. Those
  skipped legacy compilation/fresh-archive tests depend on separate tools or
  the historical Mage template ZIP; native installed compilation is covered
  by the dedicated X20 tests.
- All new prepared frames contain no PDF text operators displaying template
  content. Rendered contact sheets were visually inspected; audited exclusions
  also remove selected outlined/raster template labels and placeholders.
- Source archive hashes and installed payload are deterministic across updates
  and Windows CRLF checkouts. Prepared resource manifests bind exact font hashes
  and the complete preparation recipe; stale resources fail verification.
- Independent code review findings were addressed with regression checks.
- A fresh source archive independently prepares all 16 new resource sets from
  Downloads, installs all 17 classes into a new user tree, compiles every new
  full specimen plus an M20 preservation specimen, and preserves installed
  bytes on update. The native archive acceptance test passes; its PDFs and
  per-class page counts are under `build/x20/archive-proof/`.
- Full discovery was compared with an untouched `git archive main` checkout
  at the original `8270c61` baseline
  under the same environment. No failing test was introduced. The remaining
  four launcher failures and 34 legacy runtime/input errors also occur on main;
  the package-path and CRLF installer failures on main are resolved here.
  Final publication discovery ran 142 tests: four failures, 34 errors, 44 skips and one
  expected failure; the baseline has the same 38 remaining failing tests plus
  the two resolved failures. Dedicated native X20 rendering and archive tests
  run separately with their explicit environment flags.
- Before GitHub publication, embedded IDML image Contents were replaced by
  provenance hashes and lengths in the Dharmabook measurements. The affected
  profile's native rendering checks pass; fonts, runtime geometry and prepared
  resources are unchanged. Unpublished history was compacted to avoid including
  the original 180 MB payload. Original history is backed up locally in the
  ignored `build/prepublish-history.bundle`.

Local proof PDFs are in `build/x20/proofs/<style>/pdf/`; installed specimens
are in `build/x20/installed-specimens/`. They are ignored build artifacts.
The reproducible source archive is `build/package-test/wodtex-m20.zip` (the
existing archive name is retained), containing all 17 classes.

## Scope and source decisions

These classes provide native PDF adaptations of supplied typography, page
geometry and outer decoration, with a shared composition engine for editable
manuscripts. Title/credits/chapter composition and component boxes are native
LaTeX layouts. They are not exhaustive reproductions of alternate illustrated
clan, season or chapter frames. Audited frame exclusions can leave small gaps
in decoration. Each profile records its measurements and genuine-face
substitutions in its `*-source-audit.md` file.

The new profiles support PDF; EPUB, separate cover layouts and foreign-host
element adapters remain unsupported and fail explicitly where selectable.
Existing M20 retains its PDF/EPUB implementation. Its original resources remain
unchanged. The extra Mage Ascension IDML files in Downloads are empty, and
W20 has no supplied IDML; its audit records PDF-derived measurements. KotEK
labels are retained verbatim because their expansion is unconfirmed.

Downloaded fonts and reference PDFs are external inputs, prepared under the
ignored `inputs/profiles/` directory. They are neither modified in Downloads
nor added to the family commits or source archive. See the
[class reference](../X20-Class-Reference.md) for preparation and installation.

## Reproduce final acceptance

```powershell
$env:WODTEX_LUALATEX = "C:/path/to/lualatex.exe"
$env:WODTEX_X20_RENDER = "1"
python -m unittest tests.test_x20_profiles tests.test_x20_installation -v
$env:WODTEX_X20_ARCHIVE = "1"
python -m unittest tests.test_x20_archive -v
```

The archive test uses the supplied Downloads directory by default; set
`WODTEX_X20_SOURCE` to relocate that input. It supplies licensed M20 fonts/art
separately because the source archive deliberately excludes rendering inputs.
