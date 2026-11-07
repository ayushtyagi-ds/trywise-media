import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));import analytics
class AnalyticsTests(unittest.TestCase):
 def test_aggregates_and_zero_reach(self):
  rows=[dict(format='tip',reach='100',saves='3',shares='2',profile_visits='5',post_follows='1'),dict(format='news',reach='0',saves='0',shares='0',profile_visits='0',post_follows='0')]
  groups=analytics.analyze(rows)['groups'];self.assertIsNone(groups[0]['saves_per_1000_reach']);self.assertEqual(groups[1]['saves_per_1000_reach'],30)
 def test_missing_and_negative_not_zero(self):
  with self.assertRaises(ValueError):analytics.analyze([dict(format='tip',reach='100',saves='',shares='0',profile_visits='0',post_follows='-1')])
