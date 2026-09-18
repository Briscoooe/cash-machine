import json, urllib.request

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
    return json.load(urllib.request.urlopen(req, timeout=30))

events = []
for off in range(0, 3):
    url = f"https://gamma-api.polymarket.com/events?closed=false&limit=50&offset={off*50}&order=volume24hr&ascending=false"
    events += get(url)
print(len(events))

SKIP = ['bitcoin','btc','ethereum','eth','crypto','solana','xrp','2028','2029','2030','nfl','nba','mlb','nhl','soccer','premier league','fifa','champions league','ufc','tennis','golf','s&p','sp500','fed rate','gdp','jobs report','inflation','cpi','oscar','grammy','stock','close above','price of','coin','token','formal',]
cands = []
for ev in events:
    if ev.get('sportsMarketType'): continue
    for m in ev.get('markets', []):
        try:
            op = json.loads(m.get('outcomePrices') or '[]')
        except Exception: continue
        if len(op) < 2: continue
        try: yes = float(op[0])
        except Exception: continue
        if not (0.03 <= yes <= 0.97): continue
        q = (ev.get('title') or '') + ' | ' + (m.get('question') or '')
        low = q.lower()
        if any(s in low for s in SKIP): continue
        end = m.get('endDate') or ev.get('endDate') or ''
        cands.append({'title': ev.get('title'), 'q': m.get('question'), 'yes': yes,
                      'slug': ev.get('slug'), 'end': end,
                      'vol': m.get('volumeNum') or 0, 'desc': (m.get('description') or '')[:600]})
cands.sort(key=lambda x: -(x['vol'] or 0))
print('candidates:', len(cands))
for c in cands[:30]:
    print(round(c['yes'],3), int(c['vol']), c['q'][:110], '|', c['end'][:10], '|', c['slug'])
