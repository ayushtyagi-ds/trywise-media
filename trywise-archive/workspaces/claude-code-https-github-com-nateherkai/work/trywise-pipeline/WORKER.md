# Scheduled news-to-review worker (prototype)

`worker.py` can collect recent RSS items, atomically reserve one eligible story in the shared SQLite database, call the existing source → Gemini draft → carousel runner, and put the output in a local folder for review. It never approves, schedules, uploads, or publishes a social post. No process is installed or started automatically. The research title/date are feed metadata, not independently verified facts. The output is always a draft. A trusted human must review every factual claim, date, source, copyright, caption and slide before use.

**Not live-tested:** no Gemini credentials, Buffer credentials, or real social publishing have been used. An unattended run transmits source text to Google and can incur API charges. Google Gemini app Pro and API are separate products. Check current quotas, model availability, rate limits and data terms. This worker's daily attempt limit is a count, not a spending cap; tax, fees, other API use, and provider charges can still exceed the user's CAD 50 ceiling. Disable paid billing or configure actual provider spending controls if a hard ceiling is needed. This prototype does not calculate model cost.

## Explicit opt-in

Install the dependencies described in README, use dedicated test accounts and a private persistent data directory, and configure `GEMINI_API_KEY` in the process environment using your own secure method (never paste it in chat or commit it). Example, with an intentionally invalid model placeholder to replace only after checking your exact access:

```
python3 worker.py --db ./local-data/queue.sqlite3 --outdir ./local-data/drafts \
  --config feeds.json --allow-host blog.google --allow-host openai.com --allow-host huggingface.co --allow-host github.blog \
  --model YOUR_VERIFIED_MODEL --max-attempts-per-day 1 --days 7 \
  --run-live --ack-data-and-cost
```

That runs once, fetches feeds and may make **one live billable model request**. Add `--loop --interval-minutes 60` to poll while the machine remains awake and the process is running; it stops on reboot. One story is selected per loop using the title-based relevance heuristic among up to 1,000 recent candidates. It must have an allowlisted HTTPS host and a plausible date within the lookback. Redirects are also host-restricted. It can select irrelevant content and extract incomplete text. No advance semantic ranking, topic diversity, source licensing, full editorial fact check or quality guarantee is implemented.

Before fetching or model invocation, the worker commits a `pending` reservation for each story ID and counts it against the daily attempt limit. It never automatically retries that story, including after timeouts, partial outputs, a process crash, or definite failure. A result becomes `review` only if a receipt exists; failed attempts become `failed`, with only an error class saved. Inspect the SQLite `draft_jobs` table and output folders to investigate failures. There is intentionally no automatic unlock/reset, so a human must investigate before deliberately adjusting records. Never copy or delete a queue DB while workers are running: all workers must share the same durable SQLite database for deduplication, and backups/restores or changing a URL can still result in duplicates. Feed fetch failure is reported without abandoning successful feeds; the once-mode exits nonzero if any feed failed or the draft failed. Loop mode reports errors but no alerting system is configured.

Local unit tests simulate model and capture work, using no credentials or network. They verify concurrency reservations, basic allowlisting and freshness, daily attempt limits, failed jobs, and no retry. They do not validate the external provider, monetary cost, facts, image quality, uptime, alerting, or end-to-end publication. Before deploying, add monitoring, secure secret management, stable hosting and durable state backups; test on a test account and review provider permissions. Real Buffer delivery requires a separate approved payload and actual hosted media. An approved local review does not automatically authorize sending.

Candidate selection uses the simple, inspectable word weights in `editorial_rank.py`, favoring developer and workflow topics within the recent candidate window. It is a heuristic: it can miss relevant stories, select irrelevant stories, and does not verify truth, availability, rights, or editorial value. Ties retain the feed-date ordering. Review and adjust the rules based on observed output rather than assuming the score predicts growth.

The default feed list also includes the Hugging Face blog and GitHub AI & ML blog. Both live feeds parsed and one article from each was extracted, but the full drafting and review workflow has not been tested with these sources. Articles from these vendor blogs are primary sources for their own announcements, not independent confirmation; verify claims and avoid treating promotional material as independent testing.
