import http.client,json,sys,tempfile,threading,unittest,urllib.parse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import review_server as r

class ReviewTest(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(); self.path=Path(self.temp.name)
  (self.path/'manifest.json').write_text(json.dumps({'status':'needs_review','slides':2,'source':{'title':'<script>bad</script>','url':'https://example.com'}}))
  (self.path/'caption.txt').write_text('Caption <script>bad</script>')
  for i in (1,2): (self.path/f'{i:02}.png').write_bytes(b'\x89PNG\r\n\x1a\n'+bytes([i]))
  try: self.s=r.ReviewServer(self.path,0)
  except PermissionError:
   self.temp.cleanup(); self.skipTest('Loopback socket permission unavailable')
  self.thread=threading.Thread(target=lambda:self.s.serve_forever(poll_interval=0.01),daemon=True);self.thread.start()
 def tearDown(self): self.s.shutdown();self.s.server_close();self.thread.join();self.temp.cleanup()
 def request(self,method,path,body=None,headers=None):
  c=http.client.HTTPConnection('127.0.0.1',self.s.server_address[1],timeout=3);c.request(method,path,body,headers or {});response=c.getresponse();data=response.read();status=response.status;c.close();return status,data
 def form(self,digest=None,token=None):
  return urllib.parse.urlencode({'token':token or self.s.token,'digest':digest or r.snapshot(self.path)['digest'],'confirmed':'yes'})
 def headers(self,origin=True):
  h={'Content-Type':'application/x-www-form-urlencoded'}
  if origin: h['Origin']=self.s.origin
  return h
 def test_review_page_escapes_text(self):
  status,data=self.request('GET','/');self.assertEqual(status,200);self.assertIn(b'&lt;script&gt;',data);self.assertNotIn(b'<script>bad',data)
 def test_origin_and_csrf_required(self):
  self.assertEqual(self.request('POST','/approve',self.form(),self.headers(False))[0],403)
  self.assertEqual(self.request('POST','/approve',self.form(token='wrong'),self.headers())[0],403)
  self.assertFalse((self.path/'approval.json').exists())
 def test_approval_hash_detects_edits(self):
  old=r.snapshot(self.path)['digest'];(self.path/'caption.txt').write_text('Changed')
  status,_=self.request('POST','/approve',self.form(old),self.headers());self.assertEqual(status,409)
  self.assertFalse((self.path/'approval.json').exists())
  current=r.snapshot(self.path)['digest'];status,_=self.request('POST','/approve',self.form(current),self.headers());self.assertEqual(status,200)
  record=json.loads((self.path/'approval.json').read_text());self.assertEqual(record['digest'],current);self.assertIn('no destination',record['scope'])
  self.assertEqual(self.request('POST','/approve',self.form(current),self.headers())[0],409)
 def test_image_version_and_path_guard(self):
  digest=r.snapshot(self.path)['digest'];self.assertEqual(self.request('GET',f'/slide/1?digest={digest}')[0],200)
  (self.path/'01.png').write_bytes(b'\x89PNG\r\n\x1a\nchanged')
  self.assertEqual(self.request('GET',f'/slide/1?digest={digest}')[0],409)
  self.assertEqual(self.request('GET','/../../etc/passwd')[0],404)
 def test_symlinks_rejected(self):
  (self.path/'01.png').unlink();(self.path/'01.png').symlink_to(self.path/'02.png')
  with self.assertRaises(r.ReviewError):r.snapshot(self.path)
 def test_rejects_host_rebinding(self):
  self.assertEqual(self.request('GET','/',headers={'Host':'bad.example'})[0],403)
class SnapshotTest(unittest.TestCase):
 def test_approval_is_bound_to_changed_caption(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)
   (p/'manifest.json').write_text(json.dumps({'status':'needs_review','slides':1,'source':{}}))
   (p/'caption.txt').write_text('Original')
   (p/'01.png').write_bytes(b'\x89PNG\r\n\x1a\nexample')
   digest=r.snapshot(p)['digest']
   (p/'caption.txt').write_text('Changed')
   with self.assertRaises(r.ReviewError):r.write_approval(p,digest)
   self.assertFalse((p/'approval.json').exists())

if __name__=='__main__': unittest.main()
