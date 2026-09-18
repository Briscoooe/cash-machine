# 2026-09-17: log two pre-council rejections (market-already-knows)
import json, os, sys
for line in open("/root/.secrets/cloudflare.env"):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"'))

sys.path.insert(0, "/root/cash-machine/runtime/db")
from d1cli import d1

rej = [
    {
        "id": "R-20260917-DUMA-GAIN",
        "market": "Will United Russia (ER) gain the most seats in the next Russian parliamentary election?",
        "market_url": "https://polymarket.com/event/which-party-will-gain-most-seats-in-russian-parliamentary-election",
        "side": "NO (ER yes at 0.735)",
        "category": "market-already-knows",
        "key_figures": json.dumps([
            {"market": "ER gain-most-seats YES price", "note": "0.735"},
            {"market": "Sibling: ER win-most-seats YES price", "note": "0.99"},
            {"market": "Sibling: ER seats 325-339 + 340-354", "note": "0.35 + 0.22 = 0.57"},
            {"market": "Outgoing ER seats (2021 result)", "note": "324 of 450"},
            {"market": "Implied P(ER seats >= ~325)", "note": "0.63-0.70, within 5pts of 0.735"},
            {"market": "PolitPro trend projection (list-only)", "note": "ER 235 seats -100 vs outgoing"},
        ]),
        "my_est_yes": 0.70,
        "thesis": "Literal rules read (net seats gained vs outgoing 324) made ER YES at 0.735 look like a short. But the sibling seats market prices ER at 325+ seats with 0.57, matching the outgoing count. The market already prices the SMD-sweep thesis. Estimated fair value within 5pts of price. No edge.",
        "sources": [
            {"url": "https://gamma-api.polymarket.com/events?slug=which-party-will-gain-most-seats-in-russian-parliamentary-election", "fact": "Market resolves on seats gained compared to before the election; ER YES 0.705-0.735."},
            {"url": "https://polymarket.com/event/how-many-seats-will-united-russia-win-in-the-next-russian-legislative-election", "fact": "Sibling market: ER 325-339 seats at 35%, 340-354 at 22%."},
            {"url": "https://politpro.eu/en/russia/election/parliament/2026", "fact": "PolitPro trend: ER 47.5% list vote, 235 projected list seats; election Sep 18-20, 2026."},
        ],
    },
    {
        "id": "R-20260917-XI-SEP23",
        "market": "Will Xi Jinping visit US by September 23?",
        "market_url": "https://polymarket.com/event/will-xi-jinping-visit-us-by-september-23",
        "side": "NO (yes at 0.765)",
        "category": "market-already-knows",
        "key_figures": json.dumps([
            {"market": "Xi by Sept 23 YES price", "note": "0.765"},
            {"market": "Sibling: Xi by Sept 24 YES price", "note": "0.865"},
            {"market": "Sibling: Xi by Sept 30 YES price", "note": "0.926"},
            {"market": "Scheduled state visit date (White House)", "note": "September 24, 2026"},
            {"market": "My estimate P(arrival by Sept 23 11:59pm ET)", "note": "0.70-0.80, within 5pts of 0.765"},
        ]),
        "my_est_yes": 0.75,
        "thesis": "Visit scheduled Sept 24, so NO at 0.235 looked cheap. But the by-Sept-24 sibling at 0.865 already prices the schedule, and the 23rd price reflects the real chance of a day-before evening landing (standard state-visit protocol). Neutral estimate lands within 5pts of price. No edge.",
        "sources": [
            {"url": "https://gamma-api.polymarket.com/events?slug=will-xi-jinping-visit-us-before-2027", "fact": "Ladder prices: by Sept 23 0.765, by Sept 24 0.865, by Sept 30 0.926."},
            {"url": "https://en.wikipedia.org/wiki/2026_state_visit_by_Xi_Jinping_to_the_United_States", "fact": "State visit scheduled September 24, 2026, Washington D.C.; announced by Trump July 23."},
            {"url": "https://www.aa.com.tr/en/americas/trump-says-he-will-discuss-almost-everything-with-xi-at-white-house-meeting-defends-tariffs/4056260", "fact": "Trump confirms meeting set for Sept 24 at the White House."},
        ],
    },
]

for r in rej:
    sql = ("INSERT INTO rejected (id, ts_utc, thesis, decision, my_est_yes, proposed_price, market_price_yes, reason, side, category, market_url, key_figures) "
           "VALUES ('%s', datetime('now'), '%s', 'rejected', '%s', NULL, NULL, '%s', '%s', '%s', '%s', '%s')"
           % (r["id"], r["thesis"].replace("'", "''"), str(r["my_est_yes"]), r["market"].replace("'", "''"),
              r["side"].replace("'", "''"), r["category"], r["market_url"], r["key_figures"].replace("'", "''")))
    out = d1(sql)
    assert out.get("success"), out
    for s in r["sources"]:
        ssql = ("INSERT INTO sources (rejected_id, url, fact) VALUES ('%s', '%s', '%s')"
                % (r["id"], s["url"].replace("'", "''"), s["fact"].replace("'", "''")))
        o2 = d1(ssql)
        assert o2.get("success"), o2
    print("logged", r["id"])
