import contextlib, io, json, sys, unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import buffer_adapter as adapter

class TestPostStatus(unittest.TestCase):
    def test_status_uses_read_only_query_and_returns_report(self):
        data={'post': {'id':'p1','channelId':'c1','status':'scheduled','dueAt':None,'sentAt':None,'schedulingType':'automatic'}}
        with patch.object(sys,'argv',['buffer_adapter.py','post-status','p1']), patch.object(adapter,'read_only_query',return_value=data) as query, contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(adapter.main(),0)
        query.assert_called_once_with(adapter.POST_STATUS_QUERY,{'input':{'id':'p1'}})
        self.assertTrue(adapter.POST_STATUS_QUERY.startswith('query '))
        self.assertEqual(json.loads(output.getvalue())['buffer_report']['status'],'scheduled')
    def test_mismatched_post_is_not_accepted(self):
        with patch.object(sys,'argv',['buffer_adapter.py','post-status','p1']), patch.object(adapter,'read_only_query',return_value={'post':{'id':'other'}}), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(adapter.main(),1)
