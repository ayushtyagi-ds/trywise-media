#!/usr/bin/env python3
"""Local carousel review. Approves exact local files; never publishes."""
import argparse
import datetime as dt
import hashlib
import hmac
import html
import json
import os
import re
import secrets
import stat
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

MAX_SLIDES = 8
MAX_IMAGE = 10_000_000
MAX_TEXT = 100_000
MAX_POST = 4096

class ReviewError(ValueError): pass

def read_file(path, limit):
    # Reject symlinks and non-regular files. Bound before and during the read.
    flags = os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0)
    try:
        fd = os.open(path, flags)
        with os.fdopen(fd, 'rb') as f:
            st = os.fstat(f.fileno())
            if not stat.S_ISREG(st.st_mode) or st.st_size > limit:
                raise ReviewError('Invalid or oversized review file')
            data = f.read(limit + 1)
    except OSError:
        raise ReviewError('Review file missing or unsafe') from None
    if len(data) > limit: raise ReviewError('Review file too large')
    return data

def snapshot(directory):
    directory = Path(directory)
    if not directory.is_dir(): raise ReviewError('Review directory does not exist')
    manifest_bytes = read_file(directory / 'manifest.json', MAX_TEXT)
    caption_bytes = read_file(directory / 'caption.txt', MAX_TEXT)
    try:
        manifest = json.loads(manifest_bytes)
        caption = caption_bytes.decode('utf-8')
    except (ValueError, UnicodeError): raise ReviewError('Invalid manifest or caption') from None
    if not isinstance(manifest,dict) or manifest.get('status') != 'needs_review':
        raise ReviewError('Manifest must be marked needs_review')
    n = manifest.get('slides')
    if type(n) is not int or not 1 <= n <= MAX_SLIDES: raise ReviewError('Invalid slide count')
    if not caption.strip(): raise ReviewError('Caption is empty')
    if not isinstance(manifest.get('source'), dict): raise ReviewError('Invalid source')
    entries = [('manifest.json', manifest_bytes), ('caption.txt',caption_bytes)]
    for i in range(1,n+1):
        name=f'{i:02d}.png'; data=read_file(directory/name,MAX_IMAGE)
        if not data.startswith(b'\x89PNG\r\n\x1a\n'): raise ReviewError('Slide is not a PNG')
        entries.append((name,data))
    # Include names and hashes to bind both content and sequence unambiguously.
    files = [{'name':n, 'sha256':hashlib.sha256(d).hexdigest()} for n,d in entries]
    canonical=json.dumps({'version':1,'files':files},sort_keys=True,separators=(',',':')).encode()
    return {'digest':hashlib.sha256(canonical).hexdigest(),'files':files,'caption':caption,'manifest':manifest,'slides':n}

