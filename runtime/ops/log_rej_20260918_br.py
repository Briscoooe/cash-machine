import json, subprocess, datetime

def d1(sql):
    url = "https://api.cloudflare.com/client/v4/accounts/%s/d1/database/eeb98259-0e2f-44a0-8683-470f3d614e3c/query" % subprocess.check_output("source /root/.secrets/cloudflare.env && echo $CLOUDFLARE_ACCOUNT_ID", shell=True, executable="/bin/bash").decode().strip()
    tok = subprocess.check_output("source /root/.secrets/cloudflare.env && echo $CLOUDFLARE_API_TOKEN", shell=True, executable="/bin/bash").decode().strip()
    body = json.dumps({"sql": sql}).encode()
    req = urllib.request.Request(url, data=body, headers={"Authorization": "Bearer " + tok, "Content-Type": "application/json"})
    import urllib.request as _u
    r = json.load(_u.urlopen(req, timeout=30))
    if not r.get("success"): print("ERR", r.get("errors"))
    return r

import urllib.request

rej_id = "R-20260918-BRL-LULA1ST-NOEDGE"
ts = "2026-09-18T05:45:00Z"
thesis = "BUY NO on Lula winning the most votes in Brazil round 1 at NO 0.235. Fresh polls split: AtlasIntel Sep 11-16 Lula 44.1 vs Flavio 41.7 (+4.5 Flavio in one week); Gerp Sep 14-16 Flavio 44 vs Lula 40 valid; only older MDA (field ended Sep 13) shows Lula +10. My estimate P(Lula 1st) 0.60-0.65 vs market 0.765. Council REJECT 0-2: fair value was asserted not derived, the 2-of-3 poll picture still favors Lula, one week of Atlas momentum is not a pace, and the market reprice may reflect information outside the evidence set."

kf = [
 {"market": "market_price_no", "note": "0.235 (Lula-1st NO; Flavio-2nd YES mirror also 0.235)"},
 {"market": "my_est_yes", "note": "P(Lula 1st) 0.60-0.65 pre-council; council found this not derived"},
 {"market": "atlasintel_sep11_16", "note": "Lula 44.1 Flavio 41.7 totals; Flavio +4.5 in one week; runoff 47.2-46.8 Flavio"},
 {"market": "gerp_sep14_16", "note": "valid votes Flavio 44 Lula 40; runoff Flavio 50-43"},
 {"market": "mda_cnt_sep9_13", "note": "Lula 40.6 Flavio 30.4; outlier, oldest field"},
 {"market": "council", "note": "Astra REJECT conf 10; Fable REJECT conf 7; unanimity vs"},
]

esc = lambda s: s.replace("'", "''")
d1("INSERT INTO rejected (id, ts_utc, market, category, thesis, key_figures, market_url) VALUES ('%s','%s','%s','no-edge','%s','%s','%s')" % (
  rej_id, ts, "Will Lula win the most votes in the first round of the 2026 Brazil presidential election?", esc(thesis),
  esc(json.dumps(kf)), "https://polymarket.com/event/brazil-presidential-election-first-round-winner"))

srcs = [
 ("https://www.gazetadopovo.com.br/eleicoes/2026/pesquisa-eleitoral-2026/atlasintel-presidente-setembro-2026-2/", "AtlasIntel Sep 11-16 n=5018: Lula 44.1 Flavio 41.7 round-1; Flavio +4.5 pts in one week; runoff 47.2-46.8"),
 ("https://www.gazetadopovo.com.br/eleicoes/2026/pesquisa-eleitoral-2026/gerp-presidente-setembro-2026-2/", "Gerp Sep 14-16 n=2400: valid votes Flavio 44 Lula 40; runoff Flavio 50 Lula 43"),
 ("https://mais.opovo.com.br/jornal/politica/2026/09/16/pesquisa-mda-lula-lidera-contra-flavio-bolsonaro-no-1-e-2-turnos.html", "MDA/CNT Sep 9-13 n=2002: Lula 40.6 Flavio 30.4 round-1; the only pro-Lula outlier"),
]
for url, fact in srcs:
    d1("INSERT INTO sources (rejected_id, url, fact) VALUES ('%s','%s','%s')" % (rej_id, url, esc(fact)))

verds = [
 ("openai/gpt-6-astra", "REJECT", 10, "gen-1789665253-x05w3CtPHU9DBkpzcLI6", 0.02616, "Poll mean gap is -0.3 on totals not +2.7; sources do not establish 60-65% win probability, justify momentum extrapolation, or support dismissing MDA; claimed edge unverified."),
 ("anthropic/claude-fable-5.1", "REJECT", 7, "gen-1789665354-O0HqJHfzgcyZGHNSSFge", 0.03196, "Fair value 0.35-0.40 NO asserted not derived; two of three polls show Lula ahead or tied; one week of Atlas move is not a pace; market reprice may reflect information outside the evidence set."),
]
for model, v, conf, gid, cost, reason in verds:
    d1("INSERT INTO council_verdicts (rejected_id, model, verdict, confidence, generation_id, cost_usd, reasoning, round) VALUES ('%s','%s','%s',%d,'%s',%s,'%s','initial')" % (rej_id, model, v, conf, gid, cost, esc(reason)))
    d1("INSERT INTO council_runs (ts_utc, trigger, model, generation_id) VALUES ('%s','scan','%s','%s')" % (ts, model, gid))

d1("UPDATE watchlist SET current_price=0.235, notes='2026-09-18: NO/Flavio-2nd 0.235. Council 0-2 REJECT (fair value asserted, not derived; 2-of-3 polls still Lula). Trigger: new poll round with Flavio level or ahead in 2+ institutes, or NO below 0.20.' WHERE id='W21-BRAZIL-FLAVIO'")
print("logged")
