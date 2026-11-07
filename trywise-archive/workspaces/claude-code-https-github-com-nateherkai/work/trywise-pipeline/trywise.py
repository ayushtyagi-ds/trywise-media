#!/usr/bin/env python3
"""Research queue for Trywise AI. Never generates or publishes posts."""
import argparse
import datetime as dt
import email.utils
import hashlib
import json
import re
import sqlite3
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import xml.parsers.expat as expat
from pathlib import Path

MAX_BYTES = 3_000_000
ATOM = '{http://www.w3.org/2005/Atom}'

def canonical(url):
    p = urllib.parse.urlsplit(url.strip())
    if p.scheme not in ('http', 'https') or not p.hostname:
        return None
    query = urllib.parse.parse_qsl(p.query, keep_blank_values=True)
    query = [(k, v) for k, v in query if not (k.lower().startswith('utm_') or k.lower() in ('gclid', 'fbclid'))]
    return urllib.parse.urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path or '/', urllib.parse.urlencode(query), ''))

def plain(el):
    if el is None:
        return ''
    return re.sub(r'\s+', ' ', ''.join(el.itertext())).strip()

def parse_date(value):
    if not value:
        return None
    try:
        value = value.strip()
        if re.match(r'^\d{4}-', value):
            value = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
        else:
            value = email.utils.parsedate_to_datetime(value)
        if value.tzinfo is None:
            value = value.replace(tzinfo=dt.timezone.utc)
        return value.astimezone(dt.timezone.utc).isoformat()
    except (ValueError, TypeError, OverflowError):
        return None

def parse_feed(data, source):
    if len(data) > MAX_BYTES:
        raise ValueError('feed exceeds size limit')
    # Check XML declarations structurally, without mistaking article snippets in
    # CDATA or comments for a real DTD. Reject DTDs before parsing with ET.
    checker = expat.ParserCreate()
    def reject_declaration(*_args):
        raise ValueError('DTD/entity declarations are not supported')
    checker.StartDoctypeDeclHandler = reject_declaration
    checker.EntityDeclHandler = reject_declaration
    checker.ExternalEntityRefHandler = reject_declaration
    try:
        checker.Parse(data, True)
    except expat.ExpatError as exc:
        raise ET.ParseError(str(exc)) from exc
    root = ET.fromstring(data)
    if root.tag == ATOM + 'feed':
        items = root.findall(ATOM + 'entry')
        atom = True
    elif root.tag.lower() == 'rss':
        items = root.findall('./channel/item')
        atom = False
    else:
        raise ValueError('unsupported feed format (expected RSS 2.0 or Atom)')
    for entry in items:
        if atom:
            title = plain(entry.find(ATOM + 'title'))
            candidates = [x for x in entry.findall(ATOM + 'link') if x.get('rel', 'alternate') == 'alternate']
            link = candidates[0].get('href', '') if candidates else ''
            date = plain(entry.find(ATOM + 'published')) or plain(entry.find(ATOM + 'updated'))
        else:
            title = plain(entry.find('title'))
            link = plain(entry.find('link'))
            # Some RSS publishers provide article URLs only as permalink GUIDs.
            guid = entry.find('guid')
            if not link and guid is not None and guid.get('isPermaLink', 'true').lower() == 'true':
                candidate = plain(guid)
                parsed = urllib.parse.urlsplit(candidate)
                if parsed.scheme == 'https' and parsed.netloc:
                    link = candidate
            date = plain(entry.find('pubDate'))
        url = canonical(urllib.parse.urljoin(source, link)) if link else None
        if not title or not url:
            continue
        yield {'id': hashlib.sha256(url.encode()).hexdigest(), 'title': title, 'url': url, 'published_at': parse_date(date), 'source_feed': source}

def fetch(url):
    if not url.startswith('https://'):
        raise ValueError('configured feeds must use HTTPS')
    req = urllib.request.Request(url, headers={'User-Agent':'TrywiseResearch/0.1 (RSS feed reader)', 'Accept':'application/rss+xml, application/atom+xml, application/xml, text/xml'})
    with urllib.request.urlopen(req, timeout=15) as response:
        if urllib.parse.urlsplit(response.geturl()).scheme != 'https':
            raise ValueError('redirected to non-HTTPS URL')
        data = response.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError('feed exceeds size limit')
    return data

