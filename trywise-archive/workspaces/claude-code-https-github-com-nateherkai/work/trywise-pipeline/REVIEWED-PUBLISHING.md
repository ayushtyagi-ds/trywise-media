# Approved carousel → verified Buffer submission prototype

`review_bridge.py` and `reviewed_publish.py` connect local review to an explicit Buffer submission. They are not deployed, independently audited, or live-tested. No tests send posts. Buffer API credentials, image hosting, account access and platform eligibility remain unverified.

## What the bridge checks

- A `review_server.py` `approval.json` exists and matches a fresh snapshot of the current caption, manifest, and numbered PNG slides. This is a local file record, not cryptographic identity or evidence of factual accuracy.
- The supplied public PNG URLs resolve only to global addresses, use explicitly allowlisted exact HTTPS hostnames, valid TLS, no credentials/query parameters or unusual ports, and do not redirect. The network connection is pinned to a public DNS answer for that request. This restricts exposure but is not an independent network security audit.
- Each fetched image's SHA-256 equals its approved local slide. The caption comes from the approved local file, never from the supplied URL mapping. Checks are repeated immediately before an explicit send. Output and audit details avoid API credentials.
- A separate Buffer manifest digest binds destination channel, caption, URLs and their order. That digest is distinct from the local content review digest. The user must review destination and URLs and explicitly approve the digest before sending. The persistent `buffer_publish.py` ledger prevents blind repeat sends for a given digest.

**Limits:** hosted images become public before publication. A URL's bytes can change or disappear between verification and Buffer fetching it; matching now cannot prove future immutability. Use trusted, immutable, content-addressed storage, keep files available until publication, and verify final posts. Different URLs or changed caption can evade duplicate detection; multiple ledgers break it. Timeouts/pending/unknown require manual Buffer reconciliation, never an automatic retry. `confirmed` means Buffer accepted a request, not that Instagram published. Direct use of older `buffer_publish.py` does not enforce this bridge; use the reviewed path below. Local host resolution safeguards do not replace network isolation. No source truth, usage rights, account restrictions, scheduling policies or spending controls are automatically verified.

## Prepare

Create an approved carousel with `review_server.py` (see REVIEW.md). Upload the exact approved slides to a trusted public HTTPS image host, in slide order. An optional, unverified Cloudflare R2 uploader is included; see MEDIA_HOSTING.md. It may require account billing setup and has not been tested live. Verify permission to expose each slide publicly and keep URLs immutable. Create a JSON mapping with a dedicated Buffer test channel ID:

```
{"channel_id":"test-channel-id","image_urls":["https://cdn.example.com/slide-01.png","https://cdn.example.com/slide-02.png"]}
```

## Preview (read-only GETs of public media)

```
python3 reviewed_publish.py preview --carousel /path/to/approved/carousel \
  --input /path/to/mapping.json --allow-host cdn.example.com --ack-public-media
```

The preview prints the caption, destination, URL order, verified image hashes and Buffer manifest digest. It does not publish or schedule. Review all of that, plus source facts, rights and the visible images. The image hosts see your network request. The preview itself is not approval.

## Explicit send after review

Provide the BUFFER_API_KEY securely through environment/secret storage, not chat or command arguments. Then use the digest displayed after preview:

```
python3 reviewed_publish.py send --carousel /path/to/approved/carousel \
  --input /path/to/mapping.json --allow-host cdn.example.com --ack-public-media \
  --approved-digest DIGEST --db /private/persistent-ledger.sqlite3 --send
```

The same checks are rerun before Buffer receives one request. `send` may schedule a post and will act on the destination if it succeeds. It must be used only with the user's authorization and an approved test account. The persistent ledger must be shared across invocations; never remove or silently reset it to retry. On error, timeout, `unknown`, or `pending`, check the Buffer queue before taking further action. See PUBLISHING.md for endpoint assumptions, idempotency and ledger limits.

## Tests

```
PYTHONPATH=. python3 -m unittest discover -s tests -p 'test_review_bridge.py' -v
PYTHONPATH=. python3 -m unittest discover -s tests -p 'test_reviewed_publish.py' -v
```

These use synthetic files, fake fetchers and mocked transport; they do not prove HTTPS provider interoperability, official API compatibility or successful Instagram publication. Production release requires a separately authorized end-to-end test with an actual account and durable asset hosting.
