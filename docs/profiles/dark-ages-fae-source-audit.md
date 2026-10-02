# dark-ages-fae source mapping

Class: `darkagesfaebook`; native PDF. Source reference SHA256: `1f6e48441ee1a3d5c6f523e3a8092c51797cfbdb32e7caaf8ddd6e67e26d6082`.

Measured page: [615.9685039370079, 789.1653543307086] bp. Host geometry: `{"top": 53.85826771653544, "bottom": 65.19685039370079, "inner": 62.36220472440945, "outer": 58.0, "gutter": 12.0, "columns": 2}`.

| Role | Genuine face | Source hash |
| --- | --- | --- |
| body | GoudyOldStyleT-Regular | `380e2cd97160e14042cea52ff785ca92d966e29f873cf2b93e1746f3a582ec74` |
| bold | GoudyOldStyleT-Bold | `f3cd0e13e4a0ed77522b1ab29061da6658f449d1d89b56751cdcdeed86da47e2` |
| italic | GoudyOldStyleT-Italic | `71d2d85781689de6326a229aeba2d143a5b3e8a4f0fc93b75af197fb63bf05bd` |
| heading | GaisericDemo | `c82c0d015f22bce0f8d0b1f19b614c59e588a339d5fdb031f0c3fa3d9449e6e2` |
| chapter | Mordred-Bold | `93b06397a2fa8de93c5ad850cf140f0a36a273f4d3822b3d4066f9990cc13f56` |
| bolditalic | GoudyOldStyle-BoldItalic | `577ccf75485cd4088a94be38dcf4c0fff758c8d74b555ce05d7ee3e585dedc36` |

Adaptation decisions and limitations:

- Body leading is explicitly resolved to 120% where the IDML style does not store a numeric leading value.
- Interior titles, credits, chapter composition and component boxes are native adaptations; alternate clan/season/chapter variants are not exhaustive pixel replicas.
- PDF-only profile; EPUB and foreign-host explicit element adapters are not implemented.
- Outer frame strips use the supplied reference artwork; decorative sample art and template placeholder content are excluded.

The profile descriptor retains inherited IDML styles and master/spread records where supplied. Source data is private local input, prepared separately; no source PDF/font bytes are included in this branch.
