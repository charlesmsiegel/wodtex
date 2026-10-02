# w20-dark-ages source mapping

Class: `w20darkagesbook`; native PDF. Source reference SHA256: `2a154b58bae1464a75bcdeccfceb8e8768ffaffe8cd752faf250748bb31b397f`.

Measured page: [612.0, 792.0] bp. Host geometry: `{"top": 57.96, "bottom": 85.5, "inner": 54.0, "outer": 58.5, "gutter": 12.0, "columns": 2}`.

| Role | Genuine face | Source hash |
| --- | --- | --- |
| body | GoudyOldStyleBT-Roman | `ed08f3601307b97d8f1516a89e3939c9a477fca22e6bb7b4470d3803cf7fd288` |
| bold | GoudyOldStyleBT-Bold | `d62b6ee9f289a88e8df7710b7a44d4fbd92c2d41d2ab930616bfce3b41b4acfb` |
| italic | GoudyOldStyleBT-Italic | `b21809f9a1cd07b3ce41b4b41ec30af48e8cd00f86a3e8b98ea4f6b8ac164250` |
| heading | DSUncialFunnyHand-Medium | `6f1d5baf4d2bceb806ebda1437f6cbc216d647fc42fec719f8f8cb1f14d0e570` |
| chapter | WilhelmKlingspor | `a6fc8034f33bb48dc0f13f65a547abe56f0d8b172c8366b7607af4471d7a5a37` |
| bolditalic | GoudyOldStyleBT-Italic | `b21809f9a1cd07b3ce41b4b41ec30af48e8cd00f86a3e8b98ea4f6b8ac164250` |

Adaptation decisions and limitations:

- chapter uses the genuine WilhelmKlingspor face from another supplied package: Vampire the Masquerade 20th Anniversary Edition Clanbooks/Cover/Document fonts/[Giovanni, Ventrue] Wilkli.TTF
- No supplied matching bold italic face; nested bold italic explicitly uses the genuine italic face, without synthetic emboldening.
- Chapter display is explicitly adapted to 48bp for authored headings; source display size is retained in source measurements.
- Interior titles, credits, chapter composition and component boxes are native adaptations; alternate clan/season/chapter variants are not exhaustive pixel replicas.
- PDF-only profile; EPUB and foreign-host explicit element adapters are not implemented.
- Outer frame strips use the supplied reference artwork; decorative sample art and template placeholder content are excluded.

The profile descriptor retains inherited IDML styles and master/spread records where supplied. Source data is private local input, prepared separately; no source PDF/font bytes are included in this branch.