def connect(path):
    db = sqlite3.connect(path)
    db.execute('''CREATE TABLE IF NOT EXISTS stories (
       id TEXT PRIMARY KEY, title TEXT NOT NULL, url TEXT NOT NULL UNIQUE,
       published_at TEXT, source_feed TEXT NOT NULL, collected_at TEXT NOT NULL,
       status TEXT NOT NULL DEFAULT 'new', notes TEXT NOT NULL DEFAULT '')''')
    return db

def ingest(db, data, source, cutoff=None):
    # Parse fully before writing so malformed feeds never partially update the queue.
    entries = list(parse_feed(data, source))
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    count = 0
    with db:
        for entry in entries:
            # A feed without a trustworthy date is not automatically fresh.
            if cutoff is not None and (not entry['published_at'] or dt.datetime.fromisoformat(entry['published_at']) < cutoff):
                continue
            cur = db.execute('INSERT OR IGNORE INTO stories (id,title,url,published_at,source_feed,collected_at) VALUES (?,?,?,?,?,?)', (entry['id'], entry['title'], entry['url'], entry['published_at'], entry['source_feed'], now))
            count += cur.rowcount
    return count

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--db', default='queue.sqlite3', help='SQLite queue path')
    sub = ap.add_subparsers(dest='action', required=True)
    p = sub.add_parser('collect', help='fetch sources from JSON config')
    p.add_argument('--config', default='feeds.json')
    p.add_argument('--days', type=int, default=14, help='include dated stories from the last N days (default 14); undated items are skipped')
    p = sub.add_parser('import-feed', help='import a local RSS/Atom file for offline testing')
    p.add_argument('file'); p.add_argument('--source', required=True, help='source feed URL, used to resolve links')
    p = sub.add_parser('list', help='show queue')
    p.add_argument('--status', choices=('new','review','rejected','approved'))
    p.add_argument('--limit', type=int, default=25)
    p = sub.add_parser('mark', help='change a story review status; does not publish')
    p.add_argument('id', help='complete story id')
    p.add_argument('status', choices=('new','review','rejected','approved'))
    p.add_argument('--note', default='')
    args = ap.parse_args()
    db = connect(args.db)
    try:
        if args.action == 'collect':
            if args.days < 1 or args.days > 3650: ap.error('--days must be 1–3650')
            config = json.loads(Path(args.config).read_text(encoding='utf-8'))
            cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=args.days)
            failed = 0
            for feed in config['feeds']:
                try:
                    count = ingest(db, fetch(feed['url']), feed['url'], cutoff=cutoff)
                    print(f"{feed['name']}: {count} new stories")
                except (OSError, ValueError, ET.ParseError, KeyError) as exc:
                    print(f"{feed.get('name', 'feed')}: failed: {exc}", file=sys.stderr)
                    failed += 1
            return 1 if failed else 0
        if args.action == 'import-feed':
            if not canonical(args.source):
                ap.error('--source must be an http(s) URL')
            print(f"{ingest(db, Path(args.file).read_bytes(), args.source)} new stories")
        elif args.action == 'list':
            if args.limit < 1 or args.limit > 1000: ap.error('--limit must be 1–1000')
            sql = 'SELECT id,title,url,published_at,source_feed,collected_at,status,notes FROM stories'
            params = []
            if args.status: sql += ' WHERE status=?'; params.append(args.status)
            sql += ' ORDER BY COALESCE(published_at,collected_at) DESC LIMIT ?'; params.append(args.limit)
            db.row_factory = sqlite3.Row
            print(json.dumps([dict(row) for row in db.execute(sql, params)], ensure_ascii=False, indent=2))
        elif args.action == 'mark':
            with db:
                cursor = db.execute('UPDATE stories SET status=?,notes=? WHERE id=?', (args.status,args.note,args.id))
                if not cursor.rowcount:
                    print('No matching story ID', file=sys.stderr); return 1
            print('Updated; no post was published.')
    finally:
        db.close()
    return 0

if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, json.JSONDecodeError, ET.ParseError, sqlite3.Error) as exc:
        print(f'Error: {exc}', file=sys.stderr); raise SystemExit(1)
