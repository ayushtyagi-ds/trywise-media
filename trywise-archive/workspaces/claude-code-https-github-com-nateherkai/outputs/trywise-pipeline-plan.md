# Trywise AI — content and automation plan

Research snapshot: October 31, 2026. Budget ceiling: CAD $50/month, including taxes, exchange fees, and any existing Gemini subscription if that subscription is meant to count against the ceiling. The exact allowance and current charges depend on your accounts and region. Never enter passwords, API keys, or access tokens into chat.

## Objective and positioning

A faceless account by a software developer: “We test AI tools on real tasks and show what worked, what broke, and who can use the result.” Audience: curious professionals and early-stage builders who want useful AI workflows without needing to be developers. Working goal: 1,000 net Instagram followers/month, a target rather than a forecast. The owner later authorized automatic publishing without per-post approval. Automated systems should still verify sources and visuals, and real tool tests and evidence must be recorded.

## What we learned from creators

- Nate Herk demonstrates repeatable workflows and offers resources/community alongside them. His referenced nine-platform workflow uses a Google Sheet, n8n, and Blotato to distribute supplied content; his presentation includes a Blotato promotion. It is evidence of a distribution method, not proof of fully automated content creation or revenue. https://www.linkedin.com/posts/nateherkelman_this-n8n-workflow-auto-posts-to-9-different-activity-7361417391244722199-ExhH ; https://www.nateherk.com/about
- Matt Wolfe’s Future Tools uses AI for summaries but describes human selection/review of news. A recurring news format and a searchable resource are useful ideas, not proof of causal growth. https://futuretools.io/about ; https://mattwolfe.com/
- Treat these as testable patterns: a specific audience; recurring series; a clear problem and practical result; distinctive viewpoint; source/date; and a useful follow-up resource. We cannot research literally every creator or verify private revenue.

## Content formats and first month

Three original Instagram carousels per week; reuse source material as YouTube videos only after producing real demonstrations and narration. Test one optional short video after the carousel process works. Do not imply text carousels automatically qualify as YouTube videos or guarantee monetization.

- 1 news explainer/week: primary announcement, what changed, who has access, practical implication, and clearly identified source/date. Recheck right before publication.
- 1 practical tutorial/week: one workflow, example input, steps, a realistic output, and caveats. Use fictional data. Label examples that have not been tested.
- 1 developer experiment/week: same input, recorded test, what actually happened, cost/plan/time if verified, and failure or limitation. Human interaction is needed if access or reliable automation is unavailable.

Four-week sequence:
1. What Trywise tests; use AI to turn sample meeting notes into action items; test a simple app-generation task.
2. One current primary-source AI announcement; compare outputs from two accessible tools on the same document; a safe debugging workflow.
3. One verified announcement; extract structured data from sample text; measure whether AI-generated code passes chosen tests.
4. One verified announcement; show a reusable research checklist; report the month’s real results and errors.

A five-slide carousel: hook; what changed/problem; evidence/demo; practical steps or limitations; verdict and source. Source date on slide; links in caption/bio as appropriate. Avoid copying other people's graphics or posting their videos without rights.

## Architecture and control points

1. Scheduled collection: permitted public feeds and official provider blogs; record URL, publisher, timestamp, raw headline, dedupe ID. Do not use bypass techniques or scrape private/restricted content.
2. Prioritization: discard duplicates and old stories, score relevance, pick 3–5 candidates with clear timestamps. News stories require current primary sources.
3. Drafting: use Gemini API or another provider to produce structured JSON with headline, claims, source URLs, limitations, slide copy and caption. Model output is a draft; source must substantiate claims. Gemini subscription and API quotas/billing are separate.
4. Evidence: fetch primary source, record exact provenance and dates. A link existing is not proof that each claim is true. Test claims about tool behavior on sample data; label untested items.
5. Design: render 4:5 original carousel slides from editable layouts, with safe margins and source/date. Build varied layouts and visual hierarchy; audit on phone. Avoid generic repeated cards and copyrighted stock unless properly licensed.
6. Queue: store draft media and claims, review status, cost, and source links. Record source checks and a quality review for each post; the owner has authorized publication without per-post approval. News should expire if it becomes stale.
7. Publish: use the connected Buffer Instagram channel, verify outcomes, and prevent duplicates. Record post ID; retry cautiously; report failures. Avoid mass follows, fabricated engagement, unsolicited DMs, or platform bypass.
8. Analytics: weekly capture reach, views, saves, shares, profile visits, follows and net follows. Instagram metrics depend on actual account/API access. Track follow per 1,000 reached as diagnostic, not a guarantee. For video, retention and completion inform changes.

Potential implementation: GitHub Actions scheduled job + Python for collection, deduplication, and rendering; a Gemini API key in GitHub Secrets; GitHub artifacts or private storage for previews; a quality-checked queue; and the connected Buffer integration. GitHub Pages is static hosting, not a worker, and public Pages cannot safely hold private drafts or secrets. Scheduled jobs can be delayed; jobs must fail closed on API errors or failed quality checks. Keep test and production credentials separated. Never commit credentials.

A recurring Codex publishing task is configured, but no unattended end-to-end run has yet been verified. Buffer MCP access works; one user-scheduled carousel was sent and appeared on Instagram. A composer upload of a second carousel succeeded and was saved as an unscheduled draft. The recurring job still needs a live run to verify unattended access, source checks, duplicate handling, and actual recurring costs. The Meta screen required a business portfolio for the chosen unified-login setup, and account restrictions blocked creating one. A third-party scheduler may still require permissions affected by that restriction; do not assume it bypasses or solves it. Secure the Facebook account and use Meta’s review path.

