import importlib.util
import unittest
from lxml import etree
from tests.support import ROOT

class ConservationTests(unittest.TestCase):
    def module(self):
        spec=importlib.util.spec_from_file_location('conservation',ROOT/'scripts/verify.py')
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

    def test_marker_only_and_reversed_content_are_rejected(self):
        m=self.module()
        inventory={'unique_tokens':['A-ONE','A-TWO'],'ordered_tokens':['A-ONE','A-TWO'],
                   'passages':['A-ONE. Complete original prose.'],'asides':[],'art':[],'tables':[],'formulas':0}
        valid={'text':'A-ONE. Complete original prose. A-TWO.','asides':[],'art':[],'tables':[],'formulas':0}
        self.assertEqual(m.reconcile(valid,valid,inventory)['errors'],[])
        self.assertTrue(m.reconcile({**valid,'text':'A-ONE A-TWO'},valid,inventory)['errors'])
        self.assertTrue(m.reconcile({**valid,'text':'A-TWO A-ONE. Complete original prose.'},valid,inventory)['errors'])

    def test_formula_mutation_changes_semantic_signature(self):
        m=self.module()
        a=etree.fromstring(b'<math><msup><mi>x</mi><mn>2</mn></msup></math>')
        b=etree.fromstring(b'<math><msup><mi>x</mi><mn>3</mn></msup></math>')
        self.assertNotEqual(m.math_signature(a),m.math_signature(b))

    def test_hyphen_equivalence_requires_a_line_end_and_source_word(self):
        m=self.module()
        self.assertTrue(m.has_passage({'text':'Conserved contin- uation.','raw_text':'Conserved contin-\nuation.'},'Conserved continuation.'))
        self.assertFalse(m.has_passage({'text':'Conserved contin-uation.'},'Conserved continuation.'))
