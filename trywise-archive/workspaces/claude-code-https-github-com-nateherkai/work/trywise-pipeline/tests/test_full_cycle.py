import datetime as dt,json,os,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import trywise,worker,review_server,delivery_loop,post_review_worker
class FakeR2:
 def __init__(self):self.data={}
 def put_object(self,**kw):self.data[kw['Key']]=kw['Body']
class FullCycle(unittest.TestCase):
 def test_review_to_buffer_mocked_only(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);drafts=root/'drafts';drafts.mkdir();dbpath=root/'queue.db';ledger=root/'delivery.db'
   now=dt.datetime(2026,10,31,tzinfo=dt.timezone.utc); db=trywise.connect(dbpath);worker.setup(db);story_id='a'*64
   db.execute('INSERT INTO stories(id,title,url,published_at,source_feed,collected_at) VALUES(?,?,?,?,?,?)',(story_id,'Example','https://blog.google/announcement','2026-10-30T12:00:00+00:00','https://blog.google/rss',now.isoformat()));db.commit()
   job=worker.reserve(db,drafts,{'blog.google'},7,1,now);self.assertIsNotNone(job)
   source=json.loads((Path(__file__).parent/'source.json').read_text());model=json.loads((Path(__file__).parent/'draft-response.json').read_text());capture={'source_url':source['url'],'extract':source['body'],'sha256':'0'*64,'retrieved_at':now.isoformat()}
   with patch.dict(os.environ,{'GEMINI_API_KEY':'fixture-only'}),patch('pipeline_runner.source_capture.capture',return_value=capture),patch('pipeline_runner.draftgen.request_live',return_value=model):
    self.assertEqual(worker.execute(db,job,['blog.google'],'fake',now=now),'review')
   db.close();carousel=Path(job['output_path'])/'carousel';policy={'account_id':'a'*32,'bucket':'test-bucket','public_base':'https://assets.example.com','channel_id':'test-channel','max_posts_per_day':1};client=FakeR2();sent=[]
   def fetch(url,hosts):return client.data['trywise/'+url.rsplit('/',1)[-1]]
   def transport(payload,key):sent.append(payload);return {'data':{'createPost':{'post':{'id':'buffer-fixture'}}}}
   def deliver(carousel,config,ledger,client,key):return post_review_worker.deliver(carousel,config,ledger,client,key,fetch,transport)
   self.assertEqual(delivery_loop.cycle(dbpath,drafts,policy,str(ledger),client,'fake',deliver)['state'],'nothing_ready')
   review_server.write_approval(carousel,review_server.snapshot(carousel)['digest'])
   self.assertEqual(delivery_loop.cycle(dbpath,drafts,policy,str(ledger),client,'fake',deliver)['state'],'buffer_accepted')
   self.assertEqual(delivery_loop.cycle(dbpath,drafts,policy,str(ledger),client,'fake',deliver)['state'],'nothing_ready')
   self.assertEqual(len(sent),1);self.assertEqual(len(client.data),4)
if __name__=='__main__':unittest.main()
