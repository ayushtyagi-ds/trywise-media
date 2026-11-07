# Trywise research queue prototype

Python 3.10+; standard library only. Collects candidate headlines from configured RSS feeds into SQLite. No AI, fact checking, graphic rendering, scheduling, account access or publishing is implemented. A URL in the queue is a lead, not evidence for a claim. Verify feeds, content and terms for your own use before publishing.

From this directory:

```
python3 -m unittest discover -s tests -v
python3 trywise.py --db /tmp/trywise-demo.sqlite3 import-feed tests/sample.xml --source https://example.com/rss
python3 trywise.py --db /tmp/trywise-demo.sqlite3 list
python3 trywise.py collect --config feeds.json
python3 trywise.py list --status new
python3 trywise.py mark FULL_ID review --note 'Check original announcement'
```

Collection needs internet access. One feed failure doesn't discard other feeds, but the command exits 1 if any failed, so a scheduler can alert rather than silently proceed. Duplicate canonical links are ignored. Live collection defaults to the last 14 days and skips undated entries; use `--days N` to adjust the window. Review statuses are manual and never trigger posting. `published_at` may be null when a feed omits its date; reject stale or unknown dates manually. The default SQLite database lives in the current working directory; keep it private and back it up. Official feed addresses are starter configuration, not guaranteed availability. Check publisher terms, robots policies, and whether content may be reused. Scheduled collection, authentication, live integrations, cost caps, actual analysis and end-to-end publishing are not yet implemented or validated.
