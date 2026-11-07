import json, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/'pipeline_runner.py'
class RunnerTest(unittest.TestCase):
 def run_cli(self,*args):
  return subprocess.run([sys.executable,str(SCRIPT),*map(str,args)],capture_output=True,text=True)
 def test_offline_end_to_end_and_no_overwrite(self):
  with tempfile.TemporaryDirectory() as d:
   dest=Path(d)/'output'
   args=['--source',ROOT/'tests/source.json','--fixture-response',ROOT/'tests/draft-response.json','--out',dest]
   p=self.run_cli(*args)
   self.assertEqual(p.returncode,0,p.stderr)
   receipt=json.loads((dest/'receipt.json').read_text())
   self.assertEqual(receipt['status'],'needs_review');self.assertEqual(receipt['mode'],'fixture_offline')
   self.assertEqual(json.loads((dest/'carousel/manifest.json').read_text())['status'],'needs_review')
   self.assertEqual(len(list((dest/'carousel').glob('*.png'))),4)
   before=(dest/'receipt.json').read_bytes(); p=self.run_cli(*args)
   self.assertNotEqual(p.returncode,0);self.assertEqual((dest/'receipt.json').read_bytes(),before)
 def test_offline_fixture_cannot_fetch_url(self):
  with tempfile.TemporaryDirectory() as d:
   p=self.run_cli('--url','https://example.com/x','--allow-host','example.com','--title','x','--published-at','2026-01-01','--fixture-response',ROOT/'tests/draft-response.json','--out',Path(d)/'out')
   self.assertNotEqual(p.returncode,0);self.assertIn('offline',p.stderr)
 def test_failed_draft_leaves_no_partial_output(self):
  with tempfile.TemporaryDirectory() as d:
   bad=Path(d)/'bad.json';bad.write_text('{}');dest=Path(d)/'out'
   p=self.run_cli('--source',ROOT/'tests/source.json','--fixture-response',bad,'--out',dest)
   self.assertNotEqual(p.returncode,0);self.assertFalse(dest.exists());self.assertFalse(list(Path(d).glob('.trywise-run-*')))
 def test_live_without_explicit_ack_fails_before_network(self):
  with tempfile.TemporaryDirectory() as d:
   p=self.run_cli('--source',ROOT/'tests/source.json','--live','--out',Path(d)/'out')
   self.assertNotEqual(p.returncode,0);self.assertIn('--ack-data',p.stderr)
if __name__=='__main__':unittest.main()
