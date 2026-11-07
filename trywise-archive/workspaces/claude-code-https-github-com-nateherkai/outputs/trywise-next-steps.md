# Trywise AI: next steps

## What is ready

- Trywise AI Instagram is a professional Creator account, according to the owner.
- A Buffer account was created and the Free plan was visible during setup.
- The local pipeline is a prototype: it can collect sources, draft and render carousels, and show them for review. Its provider integrations have been tested with simulated responses, not live accounts.

## What needs your help

1. Sign in to the Trywise AI account in the Instagram tab opened next to Buffer. Use the Instagram sign-in screen; do not share passwords or verification codes in chat.
2. Tell Codex when you are signed in. We can then return to Buffer and inspect the requested permissions before completing the connection. Buffer may still report an account-specific restriction.
3. The suspicious Facebook business portfolios and advertising restriction should be investigated through Meta separately; do not connect the unfamiliar portfolio to Trywise AI.
4. We still need to determine whether your existing Gemini Pro charge counts inside the CAD $50 cap. Until clear, treat the total cap conservatively and do not activate paid API billing or storage subscriptions.

## What the pipeline needs before a real test

- A working Instagram-to-Buffer connection and dedicated Buffer API access.
- A Gemini API project with verified free-tier quota and data terms; your Gemini Pro app subscription is not automatically API credit.
- Stable public hosting for reviewed images, tested with Buffer. The prototypes explore R2 and GitHub Pages; neither has been deployed.
- Persistent hosting for the worker and queue, plus a spending plan that includes all subscriptions, taxes, and exchange fees.
- One reviewed test post, tested once on the authorized destination, with confirmation of actual Instagram publication.

No test images have been uploaded, no automated Instagram post has been published, and no new paid subscription has been activated. A mocked integration test does not verify any provider or guarantee the system will stay within the budget.

## Existing GitHub Pages portfolio

The connected GitHub account has a public `ayushtyagi-ds.github.io` repository whose `CNAME` file is `ayushtyagi.dev`. This appears to be the existing portfolio. Do not modify that repository or its DNS for the Trywise pilot. If GitHub Pages media is chosen later, use a separate project and verify the actual public URLs, custom-domain behavior, publishing rights, and whether Buffer can fetch those URLs. The GitHub connector does not currently expose repository creation or binary image upload for this workflow, so this is not yet an automated hosting solution.
