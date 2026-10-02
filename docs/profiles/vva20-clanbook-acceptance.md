# vva20-clanbook acceptance

Class: `vva20clanbook`. Family branch: `x20/vampire`.

Fresh-archive installed proof: 9 pages, compiled with LuaLaTeX after independently preparing required new-profile inputs. Ordinary installation update preserves all managed and configuration bytes.

Measured paper: 603.0 ? 783.0 bp. Genuine body face: `GoudyOldStyleT-Regular`.

Source PDF SHA256: `811f6e7a603ad842c1d4633d3fe7dbb6b36089df4b0c8ae52b43e725bd2beefe`.

The complete source specimen also passed font identity, text conservation, metadata, navigation, measured page-size and index/reference checks. Source mapping and adaptation decisions are in [vva20-clanbook-source-audit.md](vva20-clanbook-source-audit.md).

```powershell
python scripts/build.py --target pdf --source examples/profiles/vva20-clanbook.tex --out build/vva20-clanbook --verify
```

Proof artifacts: `build/x20/archive-proof/vva20-clanbook.pdf` and the per-class entry in `build/x20/archive-proof/report.json`.

See [combined acceptance](Acceptance.md) for reproducible suite commands and remaining unsupported capabilities.
