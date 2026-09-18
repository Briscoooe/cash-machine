import json, urllib.request, random

def get(url):
    req=urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
    return json.load(urllib.request.urlopen(req, timeout=30))

ev = get('https://gamma-api.polymarket.com/events?slug=which-party-will-gain-most-seats-in-russian-parliamentary-election')[0]
for m in ev['markets']:
    if m['question'].startswith('Will United Russia') or 'New People' in m['question']:
        cid = m['conditionId']
        # fallback: token ids with startTs far in past
        try:
            toks = json.loads(m['clobTokenIds'])
        except Exception:
            print('no tokens'); continue
        start = int(__import__('time').time()) - 45*86400
        url = f'https://clob.polymarket.com/prices-history?market={toks[0]}&startTs={start}&fidelity=86400'
        try:
            h = get(url)
            pts = h.get('history', [])
        except Exception as e:
            pts = []; print('err', e)
        print(m['question'][:50], '| pts', len(pts))
        for p in pts[::max(1,len(pts)//10)]:
            print('   ', p['t'], round(p['p'],3))
