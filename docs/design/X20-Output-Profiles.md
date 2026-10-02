# X20 template inventory and proposed class architecture

Prepared 2026-10-02 from `C:/Users/charl/Downloads/templates/WOD/X20`.
The inventory originally proposed these classes; all 17 now exist on
`x20/integration`, with each family implemented on its own `x20/*` branch.
See the [class reference](../X20-Class-Reference.md) and
[acceptance results](../profiles/Acceptance.md) for supported behavior.
The accompanying [source catalogue](X20-Template-Catalogue.json) records exact
relative document paths, source hashes, archive members, supplied font filenames,
and linked-asset counts. Original source packages remain in Downloads.

## Available gamelines, sublines, and formats

| Gameline / subline | Supplied format | Proposed style ID | Proposed class | Source readiness |
| --- | --- | --- | --- | --- |
| Mage: The Ascension | Sourcebook | `m20` | `m20book` (existing) | Cover/interior IDML, INDD, PDF; additional INDD-only M20 package |
| Mage: Dark Ages | Sourcebook | `m20-dark-ages` | `m20darkagesbook` | Cover/interior IDML, INDD, PDF |
| Mage: The Sorcerer's Crusade | Sourcebook | `msc` | `mscbook` | Cover/interior IDML, INDD, PDF |
| Vampire: The Masquerade | Clanbook | `v20-clanbook` | `v20clanbook` | Cover/interior IDML, INDD, PDF |
| Vampire: The Victorian Age | Sourcebook | `vva20` | `vva20book` | Cover/interior IDML, INDD, PDF |
| Vampire: The Victorian Age | Clanbook | `vva20-clanbook` | `vva20clanbook` | Cover/interior IDML, INDD, PDF inside two ZIPs; members inspected |
| Werewolf: The Apocalypse | Supplement/sourcebook | `w20` | `w20book` | `W4 InDesign`: cover/interior INDD and PDF; no IDML found |
| Werewolf: Dark Ages | Color supplement | `w20-dark-ages` | `w20darkagesbook` | Cover/interior IDML, INDD, PDF |
| Werewolf: The Wyld West | Supplement | `w20-wyld-west` | `w20wyldwestbook` | Cover/interior IDML, INDD, PDF |
| Changeling: The Dreaming | Sourcebook | `c20` | `c20book` | Cover/interior IDML, INDD, PDF |
| Dark Ages: Fae | Sourcebook | `dark-ages-fae` | `darkagesfaebook` | Cover/interior IDML, INDD, PDF |
| Demon: The Fallen | Sourcebook | `d20` | `d20book` | Cover/interior IDML, INDD, PDF |
| Wraith: The Oblivion | Sourcebook | `wr20` | `wr20book` | Cover/interior IDML, INDD, PDF |
| Kindred of the East (`KotE20` package label) | Dharmabook | `kote20-dharmabook` | `kote20dharmabook` | Cover/interior IDML and INDD; interior PDF; no cover PDF found |
| `KotEK20` (exact supplied label) | Sourcebook | `kotek20` | `kotek20book` | Cover/interior IDML, INDD, PDF |
| `KotEK20` (exact supplied label) | Legacybook | `kotek20-legacybook` | `kotek20legacybook` | Cover/interior IDML, INDD, PDF |
| World of Darkness | General sourcebook | `wod` | `wodbook` | Cover/interior IDML, INDD, PDF |

There are **17 implemented styles**, including the existing M20 style: 16 additions.
Book formats are separate styles where supplied templates differ; clanbooks,
Dharmabooks, and Legacybooks are not counted as separate gamelines.
`KotEK20` is deliberately left unexpanded: filenames and inspected story text
do not establish its full title. Resolve that identity before final public naming.
Dark Ages: Fae retains its own identity rather than being renamed Changeling.
These are names of supplied template packages, not claims about published editions.

The inventory does not contain a separate general V20 sourcebook template,
Vampire: Dark Ages template, or Hunter template. Do not derive those designs from
clanbooks or another line. The two M20 source locations have not been established
as byte-identical or equivalent to the repository's retained reference.

## Recommended implementation approach

Keep the shared author API and immutable renderer registry. Give each candidate
class its own default style and page policy, with a style adapter implementing
the generic commands using measured source typography and decorations.
Reuse internals only where the references show actual common behavior.
This follows [Crossover Style Architecture](Crossover-Style-Architecture.md).

