# 2026-09-17 evening scan: pull 150 volume-sorted events, filter, list candidates
import json, urllib.request

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "scan/1.0"})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

events = []
for offset in (0, 50, 100):
    u = "https://gamma-api.polymarket.com/events?limit=50&offset=%d&order=volume24hr&ascending=false&closed=false" % offset
    events += get(u)

BANNED = ["nfl","nba","mlb","nhl","soccer","football","basketball","tennis","ufc","fifa","premier league","champions league","la liga","bundesliga","serie a","cricket","golf","boxing","f1","formula","esports","olympic","bitcoin","btc","ethereum","eth price","solana","crypto","token","xrp","doge","s&p","nasdaq","sp500","fed rate","2028","2027","2029","2030","november 2026","december 2026","grand slam","world cup","match","vs.","beats","wins the","election 2028","ballon d'or","ballon dor","grammy","oscar","emmy"]
cands = []
for ev in events:
    title = (ev.get("title") or "")
    tl = title.lower()
    if any(b in tl for b in BANNED):
        continue
    for m in ev.get("markets", []):
        if m.get("closed") or not m.get("enableOrderBook"):
            continue
        try:
            prices = json.loads(m.get("outcomePrices") or "[]")
        except Exception:
            continue
        if len(prices) != 2:
            continue
        yes = float(prices[0])
        if not (0.03 <= yes <= 0.97):
            continue
        cands.append({
            "slug": ev.get("slug"), "title": title, "question": m.get("question") or title,
            "yes": yes, "no": 1 - yes,
            "vol24": round(float(m.get("volume24hr") or 0)),
            "volume": round(float(m.get("volumeNum") or 0)),
            "end": (m.get("endDate") or ev.get("endDate") or "")[:10],
            "condition_id": m.get("conditionId"), "desc": (m.get("description") or ev.get("description") or "")[:500],
        })

cands.sort(key=lambda c: -c["vol24"])
json.dump({"n_events": len(events), "cands": cands}, open("/root/cash-machine/runtime/ops/scan_20260917e_cands.json", "w"), indent=1)
print("events:", len(events), "candidates:", len(cands))
for c in cands[:45]:
    print("%.3f | %s | %s | v24 %d | end %s" % (c["yes"], c["question"][:85], c["slug"][:55], c["vol24"], c["end"]))
