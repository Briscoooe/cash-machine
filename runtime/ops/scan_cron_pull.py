#!/usr/bin/env python3
"""Cron scan: pull 150 events, filter, list candidates + D1 state snapshot."""
import json, urllib.request, re

def gamma(page):
    url = f'https://gamma-api.polymarket.com/events?limit=50&offset={page*50}&order=volume24hr&ascending=false&closed=false'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) Chrome/120'})
    return json.load(urllib.request.urlopen(req, timeout=60))

events = []
for p in range(3):
    events += gamma(p)

skip = re.compile(r'sport|nba|nfl|mlb|nhl|soccer|football|premier|ufc|tennis|f1|cricket|crypto|bitcoin|ethereum|solana|xrp|2028|2027|epl|champions|world cup|hollywood|oscar|grammy|grammys|oscars', re.I)
cands, seen = [], set()
for e in events:
    for m in (e.get('markets') or []):
        if m.get('closed'): continue
        try:
            op = json.loads(m.get('outcomePrices', '[]'))
        except Exception:
            continue
        if not op: continue
        price = float(op[0])
        q = m.get('question', '')
        if not (0.03 <= price <= 0.97): continue
        if skip.search(q): continue
        end = (m.get('endDate') or e.get('endDate') or '')[:10]
        if end[:4] in ('2027', '2028'): continue
        if q in seen: continue
        seen.add(q)
        cands.append({'q': q, 'price': price, 'end': end,
                      'slug': e.get('slug'), 'vol': float(m.get('volumeNum') or e.get('volume24hr') or 0),
                      'desc': (m.get('description') or '')[:400]})

cands.sort(key=lambda x: -(x['vol'] or 0))
json.dump(cands, open('/root/cash-machine/runtime/ops/scan_cands_latest.json', 'w'))
print(len(cands), 'candidates')
for c in cands[:30]:
    print(round(c['price'], 3), int(c['vol']), c['end'], c['q'][:95])
