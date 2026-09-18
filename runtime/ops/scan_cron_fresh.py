#!/usr/bin/env python3
"""Cron scan: narrow candidate list to fresh angles not already covered by rejected/watchlist."""
import json

cands = json.load(open('/root/cash-machine/runtime/ops/scan_cands_latest.json'))
covered = [
    'fed', 'interest rate', 'russia', 'united russia', 'parliament', 'brazil', 'bolsonaro',
    'lula', 'hormuz', 'bab el-mandeb', 'iranian blockade', 'iran', 'israel', 'netanyahu',
    'bennett', 'lieberman', 'eizenkot', 'berlin', 'afD', 'senate', 'house', 'midterm',
    'balance of power', 'ballon', 'saudi', 'pipeline', 'caatsa', 'merz', 'aden', 'houthis',
    'starship', 'anthropic', 'unrwa', 'taiwan', 'larusse', 'nobel', 'wti', 'crude', 'red sox',
    'spider', 'lebanon', 'chancellor', 'venezuela', 'maduro'
]
def covered_q(q):
    ql = q.lower()
    return any(k.lower() in ql for k in covered)

fresh = [c for c in cands if not covered_q(c['q'])]
print(len(fresh), 'fresh of', len(cands))
for c in fresh[:35]:
    print(round(c['price'], 3), int(c['vol']), c['end'], c['q'][:100])
    if c['desc']:
        print('    ', c['desc'][:160].replace('\n', ' '))
