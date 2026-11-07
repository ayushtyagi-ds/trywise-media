#!/usr/bin/env python3
"""Prepare an evidence capture for drafting. Supplied title/date require verification."""
import argparse,datetime,json,sys
from pathlib import Path

def prepare(capture,title,date):
    if not isinstance(capture,dict) or not all(isinstance(capture.get(k),str) and capture[k].strip() for k in ('source_url','extract','sha256','retrieved_at')): raise ValueError('Invalid capture')
    if not title.strip(): raise ValueError('Title required')
    datetime.date.fromisoformat(date)
    return {'title':title.strip(),'url':capture['source_url'],'published_at':date,'body':capture['extract'],'capture_sha256':capture['sha256'],'retrieved_at':capture['retrieved_at'],'notice':'Verify title, publication date, excerpt context, and each claim against original source.'}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--capture',required=True);p.add_argument('--title',required=True);p.add_argument('--date',required=True,help='publication date YYYY-MM-DD');p.add_argument('--out',required=True);a=p.parse_args()
    result=prepare(json.loads(Path(a.capture).read_text()),a.title,a.date)
    with Path(a.out).open('x') as f: json.dump(result,f,ensure_ascii=False,indent=2)
    print('Prepared evidence; title and date must be independently reviewed.')
if __name__=='__main__':
    try:main()
    except (ValueError,OSError,KeyError) as e: print(f'Error: {e}',file=sys.stderr);sys.exit(1)
