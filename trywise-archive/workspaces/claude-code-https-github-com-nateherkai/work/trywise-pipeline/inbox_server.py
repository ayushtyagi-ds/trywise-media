#!/usr/bin/env python3
"""Local inbox for reviewing generated drafts. Never uploads or publishes."""
import argparse,hashlib,hmac,html,json,re,secrets,sqlite3,sys,urllib.parse
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import inbox,review_server

class Server(ThreadingHTTPServer):
    daemon_threads=True
    def __init__(self,db,root,port):
        self.db=Path(db).resolve(strict=True);self.root=Path(root).resolve(strict=True)
        if not self.root.is_dir():raise ValueError('Draft root must be a directory')
        self.token=secrets.token_urlsafe(32)
        super().__init__(('127.0.0.1',port),Handler)
    @property
    def origin(self):return f'http://127.0.0.1:{self.server_address[1]}'
    def find(self,story_id):
        matches=[item for item in inbox.get_items(self.db,self.root) if item['id']==story_id]
        if len(matches)!=1:raise ValueError('Draft not found')
        return matches[0]

class Handler(BaseHTTPRequestHandler):
    def log_message(self,fmt,*args):pass
    def respond(self,status,body,kind='text/plain; charset=utf-8'):
        self.send_response(status);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(body)));self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.send_header('Content-Security-Policy',"default-src 'none'; img-src 'self'; style-src 'unsafe-inline'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'");self.end_headers();self.wfile.write(body)
    def valid_host(self):return self.headers.get('Host')==self.server.origin.removeprefix('http://')
    def do_GET(self):
        if not self.valid_host():return self.respond(403,b'Invalid Host')
        try:
            if self.path=='/':
                jobs=inbox.get_items(self.server.db,self.server.root)
                links=''.join(f'<li><a href="/draft/{j["id"]}">{html.escape(j["title"])}</a> <small>{html.escape(j["status"])}</small></li>' for j in jobs)
                text=('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Trywise inbox</title><style>body{font:17px system-ui;max-width:850px;margin:auto;padding:28px;color:#17243a}li{margin:20px 0}small{color:#566}</style><h1>Trywise review inbox</h1><p>Open a draft to check its source, slides and caption. Recording a review may trigger automatic publishing if you enabled a separate delivery policy.</p><ul>'+(links or '<li>No completed drafts yet.</li>')+'</ul>').encode()
                return self.respond(200,text,'text/html; charset=utf-8')
            m=re.fullmatch(r'/draft/([0-9a-f]{64})',self.path)
            if m:
                item=self.server.find(m.group(1));snap=review_server.snapshot(item['carousel']);page=review_server.page(snap,self.server.token).decode()
                page=page.replace('/slide/',f'/draft/{m.group(1)}/slide/').replace('action="/approve"',f'action="/draft/{m.group(1)}/approve"')
                return self.respond(200,page.encode(),'text/html; charset=utf-8')
            m=re.fullmatch(r'/draft/([0-9a-f]{64})/slide/([1-8])\?digest=([0-9a-f]{64})',self.path)
            if m:
                item=self.server.find(m.group(1));snap=review_server.snapshot(item['carousel']);idx=int(m.group(2))
                if idx>snap['slides'] or not hmac.compare_digest(snap['digest'],m.group(3)):return self.respond(409,b'Draft changed; reload')
                data=review_server.read_file(Path(item['carousel'])/f'{idx:02d}.png',review_server.MAX_IMAGE)
                if hashlib.sha256(data).hexdigest()!=snap['files'][idx+1]['sha256']:return self.respond(409,b'Draft changed; reload')
                return self.respond(200,data,'image/png')
            return self.respond(404,b'Not found')
        except (ValueError,OSError,sqlite3.Error,review_server.ReviewError):return self.respond(400,b'Could not read the draft')
    def do_POST(self):
        if not self.valid_host() or self.headers.get('Origin')!=self.server.origin:return self.respond(403,b'Invalid origin')
        m=re.fullmatch(r'/draft/([0-9a-f]{64})/approve',self.path)
        if not m or self.headers.get_content_type()!='application/x-www-form-urlencoded':return self.respond(400,b'Invalid request')
        try:
            size=int(self.headers.get('Content-Length','-1'))
            if not 0<size<=review_server.MAX_POST:return self.respond(400,b'Invalid request')
            form=urllib.parse.parse_qs(self.rfile.read(size).decode('utf-8'),strict_parsing=True,max_num_fields=8)
            if set(form)!={'token','digest','confirmed'} or any(len(x)!=1 for x in form.values()):return self.respond(400,b'Invalid form')
            if not hmac.compare_digest(form['token'][0],self.server.token) or form['confirmed'][0]!='yes':return self.respond(403,b'Invalid confirmation')
            if not re.fullmatch(r'[0-9a-f]{64}',form['digest'][0]):return self.respond(400,b'Invalid digest')
            item=self.server.find(m.group(1));review_server.write_approval(item['carousel'],form['digest'][0]);return self.respond(200,b'Review saved. If automatic delivery was separately enabled, this draft may now be posted.')
        except (ValueError,OSError,sqlite3.Error,UnicodeError,review_server.ReviewError):return self.respond(409,b'Could not save review; reload and check the draft')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--db',required=True);p.add_argument('--root',required=True);p.add_argument('--port',type=int,default=8765);a=p.parse_args()
    if not 0<=a.port<=65535:p.error('Invalid port')
    server=Server(a.db,a.root,a.port);print(f'Inbox: {server.origin}/ (local only). Ctrl-C to stop.',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
if __name__=='__main__':
    try:main()
    except (OSError,ValueError) as e:print(f'Error: {e}',file=sys.stderr);sys.exit(1)
