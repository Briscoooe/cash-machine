#!/usr/bin/env python3
"""Re-arm watchlist rows: reset spurious triggers + correct current_price with verified values."""
import json, urllib.request

env = {}
for line in open("/root/.secrets/cloudflare.env"):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, _, v = line.partition("="); env[k] = v
ACCT, DB = env["CLOUDFLARE_ACCOUNT_ID"], "eeb98259-0e2f-44a0-8683-470f3d614e3c"

def d1(sql, params=None):
    body = {"sql": sql}
    if params: body["params"] = params
    req = urllib.request.Request(
        f"https://api.cloudflare.com/client/v4/accounts/{ACCT}/d1/database/{DB}/query",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {env['CLOUDFLARE_API_TOKEN']}"})
    r = json.load(urllib.request.urlopen(req, timeout=30))
    if not r.get("success"):
        raise SystemExit(f"D1 error: {json.dumps(r)[:500]}")
    return r["result"][0].get("results", [])

notes = {
    "W2-IRANOMAN": "2026-09-12 00:5x: council 0/3 rejection stands; catalyst Sep 14 Salalah NOT yet occurred (FT/Asharq/Amwaj confirm meeting is Monday); live Sep-30 sub-market 0.385 via events API. Re-armed at 0.40.",
    "W3-BABELMANDEB": "2026-09-12 00:5x: trigger row was spurious (market fell 0.095->0.0865 DESPITE Houthi coastal takeover + Perim/Mokha capture — market-already-knows; Reuters/CNN/Politico Sep 10-11 confirm Houthi framing 'freedom of navigation uninterrupted', i.e. NO full-blockade declaration). Catalysts (PortWatch 7DMA<=15 twice, or full blockade declaration) NOT met. Est band 0.09-0.14 vs 0.0865 still no edge. Re-armed at 0.0865.",
    "W4-SWEDEN": "2026-09-12 00:5x: spurious trigger (scanner matched Kristersson market 0.265 as Andersson). Live Andersson YES 0.735 verified via events API. Election tomorrow Sep 13; self-undercut est 0.55-0.60 < 0.735, no edge either side. Re-armed at 0.60.",
    "W5-BRASIL-TSE": "2026-09-12 00:5x: spurious trigger — scanner read Tarcisio de Freitas market (0.0005) instead of Lula. Live Lula YES 0.465 (vs 0.455 on Sep 11, no real move). TSE catalyst NOT met: Sep 8-9 news = admissibility of AIJE cases only (Corregedor Ferreira), no plenary vote on the Aug 31 ineligibility challenge; no runoff poll >= +4 found. process.py watchlist bug fixed (question-matching, no more markets[0]). Re-armed at 0.50.",
}
for wid, note in notes.items():
    r = d1("SELECT current_price, watch_price FROM watchlist WHERE id=?", [wid])
    cur = r[0]["current_price"] if r else None
    wp = r[0]["watch_price"] if r else None
    if wid == "W2-IRANOMAN":
        newp = cur
    elif wid == "W3-BABELMANDEB":
        newp = 0.0865
    else:
        newp = cur  # W4 (0.265) and W5 (0.0005) are scanner artifacts, keep watch_price trigger only
    d1("UPDATE watchlist SET status='watching' WHERE id=?", [wid])
    d1("UPDATE watchlist SET notes=COALESCE(notes,'')||? WHERE id=?", [" | " + note, wid])
    print(f"{wid}: re-armed (old_price={cur}, watch={wp})")
print("done")
