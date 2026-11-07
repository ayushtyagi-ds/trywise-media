# Trywise AI setup checkpoint

Verified October 31, 2026 using live Buffer MCP tools.

- Buffer OAuth connection works in this Codex chat.
- Workspace: My organization (`6ae63280b965243d95d39b38`).
- Instagram: @trywiseai (`6ae636052f1f5ed648353cf5`), connected and unlocked.
- First carousel: Buffer post `6ae637489aa2e4d9f47f1790`, status `sent`, no error, five 1080×1350 images, automatic publishing. Sent October 31 at 1:00:54 PM America/Edmonton.
- Instagram link returned by Buffer: https://www.instagram.com/p/DfK2-REGxDZ/
- This confirms Buffer's reported delivery; Instagram appearance has not been independently inspected in this chat.
- Buffer currently has two unscheduled drafts: a clearly labelled automation test (do not publish), and a four-slide Gemini file-editing announcement draft (`6ae67f3d5c164391063bfb95`). Before reusing the Gemini story, inspect the existing draft and avoid creating duplicates. Recheck source and account availability before publication.
- Existing queue slots: Tuesday 7:25 PM, Wednesday 6:44 PM, Thursday 10:30 AM, America/Edmonton. Queue is unpaused.

## Two distinct execution paths

Codex can use the connected Buffer tools to inspect posts and prepare drafts. This OAuth connection does not supply a `BUFFER_API_KEY` to the separate Python worker. Future runs require their own available tool connection. The recurring Codex task described below was configured in a different chat.

The existing Python prototype remains at `/Users/phoenix/Documents/Codex/2026-10-31/claude-code-https-github-com-nateherkai/work/trywise-pipeline`. Current default-shell preflight found Python 3.12+, but no Pillow, boto3, Gemini key, Buffer key, R2 keys or configured delivery policy. This only checks the current process environment, not other environments or secret stores. No always-on worker has been verified.

## Operating choice

The owner selected recurring Codex publication as described below. The separate Gemini worker remains unconfigured and requires its own credentials and persistent runtime. Preserve factual and visual checks and the CAD $50 monthly ceiling. Do not purchase subscriptions, activate paid API billing or republish the successful test carousel.

## Connected Buffer workflow

1. Reuse the exact workspace and channel IDs above; verify channel connection when needed.
2. Read the existing queue before creating a post to avoid duplicates.
3. Prepare and review factual claims, caption and ordered carousel images.
4. For new media, provide stable publicly downloadable image URLs; the connected create-post tool does not upload local files.
5. The owner explicitly confirmed automatic public media upload and publishing to @trywiseai without per-post approval. Perform factual and visual quality checks before submission.
6. Record the returned Buffer post ID. Reconcile ambiguous submissions before retrying, and check sent/error status after scheduled delivery.

## Recurring Codex drafts enabled

The owner explicitly confirmed automatic publishing in chat. The automation update succeeded: active thread automation `trywise-ai-drafts-for-review`, now named **Trywise AI automatic publishing**, runs Monday, Wednesday and Friday at 9 AM America/Edmonton. It prepares a source-checked five-slide carousel and caption, inspects rendered images, and publishes to @trywiseai through Buffer without per-post approval. Intended public media upload is authorized. Use verified image hosting or the signed-in Buffer composer for local uploads. Record submission IDs, reconcile uncertain outcomes before retrying, and report actionable failures. This replaces the review-only instructions. No new subscriptions or social posts were created by this configuration change. The first scheduled automatic publishing execution has not yet been verified.

## Media upload test, October 31

Buffer composer accepted four local 1080×1350 PNG images and saved them as an unscheduled Gemini draft. The Buffer MCP reported all four assets on that draft after upload. This validates one manual composer upload in this session, but does not prove an unattended scheduled run will have browser access or can repeat the upload. No separate GitHub media repository was needed for this test.

### Direct upload procedure observed

In the signed-in Buffer composer, open a new post for @trywiseai, enter the caption, start the browser file-chooser event before clicking the upload control, select the ordered local PNG files, and wait for all upload indicators to disappear. On October 31, four files appeared at 0% initially and completed on the next status check after the upload call; the composer preview showed 1 of 4. Save Draft, then verify the resulting draft and asset count with the Buffer list_posts tool before deciding any next action. The local file chooser path requires the applicable browser tool and upload documentation, as well as browser availability in the scheduled execution. After Save Draft succeeds, track its Buffer ID; do not create another on an ambiguous response. Follow the automation prompt for publication and verification, and keep test drafts out of the live queue. This tested browser upload still requires end-to-end verification during a scheduled run.

## Gemini draft verification, October 31

