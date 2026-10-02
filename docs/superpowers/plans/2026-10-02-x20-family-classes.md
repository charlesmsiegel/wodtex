# X20 Family Classes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the 17 inventoried native PDF profiles, preserving existing M20 behavior, with each family's changes on a separate Git branch.

**Architecture:** A shared foundation supplies an explicit implemented-profile registry, isolated font/art resolution, neutral IDML parsing, and class-aware installation/build selection. Thin family classes select measured page policies and registered element adapters. Families fork from the tested foundation; an integration branch combines all families without adding one family's implementation to another family's branch.

**Tech Stack:** LaTeX/LuaLaTeX, Python unittest, fontTools, Pillow, PyMuPDF, supplied IDML/INDD/PDF/ZIP references, Git branches/worktrees.

**Spec:** `docs/design/X20-Output-Profiles.md` and `docs/design/Crossover-Style-Architecture.md`.

## Global constraints

- Implement native PDF first; new profiles explicitly reject EPUB until independently implemented. Preserve existing M20 EPUB behavior and its documented limitations.
- Preserve `m20book`, all existing M20 rendering commands, metadata, correction manifests, and ordinary-update configuration bytes.
- Classes own host page policies; explicit element styles retain their identities through nesting, continuations, and deferred output.
- Missing meaningful artwork, unsupported capabilities, and unknown profiles produce actionable errors.
- Measure each template separately in `bp`; do not infer page policy or font roles from shared ancestry or filenames.
- Keep Downloads unchanged. Prepare selected source resources under ignored workspace input directories; do not assume new licensed bytes belong in tracked bundles.
- Runtime profile records contain relative package resources, not machine-specific Downloads paths. The source catalogue remains provenance only.
- Run execution natively in this session. Separate family branches does not imply a request for parallel agents.

## Branch topology and file ownership

| Branch | Profiles/classes | Dependencies |
| --- | --- | --- |
| `x20/foundation` | Shared installer/build/parser/resource support | Current `main`, plus prepared inventory |
| `x20/mage` | Existing `m20book`; `m20darkagesbook`, `mscbook` | Foundation |
| `x20/vampire` | `v20clanbook`, `vva20book`, `vva20clanbook` | Foundation |
| `x20/werewolf` | `w20book`, `w20darkagesbook`, `w20wyldwestbook` | Foundation |
| `x20/changeling` | `c20book`, `darkagesfaebook` | Foundation |
| `x20/demon` | `d20book` | Foundation |
| `x20/wraith` | `wr20book` | Foundation |
| `x20/eastern` | `kote20dharmabook`, `kotek20book`, `kotek20legacybook` | Foundation |
| `x20/wod` | `wodbook` | Foundation |
| `x20/integration` | All family commits and combined regression evidence | All eight families |

Family worktrees live under ignored `.worktrees/<family>/` when isolation is available. Do not overwrite pre-existing branches/worktrees with those names. Commit the approved inventory and this plan as the common starting point. Never merge into `main` or push without a further instruction.

The foundation owns `scripts/profile_registry.py`, `scripts/template_reader.py`, `scripts/prepare_profile.py`, `profiles/registry.json`, `tex/wodtex-profile-core.sty`, and edits to installer/build/package support. Each family owns its root classes, `profiles/<style>.json`, `profiles/<style>.tex`, `tex/wodtex-<style>.sty`, `tex/wodtex-<style>-layout.sty`, `examples/profiles/<style>.tex`, family tests, and provenance/acceptance documents. Family registration is discovered from profile descriptors so unrelated branches do not edit a single shared registration list.

## Review focus

1. Same-named fonts in different packages must resolve to the selected profile's audited bytes.
2. A breakable or deferred foreign element must retain its own style while the host body/page policy remains unchanged.
3. Installing/updating multiple profiles must preserve existing M20 local settings and unrelated files.
4. A manuscript outside the repository, with spaces in its path, must find its class and resources.
5. A ZIP member, missing IDML, or unsupported EPUB request must never silently become an M20 rendering.

## Task 1: Reproducible baseline and shared registry

**Files:** Create `scripts/profile_registry.py`, `profiles/registry.json`, `tests/test_profile_registry.py`; modify `.gitignore` and relevant baseline fixtures.

**Interfaces:** `load_profiles(root: Path) -> dict[str, dict]` validates unique style IDs/classes and reports supported outputs, descriptor/resource paths, and required capabilities. `profile_for_class(root: Path, class_name: str) -> dict` resolves the selected class or raises an actionable error. Descriptors are discovered under `profiles/*.json` using an explicit schema marker; existing measurement JSON is not mistaken for a descriptor.

