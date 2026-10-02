# kotek20 acceptance

Class: `kotek20book`. Family branch: `x20/eastern`.

Fresh-archive installed proof: 9 pages, compiled with LuaLaTeX after independently preparing required new-profile inputs. Ordinary installation update preserves all managed and configuration bytes.

Measured paper: 603.0 ? 783.0 bp. Genuine body face: `GoudyOldStyleBT-Roman`.

Source PDF SHA256: `156d06127eb21652c62d8093843338ad93e0b86f7b0a36be7adff944833e5092`.

The complete source specimen also passed font identity, text conservation, metadata, navigation, measured page-size and index/reference checks. Source mapping and adaptation decisions are in [kotek20-source-audit.md](kotek20-source-audit.md).

```powershell
python scripts/build.py --target pdf --source examples/profiles/kotek20.tex --out build/kotek20 --verify
```

Proof artifacts: `build/x20/archive-proof/kotek20.pdf` and the per-class entry in `build/x20/archive-proof/report.json`.

See [combined acceptance](Acceptance.md) for reproducible suite commands and remaining unsupported capabilities.
