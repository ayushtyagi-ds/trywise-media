import hashlib,json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import r2_media as r
import review_server as rev

class FakeClient:
 def __init__(self,fail=False):self.calls=[];self.fail=fail
 def put_object(self,**kwargs):
  self.calls.append(kwargs)
  if self.fail: raise RuntimeError('failure or 412')

class MediaTest(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.d=Path(self.t.name)
  (self.d/'manifest.json').write_text(json.dumps({'status':'needs_review','slides':2,'source':{}}))
  (self.d/'caption.txt').write_text('hello')
  for i in range(1,3):(self.d/f'{i:02}.png').write_bytes(b'\x89PNG\r\n\x1a\n'+bytes([i]))
  rev.write_approval(self.d,rev.snapshot(self.d)['digest'])
 def tearDown(self):self.t.cleanup()
 def plan(self,**kw):return r.plan(self.d,kw.get('account','a'*32),kw.get('bucket','test-bucket'),kw.get('base','https://assets.example.com'))
 def test_plan_is_stable_and_no_remote_io(self):
  p=self.plan();self.assertEqual(p['digest'],self.plan()['digest']);self.assertEqual(len(p['plan']['files']),2)
 def test_mutation_invalidates_approval(self):
  (self.d/'caption.txt').write_text('changed')
  with self.assertRaises(r.MediaError):self.plan()
 def test_hostile_configuration_rejected(self):
  for base in ('http://assets.example.com','https://me:pass@assets.example.com','https://assets.example.com/?secret=1'):
   with self.assertRaises(r.MediaError):self.plan(base=base)
 def test_conditional_creation_and_content_hash(self):
  p=self.plan();client=FakeClient();urls=r.upload(self.d,p,client)
  self.assertEqual(len(urls),2);self.assertTrue(all(c['IfNoneMatch']=='*' for c in client.calls))
  self.assertTrue(all(hashlib.sha256(c['Body']).hexdigest() in c['Key'] for c in client.calls))
 def test_changed_file_fails_before_any_writes(self):
  p=self.plan();(self.d/'02.png').write_bytes(b'bad');c=FakeClient()
  with self.assertRaises(r.MediaError):r.upload(self.d,p,c)
  self.assertEqual(c.calls,[])
 def test_remote_error_does_not_retry(self):
  p=self.plan();c=FakeClient(True)
  with self.assertRaises(r.MediaError):r.upload(self.d,p,c)
  self.assertEqual(len(c.calls),1)
if __name__=='__main__':unittest.main()
