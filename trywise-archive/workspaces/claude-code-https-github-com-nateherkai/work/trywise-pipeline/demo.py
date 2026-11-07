#!/usr/bin/env python3
"""Generate a fictional offline Trywise carousel; optionally serve a local review page."""
import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', help='New output directory; defaults to a new temporary directory')
    parser.add_argument('--review', action='store_true', help='Start the local review server after rendering')
    parser.add_argument('--port', type=int, default=8765, help='Local review port (default 8765)')
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error('--port must be 1–65535')
    dest = Path(args.out).expanduser().resolve() if args.out else Path(tempfile.mkdtemp(prefix='trywise-demo-')) / 'draft'
    cmd = [sys.executable, str(ROOT / 'pipeline_runner.py'), '--source', str(ROOT / 'tests' / 'source.json'),
           '--fixture-response', str(ROOT / 'tests' / 'draft-response.json'), '--out', str(dest)]
    try:
        result = subprocess.run(cmd, cwd=ROOT, check=False)
    except OSError as exc:
        print(f'Could not start the demo: {exc}', file=sys.stderr)
        return 1
    if result.returncode:
        return result.returncode
    review_dir = dest / 'carousel'
    print(f'\nFictional demo saved in: {dest}', flush=True)
    print('This is not real news and is not suitable for posting.', flush=True)
    if args.review:
        print(f'Opening a local review server at http://127.0.0.1:{args.port}/', flush=True)
        print('Open that address in your browser. Press Control-C here to stop the server.', flush=True)
        try:
            return subprocess.run([sys.executable, str(ROOT / 'review_server.py'), str(review_dir), '--port', str(args.port)], cwd=ROOT, check=False).returncode
        except KeyboardInterrupt:
            return 0
    print(f'For a review page, run: {sys.executable} {ROOT / "review_server.py"} "{review_dir}" --port {args.port}', flush=True)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
