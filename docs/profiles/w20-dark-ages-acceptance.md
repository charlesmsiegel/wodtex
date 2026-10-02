# w20-dark-ages acceptance

Class: `w20darkagesbook`. Family branch: `x20/werewolf`.

Fresh-archive installed proof: 9 pages, compiled with LuaLaTeX after independently preparing required new-profile inputs. Ordinary installation update preserves all managed and configuration bytes.

Measured paper: 612.0 ? 792.0 bp. Genuine body face: `GoudyOldStyleBT-Roman`.

Source PDF SHA256: `2a154b58bae1464a75bcdeccfceb8e8768ffaffe8cd752faf250748bb31b397f`.

The complete source specimen also passed font identity, text conservation, metadata, navigation, measured page-size and index/reference checks. Source mapping and adaptation decisions are in [w20-dark-ages-source-audit.md](w20-dark-ages-source-audit.md).

```powershell
python scripts/build.py --target pdf --source examples/profiles/w20-dark-ages.tex --out build/w20-dark-ages --verify
```

Proof artifacts: `build/x20/archive-proof/w20-dark-ages.pdf` and the per-class entry in `build/x20/archive-proof/report.json`.

See [combined acceptance](Acceptance.md) for reproducible suite commands and remaining unsupported capabilities.
