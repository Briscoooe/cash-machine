#!/usr/bin/env python3
"""Cron scan: pull sibling prices for Chongqing temperature event."""
import json, urllib.request

H = {'User-Agent': 'Mozilla/5.0'}
def get(u):
    return json.load(urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=30))

# search gamma for chongqing temperature events
evs = get('https://gamma-api.polymarket.com/events?limit=40&closed=false&slug_contains=highest-temperature-in-chongqing')
print('events:', len(evs))
for e in evs[:6]:
    print(e.get('title'), '| end', e.get('endDate', '')[:10])
    for m in e.get('markets', [])[:12]:
        op = json.loads(m.get('outcomePrices', '[]') or '[]')
        print('   ', (m.get('question') or '?')[:90], op[:1])
