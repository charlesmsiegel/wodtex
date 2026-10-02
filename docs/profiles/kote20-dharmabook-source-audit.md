# kote20-dharmabook source mapping

Class: `kote20dharmabook`; native PDF. Source reference SHA256: `375c898c7cd6839d20133328a80825d3969d8765099ae6cae14554defd0c3891`.

Measured page: [603.0, 783.0] bp. Host geometry: `{"top": 72.0, "bottom": 67.5, "inner": 54.0, "outer": 72.0, "gutter": 12.0, "columns": 2}`.

| Role | Genuine face | Source hash |
| --- | --- | --- |
| body | GoudyOldStyleT-Regular | `380e2cd97160e14042cea52ff785ca92d966e29f873cf2b93e1746f3a582ec74` |
| bold | GoudyOldStyleT-Bold | `f3cd0e13e4a0ed77522b1ab29061da6658f449d1d89b56751cdcdeed86da47e2` |
| italic | GoudyOldStyleT-Italic | `71d2d85781689de6326a229aeba2d143a5b3e8a4f0fc93b75af197fb63bf05bd` |
| heading | Akira | `f337defbecaf806e96668d5ecfada1f8edc421263df99c2294b42e25bb84a0d9` |
| chapter | Run | `eb8f5495630d2f45e2c8b3283289f4643faf5ea4a92658d16613669f7c929658` |
| bolditalic | GoudyOldStyle-BoldItalic | `577ccf75485cd4088a94be38dcf4c0fff758c8d74b555ce05d7ee3e585dedc36` |

Adaptation decisions and limitations:

- Chapter display is explicitly adapted to 48bp for authored headings; source display size is retained in source measurements.
- Interior titles, credits, chapter composition and component boxes are native adaptations; alternate clan/season/chapter variants are not exhaustive pixel replicas.
- PDF-only profile; EPUB and foreign-host explicit element adapters are not implemented.
- Outer frame strips use the supplied reference artwork; decorative sample art and template placeholder content are excluded.

The profile descriptor retains inherited IDML styles and master/spread records where supplied. Source data is private local input, prepared separately; no source PDF/font bytes are included in this branch.
