# vva20-clanbook source mapping

Class: `vva20clanbook`; native PDF. Source reference SHA256: `811f6e7a603ad842c1d4633d3fe7dbb6b36089df4b0c8ae52b43e725bd2beefe`.

Measured page: [603.0, 783.0] bp. Host geometry: `{"top": 64.8, "bottom": 57.6, "inner": 63.0, "outer": 58.550000000000004, "gutter": 12.05, "columns": 2}`.

| Role | Genuine face | Source hash |
| --- | --- | --- |
| body | GoudyOldStyleT-Regular | `380e2cd97160e14042cea52ff785ca92d966e29f873cf2b93e1746f3a582ec74` |
| bold | GoudyOldStyleT-Bold | `f3cd0e13e4a0ed77522b1ab29061da6658f449d1d89b56751cdcdeed86da47e2` |
| italic | GoudyOldStyleT-Italic | `71d2d85781689de6326a229aeba2d143a5b3e8a4f0fc93b75af197fb63bf05bd` |
| heading | UniversityRomanLetPlain | `93728d03a72beda0cc0baae86e5954e33df97d4c70bb258ff7aba26f95b20730` |
| chapter | ChiseledOpen | `63d900b9c1077e70abb85389e39640f4540d571feeed55996d25a5524371b866` |
| bolditalic | GoudyOldStyle-BoldItalic | `577ccf75485cd4088a94be38dcf4c0fff758c8d74b555ce05d7ee3e585dedc36` |

Adaptation decisions and limitations:

- Chapter display is explicitly adapted to 48bp for authored headings; source display size is retained in source measurements.
- Body leading is explicitly resolved to 120% where the IDML style does not store a numeric leading value.
- Interior titles, credits, chapter composition and component boxes are native adaptations; alternate clan/season/chapter variants are not exhaustive pixel replicas.
- PDF-only profile; EPUB and foreign-host explicit element adapters are not implemented.
- Outer frame strips use the supplied reference artwork; decorative sample art and template placeholder content are excluded.

The profile descriptor retains inherited IDML styles and master/spread records where supplied. Source data is private local input, prepared separately; no source PDF/font bytes are included in this branch.
