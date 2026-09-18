#!/usr/bin/env python3
"""Check W13-BAB-NOV market price via gamma API."""
import json, urllib.request

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

slugs = ["bab-el-mandeb-strait-effectively-closed-by-october-31",
         "bab-el-mandeb-strait-effectively-closed-byptptpt"]
for slug in slugs:
    evs = get(f"https://gamma-api.polymarket.com/events?slug={slug}")
    print("SLUG", slug, "events:", len(evs))
    for ev in evs:
        for m in ev.get('markets', []):
            print(m.get('question'), '| prices:', m.get('outcomePrices'), '| end:', m.get('endDate'))
            print('DESC:', (m.get('description') or '')[:400])
