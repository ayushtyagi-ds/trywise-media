#!/usr/bin/env python3
"""Record one Buffer post's metrics snapshot. Read-only API query; not live tested."""
import argparse,datetime,json,os,sqlite3,sys,urllib.error,urllib.request
import buffer_adapter as a
QUERY='''query Metrics($input: PostInput!) { post(input: $input) { id channelId metrics { type name value unit } metricsUpdatedAt } }'''
MAX_BYTES=1000000

def get_metrics(post_id,key):
    if not isinstance(post_id,str) or not post_id.strip() or len(post_id)>200:raise ValueError('Post ID required')
    if not key:raise ValueError('BUFFER_API_KEY required')
    data=json.dumps({'query':QUERY,'variables':{'input':{'id':post_id}}}).encode()
    req=urllib.request.Request(a.ENDPOINT,data=data,headers={'Content-Type':'application/json','Authorization':'Bearer '+key},method='POST')
    try:
        with urllib.request.build_opener(a.NoRedirect()).open(req,timeout=15) as response:raw=response.read(MAX_BYTES+1)
    except (urllib.error.URLError,OSError,TimeoutError):raise ValueError('Buffer request failed; verify account and permissions') from None
    if len(raw)>MAX_BYTES:raise ValueError('Buffer response too large')
    try:
        obj=json.loads(raw)
        if not isinstance(obj,dict):raise ValueError()
        post=obj['data']['post']
        if obj.get('errors') or not isinstance(post,dict) or post.get('id')!=post_id or not isinstance(post.get('metrics'),list):raise ValueError()
        if len(post['metrics'])>1000:raise ValueError()
        metrics=[]
        for m in post['metrics']:
            if not isinstance(m,dict):raise ValueError()
            metrics.append({k:m.get(k) for k in ('type','name','value','unit')})
        return {'post_id':post['id'],'channel_id':post.get('channelId'),'metrics_updated_at':post.get('metricsUpdatedAt'),'metrics':metrics}
    except (KeyError,TypeError,ValueError):raise ValueError('Buffer returned an incomplete or invalid metrics response') from None

def record(db_path,snapshot):
    with sqlite3.connect(db_path) as db:
        db.execute('CREATE TABLE IF NOT EXISTS metric_snapshots (post_id TEXT NOT NULL, retrieved_at TEXT NOT NULL, snapshot_json TEXT NOT NULL)')
        db.execute('INSERT INTO metric_snapshots VALUES(?,?,?)',(snapshot['post_id'],datetime.datetime.now(datetime.timezone.utc).isoformat(),json.dumps(snapshot,ensure_ascii=False)))

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--post-id',required=True);p.add_argument('--db',required=True);p.add_argument('--fetch',action='store_true',help='Make a read-only Buffer API request');a=p.parse_args()
    if not a.fetch:p.error('--fetch required; this accesses Buffer')
    result=get_metrics(a.post_id,os.getenv('BUFFER_API_KEY'));record(a.db,result);print(json.dumps(result,indent=2))
if __name__=='__main__':
    try:main()
    except (ValueError,OSError,sqlite3.Error) as exc:print(f'Error: {exc}',file=sys.stderr);sys.exit(1)
