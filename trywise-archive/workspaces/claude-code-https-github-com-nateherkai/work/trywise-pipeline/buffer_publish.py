#!/usr/bin/env python3
"""Explicitly enqueue one approved Buffer post; never auto-retry uncertain writes."""
import argparse, datetime, hmac, json, os, re, sqlite3, sys, urllib.request
from pathlib import Path
import buffer_adapter as a

MAX_RESPONSE = 1_000_000

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()

def database(path):
    if path == ':memory:' or not path.strip(): raise ValueError('Use a persistent SQLite database path')
    db=sqlite3.connect(path,timeout=10)
    db.execute('PRAGMA synchronous=FULL')
    db.execute('''CREATE TABLE IF NOT EXISTS submissions (
        digest TEXT PRIMARY KEY, channel_id TEXT NOT NULL, state TEXT NOT NULL,
        created_at TEXT NOT NULL, updated_at TEXT NOT NULL, remote_post_id TEXT, detail TEXT NOT NULL DEFAULT '')''')
    return db

def reserve(db,manifest,digest):
    # INSERT + commit completes before network IO; surviving pending rows are ambiguous.
    try:
        with db:
            db.execute('INSERT INTO submissions VALUES(?,?,?,?,?,?,?)',
                (digest,manifest['channel_id'],'pending',now(),now(),None,''))
    except sqlite3.IntegrityError:
        raise ValueError('This digest already has a submission record. Do not retry; inspect and reconcile it.') from None

def write_state(db,digest,state,remote_id=None,detail=''):
    with db:
        db.execute('UPDATE submissions SET state=?,updated_at=?,remote_post_id=?,detail=? WHERE digest=?',
                   (state,now(),remote_id,detail,digest))

def post_once(payload,key):
    req=urllib.request.Request(a.ENDPOINT,data=json.dumps(payload).encode('utf-8'),
       headers={'Content-Type':'application/json','Authorization':'Bearer '+key},method='POST')
    # Any exception or non-specific error is ambiguous; we never echo response or credentials.
    with urllib.request.build_opener(a.NoRedirect()).open(req,timeout=30) as response:
        raw=response.read(MAX_RESPONSE+1)
    if len(raw)>MAX_RESPONSE: raise ValueError('response too large')
    return json.loads(raw)

def send(db,manifest,approved_digest,key,transport=post_once):
    m=a.validate_manifest(manifest)
    digest=a.manifest_digest(m)
    if not isinstance(approved_digest,str) or not re.fullmatch(r'[0-9a-fA-F]{64}',approved_digest) or not hmac.compare_digest(digest,approved_digest.lower()): raise ValueError('Approval digest does not match the current manifest')
    if not key: raise ValueError('BUFFER_API_KEY is required')
    payload=a.payload_for_preview(m)
    reserve(db,m,digest)
    try:
        result=transport(payload,key)
        result=result if isinstance(result,dict) else {}
        post=(result.get('data') or {}).get('createPost') or {}
        if result.get('errors'): raise ValueError('GraphQL error')
        if isinstance(post.get('post'),dict) and isinstance(post['post'].get('id'),str) and post['post']['id']:
            remote_id=post['post']['id'];write_state(db,digest,'confirmed',remote_id)
            return {'digest':digest,'state':'confirmed','buffer_post_id':remote_id,'note':'Accepted by Buffer; not proof of Instagram publication.'}
        if isinstance(post.get('message'),str) and post['message']:
            # Explicit Buffer mutation rejection, but still block duplicate resubmission.
            write_state(db,digest,'rejected',detail='Buffer returned MutationError; review in Buffer')
            return {'digest':digest,'state':'rejected','note':'Check Buffer; submission remains blocked from automatic retry.'}
        raise ValueError('missing success response')
    except Exception:
        # Failure to persist status itself leaves pending, which also prevents repeat.
        try: write_state(db,digest,'unknown',detail='Ambiguous response; reconcile in Buffer before further action')
        except sqlite3.Error: pass
        return {'digest':digest,'state':'unknown','note':'Do not retry. Check the Buffer queue for a matching post.'}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='action',required=True)
    p=sub.add_parser('preview');p.add_argument('manifest')
    s=sub.add_parser('send');s.add_argument('manifest');s.add_argument('--db',required=True);s.add_argument('--approved-digest',required=True);s.add_argument('--send',action='store_true');s.add_argument('--ack-public-media',action='store_true')
    i=sub.add_parser('status');i.add_argument('--db',required=True);i.add_argument('--digest',required=True)
    args=parser.parse_args()
    if args.action=='preview':
        manifest=json.loads(Path(args.manifest).read_text(encoding='utf-8'))
        print(json.dumps({'digest':a.manifest_digest(manifest),'manifest':a.validate_manifest(manifest),'note':'Preview only. If sent, Buffer will add this item to the next available queue slot using automatic scheduling. No approval or request sent.'},ensure_ascii=False,indent=2));return
    if args.action=='send':
        if not args.send or not args.ack_public_media: raise ValueError('Sending requires --send and --ack-public-media after review')
        manifest=json.loads(Path(args.manifest).read_text(encoding='utf-8'))
        db=database(args.db)
        try:
            result=send(db,manifest,args.approved_digest,os.getenv('BUFFER_API_KEY'))
            print(json.dumps(result,indent=2))
            if result['state'] != 'confirmed': return 2
        finally: db.close()
    else:
        db=database(args.db)
        try:
            row=db.execute('SELECT digest,channel_id,state,created_at,updated_at,remote_post_id,detail FROM submissions WHERE digest=?',(args.digest,)).fetchone()
            print(json.dumps(dict(zip(('digest','channel_id','state','created_at','updated_at','remote_post_id','detail'),row)) if row else {'error':'No submission found'},indent=2))
        finally:db.close()
if __name__=='__main__':
    try: sys.exit(main() or 0)
    except (ValueError, OSError, sqlite3.Error) as e: print(f'Error: {e}',file=sys.stderr);sys.exit(1)