def write_approval(directory, expected):
    snap=snapshot(directory)
    if not hmac.compare_digest(snap['digest'],expected):
        raise ReviewError('Content changed since it was displayed. Reload and review again.')
    record={'type':'local_content_review','version':1,'digest':snap['digest'], 'files':snap['files'],
            'reviewed_at':dt.datetime.now(dt.timezone.utc).isoformat(),
            'scope':'Local file contents only; no destination or publishing approval.'}
    path=Path(directory)/'approval.json'
    try:
        fd=os.open(path, os.O_WRONLY|os.O_CREAT|os.O_EXCL | getattr(os,'O_NOFOLLOW',0),0o600)
        with os.fdopen(fd,'w',encoding='utf-8') as f:
            json.dump(record,f,indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    except FileExistsError: raise ReviewError('An approval already exists; create a fresh review folder for another review.') from None
    except OSError: raise ReviewError('Could not save approval') from None
    return record

def page(snap, token):
    esc=lambda s:html.escape(str(s),quote=True)
    slides=''.join(f'<section><h2>Slide {i}</h2><img src="/slide/{i}?digest={snap['digest']}" alt="Carousel slide {i}" loading="lazy"></section>' for i in range(1,snap['slides']+1))
    claims=snap['manifest'].get('claims',[]); notes=snap['manifest'].get('review_notes',[])
    if not isinstance(claims,list) or not isinstance(notes,list): raise ReviewError('Invalid evidence')
    claims_html=''.join(f'<li><strong>{esc(c.get("text", ""))}</strong><br>Source excerpt: {esc(c.get("evidence", ""))}</li>' for c in claims if isinstance(c,dict))
    notes_html=''.join(f'<li>{esc(n)}</li>' for n in notes if isinstance(n,str))
    evidence_html='<h2>Evidence to check</h2><p>Excerpts may be incomplete and do not verify all slide or caption claims. Check the original source.</p><ul>'+ (claims_html or '<li>No evidence provided: check the source manually.</li>') +'</ul><h2>Review notes</h2><ul>'+(notes_html or '<li>No notes supplied.</li>')+'</ul>'
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Trywise review</title><style>body{{font:16px system-ui;margin:auto;max-width:900px;padding:24px;color:#18233a;background:#f4f5f7}}h1{{margin-bottom:0}}.note{{padding:16px;background:#fff0c3}}img{{max-width:420px;width:100%;border:1px solid #ccd4dd}}pre{{white-space:pre-wrap;background:white;padding:20px;overflow-wrap:anywhere}}button{{background:#142442;color:white;border:0;border-radius:6px;padding:14px;font-size:16px;cursor:pointer}}code{{overflow-wrap:anywhere}}section{{margin:20px 0}}</style></head><body><h1>Trywise carousel review</h1><p class="note"><strong>Review only.</strong> Check every claim, source, image, and caption. Approval saves a local record for these exact files. If you separately enabled automatic delivery, this review can trigger a post to your configured channel.</p><p>Source: {esc(snap['manifest'].get('source',{}).get('title',''))} · {esc(snap['manifest'].get('source',{}).get('url',''))}</p><p>Content digest: <code>{snap['digest']}</code></p>{slides}{evidence_html}<h2>Caption</h2><pre>{esc(snap['caption'])}</pre><form method="post" action="/approve"><input type="hidden" name="token" value="{token}"><input type="hidden" name="digest" value="{snap['digest']}"><label><input type="checkbox" name="confirmed" value="yes" required> I reviewed the claims, source, slides and caption.</label><p><button type="submit">Record local review</button></p></form></body></html>'''.encode()

class ReviewServer(ThreadingHTTPServer):
    daemon_threads=True
    def __init__(self, directory, port=0):
        self.directory=Path(directory).resolve(strict=True)
        if not self.directory.is_dir(): raise ReviewError('Review directory must be a directory')
        self.token=secrets.token_urlsafe(32)
        super().__init__(('127.0.0.1', port), Handler)
    @property
    def origin(self): return f'http://127.0.0.1:{self.server_address[1]}'

class Handler(BaseHTTPRequestHandler):
    server_version='TrywiseReview/1'
    def log_message(self,fmt,*args): pass
    def response(self,status,body,typ='text/plain; charset=utf-8'):
        self.send_response(status); self.send_header('Content-Type',typ); self.send_header('Content-Length',str(len(body)))
        self.send_header('Cache-Control','no-store'); self.send_header('X-Content-Type-Options','nosniff'); self.send_header('Content-Security-Policy',"default-src 'none'; img-src 'self'; style-src 'unsafe-inline'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'")
        self.end_headers(); self.wfile.write(body)
    def host_ok(self): return self.headers.get('Host') == self.server.origin.removeprefix('http://')
    def do_GET(self):
        if not self.host_ok(): return self.response(403,b'Invalid Host')
        try:
            if self.path == '/': return self.response(200,page(snapshot(self.server.directory),self.server.token),'text/html; charset=utf-8')
            m=re.fullmatch(r'/slide/([1-8])\?digest=([0-9a-f]{64})',self.path)
            if m:
                index=int(m.group(1)); snap=snapshot(self.server.directory)
                if index>snap['slides']: return self.response(404,b'Not found')
                if not hmac.compare_digest(m.group(2),snap['digest']): return self.response(409,b'Files changed; reload to review')
                data=read_file(self.server.directory/f'{index:02d}.png',MAX_IMAGE)
                if hashlib.sha256(data).hexdigest()!=snap['files'][index+1]['sha256']: return self.response(409,b'Files changed; reload to review')
                return self.response(200,data,'image/png')
            return self.response(404,b'Not found')
        except ReviewError as exc: return self.response(400,str(exc).encode())
    def do_POST(self):
        if not self.host_ok() or self.headers.get('Origin') != self.server.origin:
            return self.response(403,b'Invalid origin')
        if self.path != '/approve': return self.response(404,b'Not found')
        if self.headers.get_content_type() != 'application/x-www-form-urlencoded': return self.response(400,b'Invalid form')
        try:
            length=int(self.headers.get('Content-Length','-1'))
            if not 0 < length <= MAX_POST: return self.response(400,b'Invalid form length')
            form=urllib.parse.parse_qs(self.rfile.read(length).decode('utf-8'),strict_parsing=True,max_num_fields=8)
            if any(len(v)!=1 for v in form.values()) or set(form)!={'token','digest','confirmed'}:
                return self.response(400,b'Invalid form fields')
            if not hmac.compare_digest(form['token'][0],self.server.token) or form['confirmed'][0]!='yes':
                return self.response(403,b'Invalid token or confirmation')
            if not re.fullmatch(r'[0-9a-f]{64}',form['digest'][0]): return self.response(400,b'Invalid digest')
            write_approval(self.server.directory,form['digest'][0])
            return self.response(200,b'Review saved locally. Nothing was posted.')
        except (ValueError,UnicodeError,ReviewError) as exc: return self.response(409,str(exc).encode())

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('directory');p.add_argument('--port',type=int,default=8765);a=p.parse_args()
    if not 0<=a.port<=65535: p.error('Port must be 0-65535')
    server=ReviewServer(a.directory,a.port)
    print(f'Review at {server.origin}/ (local access only). Press Ctrl+C to stop.',flush=True)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()
if __name__=='__main__':
    try: main()
    except (OSError,ReviewError) as exc: print(f'Error: {exc}',file=sys.stderr);sys.exit(1)
