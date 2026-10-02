# c20 source mapping

Class: `c20book`; native PDF. Source reference SHA256: `f20b6a3bcc8b62d5297a47c519c921953abf3e9345a91984c95cd8ff78d201f7`.

Measured page: [612.0, 792.0] bp. Host geometry: `{"top": 49.5, "bottom": 63.0, "inner": 49.5, "outer": 54.0, "gutter": 13.5, "columns": 2}`.

| Role | Genuine face | Source hash |
| --- | --- | --- |
| body | GoudyStd | `959235f5890f0acab727b09fbedf50049083a411d8767f0e38ae7d83299698f7` |
| bold | GoudyStd-Bold | `feb16e439ff1bbd5af60e33123d658dac903a211b2ce8c064a0bbc70f43d2574` |
| italic | GoudyStd-Italic | `bd7bf605b6d1e7548047e363a588300f29dab4dac31635204842f754bd4564ab` |
| heading | Kells | `30cb96d65f181162d4041b504885cade77c724ec2f2b08479071ead678d8ebc9` |
| chapter | CasablancaAntiquePlain | `45c6e4e2f1c64f53f16cbc16edfa102cbf3781bb0a51ee2d96bd883d7ee50e3e` |
| bolditalic | GoudyStd-BoldItalic | `40db7d660f0f76317228b1f5b9f902cbe01461f4542b03882fb79ff4a4407ae6` |

Adaptation decisions and limitations:

- Chapter display is explicitly adapted to 48bp for authored headings; source display size is retained in source measurements.
- Interior titles, credits, chapter composition and component boxes are native adaptations; alternate clan/season/chapter variants are not exhaustive pixel replicas.
- PDF-only profile; EPUB and foreign-host explicit element adapters are not implemented.
- Outer frame strips use the supplied reference artwork; decorative sample art and template placeholder content are excluded.

The profile descriptor retains inherited IDML styles and master/spread records where supplied. Source data is private local input, prepared separately; no source PDF/font bytes are included in this branch.
