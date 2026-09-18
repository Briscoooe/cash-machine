import json, urllib.request, re

def get(url):
    req=urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

# Need current Musk tweet count Sept 14 12:00 ET -> Sept 16 12:00 ET window.
# Sept 15 00:05Z run noted 40-64 at 0.65 / 65-89 at 0.34. Get live count from a public counter.
# Try a simple approach: Exa search handled elsewhere. Here just re-pull price to see drift.
ev = get("https://gamma-api.polymarket.com/events?slug=elon-musk-of-tweets-september-14-september-16-2026")
for e in ev:
    for m in e.get('markets',[]):
        op=json.loads(m.get('outcomePrices') or '[]')
        if op and float(op[0])>0.05:
            print(m.get('question')[:80], op[0], m.get('clobTokenIds','')[:60])
