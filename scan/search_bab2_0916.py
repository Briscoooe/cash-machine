#!/usr/bin/env python3
"""List all Bab el-Mandeb search events with market prices."""
import json, urllib.request

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

data = get("https://gamma-api.polymarket.com/public-search?q=bab+el-mandeb&limit_per_type=10")
for ev in data.get('events', []):
    print("==", ev['slug'], "| closed:", ev.get('closed'), "| end:", ev.get('endDate'))
    for m in ev.get('markets', []):
        prices = m.get('outcomePrices')
        print("   ", m.get('question')[:95], "|", prices, "| end", m.get('endDate'))
