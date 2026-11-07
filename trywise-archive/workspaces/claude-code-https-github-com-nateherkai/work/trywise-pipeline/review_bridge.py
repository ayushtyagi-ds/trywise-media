#!/usr/bin/env python3
"""Compare approved local slides to hosted images; create a Buffer preview manifest.

Never schedules or publishes. Hosted images remain mutable after verification.
"""
import argparse
import datetime as dt
import hashlib
import hmac
import http.client
import ipaddress
import json
import os
import re
import socket
import ssl
import sys
import urllib.parse
from pathlib import Path

import buffer_adapter
import review_server

MAX_RESPONSE = review_server.MAX_IMAGE
MAX_INPUT = 100_000


def public_ip(address):
    try:
        ip = ipaddress.ip_address(address.split('%', 1)[0])
    except ValueError:
        return False
    if getattr(ip, 'ipv4_mapped', None):
        return public_ip(str(ip.ipv4_mapped))
    return ip.is_global and not (ip.is_multicast or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_unspecified)


def checked_url(url, allowed_hosts):
    if not isinstance(url, str) or len(url) > 2000 or any(c.isspace() for c in url):
        raise ValueError('Image URL must be a short valid URL')
    try:
        p = urllib.parse.urlsplit(url)
        host = p.hostname
        if (p.scheme != 'https' or not host or p.username or p.password or p.port not in (None, 443)
                or p.query or p.fragment or not p.path or host.lower() not in allowed_hosts):
            raise ValueError('Image URL must use an explicitly allowed HTTPS host and have no credentials, query or fragment')
        try:
            ipaddress.ip_address(host)
        except ValueError:
            pass
        else:
            raise ValueError('Literal IP addresses are not supported')
        if not re.fullmatch(r'[a-z0-9.-]+', host) or '..' in host or '.' not in host:
            raise ValueError('Invalid public hostname')
        return host, p.path
    except ValueError:
        raise ValueError('Image URL must use an explicitly allowed public HTTPS host without credentials, query or fragment') from None


def fetch_public_png(url, allowed_hosts):
    host, path = checked_url(url, allowed_hosts)
    # Refuse any DNS result that isn't publicly routable, then pin the selected
    # address for the connection while keeping TLS hostname verification.
    try:
        addresses = {item[4][0] for item in socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)}
    except OSError:
        raise ValueError('Image host could not be resolved') from None
    if not addresses or not all(public_ip(a) for a in addresses):
        raise ValueError('Image host resolves to a non-public address')
    address = sorted(addresses)[0]
    connection = http.client.HTTPSConnection(host, 443, timeout=15, context=ssl.create_default_context())
    connection._create_connection = lambda _addr, timeout=socket._GLOBAL_DEFAULT_TIMEOUT, source_address=None: socket.create_connection((address, 443), timeout, source_address)
    try:
        connection.request('GET', path, headers={'Accept':'image/png','User-Agent':'TrywiseReview/1'})
        response = connection.getresponse()
        # This direct client does not follow redirects; destination remains the one approved host.
        if response.status != 200:
            raise ValueError('Image URL did not return HTTP 200 (redirects are not followed)')
        if response.headers.get_content_type() != 'image/png':
            raise ValueError('Image URL did not return image/png')
        length = response.getheader('Content-Length')
        if length is not None:
            try: length = int(length)
            except ValueError: raise ValueError('Invalid image Content-Length') from None
            if length < 0 or length > MAX_RESPONSE: raise ValueError('Hosted image exceeds size limit')
        body = response.read(MAX_RESPONSE + 1)
        if len(body) > MAX_RESPONSE: raise ValueError('Hosted image exceeds size limit')
        if not body.startswith(b'\x89PNG\r\n\x1a\n'): raise ValueError('Hosted image is not PNG')
        return body
    except (OSError, http.client.HTTPException, ssl.SSLError):
        raise ValueError('Could not fetch a hosted image securely') from None
    finally:
        connection.close()


