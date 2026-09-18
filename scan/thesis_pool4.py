#!/usr/bin/env python3
"""Liquidity-first non-sports candidates from all 150 events: relax mid-price, list any price."""
import json

cands = json.load(open('/root/cash-machine/scan/scan_candidates.json'))
# Anything with real volume, non-sports words
sports_kw = ['game', 'vs.', ' vs ', 'set ', 'match', 'spread', 'o/u', 'over/under', 'handicap',
             'moneyline', 'innings', 'slay', 'kills', 'nashor', 'dragon', 'inhibitor', 'rounds',
             'winner:', 'total goals', 'score', 'half', 'goals', 'corners', 'aces', 'win on 2026',
             'exact margin', 'team total', 'major league', 'serie a', 'ufc', 'nfl', 'nba', 'tennis',
             'baseball', 'football', 'hockey', 'soccer', 'cs2', 'counter-strike', 'league of legends',
             'valorant', 'volleyball', 'cycling', 'f1', 'formula']
skip_kw = ['fed interest', 'fed rate', 'hormuz', 'iran', 'blockade', 'bab el-mandeb', 'berlin',
           'linke', 'russia', 'duma', 'lula', 'brazil', 'bolsonaro', 'merz', 'anthropic',
           'clarity act', 'talarico', 'texas senate', 'saudi', 'pipeline', 'kvaratskhelia',
           'ballon', 'kimmel', 'emmy', 'starship', 'spacex', 'caatsa', 'turkey', 'earthquake',
           'measles', 'kane', 'netanyahu', 'eizenkot', 'andersson', 'sweden', 'wti', 'lebanon',
           'houthi', 'aden', 'venezuela', 'maduro', 'elon musk', 'tweets', 'best ai model',
           'other company', 'mrbeast', 'control the', 'balance of power', 'taiwan']
seen = set()
out = []
for c in cands:
    q = (c['question'] or '').lower()
    if any(k in q for k in skip_kw) or any(k in q for k in sports_kw):
        continue
    if (c['vol24'] or 0) < 3000:
        continue
    k = q
    if k in seen:
        continue
    seen.add(k)
    out.append(c)
print('TOTAL:', len(out))
for c in out:
    print(f"{c['yes']:.2f} | vol24={int(c['vol24'] or 0)} | end={c['end']} | {c['question']}")
