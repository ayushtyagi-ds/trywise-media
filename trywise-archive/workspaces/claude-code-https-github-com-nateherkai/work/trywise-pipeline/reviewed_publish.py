#!/usr/bin/env python3
"""Bridge approved local carousel to a guarded Buffer submission; no auto-posts."""
import argparse
import hmac
import json
import os
import re
import sys

import buffer_adapter
import buffer_publish
import review_bridge
import review_server


def load_spec(path):
    raw=review_server.read_file(path,review_bridge.MAX_INPUT)
    try: obj=json.loads(raw)
    except (ValueError,UnicodeError): raise ValueError('Input must be valid JSON') from None
    if not isinstance(obj,dict): raise ValueError('Input must be a JSON object')
    return obj


def prepare(carousel,spec,allowed_hosts,fetcher=review_bridge.fetch_public_png):
    return review_bridge.create_manifest(carousel,spec.get('channel_id'),spec.get('image_urls'),allowed_hosts,fetcher)


def submit_reviewed(carousel,spec,allowed_hosts,digest,key,db_path,fetcher=review_bridge.fetch_public_png,transport=buffer_publish.post_once):
    if not key: raise ValueError('BUFFER_API_KEY is required')
    if not isinstance(digest,str) or not re.fullmatch(r'[0-9a-fA-F]{64}',digest):
        raise ValueError('A valid Buffer manifest digest is required')
    # Fetch and compare all hosted bytes again, immediately before reservation/sending.
    manifest=prepare(carousel,spec,allowed_hosts,fetcher)
    actual=buffer_adapter.manifest_digest(manifest)
    if not hmac.compare_digest(actual,digest.lower()):
        raise ValueError('Approved digest does not match current channel, caption and URLs')
    db=buffer_publish.database(db_path)
    try:
        return buffer_publish.send(db,manifest,digest,key,transport=transport)
    finally:
        db.close()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='action',required=True)
    for name in ('preview','send'):
        p=sub.add_parser(name)
        p.add_argument('--carousel',required=True)
        p.add_argument('--input',required=True,help='JSON with channel_id and ordered image_urls')
        p.add_argument('--allow-host',action='append',required=True)
        p.add_argument('--ack-public-media',action='store_true')
        if name=='send':
            p.add_argument('--approved-digest',required=True)
            p.add_argument('--db',required=True,help='durable SQLite ledger shared by all runners')
            p.add_argument('--send',action='store_true')
    args=parser.parse_args()
    if not args.ack_public_media: raise ValueError('Public media acknowledgement is required')
    if args.action=='send' and not args.send: raise ValueError('Explicit --send is required')
    spec=load_spec(args.input)
    if args.action=='preview':
        manifest=prepare(args.carousel,spec,args.allow_host)
        print(json.dumps({'manifest':manifest,'note':'Preview only; no post was created. Review destination and public media before separately authorizing any send.'},ensure_ascii=False,indent=2))
        return 0
    result=submit_reviewed(args.carousel,spec,args.allow_host,args.approved_digest,os.getenv('BUFFER_API_KEY'),args.db)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result['state']=='confirmed' else 2

if __name__=='__main__':
    try: sys.exit(main())
    except (ValueError,OSError,review_server.ReviewError) as e:
        print('Error:',e,file=sys.stderr);sys.exit(1)
