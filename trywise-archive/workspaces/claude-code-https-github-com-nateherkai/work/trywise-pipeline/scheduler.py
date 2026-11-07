#!/usr/bin/env python3
"""Run only the research collector periodically; no draft or post creation."""
import argparse, datetime as dt, json, os, subprocess, sys, time
from pathlib import Path

def due(last,now,interval):
    if not last:return True
    try:
        timestamp=dt.datetime.fromisoformat(last)
        if timestamp.tzinfo is None:return True
        return (now-timestamp).total_seconds() >= interval
    except (ValueError,TypeError):return True

def tick(state_path,db,config,interval,run=subprocess.run,now=None):
    now=now or dt.datetime.now(dt.timezone.utc); state_path=Path(state_path)
    if state_path.exists():
        try: state=json.loads(state_path.read_text())
        except (ValueError,OSError): raise ValueError('State unreadable; fix or remove it manually')
    else: state={}
    if not due(state.get('last_attempt'),now,interval): return 'not_due'
    command=[sys.executable,str(Path(__file__).with_name('trywise.py')),'--db',str(db),'collect','--config',str(config)]
    result=run(command,check=False,capture_output=True,text=True)
    new={'last_attempt':now.isoformat(),'last_exit_code':result.returncode,'stdout':result.stdout[-5000:],'stderr':result.stderr[-5000:]}
    state_path.parent.mkdir(parents=True,exist_ok=True)
    temp=state_path.with_suffix(state_path.suffix+'.tmp')
    temp.write_text(json.dumps(new,indent=2)); os.replace(temp,state_path)
    return 'ok' if result.returncode==0 else 'failed'

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--db',required=True);p.add_argument('--state',required=True);p.add_argument('--config',required=True);p.add_argument('--interval-hours',type=float,default=24);p.add_argument('--loop',action='store_true');a=p.parse_args()
    if not 1<=a.interval_hours<=168:p.error('interval must be 1–168 hours')
    while True:
        status=tick(a.state,a.db,a.config,a.interval_hours*3600);print(status,flush=True)
        if not a.loop: return 1 if status=='failed' else 0
        time.sleep(300)
if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError,OSError) as exc:print(f'Error: {exc}',file=sys.stderr);sys.exit(1)
