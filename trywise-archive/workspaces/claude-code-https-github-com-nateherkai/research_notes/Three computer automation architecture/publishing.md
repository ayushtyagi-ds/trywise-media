# Publishing and hosted media

## Can the new server post to two Instagram accounts without another Meta app?

### Takeaway
Buffer's free tier currently supports three social channels and its API can publish Instagram posts and reels; adding the second account and provisioning separate server authentication still require verification.

### Cited Findings
- Buffer's pricing page lists three channels, 10 queued posts per channel, and API access with one API key for the free plan; 1,000 requests per channel/month up to 3,000 are listed. [Buffer pricing](https://buffer.com/pricing)
- Buffer's official n8n instructions require a Buffer API key in an n8n MCP Client node using the Buffer MCP endpoint. Existing authorization in another application does not in itself document that an API key was provisioned on a different machine. [Buffer n8n integration](https://developers.buffer.com/guides/integrations/n8n.html)
- Buffer says Professional Instagram accounts can connect using Instagram login for auto-publishing and that a linked Facebook Page is optional for this route, although some features require a Page. Personal accounts cannot automatically publish via Buffer. [Connecting Instagram to Buffer](https://support.buffer.com/en-us/articles/connecting-your-instagram-account-to-buffer-n9Ad6veXsu)
- Buffer says the API supports Instagram post, story, and reel types, but not reading/replying to comments; complete analytics are not generally available and its experimental per-post metrics should not be relied on for full reporting. [Buffer API support](https://support.buffer.com/en-us/articles/what-is-buffers-api-GtIYIQilz5)

### Inferences
- Two Instagram profiles and a YouTube channel could fit the three-channel free cap, if all are eligible and connected. Daily posting can fit ten pending posts per channel by continually refilling rather than scheduling a month ahead; access and free-tier behavior still need to be tested on the user's account.
- The existing Codex Buffer MCP OAuth session and successfully created draft don't prove the n8n server has its own working authentication. Credentials should be entered into the server's credential store rather than shared in chat or committed to GitHub.

### Gaps
- The Cozy Two account's professional status, ownership, connection, and auto-publishing capability have not been checked. Buffer free limit information for 30-day API requests is worded differently in pricing versus support; verify live account limits and rate windows rather than assume a simple aggregate.

## What media hosting does unattended publication need?

### Takeaway
The direct media URL must remain usable publicly throughout the queue period; creating a Buffer draft is insufficient proof of actual downstream delivery.

### Cited Findings
- Buffer's API does not accept a native file upload: assets need publicly accessible direct URLs that stay reachable until publication. For video API posts, Buffer says the media is not re-hosted. [Buffer hosting guide](https://developers.buffer.com/guides/hosting-media); [Buffer video troubleshooting](https://support.buffer.com/en-us/articles/troubleshooting-video-uploads-in-buffer-LK0CldlFNB)
- GitHub warns for files over 50 MiB and blocks ordinary Git files larger than 100 MiB. [GitHub file limits](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github)
- Cloudflare states that public R2 `r2.dev` bucket access is rate-limited and designed for non-production; it recommends a custom domain for production. [Cloudflare public buckets](https://developers.cloudflare.com/r2/buckets/public-buckets/)

### Inferences
- The user's `trywise-media` GitHub repo works for the existing small still images based on the in-session test, but should not be assumed to be a durable or scalable video distribution service. Evaluate format, file sizes, public hosting terms, and CDN behavior before committing to video hosting; don't expose private files.
- Track content hash, destination, schedule and returned post ID; verify final provider state after delivery. On an ambiguous result, reconcile against existing posts before retries to avoid duplicate posts.

### Gaps
- The stable production-grade hosting service, delivered video size, first publication outcome, and whether account resources are accessible from n8n are not yet verified.

## What about YouTube uploads?

### Takeaway
YouTube can be a later channel through Buffer or a separately authorized Data API uploader, but account authorization, actual project quota and upload behavior must be tested.

### Cited Findings
- Current YouTube `videos.insert` documentation lists 100 calls per day in a separate upload quota bucket and says videos uploaded from unverified API projects are not restricted to private viewing mode. Its `privacyStatus` default is public if not supplied, subject to account settings. [YouTube videos.insert](https://developers.google.com/youtube/data/reference/rest/v3/videos/insert)
- The historical July 2020 revision says videos uploaded by unverified API projects were restricted to private. This conflicts with current endpoint documentation, so the old statement should not be presented as current policy without a successful test or clarification. [YouTube revision history](https://developers.google.com/youtube/data/revision_history)
- YouTube's API quota page describes separate daily default buckets of 100 upload calls, 100 search calls, and 10,000 units for other methods; extra quota requires audit. [YouTube audit and quota](https://developers.google.com/youtube/data/guides/quota_and_compliance_audits)
- YouTube evaluates whether channel content is original and authentic; repetitive mass-produced videos with little value and reused material without substantial original contribution may be ineligible for monetization. [YouTube monetization policies](https://support.google.com/youtube/answer/1311392?hl=en)

### Inferences
- A 3D-style couple needs genuinely distinct stories and consistent quality; using AI tools does not establish monetization eligibility. Tests should explicitly set video privacy and confirm actual result before any public schedule is relied upon.

### Gaps
- Actual eligibility, OAuth status, quotas and video features for the owner's YouTube channel are unknown, and YouTube is not required for the initial Instagram-only launch.
