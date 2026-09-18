# log rejected LA-mayor thesis + verdicts into D1 via d1.py
import sys, json, urllib.request
sys.path.insert(0, "/root/cash-machine/runtime/db")
from d1 import d1

ts = "2026-09-17T05:00:00Z"
rej_id = "R-20260917-LA-MAYOR-RAMAN"
market_url = "https://polymarket.com/event/los-angeles-mayoral-election-117"

thesis = ("LA mayor runoff Nov 3: Raman YES at 0.364. Claimed edge from May Berkeley IGS head-to-head "
          "(Raman 32 Bass 28) and primary-transfer base case ~0.42-0.47. Council REJECT (0-2): "
          "vote-share conflated with win probability; honest range collapses to Fair Stake 31-43 "
          "centered on the 36.4 price. No edge.")
kf = json.dumps([
  {"market": "Raman YES price", "note": "0.364"},
  {"market": "My estimate", "note": "0.42-0.47 before council correction"},
  {"market": "Post-council fair range", "note": "0.31-0.43 (Fair Stake transfer model)"},
  {"market": "May Berkeley IGS head-to-head", "note": "Raman 32 Bass 28, ~25% neither, pre-primary"},
  {"market": "June 2 primary certified", "note": "Bass 34.3 Raman 29.0 Pratt 25.5"},
  {"market": "Valid post-primary polls", "note": "none (Median Strategies fake)"},
  {"market": "Council verdict", "note": "REJECT 0-2 (Astra conf 9, Fable conf 7)"},
])
d1("UPDATE rejected SET thesis='%s', my_est_yes='0.45', proposed_price=0.364, market_price_yes=0.364, reason='%s', key_figures='%s' WHERE id='%s'" % (thesis.replace("'","''"), "Vote-share conflated with win probability; corrected fair value 0.31-0.43 overlaps 0.364. No edge.", kf, rej_id))

srcs = [
 ("https://data.ddhq.io/polls/2026/05/28/University-of-California-Berkeley-Institute-of-Governmental-Studies-Los-Angeles", "Berkeley IGS/LA Times May 19-24: head-to-head Raman 32 Bass 28 registered, ~25% neither"),
 ("https://www.lamag.com/news-and-politics/poll-showing-karen-bass-crushing-nithya-raman-revealed-as-fake/", "Median Strategies runoff poll (Bass+12) admitted fabricated Aug 2026; withdrawn"),
 ("https://thefairstake.com/los-angeles-mayor-2026-odds-nithya-raman-35c-value/", "Transfer model: Raman 37%, range 31-43%; no edge at 35.2c"),
 ("https://www.oddsshopper.com/articles/prediction-markets/bass-vs-raman-odds", "Primary certified Bass 34.3 Raman 29.0 Pratt 25.5; Bass favorability 32/50"),
]
for url, fact in srcs:
    d1("INSERT INTO sources (rejected_id, url, fact) VALUES ('%s','%s','%s')" % (rej_id, url, fact.replace("'", "''")))

reasons = {
 "openai/gpt-6-astra": "Estimate not reproducibly derived; removing a fabricated poll does not create edge; Fair Stake range includes prices below entry; 2001/2013/2022 LA elections were open seats, not incumbent runoff wins.",
 "anthropic/claude-fable-5.1": "Conflates vote share with win probability; base case has Raman losing the two-way share; corrected range ~31-43% centered on market 36.4%; 8-model AI panel carries no evidentiary weight.",
}
for m in ["openai/gpt-6-astra", "anthropic/claude-fable-5.1"]:
    conf = 9 if "astra" in m else 7
    gid = "gen-1789617780-vMQsU6gmiKi4bIDu5Zl6" if "astra" in m else "gen-1789617791-xKlginz9MmqVwtb95zNc"
    d1("INSERT INTO council_verdicts (rejected_id, model, verdict, confidence, generation_id, reasoning, round) VALUES ('%s','%s','REJECT',%d,'%s','%s','initial')" % (rej_id, m, conf, gid, reasons[m].replace("'", "''")))
    d1("INSERT INTO council_runs (ts_utc, trigger, model, generation_id) VALUES ('%s','scan','%s','%s')" % (ts, m, gid))

d1("UPDATE watchlist SET notes = notes || ' | refresh 2026-09-17: Lula 0.445/Flavio 0.541; still no trigger, hold watching.' WHERE id='W5-BRASIL-TSE'")
print("logged OK")
