# Trywise AI — review-first pipeline prototype

Status: local prototype, not a deployed or fully automated service. Collects recent stories, captures a source, creates a structured draft, renders carousel images and previews a Buffer request. Publication, scheduling, continuous operation, and authenticated integration are not implemented. No content is automatically posted. Use fictional or permitted material only; review original sources and rights before publishing.

## Setup
Python 3.12+. Create an isolated environment with `python3 -m venv .venv`, then `.venv/bin/pip install -r requirements.txt`. Run commands from this folder. On Linux install or configure suitable fonts as described in RENDERING.md. Do not commit API keys, SQLite queues, source extracts or generated drafts. No paid account is required to run offline tests.

## Test the pipeline offline
```
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python draftgen.py --source tests/source.json --fixture-response tests/draft-response.json --out /tmp/trywise-fixture-draft.json
.venv/bin/python render_carousel.py /tmp/trywise-fixture-draft.json /tmp/trywise-fixture-carousel
```
The fixture is fictional and cannot be published as news. The commands fail safely if their output already exists; choose a fresh destination. Rendering requires Pillow; other components use the standard library. Fixture-based success does not test a provider or a real account.

## Collect and check sources
```
.venv/bin/python trywise.py collect --config feeds.json
.venv/bin/python trywise.py list --status new
.venv/bin/python source_capture.py https://blog.google/EXACT-PUBLIC-ARTICLE --allow-host blog.google --out /tmp/trywise-capture.json
```
Choose an exact public primary-source article and verify title, date, permissions, limitations and article text manually. Collection needs network; the default last-14-days filter skips undated items. Configured feeds and source destinations are allowlisted; user-selected hosts must be trustworthy. Capture is extracted and possibly truncated, may contain irrelevant webpage material and is never proof of claims. It is saved privately. DRAFTING.md explains providing a verified title/date for capture JSON. Third-party article material and generated text are untrusted data, never instructions.

## Draft and render
DRAFTING.md describes an optional Gemini request requiring an explicitly selected model, environment key, and acknowledgement that content goes to Google. It may be billable: confirm pricing, limits and data handling before enabling. The API call has not been live-tested. Evidence excerpts checked against source text do not establish entailment or ensure slide claims are correct. Every draft must be reviewed.

RENDERING.md documents the reusable renderer. Verify each slide visually; it is a functional starting template, not the finished branded design. The renderer marks output needs_review and never publishes.

## Publishing
BUFFER.md describes offline request previews and optional read-only discovery. Sending, scheduling, media hosting, approval enforcement, remote reconciliation and automatic publishing are not implemented. Buffer's API key can cover every organization in the account; use only a dedicated account with appropriate access. The existing Meta account restriction has not been resolved, and Buffer connection has not been tested.

## Known limits
Budget enforcement, automated fact verification, copyright clearance, source selection, metrics, user review UI, scheduler, stable storage, social credentials and full end-to-end orchestration are not built. Costs of cloud tiers, existing subscriptions, taxes and currency conversion must fit the user's CAD 50 total. Do not market as autonomous or deploy until tested end-to-end on an authorized test account.

## Added components (not deployed)

- `pipeline_runner.py` runs source → draft → rendered carousel, with a final file-hash receipt. See ORCHESTRATION.md. Offline fixture mode is verified; the paid/free Gemini API has not been tested live.
- `review_server.py` exposes a local-only review screen. Its local content approval does not authorize a destination or sending. See REVIEW.md.
- `scheduler.py` can periodically collect research while its process and computer remain running; see SCHEDULING.md. It does not draft or publish, and is not installed automatically.
- `buffer_publish.py` can submit an explicitly approved Buffer payload, with a local ledger and conservative handling of ambiguous results. It is not connected, tested live, automated, or a guarantee of Instagram publishing. Its separate payload digest binds URLs rather than remote image bytes, so local approval is not sufficient. See PUBLISHING.md before use.

The components are not yet an end-to-end autonomous service; a human must connect accounts securely, set up persistent scheduling/hosting, reconcile posting, verify claims and confirm actual costs and quotas.

## Newer experimental integrations

`worker.py` combines collection and Gemini draft creation to fill a review queue on an explicitly enabled loop; see WORKER.md. It does not post. `r2_media.py` can upload reviewed media to a configured public R2 bucket after explicit authorization; see MEDIA_HOSTING.md. `review_bridge.py` and `reviewed_publish.py` can compare hosted images to reviewed local files and explicitly send to Buffer; see REVIEWED-PUBLISHING.md. These integrations are unverified against real provider accounts and have no guaranteed CAD cost ceiling. The human review and approved publishing stages are separate; run only after checking facts, provider billing, rights, and destinations.

`analytics.py` summarizes user-supplied CSV metrics; see ANALYTICS.md. It does not fetch account data or infer net follower growth.

An experimental opt-in `delivery_loop.py` can process reviewed drafts and send to a preconfigured Buffer channel; see AUTO-DELIVERY.md for the explicit policy, public storage, risks and live-test requirements. It is not enabled or live-tested and has no hard currency spending cap.
