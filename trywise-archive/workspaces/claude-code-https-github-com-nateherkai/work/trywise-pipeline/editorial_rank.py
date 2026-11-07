#!/usr/bin/env python3
"""Transparent title-based candidate ranking. This does not verify facts or relevance."""
import re

# Small, adjustable heuristics only; humans must verify relevance and source.
WEIGHTS={'developer':5,'developers':5,'coding':5,'code':4,'api':4,'build':3,'workflow':3,'automation':3,'tools':2,'tool':2,'agent':2,'agents':2,'gemini':1,'claude':1,'openai':1,'ai':1}
PENALTIES={'earnings':-3,'quarterly':-2,'investor':-2,'financial':-2,'lawsuit':-2}

def rank_title(title):
    if not isinstance(title,str):return {'score':0,'reasons':[]}
    tokens=set(re.findall(r"[a-z0-9]+",title.lower()))
    found=sorted((w,v) for w,v in {**WEIGHTS,**PENALTIES}.items() if w in tokens)
    return {'score':sum(v for _,v in found),'reasons':[f'{w}: {v:+d}' for w,v in found]}
