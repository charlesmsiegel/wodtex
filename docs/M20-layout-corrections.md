# M20 PDF layout correction checkpoint

These changes record a local PDF layout review. They are a correction checkpoint, not a claim that every framework output or acceptance test has been revalidated.

## Decorative input preparation

Licensed fonts, original template files, rendered art and manuscript inputs are not included. Supply licensed inputs locally. The extraction scripts use PyMuPDF and a pinned original reference PDF checksum to prevent accidentally mixing a different template revision.

`extract_template_art.py TEMPLATE.pdf --out assets` extracts the original closed-page border and chapter-opening panel. `extract_spread_and_page_types.py TEMPLATE.pdf --out assets` extracts ordinary facing-page spread halves, interior title/sidebar backgrounds and both half-page art frames. Source image bytes, color spaces, clipping and gradients are retained in PDF assets. Ordinary spread halves are distinct left/right crops, not mirrored closed-page borders.

## PDF behavior in this checkpoint

- Original full-page title background, gold title text, separate cover workflow and source-positioned credits helper
- Ordinary outer spread borders, dedicated chapter opening panel, deliberate chapter-facing blank versos and alternating book/chapter footer runners
- Compact shaded hanging lists and purple keyed stat blocks; pipe separators within stat entries display as new lines without changing table syntax
- Short standalone full-width tables use native top/bottom floats; long tables retain repeated-header owner pagination; contained tables remain in sidebars
- A bounded table-lead wrapper keeps existing caption, introductory prose and table together in one float, rather than duplicating or losing those tokens
- Sidebar prose/table bands on a page share one continuous frame; short sidebars keep together when they fit a full region; long content continues across pages
- Modest external sidebar clearance and strong paragraph endpoint safeguards, reapplied after body restarts and headings; explicit manual overrides remain supported
- Horizontal reserves queue as native top/bottom-only wide floats; vertical reserves default to the outside edge, with page-local column reversal and a substantial live-height side region
- Strong but finite body hyphenation penalties, high consecutive-hyphen demerits and optional installed microtype; automatic and authored-hyphen line breaks are prohibited in heading styles

## Authoring migration notes

Use `m20statblock` with `mTwentyStatEntry` for existing keyed summaries. Use the bounded `m20tablelead` wrapper around an existing title/lead/table group when their association must survive floating. These wrappers preserve source text and anchors; they are layout helpers, not a content-schema rewrite.

Use `mTwentyInteriorTitle` and `mTwentyInteriorCredits` for the corresponding front-matter leaves. Put actual existing attribution text in the credits helper; it does not invent legal or authorship text. An original back-cover asset is not synthesized.

The new wrappers are currently PDF-local. EPUB mapping and semantic adapters for these wrappers have not been implemented or claimed validated in this correction pass.

## Verification and remaining refinements

Focused PDF tests cover sidebar endpoint safeguards, one-frame-per-page composition, native table packing, repeated headers, once-only notes/anchors and table-lead association. A complete local book was raster-reviewed and all checked narrative blocks, cells and original anchors were confirmed present. The broad framework suite has independent runtime/font/legacy-expectation failures and is not claimed fully green by this correction checkpoint.

The page-edge art, body/heading hyphenation controls and body-restart whitespace correction are implemented. The bounded table-lead float stays inside live columns, rather than closing and balancing prose merely to enqueue a table. Vertical frames use the actual live column region so a short preceding paragraph or queued top table does not create an oversized reserve. Chapter-facing intentional blank pages remain unchanged.

The latest local PDF build passes strict overflow verification. Focused art-edge and sidebar endpoint/page-frame tests have run. Full merged PDF/EPUB acceptance remains pending; these PDF-local wrappers still need an EPUB adapter before they may be claimed portable.

### Practical manual adjustments

For exceptional heading words or dense table headers, allocate enough column width for the whole word. The heading policy wraps at spaces without altering authored text. Body regions call `mTwentyParagraphControls`; a book may deliberately redefine that hook to tune its house policy. Routine paragraphs allow at most 0.4bp shrinkage of the template's 1.44bp paragraph clearance, avoiding a forced extra line without inflating whitespace. Explicit `inner` vertical placement remains available when outside placement is unsuitable; `outer` is the default.
