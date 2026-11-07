import io,json,os,sqlite3,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));import buffer_metrics as m
class Tests(unittest.TestCase):
 def test_read_only_query_no_secret_in_output_and_persist(self):
  class Resp(io.BytesIO):
   def __enter__(self):return self
   def __exit__(self,*args):self.close()
  class Opener:
   def open(self,req,timeout):
    self.request=req;return Resp(b'{"data":{"post":{"id":"id1","channelId":"c","metrics":[{"name":"reach","value":2}],"metricsUpdatedAt":null}}}')
  op=Opener()
  with patch('urllib.request.build_opener',return_value=op):result=m.get_metrics('id1','fake-secret')
  self.assertNotIn('fake-secret',json.dumps(result));self.assertTrue(json.loads(op.request.data)['query'].startswith('query '))
  with tempfile.TemporaryDirectory() as td:
   path=str(Path(td)/'metrics.db');m.record(path,result)
   with sqlite3.connect(path) as db:self.assertEqual(db.execute('select count(*) from metric_snapshots').fetchone()[0],1)
 def test_missing_key_and_incomplete_response_fail(self):
  with self.assertRaises(ValueError):m.get_metrics('id1','')
  class Resp(io.BytesIO):
   def __enter__(self):return self
   def __exit__(self,*args):self.close()
  class O:
   def open(self,*a,**k):return Resp(b'{"data":{"post":{"id":"other","metrics":[]}}}')
  with patch('urllib.request.build_opener',return_value=O()):
   with self.assertRaises(ValueError):m.get_metrics('id1','fake')
