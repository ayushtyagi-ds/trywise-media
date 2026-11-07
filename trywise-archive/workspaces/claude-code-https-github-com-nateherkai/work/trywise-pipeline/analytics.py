#!/usr/bin/env python3
"""Summarize manually exported per-post metrics; no account connection."""
import argparse,csv,json,sys
from collections import defaultdict

def analyze(rows):
    groups=defaultdict(lambda: {'posts':0,'reach':0,'saves':0,'shares':0,'profile_visits':0,'post_follows':0})
    for row in rows:
        topic=row.get('format','').strip()
        if not topic:raise ValueError('Each row requires format')
        v={}
        for k in ('reach','saves','shares','profile_visits','post_follows'):
            raw=row.get(k,'')
            if not isinstance(raw,str) or not raw.isdecimal():raise ValueError(f'{k} must be a nonnegative integer')
            v[k]=int(raw)
        g=groups[topic];g['posts']+=1
        for k in v:g[k]+=v[k]
    out=[]
    for topic,g in sorted(groups.items()):
        r=g['reach'];out.append({'format':topic,**g,'saves_per_1000_reach':round(1000*g['saves']/r,2) if r else None,'shares_per_1000_reach':round(1000*g['shares']/r,2) if r else None,'post_follows_per_1000_reach':round(1000*g['post_follows']/r,2) if r else None})
    return {'groups':out,'note':'Use comparable measurement windows. Summed per-post reach may count the same person multiple times. Post-attributed follows are not net account follows; missing metrics must not be entered as zero.'}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('csv_file');a=p.parse_args()
    with open(a.csv_file,encoding='utf-8-sig',newline='') as f:print(json.dumps(analyze(csv.DictReader(f)),indent=2))
if __name__=='__main__':
    try:main()
    except (ValueError,OSError) as e:print('Error:',e,file=sys.stderr);sys.exit(1)
