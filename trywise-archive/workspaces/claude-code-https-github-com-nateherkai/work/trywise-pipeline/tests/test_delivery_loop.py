import sqlite3,tempfile,unittest,sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));import delivery_loop as loop
class Tests(unittest.TestCase):
 def test_no_reviewed_is_noop(self):
  with tempfile.TemporaryDirectory() as t,patch('inbox.get_items',return_value=[{'status':'needs_review'}]):
   self.assertEqual(loop.cycle('unused',t,{},str(Path(t)/'l.db'),None,'x')['state'],'nothing_ready')
 def test_reviewed_delivered_once_selection(self):
  with tempfile.TemporaryDirectory() as t,patch('inbox.get_items',return_value=[{'status':'reviewed','carousel':'somewhere'}]),patch('review_server.snapshot',return_value={'digest':'abc'}):
   calls=[]
   def delivery(*args):calls.append(args);return {'state':'buffer_accepted'}
   self.assertEqual(loop.cycle('unused',t,{},str(Path(t)/'l.db'),None,'key',delivery)['state'],'buffer_accepted');self.assertEqual(len(calls),1)
