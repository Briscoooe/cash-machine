import json, urllib.request, urllib.parse, os, sys

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
    return json.load(urllib.request.urlopen(req, timeout=30))

events=[]
for page in range(3):
    u=f"https://gamma-api.polymarket.com/events?limit=50&offset={page*50}&order=volume24hr&ascending=false&closed=false"
    events+=get(u)

SKIP=('nfl-','nba-','mlb-','nhl-','epl-','ucl-','la-liga','serie-a','bundesliga','ligue-','ufc-','f1-','atp-','wta-','soccer','football','hockey','baseball','basketball','tennis','golf','boxing','crypto','bitcoin','bitcoin-','ethereum','solana','xrp','doge','2028','2029','2030','presidential-election-2028','spacex','starship')
cands=[]
for ev in events:
    slug=ev.get('slug','')
    title=ev.get('title','')
    if any(s in slug.lower() or s in title.lower() for s in SKIP): continue
    for m in ev.get('markets',[]):
        try:
            prices=json.loads(m.get('outcomePrices','[]'))
            p=float(prices[0])
        except Exception: continue
        if not (0.03<=p<=0.97): continue
        cands.append({'slug':slug,'title':title,'q':m.get('question',''),'p':p,'vol':m.get('volumeNum') or m.get('volume'),'end':m.get('endDate','')})
        break  # one market per event is enough for candidate scan
print(len(events),'events,',len(cands),'candidates')
for c in sorted(cands,key=lambda x:-(float(x['vol'] or 0)))[:40]:
    print(round(c['p'],3), c['title'],'|',c['q'][:110],'| vol',c['vol'])