- [ ] Write failing tests for duplicate IDs/classes, invalid paths, unknown classes, explicit output support, and M20 preservation.
- [ ] Run `python -m unittest tests.test_profile_registry -v`; confirm failures demonstrate absent functionality.
- [ ] Implement validated discovery and an M20 descriptor without changing existing `profiles/m20.json` measurements.
- [ ] Point input-dependent baseline tests to the supplied M20 IDML via `WODTEX_IDML`; retain separate reports for source mismatch versus missing files. Diagnose launcher path failures on Windows before fixing anything.
- [ ] Establish a usable LuaLaTeX runtime or document the concrete external dependency; do not treat skipped rendering checks as acceptance.
- [ ] Run registry and affected baseline tests; commit on `x20/foundation`.

## Task 2: Neutral ingestion and isolated resources

**Files:** Create `scripts/template_reader.py`, `scripts/prepare_profile.py`, `tex/wodtex-profile-core.sty`, `tests/test_template_reader.py`, `tests/test_profile_resources.py`; preserve the legacy M20 preparer contract.

**Interfaces:** `read_idml(path: Path, member: str | None = None) -> dict` returns source hash, document units/dimensions, raw and resolved styles, master/spread records, swatches, and links without assigning M20 roles. `prepare_profile(profile_id: str, source_root: Path, output_root: Path) -> dict` consumes audited role mappings and produces selected, hashed, namespaced resources/provenance. A PDF measurement record is supported for W20 without pretending it came from IDML.

- [ ] Test style inheritance/cycles, ZIP member selection/traversal rejection, document dimensions, genuine font faces, and two profiles with colliding font filenames.
- [ ] Run the new tests and confirm failure before implementation.
- [ ] Implement neutral parsing and explicit role mapping; never hard-code another profile's typography into fallback paths.
- [ ] Add style-scoped font/art path resolution with clear missing-resource errors. Resources are not selected through a mutable global default at shipout.
- [ ] Verify that preparation preserves source hashes/bytes and that the legacy M20 resolver output remains compatible; commit.

## Task 3: Class-aware installation, packaging, and builds

**Files:** Modify `scripts/install.py`, `scripts/build.py`, `scripts/package.py`, `package-manifest.json`; create `tests/test_multi_profile_install.py`, `tests/test_multi_profile_build.py`.

**Interfaces:** Existing command lines remain valid. Add repeatable `--profile STYLE` selection to installation/resource preparation; default installation retains M20. Builder resolves the manuscript's actual registered class and reports its descriptor/measurement hashes. It rejects ambiguous/missing class selection and unsupported output before conversion. Existing M20 configuration remains readable; new per-profile configuration is additive and explicitly configured.

- [ ] Test fresh installation and repeat update of two fixture profiles, all selected class/package files, unchanged M20 config bytes, missing assets, moved roots, unowned-file refusal, and paths containing spaces.
- [ ] Test builder selection from commented/option-bearing documentclass declarations and reject unsupported EPUB without invoking tex4ebook.
- [ ] Run new tests, implement class-aware payload/search-path/configuration support, and use the platform path separator for TeX search paths.
- [ ] Include descriptors/classes/family examples in source archives, preserving licensed-input exclusions.
- [ ] Run `python -m unittest tests.test_multi_profile_install tests.test_multi_profile_build tests.test_install tests.test_package -v`; run M20 native regression checks once runtime is available; commit the foundation.

## Family delivery procedure (Tasks 4–11)

Each task below is an independently reviewable family branch, forked from the completed foundation. Repeat every step for each listed style; the existing M20 profile in Task 5 is a preservation check, not an additional class.

**Interfaces:** Consume the foundation descriptor/resource API. Classes load neutral metadata/author commands, their own page policy, and their adapter; select their registered default with `\wodtexSetClassStyle{STYLE}`. Register the callback signatures already specified in `Crossover-Style-Architecture.md`. Local element implementations may share audited neutral mechanics; they must not load M20 page policy as their host.

- [ ] Audit interior reference pixels/text/font spans and IDML inheritance. Record measured geometry, font roles/faces, heading/body metrics, colors, page backgrounds, opener/frontmatter behavior, sidebars, tables/stat blocks, and art. Inspect cover references separately; record cover support independently from interior title support.
- [ ] Save `docs/profiles/<style>-source-audit.md` and profile measurements. Document any required source-export limitation, absent font face, or reference component requiring a design decision before claiming fidelity.
- [ ] Write `tests/test_<family>_profiles.py` checks for every class's default selection, source-backed measurements, missing inputs, metadata, text conservation, navigation, and resource isolation. Include rendered multi-page continuation and outside-directory install tests.
- [ ] Confirm new-class probes fail before implementation.
- [ ] Prepare only audited required fonts/decorations and provenance under ignored `inputs/profiles/<style>/`; hash-check originals. Keep tracked code/descriptors separate from licensed payloads.
- [ ] Implement each listed class, style profile, page policy, adapter, and example specimen. Generic commands select that class by default; explicitly prefixed rendering keeps its style where supported.
- [ ] Render specimens twice or to bounded reference convergence, inspect PNG previews against reference page types, and verify real font spans, no clipping/missing glyphs, conserved text, and expected page transitions. Probe unsupported cross-style and EPUB combinations for actionable errors.
- [ ] Verify fresh install plus update, run family tests and relevant foundation/M20 checks, and save `docs/profiles/<style>-acceptance.md` with commands, measured results, and actual remaining limitations.
- [ ] Commit family changes only to its branch. Mark a task complete only when its classes/resources/install/build route and native PDF acceptance pass.

