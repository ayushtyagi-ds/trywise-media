#!/usr/bin/env python3
"""Select recent feed items and produce local drafts for review; never publish."""
import argparse, datetime as dt, json, os, re, sqlite3, sys, time
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import urlsplit
import pipeline_runner, trywise, editorial_rank

UTC=dt.timezone.utc

def setup(db):
    db.execute('''CREATE TABLE IF NOT EXISTS draft_jobs (
      story_id TEXT PRIMARY KEY, state TEXT NOT NULL, reserved_at TEXT NOT NULL,
      completed_at TEXT, output_path TEXT NOT NULL, error_kind TEXT NOT NULL DEFAULT '',
      FOREIGN KEY(story_id) REFERENCES stories(id))''')
    db.commit()

def reserve(db,outdir,allowed,max_days,max_attempts,now=None):
    """Atomically claim one story and reserve one potential provider call.

    Reservation is committed before work. Interrupted/failed jobs are never retried
    automatically, so a crash after a billable call cannot multiply charges.
    """
    now=now or dt.datetime.now(UTC)
    cutoff=(now-dt.timedelta(days=max_days)).isoformat()
    today=now.replace(hour=0,minute=0,second=0,microsecond=0).isoformat()
    upper=(now+dt.timedelta(minutes=5)).isoformat()
    db.execute('BEGIN IMMEDIATE')
    try:
        count=db.execute('SELECT COUNT(*) FROM draft_jobs WHERE reserved_at >= ?', (today,)).fetchone()[0]
        if count>=max_attempts:
            db.commit();return None
        rows=db.execute('''SELECT s.id,s.title,s.url,s.published_at FROM stories s
             LEFT JOIN draft_jobs j ON s.id=j.story_id
             WHERE s.status='new' AND j.story_id IS NULL AND s.published_at>=? AND s.published_at<=?
             ORDER BY s.published_at DESC LIMIT 1000''',(cutoff,upper)).fetchall()
        # Candidate ranking is a transparent heuristic, not a truth or relevance check.
        rows.sort(key=lambda row: editorial_rank.rank_title(row[1])['score'], reverse=True)
        for story_id,title,url,published in rows:
            parsed=urlsplit(url)
            if not re.fullmatch('[0-9a-f]{64}',story_id) or parsed.scheme!='https' or parsed.hostname not in allowed or parsed.username or parsed.password:
                continue
            try:
                date=dt.datetime.fromisoformat(published).date().isoformat()
            except (ValueError,TypeError):continue
            output=str(Path(outdir)/story_id)
            db.execute('INSERT INTO draft_jobs (story_id,state,reserved_at,output_path) VALUES (?,\'pending\',?,?)',(story_id,now.isoformat(),output))
            db.commit()
            return {'story_id':story_id,'title':title,'url':url,'published_at':date,'output_path':output}
        db.commit();return None
    except Exception:
        db.rollback();raise

def execute(db,job,allowed,model,runner=pipeline_runner.run,now=None):
    args=SimpleNamespace(out=job['output_path'], url=job['url'],allow_host=allowed,
       title=job['title'],published_at=job['published_at'],live=True,model=model,
       ack_data=True,source=None,fixture_response=None)
    try:
        runner(args)
        receipt=Path(job['output_path'])/'receipt.json'
        if not receipt.is_file(): raise ValueError('missing completion receipt')
        state='review'; err=''
    except Exception as exc:
        # Never persist exception text: provider responses can contain sensitive data.
        state='failed';err=type(exc).__name__
    with db:
        db.execute('UPDATE draft_jobs SET state=?,completed_at=?,error_kind=? WHERE story_id=?',
            (state,(now or dt.datetime.now(UTC)).isoformat(),err,job['story_id']))
    return state

def collect(db,config,days):
    cfg=json.loads(Path(config).read_text(encoding='utf-8')); cutoff=dt.datetime.now(UTC)-dt.timedelta(days=days)
    count=0;failed=0
    for feed in cfg['feeds']:
        try:count+=trywise.ingest(db,trywise.fetch(feed['url']),feed['url'],cutoff=cutoff)
        except Exception:failed+=1
    return count,failed

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--db',required=True);p.add_argument('--outdir',required=True);p.add_argument('--config',default=str(Path(__file__).with_name('feeds.json')))
    p.add_argument('--allow-host',action='append',required=True);p.add_argument('--model',required=True);p.add_argument('--max-attempts-per-day',type=int,required=True)
    p.add_argument('--days',type=int,default=7);p.add_argument('--interval-minutes',type=int,default=60);p.add_argument('--loop',action='store_true')
    p.add_argument('--run-live',action='store_true');p.add_argument('--ack-data-and-cost',action='store_true')
    a=p.parse_args()
    if not a.run_live or not a.ack_data_and_cost:p.error('requires --run-live and --ack-data-and-cost; may incur charges')
    if not os.environ.get('GEMINI_API_KEY'):p.error('GEMINI_API_KEY must be supplied securely in environment')
    if not 1<=a.max_attempts_per_day<=20 or not 1<=a.days<=30 or not 30<=a.interval_minutes<=10080:p.error('invalid attempts, days or interval limit')
    out=Path(a.outdir);out.mkdir(parents=True,exist_ok=True)
    db=trywise.connect(a.db);setup(db)
    try:
        while True:
            count,failed=collect(db,a.config,a.days)
            if failed: print(f'Warning: {failed} feed(s) failed; successful feeds kept',file=sys.stderr)
            job=reserve(db,out,set(a.allow_host),a.days,a.max_attempts_per_day)
            job_result = execute(db,job,a.allow_host,a.model) if job else None
            if job: print(f"job {job['story_id']}: {job_result}",flush=True)
            else:print('No eligible fresh story or daily limit reached',flush=True)
            if not a.loop:return 1 if failed or job_result == 'failed' else 0
            time.sleep(a.interval_minutes*60)
    finally:db.close()
if __name__=='__main__':
    try:sys.exit(main() or 0)
    except (OSError,ValueError,sqlite3.Error,KeyError) as exc:print('Worker failed:',type(exc).__name__,file=sys.stderr);sys.exit(1)
