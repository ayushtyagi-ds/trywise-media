import json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import review_server as review, reviewed_publish as publisher
PNG=b'\x89PNG\r\n\x1a\nreviewed slide'
class ReviewedPublishTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.path=Path(self.temp.name);self.carousel=self.path/'carousel';self.carousel.mkdir()
  (self.carousel/'01.png').write_bytes(PNG)
  (self.carousel/'caption.txt').write_text('A reviewed caption')
  (self.carousel/'manifest.json').write_text(json.dumps({'status':'needs_review','slides':1,'source':{'title':'Example'}}))
  review.write_approval(self.carousel,review.snapshot(self.carousel)['digest'])
  self.spec={'channel_id':'test-channel','image_urls':['https://cdn.example.com/slide.png']}
  self.fetch=lambda u,h:PNG
  self.digest=publisher.prepare(self.carousel,self.spec,{'cdn.example.com'},self.fetch)['_review_verification']['buffer_manifest_digest']
  self.db=str(self.path/'ledger.sqlite')
 def tearDown(self):self.temp.cleanup()
 def test_success_then_duplicate_blocked(self):
  calls=[]
  def transport(payload,key):
   calls.append(payload);return {'data':{'createPost':{'post':{'id':'test-id'}}}}
  out=publisher.submit_reviewed(self.carousel,self.spec,{'cdn.example.com'},self.digest,'fake-key',self.db,self.fetch,transport)
  self.assertEqual(out['state'],'confirmed')
  with self.assertRaises(ValueError):publisher.submit_reviewed(self.carousel,self.spec,{'cdn.example.com'},self.digest,'fake-key',self.db,self.fetch,transport)
  self.assertEqual(len(calls),1)
 def test_remote_change_blocks_send(self):
  calls=[]
  def transport(*args):calls.append(args)
  with self.assertRaises(ValueError):publisher.submit_reviewed(self.carousel,self.spec,{'cdn.example.com'},self.digest,'fake-key',self.db,lambda u,h:PNG+b'changed',transport)
  self.assertEqual(calls,[])
 def test_caption_change_blocks_send(self):
  (self.carousel/'caption.txt').write_text('Altered')
  with self.assertRaises(ValueError):publisher.submit_reviewed(self.carousel,self.spec,{'cdn.example.com'},self.digest,'fake-key',self.db,self.fetch,lambda *a:{})
 def test_destination_change_blocks_send(self):
  new={'channel_id':'other-channel','image_urls':self.spec['image_urls']}
  with self.assertRaises(ValueError):publisher.submit_reviewed(self.carousel,new,{'cdn.example.com'},self.digest,'fake-key',self.db,self.fetch,lambda *a:{})
 def test_timeout_records_unknown_and_blocks_retry(self):
  def timeout(*args):raise TimeoutError('timeout')
  result=publisher.submit_reviewed(self.carousel,self.spec,{'cdn.example.com'},self.digest,'fake-key',self.db,self.fetch,timeout)
  self.assertEqual(result['state'],'unknown')
  with self.assertRaises(ValueError):publisher.submit_reviewed(self.carousel,self.spec,{'cdn.example.com'},self.digest,'fake-key',self.db,self.fetch,timeout)
 def test_missing_key_fails_before_hosted_fetch(self):
  calls=[]
  def fetch(u,h):calls.append(u);return PNG
  with self.assertRaises(ValueError):publisher.submit_reviewed(self.carousel,self.spec,{'cdn.example.com'},self.digest,'',self.db,fetch,lambda *a:{})
  self.assertEqual(calls,[])
if __name__=='__main__':unittest.main()
