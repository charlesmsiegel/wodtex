# kotek20 source mapping

Class: `kotek20book`; native PDF. Source reference SHA256: `156d06127eb21652c62d8093843338ad93e0b86f7b0a36be7adff944833e5092`.

Measured page: [603.0, 783.0] bp. Host geometry: `{"top": 81.0, "bottom": 31.5, "inner": 58.45, "outer": 63.0, "gutter": 18.0, "columns": 2}`.

| Role | Genuine face | Source hash |
| --- | --- | --- |
| body | GoudyOldStyleBT-Roman | `ed08f3601307b97d8f1516a89e3939c9a477fca22e6bb7b4470d3803cf7fd288` |
| bold | GoudyOldStyleBT-Bold | `d62b6ee9f289a88e8df7710b7a44d4fbd92c2d41d2ab930616bfce3b41b4acfb` |
| italic | GoudyOldStyleBT-Italic | `b21809f9a1cd07b3ce41b4b41ec30af48e8cd00f86a3e8b98ea4f6b8ac164250` |
| heading | Caesar | `b7ab1b33768f4a4399d837f03b36b3a1e58d1049db72663065c7ad4902697256` |
| chapter | Caesar | `b7ab1b33768f4a4399d837f03b36b3a1e58d1049db72663065c7ad4902697256` |
| bolditalic | GoudyOldStyleBT-Italic | `b21809f9a1cd07b3ce41b4b41ec30af48e8cd00f86a3e8b98ea4f6b8ac164250` |

Adaptation decisions and limitations:

- No supplied matching bold italic face; nested bold italic explicitly uses the genuine italic face, without synthetic emboldening.
- Chapter display is explicitly adapted to 48bp for authored headings; source display size is retained in source measurements.
- Interior titles, credits, chapter composition and component boxes are native adaptations; alternate clan/season/chapter variants are not exhaustive pixel replicas.
- PDF-only profile; EPUB and foreign-host explicit element adapters are not implemented.
- Outer frame strips use the supplied reference artwork; decorative sample art and template placeholder content are excluded.

The profile descriptor retains inherited IDML styles and master/spread records where supplied. Source data is private local input, prepared separately; no source PDF/font bytes are included in this branch.

- Outlined or raster template labels/folios are excluded by audited normalized frame rectangles. Small gaps in the outer decoration are intentional.
