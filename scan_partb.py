import json, urllib.request

def gamma(page):
    url = f"https://gamma-api.polymarket.com/events?limit=50&offset={page*50}&order=volume24hr&ascending=false&closed=false"
    req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

events = []
for p in range(3):
    events += gamma(p)
print("events:", len(events))
out = []
for e in events:
    for m in e.get("markets", []):
        try:
            prices = json.loads(m.get("outcomePrices") or "[]")
            yes = float(prices[0]) if prices else None
        except Exception:
            yes = None
        if yes is None or not (0.03 <= yes <= 0.97):
            continue
        q = m.get("question","")
        ql = q.lower()
        # filter sports/crypto/2028/long-dated
        bad = ["nba","nfl","mlb","nhl","soccer","premier league","champions league","fifa","tennis",
               "ufc","boxing","f1","formula","golf","cricket","rugby","match","game","beat the",
               "bitcoin","btc","eth","ethereum","solana","crypto","coin","2028","2029","2030","2031",
               "before 2027","in 2027","by 2027","2027"]  # keep an eye; 2027 maybe ok? exclude per long-dated rule
        if any(b in ql for b in bad):
            continue
        end = m.get("endDate") or e.get("endDate") or ""
        out.append({"q": q, "yes": round(yes,3), "end": end[:10], "slug": e.get("slug",""), "vol": m.get("volumeNum") or e.get("volume24hr"), "eid": e.get("id")})
print("candidates:", len(out))
with open("/root/cash-machine/scan_events.json","w") as f:
    json.dump(out, f)
for o in out[:80]:
    print(o["yes"], o["end"], o["q"][:100])
