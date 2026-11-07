#!/usr/bin/env python3
"""Create a review-only carousel from a source; never posts or approves content."""
import argparse, datetime as dt, hashlib, json, os, shutil, sys, tempfile
from pathlib import Path

import draftgen
import render_carousel
import source_capture

class RunError(ValueError):
    pass

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def run(args):
    dest = Path(args.out)
    if dest.exists():
        raise RunError('Output already exists')
    if args.url and args.fixture_response:
        raise RunError('Fixture mode requires a local source, so it stays offline')
    if args.url and (not args.allow_host or not args.title or not args.published_at):
        raise RunError('--url requires --allow-host, --title and --published-at')
    if args.live and (not args.model or not args.ack_data):
        raise RunError('--live requires --model and --ack-data')
    if args.live and not os.environ.get('GEMINI_API_KEY'):
        raise RunError('GEMINI_API_KEY environment variable is required')
    # Create a sibling staging directory; never expose partial output as complete.
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix='.trywise-run-', dir=dest.parent))
    try:
        if args.url:
            capture = source_capture.capture(args.url, set(args.allow_host))
            (tmp/'capture.json').write_text(json.dumps(capture, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
            source = draftgen.read_input(tmp/'capture.json', args.title, args.published_at)
        else:
            source = draftgen.read_input(args.source, args.title, args.published_at)
        if args.live:
            generated = draftgen.request_live(source, args.model, os.environ['GEMINI_API_KEY'])
        else:
            raw = Path(args.fixture_response).read_bytes()
            if len(raw) > draftgen.MAX_RESPONSE_BYTES:
                raise RunError('Fixture exceeds size limit')
            generated = json.loads(raw)
        draft = draftgen.validate_generated(generated, source)
        (tmp/'draft.json').write_text(json.dumps(draft, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        render_carousel.render(draft, tmp/'carousel')
        files = ['draft.json'] + (['capture.json'] if args.url else []) + [str(p.relative_to(tmp)) for p in sorted((tmp/'carousel').iterdir()) if p.is_file()]
        receipt = {'status':'needs_review', 'mode':'live' if args.live else 'fixture_offline',
                   'source_url':source['url'], 'generated_at':dt.datetime.now(dt.timezone.utc).isoformat(),
                   'files_sha256':{name:sha(tmp/name) for name in files},
                   'warning':'Verify every claim, source date, content rights and slide before any publishing. No post has been scheduled or sent.'}
        (tmp/'receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        # Reserve the final directory exclusively; an existing output is never overwritten.
        dest.mkdir()
        try:
            for p in tmp.iterdir():
                if p.name != 'receipt.json': shutil.move(str(p), dest/p.name)
            # Final commit marker is written last: readers must require receipt.json.
            shutil.move(str(tmp/'receipt.json'), dest/'receipt.json')
        except Exception:
            shutil.rmtree(dest, ignore_errors=True)
            raise
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return dest

def main():
    p=argparse.ArgumentParser(description=__doc__)
    source=p.add_mutually_exclusive_group(required=True)
    source.add_argument('--source', help='local source or source-capture JSON')
    source.add_argument('--url', help='public source URL, requires allowlisted host and verified title/date')
    mode=p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--fixture-response', help='local generated JSON; no network')
    mode.add_argument('--live', action='store_true',help='call Gemini; possibly billable')
    p.add_argument('--out',required=True,help='new output directory')
    p.add_argument('--allow-host',action='append',help='permitted HTTPS host; repeat for allowed redirects')
    p.add_argument('--title',help='manually verified title for captured source')
    p.add_argument('--published-at',help='manually verified publication date for captured source')
    p.add_argument('--model',help='explicitly chosen Gemini model for live generation')
    p.add_argument('--ack-data',action='store_true',help='send the source to Google; charges may apply')
    args=p.parse_args()
    try:
        path=run(args)
        print(f'Review-only draft created at {path}. No content was published.')
        return 0
    except (OSError,ValueError,KeyError,json.JSONDecodeError,draftgen.DraftError) as exc:
        print(f'Pipeline failed: {exc}',file=sys.stderr)
        return 1
if __name__=='__main__': raise SystemExit(main())
