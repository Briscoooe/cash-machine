#!/usr/bin/env python3
import json, os, urllib.request

ACC = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
TOK = os.environ.get("CLOUDFLARE_API_TOKEN")
DB = "eeb98259-0e2f-44a0-8683-470f3d614e3c"
if not ACC or not TOK:
    for line in open("/root/.secrets/cloudflare.env"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"'))
    ACC = os.environ["CLOUDFLARE_ACCOUNT_ID"]; TOK = os.environ["CLOUDFLARE_API_TOKEN"]

def q(sql):
    body = json.dumps({"sql": sql}).encode()
    req = urllib.request.Request(
        f"https://api.cloudflare.com/client/v4/accounts/{ACC}/d1/database/{DB}/query",
        data=body, headers={"Authorization": f"Bearer {TOK}", "Content-Type": "application/json"})
    r = json.load(urllib.request.urlopen(req, timeout=30))
    ok = r.get("success")
    print(("OK  " if ok else "FAIL"), sql[:60].replace("\n", " "))
    if not ok: print("   ", r.get("errors"))
    return ok

RID = "RJ-20260918-ALASKA-PELTOLA-COUNCIL"
kf = json.dumps([
 {"market": "Polymarket Peltola YES", "note": "0.68 (2026-09-18); sibling Sullivan 0.325; history 0.645 (21d), 0.635 (14d), 0.665 (7d), 0.68 now"},
 {"market": "AARP poll (Fabrizio Ward/Impact, Sep 8-11, n=800)", "note": "initial 46-41 Peltola; RCV final 53-47 Peltola; 50+ voters favor Sullivan 54-46"},
 {"market": "Alaska Survey Research (n=1495)", "note": "RCV final Peltola 50.6 - Sullivan 49.4, statistical tie"},
 {"market": "Rasmussen (Sep 13-14)", "note": "39-39 tie first round; 13% to two other GOP names; known GOP house effect"},
 {"market": "Primary (Aug 2026)", "note": "Peltola 49.5 - Sullivan 41.4; Cook and Sabato rate general a toss-up"},
 {"market": "Council", "note": "Astra REJECT conf 9, cost 0.0331; Fable REJECT conf 7, cost lookup 404; 0-2"},
], ensure_ascii=False)

thesis = ("BUY YES on Mary Peltola winning the Alaska Senate race (RCV winner, Nov 3 2026) at 0.68. "
          "AARP (Sep 8-11) shows Peltola 53-47 after RCV; ASR shows 50.6-49.4; Rasmussen tie. "
          "Claimed P(Peltola) 0.73-0.76 vs market 0.68.")
reason = ("Council 0-2 REJECT. Astra (conf 9): decomposition self-inconsistent (0.725 vs claimed 0.74-0.76); "
          "true edge ~4.5pts below the 5pt bar; Rasmussen first-round tie does not establish a Peltola RCV advantage; "
          "primary and Cook/Sabato claims unlinked. Fable (conf 7): poll aggregate implies 0.55-0.62 not 0.73+; "
          "a poll tie maps to ~0.50 not 0.72; three-GOP-ballot RCV reallocation consolidates toward Sullivan; "
          "2024 precedent shows Peltola can win a primary by ~8 and lose the RCV general; price drift claim is speculation.")

q(f"INSERT INTO rejected (id, ts_utc, thesis, decision, council_cost_usd, my_est_yes, proposed_price, market_price_yes, reason, side, category, market_url, key_figures) VALUES ('{RID}','2026-09-18T11:55:00Z','{thesis.replace(chr(39),chr(39)*2)}','rejected',0.0331,'0.725',0.68,0.68,'{reason.replace(chr(39),chr(39)*2)}','YES','no-edge','https://polymarket.com/event/alaska-senate-election-winner','{kf.replace(chr(39),chr(39)*2)}')")

sources = [
 ("https://www.aarp.org/government-elections/alaska-election-poll-2026/", "AARP poll Sep 8-11: Peltola 46 - Sullivan 41 initial; Peltola 53-47 after RCV reallocation."),
 ("https://www.juneauindependent.com/post/peltola-won-primary-by-8-but-new-poll-shows-general-election-race-tied-with-sen-sullivan", "Alaska Survey Research: RCV final round Peltola 50.6 - Sullivan 49.4, statistical tie."),
 ("https://www.rasmussenreports.com/public_content/politics/public_surveys/crosstabs_alaska_senate_september_13_14_2026", "Rasmussen Sep 13-14: Sullivan 39, Peltola 39, other GOP 13 combined."),
]
for url, fact in sources:
    q(f"INSERT INTO sources (rejected_id, url, fact) VALUES ('{RID}','{url}','{fact.replace(chr(39),chr(39)*2)}')")

verdicts = [
 ("openai/gpt-6-astra", "REJECT", 9, 0.0331, "Decomposition self-inconsistent (0.725 vs claimed 0.74-0.76); real edge ~4.5pts below 5pt bar; Rasmussen first-round tie does not establish Peltola RCV advantage; primary/Cook-Sabato claims unlinked; price history does not establish informed drift."),
 ("anthropic/claude-fable-5.1", "REJECT", 7, 0.0, "Poll aggregate implies 0.55-0.62, below market 0.68; poll tie maps to ~0.50 not 0.72; three-GOP RCV reallocation consolidates toward Sullivan; 2024 precedent shows primary win can precede RCV general loss; drift claim speculative; market already prices AARP upside."),
]
for model, verdict, conf, cost, why in verdicts:
    q(f"INSERT INTO council_verdicts (rejected_id, model, verdict, confidence, cost_usd, reasoning) VALUES ('{RID}','{model}','{verdict}',{conf},{cost},'{why.replace(chr(39),chr(39)*2)}')")

q("UPDATE watchlist SET current_price=0.68, status='rejected-no-edge' WHERE id='W25-ALASKA-SEN'")
print("done")
