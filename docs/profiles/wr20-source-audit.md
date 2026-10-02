# wr20 source mapping

Class: `wr20book`; native PDF. Source reference SHA256: `24419c73eab5a5c82e530e83c746f5694ea722968dd328d46c1ddb9683292759`.

Measured page: [612.0, 792.0] bp. Host geometry: `{"top": 58.5, "bottom": 81.0, "inner": 63.0, "outer": 63.0, "gutter": 18.0, "columns": 2}`.

| Role | Genuine face | Source hash |
| --- | --- | --- |
| body | GoudyStd | `959235f5890f0acab727b09fbedf50049083a411d8767f0e38ae7d83299698f7` |
| bold | GoudyStd-Bold | `feb16e439ff1bbd5af60e33123d658dac903a211b2ce8c064a0bbc70f43d2574` |
| italic | GoudyStd-Italic | `bd7bf605b6d1e7548047e363a588300f29dab4dac31635204842f754bd4564ab` |
| heading | MatrixTall | `22ea7861bb7dac2b0645bbe3def845e6731f581f928b71c56be8b347977aae84` |
| chapter | WilhelmKlingsporGotisch | `c409008ab513ca5b423ec641b39c8131db46def9742b3941deedeed71faa314a` |
| bolditalic | GoudyStd-BoldItalic | `40db7d660f0f76317228b1f5b9f902cbe01461f4542b03882fb79ff4a4407ae6` |

Adaptation decisions and limitations:

- Chapter display is explicitly adapted to 48bp for authored headings; source display size is retained in source measurements.
- Interior titles, credits, chapter composition and component boxes are native adaptations; alternate clan/season/chapter variants are not exhaustive pixel replicas.
- PDF-only profile; EPUB and foreign-host explicit element adapters are not implemented.
- Outer frame strips use the supplied reference artwork; decorative sample art and template placeholder content are excluded.

The profile descriptor retains inherited IDML styles and master/spread records where supplied. Source data is private local input, prepared separately; no source PDF/font bytes are included in this branch.
