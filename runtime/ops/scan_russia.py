import json, urllib.request

def get(url):
    req=urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

ev = get("https://gamma-api.polymarket.com/events?slug=which-party-will-gain-most-seats-in-russian-parliamentary-election")
for e in ev:
    print("DESC:", (e.get('description') or '')[:1200])
    for m in e.get('markets',[]):
        op=json.loads(m.get('outcomePrices') or '[]')
        print(json.loads(m['outcomes'])[0] if m.get('outcomes') else '?', '|', m.get('question')[:90], '|', op)
