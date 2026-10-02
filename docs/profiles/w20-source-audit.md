# w20 source mapping

Class: `w20book`; native PDF. Source reference SHA256: `be7d95d055f77d7182b649440fd707086b7205efe8b4078ce582a9c17462af72`.

Measured page: [612.0, 792.0] bp. Host geometry: `{"top": 54.0, "bottom": 54.0, "inner": 63.0, "outer": 54.0, "columns": 2, "gutter": 12.0}`.

| Role | Genuine face | Source hash |
| --- | --- | --- |
| body | GoudyOldStyleT-Regular | `380e2cd97160e14042cea52ff785ca92d966e29f873cf2b93e1746f3a582ec74` |
| bold | GoudyOldStyleT-Bold | `f3cd0e13e4a0ed77522b1ab29061da6658f449d1d89b56751cdcdeed86da47e2` |
| italic | GoudyOldStyleT-Italic | `71d2d85781689de6326a229aeba2d143a5b3e8a4f0fc93b75af197fb63bf05bd` |
| heading | Balthazar | `d15c469565c4ce3a52ef9cdd6b79d0dcd68521d598166055d8c330186f981e7f` |
| chapter | Balthazar | `d15c469565c4ce3a52ef9cdd6b79d0dcd68521d598166055d8c330186f981e7f` |
| bolditalic | GoudyOldStyle-BoldItalic | `577ccf75485cd4088a94be38dcf4c0fff758c8d74b555ce05d7ee3e585dedc36` |

Adaptation decisions and limitations:

- No IDML supplied: page and typography measured from PDF; body margins use the PDF text-frame envelope with explicit two-column composition.
- Interior titles, credits, chapter composition and component boxes are native adaptations; alternate clan/season/chapter variants are not exhaustive pixel replicas.
- PDF-only profile; EPUB and foreign-host explicit element adapters are not implemented.
- Outer frame strips use the supplied reference artwork; decorative sample art and template placeholder content are excluded.

The profile descriptor retains inherited IDML styles and master/spread records where supplied. Source data is private local input, prepared separately; no source PDF/font bytes are included in this branch.
