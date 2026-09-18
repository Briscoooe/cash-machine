import json, urllib.request

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return json.load(urllib.request.urlopen(req, timeout=30))

events = []
for offset in (0, 50, 100):
    u = ("https://gamma-api.polymarket.com/events?limit=50&offset=%d"
         "&order=volume24hr&ascending=false&closed=false" % offset)
    events += get(u)

out = []
for ev in events:
    for m in ev.get("markets", []):
        try:
            prices = json.loads(m.get("outcomePrices") or "[]")
            if not prices:
                continue
            yes = float(prices[0])
        except Exception:
            continue
        if not (0.03 <= yes <= 0.97):
            continue
        title = m.get("question") or ev.get("title", "")
        low = title.lower()
        bad = ["sport", "nba", "nfl", "mlb", "nhl", "soccer", "premier league",
               "champions league", "la liga", "tennis", "ufc", "boxing", "f1",
               "formula", "golf", "cricket", "esports", "bitcoin", "btc", "eth",
               "ethereum", "crypto", "solana", "xrp", "doge", "2028", "2029",
               "2030", "super bowl", "world cup", "oscar", "grammy", "emmy",
               "spider-man", "box office", "s&p", "nasdaq", "fed funds", "sp500"]
        if any(b in low for b in bad):
            continue
        end = m.get("endDate") or ""
        if end and end[:4] < "2026":
            continue
        out.append({
            "q": title,
            "yes": yes,
            "vol24": m.get("volume24hr") or ev.get("volume24hr"),
            "vol": m.get("volumeNum") or m.get("volume"),
            "end": end,
            "slug": ev.get("slug", ""),
            "cond": m.get("conditionId", ""),
        })

out.sort(key=lambda x: -(x["vol24"] or 0))
with open("/root/polymarket/scan_20260916.json", "w") as f:
    json.dump(out, f, indent=1)
print(len(events), "events;", len(out), "candidate markets")
for c in out[:40]:
    print(round(c["yes"], 3), "|", (c["vol24"] or 0), "|", c["end"][:10], "|", c["q"][:110])
