# X20 implementation acceptance

Completed 2026-10-02. `x20/integration` combines all eight family branches;
`main` remains at the original baseline. No branches were pushed.

| Family branch | Implemented styles |
| --- | --- |
| `x20/mage` | Existing M20, M20 Dark Ages, Mage: The Sorcerers Crusade |
| `x20/vampire` | V20 clanbook, Victorian Age V20, Victorian clanbook |
| `x20/werewolf` | W20, W20 Dark Ages, W20 Wyld West |
| `x20/changeling` | C20, Dark Ages Fae |
| `x20/demon` | D20 |
| `x20/wraith` | Wr20 |
| `x20/eastern` | KotE20 dharmabook, KotEK20, KotEK20 legacybook |
| `x20/wod` | General World of Darkness sourcebook |

Every family starts from `x20/foundation` and includes the final shared fixes.
Family branches contain their own classes, descriptors, specimens and source
audits. The integration branch adds the complete inventory acceptance tests.
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
