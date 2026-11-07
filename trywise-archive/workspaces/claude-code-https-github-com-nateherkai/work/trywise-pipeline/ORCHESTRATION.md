# Unified review-only runner

`pipeline_runner.py` combines source capture, draft generation and carousel rendering into one operation. It **never schedules, approves or publishes**. Its output is a folder containing the draft, carousel, and a receipt with SHA-256 file hashes. The receipt is written last; a folder without `receipt.json` is incomplete and must not be treated as an output. Hashes record bytes at generation time, not editorial approval, verification, tamper protection, publishing rights, or proof of authorship.

## Offline fixture — no API, no network, no charges

From this directory, after installing Pillow:

```
python3 pipeline_runner.py --source tests/source.json --fixture-response tests/draft-response.json --out /tmp/trywise-offline-example
```

The fixture contains fictional information; do not publish it. The destination must not exist. On normal failure the script removes staging files and leaves no output. A process or machine crash can leave a partial directory; its missing receipt indicates it is incomplete. Do not interpret receipt presence as approval.

## Real source and Gemini (not yet live tested)

After verifying your API provider's billing/free tier, model availability, usage limits, and handling of the source, supply a key via a secret store or environment variable. Never put a key in a command, source file, chat or image. Pick an exact public primary-source page and inspect its publication date and title. Avoid restricted material. Do not send sensitive data. One request may incur charges and `--ack-data` explicitly signals that the source will be transmitted to Google:

```
python3 pipeline_runner.py --url 'https://blog.google/EXACT-ARTICLE' --allow-host blog.google --title 'Verified title' --published-at YYYY-MM-DD --live --model YOUR_MODEL --ack-data --out /tmp/trywise-draft-001
```

A local captured source or prepared evidence JSON can instead be provided with `--source`; capture JSON additionally needs `--title` and `--published-at`. For URLs, only explicitly allowed HTTPS hosts and redirects are permitted. A fixture run refuses URL inputs to ensure it remains offline. No real provider calls have been tested. Validate source extraction and quotations against the original page. Evidence quotation matching checks neither all claims nor entailment. Verify every claim, currency, eligibility, date, visual and content right before using the output. Publicly display original source as appropriate.

## Gaps

No persistent scheduling, deduplication across runs beyond the separate research queue, reviewer UI/approval enforcement, analytics, content safety/fact-check automation, cost controls, durable remote asset hosting, authenticated integrations, or posting exists. Verify the test account and Meta restriction before connecting a scheduler. This component is not a production system.
