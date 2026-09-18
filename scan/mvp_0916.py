#!/usr/bin/env python3
"""Get Mecklenburg-Vorpommern + Hamburg election market slugs from gamma."""
import json, urllib.request

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

data = get("https://gamma-api.polymarket.com/public-search?q=mecklenburg&limit_per_type=5")
for ev in data.get('events', []):
    print('==', ev['slug'], '| end', ev.get('endDate'))
    for m in ev.get('markets', []):
        print('   ', m.get('question')[:90], '|', m.get('outcomePrices'))
