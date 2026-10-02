# v20-clanbook acceptance

Class: `v20clanbook`. Family branch: `x20/vampire`.

Fresh-archive installed proof: 9 pages, compiled with LuaLaTeX after independently preparing required new-profile inputs. Ordinary installation update preserves all managed and configuration bytes.

Measured paper: 603.0 ? 783.0 bp. Genuine body face: `GoudyOldStyleT-Regular`.

Source PDF SHA256: `c5308d00630f790f4313fadadbd2d9162b28259cffb7acdb091310bb1163a5d0`.

The complete source specimen also passed font identity, text conservation, metadata, navigation, measured page-size and index/reference checks. Source mapping and adaptation decisions are in [v20-clanbook-source-audit.md](v20-clanbook-source-audit.md).

```powershell
python scripts/build.py --target pdf --source examples/profiles/v20-clanbook.tex --out build/v20-clanbook --verify
```

Proof artifacts: `build/x20/archive-proof/v20-clanbook.pdf` and the per-class entry in `build/x20/archive-proof/report.json`.

See [combined acceptance](Acceptance.md) for reproducible suite commands and remaining unsupported capabilities.
