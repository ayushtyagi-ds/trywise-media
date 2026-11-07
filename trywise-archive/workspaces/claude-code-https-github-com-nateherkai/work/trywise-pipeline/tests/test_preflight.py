import json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));import preflight
class Tests(unittest.TestCase):
 def test_never_returns_secret(self):
  secret='sensitive-fake-token';result=preflight.check({'GEMINI_API_KEY':secret});self.assertTrue(result['checks']['gemini_key_present']);self.assertNotIn(secret,json.dumps(result));self.assertFalse(result['checks']['buffer_key_present'])
 def test_missing_policy_fails_closed(self):
  self.assertFalse(preflight.check({},'/nonexistent/trywise-policy')['checks']['delivery_policy_shape_accepted'])
if __name__=='__main__':unittest.main()
