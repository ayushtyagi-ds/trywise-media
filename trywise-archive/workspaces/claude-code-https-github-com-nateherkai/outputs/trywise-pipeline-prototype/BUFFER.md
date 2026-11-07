# Buffer integration: read-only discovery and offline payload preview

Status: research prototype. No publishing, scheduling, creation, uploading, approving, or remote mutations are implemented. A successful preview is NOT evidence that Buffer, Instagram, media hosting, credentials, permissions, or social account restrictions will permit publishing. Do not paste API keys in chat or commit them to source control.

## Rationale

Buffer documents its GraphQL API at https://api.buffer.com with account-level bearer API keys. Keys can access all organizations and channels in the Buffer account: https://developers.buffer.com/guides/authentication.html . Buffer says Instagram professional accounts can connect directly using Instagram login; your Facebook security situation still needs independent attention and this connection has not been tested: https://support.buffer.com/en-us/articles/connecting-your-instagram-account-to-buffer-n9Ad6veXsu

Buffer expects ordered, publicly reachable, stable direct media URLs; the API doesn't upload files: https://developers.buffer.com/guides/hosting-media . Such URLs expose media to anyone who has the URL, so host only images you intend to publish; confirm each image's public reachability and permitted use. This preview doesn't contact asset URLs, and rejects URLs containing query strings to reduce accidental exposure of signed URLs or secrets.

## Offline preview

Create JSON with fields:

```json
{"channel_id":"test-channel-id","caption":"Sample for review","image_urls":["https://example.com/slide-1.png","https://example.com/slide-2.png"]}
```

Run `python3 buffer_adapter.py preview path/to/manifest.json`. It prints a deterministic content digest and a possible GraphQL request, but **does not send it**, approve it, validate it against Buffer or post. A digest isn't proof that a human approved anything. Keep preview files private as they may contain unpublished caption and image URLs. The request shape follows https://developers.buffer.com/examples/create-image-post.html ; automatic Instagram carousel behavior remains untested.

## Read-only account inspection, optional

Once the user has securely connected their own account and intentionally supplied a Buffer API key as an environment variable in their own shell, `python3 buffer_adapter.py organizations` fetches account organizations; `python3 buffer_adapter.py channels ORGANIZATION_ID` lists channels. No key or authorization header is printed. Both make one read-only request to the official Buffer endpoint. Do not put keys in shell history; use a secure secret mechanism. API key access is not limited to one channel, so use a dedicated test account.

## Work needed for safe write integration

An actual sender should accept a specific approved content digest and destination channel, verify the approved artifact has not changed, revalidate URL reachability and publishing rights, and record a durable local write-ahead state before sending. Buffer warns its create-post writes lack idempotency keys; a timeout can mean a post succeeded even if the response was lost. Never automatically retry an ambiguous write. Halt in `unknown` state and reconcile against the user's Buffer queue before any retry: https://developers.buffer.com/guides/efficient-api-usage.html . Persist returned Buffer post ID and check its status separately. Prevent concurrent duplicate submissions with transactional locking. Prove carousel scheduling, image reachability until publication, quota use and failure handling on a connected test account before considering unattended operation.
