#!/usr/bin/env python3
"""Plan and explicitly upload locally reviewed carousel images to an R2 public bucket."""
import argparse, hashlib, hmac, json, os, re, sys, urllib.parse
from pathlib import Path
import review_server as review

class MediaError(ValueError): pass

def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')

def plan(directory, account, bucket, base):
    directory=Path(directory)
    if not re.fullmatch(r'[0-9a-f]{32}',account): raise MediaError('R2 account ID must be 32 lowercase hexadecimal characters')
    if not re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{1,61}[a-z0-9])?',bucket): raise MediaError('Invalid bucket name')
    p=urllib.parse.urlsplit(base)
    if p.scheme!='https' or not p.hostname or p.username or p.password or p.port not in (None,443) or p.query or p.fragment: raise MediaError('Public base must be a plain HTTPS URL without credentials, query or fragment')
    if not re.fullmatch(r'[A-Za-z0-9.-]+',p.hostname) or not re.fullmatch(r'/[A-Za-z0-9/_-]*|',p.path): raise MediaError('Invalid public URL host or path')
    # Remote byte validation remains separate; this does not prove the domain points to the bucket.
    base=urllib.parse.urlunsplit(('https',p.netloc.lower(),p.path.rstrip('/'),'',''))
    snap=review.snapshot(directory)
    try: approval=json.loads(review.read_file(directory/'approval.json', review.MAX_TEXT))
    except (ValueError, OSError, review.ReviewError): raise MediaError('Valid local approval.json required') from None
    if not isinstance(approval,dict) or approval.get('type')!='local_content_review' or not isinstance(approval.get('digest'),str) or not hmac.compare_digest(approval['digest'],snap['digest']):
        raise MediaError('Review is missing or no longer matches local content')
    files=[]
    for entry in snap['files'][2:]:
        key='trywise/'+entry['sha256']+'.png'
        files.append({'local_name':entry['name'],'sha256':entry['sha256'],'key':key,'url':base+'/'+key})
    payload={'version':1,'account_id':account,'bucket':bucket,'base':base,'content_digest':snap['digest'],'files':files}
    return {'plan':payload,'digest':hashlib.sha256(canonical(payload)).hexdigest()}

def upload(directory, p, client):
    # Load the exact reviewed bytes and validate all images before the first write.
    local=[]
    for f in p['plan']['files']:
        data=review.read_file(Path(directory)/f['local_name'],review.MAX_IMAGE)
        if not hmac.compare_digest(hashlib.sha256(data).hexdigest(),f['sha256']): raise MediaError('Local slide changed; review again')
        local.append((f,data))
    completed=[]
    for f,data in local:
        try:
            client.put_object(Bucket=p['plan']['bucket'],Key=f['key'],Body=data,ContentType='image/png',IfNoneMatch='*')
        except Exception:
            # 412, timeout, or lost response all fail closed; never overwrite or claim success.
            raise MediaError('Upload failed or object exists. Some files may be public; inspect bucket and verify bytes before retrying.') from None
        completed.append(f['url'])
    return completed

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory');parser.add_argument('--account-id',required=True);parser.add_argument('--bucket',required=True);parser.add_argument('--public-base',required=True)
    parser.add_argument('--upload',action='store_true');parser.add_argument('--ack-public',action='store_true');parser.add_argument('--approved-plan',help='Digest from reviewed preview; binds bucket, public domain, and exact local content')
    a=parser.parse_args();p=plan(a.directory,a.account_id,a.bucket,a.public_base)
    if not a.upload:
        print(json.dumps(p,indent=2));return 0
    if not a.ack_public or not a.approved_plan or not hmac.compare_digest(a.approved_plan,p['digest']): raise MediaError('Upload requires --ack-public and exact --approved-plan from preview')
    key=os.getenv('R2_ACCESS_KEY_ID'); secret=os.getenv('R2_SECRET_ACCESS_KEY')
    if not key or not secret: raise MediaError('R2_ACCESS_KEY_ID and R2_SECRET_ACCESS_KEY are required in the environment')
    try:
        import boto3
        from botocore.config import Config
    except ImportError: raise MediaError('Install boto3 in an isolated environment before using --upload') from None
    session=boto3.session.Session(aws_access_key_id=key,aws_secret_access_key=secret,region_name='auto')
    client=session.client('s3',endpoint_url=f'https://{a.account_id}.r2.cloudflarestorage.com',config=Config(retries={'max_attempts':0},connect_timeout=10,read_timeout=30))
    urls=upload(a.directory,p,client)
    print(json.dumps({'status':'uploaded_not_verified','plan_digest':p['digest'],'public_urls':urls,'note':'Public GET verification and destination review required. Nothing was posted.'},indent=2))
    return 0
if __name__=='__main__':
    try:sys.exit(main())
    except (MediaError,review.ReviewError,OSError,ValueError) as e:print(f'Error: {e}',file=sys.stderr);sys.exit(1)
