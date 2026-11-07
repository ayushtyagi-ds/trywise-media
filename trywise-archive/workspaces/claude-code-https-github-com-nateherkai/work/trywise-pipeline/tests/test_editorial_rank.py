import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));import editorial_rank as r
class Tests(unittest.TestCase):
 def test_relevance_reasons_are_visible(self):
  developer=r.rank_title('A new developer API for AI coding tools');corporate=r.rank_title('Quarterly investor earnings')
  self.assertGreater(developer['score'],corporate['score']);self.assertIn('developer: +5',developer['reasons'])
 def test_deduplicates_repeated_words_and_empty(self):
  self.assertEqual(r.rank_title('API API')['score'],r.rank_title('API')['score']);self.assertEqual(r.rank_title(None)['score'],0)
