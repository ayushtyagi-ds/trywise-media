#!/usr/bin/env python3
"""Render review-only Trywise carousels from structured draft JSON. Never publishes."""
import argparse
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlparse

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit('Pillow is required: python3 -m pip install -r requirements.txt')

W, H = 1080, 1350
NAVY, PAPER, LIME, CORAL, MUTED = '#121a36', '#f6f4ec', '#d6f25b', '#ff805f', '#687289'

class RenderError(ValueError):
    pass

def font_path(bold=False):
    override = os.environ.get('TRYWISE_FONT_BOLD' if bold else 'TRYWISE_FONT_REGULAR')
    candidates = ([override] if override else []) + ([
        '/System/Library/Fonts/Supplemental/Arial Bold.ttf' if bold else '/System/Library/Fonts/Supplemental/Arial.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    ])
    for name in candidates:
        if name and Path(name).is_file():
            return name
    raise RenderError('Font not found. Set TRYWISE_FONT_REGULAR and TRYWISE_FONT_BOLD to readable TTF paths.')

def font(size, bold=False):
    return ImageFont.truetype(font_path(bold), size)

def checked_text(value, name, max_chars):
    if not isinstance(value, str) or not value.strip() or len(value) > max_chars:
        raise RenderError(f'{name} must be non-empty text, at most {max_chars} characters')
    if any(ord(c) < 32 and c not in '\n\t' for c in value):
        raise RenderError(f'{name} contains unsupported control characters')
    return value.strip().replace('\t', ' ')

def lines_for(draw, text, face, width):
    lines = []
    for para in text.split('\n'):
        words = para.split()
        if not words:
            lines.append(''); continue
        line = ''
        for word in words:
            candidate = f'{line} {word}'.strip()
            if draw.textlength(word, font=face) > width:
                raise RenderError('A word or URL is too wide for the slide; shorten it.')
            if draw.textlength(candidate, font=face) <= width:
                line = candidate
            else:
                lines.append(line); line = word
        lines.append(line)
    return lines

def block(draw, text, box, size, min_size, fill, bold=False, line_ratio=1.24):
    x, y, width, height = box
    # Decrease type size only as far as the legibility floor; overflow is an error.
    for point in range(size, min_size - 1, -2):
        face = font(point, bold)
        try:
            lines = lines_for(draw, text, face, width)
        except RenderError:
            continue
        advance = int(point * line_ratio)
        if len(lines) * advance <= height:
            for line in lines:
                draw.text((x, y), line, font=face, fill=fill, anchor='lt')
                y += advance
            return
    raise RenderError(f'Text does not fit legibly: {text[:70]!r}')

def validate(draft):
    if not isinstance(draft, dict) or not isinstance(draft.get('slides'), list):
        raise RenderError('Draft must contain a slides array')
    slides = draft['slides']
    if not 3 <= len(slides) <= 8:
        raise RenderError('Draft must have between 3 and 8 slides')
    clean = []
    for i, slide in enumerate(slides):
        if not isinstance(slide, dict): raise RenderError(f'slides[{i}] must be an object')
        clean.append({'heading': checked_text(slide.get('heading'), f'slides[{i}].heading', 150),
                      'body': checked_text(slide.get('body'), f'slides[{i}].body', 700)})
    source = draft.get('source')
    if not isinstance(source, dict): raise RenderError('source object required')
    url = checked_text(source.get('url'), 'source.url', 2000)
    parsed = urlparse(url)
    if parsed.scheme not in ('http','https') or not parsed.hostname or parsed.username or parsed.password:
        raise RenderError('source.url must be an http(s) URL without credentials')
    title = checked_text(source.get('title'), 'source.title', 300)
    date = checked_text(source.get('published_at'), 'source.published_at', 50)
    caption = checked_text(draft.get('caption'), 'caption', 4000)
    return clean, {'url':url,'domain':parsed.hostname,'title':title,'published_at':date}, caption

def make_slide(slide, number, total, source):
    first = number == 1
    last = number == total
    dark = first or last or number % 3 == 0
    bg, fg = (NAVY, PAPER) if dark else (PAPER, NAVY)
    im = Image.new('RGB', (W,H), bg)
    d = ImageDraw.Draw(im)
    block(d, 'TRYWISE', (65,57,175,42), 30, 28, fg, True)
    block(d, 'AI', (224,57,80,42), 30, 28, CORAL, True)
    block(d, 'FIELD NOTES', (758,62,260,34), 23, 21, fg, True)
    d.line((65,116,1015,116), fill='#525c73' if dark else '#cdd4d1', width=2)
    label = 'THE BIG PICTURE' if first else ('TAKEAWAY' if last else f'WHAT TO KNOW  /  {number-1:02d}')
    block(d, label, (68,157,900,42), 25, 23, LIME if dark else '#53674b', True)
    if first:
        # Large cover and small visual mark, not a screenshot or a claim of a product test.
        block(d, slide['heading'], (65,236,940,345), 90, 45, fg, True, 1.14)
        d.rounded_rectangle((66,685,1014,1064), radius=36, fill='#d6f25b')
        d.rounded_rectangle((108,728,210,830), radius=24, fill=NAVY)
        block(d, 'AI', (127,749,65,45), 31, 29, LIME, True)
        block(d, slide['body'], (247,724,700,295), 46, 32, NAVY, False, 1.28)
    elif number % 2 == 0 and not last:
        block(d, slide['heading'], (65,236,930,325), 73, 45, fg, True, 1.15)
        d.line((82,650,82,1050), fill=CORAL, width=12)
        block(d, slide['body'], (126,650,840,410), 50, 32, fg, False, 1.3)
    else:
        block(d, slide['heading'], (65,236,930,325), 73, 45, fg, True, 1.15)
        d.rounded_rectangle((65,640,1015,1090), radius=32, fill='#eef0e6' if dark else '#e3ebd0')
        block(d, f'{number:02d}', (105,674,120,65), 38, 34, CORAL, True)
        d.line((105,750,970,750), fill='#c5cdbf', width=2)
        block(d, slide['body'], (105,785,850,260), 45, 32, NAVY, False, 1.3)
    d.line((65,1205,1015,1205), fill='#525c73' if dark else '#cdd4d1', width=2)
    source_label = f"SOURCE: {source['domain']} · {source['published_at']}"
    block(d, source_label, (65,1230,810,55), 21, 18, fg, True)
    block(d, f'{number:02d} / {total:02d}', (900,1230,110,55), 23, 21, fg, True)
    return im

def render(draft, dest):
    slides, source, caption = validate(draft)
    dest = Path(dest)
    if dest.exists(): raise RenderError(f'Output path already exists: {dest}; choose a new path')
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix='.trywise-render-', dir=dest.parent))
    try:
        for i, slide in enumerate(slides, 1):
            make_slide(slide, i, len(slides), source).save(tmp / f'{i:02d}.png', format='PNG', optimize=True)
        (tmp/'caption.txt').write_text(caption + '\n\nSource: ' + source['url'] + '\n', encoding='utf-8')
        claims=draft.get('claims',[]); notes=draft.get('review_notes',[])
        if not isinstance(claims,list) or len(claims)>15 or not isinstance(notes,list) or len(notes)>20:
            raise RenderError('Invalid evidence or review notes')
        evidence=[]
        for claim in claims:
            if not isinstance(claim,dict): raise RenderError('Invalid claim')
            evidence.append({'text':checked_text(claim.get('text'),'claim',1000),'evidence':checked_text(claim.get('evidence'),'evidence',500)})
        clean_notes=[checked_text(note,'review note',1000) for note in notes]
        manifest={'status':'needs_review','source':source,'slides':len(slides),'claims':evidence,'review_notes':clean_notes,'note':'Source excerpts do not verify all claims; review the original page, slides and caption.'}
        (tmp/'manifest.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
        tmp.rename(dest)
    except Exception:
        shutil.rmtree(tmp, ignore_errors=True)
        raise
    return dest

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('draft',type=Path); parser.add_argument('output',type=Path)
    args=parser.parse_args()
    try:
        draft=json.loads(args.draft.read_text(encoding='utf-8'))
        path=render(draft,args.output)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f'Render failed: {exc}',file=sys.stderr); return 1
    print(f'Review-only carousel created: {path}'); return 0
if __name__=='__main__': raise SystemExit(main())
