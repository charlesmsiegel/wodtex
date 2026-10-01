# Original M20 PDF correction source patch

This opt-in checkpoint preserves the local original-template PDF correction code without replacing the current PR defaults. It was reconciled against commit 906befdcc77ee47093c1c6d469da5c34be988438, retaining the newer physical-folio evidence, reference/semantic work, repeated-header sanitization and rule-aware table-width changes.

The default class, runtime, PDF/EPUB adapters and validation code remain unchanged until you explicitly apply this patch. The patch is not a completed framework release. It requires the separately prepared original-template PDF assets and licensed fonts described in docs/M20-layout-corrections.md. No licensed assets or private manuscript are included.

Inspect changes.patch and the two public correction documents first. Run python3 contrib/original-m20-layout/apply.py --check in a disposable checkout of the listed base commit. To apply the source replacements there, run the same command with --apply. The helper refuses changed base files, backs up each replaced source under build/, then installs the reconciled overrides. Do not apply it blindly over later work; merge the patch instead.

The patch includes focused sidebar tests under overrides/tests. Python syntax compilation was checked during publication. Earlier local PDF correction tests and rendered-book checks are described in the correction document; the merged package has not passed the complete current framework acceptance suite, EPUB validation, or full visual review. The PDF-local stat/list/table-lead wrappers still need EPUB adapters, the correction changes chapter-title fitting behavior, and separately extracted decoration is not part of the default asset importer.

The follow-up includes native page-edge horizontal floats, outside-edge adaptive vertical reserves, the bounded table-lead seam correction, strong paragraph endpoint controls, pragmatic body hyphenation, heading hyphenation bans and limited paragraph-glue shrinkage. The experimental m20-art.sty change is excluded; that default module remains unchanged.

The manifest uses exact remote source bytes and the current checkpoint as its base, including extraction scripts already present there. Check/apply was tested on an exact-byte current-source copy. A local combined PDF passed strict overflow verification; final semantic-seam rebuilding and independent visual review were still running when this publication checkpoint was prepared. Full merged PDF/EPUB acceptance remains pending.
