import hashlib,http.client,json,sqlite3,sys,tempfile,threading,unittest,urllib.parse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));import inbox_server
class InboxServerTests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();p=Path(self.t.name);self.root=p/'drafts';self.root.mkdir();self.id='a'*64;path=self.root/self.id;car=path/'carousel';car.mkdir(parents=True);(path/'receipt.json').write_text('{}');(car/'manifest.json').write_text(json.dumps({'status':'needs_review','slides':1,'source':{'title':'Source','url':'https://example.com'}}));(car/'caption.txt').write_text('caption');(car/'01.png').write_bytes(b'\x89PNG\r\n\x1a\nfoo');db=p/'q.db';c=sqlite3.connect(db);c.executescript('create table stories(id text,title text);create table draft_jobs(story_id text,state text,output_path text,completed_at text);');c.execute('insert into stories values(?,?)',(self.id,'<script>bad</script>'));c.execute('insert into draft_jobs values(?,?,?,?)',(self.id,'review',str(path),'2026-01-01'));c.commit();c.close();self.car=car
  try:self.server=inbox_server.Server(db,self.root,0)
  except PermissionError:self.t.cleanup();self.skipTest('Local socket binding disallowed')
  self.thread=threading.Thread(target=lambda:self.server.serve_forever(poll_interval=.01),daemon=True);self.thread.start()
 def tearDown(self):
  if hasattr(self,'server'):self.server.shutdown();self.server.server_close();self.thread.join()
  self.t.cleanup()
 def req(self,method,path,body=None,headers=None):
  c=http.client.HTTPConnection('127.0.0.1',self.server.server_address[1],timeout=5);c.request(method,path,body,headers or {});r=c.getresponse();data=r.read();status=r.status;c.close();return status,data
 def test_inbox_escapes_title_and_draft_loads(self):
  status,data=self.req('GET','/');self.assertEqual(status,200);self.assertNotIn(b'<script>bad',data);self.assertIn(b'&lt;script&gt;',data)
  status,data=self.req('GET','/draft/'+self.id);self.assertEqual(status,200);self.assertIn(b'trigger a post',data.lower())
 def test_review_records_approval_for_exact_visible_draft(self):
  import re
  status,data=self.req('GET','/draft/'+self.id);self.assertEqual(status,200)
  token=re.search(rb'name="token" value="([^"]+)"',data).group(1).decode();digest=re.search(rb'name="digest" value="([^"]+)"',data).group(1).decode()
  body=urllib.parse.urlencode({'token':token,'digest':digest,'confirmed':'yes'})
  status,data=self.req('POST','/draft/'+self.id+'/approve',body,{'Origin':self.server.origin,'Content-Type':'application/x-www-form-urlencoded'})
  self.assertEqual(status,200);self.assertTrue((self.car/'approval.json').exists())
 def test_cross_origin_and_traversal_fail(self):
  status,_=self.req('POST','/draft/'+self.id+'/approve','x=1',{'Origin':'https://evil.example','Content-Type':'application/x-www-form-urlencoded'});self.assertEqual(status,403)
  status,_=self.req('GET','/draft/../../etc/passwd');self.assertEqual(status,404)
if __name__=='__main__':unittest.main()