## Budget options

Option A — lowest-cost pilot: $0 additional committed spend. Gemini API free tier where eligible, GitHub Free within allowance, original local graphics, manually publish/schedule the first posts. Limits and actual access require verification. The free Gemini API may use content to improve Google products: use public or fictional material only. https://ai.google.dev/gemini-api/docs/pricing ; https://docs.github.com/en/billing/reference/product-usage-included

Option B — free scheduler evaluation: Buffer’s free pricing page currently lists up to 3 channels and 10 scheduled posts per channel; API availability and actual Instagram carousel support/account eligibility must be verified. https://buffer.com/pricing

Option C — Blotato: Starter advertised US$29/month; exact CAD depends on exchange rate, taxes and billing; converting US$29 at hypothetical CAD 1.40/USD = CAD 40.60 before tax, leaving CAD 9.40 for all other costs. This is arithmetic, not a live exchange quote. API unavailable during trial; generating its API key immediately starts a paid subscription. Includes stated AI credits but test per-carousel credit consumption before committing. Any n8n hosting or model API costs are additional. https://www.blotato.com/pricing ; https://help.blotato.com/settings/billing-and-credits

Set a hard spending ceiling with service provider controls where available and disable paid billing until deliberately chosen. Budget alerts do not necessarily prevent charges. Confirm whether Gemini Pro is included inside CAD 50 or is an already-paid separate cost before committing.

## Measurement and monetization

- Establish baseline followers and track weekly net follows; target is 1,000/month, not a forecast or paid-engagement target.
- Log each post’s topic, format, source, date, time, reach, saves, shares, profile visits and follower change. Attribute results carefully; small samples are noisy.
- After 12 posts, compare saves and shares per reach and review which topics generated qualified comments. Keep hypotheses, avoid declaring winners prematurely.
- Initial monetization tests: useful free template; optional affiliate offers only for relevant tools with clear disclosure; later an original paid template or service, if audiences actually want it. No revenue estimates without evidence.
- YouTube ad eligibility commonly requires 1,000 subscribers plus 4,000 valid public watch hours in 12 months or 10 million valid Shorts views in 90 days, plus other requirements and review. Earlier access to some features has lower thresholds. Requirements vary by region and can change. https://support.google.com/youtube/answer/13429240
- YouTube prohibits monetization of mass-produced repetitive or minimally transformed content. AI assistance itself is not automatically disqualifying. Realistic altered/synthetic content can require disclosure. https://support.google.com/youtube/answer/1311392 ; https://support.google.com/youtube/answer/14328491

## Acceptance tests before launch

1. Select a real primary source and confirm every factual claim, date, and access condition.
2. Produce a visually reviewed carousel at 1080×1350 with legible copy and an original design.
3. Test one real workflow, record input/output and limitations without personal data.
4. Measure generation time and actual marginal usage; project the month including taxes and FX.
5. Demonstrate duplicate detection, stale-story rejection, and missing-credential behavior; the owner has authorized automatic publishing.
6. Confirm secure secrets, recovery, allowed API scopes, and whether social account restriction is resolved.
7. Verify the already published test and absence of duplicates; observe a scheduled automated run and record failure handling.
8. Log first analytics and provide a weekly review to the account owner. Do not claim autonomous operation before a real scheduled end-to-end test succeeds.

## Publishing research update

Buffer documents direct Instagram Login for professional Creator accounts, with automatic publishing and analytics without a Facebook Page for ordinary use; it lists limitations for location, collaborators, and music. This is a documented integration option, not a verified solution for this particular account or restriction. The user should sign in through Buffer/Meta directly and review requested scopes; do not copy credentials into chat. https://support.buffer.com/en-us/articles/connecting-your-instagram-account-to-buffer-n9Ad6veXsu

Buffer also documents a 3:4 to 1.91:1 range for automatic image publishing; 1080×1350 (4:5) falls within that range; test actual carousel requirements before posting. https://support.buffer.com/articles/instagram-error-library-P7TDLmDSKm

## Currency check: October 30, 2026

Bank of Canada's indicative daily rate was USD 1 = CAD 1.3960. At that rate alone, Blotato's advertised USD 29/month is CAD 40.48 before taxes, card conversion spreads, or other services, leaving CAD 9.52 of a CAD 50 ceiling. This is not a billing quote and does not include the user's Gemini Pro charge. Confirm actual account prices and subscriptions before buying. Sources: https://www.bankofcanada.ca/rates/exchange/daily-exchange-rates-lookup/?dF=2026-10-17&dT=2026-10-31&lP=lookup_daily_exchange_rates_2017.php&rangeType=dates&sR=2017-01-01&se=FXUSDCAD ; https://www.blotato.com/pricing

## Live setup update: October 31, 2026

Buffer workspace My organization is connected to @trywiseai. The first five-slide carousel was sent and appeared on the Instagram profile. A separate four-slide Gemini draft is saved but unscheduled. A Codex automation configured in the user’s other chat is active Monday, Wednesday and Friday at 9 AM America/Edmonton; the owner there explicitly authorized automatic publishing without per-post approval. Its first scheduled execution has not yet been verified. On October 31, the account showed 0 followers and 1 post. A labelled test draft must not be published. See `/Users/phoenix/Documents/Codex/2026-10-31/con/outputs/trywise-setup-status.md` for the current operational checkpoint.
