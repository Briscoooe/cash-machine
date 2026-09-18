import json, urllib.request

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
    return json.load(urllib.request.urlopen(req, timeout=30))

slugs = [
    ("merz", "friedrich-merz-out-as-chancellor-of-germany-before-december-31-2026"),
    ("lula", "will-luiz-inacio-lula-da-silva-win-the-2026-brazilian-presidential-election"),
    ("flavio", "will-flavio-bolsonaro-win-the-2026-brazilian-presidential-election"),
    ("hormuz", "iran-charges-hormuz-fees-by-october-31"),
    ("recession", "us-recession-by-end-of-2026"),
    ("dems-house", "will-the-democratic-party-control-the-house-after-the-2026-midterm-elections"),
]
for name, slug in slugs:
    try:
        d = get("https://gamma-api.polymarket.com/markets?slug=" + slug)
        for m in d:
            try:
                prices = json.loads(m.get('outcomePrices','[]'))
            except Exception:
                continue
            print(name, "|", m.get('question','')[:90], "| yes", prices[0] if prices else '?', "| end", (m.get('endDate') or '')[:10])
            desc = (m.get('description') or '')[:600].replace('\n',' ')
            print("   DESC:", desc)
    except Exception as ex:
        print(name, "ERR", ex)
