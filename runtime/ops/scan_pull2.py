import json, urllib.request

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
    return json.load(urllib.request.urlopen(req, timeout=30))

# 1) Russia ER event + description + siblings
try:
    evs = get("https://gamma-api.polymarket.com/events?slug=united-russia-er-gain-most-seats-in-next-russian-parliamentary-election")
    if not evs:
        evs = get("https://gamma-api.polymarket.com/public-search?q=Russian%20parliamentary%20election%20most%20seats&limit_per_type=5")
        evs = evs.get('events', [])
    for e in evs[:2]:
        print("EVENT:", e.get('title'), "|", e.get('slug'))
        print("DESC:", (e.get('description') or '')[:900].replace('\n',' '))
        for m in e.get('markets', []):
            try:
                prices = json.loads(m.get('outcomePrices','[]'))
            except Exception:
                continue
            print("  M:", m.get('question','')[:80], "| yes", prices[0] if prices else '?', "| cid", (m.get('conditionId') or '')[:20])
except Exception as ex:
    print("RUSSIA ERR", ex)

# 2) Lula market: conditionId + price history
try:
    ms = get("https://gamma-api.polymarket.com/markets?slug=will-luiz-incio-lula-da-silva-win-the-2026-brazilian-presidential-election")
    for m in ms:
        cid = m.get('conditionId')
        print("LULA cid:", cid)
        h = get("https://clob.polymarket.com/prices-history?market=%s&interval=1m&fidelity=1d" % cid)
        pts = h.get('history', [])
        print("LULA 1m daily YES:", [ (p['t'], round(p['p'],3)) for p in pts ][-14:])
except Exception as ex:
    print("LULA HIST ERR", ex)
