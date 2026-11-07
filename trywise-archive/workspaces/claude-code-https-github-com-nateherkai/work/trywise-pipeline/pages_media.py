#!/usr/bin/env python3
"""Stage approved PNGs for GitHub Pages. This tool never uploads or deploys."""
import argparse,hashlib,hmac,json,os,re,shutil,sys,tempfile,urllib.parse
from pathlib import Path
import review_bridge,review_server

def stage(carousel,base,dest):
    try:p=urllib.parse.urlsplit(base)
    except ValueError:raise ValueError('Invalid Pages site URL') from None
    if p.scheme!='https' or not p.hostname or not p.hostname.endswith('.github.io') or p.username or p.password or p.port not in (None,443) or p.query or p.fragment or not re.fullmatch(r'/[A-Za-z0-9/_-]*|',p.path):raise ValueError('Expected plain HTTPS github.io Pages URL')
    approved=review_bridge.verify_approval(carousel)
    target=Path(dest)
    if target.exists():raise ValueError('Output already exists')
    target.parent.mkdir(parents=True,exist_ok=True)
    tmp=Path(tempfile.mkdtemp(prefix='.trywise-pages-',dir=target.parent))
    try:
        media=tmp/'media';media.mkdir();urls=[]
        for i,entry in enumerate(approved['files'][2:],1):
            data=review_server.read_file(Path(carousel)/f'{i:02d}.png',review_server.MAX_IMAGE)
            if not hmac.compare_digest(hashlib.sha256(data).hexdigest(),entry['sha256']):raise ValueError('Review changed')
            name=entry['sha256']+'.png';(media/name).write_bytes(data);urls.append(base.rstrip('/')+'/media/'+name)
        # A nojekyll file permits direct publication of static files.
        (tmp/'.nojekyll').write_text('');(tmp/'urls.json').write_text(json.dumps({'content_digest':approved['digest'],'image_urls':urls,'status':'staged_not_uploaded'},indent=2))
        if not hmac.compare_digest(review_bridge.verify_approval(carousel)['digest'],approved['digest']):raise ValueError('Review changed')
        tmp.rename(target)
    except Exception:
        shutil.rmtree(tmp,ignore_errors=True);raise
    return urls

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--carousel',required=True);p.add_argument('--site-base',required=True);p.add_argument('--out',required=True);a=p.parse_args();stage(a.carousel,a.site_base,a.out);print('Staged only. No media uploaded or published.')
if __name__=='__main__':
    try:main()
    except (OSError,ValueError,review_server.ReviewError) as e:print('Error:',e,file=sys.stderr);sys.exit(1)
