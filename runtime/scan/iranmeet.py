import json, urllib.request, os, sys, time
sys.path.insert(0, '/root/cash-machine/runtime/db')
for line in open('/root/.secrets/cloudflare.env'):
    line=line.strip()
    if '=' in line and not line.startswith('#'):
        k,v=line.split('=',1); os.environ[k]=v.strip().strip('"')
import importlib; d1p=importlib.import_module('d1p')

def get(url):
    req=urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
    return json.load(urllib.request.urlopen(req, timeout=30))

slug='next-round-of-us-iran-peace-talks-byptptpt-20260623022722982'
ev = get(f'https://gamma-api.polymarket.com/events?slug={slug}')[0]
print('DESC:', (ev.get('description') or '')[:900].replace('\n',' '))
snap = []
for m in ev['markets']:
    try: yes = float(json.loads(m['outcomePrices'])[0])
    except Exception: continue
    q = m['question']
    if 'diplomatic meeting by' not in q: continue
    print(round(yes,3), q[:70], '| vol', int(m.get('volumeNum') or 0))
    snap.append((q, yes, m['conditionId']))
    d1p.q("INSERT INTO market_snapshots (ts_utc, condition_id, question, yes_price, volume, end_date) VALUES (datetime('now'), '%s', '%s', %s, %s, '%s')" % (m['conditionId'], q.replace("'","''"), yes, m.get('volumeNum') or 0, (m.get('endDate') or '')[:10]))
print('snapshots:', len(snap))
# history for Sep30 and Dec31 markets
for q, yes, cid in snap:
    if 'September 30' in q or 'December 31' in q:
        try:
            toks = json.loads([m for m in ev['markets'] if m['conditionId']==cid][0]['clobTokenIds'])
            start = int(time.time()) - 60*86400
            h = get(f'https://clob.polymarket.com/prices-history?market={toks[0]}&startTs={start}&fidelity=86400')
            pts = h.get('history', [])
            print(q[:45], [round(p['p'],3) for p in pts[::max(1,len(pts)//8)]])
        except Exception as e:
            print(q[:45], 'hist err', e)
