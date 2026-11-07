# Trywise draft generation

`draftgen.py` creates a source-grounded structured carousel draft. It does not approve, publish or post. It makes no network call unless `--live` is explicitly selected. Examples are fictional and must not be published as news.

Offline proof from this directory:

```
python3 draftgen.py --source tests/source.json --fixture-response tests/draft-response.json --out /tmp/trywise-fixture-draft.json
python3 -m unittest discover -s tests -v
```

Input is a JSON object containing nonempty `title`, public HTTPS `url`, `published_at`, and `body`. The body should be an excerpt that you have permission to process and is the only source evidence submitted to the model. No article content is fetched by this component. When using `source_capture.py` JSON as input, supply its verified article title and publication date explicitly:

```
python3 draftgen.py --source captured.json --title 'Verified article title' --published-at 2026-10-30 --fixture-response tests/draft-response.json --out draft.json
```

The sample fixture evidence matches `tests/source.json` only and normally will fail with a different captured article. For an actual API request, after checking account quotas, billing, data terms and availability, set `GEMINI_API_KEY` using a secure environment mechanism (never commit it or paste it in a chat). Select a model you have verified is available and within your budget. Then run:

```
python3 draftgen.py --source captured.json --title 'Verified article title' --published-at 2026-10-30 --out draft.json --live --model MODEL_NAME --ack-data
```

**One live request may incur provider charges.** `--ack-data` confirms source text is transmitted to Google; free and paid tier data terms differ. See https://ai.google.dev/gemini-api/docs/pricing and https://ai.google.dev/api/generate-content . A Gemini app subscription does not automatically fund Gemini API usage. The live API integration and the exact model-specific structured-output configuration remain untested against real credentials; offline tests validate only parsing and guards.

The program rejects malformed drafts, unsupported slide counts, and claims whose quoted evidence is not an exact substring of the captured source; it unconditionally assigns `needs_review` and does not overwrite existing output. Exact quotations do not prove the claim is supported, current, complete, or legal to reuse. The model can omit claims, ignore instructions or include unsupported statements in slides or captions. Human review of all text and original sources is required before publication, including release dates, availability, permissions, and copyright. Do not put private, financial or sensitive material into source files without considering the model provider's data terms. Captured source may contain navigation or truncated text and needs verification against the original page.
