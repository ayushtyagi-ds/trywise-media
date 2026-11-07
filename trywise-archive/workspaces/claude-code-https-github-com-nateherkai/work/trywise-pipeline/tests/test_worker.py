import datetime as dt,json,os,sys,tempfile,threading,unittest
from unittest.mock import patch
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));import worker,trywise
UTC=dt.timezone.utc
class WorkerTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.db=trywise.connect(self.root/'queue.sqlite3');worker.setup(self.db);self.now=dt.datetime(2026,10,31,tzinfo=UTC)
 def tearDown(self):self.db.close();self.tmp.cleanup()
 def add(self,n,url='https://blog.google/a',published='2026-10-30T12:00:00+00:00'):
  id=f'{n:064x}';self.db.execute('INSERT INTO stories(id,title,url,published_at,source_feed,collected_at) VALUES (?,?,?,?,?,?)',(id,'Example',url,published,'https://blog.google/rss',self.now.isoformat()));self.db.commit();return id
 def reserve(self,n=1,now=None):return worker.reserve(self.db,self.root,{'blog.google'},7,n,now or self.now)
 def test_dedupe_and_daily_cap(self):
  first=self.add(1);self.add(2,url='https://blog.google/b')
  job=self.reserve();self.assertEqual(job['story_id'],first)
  self.assertIsNone(self.reserve());self.assertEqual(self.db.execute('SELECT state FROM draft_jobs').fetchone()[0],'pending')
 def test_prioritizes_relevant_title_within_recent_candidates(self):
  older=self.add(1,'https://blog.google/api','2026-10-29T12:00:00+00:00');self.add(2,'https://blog.google/earnings','2026-10-30T12:00:00+00:00')
  self.db.execute('UPDATE stories SET title=? WHERE id=?',('New developer coding API',older));self.db.execute('UPDATE stories SET title=? WHERE url=?',('Quarterly investor earnings','https://blog.google/earnings'));self.db.commit()
  self.assertEqual(self.reserve()['story_id'],older)
 def test_allowlist_and_freshness(self):
  self.add(1,'https://evil.example/',published='2026-10-30T12:00:00+00:00');self.add(2,'https://blog.google/old','2026-10-01T12:00:00+00:00');self.add(3,'https://blog.google/future','2027-01-01T12:00:00+00:00')
  self.assertIsNone(self.reserve())
 def test_success_and_review_state(self):
  self.add(1);job=self.reserve()
  def fake(args):
   p=Path(args.out);p.mkdir();(p/'receipt.json').write_text('{}')
  self.assertEqual(worker.execute(self.db,job,['blog.google'],'model',fake,self.now),'review')
  self.assertEqual(self.db.execute('SELECT state FROM draft_jobs').fetchone()[0],'review')
 def test_failure_no_secret_and_no_retry(self):
  self.add(1);job=self.reserve()
  def fail(args):raise RuntimeError('secret-token')
  self.assertEqual(worker.execute(self.db,job,['blog.google'],'model',fail,self.now),'failed')
  self.assertNotIn('secret-token',str(self.db.execute('SELECT * FROM draft_jobs').fetchall()))
  self.assertIsNone(self.reserve(2))
 def test_real_orchestration_with_mocked_provider(self):
  self.add(1);job=self.reserve()
  source=json.loads((Path(__file__).parent/'source.json').read_text())
  generated=json.loads((Path(__file__).parent/'draft-response.json').read_text())
  captured={'source_url':source['url'],'extract':source['body'],'sha256':'0'*64,'retrieved_at':self.now.isoformat()}
  with patch.dict(os.environ,{'GEMINI_API_KEY':'test-fixture'}), patch('pipeline_runner.source_capture.capture',return_value=captured), patch('pipeline_runner.draftgen.request_live',return_value=generated):
   self.assertEqual(worker.execute(self.db,job,['blog.google'],'fixture-model',now=self.now),'review')
  dest=Path(job['output_path']);self.assertTrue((dest/'receipt.json').exists());self.assertTrue((dest/'carousel'/'01.png').exists())
  self.assertEqual(json.loads((dest/'draft.json').read_text())['status'],'needs_review')
 def test_crash_pending_not_retried(self):
  self.add(1);self.reserve();self.assertIsNone(self.reserve(2))
 def test_concurrent_claim_unique(self):
  self.add(1); claims=[]
  def claim():
   db=trywise.connect(self.root/'queue.sqlite3');claims.append(worker.reserve(db,self.root,{'blog.google'},7,3,self.now));db.close()
  ts=[threading.Thread(target=claim) for _ in range(2)]
  for t in ts:t.start()
  for t in ts:t.join()
  self.assertEqual(sum(c is not None for c in claims),1)
if __name__=='__main__':unittest.main()
