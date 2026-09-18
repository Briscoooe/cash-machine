#!/usr/bin/env python3
"""Print the 34 non-sports mid-priced candidates not yet listed."""
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
           'house after the 2026', 'taiwan', 'win on 2026', 'balance of power', 'control the',
           'elon musk', 'tweets', 'best ai model', 'other company', 'mrbeast', 'exact margin']
seen = set()
out = []
for c in cands:
    q = (c['question'] or '').lower()
    if any(k in q for k in skip_kw):
        continue
    if 0.03 <= c['yes'] <= 0.97:
        k = q
        if k in seen:
            continue
        seen.add(k)
        out.append(c)
print('TOTAL unfiltered price:', len(out))
shown = 0
for c in out:
    q = c['question']
    print(f"{c['yes']:.2f} | vol24={int(c['vol24'] or 0)} | end={c['end']} | {q}")
    print('    ', (c['desc'] or '')[:130].replace('\n', ' '))
    shown += 1
    if shown > 120:
        break