The four local slide images were visually inspected and the draft checked against Google’s October 29 announcement at https://blog.google/innovation-and-ai/products/gemini-app/edit-files-directly/. Google states that file creation and editing are available in the Gemini app, PDF preview/editing works on web and mobile, and the other listed formats work on the web. The draft presents a suggestion to try a non-sensitive sample and does not claim a hands-on test. The draft remains unscheduled. Verify claims again at publication time, since availability can change; the draft is four slides and the recurring task requests five. Do not publish the marked automation test draft.

## First post metrics baseline

At about 5:53 PM Edmonton time on October 31, the Buffer get_post response for the first carousel returned `metrics: null`; its `metricsUpdatedAt` was before the 1:00 PM send. Treat performance as unavailable, not zero. Review metrics after provider ingestion; do not infer follows, engagement or reach from missing data.

## Follower baseline availability

Buffer channel details on October 31 did not expose a follower count. Its weekly posting goal showed one sent post and three as the target; this is a posting-frequency metric, not a follower baseline. Obtain a dated follower count from Instagram insights or another authorized source before calculating monthly net growth.

Instagram profile baseline observed directly on October 31, 2026 (late afternoon Edmonton): 0 followers, 1 post, 0 following. The first carousel was visibly present on @trywiseai. This is a point-in-time count, not a measurement of reach or engagement.

## Weekly measurement procedure

On Friday runs, if access is available, record the date and current follower count from the @trywiseai Instagram profile, plus available Buffer post metrics and their refresh timestamps. Compare the follower count with the last dated observation (initial observation: 0 on October 31); distinguish net change over the observed interval from follows attributed to a specific post. Report unavailable metrics as unavailable, never as zero. Record post reach, saves and shares only where the provider actually supplies them. Compare similar posts of similar age and treat early results as tentative. Save the observation privately in the workspace, avoid duplicate records, and use it to form one testable content hypothesis for the next week. Do not send unsolicited DMs or manipulate engagement. If profile access or metrics are unavailable, preserve publishing if its independent checks pass and note the missing measurement.

## Candidate: agent memory explainer

A five-slide candidate was prepared locally from the October 31 GitHub Trending signal and claude-mem repository description; path `/Users/phoenix/Documents/Codex/2026-10-31/claude-code-https-github-com-nateherkai/outputs/agent-memory-draft/corrected`. This is not yet in Buffer or scheduled. The date on the slides is the source-observation date, not the repository creation date. Its example prompt is editorial advice, not a hands-on product demonstration. Verify source, currency, image readability and avoid topic duplicates before use.

## Gemini carousel scheduled

Buffer post `6ae67f3d5c164391063bfb95` is scheduled for `2026-11-04T01:25:00Z` (November 3, 19:25 America/Edmonton) as an automatic Instagram post. All four images verified in the scheduling response. Do not publish or schedule a duplicate; check its current Buffer status and published link after the due time.

## Public media host and agent-memory Buffer draft

The owner created and authorized public GitHub repository `ayushtyagi-ds/trywise-media`. GitHub connector write access verified. Its `main` branch contains five publicly intended agent-memory images at `2026-10-31/agent-memory/` in commit `b883a490950fa264e13911f30736552bd42dd86f`. Buffer accepted all five immutable `raw.githubusercontent.com` URLs as 1080x1350 image assets in unscheduled Instagram draft `6ae697ea1ee172cd6dd31429`; this verifies draft ingestion, not Instagram publication. Avoid creating a duplicate; inspect and reuse this draft where timely and appropriate. For future original public carousel images, upload to this dedicated public repository through the GitHub connector, use commit-pinned raw URLs, verify Buffer assets, and reconcile before publishing. Never upload secrets or private data. GitHub Git Data blob supports base64 binary, tree/commit/ref operations can publish multiple files atomically; preserve existing files with the correct base tree and protect against concurrent ref changes.

## Daily cadence update

November 1 daily run: reused the five-slide agent-memory draft `6ae697ea1ee172cd6dd31429` after source and visual checks. Buffer confirmed `sent` at `2026-11-01T15:49:41.913Z`, no error, public link https://www.instagram.com/p/DfNF41voW_P/ . Do not publish another post on November 1. Ledger: `2026-11-01-publication.json`. Gemini carousel remains scheduled for November 3 evening, not yet due. This verifies the first automatic publication through Buffer; no additional subscription or spend was activated.

On October 31 the owner requested daily posting. The existing automatic publishing heartbeat was updated to run daily at 9 a.m. America/Edmonton, superseding the older Monday/Wednesday/Friday cadence. Aim for one quality-checked post per local calendar day; if a suitable post is already scheduled or sent on that date, do not publish another. The Gemini post remains scheduled for November 3. The first unattended publishing run is not yet verified.


## November 2 publication

