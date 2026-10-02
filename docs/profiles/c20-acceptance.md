# c20 acceptance

Class: `c20book`. Family branch: `x20/changeling`.

Fresh-archive installed proof: 9 pages, compiled with LuaLaTeX after independently preparing required new-profile inputs. Ordinary installation update preserves all managed and configuration bytes.

Measured paper: 612.0 ? 792.0 bp. Genuine body face: `GoudyStd`.

Source PDF SHA256: `f20b6a3bcc8b62d5297a47c519c921953abf3e9345a91984c95cd8ff78d201f7`.

The complete source specimen also passed font identity, text conservation, metadata, navigation, measured page-size and index/reference checks. Source mapping and adaptation decisions are in [c20-source-audit.md](c20-source-audit.md).

```powershell
python scripts/build.py --target pdf --source examples/profiles/c20.tex --out build/c20 --verify
```

Proof artifacts: `build/x20/archive-proof/c20.pdf` and the per-class entry in `build/x20/archive-proof/report.json`.

See [combined acceptance](Acceptance.md) for reproducible suite commands and remaining unsupported capabilities.
