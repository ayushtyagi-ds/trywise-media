import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));import budget_estimate as b
class Tests(unittest.TestCase):
 def test_canadian_total_includes_fx_tax_and_reserve(self):
  x={'ceiling_cad':50,'cad_per_usd':'1.40','tax_fraction':'0.05','reserve_cad':'5','services':[{'name':'Example','currency':'USD','monthly':'29'}]}
  result=b.estimate(x);self.assertEqual(result['total_with_assumed_tax_and_reserve_cad'],'47.63');self.assertTrue(result['within_ceiling_estimate'])
 def test_rejects_missing_negative_and_nan(self):
  with self.assertRaises(ValueError):b.estimate({'ceiling_cad':50,'cad_per_usd':'NaN','tax_fraction':0,'reserve_cad':0,'services':[{'name':'Example','currency':'CAD','monthly':'2'}]})
