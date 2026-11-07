# Carousel renderer (preview only)

`render_carousel.py` accepts draft JSON and makes 1080×1350 PNG slides, a caption and a review manifest. It does not publish, verify claims, perform licensing checks, or approve anything. A source link is printed on slides and added to the caption, but it does not prove the draft is true. The included example is illustrative; example.com is not a real source for publishing.

Install Pillow in a dedicated environment using `python3 -m venv .venv`, then `.venv/bin/pip install -r requirements.txt`. Run:

```
.venv/bin/python render_carousel.py example-draft.json /tmp/trywise-carousel-preview
```

Output path must not already exist, so a preview can never silently overwrite an existing project. The JSON object needs a `source` object with `title`, `url`, `published_at`, an array `slides` of 3–8 objects (`heading`, `body`), and `caption`. The renderer sets the resulting manifest to `needs_review` regardless of input. Source URLs must be HTTP(S) and cannot have embedded credentials. If content cannot fit above the minimum font sizes, rendering stops and removes the incomplete temporary files. Shorten the text rather than making it illegible. Slide images need visual review and source and fact verification before publication. Ensure images, fonts, and any source data have appropriate usage rights.

Fonts default to Arial on macOS or DejaVu Sans on Linux. For other environments, set `TRYWISE_FONT_REGULAR` and `TRYWISE_FONT_BOLD` to font file paths. For international scripts, choose fonts with suitable glyph support and visually review: glyph coverage is not automatically checked.
