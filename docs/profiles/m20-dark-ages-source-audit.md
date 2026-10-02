# m20-dark-ages source mapping

Class: `m20darkagesbook`; native PDF. Source reference SHA256: `4b9b2ff5c510f12d2f937839d37dbffb09166a5c063f51ce188db6bbf6eae004`.

Measured page: [603.0, 783.0] bp. Host geometry: `{"top": 61.2, "bottom": 61.2, "inner": 54.0, "outer": 82.8, "gutter": 12.0, "columns": 2}`.

| Role | Genuine face | Source hash |
| --- | --- | --- |
| body | Goudy | `814c20d013d9328c011c98a69a880aef94522bea3f5262cda888a30dda9a1b74` |
| bold | Goudy-Bold | `6393d53104529d492cd987375d67f53af79b6a78953440955a8cee3e8b5de947` |
| italic | Goudy-Italic | `5189cb0bed1d785894d524405696b55cde4724f10466e569663f2551d29e3b4a` |
| heading | Solemnity | `3b7fd9561dfb8131fe43d35fad7fc2016f5f623a64d645471b89ee4c1632c00a` |
| chapter | Solemnity | `3b7fd9561dfb8131fe43d35fad7fc2016f5f623a64d645471b89ee4c1632c00a` |
| bolditalic | Goudy-Italic | `5189cb0bed1d785894d524405696b55cde4724f10466e569663f2551d29e3b4a` |

Adaptation decisions and limitations:

- No supplied matching bold italic face; nested bold italic explicitly uses the genuine italic face, without synthetic emboldening.
- Chapter display is explicitly adapted to 48bp for authored headings; source display size is retained in source measurements.
- Interior titles, credits, chapter composition and component boxes are native adaptations; alternate clan/season/chapter variants are not exhaustive pixel replicas.
- PDF-only profile; EPUB and foreign-host explicit element adapters are not implemented.
- Outer frame strips use the supplied reference artwork; decorative sample art and template placeholder content are excluded.

The profile descriptor retains inherited IDML styles and master/spread records where supplied. Source data is private local input, prepared separately; no source PDF/font bytes are included in this branch.
