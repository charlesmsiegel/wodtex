# wr20 acceptance

Class: `wr20book`. Family branch: `x20/wraith`.

Fresh-archive installed proof: 9 pages, compiled with LuaLaTeX after independently preparing required new-profile inputs. Ordinary installation update preserves all managed and configuration bytes.

Measured paper: 612.0 ? 792.0 bp. Genuine body face: `GoudyStd`.

Source PDF SHA256: `24419c73eab5a5c82e530e83c746f5694ea722968dd328d46c1ddb9683292759`.

The complete source specimen also passed font identity, text conservation, metadata, navigation, measured page-size and index/reference checks. Source mapping and adaptation decisions are in [wr20-source-audit.md](wr20-source-audit.md).

```powershell
python scripts/build.py --target pdf --source examples/profiles/wr20.tex --out build/wr20 --verify
```

Proof artifacts: `build/x20/archive-proof/wr20.pdf` and the per-class entry in `build/x20/archive-proof/report.json`.

See [combined acceptance](Acceptance.md) for reproducible suite commands and remaining unsupported capabilities.
