# m20-dark-ages acceptance

Class: `m20darkagesbook`. Family branch: `x20/mage`.

Fresh-archive installed proof: 9 pages, compiled with LuaLaTeX after independently preparing required new-profile inputs. Ordinary installation update preserves all managed and configuration bytes.

Measured paper: 603.0 ? 783.0 bp. Genuine body face: `Goudy`.

Source PDF SHA256: `4b9b2ff5c510f12d2f937839d37dbffb09166a5c063f51ce188db6bbf6eae004`.

The complete source specimen also passed font identity, text conservation, metadata, navigation, measured page-size and index/reference checks. Source mapping and adaptation decisions are in [m20-dark-ages-source-audit.md](m20-dark-ages-source-audit.md).

```powershell
python scripts/build.py --target pdf --source examples/profiles/m20-dark-ages.tex --out build/m20-dark-ages --verify
```

Proof artifacts: `build/x20/archive-proof/m20-dark-ages.pdf` and the per-class entry in `build/x20/archive-proof/report.json`.

See [combined acceptance](Acceptance.md) for reproducible suite commands and remaining unsupported capabilities.
