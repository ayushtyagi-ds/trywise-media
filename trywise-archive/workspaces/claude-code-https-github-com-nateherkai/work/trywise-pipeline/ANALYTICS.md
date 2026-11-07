# Metrics overview

`analytics.py` summarizes a user-provided CSV export. It doesn't connect to Instagram or fetch data. Required columns: `format,reach,saves,shares,profile_visits,post_follows` with nonnegative whole numbers. Only compare metrics measured over the same time window. Missing data must not be silently entered as zero. Summed per-post reach counts repeat viewers and does not establish unique account reach. Post-attributed follows are not net followers, and correlation is not causation. Account-level net follows should be tracked separately.

Example: `python3 analytics.py /path/to/metrics.csv`. API metrics retrieval and scheduled reporting remain unimplemented.

## Buffer metrics prototype

`buffer_metrics.py --post-id BUFFER_POST_ID --db /private/metrics.sqlite3 --fetch` makes one read-only request using `BUFFER_API_KEY` from the environment and records the exact metric names, units and values returned. It requires a personal Buffer API key and should be used only with the account owner's authorization. Do not share keys in chat or commit them. Buffer says this endpoint is available for personal workflows and automations: https://developers.buffer.com/examples/get-post-metrics.html. A missing metric is not zero; account-level net followers are not equivalent to follows attributed to a post. Existing snapshots may contain non-public business data; store the SQLite database privately.

The integration is not live-tested; exact availability and metrics depend on the connected channel and Buffer account. No automated poll schedule, trend analysis, notification, Instagram-post verification, or account-wide follower tracking is implemented. Unit tests use a fabricated API response and do not establish provider compatibility.
