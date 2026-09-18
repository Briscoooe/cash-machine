import json, urllib.request, os, datetime, re

# Part B: 150 events from gamma-api, 3 pages x 50, volume sorted
excluded_kw = ['nfl','nba','mlb','nhl','soccer','football','uefa','fifa','premier','laliga','la liga','serie',
 'champions','ucl','tennis','wta','atp','ufc','boxing','cricket','formula','f1','nascar','golf','olympics',
 'esports','cs2','dota','bitcoin','btc','ethereum','eth','solana','crypto','token','xrp','doge','stablecoin',
 '2028','2029','2030','2031','2032',' Super Bowl','world cup','spider-man','box office','oscar','grammy','emmy']

def get(url):
    req=urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

events=[]
for off in (0,50,100):
    url=("https://gamma-api.polymarket.com/events?closed=false&limit=50&offset=%d"
         "&order=volume24hr&ascending=false" % off)
    events += get(url)

def parse_price(m):
    try:
        op=json.loads(m.get('outcomePrices') or 'null')
        return float(op[0]) if op else None
    except Exception: return None

cands=[]
for ev in events:
    title=ev.get('title','')
    low=title.lower()
    if any(k in low for k in excluded_kw): continue
    if ev.get('closed'): continue
    end=ev.get('endDate') or ''
    if end and end[:4] not in ('2026',): continue
    for m in ev.get('markets',[]):
        p=parse_price(m)
        if p is None: continue
        pno=1-p
        side='YES' if 0.03<=p<=0.97 else ('NO' if 0.03<=pno<=0.97 else None)
        if not side: continue
        cands.append({
            'event': title, 'slug': ev.get('slug'),
            'question': m.get('question', title), 'side': side,
            'price': p if side=='YES' else round(pno,4),
            'vol24': ev.get('volume24hr'), 'end': end[:10],
            'outcomes': m.get('outcomes'), 'negRisk': m.get('negRisk'),
        })

cands.sort(key=lambda c: -(c['vol24'] or 0))
print("TOTAL events:", len(events), "candidates:", len(cands))
for c in cands[:40]:
    print(json.dumps(c))
json.dump(cands, open('/root/cash-machine/runtime/ops/scan_cands.json','w'))
