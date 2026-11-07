# Optional GitHub Pages media staging

`pages_media.py` stages already reviewed slides at content-derived paths for a GitHub Pages site. It never uploads, edits a repository, enables Pages, changes DNS, or posts. Example:

```
python3 pages_media.py --carousel /path/to/approved/carousel --site-base https://YOURNAME.github.io/YOURMEDIAREPO --out /private/new-staging-folder
```

The site-base must be the exact owner-controlled HTTPS github.io Pages site. Output contains `media/<sha256>.png`, `.nojekyll`, and `urls.json`. The URL is an unverified prediction until an authorized operator deploys these files to that exact public Pages site and validates access. Publishing to Pages makes slides public before a social post, and GitHub Pages has usage/content limits; check https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits and service terms. The existing ayushtyagi.dev portfolio is not involved. Do not enable or change DNS without reviewing the site setup.

Page files can be replaced or removed by repository operators. Hashed names alone do not enforce immutability; verify served bytes using `reviewed_publish.py` immediately before submission, maintain access until Buffer retrieves them, and monitor final posting. Cache propagation can delay availability. Private drafts and secrets must never go into a public repo. The delivery loop currently only supports the R2 uploader; Pages staging and deployment are separate manual steps and not end-to-end automated. No live Pages deployment, Buffer retrieval, or Instagram publication has been tested.

## GitHub connector capability check

The connected GitHub tools include `create_blob` with base64 input, so they can represent PNG binary data; an earlier assessment that binary upload was unavailable was incorrect. The connector also exposes tree, commit and branch-ref operations. It does not expose repository creation or Pages configuration in the available tool list. No suitable dedicated Trywise repository has been identified, so none of the existing personal/project repositories should be repurposed. A separate repository and Pages configuration are still needed before a live test; Pages use and account eligibility must be verified. These tool capabilities have not been tested on a repository for this project.
