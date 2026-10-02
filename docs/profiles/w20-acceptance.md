# w20 acceptance

Class: `w20book`. Family branch: `x20/werewolf`.

Fresh-archive installed proof: 9 pages, compiled with LuaLaTeX after independently preparing required new-profile inputs. Ordinary installation update preserves all managed and configuration bytes.

Measured paper: 612.0 ? 792.0 bp. Genuine body face: `GoudyOldStyleT-Regular`.

Source PDF SHA256: `be7d95d055f77d7182b649440fd707086b7205efe8b4078ce582a9c17462af72`.

The complete source specimen also passed font identity, text conservation, metadata, navigation, measured page-size and index/reference checks. Source mapping and adaptation decisions are in [w20-source-audit.md](w20-source-audit.md).

```powershell
python scripts/build.py --target pdf --source examples/profiles/w20.tex --out build/w20 --verify
```

Proof artifacts: `build/x20/archive-proof/w20.pdf` and the per-class entry in `build/x20/archive-proof/report.json`.

See [combined acceptance](Acceptance.md) for reproducible suite commands and remaining unsupported capabilities.
