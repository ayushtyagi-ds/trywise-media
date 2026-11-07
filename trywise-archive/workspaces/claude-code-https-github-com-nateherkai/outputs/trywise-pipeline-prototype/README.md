# Trywise AI — review-first pipeline prototype

Status: local prototype, not a deployed or fully automated service. Collects recent stories, captures a source, creates a structured draft, renders carousel images and previews a Buffer request. Publication, scheduling, continuous operation, and authenticated integration are not implemented. No content is automatically posted. Use fictional or permitted material only; review original sources and rights before publishing.

## Setup
Python 3.10+. Create an isolated environment with `python3 -m venv .venv`, then `.venv/bin/pip install -r requirements.txt`. Run commands from this folder. On Linux install or configure suitable fonts as described in RENDERING.md. Do not commit API keys, SQLite queues, source extracts or generated drafts. No paid account is required to run offline tests.

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
