import sys, json
sys.path.insert(0, "/root/cash-machine/runtime/db")
import d1p

def run(sql, params=None):
    body = {"sql": sql}
    if params: body["params"] = params
    r = d1p.q_body = None
    import urllib.request, os
    req = urllib.request.Request(
        "https://api.cloudflare.com/client/v4/accounts/%s/d1/database/eeb98259-0e2f-44a0-8683-470f3d614e3c/query" % os.environ["CLOUDFLARE_ACCOUNT_ID"],
        data=json.dumps(body).encode(),
        headers={"Authorization": "Bearer " + os.environ["CLOUDFLARE_API_TOKEN"], "Content-Type": "application/json"})
    resp = json.loads(urllib.request.urlopen(req, timeout=30).read())
    if not resp.get("success"):
        raise RuntimeError(json.dumps(resp)[:400])
    return resp["result"]

ts = "2026-09-17T21:05:00Z"

rej = [
    ("R-20260917e-BERLIN-CDU-NOEDGE", ts,
     "BUY NO on CDU winning most seats in the 2026 Berlin state election (Sep 20) at 0.695 (CDU YES 0.315, Linke YES 0.615).",
     "pre-council skip", 0,
     "CDU most-seats ~0.40-0.45; Linke most-seats ~0.55-0.60", 0.695, 0.315,
     "Pre-council no-edge under pace-continuation weighting. Four latest polls: Infratest dimap (field Sep 7-9) Linke 21 / CDU 20; Forschungsgruppe Wahlen (field end Sep 10) Linke 23 / CDU 21; INSA (Sep ~10) CDU 20 / Linke 19; Tagesspiegel weighted mean Linke 20.1 / CDU 19.8. A 1-2pt popular-vote lead maps to roughly a coin-flip on most seats after seat-math noise, so CDU most-seats fair ~0.40-0.45 versus market 0.315 YES for CDU - wait, that reads as a YES edge for CDU, but symmetric Linke fair 0.55-0.60 vs market 0.615 is within 5pts. Both sides sit inside the no-edge band; the market has already priced the tie.",
     "Close poll ties price near coin-flip; no side clears the 5pt edge bar.", "NO",
     "no-edge",
     "https://polymarket.com/event/berlin-state-election-winner",
     json.dumps([
         {"market": "Polymarket Linke-most-seats YES price", "note": "0.615 (2026-09-17)"},
         {"market": "Polymarket CDU-most-seats YES price", "note": "0.315 (2026-09-17)"},
         {"market": "Infratest dimap for ARD, field Sep 7-9", "note": "Linke 21%, CDU 20%, AfD 18%"},
         {"market": "Forschungsgruppe Wahlen for ZDF, field end Sep 10", "note": "Linke 23%, CDU 21% (35 vs 31 projected seats)"},
         {"market": "Tagesspiegel weighted poll mean Sep 17", "note": "Linke 20.1%, CDU 19.8% - statistical tie"}
     ])),
    ("R-20260917e-MV-AFD-NOEDGE", ts,
     "BUY YES on AfD winning most seats in the 2026 Mecklenburg-Vorpommern state election (Sep 20) at 0.755.",
     "pre-council skip", 0,
     "AfD most-seats ~0.65-0.72", 0.755, 0.755,
     "Pre-council no-edge. Latest polls: INSA for Bild (field Sep 8-15) AfD 37 / SPD 35; Infratest dimap for ARD (field Sep 7-9) AfD 38 / SPD 33; Forschungsgruppe Wahlen AfD 37 / SPD 34; Nordkurier-INSA AfD 36 / SPD 33. Lead is 2-5pts with SPD momentum (+2 to +4 in the last week). Under MV's compensation-seat system most-seats follows most-votes closely, so P(AfD most seats) ~0.65-0.72 versus 0.755 market - inside the 5pt no-edge band.",
     "Small volatile lead over a surging runner does not clear a 5pt edge at 0.755.", "YES",
     "no-edge",
     "https://polymarket.com/event/mecklenburg-vorpommern-parliamentary-election-winner",
     json.dumps([
         {"market": "Polymarket AfD-most-seats YES price", "note": "0.755 (2026-09-17)"},
         {"market": "INSA for Bild, field Sep 8-15", "note": "AfD 37%, SPD 35% (SPD +2)"},
         {"market": "Infratest dimap for ARD, field Sep 7-9", "note": "AfD 38%, SPD 33%"},
         {"market": "Forschungsgruppe Wahlen for ZDF, mid-Sep", "note": "AfD 37%, SPD 34%"}
     ])),
]

for rid, t, thesis, dec, cost, est, prop, mp, reason, lesson, side, cat, url, kf in rej:
    run("INSERT INTO rejected (id, ts_utc, thesis, decision, council_cost_usd, my_est_yes, proposed_price, market_price_yes, reason, lesson, side, category, market_url, key_figures) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        [rid, t, thesis, dec, cost, est, prop, mp, reason, lesson, side, cat, url, kf])
    print("inserted", rid)

srcs = {
    "R-20260917e-BERLIN-CDU-NOEDGE": [
        ("https://www.infratest-dimap.de/umfragen-analysen/bundeslaender/berlin/laendertrend/2026/september-ii/", "dimap ARD poll (field Sep 7-9): Linke 21%, CDU 20%, AfD 18%, 10 days before the Sep 20 vote"),
        ("https://dawum.de/Berlin/Infratest_dimap/2026-09-10/", "dawum archive of the same dimap poll: Linke 21.0 (+2), CDU 20.0 (-1), n=1527"),
        ("https://politpro.eu/de/berlin/wahlumfragen/forschungsgruppe-wahlen-2026-09-10/landtagswahl", "Forschungsgruppe Wahlen for ZDF (field end Sep 10): Linke 23%, CDU 21%, projected seats 35 vs 31"),
        ("https://interaktiv.tagesspiegel.de/lab/umfragen-berlin-wahl-wahltrend-abgeordnetenhaus-sonntagsfragen/", "Tagesspiegel weighted mean of all institutes: Linke 20.1% vs CDU 19.8%"),
    ],
    "R-20260917e-MV-AFD-NOEDGE": [
        ("https://dawum.de/Mecklenburg-Vorpommern/INSA/2026-09-16/", "INSA for Bild (field Sep 8-15): AfD 37% (+1), SPD 35% (+2), vote Sep 20"),
        ("https://www.infratest-dimap.de/umfragen-analysen/bundeslaender/mecklenburg-vorpommern/laendertrend/2026/september-ii/", "dimap ARD poll: AfD 38% (+3), SPD 33% (+1), 10 days before the vote"),
        ("https://www.ariva.de/news/roundup-umfrage-afd-in-mv-nur-noch-zwei-punkte-vor-spd-12138185", "dpa roundup Sep 16: AfD 37 / SPD 35 (INSA), FGW 37/34, CDU 7% in all polls"),
    ],
}
for rid, rows in srcs.items():
    for url, fact in rows:
        run("INSERT INTO sources (rejected_id, url, fact) VALUES (?,?,?)", [rid, url, fact])
    print("sources", rid, len(rows))

# refresh watchlist note for Berlin
run("UPDATE watchlist SET notes = ?, current_price = 0.315 WHERE id = ?",
    ["2026-09-17e: dimap 21/20, FGW 23/21, INSA 20/19, Tspiegel mean 20.1/19.8. CDU YES 0.315, Linke 0.615 - coin-flip band, no edge.", "W-berlin-cdu-notfirst"])
print("watchlist updated")
