#!/usr/bin/env python3
"""Re-verify market snapshot prices for the Hormuz Sep 30 thesis."""
import json, urllib.request

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

slugs = ['iran-oman-hormuz-management-agreement-byptptpt-20260804222725871',
         'us-announces-end-of-iranian-blockade-byptptpt-20260713152715080']
for slug in slugs:
    evs = get(f"https://gamma-api.polymarket.com/events?slug={slug}")
    for ev in evs:
        print('==', ev.get('title'))
        for m in ev.get('markets', []):
            q = m.get('question') or ''
            if 'September 30' in q or 'Oct 31' in q or 'October 31' in q:
                print('  ', q[:90], '|', m.get('outcomePrices'), '| vol24', m.get('volume24hr'))
