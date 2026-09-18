# 2026-09-17 scan: log two pre-council skips (no-edge) with sources
import json, os, urllib.request, datetime

DB = "eeb98259-0e2f-44a0-8683-470f3d614e3c"
ACC = os.environ["CLOUDFLARE_ACCOUNT_ID"]
TOK = os.environ["CLOUDFLARE_API_TOKEN"]

def d1(sql):
    req = urllib.request.Request(
        f"https://api.cloudflare.com/client/v4/accounts/{ACC}/d1/database/{DB}/query",
        data=json.dumps({"sql": sql, "params": None}).encode(),
        headers={"Authorization": f"Bearer {TOK}", "Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

def q(sql):
    r = d1(sql)
    if not r.get("success"):
        raise SystemExit("D1 error: %s" % json.dumps(r.get("errors")))
    return r

ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

rows = [
    dict(
        id="REJ-20260917-LULA-WIN-NOEDGE",
        thesis="BUY YES Lula wins 2026 Brazilian presidential election at 0.542 (price 0.542). Claim: post-Dark-Horse polls (BTG/Nexus 42-37 Lula, first 1st-round numeric lead) push Lula win prob above market.",
        decision="pre-council skip",
        my_est="0.55-0.58",
        proposed=0.542,
        mkt=0.542,
        reason="Fair value 0.55-0.58 vs price 0.542 sits within 5pts. Runoff still a tie (Datafolha 46-44, BTG 47-46, Meio/Ideia 46-46). No edge.",
        lesson="Runoff-tied markets price the first-round leader near 0.55; a 5pt poll lead is not enough.",
        side="YES",
        category="no-edge",
        market_url="https://polymarket.com/event/brazil-presidential-election",
        kf=json.dumps([
            {"market": "Lula first-round lead (BTG/Nexus, Sep 11-13)", "note": "42 vs 37 (+5)"},
            {"market": "Runoff polls", "note": "Datafolha 46-44; BTG 47-46; Meio/Ideia 46-46"},
            {"market": "Market price Lula YES", "note": "0.542"},
        ]),
        sources=[
            ("https://gcmais.com.br/noticias/2026/09/14/pesquisa-btg-nexus-lula-tem-42-e-flavio-bolsonaro-37-no-1-turno",
             "BTG/Nexus Sep 14: Lula 42 vs Flavio 37 in 1st round; runoff 47-46 Lula, technical tie."),
            ("https://www1.folha.uol.com.br/poder/2026/09/datafolha-lula-tem-39-e-flavio-bolsonaro-35-em-primeiro-turno.shtml",
             "Datafolha Sep 11: 1st round Lula 39 vs Flavio 35; runoff 46-44."),
        ],
    ),
    dict(
        id="REJ-20260917-MUSK-160-179-NOEDGE",
        thesis="BUY NO on Musk 160-179 tweets Sep 11-18 at 0.863. Claim: pace collapsed to 18-20/day (lines.com, Sep 12-14), 7-day total projects ~126-140, far below 160.",
        decision="pre-council skip",
        my_est="0.90-0.92 (fair YES 0.08-0.10)",
        proposed=0.863,
        mkt=0.863,
        reason="NO fair 0.90-0.92 vs price 0.863 gives a 4-6pt edge after pace-uncertainty haircut (prior week ran 28.5/day, which would yield 200+). Edge under 5pts. Skip.",
        lesson="Musk pace variance between weeks is wide enough to erase sub-5pt edges on bracket NOs.",
        side="NO",
        category="no-edge",
        market_url="https://polymarket.com/event/elon-musk-of-tweets-september-11-september-18-2026",
        kf=json.dumps([
            {"market": "Recent pace (Sep 12-14, lines.com)", "note": "18-20 posts/day"},
            {"market": "Projected 7-day total at 18-20/day", "note": "126-140 posts (need 160+)"},
            {"market": "Prior-week pace (REJ-20260914)", "note": "28.5/day -> ~200 posts"},
            {"market": "Market price 160-179 YES", "note": "0.137"},
        ]),
        sources=[
            ("https://www.lines.com/prediction-markets/politics/elon-musk-of-tweets-september-14-september-16-2026",
             "XTracker Sep 12-14 pace read at 18 posts/day; 40-64 bracket favored for adjacent window."),
            ("https://polymarket.com/event/elon-musk-of-tweets-september-14-september-16-2026/elon-musk-of-tweets-september-14-september-16-2026-215-239",
             "Polymarket market text: early-to-mid September rhythm 13-21 posts/day; 215-239 bracket priced near zero."),
        ],
    ),
]

total = 0.0
for r in rows:
    q("INSERT INTO rejected (id, ts_utc, thesis, decision, council_cost_usd, my_est_yes, proposed_price, market_price_yes, reason, lesson, side, category, market_url, key_figures) VALUES ('%s','%s',%s,'%s',0,'%s',%s,%s,%s,'%s','%s','%s','%s','%s')" % (
        r["id"], ts, sqlstr(r["thesis"]), r["decision"], r["my_est"], r["proposed"], r["mkt"],
        sqlstr(r["reason"]), r["lesson"], r["side"], r["category"], r["market_url"], sqlstr(r["kf"])))
    for url, fact in r["sources"]:
        q("INSERT INTO sources (rejected_id, url, fact) VALUES ('%s', '%s', '%s')" % (r["id"], url, sqlstr(fact)))
    total += 1

print("logged", total, "rejected rows + sources, cost $0.00")