Published Handy local-dictation explainer via signed-in Buffer composer in My organization after source and visual checks. Buffer post ID `6ae92c27f66eb6d310d1b28a`; UI confirmed Published November 2 at 6:35 PM America/Edmonton. Public link: https://www.instagram.com/p/DfQm14-EaKb/ . Do not publish another on November 2. Files, caption, source, hypothesis, hashes and ledger in `2026-11-02-handy/`. Cover is original AI-generated illustration, labelled and AI disclosure enabled. No paid API or subscription activated. Gemini remains scheduled for November 3 7:25 PM; not due at this run. Buffer connector unavailable, browser delivery verified. Metrics recorded in `2026-11-02-metrics.json`; provider refresh lags and post ages differ. No causal winner inferred.


## November 3 publication and overlap

User cadence now allows up to three distinct posts daily, with checks at 9 AM, 2 PM and 7 PM; older one-per-day guidance is superseded. Desktop-agent explainer published at 5:12 PM Edmonton: Buffer ID `6aea6a44c98030ac3920c77b`, https://www.instagram.com/p/DfTCLAoDr77/ . After submission, refreshed Buffer revealed a separate Claude API post published at 5:11 PM: https://www.instagram.com/p/DfTCEylEbF5/ . This was not visible in the pre-drafting Sent check. The spacing safeguard failed under concurrent publishing. No additional submission or deletion attempted. Count both plus the pre-existing Gemini post scheduled 7:25 PM as THREE today. Do not publish any more on November 3. Check Gemini status after 2026-11-04T01:25Z.

Before any future publishing run, coordinate through an atomic shared lock directory `outputs/.trywise-publication-lock`, with a run receipt containing start time and topic. If already present, do not publish; reconcile its receipt and current Buffer state. Hold the lock from queue inspection through delivery reconciliation. Refresh Sent and Queue immediately before final Publish, after uploads, to catch concurrent submissions and enforce two-hour spacing. Release a lock owned by the run only after definitive outcome is saved; preserve an ambiguous-submission receipt for reconciliation. This coordination change has not yet been tested across all publishing automations.


Nov 4: Another Trywise news-roundup publication is in progress in this chat. Before posting, check Buffer Sent, Queue, and /Users/phoenix/Documents/Codex/2026-10-31/claude-code-https-github-com-nateherkai/outputs/news-2026-11-04/ledger.json. Avoid a concurrent submission.


## November 4 reconciliation and withheld roundup

Verified Gemini post `6ae67f3d5c164391063bfb95` in Buffer Sent: Nov 3 at 7:25 PM Edmonton, public link https://www.instagram.com/p/DfTRXsODJlf/ . Do not duplicate.

This run researched and rendered a two-story Nov 4 roundup (Guided Learning, Copilot in Air). Shared lock was acquired, but final live check after upload caught another publisher’s overlapping three-story roundup sent Nov 4 at 6:33 PM: https://www.instagram.com/p/DfVwNldFjxs/ . No public submission was made by this run. Preserved as unscheduled draft `6aebcfa1827edfb2d75cafee`, with explicit DO NOT PUBLISH note; do not queue or publish it. Local files and ledger: `2026-11-04-roundup/`. Avoid both stories if covered by the already-published roundup. Do not publish another within two hours of 6:33 PM. The shared lock is not yet observed by all publishers; the fresh check prevented the duplicate. No new spend or subscription.


## November 5 Xcode publication

Published five-slide Copilot-in-Xcode public-preview explainer. Buffer `6aed5b572f69631c7d7ff44b` confirmed sent: https://www.instagram.com/p/DfYx38_lrFh/ . Browser UI Nov 5 10:45 PM; delivery verified after processing. Assets, caption, hashes, source and hypothesis: `2026-11-05-xcode/`. No hands-on test claimed. Original drawn illustration labeled; AI disclosure enabled. Fresh Sent/Queue check showed zero earlier Nov 5 posts and empty queue immediately before submission. No new spend. Avoid duplicating this topic; obtain 24/72h metrics when available.


## November 6 Vids publication

Google Vids free monthly video allowance explainer published; Buffer `6aee5df9ec406dc8710d39b0` verified sent, https://www.instagram.com/p/DfawKXinTik/ . Delivery verified 2026-11-06T23:09Z (Buffer UI 5:09 PM). Five original 1080x1350 slides, fictional untested prompt, source links, original film-strip cover labeled; AI disclosure enabled. Files/ledger `2026-11-06-vids/`. One post observed for Nov 6; reserve two hours from this delivery before another. No new spend. Research-board idea reused, no duplicate draft. Metrics snapshot in `2026-11-06-metrics.json`; follower count/profile visits unavailable in Buffer view, data lag about five hours. No causal growth conclusion.
