# d20 acceptance

Class: `d20book`. Family branch: `x20/demon`.

Fresh-archive installed proof: 9 pages, compiled with LuaLaTeX after independently preparing required new-profile inputs. Ordinary installation update preserves all managed and configuration bytes.

Measured paper: 603.0 ? 783.0 bp. Genuine body face: `Goudy`.

Source PDF SHA256: `e6172056f3896cf589ae348c725fd5a2424e40d2a72bdd5f13373645c7398fd4`.

The complete source specimen also passed font identity, text conservation, metadata, navigation, measured page-size and index/reference checks. Source mapping and adaptation decisions are in [d20-source-audit.md](d20-source-audit.md).

```powershell
python scripts/build.py --target pdf --source examples/profiles/d20.tex --out build/d20 --verify
```

Proof artifacts: `build/x20/archive-proof/d20.pdf` and the per-class entry in `build/x20/archive-proof/report.json`.

See [combined acceptance](Acceptance.md) for reproducible suite commands and remaining unsupported capabilities.
