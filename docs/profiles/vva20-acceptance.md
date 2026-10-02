# vva20 acceptance

Class: `vva20book`. Family branch: `x20/vampire`.

Fresh-archive installed proof: 9 pages, compiled with LuaLaTeX after independently preparing required new-profile inputs. Ordinary installation update preserves all managed and configuration bytes.

Measured paper: 603.0 ? 783.0 bp. Genuine body face: `GoudyOldStyleT-Regular`.

Source PDF SHA256: `bd1ca22061721353eb908a7fa3b7ce08b8abe5e50b6b786eeb67b869390d3a43`.

The complete source specimen also passed font identity, text conservation, metadata, navigation, measured page-size and index/reference checks. Source mapping and adaptation decisions are in [vva20-source-audit.md](vva20-source-audit.md).

```powershell
python scripts/build.py --target pdf --source examples/profiles/vva20.tex --out build/vva20 --verify
```

Proof artifacts: `build/x20/archive-proof/vva20.pdf` and the per-class entry in `build/x20/archive-proof/report.json`.

See [combined acceptance](Acceptance.md) for reproducible suite commands and remaining unsupported capabilities.
