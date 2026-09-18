import json, urllib.request, random

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    return json.load(urllib.request.urlopen(req, timeout=30))

events = []
for off in range(0, 3):
    url = f"https://gamma-api.polymarket.com/events?closed=false&limit=50&offset={off*50}&order=volume24hr&ascending=false"
    events += get(url)

SKIP = ['bitcoin','btc','ethereum','eth','crypto','solana','xrp','2028','2029','2030','nfl','nba','mlb','nhl','soccer','premier league','fifa','champions league','ufc','tennis','golf','s&p','sp500','fed rate','gdp','jobs report','inflation','cpi','oscar','grammy','stock','close above','price of','coin','token','ballon','messi','yamal','mbapp','duma','parliamentary','berlin','mecklenburg','lula','bolsonaro','invade iran','iranian regime','taiwan','bab el-mandeb','blockade','hormuz','clarity act','netanyahu','prime minister of israel','putin','xi jinping','peltola','alaska','maine','texas senate','wti','crude','spider','starship','anthropic','musk','tweet']
cands = []
for ev in events:
    if ev.get('sportsMarketType'): continue
    for m in ev.get('markets', []):
        try: op = json.loads(m.get('outcomePrices') or '[]')
        except Exception: continue
        if len(op) < 2: continue
        try: yes = float(op[0])
        except Exception: continue
        if not (0.03 <= yes <= 0.97): continue
        q = (ev.get('title') or '') + ' | ' + (m.get('question') or '')
        low = q.lower()
        if any(s in low for s in SKIP): continue
        cands.append({'q': m.get('question'), 'yes': yes, 'slug': ev.get('slug'),
                      'end': (m.get('endDate') or '')[:10], 'vol': m.get('volumeNum') or 0})
cands.sort(key=lambda x: -(x['vol'] or 0))
print('remaining candidates:', len(cands))
for c in cands[:45]:
    print(round(c['yes'],3), int(c['vol']), c['q'][:100], '|', c['end'], '|', c['slug'])
