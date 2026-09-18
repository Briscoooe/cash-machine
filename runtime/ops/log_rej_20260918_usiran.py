import sys, os, json
sys.path.insert(0, '/root/cash-machine/runtime/db')
for line in open('/root/.secrets/cloudflare.env'):
    line=line.strip()
    if '=' in line and not line.startswith('#'):
        k,v=line.split('=',1); os.environ[k]=v.strip().strip('"')
import importlib; d1p=importlib.import_module('d1p')

rj_id = 'RJ-20260918-USIRAN-SEP30-NOEDGE'
d1p.q("INSERT INTO rejected (id, ts_utc, thesis, decision, council_cost_usd, my_est_yes, proposed_price, market_price_yes, reason, lesson, side, category, market_url, key_figures) VALUES ('%s', datetime('now'), '%s', 'skipped', 0, %s, %s, %s, '%s', '%s', 'YES', 'no-edge', 'https://polymarket.com/event/next-round-of-us-iran-peace-talks-byptptpt-20260623022722982', '%s')" % (
  rj_id,
  "BUY YES on US x Iran senior diplomatic meeting by Sept 30 at 0.095. Trump says talks possible; Gulf-leaders UNGA meeting Sep 22 as catalyst. But Iran publicly rejects talks unless conditions are met (Rezaei), Islamabad MoU collapsed, and Salalah Iran-Gulf meeting already postponed. Market price near multi-month fair value.",
  "0.14", "0.095", "0.095",
  "Siblings ladder cleanly: Oct31 0.205, Dec31 0.42, Mar31 0.625. Conditional Sep30|no-September-talks ~0.10 matches price 0.095. Catalyst (Trump-Gulf meeting Sep 22) could raise Dec31 more than Sep30. No edge found.",
  "Derived-event ladders price the conditional consistently; entering the near leg needs a concrete scheduled meeting, not open-to-talks rhetoric.",
  json.dumps([
    {"market": "US x Iran diplomatic meeting by September 30, 2026", "note": "YES 0.095 (gamma-api, fetched 2026-09-18)"},
    {"market": "US x Iran diplomatic meeting by October 31, 2026", "note": "YES 0.205"},
    {"market": "US x Iran diplomatic meeting by December 31, 2026", "note": "YES 0.42"},
    {"market": "US x Iran diplomatic meeting by March 31, 2027", "note": "YES 0.625"},
    {"market": "Rezaei (SNSC) via Al Jazeera 2026-09-17", "note": "Iran rejects talks until its conditions are met; no Tehran confirmation of direct talks"}
  ]).replace("'", "''").replace('"', '"'),
))
print('rejected row inserted')
s1 = d1p.q("INSERT INTO sources (rejected_id, url, fact) VALUES ('%s', 'https://www.aljazeera.com/news/2026/9/17/trump-claims-direct-talks-with-iran-is-diplomacy-picking-up-again', 'Iran SNSC secretary Rezaei: no talks until Iran conditions met; Islamabad MoU collapsed; no Tehran confirmation of direct talks')" % rj_id)
s2 = d1p.q("INSERT INTO sources (rejected_id, url, fact) VALUES ('%s', 'https://www.iranintl.com/en/202609177671', 'Trump weighs renewed large-scale strikes; Gulf leaders meeting next Tuesday at UNGA; Wang Yi urged both sides to resume consultations')" % rj_id)
s3 = d1p.q("INSERT INTO sources (rejected_id, url, fact) VALUES ('%s', 'https://thesoufancenter.org/intelbrief-2026-september-17/', 'Salalah Iran-Gulf meeting on Hormuz collapsed after Saudi request; Iran FM says strait stays closed until US meets demands')" % rj_id)
print('sources inserted')
b = d1p.q("INSERT INTO balance_history (date_utc, balance, unrealized_pl, total_value, open_positions) SELECT date_utc, balance, unrealized_pl, total_value, open_positions FROM balance_history WHERE date_utc = (SELECT MAX(date_utc) FROM balance_history)")
print('ok')