### Task 4: General World of Darkness — `x20/wod`

Create `wodbook.cls` and `wod` profile/adapter/layout/example files. Test with `python -m unittest tests.test_wod_profiles -v`. Use the general WoD IDML/PDF pair; this establishes the first foreign host and M20-element isolation proof.

### Task 5: Mage — `x20/mage`

Create `m20darkagesbook.cls` (`m20-dark-ages`) and `mscbook.cls` (`msc`). Compare the two supplied Ascension packages with the retained M20 source before changing any M20 resources. Test with `python -m unittest tests.test_mage_profiles tests.test_generic_book -v`. Preserve current M20 default/prefixed rendering behavior and configuration.

### Task 6: Vampire — `x20/vampire`

Create `v20clanbook.cls`, `vva20book.cls`, and `vva20clanbook.cls` for their matching IDs. Read Victorian clanbook documents/fonts/assets through their exact ZIP members. Test with `python -m unittest tests.test_vampire_profiles -v`. Do not present Masquerade clanbook styling as an absent general V20 sourcebook style.

### Task 7: Werewolf — `x20/werewolf`

Create `w20book.cls`, `w20darkagesbook.cls`, and `w20wyldwestbook.cls`. Derive Apocalypse metrics from supplied PDFs unless an IDML export becomes available; inspect font spans and compare every supported page type. Preserve Dark Ages color distinctions and Wyld West ornamentation. Test with `python -m unittest tests.test_werewolf_profiles -v`.

### Task 8: Changeling and Fae — `x20/changeling`

Create `c20book.cls` and `darkagesfaebook.cls`. Keep independent typography, ornamentation and page policies; shared family grouping is a branch organization choice. Test with `python -m unittest tests.test_changeling_profiles -v`.

### Task 9: Demon — `x20/demon`

Create `d20book.cls` and `d20` files. Test with `python -m unittest tests.test_demon_profiles -v`.

### Task 10: Wraith — `x20/wraith`

Create `wr20book.cls` and `wr20` files; verify asymmetric left/right decorations and chapter frame variants explicitly. Test with `python -m unittest tests.test_wraith_profiles -v`.

### Task 11: Eastern packages — `x20/eastern`

Create `kote20dharmabook.cls`, `kotek20book.cls`, and `kotek20legacybook.cls`. Retain exact package labels for unconfirmed `KotEK20` identity; no invented expanded title. The absent Dharmabook cover PDF does not block interior implementation; mark cover fidelity unverified until a reference export exists. Test with `python -m unittest tests.test_eastern_profiles -v`.

## Task 12: Combined installation and regression acceptance

**Files:** Create `tests/test_all_profiles.py`, `examples/profiles/README.md`, `docs/profiles/Acceptance.md`; update README/installation docs and package manifest as needed.

- [ ] Create `x20/integration` from the foundation and merge all eight tested family branches, resolving descriptor/discovery/manifest interactions without merging into `main`.
- [ ] Assert 17 implemented class/default-style mappings and unique packaged filenames; build and install all profiles together.
- [ ] Run outside-directory compilation with the installed tree for all classes, repeat update, and compare per-style resource hashes/configuration bytes.
- [ ] Run `python -m unittest discover -s tests -t . -v`, separate pre-existing/platform/input-dependent failures from introduced failures, and resolve introduced failures.
- [ ] Verify cross-style resource/typography/page-policy isolation for supported combinations, multiple-page continuations, metadata/navigation, and explicit unsupported-capability errors.
- [ ] Package source and inspect archive contents; verify fresh-unpack preparation/install/build for every family using the supplied local inputs.
- [ ] Complete branch-wide review and publish branch names, commit IDs, specimens, and acceptance results. Do not claim complete fidelity or full EPUB support beyond measured evidence.

## Observed pre-implementation environment

The baseline probe on 2026-10-02 ran 12 tests: four passed, four profile tests errored because the default external M20 IDML path does not exist, and four shell-launcher tests failed on Windows with incorrect/un-normalized script paths. These are pre-existing results, not family implementation regressions. LuaLaTeX/kpsewhich/tex4ebook are absent from the current PATH; Poppler tools are available. One conventional user MiKTeX location could not be inspected due to filesystem permissions, so runtime absence has not been established beyond PATH. Resolve runtime access before visual acceptance; do not install or claim it exists based on speculation.

## Plan review status

The user approved implementing all inventoried profiles with one branch per family. This written implementation plan is ready for review; no product implementation has started. Execution will use the native method, with sequential family work and no subagents unless subsequently requested.
