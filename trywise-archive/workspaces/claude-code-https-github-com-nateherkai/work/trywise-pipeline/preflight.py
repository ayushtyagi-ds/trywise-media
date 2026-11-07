#!/usr/bin/env python3
"""Check local readiness without printing credentials or contacting providers."""
import argparse,importlib.util,json,os,sys
from pathlib import Path

def check(environ=None,policy_path=None):
    e=os.environ if environ is None else environ
    checks={'python_3_12_or_later':sys.version_info >= (3,12),
            'pillow_installed':importlib.util.find_spec('PIL') is not None,
            'boto3_installed':importlib.util.find_spec('boto3') is not None,
            'gemini_key_present':bool(e.get('GEMINI_API_KEY')),
            'buffer_key_present':bool(e.get('BUFFER_API_KEY')),
            'r2_key_present':bool(e.get('R2_ACCESS_KEY_ID')) and bool(e.get('R2_SECRET_ACCESS_KEY')),
            'delivery_policy_shape_accepted':False}
    if policy_path:
        try:
            import post_review_worker
            post_review_worker.config_load(policy_path)
            checks['delivery_policy_shape_accepted']=True
        except (OSError,ValueError,KeyError,TypeError):pass
    return {'checks':checks,'note':'Local presence checks only. No secret values shown, no network contacted. Does not validate credentials, account ownership, permissions, provider billing, CAD spending cap, media host, uptime, or publication.'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--policy',help='optional private delivery policy JSON');a=p.parse_args();print(json.dumps(check(policy_path=a.policy),indent=2))
if __name__=='__main__':main()
