# Model handoff and cost

## How do the three services connect without manual handoffs?

### Takeaway

Self-hosted n8n can call authenticated APIs and pass structured data through a workflow; the current chat subscriptions are not equivalent to portable API credentials. Video generation needs its own supported endpoint and cost measurement.

### Cited Findings

- n8n documents [Anthropic API-key credentials](https://docs.n8n.io/integrations/builtin/credentials/anthropic/), an [Anthropic chat model node](https://docs.n8n.io/integrations/builtin/cluster-nodes/sub-nodes/n8n-nodes-langchain.lmchatanthropic/), and [OpenAI API-key credentials](https://docs.n8n.io/integrations/builtin/credentials/openai/). n8n Cloud can use Gateway credits in supported nodes; that is not the same as self-hosted user subscription access.
- Anthropic says Claude chat and Console/API are billed separately. The current help page says certain Max, Ultra and Team plans include monthly API credits; plan, eligibility, and remaining balance are unknown here. [Claude support](https://support.anthropic.com/en/articles/9876003-i-subscribe-to-a-paid-claude-ai-plan-why-do-i-have-to-pay-separately-for-api-usage-on-console).
- OpenAI says ChatGPT and API billing are separate; some eligible subscriptions may offer promotional API credits. [OpenAI billing](https://help.openai.com/en/articles/9039756-managing-billing-for-chatgpt-and-the-api-platform).
- Google says Gemini API projects have their own free and paid tiers, with account/model-specific availability, and charges depend on the API project. [Google billing](https://ai.google.dev/gemini-api/docs/billing/). Google's employee states consumer Google AI Pro/AI Studio interface allowances differ from programmatic API billing. [Google developers forum](https://discuss.ai.google.dev/t/google-ai-pro-subscriber-hitting-daily-quota-limit-in-ai-studio-build/187831).
- Anthropic documents that eligible Claude Pro/Max can authenticate Claude Code with a Claude subscription. Whether an unattended scripted use case is supported under the user's actual entitlement and conditions needs separate verification. [Claude Code setup](https://docs.anthropic.com/en/docs/claude-code/getting-started).
- Google's current [Gemini API video overview](https://ai.google.dev/gemini-api/docs/video) says the `veo-3.1-*-preview` Gemini Developer API endpoints shut down on 2026-10-22 and directs developers to `gemini-omni-1.1-flash` or GA models through Google's separate enterprise platform. Older official Veo pages and indexed price snippets contradict this shutdown notice and include obsolete runnable snippets; use the explicit shutdown notice over them.
- [Gemini Omni guide](https://ai.google.dev/gemini-api/docs/omni) documents image-to-video, 9:16 portrait, reference images and direct REST/SDK use. Prompting and reference images can help consistency but the documentation does not guarantee identical characters every time.

### Inferences

- For a robust automation pilot, pass a structured script/storyboard plus stable character references through model API calls; persist output files, costs and processing state, retry transient failures carefully, and review generation quality automatically. A GUI session can be used manually but is not equivalent to a durable API integration.
- Not every job needs all three models: test whether the second reviewer improves output enough to justify its cost and latency.

### Gaps

- Exact user's Claude and ChatGPT plan, any included developer credits, Gemini account/project eligibility, and actual usable quotas have not been inspected. Do not request or expose keys in chat.
- Exact Gemini Omni character consistency, Canadian commercial terms, per-project API quota, and usable visual quality for this couple are untested.

## Can the plan fit CAD $50 per month?

### Takeaway

Short text calls can be relatively inexpensive while AI-generated video can dominate the budget. Daily video is not demonstrably viable under CAD $50 total, especially if existing subscription fees count.

### Cited Findings

- Google currently lists Gemini Omni Flash (`gemini-omni-1.1-flash`) video generation as paid-tier only: US$17.50/million video output tokens, or approximately US$0.10/second of 720p output, with input separately priced. [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing).
- Google's [Gemini API billing](https://ai.google.dev/gemini-api/docs/billing/) says default paid tier cap may be US$250; project spend caps are experimental and subject to billing latency and possible overages. Do not describe an alert or provider cap as a perfect hard CAD $50 limit.
- For reference, Anthropic lists Claude Haiku 4.5 at US$1/million input and US$5/million output tokens under standard pricing; actual spend depends on tokens, image inputs, tools, caching, retries and model availability. [Claude API pricing](https://platform.claude.com/docs/en/about-claude/pricing).
- Bank of Canada indicative daily rate for October 30, 2026: US$1 = CAD $1.3960; card fees, tax and future exchange movement are not included. [Bank of Canada](https://www.bankofcanada.ca/rates/exchange/daily-exchange-rates-lookup/?dF=2026-10-17&dT=2026-10-31&lP=lookup_daily_exchange_rates_2017.php&rangeType=dates&sR=2017-01-01&se=FXUSDCAD).

### Inferences

- Illustrative 30 days × 16 generated seconds at US$0.10/sec = US$48, approximately CAD $67.01 output only at the dated exchange rate. This excludes generated clips discarded on quality checks, input tokens, sales taxes, other model calls, hosting/electricity and subscriptions, so it is not a full budget.
- Illustrative 12 Reels × 16 generated seconds = US$19.20, approximately CAD $26.80 for output alone. If half the generated seconds must be regenerated, this goes to US$28.80 ≈ CAD $40.20 output alone. Both examples assume exactly those billable seconds and no free credits; actual output, retries and pricing can differ.
- Reserve upfront per-job cost plus maximum attempts against an application-managed monthly ledger, set provider caps lower than the allocation where available, and stop paid calls at the ledger limit. Provider delays, in-flight calls and other usage can still cause overshoot; never promise a mathematically hard cap solely from a spend alert.

### Gaps

- Whether the CAD $50 includes existing subscriptions is unresolved. Current exchange rate is illustrative, not a guaranteed billed conversion. The likely number of takes per publishable scene is unknown; this is the largest cost uncertainty.
