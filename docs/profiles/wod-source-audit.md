# wod source mapping

Class: `wodbook`; native PDF. Source reference SHA256: `eb0a320af9e6d061ed4df32be2e17a1c97e4bed6338a6e611fd2d13db9a1dd0c`.

Measured page: [612.0, 792.0] bp. Host geometry: `{"top": 45.0, "bottom": 45.0, "inner": 63.0, "outer": 36.0, "gutter": 18.0, "columns": 2}`.

| Role | Genuine face | Source hash |
| --- | --- | --- |
| body | GoudySSi | `df44e44bae4821795218b1b4d3ee914fb1327c9cdb0e43227ec313d95b2618db` |
| bold | GoudySSiBold | `966869e01c542c93e25e7a8fff78e0ddd870e2dd23a94a0a107e8c3fd617f71b` |
| italic | GoudySSiItalic | `0ec0f624f513dd8197954d767908caf0ca66f202811d381802464b5b5d17b488` |
| heading | OPTIProtea | `569a0ac5cee9ccd960cf7edd0fd3786269ebb522818621a112ae18fa173837ae` |
| chapter | OPTIProtea | `569a0ac5cee9ccd960cf7edd0fd3786269ebb522818621a112ae18fa173837ae` |
| bolditalic | GoudySSiBoldItalic | `3f618506f68ccab17d402ac9543ce25ac54f3408817cf3f86bc732ae2948a019` |

Adaptation decisions and limitations:

- Chapter display is explicitly adapted to 48bp for authored headings; source display size is retained in source measurements.
- Interior titles, credits, chapter composition and component boxes are native adaptations; alternate clan/season/chapter variants are not exhaustive pixel replicas.
- PDF-only profile; EPUB and foreign-host explicit element adapters are not implemented.
- Outer frame strips use the supplied reference artwork; decorative sample art and template placeholder content are excluded.

The profile descriptor retains inherited IDML styles and master/spread records where supplied. Source data is private local input, prepared separately; no source PDF/font bytes are included in this branch.
