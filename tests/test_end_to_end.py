import importlib.util
import json
import subprocess
import unittest
from tests.support import ROOT

class EndToEndTests(unittest.TestCase):
    def test_shared_specimen_conserves_semantics_and_actual_placement(self):
        out=ROOT/'build/specimen'
        p=subprocess.run(['python3','scripts/build.py','--target','all','--source','examples/specimen.tex','--out',str(out),'--verify'],cwd=ROOT,text=True,capture_output=True,timeout=360)
        self.assertEqual(p.returncode,0,p.stdout[-6000:]+p.stderr)
        report=json.loads((out/'build-report.json').read_text())
        pdf=report['targets']['pdf']['verification'];epub=report['targets']['epub']['verification']
        spec=importlib.util.spec_from_file_location('m20verify',ROOT/'scripts/verify.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
        inventory=json.loads((ROOT/'examples/content/inventory.json').read_text())
        conservation=v.reconcile(pdf,epub,inventory)
        self.assertEqual(conservation['errors'],[])
        for ident in ['here-narrow','here-wide1','here-wide2']:
            anchor=next(r for r in pdf['positions'] if r['id']==ident+'-anchor')
            frame=next(r for r in pdf['positions'] if r['id']==ident)
            self.assertEqual(anchor['page'],frame['page'])
            self.assertLess(abs(anchor['y']-frame['y']),32)
        for ident in ['long-narrow','long-wide1','long-wide2']:
            self.assertGreaterEqual(sum(r['id']==ident and r['kind']=='sidebar' for r in pdf['positions']),2)
        (out/'verification-report.json').write_text(json.dumps(conservation,indent=2)+'\n')
