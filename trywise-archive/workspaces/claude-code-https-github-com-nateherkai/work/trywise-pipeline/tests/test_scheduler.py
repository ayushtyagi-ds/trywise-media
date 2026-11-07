import unittest,tempfile,datetime as dt,sys
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));import scheduler
class SchedulerTests(unittest.TestCase):
 def test_due_and_failure_retry_interval(self):
  with tempfile.TemporaryDirectory() as d:
   state=Path(d)/'state.json';now=dt.datetime(2026,10,31,tzinfo=dt.timezone.utc);calls=[]
   def run(*a,**kw):calls.append(a);return SimpleNamespace(returncode=1,stdout='',stderr='offline')
   self.assertEqual(scheduler.tick(state,'queue','feeds',3600,run,now),'failed')
   self.assertEqual(scheduler.tick(state,'queue','feeds',3600,run,now+dt.timedelta(minutes=5)),'not_due')
   self.assertEqual(scheduler.tick(state,'queue','feeds',3600,run,now+dt.timedelta(hours=1)),'failed')
   self.assertEqual(len(calls),2)
 def test_corrupt_state_fails_closed(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'state';p.write_text('{')
   with self.assertRaises(ValueError):scheduler.tick(p,'db','feeds',3600)
if __name__=='__main__':unittest.main()
