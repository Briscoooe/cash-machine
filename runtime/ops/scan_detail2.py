import json, urllib.request

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
    return json.load(urllib.request.urlopen(req, timeout=30))

queries = ["Merz out as Chancellor", "Lula da Silva win the 2026 Brazilian", "Flavio Bolsonaro win the 2026"]
for q in queries:
    d = get("https://gamma-api.polymarket.com/events?slug=" + urllib.request.quote(q))
    # use public search instead
    try:
        s = get("https://gamma-api.polymarket.com/public-search?q=" + urllib.request.quote(q) + "&limit_per_type=5")
        events = s.get('events', [])
    except Exception as ex:
        print(q, "search ERR", ex); continue
    for e in events[:3]:
        print("== ", e.get('title'), e.get('slug'))
        for m in e.get('markets', []):
            try:
                prices = json.loads(m.get('outcomePrices','[]'))
            except Exception:
                continue
            print("   ", m.get('question','')[:95], "| yes", prices[0] if prices else '?', "| end", (m.get('endDate') or '')[:10], "| slug", m.get('slug'))
