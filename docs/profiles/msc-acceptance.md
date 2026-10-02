# msc acceptance

Class: `mscbook`. Family branch: `x20/mage`.

Fresh-archive installed proof: 9 pages, compiled with LuaLaTeX after independently preparing required new-profile inputs. Ordinary installation update preserves all managed and configuration bytes.

Measured paper: 603.0 ? 783.0 bp. Genuine body face: `Goudy`.

Source PDF SHA256: `0f242318146ede29e0a15f34a00007a2fae64bf586db2e934b62f63c9d3b741f`.

The complete source specimen also passed font identity, text conservation, metadata, navigation, measured page-size and index/reference checks. Source mapping and adaptation decisions are in [msc-source-audit.md](msc-source-audit.md).

```powershell
python scripts/build.py --target pdf --source examples/profiles/msc.tex --out build/msc --verify
```

Proof artifacts: `build/x20/archive-proof/msc.pdf` and the per-class entry in `build/x20/archive-proof/report.json`.

See [combined acceptance](Acceptance.md) for reproducible suite commands and remaining unsupported capabilities.
