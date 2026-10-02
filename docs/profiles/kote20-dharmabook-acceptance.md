# kote20-dharmabook acceptance

Class: `kote20dharmabook`. Family branch: `x20/eastern`.

Fresh-archive installed proof: 9 pages, compiled with LuaLaTeX after independently preparing required new-profile inputs. Ordinary installation update preserves all managed and configuration bytes.

Measured paper: 603.0 ? 783.0 bp. Genuine body face: `GoudyOldStyleT-Regular`.

Source PDF SHA256: `375c898c7cd6839d20133328a80825d3969d8765099ae6cae14554defd0c3891`.

The complete source specimen also passed font identity, text conservation, metadata, navigation, measured page-size and index/reference checks. Source mapping and adaptation decisions are in [kote20-dharmabook-source-audit.md](kote20-dharmabook-source-audit.md).

```powershell
python scripts/build.py --target pdf --source examples/profiles/kote20-dharmabook.tex --out build/kote20-dharmabook --verify
```

Proof artifacts: `build/x20/archive-proof/kote20-dharmabook.pdf` and the per-class entry in `build/x20/archive-proof/report.json`.

See [combined acceptance](Acceptance.md) for reproducible suite commands and remaining unsupported capabilities.
