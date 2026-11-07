# Trywise AI — start here

This is a **prototype**, not yet an always-on social media account manager. You can try the first part for free without connecting your accounts. The demo uses made-up information, so do **not** post it as news.

## What the demo does

The demo takes a fictional source and an example AI response, creates a four-slide carousel and caption, and opens a review page on your Mac. It does not call Gemini, send data to Instagram, create an account, or publish anything. It needs Python 3.12 or newer and the Pillow image library. Installing Pillow requires an internet connection; after it is installed the demo itself works offline.

## Run it on your Mac

1. Extract the ZIP and open **Terminal**.
2. Type `cd ` (including the space), drag the extracted `trywise-pipeline` folder onto the Terminal window, and press Return. This changes to the folder without typing its full path.
3. Paste these commands one at a time, pressing Return after each one:

   ```sh
   python3 -m venv .venv
   .venv/bin/python -m pip install -r requirements.txt
   .venv/bin/python demo.py --review
   ```

4. Open **http://127.0.0.1:8765/** in your browser. Scroll through the slides and caption. The example is fictional and should not be published.
5. When you finish, return to Terminal and press **Control-C** to stop the local review page. The carousel files are in the folder path printed in Terminal.

If Terminal says `python3` is missing or its version is older than 3.12, install a current Python release first. Check your version with `python3 --version`. If the address doesn't open, check that the server is still running and no other app is using port 8765. You can use another port with `.venv/bin/python demo.py --review --port 8766`, then open `http://127.0.0.1:8766/` instead. On Linux, fonts may need configuring; see `RENDERING.md`.

## What the review button means

The review page's **Record local review** button stores an `approval.json` file tied to those exact local images and caption. The review screen itself does not publish or upload; however, if automatic delivery is separately enabled, recording a review can cause a post to be sent to the configured channel. It does not validate facts or let you choose a destination. For a real post, check the source and every slide before recording review. An existing approval isn't overwritten; the demo makes a new folder on each run.

## What is available next

- **Research:** `trywise.py` can collect candidate headlines from configured official feeds. See `README.md`.
- **Drafting:** `draftgen.py` and `pipeline_runner.py` can prepare drafts with the Gemini API. A real request needs an API key and an explicit opt-in and may cost money; your Gemini app subscription may not cover API usage. Live access has not been tested. See `DRAFTING.md` and `ORCHESTRATION.md`.
- **Review queue:** `worker.py` can collect and draft periodically while the program and computer are running. It does not post, and its per-day attempt limit is not a dollar spending cap. See `WORKER.md`.
- **Hosting and publishing:** Optional prototypes can host reviewed images and submit to Buffer after separate steps. They have not been tested with real accounts; storage, provider billing, actual Instagram publication, and account eligibility still need verification. See `MEDIA_HOSTING.md` and `REVIEWED-PUBLISHING.md`.

Keep the **CAD $50/month ceiling** in mind, including your existing Gemini subscription if it counts toward that amount, currency conversion and tax. Do not enable paid API access or generate paid service keys until the cost and any payment method requirements are clear. The prototype does not enforce a hard spending limit.

Never paste passwords, API keys, access tokens or verification codes into chat, screenshots or source files. Your Facebook security issue is separate and should be resolved through Meta's recovery process. No software here has connected to or changed those accounts.

## Check readiness without sharing keys

After configuring the environment yourself, run `python3 preflight.py` to see which optional components and credential variables are present. It prints only true/false, never their values, and does not contact any service. A present credential might still be expired or lack permission, and the check cannot verify spending, CAD budget, sign-in status, or actual publication. To check the basic shape of a delivery policy, add `--policy /private/path/policy.json`.
