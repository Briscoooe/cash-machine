#!/usr/bin/env python3
"""Part B: pull 150 volume-sorted events from gamma-api, filter, print candidates."""
import json, urllib.request

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "scan/1.0"})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

def dec(s):
    try: return json.loads(s)
    except Exception: return s

events = []
for off in (0, 50, 100):
    data = get(f"https://gamma-api.polymarket.com/events?limit=50&offset={off}&order=volume24hr&ascending=false&closed=false")
    events.extend(data)

BAD = ("nba","nfl","mlb","nhl","soccer","match","vs","football","tennis","ufc","f1","cricket","crypto","bitcoin","btc","ethereum","eth","solana","satoshi","2028","2027","game","score","playoff","draf","golf","boxing","olympic","premier","league","cup","tennis")
SKIP_Q = ("tweets", "musk")  # already handled
cands = []
for e in events:
    slug = e.get("slug","")
    q = e.get("title","") or ""
    vol = float(e.get("volume24hr") or 0)
    for m in e.get("markets", []):
        try:
            op = [float(x) for x in dec(m.get("outcomePrices","[]"))]
            if len(op) != 2: continue
            yes = op[0]
        except Exception: continue
        if not (0.03 <= yes <= 0.97): continue
        mq = m.get("question","")
        low = (mq+" "+q+" "+slug).lower()
        if any(b in low for b in BAD): continue
        end = m.get("endDate","") or ""
        if end and end[:4] not in ("2026",): continue
        cands.append({"q": mq, "yes": round(yes,4), "vol24": vol, "end": end[:10],
                      "slug": slug, "cond": m.get("conditionId","")})

# dedupe
seen=set(); out=[]
for c in cands:
    if c["q"] in seen: continue
    seen.add(c["q"]); out.append(c)
print(len(out), "candidates")
with open("/root/cash-machine/scan/cands_today.json","w") as f:
    json.dump(out, f, indent=1)
for c in out[:60]:
    print(f"{c['yes']:.3f} vol24={c['vol24']:.0f} end={c['end']} {c['q'][:110]} | {c['slug']}")