Two alternatives are a single class with a profile option, or independent full
copies of `m20book`. The single class makes selection compact but does not by
itself separate the current global M20 page policy; full copies are quick to
start but duplicate layout machinery and fixes. Thin classes plus adapters
provide the requested class selection while keeping ownership explicit.

Proposed author usage, once a class is implemented:

```tex
\documentclass{c20book}
\title{A Changeling Supplement}
\author{Author}
\begin{document}
\frontmatter
\maketitle
\makecredits
\tableofcontents
\mainmatter
\chapter{First Chapter}
\begin{sidebar}{A Field Note}
The class selects the Changeling renderer.
\end{sidebar}
\end{document}
```

Classes own page size, margins, columns, backgrounds, running matter, chapter
openers, and frontmatter transitions. Adapters own element fonts, colors,
frames, internal metrics, and continuations. Shared metadata remains neutral.
Explicit M20 rendering commands retain M20 meaning; foreign-style elements
must not replace the host's geometry or output routine. Cross-style rendering
requires measured fitting policies and acceptance checks, not automatic inheritance.

## Repository work required before adding the second class

1. **Source measurement:** inspect reference pages and resolve IDML style
   inheritance separately for each source. Audit actual font roles, genuine
   weight/style faces, geometry, colors, decorations, and component variants.
   Fonts in the catalogue are supplied files, not yet approved role mappings.
   Export W20 IDML if practical; otherwise measure its PDFs and document the
   limits. Victorian clanbook ZIP members can be read without unpacking.
2. **Resource ownership:** use per-style font/art directories and configuration
   keys. Many packages contain identical font filenames; equality must be
   established by hashes, not filenames. Select needed assets, retain source
   hashes and notices, and record distribution scope before bundling them.
3. **Class and adapter:** add a thin class, page-policy implementation, and
   `tex/wodtex-<style>.sty` adapter registering actual supported capabilities.
   Define only reference-backed designs. A missing reference component needs
   an explicit design decision. Missing styles/capabilities must fail clearly.
4. **Profile data:** add measured profile JSON/TeX with style-specific names.
   `scripts/prepare_assets.py` currently fixes M20 roles, geometry defaults,
   asset names, and TeX macro names. A different IDML input does not make it a
   generic importer. Separate neutral parsing from M20 role mapping before reuse.
5. **Installation and packaging:** `scripts/install.py` explicitly includes
   only `m20book.cls`, rewrites M20 resource paths, injects local configuration
   into that class, and verifies an M20 bundle. Add an explicit implemented-profile
   registry describing classes, adapters, resources, and supported outputs.
   Keep this source inventory separate from that runtime registry.
   `package-manifest.json` also explicitly lists only `m20book.cls`.
6. **Build selection:** `scripts/build.py` passes output options to `m20book`,
   records `profiles/m20.json`, and uses M20 EPUB config/validation. Select the
   actual entry class and its implemented output adapter. Do not pass an
   unsupported class through M20 conversion and report successful support.
7. **Existing M20 workflow:** preserve `m20book`, prefixed commands, user font/art
   overrides, and ordinary-update config preservation. Keep the base and corrected
   installation paths explicit. Changes to correction overrides require matching
   manifest hashes and patch updates.

## Suggested delivery order and acceptance

Start with the general WoD sourcebook (`wodbook`): it has IDML/PDF references and
is already the next host envisioned by the crossover guide. Then implement
Sorcerer's Crusade (`mscbook`), followed by one representative style from each
remaining family. Treat historical and specialized book formats individually;
shared ancestry does not establish identical layout. Schedule W20 after its
INDD-only measurement/export path is settled. Confirm `KotEK20` naming before
publishing those class names.

For every class, render a specimen containing title, credits, short and long
TOCs, chapter spreads, prose/headings/lists, narrow and wide continued sidebars,
tables, stat blocks, art, references, and index where supported. Compare PDF
pixels, dimensions, font spans, conserved text, and navigation to its reference.
Verify fresh installation and update from an unrelated manuscript directory.
Run M20 regressions and mixed-style isolation/continuation checks for each
supported cross-style combination. Test unsupported capability errors.
PDF acceptance and EPUB acceptance are separate; begin with reference-backed
native PDF classes and explicitly defer EPUB until mappings and checks exist.

The architecture and delivery notes above preserve the original preparation
proposal. The subsequent implementation uses a descriptor registry, neutral
IDML reader, separate preparation and native PDF builder, and generalized
installer/package payload. Current supported behavior and validation are in
[the acceptance record](../profiles/Acceptance.md).
