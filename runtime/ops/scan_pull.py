import json, urllib.request, re

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
    return json.load(urllib.request.urlopen(req, timeout=30))

events = []
for off in range(3):
    d = get("https://gamma-api.polymarket.com/events?limit=50&offset=%d&order=volume24hr&ascending=false&closed=false" % (off*50))
    events.extend(d)
print("events:", len(events))

cands = []
for e in events:
    for m in e.get('markets', []):
        try:
            prices = json.loads(m.get('outcomePrices','[]'))
        except Exception:
            continue
        if not prices: continue
        try:
            yes = float(prices[0])
        except Exception:
            continue
        if not (0.03 <= yes <= 0.97):
            continue
        q = m.get('question','')
        if e.get('startDate') and e['startDate'] > '2027-01-01':
            continue
        if re.search(r'nfl|nba|mlb|nhl|ncaa|soccer|premier|la liga|bundesliga|serie a|ufc|boxing|tennis|golf|f1|cricket|bitcoin|btc|ethereum|eth price|solana|xrp|2028|2029|2030|2031|2032', q.lower()):
            continue
        cands.append((yes, q, float(m.get('volume24hr') or m.get('volume', 0) or 0), (m.get('endDate') or '')[:10], m.get('slug'), m.get('id')))
cands.sort(key=lambda c: -c[2])
for c in cands[:40]:
    print(round(c[0],3), "|", c[1][:110], "| end", c[3], "| vol", int(c[2]))
