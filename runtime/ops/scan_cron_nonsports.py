#!/usr/bin/env python3
"""Cron scan: list non-sports, non-esports candidates in the 5-95% band."""
import json, re

cands = json.load(open('/root/cash-machine/runtime/ops/scan_cands_latest.json'))
non_sports = re.compile(r'sweden|brewers|phillies|cubs|braves|dodgers|rays|yankees|tennis|sao paulo|counter-strike|tennis|game spread|map \d|baron|dragon|inhibitor|kill|world series|fc |atlético|soccer|esports|league of legends|shenyang|nashor|cs2', re.I)
out = []
seen = set()
for c in cands:
    if non_sports.search(c['q']):
        continue
    if c['q'] in seen:
        continue
    seen.add(c['q'])
    out.append(c)
print(len(out), 'non-sports candidates')
for c in out[:40]:
    print(round(c['price'], 3), int(c['vol']), c['end'], c['q'][:105])
    if c['desc']:
        print('    ', c['desc'][:150].replace('\n', ' '))
