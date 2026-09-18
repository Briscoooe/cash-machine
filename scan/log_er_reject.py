#!/usr/bin/env python3
"""Log Russia ER most-seats skip: resolution-mechanics ambiguity."""
import sys, json
sys.path.insert(0, '/root/cash-machine/runtime/db')
import d1p

thesis = ("BUY NO 'United Russia (ER) gains the most seats in the next Russian parliamentary election' @ 0.755 YES. "
          "Description literally resolves on seats GAINED 'compared to before the election'. Every poll shows ER vote share "
          "down 2-14pts vs 2021 (PolitPro trend 46.0 vs 49.8; ExtremeScan 35.6; FOM 49.3), so ER likely loses net seats and "
          "NL (+6.2 trend) or LDPR (+5.2) would win a net-gain reading. But $10.7M of volume prices ER at 0.755 and NL at 0.207, "
          "which is only consistent with a 'wins most seats' reading (ER SMD domination could still net gains). "
          "Under my own literal reading NO is a large edge; under the market's apparent reading NO is a large loss. "
          "The outcome hinges on UMA resolution interpretation, not on the facts. No stake-able edge after the sibling-price check.")
key_figures = json.dumps([
    {"market": "ER YES price", "note": "0.755"},
    {"market": "NL YES price", "note": "0.207"},
    {"market": "LDPR YES price", "note": "0.0265"},
    {"market": "PolitPro election trend 2026-09-13", "note": "ER 46.0 (-3.8 vs 2021), KPRF 15.7 (-3.2), LDPR 12.9 (+5.2), NL 11.5 (+6.2)"},
    {"market": "ExtremeScan 2026-09-10", "note": "ER 35.6 (-14.2), KPRF 23.9 (+5.0), NL 16.2 (+10.9), LDPR 11.0 (+3.4)"},
    {"market": "FOM 2026-09-06", "note": "ER 49.3 (-0.5), LDPR 14.9 (+7.3), NL 7.5 (+2.2)"},
    {"market": "2021 ER baseline", "note": "324 of 450 seats (49.8% list + SMD sweep)"},
])
r = d1p.q("INSERT INTO rejected (id, ts_utc, thesis, decision, category, my_est_yes, proposed_price, market_price_yes, reason, market_url, key_figures) "
          "VALUES ('REJ-20260916-ER-RESMECH', '2026-09-16T12:00:00Z', ?, 'skipped-pre-council', 'resolution-mechanics', NULL, 0.245, 0.755, ?, ?, ?)",
          [thesis, "Resolution hinges on reading of 'gains ... compared to before the election': net-gain text vs 'wins most seats' market pricing on $10.7M volume. Sibling prices show informed money on the wins-reading; no verifiable edge.",
           "https://polymarket.com/event/which-party-will-gain-most-seats-in-russian-parliamentary-election", key_figures])
print(r if 'HTTP_ERROR' in r else 'rejected row ok')
rid = 'REJ-20260916-ER-RESMECH'
for url, fact in [
    ("https://polymarket.com/event/which-party-will-gain-most-seats-in-russian-parliamentary-election",
     "Gamma description: resolves to 'the political party that gains the greatest number of seats ... compared to before the election'; sibling prices ER 0.755, NL 0.207, LDPR 0.0265; $10.7M event volume."),
    ("https://politpro.eu/en/russia",
     "PolitPro election trend 2026-09-13: ER 46.0 (-3.8 vs 2021), NL 11.5 (+6.2), LDPR 12.9 (+5.2); ER+LDPR alliance 64.2% of seats."),
    ("https://politpro.eu/en/russia/opinion-polls/extremescan-2026-09-10/parliamentary-election",
     "ExtremeScan 2026-09-10: ER 35.6 (-14.2), KPRF 23.9 (+5.0), NL 16.2 (+10.9), LDPR 11.0 (+3.4)."),
]:
    rr = d1p.q("INSERT INTO sources (rejected_id, url, fact) VALUES (?,?,?)", [rid, url, fact])
    print(rr if 'HTTP_ERROR' in rr else 'source ok:', url[:60])
