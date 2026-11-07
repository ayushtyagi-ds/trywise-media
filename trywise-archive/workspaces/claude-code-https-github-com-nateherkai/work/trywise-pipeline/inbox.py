#!/usr/bin/env python3
"""List completed review drafts and launch a local reviewer; never posts."""
import argparse,json,os,re,sqlite3,sys
from pathlib import Path
import review_server

def get_items(db_path,root):
    root=Path(root).resolve(strict=True)
    if not root.is_dir():raise ValueError('Draft root must be a directory')
    p=Path(db_path).resolve(strict=True)
    db=sqlite3.connect(p.as_uri()+'?mode=ro',uri=True)
    try:rows=db.execute("SELECT j.story_id,s.title,j.output_path FROM draft_jobs j JOIN stories s ON s.id=j.story_id WHERE j.state='review' ORDER BY j.completed_at DESC").fetchall()
    finally:db.close()
    items=[]
    for story_id,title,output in rows:
        if not re.fullmatch(r'[0-9a-f]{64}',story_id):continue
        raw=Path(output)
        if raw.name != story_id or raw.is_symlink():continue
        try:
            path=raw.resolve(strict=True)
            if path.parent != root or not (path/'receipt.json').is_file() or (path/'carousel').is_symlink():continue
            carousel=(path/'carousel').resolve(strict=True)
            if carousel.parent!=path:continue
            snap=review_server.snapshot(carousel)
            status='needs_review'
            approval=carousel/'approval.json'
            if approval.exists():
                a=json.loads(review_server.read_file(approval,review_server.MAX_TEXT))
                status='reviewed' if isinstance(a,dict) and a.get('type')=='local_content_review' and a.get('digest')==snap['digest'] and a.get('files')==snap['files'] else 'changed_since_review'
            items.append({'id':story_id,'title':title,'status':status,'carousel':str(carousel)})
        except (OSError,ValueError,review_server.ReviewError):continue
    return items

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--db',required=True);p.add_argument('--root',required=True);p.add_argument('--open',metavar='STORY_ID');p.add_argument('--port',type=int,default=8765);a=p.parse_args()
    if not 1<=a.port<=65535:p.error('Invalid port')
    items=get_items(a.db,a.root)
    if not a.open:
        print(json.dumps(items,indent=2,ensure_ascii=False));return 0
    matches=[i for i in items if i['id']==a.open]
    if len(matches)!=1:raise ValueError('Story not found or output incomplete')
    server=review_server.ReviewServer(matches[0]['carousel'],a.port)
    print(f'Review at {server.origin}/. Press Ctrl-C to stop. Nothing is posted.',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
    return 0
if __name__=='__main__':
    try:sys.exit(main())
    except (OSError,ValueError,sqlite3.Error,review_server.ReviewError) as e:print('Inbox error:',e,file=sys.stderr);sys.exit(1)
