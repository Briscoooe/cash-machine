import json, urllib.request

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
    return json.load(urllib.request.urlopen(req, timeout=30))

slugs = ["will-flvio-bolsonaro-win-the-2026-brazilian-presidential-election",
         "will-luiz-incio-lula-da-silva-win-the-2026-brazilian-presidential-election"]
for slug in slugs:
    try:
        d = get("https://clob.polymarket.com/book?token_id=" + slug)  # placeholder
    except Exception:
        pass
    try:
        ms = get("https://gamma-api.polymarket.com/markets?slug=" + slug)
        for m in ms:
            print(m['question'][:60], "| yes", json.loads(m['outcomePrices'])[0],
                  "| spread", m.get('spread'), "| liq", m.get('liquidityNum'))
    except Exception as ex:
        print(slug, "ERR", ex)
