import json, urllib.request

env = {}
for line in open('/root/.secrets/cloudflare.env'):
    line = line.strip()
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1); env[k] = v.strip().strip('"')

DBURL = ("https://api.cloudflare.com/client/v4/accounts/" + env['CLOUDFLARE_ACCOUNT_ID']
         + "/d1/database/eeb98259-0e2f-44a0-8683-470f3d614e3c/query")

def d1(payload):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(DBURL, data=data, headers={
        "Authorization": "Bearer " + env['CLOUDFLARE_API_TOKEN'],
        "Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req))

REJ = "REJ-20260916-BRAZIL-FLAVIO-NOEDGE"

thesis = ("BUY NO Flavio Bolsonaro wins 2026 Brazilian presidential election @ 0.545 YES. "
          "Market prices Flavio as favorite; fresh poll mix shows a coin-flip race.")
reason = ("Pre-council no-edge. Four institutes polled Sep 8-13: Quaest has Flavio +2 (42-40) in runoff; "
          "Datafolha has Lula +2 (46-44); MDA has Lula +7.3 (47.3-40); Meio/Ideia tie 46-46. "
          "First round: Lula leads in all four (36-40.6 vs 30.4-35). Fair P(Flavio win) under "
          "pace-continuation weighting: P(reaches runoff) ~0.95 x P(win runoff | mixed polls) ~0.49 = ~0.47. "
          "Within 5 pts of the 0.545 market price after momentum shading. No edge either side.")
lesson = ("A tightening poll race can still hold no edge when the market already moved to the challenger; "
          "test both sides before a council.")
kf = json.dumps([
    {"market": "Quaest runoff (Sep 10-13, n=2004, MoE 2)", "note": "Flavio 42 vs Lula 40, within margin of error"},
    {"market": "Datafolha runoff (Sep 8-10, n=2002, MoE 2)", "note": "Lula 46 vs Flavio 44, technical tie"},
    {"market": "MDA runoff (Sep 9-13, n=2002, MoE 2.2)", "note": "Lula 47.3 vs Flavio 40, lead outside margin"},
    {"market": "Meio/Ideia runoff (Sep 4-7, n=1500, MoE 2.5)", "note": "46-46 tie"},
    {"market": "First round aggregate", "note": "Lula leads in all four institutes: 36-40.6 vs 30.4-35"},
    {"market": "My fair value", "note": "P(Flavio win) ~0.95 x ~0.49 = ~0.47 vs market 0.545"}])
murl = "https://polymarket.com/event/will-flvio-bolsonaro-win-the-2026-brazilian-presidential-election"

r = d1({"sql": ("INSERT INTO rejected (id, ts_utc, thesis, decision, my_est_yes, proposed_price, market_price_yes, "
                "reason, lesson, side, category, market_url, key_figures, council_verdicts) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)"),
        "params": [REJ, "2026-09-16T08:00:00Z", thesis, "rejected_pre_council", 0.47, 0.545, 0.545,
                   reason, lesson, "NO", "no-edge", murl, kf, "pre-council self-check, no council run"]})
print("rejected:", r.get('success'), r.get('errors') or '')

srcs = [
    ("https://www.estadao.com.br/politica/eleicoes/pesquisa-quaest-14-setembro-lula-luiz-inacio-lula-silva-flavio-bolsonaro/",
     "Quaest Sep 10-13: Flavio 42 vs Lula 40 in runoff, within 2pt margin; first round Lula 36, Flavio 31"),
    ("https://mais.opovo.com.br/jornal/politica/2026/09/16/pesquisa-mda-lula-lidera-contra-flavio-bolsonaro-no-1-e-2-turnos.html",
     "MDA Sep 9-13 (CNT, BR-06902/2026): Lula 47.3 vs Flavio 40 in runoff, lead outside 2.2pt margin; first round Lula 40.6, Flavio 30.4"),
    ("https://www.aa.com.tr/en/americas/lula-maintains-lead-over-flavio-bolsonaro-ahead-of-brazil-election-poll/4055445",
     "Datafolha Sep 8-10: Lula 39 vs Flavio 35 first round; runoff Lula 46 vs Flavio 44, within margin"),
    ("https://www.washingtonpost.com/world/2026/09/12/brazil-flvio-bolsonaro-enjoys-late-surge-ahead-presidential-elections/",
     "WaPo Sep 12: Flavio polls evenly with Lula; prediction markets favor the challenger for the first time in months"),
]
for url, fact in srcs:
    r = d1({"sql": "INSERT INTO sources (rejected_id, url, fact) VALUES (?,?,?)", "params": [REJ, url, fact]})
    print("source:", r.get('success'), r.get('errors') or '')

w = d1({"sql": ("INSERT INTO watchlist (id, question, slug, current_price, watch_price, direction, thesis_seed, "
                "catalyst, catalyst_date, status) VALUES (?,?,?,?,?,?,?,?,?,?)"),
        "params": ["W21-BRAZIL-FLAVIO",
                   "Will Flavio Bolsonaro win the 2026 Brazilian presidential election?",
                   "will-flvio-bolsonaro-win-the-2026-brazilian-presidential-election",
                   0.545, 0.62, "NO",
                   "Fair value ~0.47 vs 0.545 market. Edge needs >5pt drift toward Flavio on next poll round or market >0.62. Lula still leads round 1 in all four fresh institutes.",
                   "Next Quaest/Datafolha/MDA poll round or Oct 4 first round", "2026-10-04", "watching"]})
print("watchlist:", w.get('success'), w.get('errors') or '')

chk = d1({"sql": "SELECT id, category FROM rejected WHERE id='" + REJ + "'"})
print(chk['result'][0]['results'])
