#!/usr/bin/env python3
"""Ballon d'Or market: full ladder with prices + volume24h."""
import json, urllib.request

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

evs = get("https://gamma-api.polymarket.com/events?slug=ballon-dor-winner-2026")
for ev in evs:
    print(ev.get('title'), '| vol24h:', ev.get('volume24hr'), '| end:', ev.get('endDate'))
    ms = ev.get('markets', [])
    rows = []
    for m in ms:
        try:
            p = json.loads(m.get('outcomePrices') or '[]')
        except Exception:
            p = []
        try:
            vol = float(m.get('volume24hr') or 0)
        except Exception:
            vol = 0
        if p:
            rows.append((float(p[0]), vol, m.get('question')))
    rows.sort(key=lambda r: -r[0])
    for yes, vol, q in rows[:12]:
        print(f"  {yes:.3f} vol24={vol:.0f} | {q}")
