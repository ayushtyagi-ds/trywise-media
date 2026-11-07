import json,tempfile,unittest,sys,sqlite3
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));import post_review_worker as w,review_server as r
PNG=b'\x89PNG\r\n\x1a\nhello'
class Client:
 def __init__(self):self.data={}
 def put_object(self,**k):self.data[k['Key']]=k['Body']
class Tests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.path=Path(self.t.name);self.c=self.path/'carousel';self.c.mkdir();(self.c/'01.png').write_bytes(PNG);(self.c/'caption.txt').write_text('caption');(self.c/'manifest.json').write_text(json.dumps({'status':'needs_review','slides':1,'source':{}}));r.write_approval(self.c,r.snapshot(self.c)['digest']);self.cfg={'account_id':'a'*32,'bucket':'test-bucket','public_base':'https://assets.example.com','channel_id':'test','max_posts_per_day':1};self.client=Client();self.db=str(self.path/'ledger.sqlite3')
 def tearDown(self):self.t.cleanup()
 def fetch(self,url,allowed):return self.client.data[url.split('/trywise/')[1] and 'trywise/'+url.split('/trywise/')[1]]
 def test_end_to_end_and_duplicate_block(self):
  calls=[]
  def send(payload,key):calls.append(payload);return {'data':{'createPost':{'post':{'id':'one'}}}}
  result=w.deliver(self.c,self.cfg,self.db,self.client,'fake',self.fetch,send)
  self.assertEqual(result['state'],'buffer_accepted');self.assertEqual(len(calls),1)
  with self.assertRaises(ValueError):w.deliver(self.c,self.cfg,self.db,self.client,'fake',self.fetch,send)
  self.assertEqual(len(calls),1)
 def test_ambiguous_fails_closed(self):
  def send(*a):raise TimeoutError('unknown')
  result=w.deliver(self.c,self.cfg,self.db,self.client,'fake',self.fetch,send)
  self.assertEqual(result['state'],'needs_reconciliation')
  with self.assertRaises(ValueError):w.deliver(self.c,self.cfg,self.db,self.client,'fake',self.fetch,send)
 def test_unapproved_never_uploads(self):
  (self.c/'caption.txt').write_text('changed')
  with self.assertRaises(ValueError):w.deliver(self.c,self.cfg,self.db,self.client,'fake',self.fetch,lambda *a:{})
  self.assertEqual(self.client.data,{})
 def test_policy_requires_explicit_authorization(self):
  p=self.path/'policy.json';p.write_text(json.dumps(self.cfg))
  with self.assertRaises(ValueError):w.config_load(p)
