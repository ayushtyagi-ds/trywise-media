import json,sqlite3,tempfile,unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));import inbox
class InboxTest(unittest.TestCase):
 def test_lists_only_completed_safe_children(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t)/'drafts';root.mkdir();db=Path(t)/'q.db';ident='a'*64
   conn=sqlite3.connect(db);conn.executescript('create table stories(id text,title text);create table draft_jobs(story_id text,state text,output_path text,completed_at text);');conn.execute('insert into stories values(?,?)',(ident,'Test'));conn.execute('insert into draft_jobs values(?,?,?,?)',(ident,'review',str(root/ident),'2026-01-01'));conn.commit();conn.close()
   self.assertEqual(inbox.get_items(db,root),[])
   job=root/ident;carousel=job/'carousel';carousel.mkdir(parents=True);(job/'receipt.json').write_text('{}');(carousel/'manifest.json').write_text(json.dumps({'status':'needs_review','slides':1,'source':{}}));(carousel/'caption.txt').write_text('caption');(carousel/'01.png').write_bytes(b'\x89PNG\r\n\x1a\nfoo')
   result=inbox.get_items(db,root);self.assertEqual(len(result),1);self.assertEqual(result[0]['status'],'needs_review')
if __name__=='__main__':unittest.main()
