#!/usr/bin/env python3
"""Explicitly enabled delivery of locally reviewed content. Experimental; not live tested."""
import argparse,datetime,hashlib,json,os,re,sqlite3,sys,time,urllib.parse
from pathlib import Path
import review_server,review_bridge,r2_media,reviewed_publish,buffer_adapter,buffer_publish

def config_load(path):
    config=json.loads(Path(path).read_text(encoding='utf-8'))
    needed=('account_id','bucket','public_base','channel_id','max_posts_per_day')
    if not isinstance(config,dict) or config.get('authorize_reviewed_to_configured_channel') is not True or any(k not in config for k in needed):
        raise ValueError('Explicit delivery policy and destination required')
    if not isinstance(config['channel_id'],str) or not config['channel_id'].strip():raise ValueError('Channel required')
    if type(config['max_posts_per_day']) is not int or not 1<=config['max_posts_per_day']<=5:raise ValueError('Daily limit must be 1–5')
    return config

def setup(db):
    db.execute('CREATE TABLE IF NOT EXISTS delivery_jobs (content_digest TEXT PRIMARY KEY, state TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, detail TEXT NOT NULL)')
    db.commit()
def reserve(db,digest,limit,now=None):
    now=now or datetime.datetime.now(datetime.timezone.utc);today=now.replace(hour=0,minute=0,second=0,microsecond=0).isoformat()
    db.execute('BEGIN IMMEDIATE')
    try:
        count=db.execute('SELECT COUNT(*) FROM delivery_jobs WHERE created_at>=?',(today,)).fetchone()[0]
        if count>=limit:raise ValueError('Daily delivery limit reached')
        db.execute('INSERT INTO delivery_jobs VALUES(?,?,?,?,?)',(digest,'pending',now.isoformat(),now.isoformat(),''));db.commit()
    except sqlite3.IntegrityError:
        db.rollback();raise ValueError('Content already attempted; reconcile before any further action') from None
    except Exception:
        db.rollback();raise

def update(db,digest,state,detail=''):
    with db:db.execute('UPDATE delivery_jobs SET state=?,updated_at=?,detail=? WHERE content_digest=?',(state,datetime.datetime.now(datetime.timezone.utc).isoformat(),detail,digest))

def deliver(carousel,config,ledger,r2client,buffer_key,fetcher=review_bridge.fetch_public_png,transport=buffer_publish.post_once):
    # All setup and local review checks happen before reservation and external effects.
    plan=r2_media.plan(carousel,config['account_id'],config['bucket'],config['public_base'])
    host=urllib.parse.urlsplit(config['public_base']).hostname
    if not host or not buffer_key:raise ValueError('Valid public host and Buffer credential required')
    digest=plan['plan']['content_digest'];db=sqlite3.connect(ledger,timeout=10);setup(db)
    try:
        reserve(db,digest,config['max_posts_per_day'])
        try:
            urls=r2_media.upload(carousel,plan,r2client)
            spec={'channel_id':config['channel_id'],'image_urls':urls}
            prepared=reviewed_publish.prepare(carousel,spec,{host},fetcher)
            final_digest=buffer_adapter.manifest_digest(prepared)
            result=reviewed_publish.submit_reviewed(carousel,spec,{host},final_digest,buffer_key,ledger,fetcher,transport)
            state='buffer_accepted' if result['state']=='confirmed' else 'needs_reconciliation'
            update(db,digest,state,result.get('buffer_post_id',''))
            return {'state':state,'content_digest':digest,'buffer_post_id':result.get('buffer_post_id'),'note':'Buffer acceptance is not proof of Instagram publication.'}
        except Exception:
            # R2 may contain public files; Buffer may have accepted a request.
            update(db,digest,'needs_reconciliation','Inspect storage and Buffer before any retry')
            return {'state':'needs_reconciliation','content_digest':digest,'note':'Do not retry automatically; inspect storage and Buffer.'}
    finally:db.close()

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--carousel',required=True);p.add_argument('--policy',required=True);p.add_argument('--ledger',required=True);p.add_argument('--run-live',action='store_true');p.add_argument('--ack-public-media-and-cost',action='store_true');a=p.parse_args()
    if not a.run_live or not a.ack_public_media_and_cost:raise ValueError('Explicit live and public-media/cost flags required')
    c=config_load(a.policy)
    key=os.getenv('R2_ACCESS_KEY_ID');secret=os.getenv('R2_SECRET_ACCESS_KEY');buffer=os.getenv('BUFFER_API_KEY')
    if not all((key,secret,buffer)):raise ValueError('Required credentials not configured')
    try:
        import boto3
        from botocore.config import Config
    except ImportError:raise ValueError('Install optional R2 dependencies first') from None
    client=boto3.session.Session(aws_access_key_id=key,aws_secret_access_key=secret,region_name='auto').client('s3',endpoint_url=f"https://{c['account_id']}.r2.cloudflarestorage.com",config=Config(retries={'max_attempts':0},connect_timeout=10,read_timeout=30))
    result=deliver(a.carousel,c,a.ledger,client,buffer);print(json.dumps(result,indent=2));return 0 if result['state']=='buffer_accepted' else 2
if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError,OSError,sqlite3.Error,review_server.ReviewError) as e:print(f'Error: {e}',file=sys.stderr);sys.exit(1)
