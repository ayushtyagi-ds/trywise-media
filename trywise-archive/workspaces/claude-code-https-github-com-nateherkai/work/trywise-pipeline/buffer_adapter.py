#!/usr/bin/env python3
"""Buffer preview and read-only account inspection; cannot create posts."""
import argparse
import hashlib
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ENDPOINT = 'https://api.buffer.com'
MAX_RESPONSE_BYTES = 1_000_000

# A preview is deliberately not executable by this program. Verify schema and
# carousel support on your own account before adding any createPost operation.
CREATE_POST = '''mutation CreatePost($input: CreatePostInput!) {
  createPost(input: $input) {
    ... on PostActionSuccess { post { id dueAt } }
    ... on MutationError { message }
  }
}'''
ACCOUNT_QUERY = '''query { account { organizations { id name } } }'''
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


POST_STATUS_QUERY = '''query PostStatus($input: PostInput!) {
  post(input: $input) { id channelId status dueAt sentAt schedulingType }
}'''


CHANNEL_QUERY = '''query GetChannels($organizationId: OrganizationId!) {
  channels(input: { organizationId: $organizationId }) {
    id name displayName service isQueuePaused
  }
}'''


def validate_manifest(manifest):
    if not isinstance(manifest, dict):
        raise ValueError('manifest must be a JSON object')
    channel = manifest.get('channel_id')
    caption = manifest.get('caption')
    urls = manifest.get('image_urls')
    if not isinstance(channel, str) or not channel.strip() or len(channel) > 200:
        raise ValueError('channel_id must be a nonempty string')
    if not isinstance(caption, str) or not caption.strip() or len(caption) > 2200:
        raise ValueError('caption must be nonempty and at most 2200 characters')
    if not isinstance(urls, list) or not (1 <= len(urls) <= 20):
        raise ValueError('image_urls must contain 1 to 20 image URLs')
    for url in urls:
        if not isinstance(url, str) or len(url) > 2000:
            raise ValueError('each image URL must be a short text URL')
        parts = urllib.parse.urlsplit(url)
        # Do not leak tokens/signed URLs. Reachability and rights are not checked.
        if (parts.scheme != 'https' or not parts.hostname or parts.username or
            parts.password or parts.query or parts.fragment or not parts.path or
            any(c.isspace() for c in url)):
            raise ValueError('each image URL must be a direct HTTPS URL without credentials, query, or fragment')
    return {'channel_id': channel, 'caption': caption, 'image_urls': urls}


def payload_for_preview(manifest):
    m = validate_manifest(manifest)
    data = {'text': m['caption'], 'channelId': m['channel_id'],
            'schedulingType': 'automatic', 'mode': 'addToQueue', 'needsApproval': False,
            'metadata': {'instagram': {'type': 'post', 'shouldShareToFeed': True}},
            'assets': [{'image': {'url': url}} for url in m['image_urls']]}
    return {'query': CREATE_POST, 'variables': {'input': data}}


def manifest_digest(manifest):
    canon = json.dumps(validate_manifest(manifest), sort_keys=True, ensure_ascii=False,
                       separators=(',', ':')).encode('utf-8')
    return hashlib.sha256(canon).hexdigest()


def read_only_query(query, variables=None):
    # This function only permits constants defined in this module and cannot send mutations.
    if query not in (ACCOUNT_QUERY, CHANNEL_QUERY, POST_STATUS_QUERY):
        raise ValueError('only built-in read-only queries are allowed')
    key = os.environ.get('BUFFER_API_KEY')
    if not key:
        raise ValueError('BUFFER_API_KEY environment variable is missing')
    data = json.dumps({'query': query, 'variables': variables or {}}).encode('utf-8')
    req = urllib.request.Request(ENDPOINT, data=data,
            headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {key}'}, method='POST')
    try:
        with urllib.request.build_opener(NoRedirect()).open(req, timeout=15) as response:
            raw = response.read(MAX_RESPONSE_BYTES + 1)
    except (urllib.error.URLError, TimeoutError, OSError):
        # Avoid printing server error bodies, request details, or secrets.
        raise RuntimeError('Buffer read-only request failed; check connectivity and credentials') from None
    if len(raw) > MAX_RESPONSE_BYTES:
        raise RuntimeError('Buffer response exceeds size limit')
    try:
        result = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise RuntimeError('Buffer returned an invalid response') from None
    if not isinstance(result, dict) or result.get('errors') or not isinstance(result.get('data'), dict):
        raise RuntimeError('Buffer query returned an error; check credentials and account access')
    return result['data']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    preview = sub.add_parser('preview', help='Validate JSON and print a NON-EXECUTING request preview')
    preview.add_argument('manifest', type=Path)
    sub.add_parser('organizations', help='Make one read-only API query')
    status = sub.add_parser('post-status', help='Read status of one existing Buffer post')
    status.add_argument('post_id')
    channels = sub.add_parser('channels', help='Make one read-only API query')
    channels.add_argument('organization_id')
    args = parser.parse_args()
    try:
        if args.command == 'preview':
            manifest = json.loads(args.manifest.read_text(encoding='utf-8'))
            output = {'execution': 'preview only; no request sent',
                      'sha256_of_validated_manifest': manifest_digest(manifest),
                      'checks_not_performed': ['approval', 'rights', 'public reachability', 'Buffer or Instagram account eligibility', 'Instagram carousel support'],
                      'payload': payload_for_preview(manifest)}
        elif args.command == 'organizations':
            output = read_only_query(ACCOUNT_QUERY)
        elif args.command == 'channels':
            output = read_only_query(CHANNEL_QUERY, {'organizationId': args.organization_id})
        else:
            if not args.post_id.strip() or len(args.post_id) > 200:
                raise ValueError('A valid Buffer post ID is required')
            output = read_only_query(POST_STATUS_QUERY, {'input': {'id': args.post_id}})
            post = output.get('post')
            if not isinstance(post, dict) or post.get('id') != args.post_id:
                raise RuntimeError('Buffer returned an invalid post status')
            output = {'buffer_report': post, 'note': 'Buffer status is not independent proof of visibility on Instagram; check the social account.'}
        print(json.dumps(output, ensure_ascii=False, indent=2))
    except (ValueError, RuntimeError, OSError, json.JSONDecodeError) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 1
    return 0

if __name__ == '__main__':
    sys.exit(main())
