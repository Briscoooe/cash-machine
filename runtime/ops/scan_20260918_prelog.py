import sys, json, os, urllib.request
sys.path.insert(0, "/root/cash-machine/runtime/db")

META = "/root/.secrets/cashmachine_d1.json"
env = {}
for line in open("/root/.secrets/cloudflare.env"):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, _, v = line.partition("=")
        env[k] = v
uuid = json.load(open(META))["database_uuid"]
H = {"Authorization": "Bearer " + env["CLOUDFLARE_API_TOKEN"], "Content-Type": "application/json"}

def run(sql, params=None):
    body = {"sql": sql}
    if params:
        body["params"] = params
    req = urllib.request.Request(
        "https://api.cloudflare.com/client/v4/accounts/%s/d1/database/%s/query" % (env["CLOUDFLARE_ACCOUNT_ID"], uuid),
        data=json.dumps(body).encode(), headers=H)
    resp = json.loads(urllib.request.urlopen(req, timeout=30).read())
    if not resp.get("success"):
        raise RuntimeError(json.dumps(resp)[:400])
    return resp["result"]

ts = "2026-09-18T00:30:00Z"

rej = [
    ("R-20260918-WTI110-NOEDGE", ts,
     "BUY NO on WTI hitting HIGH $110 in September at NO 0.805 (YES 0.195). Spot WTI 100.28 on Sep 17 after two down days.",
     "pre-council skip", 0,
     "YES fair 0.15-0.25", 0.805, 0.195,
     "Pre-council no-edge. Spot 100.28 needs +9.7% within 9 sessions. Zero-drift touch math with 3.5% daily vol gives YES ~0.6, but the live pace is a sustained downtrend (WTI -3.2% Wed, -1.1% Thu on Saudi supply restoration hopes and the Fed hike), and the Sept low-ladder already paid (LOW $95 YES 0.825). Under pace-continuation weighting the downtrend pulls the touch probability toward the market's 0.195. Fair range straddles price; no 5pt edge.",
     "Ladder prices already embed the live drift; a zero-drift vol model overstates the counter-trend side.",
     "NO", "no-edge",
     "https://polymarket.com/event/what-price-will-wti-hit-in-september-2026",
     json.dumps([
         {"market": "Polymarket WTI HIGH $110 YES price", "note": "0.195 (2026-09-17)"},
         {"market": "Polymarket WTI LOW $95 YES price (sibling)", "note": "0.825 (2026-09-17)"},
         {"market": "WTI spot, WSJ Sep 17", "note": "100.28 USD/bbl, -1.1% Thursday after -3.2% Wednesday"},
         {"market": "Sessions remaining", "note": "about 9 trading sessions to Sep 30"}
     ])),
    ("R-20260918-IRANOMAN-SEP30-MAK", ts,
     "BUY YES on Iran-Oman Hormuz Agreement by September 30 at 0.095. Claim: deal finalized per TASS Sep 16, announcement 'soon' per Mehr Sep 13.",
     "pre-council skip", 0,
     "YES fair 0.10-0.20", 0.095, 0.095,
     "Pre-council skip: market-already-knows. The TASS Sep 16 headline (Araghchi: agreement with Oman reached) and the Mehr Sep 13 'announcement soon' report are both public, and the market did not move off 0.095-0.145. The resolution needs an official announced diplomatic instrument; the Salalah Gulf-FM meeting was postponed indefinitely on Sep 13 after Saudi objections, with no new date. Informed money holds the price low despite the headline; the market reads the final joint announcement as blocked on Saudi consensus.",
     "A public headline that fails to move the price means the market already priced the fact and its qualification risk.",
     "YES", "market-already-knows",
     "https://polymarket.com/event/iran-oman-hormuz-management-agreement-byptptpt-20260804222725871",
     json.dumps([
         {"market": "Polymarket Iran-Oman agreement by Sep 30 YES", "note": "0.095 (2026-09-17)"},
         {"market": "Polymarket Iran-Oman agreement by Oct 31 YES (sibling)", "note": "0.34 (2026-09-17)"},
         {"market": "Salalah meeting status", "note": "postponed indefinitely Sep 13, no new date"}
     ])),
]

for rid, t, thesis, dec, cost, est, prop, mp, reason, lesson, side, cat, url, kf in rej:
    run("INSERT INTO rejected (id, ts_utc, thesis, decision, council_cost_usd, my_est_yes, proposed_price, market_price_yes, reason, lesson, side, category, market_url, key_figures) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        [rid, t, thesis, dec, cost, est, prop, mp, reason, lesson, side, cat, url, kf])
    print("inserted", rid)

srcs = {
    "R-20260918-WTI110-NOEDGE": [
        ("https://www.wsj.com/business/energy-oil/oil-prices-slip-after-feds-first-rate-hike-in-three-years-4efe3854", "WSJ Sep 17: WTI fell 1.1% to 100.28 after -3.2% Wednesday; Saudi supply restoration hopes"),
        ("https://finance.yahoo.com/", "Yahoo Finance Sep 17: Crude Oil Oct 26 (CL=F) 102.45, -3.19%"),
        ("https://gamma-api.polymarket.com/events?slug=what-price-will-wti-hit-in-september-2026", "Gamma API ladder: HIGH $110 YES 0.195, LOW $95 YES 0.825, HIGH $115 YES 0.10"),
    ],
    "R-20260918-IRANOMAN-SEP30-MAK": [
        ("https://tass.com/world/2188349", "TASS Sep 16: Araghchi says Iran and Oman agreed a plan to reopen Hormuz; MoU with US still in force"),
        ("https://www.aljazeera.com/news-analysis/2026/9/14/temporary-hormuz-solution-deferred-as-iran-arab-summit-falls-through", "Al Jazeera Sep 14: Salalah meeting postponed, Saudi objection; deal does not reopen the strait"),
        ("https://en.mehrnews.com/news/247696/New-details-on-Iran-Oman-Hormuz-agreement-released", "Mehr Sep 13: final agreement to be announced 'soon' at a Gulf FM meeting; strait stays closed pending Iran's seven US conditions"),
    ],
}
for rid, rows in srcs.items():
    for url, fact in rows:
        run("INSERT INTO sources (rejected_id, url, fact) VALUES (?,?,?)", [rid, url, fact])
    print("sources", rid, len(rows))

run("UPDATE watchlist SET notes = ?, current_price = 0.095 WHERE id = 'W15-HORM-SEP30'",
    ["2026-09-18 scan: TASS Sep 16 confirms bilateral deal, but Sep 30 rung still 0.095 and Oct 31 0.34 - market-already-knows, announcement blocked on Saudi consensus. Salalah meeting postponed with no new date."])
print("watchlist updated")