def verify_approval(directory):
    snap = review_server.snapshot(directory)
    try:
        approval = json.loads(review_server.read_file(Path(directory)/'approval.json', review_server.MAX_TEXT))
    except (ValueError, UnicodeError):
        raise ValueError('Invalid local approval record') from None
    if (not isinstance(approval, dict) or approval.get('type') != 'local_content_review'
            or approval.get('version') != 1 or not isinstance(approval.get('digest'), str)
            or not hmac.compare_digest(approval['digest'], snap['digest'])
            or approval.get('files') != snap['files']):
        raise ValueError('Local content has changed or approval does not match')
    return snap


def create_manifest(directory, channel_id, image_urls, allowed_hosts, fetcher=fetch_public_png):
    allowed = {h.lower() for h in allowed_hosts}
    if not allowed: raise ValueError('At least one explicitly trusted image host is required')
    snap = verify_approval(directory)
    if not isinstance(image_urls, list) or len(image_urls) != snap['slides']:
        raise ValueError('Image URL count must match the approved slide count')
    manifest = buffer_adapter.validate_manifest({'channel_id': channel_id,'caption': snap['caption'],'image_urls': image_urls})
    hosted = []
    for index, url in enumerate(image_urls):
        checked_url(url, allowed)
        data = fetcher(url, allowed)
        if not isinstance(data, bytes) or len(data) > MAX_RESPONSE: raise ValueError('Hosted image could not be verified')
        digest = hashlib.sha256(data).hexdigest()
        expected = snap['files'][index + 2]['sha256']
        if not hmac.compare_digest(digest, expected):
            raise ValueError(f'Hosted image {index + 1} differs from approved slide')
        hosted.append({'url': url, 'sha256': digest})
    # Any local edit during fetch invalidates the preview.
    if not hmac.compare_digest(verify_approval(directory)['digest'], snap['digest']):
        raise ValueError('Local files changed while hosted images were checked')
    manifest['_review_verification'] = {
        'verified_at': dt.datetime.now(dt.timezone.utc).isoformat(),
        'local_content_digest': snap['digest'],
        'buffer_manifest_digest': buffer_adapter.manifest_digest(manifest),
        'hosted_slides': hosted,
        'notice': 'Matches checked at this time only. URLs may change later; no post was submitted or approved for publication.'}
    return manifest


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--carousel', required=True, help='Directory with content and local approval.json')
    p.add_argument('--input', required=True, help='JSON with channel_id and image_urls')
    p.add_argument('--allow-host', action='append', required=True, help='Trusted HTTPS image host; repeat as needed')
    p.add_argument('--ack-public-media', action='store_true', help='Acknowledge images are publicly reachable')
    p.add_argument('--out', required=True, help='New Buffer manifest file; never overwritten')
    a = p.parse_args()
    if not a.ack_public_media: raise ValueError('Hosted media is public; --ack-public-media is required')
    data = review_server.read_file(a.input, MAX_INPUT)
    try: spec = json.loads(data)
    except (ValueError, UnicodeError): raise ValueError('Input must be valid JSON') from None
    if not isinstance(spec, dict): raise ValueError('Input must be an object')
    result = create_manifest(a.carousel, spec.get('channel_id'), spec.get('image_urls'), a.allow_host)
    target = Path(a.out)
    try:
        fd = os.open(target, os.O_WRONLY|os.O_CREAT|os.O_EXCL|getattr(os,'O_NOFOLLOW',0),0o600)
        with os.fdopen(fd,'w',encoding='utf-8') as f:
            json.dump(result,f,ensure_ascii=False,indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    except OSError:
        raise ValueError('Could not create new output file') from None
    print('Hosted images matched reviewed local files. Preview manifest created; nothing was posted.')
    print('Buffer manifest digest:', result['_review_verification']['buffer_manifest_digest'])

if __name__ == '__main__':
    try: main()
    except (ValueError, OSError, review_server.ReviewError) as e:
        print('Error:',e,file=sys.stderr); sys.exit(1)
