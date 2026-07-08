#!/usr/bin/env python3
"""Regenerate animations.js from the animations/ folder.
Run from the repository root: python tools/build_animation_manifest.py
"""
import json, re, html
from pathlib import Path
from urllib.parse import quote

def clean_text(s):
    s = re.sub(r'<[^>]+>', ' ', s or '')
    s = html.unescape(s)
    return re.sub(r'\s+', ' ', s).strip()

def title_case_from_path(stem):
    stem = re.sub(r'[_\-]+', ' ', stem)
    return re.sub(r'\s+', ' ', stem).strip().title()

def extract_title_and_desc(path):
    txt = path.read_text(encoding='utf-8', errors='ignore')
    title = ''
    for pat in [r'<title[^>]*>(.*?)</title>', r'<h1[^>]*>(.*?)</h1>']:
        m = re.search(pat, txt, flags=re.I|re.S)
        if m:
            title = clean_text(m.group(1))
            break
    if not title:
        title = title_case_from_path(path.stem)
    desc = ''
    m = re.search(r'<meta\s+[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)["\'][^>]*>', txt, flags=re.I|re.S)
    if m:
        desc = clean_text(m.group(1))
    return title, desc

def url_for(path):
    rel = path.as_posix()
    return '/'.join(quote(seg) for seg in rel.split('/'))

root = Path('animations')
items = []
for category_dir in sorted([p for p in root.iterdir() if p.is_dir()], key=lambda p: p.name.lower()):
    category = re.sub(r'\s+', ' ', category_dir.name.replace('_',' ').replace('-', ' ')).strip()
    for hp in sorted(category_dir.rglob('*.html'), key=lambda p: p.as_posix().lower()):
        title, desc = extract_title_and_desc(hp)
        items.append({
            'title': title,
            'category': category,
            'description': desc or f'Interactive animation in the {category} category.',
            'url': url_for(hp),
            'folder': hp.parent.relative_to(root).as_posix(),
            'filename': hp.name,
        })
Path('animations.js').write_text('window.ANIMATIONS = ' + json.dumps(items, indent=2, ensure_ascii=False) + ';\n', encoding='utf-8')
print(f'Wrote animations.js with {len(items)} animations.')
