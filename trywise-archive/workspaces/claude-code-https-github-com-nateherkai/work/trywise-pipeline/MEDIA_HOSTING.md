# Reviewed carousel media hosting (R2 prototype)

Buffer requires each image at a stable, public, direct HTTPS URL for its API and says it may fetch that URL at publication time; it does not upload image files. Public exposure happens as soon as an object is accessible: use only slides you have reviewed and intend to make public. https://developers.buffer.com/guides/hosting-media

This **unverified, optional prototype** previews and uploads already-reviewed PNG slides to a user-controlled Cloudflare R2 bucket. Nothing is published to social media. An R2 account, bucket, credentials, and a separately configured public domain pointing to that bucket are prerequisites; none are created here. Do not connect this to personal accounts during the suspected-compromise investigation. Cloudflare says an R2 subscription is required to create an API token; setup may require a payment method even when usage stays within free allowances. https://developers.cloudflare.com/r2/api/tokens/ Confirm the provider's current region availability, pricing, free-tier and cost controls before enabling. Cloudflare describes Standard R2 free tier as 10 GB-month storage, 1 million Class A operations and 10 million Class B operations each month; exceeding quotas incurs fees. These are separate from your existing Gemini subscription, taxes and FX. https://developers.cloudflare.com/r2/pricing/

This prototype supports only the default global R2 endpoint, not jurisdiction-specific buckets. Cloudflare documents its `r2.dev` public endpoint as for non-production use and rate limited. For sustained publication, configure an appropriate custom domain and confirm its routing, caching, and permission settings. There is no guarantee a public file is immutable or that Buffer can reach it. https://developers.cloudflare.com/r2/buckets/public-buckets/ ; https://developers.cloudflare.com/r2/platform/limits/

## Setup

Install the optional SDK separately in a dedicated Python environment: `pip install 'boto3>=1.35,<2'`. We do not bundle it or install it automatically. Create a bucket-specific, least-privilege credential, store it securely in your runtime's secret mechanism, and configure `R2_ACCESS_KEY_ID` and `R2_SECRET_ACCESS_KEY` there. Do not send credentials through chat, logs, screenshots, command arguments or version control. Restrict credentials and revoke/rotate them if exposed.

## Preview and upload

Review the carousel through `review_server.py` first, producing `approval.json` bound to exact local bytes. Preview requires **no credentials or network**:

```
python3 r2_media.py /path/to/carousel --account-id YOUR_32_CHARACTER_ACCOUNT_ID --bucket YOUR_BUCKET --public-base https://assets.example.com
```

Preview prints the bucket, intended public URLs, content hashes and a plan digest. Confirm the exact account, bucket, domain and images. If you deliberately choose to make these images public, call the same command with `--upload --ack-public --approved-plan EXACT_PLAN_DIGEST`. The confirmation is for *public hosting*, not permission to submit a Buffer post. The upload requires API environment credentials. No network operation is performed by default.

Files are named by their SHA-256 content digest. R2's `If-None-Match: *` conditional create prevents this client from overwriting an existing object. Cloudflare documents conditional puts as atomic: https://developers.cloudflare.com/r2/api/s3/api/. If any call fails (including an existing object or timeout), the program stops without retrying; one or more images may already be public. Inspect the bucket and public URLs and verify byte hashes before deciding what to do. Delete only when safe and permitted. There is no automatic rollback or cross-run ledger. Another credential or actor can still overwrite/delete the same object, so restrict write access, keep objects stable and monitor until Buffer publishes; conditional creates are not global immutability.

The reported status is **uploaded_not_verified**. The local file checksum and host URL do not prove that the URL maps to this bucket, is public, serves the expected bytes, remains available, or is reachable by Buffer. Independently GET each URL without authentication, compare the retrieved bytes to the reviewed slides, and bind the verified ordered URLs and destination channel to a separate explicit publishing review. Even successful verification is point-in-time and not a guarantee against later mutation. The separate Buffer component and review bridge must be validated before enabling a send. This upload module has only mock tests; no real upload or publication has been performed.
