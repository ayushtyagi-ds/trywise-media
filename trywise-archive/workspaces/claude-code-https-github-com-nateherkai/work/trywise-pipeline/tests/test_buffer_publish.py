import os,sys,sqlite3,tempfile,threading,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import buffer_publish as p
import buffer_adapter as a
M={'channel_id':'test-channel','caption':'A post','image_urls':['https://example.com/1.png','https://example.com/2.png']}
class PublishTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.path=os.path.join(self.tmp.name,'ledger.sqlite');self.db=p.database(self.path);self.digest=a.manifest_digest(M);self.calls=0
 def tearDown(self):self.db.close();self.tmp.cleanup()
 def success(self,payload,key):
  self.calls+=1;return {'data':{'createPost':{'post':{'id':'abc','dueAt':'2026-11-01T00:00:00Z'}}}}
 def test_preview_payload_correct(self):
  r=p.send(self.db,M,self.digest,'secret',self.success)
  self.assertEqual(r['state'],'confirmed');self.assertEqual(r['buffer_post_id'],'abc');self.assertEqual(self.calls,1)
  with self.assertRaises(ValueError):p.send(self.db,M,self.digest,'secret',self.success)
  self.assertEqual(self.calls,1)
 def test_mutation_failure_is_never_retried(self):
  r=p.send(self.db,M,self.digest,'secret',lambda *_:{'data':{'createPost':{'message':'bad input'}}})
  self.assertEqual(r['state'],'rejected')
  with self.assertRaises(ValueError):p.send(self.db,M,self.digest,'secret',self.success)
 def test_ambiguous_timeout_blocks_retry(self):
  def timeout(*_):raise TimeoutError('private-token')
  r=p.send(self.db,M,self.digest,'secret',timeout);self.assertEqual(r['state'],'unknown');self.assertNotIn('secret',str(r))
  with self.assertRaises(ValueError):p.send(self.db,M,self.digest,'secret',self.success)
 def test_changed_caption_or_channel_fails_approval(self):
  for changed in ({**M,'caption':'changed'},{**M,'channel_id':'other'},{**M,'image_urls':['https://example.com/a.png']}):
   with self.assertRaises(ValueError):p.send(self.db,changed,self.digest,'secret',self.success)
  self.assertEqual(self.calls,0)
 def test_missing_key_fails_before_reserve(self):
  with self.assertRaises(ValueError):p.send(self.db,M,self.digest,None,self.success)
  self.assertEqual(self.db.execute('select count(*) from submissions').fetchone()[0],0)
 def test_persistent_pending_blocks_next_process(self):
  p.reserve(self.db,M,self.digest);other=p.database(self.path)
  try:
   with self.assertRaises(ValueError):p.send(other,M,self.digest,'secret',self.success)
  finally:other.close()
 def test_memory_database_rejected(self):
  with self.assertRaises(ValueError):p.database(':memory:')
 def test_concurrent_same_digest_once(self):
  gate=threading.Barrier(2); results=[];lock=threading.Lock()
  def run():
   db=p.database(self.path)
   try:
    gate.wait()
    try:res=p.send(db,M,self.digest,'secret',self.success)
    except ValueError:res='blocked'
    with lock:results.append(res)
   finally:db.close()
  ts=[threading.Thread(target=run) for _ in range(2)]
  for t in ts:t.start()
  for t in ts:t.join()
  self.assertEqual(self.calls,1);self.assertEqual(len(results),2);self.assertIn('blocked',results)
if __name__=='__main__':unittest.main()
