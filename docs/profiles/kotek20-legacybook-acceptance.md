# kotek20-legacybook acceptance

Class: `kotek20legacybook`. Family branch: `x20/eastern`.

Fresh-archive installed proof: 9 pages, compiled with LuaLaTeX after independently preparing required new-profile inputs. Ordinary installation update preserves all managed and configuration bytes.

Measured paper: 603.0 ? 783.0 bp. Genuine body face: `GoudyOldStyleBT-Roman`.

Source PDF SHA256: `94d102c21b5b32de3f81dfc657ded5e3ab2c18be463c588065f4d5a0a0df3adb`.

The complete source specimen also passed font identity, text conservation, metadata, navigation, measured page-size and index/reference checks. Source mapping and adaptation decisions are in [kotek20-legacybook-source-audit.md](kotek20-legacybook-source-audit.md).

```powershell
python scripts/build.py --target pdf --source examples/profiles/kotek20-legacybook.tex --out build/kotek20-legacybook --verify
```

Proof artifacts: `build/x20/archive-proof/kotek20-legacybook.pdf` and the per-class entry in `build/x20/archive-proof/report.json`.

See [combined acceptance](Acceptance.md) for reproducible suite commands and remaining unsupported capabilities.
