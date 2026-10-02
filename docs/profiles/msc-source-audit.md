# msc source mapping

Class: `mscbook`; native PDF. Source reference SHA256: `0f242318146ede29e0a15f34a00007a2fae64bf586db2e934b62f63c9d3b741f`.

Measured page: [603.0, 783.0] bp. Host geometry: `{"top": 72.0, "bottom": 54.0, "inner": 63.0, "outer": 58.5, "gutter": 12.0, "columns": 2}`.

| Role | Genuine face | Source hash |
| --- | --- | --- |
| body | Goudy | `814c20d013d9328c011c98a69a880aef94522bea3f5262cda888a30dda9a1b74` |
| bold | Goudy-Bold | `6393d53104529d492cd987375d67f53af79b6a78953440955a8cee3e8b5de947` |
| italic | Goudy-Italic | `5189cb0bed1d785894d524405696b55cde4724f10466e569663f2551d29e3b4a` |
| heading | Clairvaux | `c4a89949fa0dd2c23fe97d165a90efe9f39ff86d8a1ca38ce1a98904158e0a02` |
| chapter | Clairvaux | `c4a89949fa0dd2c23fe97d165a90efe9f39ff86d8a1ca38ce1a98904158e0a02` |
| bolditalic | Goudy-Italic | `5189cb0bed1d785894d524405696b55cde4724f10466e569663f2551d29e3b4a` |

Adaptation decisions and limitations:

- No supplied matching bold italic face; nested bold italic explicitly uses the genuine italic face, without synthetic emboldening.
- Chapter display is explicitly adapted to 48bp for authored headings; source display size is retained in source measurements.
- Interior titles, credits, chapter composition and component boxes are native adaptations; alternate clan/season/chapter variants are not exhaustive pixel replicas.
- PDF-only profile; EPUB and foreign-host explicit element adapters are not implemented.
- Outer frame strips use the supplied reference artwork; decorative sample art and template placeholder content are excluded.

The profile descriptor retains inherited IDML styles and master/spread records where supplied. Source data is private local input, prepared separately; no source PDF/font bytes are included in this branch.

- Outlined or raster template labels/folios are excluded by audited normalized frame rectangles. Small gaps in the outer decoration are intentional.
