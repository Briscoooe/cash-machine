#!/usr/bin/env python3
"""Read D1 rejected/intents; fetch gamma top markets."""
import json, os, urllib.request

CREDS = "/root/.secrets/cloudflare.env"
DB = "eeb98259-0e2f-44a0-8683-470f3d614e3c"

def load_env(path):
    env = {}
    for line in open(path):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k.strip().strip('"\'')] = v.strip().strip('"\'')
    return env

env = load_env(CREDS)
acct, tok = env["CLOUDFLARE_ACCOUNT_ID"], env["CLOUDFLARE_API_TOKEN"]
url = f"https://api.cloudflare.com/client/v4/accounts/{acct}/d1/database/{DB}/query"

def d1q(sql):
    body = json.dumps({"sql": sql}).encode()
    req = urllib.request.Request(url, data=body, headers={
        "Authorization": f"Bearer {tok}", "Content-Type": "application/json"})
    d = json.loads(urllib.request.urlopen(req, timeout=30).read())
    return d["result"][0].get("results", [])

for r in d1q("SELECT id, thesis, category, my_est_yes, proposed_price, market_price_yes, ts_utc FROM rejected ORDER BY ts_utc DESC LIMIT 15"):
    print("REJ:", json.dumps(r, default=str)[:250])
for r in d1q("SELECT id, status, market, ts_utc FROM trade_intents ORDER BY ts_utc DESC LIMIT 8"):
    print("INT:", json.dumps(r, default=str)[:250])

# gamma top volume markets
for page in range(1, 4):
    u = f"https://gamma-api.polymarket.com/events?closed=false&order=volume24hr&ascending=false&limit=50&page={page}"
    try:
        evs = json.loads(urllib.request.urlopen(u, timeout=30).read())
    except Exception as e:
        print("GAMMA ERR", page, repr(e)[:200]); continue
    for ev in evs:
        title = ev.get("title", "")
        slug = ev.get("slug", "")
        vol = ev.get("volume24hr") or ev.get("volume", 0)
        try: vol = float(vol or 0)
        except Exception: vol = 0
        t = ev.get("endDate", "") or ""
        for m in ev.get("markets", []):
            try:
                prices = json.loads(m.get("outcomePrices", "[]"))
                yes = float(prices[0])
            except Exception:
                continue
            if m.get("closed") or m.get("archived"): continue
            if yes < 0.03 or yes > 0.97: continue
            low = title.lower()
            if any(w in low for w in ["nfl","nba","mlb","nhl","soccer","premier","ufc","fights","bitcoin","btc","ethereum","eth","crypto","solana","xrp","2028","2029","2030"]): continue
            print(f"MKT|{yes:.3f}|{vol:>10.0f}|{t[:10]}|{title[:80]}|{m.get('question','')[:100]}|{slug}")
    print("---PAGE", page)
