# w20-wyld-west acceptance

Class: `w20wyldwestbook`. Family branch: `x20/werewolf`.

Fresh-archive installed proof: 9 pages, compiled with LuaLaTeX after independently preparing required new-profile inputs. Ordinary installation update preserves all managed and configuration bytes.

Measured paper: 612.0 ? 792.0 bp. Genuine body face: `GoudyOldStyleT-Regular`.

Source PDF SHA256: `4eb115266dee71820340b2430d3cfecd301664dacf7ffa74b60ba28674d165b0`.

The complete source specimen also passed font identity, text conservation, metadata, navigation, measured page-size and index/reference checks. Source mapping and adaptation decisions are in [w20-wyld-west-source-audit.md](w20-wyld-west-source-audit.md).

```powershell
python scripts/build.py --target pdf --source examples/profiles/w20-wyld-west.tex --out build/w20-wyld-west --verify
```

Proof artifacts: `build/x20/archive-proof/w20-wyld-west.pdf` and the per-class entry in `build/x20/archive-proof/report.json`.

See [combined acceptance](Acceptance.md) for reproducible suite commands and remaining unsupported capabilities.
