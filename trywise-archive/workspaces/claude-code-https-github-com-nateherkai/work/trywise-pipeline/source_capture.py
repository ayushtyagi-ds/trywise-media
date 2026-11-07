#!/usr/bin/env python3
"""Capture a reviewable excerpt of an HTTPS source; never publish."""
import argparse, datetime, hashlib, html.parser, json, socket, sys, urllib.parse, urllib.request
from pathlib import Path

MAX_BYTES=2_000_000
class ArticleText(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True); self.skip=0; self.parts=[]
    def handle_starttag(self,tag,attrs):
        if tag.lower() in ('script','style','nav','footer','header','noscript','svg'): self.skip+=1
        if tag.lower() in ('p','h1','h2','h3','li','article'): self.parts.append('\n')
    def handle_endtag(self,tag):
        if tag.lower() in ('script','style','nav','footer','header','noscript','svg') and self.skip: self.skip-=1
        if tag.lower() in ('p','h1','h2','h3','li','article'): self.parts.append('\n')
    def handle_data(self,data):
        if not self.skip: self.parts.append(data)
def extract(data):
    p=ArticleText(); p.feed(data.decode('utf-8','replace'))
    return '\n'.join(' '.join(line.split()) for line in ''.join(p.parts).splitlines() if line.strip())
class RestrictRedirect(urllib.request.HTTPRedirectHandler):
    def __init__(self,allowed): self.allowed=allowed
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        validate_url(newurl,self.allowed)
        return super().redirect_request(req,fp,code,msg,headers,newurl)
def validate_url(url,allowed):
    p=urllib.parse.urlsplit(url)
    if p.scheme!='https' or p.hostname not in allowed or p.username or p.password or p.port not in (None,443):
        raise ValueError('URL must be HTTPS on a configured allowed host')
    return url
def capture(url,allowed):
    validate_url(url,allowed)
    opener=urllib.request.build_opener(RestrictRedirect(allowed))
    req=urllib.request.Request(url,headers={'User-Agent':'TrywiseResearch/0.1','Accept':'text/html'})
    with opener.open(req,timeout=15) as r:
        final=validate_url(r.geturl(),allowed)
        if r.headers.get_content_type() not in ('text/html','application/xhtml+xml'):
            raise ValueError('source is not HTML')
        data=r.read(MAX_BYTES+1)
    if len(data)>MAX_BYTES: raise ValueError('source too large')
    content=extract(data)
    if len(content)<80: raise ValueError('article extraction too short; manual review required')
    return {'source_url':final,'retrieved_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sha256':hashlib.sha256(data).hexdigest(),'extract':content[:20000],'truncated':len(content)>20000,'notice':'Untrusted extracted source text. Verify claims against original page before publishing.'}
def main():
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('url'); ap.add_argument('--allow-host',action='append',required=True); ap.add_argument('--out',required=True)
    a=ap.parse_args(); result=capture(a.url,set(a.allow_host)); Path(a.out).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8'); print('Captured source for review; no post generated.')
if __name__=='__main__':
    try: main()
    except (ValueError,OSError,socket.timeout) as e: print(f'Capture failed: {e}',file=sys.stderr);sys.exit(1)
