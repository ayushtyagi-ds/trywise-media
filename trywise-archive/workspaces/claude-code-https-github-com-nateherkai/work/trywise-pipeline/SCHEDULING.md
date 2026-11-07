# Research collection scheduler

`scheduler.py` can run the research collection periodically, but does not create drafts or publish anything. No scheduler is enabled or installed automatically. It needs the computer and process to remain running and the network to be available. One process only: concurrent loops are unsupported. Store queue and state in a private, backed-up directory outside the source tree. The state file contains recent collector output/errors. Failed runs are recorded and wait until the next interval; check them rather than assuming success. Internet access and provider feed terms apply.

From the project directory, create a private data directory and run (paths can be changed):

```
mkdir -p ./local-data
python3 scheduler.py --db ./local-data/queue.sqlite3 --state ./local-data/schedule.json --config feeds.json --interval-hours 24 --loop
```

Stop with Ctrl-C. `--loop` omitted performs one due check. Sleeping or rebooting stops the process; a real always-on deployment needs a managed host, persistent storage, monitoring, and startup configuration. A local scheduler is not a fully automated content system. This has not been deployed; automated timing is tested only with mock subprocesses, not over a real 24-hour run.
