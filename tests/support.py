from pathlib import Path
import os
ROOT = Path(__file__).resolve().parents[1]
IDML = Path(os.environ.get('WODTEX_IDML', ROOT/'inputs/M20/M20 Template Interior.idml'))
if not IDML.exists():
    IDML = ROOT.parent/'indesign-sample/template/M20/InDesign/M20 Template Interior/M20 Template Interior.idml'
SOURCE = IDML.parent
