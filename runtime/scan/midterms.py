import json, urllib.request

def get(url):
    req=urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
    return json.load(urllib.request.urlopen(req, timeout=30))

# All midterms markets from the 3 events, with conditionIds for calibration tracking
slugs = ['which-party-will-win-the-house-in-2026','which-party-will-win-the-senate-in-2026','balance-of-power-2026-midterms']
out = {}
for slug in slugs:
    ev = get(f'https://gamma-api.polymarket.com/events?slug={slug}')[0]
    for m in ev['markets']:
        try: yes = json.loads(m['outcomePrices'])[0]
        except Exception: continue
        out[m['question']] = (float(yes), m['conditionId'], ev['slug'])
for q,(y,cid,slug) in sorted(out.items(), key=lambda kv: -kv[1][0]):
    print(round(y,3), q[:70], '|', slug)
json.dump({q:{'yes':y,'cid':cid,'slug':slug} for q,(y,cid,slug) in out.items()}, open('/root/cash-machine/runtime/scan/midterms.json','w'), indent=1)
