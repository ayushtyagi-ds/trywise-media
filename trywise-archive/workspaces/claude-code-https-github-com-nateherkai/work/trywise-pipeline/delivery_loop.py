#!/usr/bin/env python3
"""Explicit opt-in poller for approved drafts; experimental and not live tested."""
import argparse,os,sqlite3,sys,time
from pathlib import Path
import inbox,post_review_worker as d

def cycle(queue,root,policy,ledger,client,key,deliver=d.deliver):
    jobs=[x for x in inbox.get_items(queue,root) if x['status']=='reviewed']
    conn=sqlite3.connect(ledger,timeout=10);d.setup(conn)
    try: attempted={r[0] for r in conn.execute('SELECT content_digest FROM delivery_jobs')}
    finally:conn.close()
    import review_server
    for job in reversed(jobs):
        snap=review_server.snapshot(job['carousel'])
        if snap['digest'] in attempted:continue
        try:return deliver(job['carousel'],policy,ledger,client,key)
        except ValueError as exc:
            if str(exc)=='Daily delivery limit reached':return {'state':'daily_limit'}
            raise
    return {'state':'nothing_ready'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--db',required=True);p.add_argument('--root',required=True);p.add_argument('--policy',required=True);p.add_argument('--ledger',required=True);p.add_argument('--loop',action='store_true');p.add_argument('--interval-minutes',type=int,default=60);p.add_argument('--run-live',action='store_true');p.add_argument('--ack-public-media-and-cost',action='store_true');a=p.parse_args()
    if not (a.run_live and a.ack_public_media_and_cost):p.error('Both --run-live and --ack-public-media-and-cost required')
    if not 15<=a.interval_minutes<=10080:p.error('Interval must be 15–10080 minutes')
    policy=d.config_load(a.policy);rkey=os.getenv('R2_ACCESS_KEY_ID');secret=os.getenv('R2_SECRET_ACCESS_KEY');bkey=os.getenv('BUFFER_API_KEY')
    if not all((rkey,secret,bkey)):p.error('Credentials must be supplied securely in environment')
    try:
        import boto3
        from botocore.config import Config
    except ImportError: p.error('Optional R2 dependency missing')
    client=boto3.session.Session(aws_access_key_id=rkey,aws_secret_access_key=secret,region_name='auto').client('s3',endpoint_url=f"https://{policy['account_id']}.r2.cloudflarestorage.com",config=Config(retries={'max_attempts':0},connect_timeout=10,read_timeout=30))
    while True:
        result=cycle(a.db,a.root,policy,a.ledger,client,bkey);print(result['state'],flush=True)
        if result['state']=='needs_reconciliation':return 2
        if not a.loop:return 0
        time.sleep(a.interval_minutes*60)
if __name__=='__main__':
    try:sys.exit(main())
    except (OSError,ValueError,sqlite3.Error) as e:print('Delivery failed:',type(e).__name__,file=sys.stderr);sys.exit(1)
