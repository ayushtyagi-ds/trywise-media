# Local review interface

`review_server.py` offers a localhost-only page for reviewing a carousel directory produced by `render_carousel.py`. It does not itself send data to a service, upload, schedule, or publish. If a separate automatic delivery worker is enabled, a recorded review can trigger a post to its configured channel. Start it from the pipeline directory:

```
python3 review_server.py /path/to/rendered-carousel --port 8765
```

Open `http://127.0.0.1:8765/` on the same computer. Review every slide, the caption and the source, then confirm the checkbox and record review. Press Ctrl+C to stop. You need permission to bind a local TCP port; some sandboxes disallow local server sockets. No extra packages are required for the reviewer.

Approval is saved once as `approval.json` in the rendered directory, and binds the exact manifest, caption, and ordered image bytes. A changed file invalidates the displayed approval digest; image requests are digest-bound. The record covers local content only—it is **not** approval for a destination, media URL, account, time, or act of publication. It does not verify copyright, source accuracy, semantic truth, or the identity of the human pressing the button. A separate publishing system must validate that reviewed content matches hosted media and bind any publication approval to its destination and timing. The current Buffer preview does not use or enforce this file.

An approval record is created once and never overwritten. If a file changes, create a fresh render directory and review the new files. Keep this directory private. The server binds to IPv4 loopback only, requires same-origin POST plus an unpredictable per-run CSRF token, checks host headers and rejects symbolic-link input files; it is not designed as a public-facing service. Don't use it on a shared untrusted machine or expose it using port-forwarding or a reverse proxy.

## Finding drafts produced by the worker

`python3 inbox.py --db /private/queue.sqlite3 --root /private/drafts` lists completed review folders and their IDs. `python3 inbox.py --db /private/queue.sqlite3 --root /private/drafts --open FULL_STORY_ID` opens the local reviewer for a listed draft at 127.0.0.1:8765. This is a command-line inbox, not a remotely accessible dashboard; it does not publish. It skips missing and unsafe folders and marks modified approvals `changed_since_review`. The queue DB and draft root must be the same persistent locations used by the worker. The user must provide a full story ID, review the source and media, and record approval on the local page.

## Local browser inbox

To browse all finished drafts in one place, run `python3 inbox_server.py --db /private/queue.sqlite3 --root /private/drafts` and open `http://127.0.0.1:8765/`. This server is local-only. It lists completed worker drafts, shows each source and carousel, and records local review; it does not itself upload or post. If the separate automatic delivery worker has been explicitly enabled, recording a review can cause a later public post to the channel in its policy. No service is enabled by default. Do not expose this server publicly or use it on an untrusted shared machine.

Drafts generated with evidence include the model's listed claims, supporting source excerpts and uncertainty notes in the review screen. These are recorded in the reviewed manifest, so changing them invalidates the local approval digest. Evidence extraction can omit claims, take text out of context, or misinterpret it; reviewers must still check the entire original source and every slide and caption. Older or manually written drafts may have no evidence.
