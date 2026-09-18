#!/usr/bin/env python3
"""Show non-sports/infrastructure-ish mid-priced candidates for thesis hunting."""
import json

cands = json.load(open('/root/cash-machine/scan/scan_candidates.json'))
skip_kw = ['fed interest', 'fed rate', 'hormuz', 'iran', 'blockade', 'bab el-mandeb', 'berlin',
           'linke', 'russia', 'duma', 'lula', 'brazil', 'bolsonaro', 'merz', 'anthropic',
           'clarity act', 'talarico', 'texas senate', 'saudi', 'pipeline', 'kvaratskhelia',
           'ballon', 'kimmel', 'emmy', 'starship', 'spacex', 'caatsa', 'turkey', 'earthquake',
           'measles', 'kane', 'netanyahu', 'eizenkot', 'andersson', 'sweden', 'wti', 'lebanon',
           'houthi', 'aden', 'venezuela', 'maduro', 'game', 'set ', 'match', 'spread', 'vs.',
           ' vs ', 'o/u', 'over/under', 'handicap', 'map ', 'moneyline', 'innings', 'slay',
           'kills', 'nashor', 'dragon', 'inhibitor', 'rounds', 'winner:', 'outright', 'total goals',
           'score', 'half', 'goals', 'corners', 'cards', 'aces', 'grand slam', 'september 2026 meeting',
           'house after the 2026', 'taiwan']
seen = set()
n = 0
for c in cands:
    q = (c['question'] or '').lower()
    if any(k in q for k in skip_kw):
        continue
    if 0.06 < c['yes'] < 0.94:
        k = q
        if k in seen:
            continue
        seen.add(k)
        n += 1
        if n <= 40:
            print(f"{c['yes']:.2f} | vol24={int(c['vol24'] or 0)} | end={c['end']} | {c['question']}")
            print('    ', (c['desc'] or '')[:150].replace('\n', ' '))
print('TOTAL non-sports mid-priced:', n)
