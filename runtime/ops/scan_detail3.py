import json, urllib.request

def get(url):
    req=urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

# pull full detail for the shortlist candidates
slugs = [
 "elon-musk-of-tweets-september-14-september-16-2026",
 "what-price-will-wti-hit-in-september-2026",
 "israel-x-iran-ceasefire-continues-throughptptpt-20260716224448963",
 "brazil-presidential-election",
]
out={}
for s in slugs:
    ev = get(f"https://gamma-api.polymarket.com/events?slug={s}")
    for e in ev:
        ms=[]
        for m in e.get('markets',[]):
            op=json.loads(m.get('outcomePrices') or '[]')
            ms.append({'q': m.get('question'), 'yes': op[0] if op else None,
                       'end': (m.get('endDate') or '')[:10]})
        out[s]={'desc': (e.get('description') or '')[:900], 'markets': ms,
                'vol24': e.get('volume24hr'), 'endDate': (e.get('endDate') or '')[:10]}
json.dump(out, open('/root/cash-machine/runtime/ops/scan_detail3.json','w'), indent=1)
for s,v in out.items():
    print("=== ", s, "vol24", round(v['vol24'] or 0))
    print(v['desc'][:400].replace('\n',' '))
    for m in v['markets']:
        print("  ", m['yes'], "|", m['q'][:95])
