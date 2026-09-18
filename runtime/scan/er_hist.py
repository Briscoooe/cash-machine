import json, urllib.request

def get(url):
    req=urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
    return json.load(urllib.request.urlopen(req, timeout=30))

ev = get('https://gamma-api.polymarket.com/events?slug=which-party-will-gain-most-seats-in-russian-parliamentary-election')[0]
for m in ev['markets']:
    if m['question'].startswith('Will United Russia') or 'New People' in m['question']:
        cid = m['conditionId']
        h = get(f'https://clob.polymarket.com/prices-history?market={cid}&interval=1m&fidelity=1440')
        pts = h.get('history', [])
        n = len(pts)
        print(m['question'][:45], '| pts', n)
        for i in [0, n//3, 2*n//3, n-1]:
            if 0 <= i < n:
                print('   ', round(pts[i]['p'],3))
