import json, urllib.request, os, sys
sys.path.insert(0, '/root/cash-machine/runtime/db')
for line in open('/root/.secrets/cloudflare.env'):
    line=line.strip()
    if '=' in line and not line.startswith('#'):
        k,v=line.split('=',1); os.environ[k]=v.strip().strip('"')
import importlib; d1p=importlib.import_module('d1p')

# 1. market snapshots for ER most-seats (condition ids needed) -> use slug price history? simpler: pull gamma market for ER + NL with conditionIds
def get(url):
    req=urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
    return json.load(urllib.request.urlopen(req, timeout=30))

ev = get('https://gamma-api.polymarket.com/events?slug=which-party-will-gain-most-seats-in-russian-parliamentary-election')[0]
cids = {}
for m in ev['markets']:
    if m['question'].startswith('Will United Russia') or 'New People' in m['question']:
        cids[m['question'][:25]] = m['conditionId']
        r = d1p.q("INSERT INTO market_snapshots (ts_utc, condition_id, question, yes_price, volume, end_date) VALUES (datetime('now'), '%s', '%s', %s, %s, '2026-09-30')" % (m['conditionId'], m['question'].replace("'","''"), m['outcomePrices'].strip('[]"') if False else json.loads(m['outcomePrices'])[0], m.get('volumeNum') or 0))
# price history
for label, cid in cids.items():
    try:
        h = get(f'https://clob.polymarket.com/prices-history?market={cid}&interval=1m&fidelity=1440')
        pts = h.get('history', [])
        if pts:
            print(label, '| 1m ago', round(pts[0]['p'],3), '| 2w ago', round(pts[-len(pts)//2]['p'],3) if len(pts)>2 else '-', '| now', round(pts[-1]['p'],3))
    except Exception as e:
        print(label, 'hist err', e)
print('snapshots inserted:', len(cids))
