# w20-wyld-west source mapping

Class: `w20wyldwestbook`; native PDF. Source reference SHA256: `4eb115266dee71820340b2430d3cfecd301664dacf7ffa74b60ba28674d165b0`.

Measured page: [612.0, 792.0] bp. Host geometry: `{"top": 76.5, "bottom": 85.5, "inner": 54.0, "outer": 76.5, "gutter": 12.0024, "columns": 2}`.

| Role | Genuine face | Source hash |
| --- | --- | --- |
| body | GoudyOldStyleT-Regular | `380e2cd97160e14042cea52ff785ca92d966e29f873cf2b93e1746f3a582ec74` |
| bold | GoudyOldStyleT-Bold | `f3cd0e13e4a0ed77522b1ab29061da6658f449d1d89b56751cdcdeed86da47e2` |
| italic | GoudyOldStyleT-Italic | `71d2d85781689de6326a229aeba2d143a5b3e8a4f0fc93b75af197fb63bf05bd` |
| heading | Saddlebag-Black | `f2bcccc784635304a3e31aecda77fcf73319781d2896ded089720aa27e71b04f` |
| chapter | Saddlebag-Black | `f2bcccc784635304a3e31aecda77fcf73319781d2896ded089720aa27e71b04f` |
| bolditalic | GoudyOldStyle-BoldItalic | `577ccf75485cd4088a94be38dcf4c0fff758c8d74b555ce05d7ee3e585dedc36` |

Adaptation decisions and limitations:

- Referenced IFC INSANE RODEO BOLD is absent; chapter display explicitly uses supplied Saddlebag. This is a typography substitution, not exact template fidelity.
- Chapter display is explicitly adapted to 48bp for authored headings; source display size is retained in source measurements.
- Interior titles, credits, chapter composition and component boxes are native adaptations; alternate clan/season/chapter variants are not exhaustive pixel replicas.
- PDF-only profile; EPUB and foreign-host explicit element adapters are not implemented.
- Outer frame strips use the supplied reference artwork; decorative sample art and template placeholder content are excluded.

The profile descriptor retains inherited IDML styles and master/spread records where supplied. Source data is private local input, prepared separately; no source PDF/font bytes are included in this branch.
