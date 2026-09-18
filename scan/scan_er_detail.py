#!/usr/bin/env python3
"""Fetch market description + sibling prices for the ER most-seats event."""
import json, urllib.request

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "scan/1.0"})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

ev = get("https://gamma-api.polymarket.com/events?slug=which-party-will-gain-most-seats-in-russian-parliamentary-election")[0]
print("title:", ev.get("title"))
print("desc:", (ev.get("description") or "")[:2500])
for m in ev.get("markets", []):
    op = json.loads(m["outcomePrices"])
    print(f"{op[0]}  {m.get('question')[:80]}  vol={m.get('volume')}  closed={m.get('closed')}  end={m.get('endDate')}")
