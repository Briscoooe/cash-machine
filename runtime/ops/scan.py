#!/usr/bin/env python3
import json, urllib.request, os

env = {}
for line in open('/root/.secrets/cloudflare.env'):
    line = line.strip()
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        env[k] = v.strip().strip('"')

def d1(sql):
    req = urllib.request.Request(
        f"https://api.cloudflare.com/client/v4/accounts/{env['CLOUDFLARE_ACCOUNT_ID']}/d1/database/eeb98259-0e2f-44a0-8683-470f3d614e3c/query",
        data=json.dumps({"sql": sql}).encode(),
        headers={"Authorization": f"Bearer {env['CLOUDFLARE_API_TOKEN']}", "Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req))

def gamma(params):
    url = "https://gamma-api.polymarket.com/events?" + "&".join(f"{k}={v}" for k, v in params.items())
    req = urllib.request.Request(url, headers={"User-Agent": "scan/1.0"})
    return json.load(urllib.request.urlopen(req))

def jp(s):
    try: return json.loads(s)
    except Exception: return s

def price_of(m):
    p = jp(m.get('outcomePrices'))
    try: return float(p[0])
    except Exception: return None

# collect candidate markets across 3 pages, 50 each, volume sorted
events = []
for off in (0, 50, 100):
    events += gamma({"limit": 50, "offset": off, "order": "volume24hr", "ascending": "false",
                     "closed": "false", "active": "true"})

seen, cands = set(), []
SKIP = ('nba', 'nfl', 'nhl', 'mlb', 'soccer', 'epl', 'ufc', 'premier', 'champions', 'fifa',
        'bitcoin', 'btc', 'eth', 'crypto', 'satoshi', 'solana', 'xrp', '2028', '2029', '2030')
for ev in events:
    for m in ev.get('markets', []):
        q = m.get('question', '')
        slug = m.get('slug', '')
        if slug in seen: continue
        seen.add(slug)
        p = price_of(m)
        if p is None or not (0.03 <= p <= 0.97): continue
        if m.get('endDate') and m['endDate'] > '2027-01-01': continue
        low = (q + ' ' + ev.get('title', '')).lower()
        if any(k in low for k in SKIP): continue
        vol = float(m.get('volume24hr') or 0)
        cands.append({"q": q, "p": p, "slug": slug, "vol24": round(vol), "end": m.get('endDate', ''), "ev": ev.get('title', '')})

cands.sort(key=lambda c: -c['vol24'])
print(f"events={len(events)} markets={len(seen)} candidates={len(cands)}")
for c in cands[:40]:
    print(json.dumps(c))

# also fetch market descriptions for the top 15 for candidate vetting
descs = {}
for c in cands[:15]:
    try:
        r = gamma({"slug": c['slug']})
        if r:
            ms = r[0].get('markets', [])
            descs[c['slug']] = jp(ms[0].get('description', ''))[:600] if ms else ''
    except Exception as e:
        descs[c['slug']] = f"ERR {e}"
json.dump({"cands": cands[:40], "descs": descs}, open('/root/cash-machine/runtime/ops/scan_cands.json', 'w'), indent=1)
print("saved scan_cands.json")
