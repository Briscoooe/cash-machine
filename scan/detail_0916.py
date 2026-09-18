#!/usr/bin/env python3
"""Fetch full details for 5 candidate markets from gamma."""
import json, urllib.request

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

slugs = {
 'NL': 'how-many-ships-transit-bab-el-mandeb-strait-week-of-september-14',
 'MVP': 'mecklenburg-vorpommern-parliamentary-elections',
 'BERLIN': 'berlin-state-election-winner',
 'FED': 'fed-september-2026-interest-rate-decision',
 'BLK': 'us-announces-end-of-iranian-blockade-byptptpt-20260713152715080',
}
for tag, slug in slugs.items():
    try:
        evs = get(f"https://gamma-api.polymarket.com/events?slug={slug}")
        if not evs:
            print(tag, 'NO EVENT'); continue
        ev = evs[0]
        print('=====', tag, ev.get('title'), '| vol24h:', ev.get('volume24hr'), '| end:', ev.get('endDate'))
        print('DESC:', (ev.get('description') or '')[:700].replace('\n', ' '))
        for m in ev.get('markets', []):
            print('  -', (m.get('question') or '')[:95], '|', m.get('outcomePrices'), '| vol24:', m.get('volume24hr'))
    except Exception as e:
        print(tag, 'ERR', repr(e)[:100])
