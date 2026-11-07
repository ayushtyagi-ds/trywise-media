import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import draftgen

class TestDrafting(unittest.TestCase):
    def setUp(self):
        self.source=draftgen.read_input(ROOT/'tests/source.json')
        self.payload=json.loads((ROOT/'tests/draft-response.json').read_text())
    def test_captured_source_requires_verified_metadata(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'capture.json'
            path.write_text(json.dumps({'source_url':'https://example.com/announcement','extract':'Test content'}))
            with self.assertRaises(draftgen.DraftError): draftgen.read_input(path)
            result=draftgen.read_input(path,'Verified title','2026-10-31')
            self.assertEqual(result['body'],'Test content')
            self.assertEqual(result['url'],'https://example.com/announcement')
    def test_validates_and_never_approves(self):
        self.payload['status']='approved'
        result=draftgen.validate_generated(self.payload,self.source)
        self.assertEqual(result['status'],'needs_review')
        self.assertEqual(result['source']['url'],self.source['url'])
        self.assertNotIn('body',result['source'])
    def test_rejects_invented_evidence(self):
        self.payload['claims'][0]['evidence']='a fabricated quotation'
        with self.assertRaises(draftgen.DraftError): draftgen.validate_generated(self.payload,self.source)
    def test_rejects_bad_slide_count(self):
        self.payload['slides']=self.payload['slides'][:1]
        with self.assertRaises(draftgen.DraftError): draftgen.validate_generated(self.payload,self.source)
    def test_offline_fixture_cli_and_existing_file_guard(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'draft.json'
            cmd=[sys.executable,str(ROOT/'draftgen.py'),'--source',str(ROOT/'tests/source.json'),'--out',str(out),'--fixture-response',str(ROOT/'tests/draft-response.json')]
            result=subprocess.run(cmd,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            original=out.read_bytes()
            self.assertEqual(json.loads(original)['status'],'needs_review')
            self.assertNotEqual(subprocess.run(cmd,capture_output=True).returncode,0)
            self.assertEqual(out.read_bytes(),original)
    def test_live_requires_explicit_consent_and_model(self):
        with tempfile.TemporaryDirectory() as d, patch.dict('os.environ',{'GEMINI_API_KEY':'example-secret'}):
            cmd=[sys.executable,str(ROOT/'draftgen.py'),'--source',str(ROOT/'tests/source.json'),'--out',str(Path(d)/'draft.json'),'--live']
            result=subprocess.run(cmd,capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)
            self.assertNotIn('example-secret',result.stderr)
            self.assertIn('--model and --ack-data',result.stderr)
    def test_request_has_no_key_and_user_content_is_marked_untrusted(self):
        req=draftgen.build_request(self.source)
        self.assertIn('untrusted data',req['contents'][0]['parts'][0]['text'])
        self.assertNotIn('GEMINI_API_KEY',json.dumps(req))

if __name__=='__main__': unittest.main()
