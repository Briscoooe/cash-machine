#!/usr/bin/env python3
"""Filter candidates against D1 history and produce shortlist."""
import json

cands = json.load(open('/root/cash-machine/scan/scan_candidates.json'))

# skip themes recently rejected or already covered (from D1 review + prior runs)
skip_kw = ['fed interest', 'fed rate', 'hormuz', 'iran-oman', 'iran oman', 'blockade', 'bab el-mandeb',
           'berlin', 'linke', 'russia', 'duma', 'lula', 'brazil', 'bolsonaro', 'merz', 'anthropic',
           'clarity act', 'hormuz', 'talarico', 'texas senate', 'saudi', 'pipeline', 'kvaratskhelia',
           'ballon', 'kimmel', 'emmy', 'starship', 'spacex', 'caatsa', 'turkey', 'earthquake',
           'measles', 'kane', 'netanyahu', 'eizenkot', 'andes', 'andersson', 'sweden', 'wti',
           'lebanon', 'mariners', 'angels', 'marlins', 'diamondbacks', 'charaeva', 'quadra kill',
           'houthi', 'aden', 'venezuela', 'maduro', 'extra innings', 'team total']
short = []
for c in cands:
    q = (c['question'] or '').lower()
    if any(k in q for k in skip_kw):
        continue
    short.append(c)

# dedupe by question, keep first (highest vol)
seen = set()
uniq = []
for c in short:
    k = (c['question'] or '').lower()
    if k in seen:
        continue
    seen.add(k)
    uniq.append(c)

print('SHORTLIST:', len(uniq))
for c in uniq[:35]:
    print(f"{c['yes']:.2f} | vol24={int(c['vol24'] or 0)} | end={c['end']} | {c['question']} | {c['desc'][:180]}")
json.dump(uniq[:35], open('/root/cash-machine/scan/shortlist.json', 'w'), indent=1)
