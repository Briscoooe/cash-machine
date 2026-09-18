#!/usr/bin/env python3
"""Cron scan: widen non-sports filter to all matches, print exotic candidates 130-400."""
import json, re

cands = json.load(open('/root/cash-machine/runtime/ops/scan_cands_latest.json'))
non_sports = re.compile(r'sweden|brewers|phillies|cubs|braves|dodgers|rays|yankees|tennis|sao paulo|counter-strike|game spread|map \d|baron|dragon|inhibitor|kill|world series|fc |atlético|soccer|esports|league of legends|shenyang|nashor|cs2|fed|interest rate|rate cut|rate hike|russia|united russia|parliament|brazil|bolsonaro|lula|hormuz|bab el-mandeb|iran|israel|netanyahu|bennett|lieberman|eizenkot|berlin|afd|senate|house|midterm|balance of power|ballon|saudi|pipeline|caatsa|merz|aden|houthis|starship|anthropic|unrwa|taiwan|nobel|wti|crude|red sox|spider|lebanon|chancellor|venezuela|maduro|ceasefire|blockade|diplomatic|roshan|barracks|rampage|daytime|company [a-k]|other company|fide|chess|mrbeast|spread|moneyline|o/u|total rounds|handicap|2h|1h|tweets|musk|visit us|ethiopia|abiy|ai model|arena', re.I)
out, seen = [], set()
for c in cands:
    q = c['q']
    if non_sports.search(q) or q in seen:
        continue
    seen.add(q)
    out.append(c)
print(len(out), 'candidates after broad filter')
for c in out[:80]:
    print(round(c['price'], 3), int(c['vol']), c['end'], c['q'][:110])
