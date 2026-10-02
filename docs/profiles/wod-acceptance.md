# wod acceptance

Class: `wodbook`. Family branch: `x20/wod`.

Fresh-archive installed proof: 9 pages, compiled with LuaLaTeX after independently preparing required new-profile inputs. Ordinary installation update preserves all managed and configuration bytes.

Measured paper: 612.0 ? 792.0 bp. Genuine body face: `GoudySSi`.

Source PDF SHA256: `eb0a320af9e6d061ed4df32be2e17a1c97e4bed6338a6e611fd2d13db9a1dd0c`.

The complete source specimen also passed font identity, text conservation, metadata, navigation, measured page-size and index/reference checks. Source mapping and adaptation decisions are in [wod-source-audit.md](wod-source-audit.md).

```powershell
python scripts/build.py --target pdf --source examples/profiles/wod.tex --out build/wod --verify
```

Proof artifacts: `build/x20/archive-proof/wod.pdf` and the per-class entry in `build/x20/archive-proof/report.json`.

See [combined acceptance](Acceptance.md) for reproducible suite commands and remaining unsupported capabilities.
