#!/usr/bin/env python3
"""Cron scan: review exact-price descriptions of 6-8 candidate markets from the 150-event pull."""
import json, urllib.request, re

cands = json.load(open('/root/cash-machine/runtime/ops/scan_cands_latest.json'))

# Candidate questions worth a price-resolution look
targets = [
    ('nvidia', None), ('eps', None), ('quarterly', None), ('revenue', None),
    ('gdp', None), ('inflation', None), ('cpi', None), ('ceasefire', None),
    ('nobel', None), ('temperature', None), ('chongqing', None), ('bez', None),
    ('moderate party', None), ('besiktas', None), ('leverkusen', None), ('osasuna', None),
    ('kashiwa', None), ('warsh', None), ('xi jinping', None), ('first blood', None),
]
found = {}
for c in cands:
    ql = c['q'].lower()
    for t, _ in targets:
        if t in ql and t not in found:
            found[t] = c
            break

def by_slug(slug):
    url = f'https://gamma-api.polymarket.com/events?slug={slug}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    return json.load(urllib.request.urlopen(req, timeout=30))

for t, c in found.items():
    print('=' * 20, t.upper())
    print(c['q'], '| price', round(c['price'], 3), '| end', c['end'])
    ev = by_slug(c['slug'])
    if ev:
        m = ev[0].get('markets', [{}])[0]
        print((m.get('description') or '')[:700].replace('\n', ' '))
