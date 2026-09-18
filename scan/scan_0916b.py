#!/usr/bin/env python3
"""One-off scan: D1 dedupe state + gamma candidates, better filters."""
import json, urllib.request, os, re

ACC = TOK = None
for line in open('/root/.secrets/cloudflare.env'):
    line = line.strip()
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        os.environ.setdefault(k, v)
ACC = os.environ['CLOUDFLARE_ACCOUNT_ID']
TOK = os.environ['CLOUDFLARE_API_TOKEN']
DB = 'eeb98259-0e2f-44a0-8683-470f3d614e3c'

def d1(sql):
    body = json.dumps({"sql": sql}).encode()
    req = urllib.request.Request(
        f"https://api.cloudflare.com/client/v4/accounts/{ACC}/d1/database/{DB}/query",
        data=body, headers={'Authorization': f'Bearer {TOK}', 'Content-Type': 'application/json'})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())['result'][0]['results']

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

state = {}
for t in ['rejected', 'watchlist', 'trade_intents']:
    try:
        state[t] = d1(f"SELECT question, id, status, category FROM {t} ORDER BY rowid DESC LIMIT 200")
    except Exception as e:
        state[t] = []
        print(t, 'ERR', repr(e)[:120])
print("STATE rejected/watchlist/intents:", len(state['rejected']), len(state['watchlist']), len(state['trade_intents']))
for r in state['trade_intents'][:10]:
    print("INTENT:", r['id'], r['status'], r['question'][:70])

seen_q = set()
for t in state.values():
    for r in t:
        seen_q.add((r.get('question') or '')[:70].lower())

SPORT = re.compile(r'nba|nfl|mlb|nhl|nhl|soccer|football|premier league|tennis|ufc|f1|formula|match|spread|innings|o/u|fifa|la liga|serie a|bundesliga|cricket|golf|pga|boxing|esports|dota|cs2|counter.strike|game \d|roshan|rampage|ultra kill|wimbledon|open:|vs\.?', re.I)
CRYPTO = re.compile(r'bitcoin|btc|ethereum|eth|crypto|solana|xrp|doge|token|coin', re.I)

events = []
for off in range(3):
    url = (f"https://gamma-api.polymarket.com/events?limit=50&offset={off*50}"
           f"&order=volume24hr&ascending=false&closed=false&active=true")
    try:
        events += get(url)
    except Exception as e:
        print('gamma err', off, repr(e)[:80])

cands = []
for ev in events:
    for m in ev.get('markets', []):
        try:
            prices = json.loads(m.get('outcomePrices') or '[]')
        except Exception:
            continue
        if len(prices) < 2:
            continue
        try:
            yes = float(prices[0])
        except Exception:
            continue
        if not (0.03 <= yes <= 0.97):
            continue
        q = m.get('question') or ev.get('title') or ''
        if q[:70].lower() in seen_q:
            continue
        blob = (q + ' ' + (ev.get('title') or '') + ' ' + (ev.get('category') or ''))
        if SPORT.search(blob) or CRYPTO.search(blob):
            continue
        end = (m.get('endDate') or ev.get('endDate') or '')
        if end[:4] in ('2027', '2028', '2029', '2030'):
            continue
        cands.append({
            'question': q, 'yes': yes,
            'vol24': round(float(m.get('volume24hr') or ev.get('volume24hr') or 0)),
            'end': end[:10], 'slug': ev.get('slug'),
            'desc': (m.get('description') or '')[:500]})

cands.sort(key=lambda c: -c['vol24'])
print("EVENTS:", len(events), "CANDS:", len(cands))
with open('/root/cash-machine/scan/cands_0916b.json', 'w') as f:
    json.dump(cands, f, indent=1)
for c in cands[:35]:
    print(f"{c['yes']:.2f} vol24={c['vol24']} end={c['end']} | {c['question'][:90]}")
