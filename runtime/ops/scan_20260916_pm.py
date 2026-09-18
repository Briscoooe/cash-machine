#!/usr/bin/env python3
"""One-shot: pull current prices for watchlist slugs + flag fresh candidates not recently rejected."""
import json, urllib.request

def gamma_events(slugs):
    out = {}
    for s in slugs:
        try:
            req = urllib.request.Request(f'https://gamma-api.polymarket.com/events?slug={s}',
                                         headers={'User-Agent': 'Mozilla/5.0'})
            evs = json.load(urllib.request.urlopen(req, timeout=30))
            for e in evs:
                for m in (e.get('markets') or []):
                    op = json.loads(m.get('outcomePrices', '[]'))
                    if op:
                        out[m.get('question', s)] = (float(op[0]), e.get('slug'), (m.get('endDate') or '')[:10])
        except Exception as ex:
            out[s] = ('ERR', str(ex)[:60], '')
    return out

slugs = ["israel-x-lebanon-diplomatic-meeting-byptptpt-20260810145737299",
         "spider-man-brand-new-day-total-domestic-gross-by-september-30",
         "bab-el-mandeb-strait-effectively-closed-by-october-31",
         "ballon-dor-winner-2026",
         "what-price-will-wti-hit-in-september-2026",
         "will-anthropic-ipo-by-november-15-2026",
         "will-flvio-bolsonaro-win-the-2026-brazilian-presidential-election",
         "cdu-win-most-seats-2026-berlin-state-election"]
for q, (p, s, end) in gamma_events(slugs).items():
    print(f"{p}  {end}  {q[:80]}")

print('=== fresh candidates not seen in recent rejects ===')
cands = json.load(open('/root/cash-machine/runtime/ops/scan_cands_latest.json'))
seen_frags = ['Lula', 'Bolsonaro', 'Spider-Man', 'Bab el-Mandeb', 'Mecklenburg', 'Chongqing',
              'Iran', 'Saudi', 'Russia', 'Sweden', 'Fed', 'Kimmel', 'Clarity', 'Berlin', 'Israel']
fresh = [c for c in cands if not any(f.lower() in c['q'].lower() for f in seen_frags)]
for c in fresh[:25]:
    print(f"{round(c['price'],3)}  {c['end']}  vol{int(c['vol'])}  {c['q'][:85]}")
