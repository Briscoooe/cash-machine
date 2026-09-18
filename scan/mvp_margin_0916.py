#!/usr/bin/env python3
"""MVP margin-of-victory ladder prices."""
import json, urllib.request

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

evs = get("https://gamma-api.polymarket.com/events?slug=mecklenburg-vorpommern-parliamentary-election-vote-share-margin-of-victory")
for ev in evs:
    for m in ev.get('markets', []):
        print(m.get('question')[:90], '|', m.get('outcomePrices'), '| vol24', m.get('volume24hr'))
