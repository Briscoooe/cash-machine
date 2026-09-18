import json, urllib.request

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    return json.load(urllib.request.urlopen(req, timeout=30))

slugs = [
 'which-party-will-gain-most-seats-in-russian-parliamentary-election',  # ER 0.765, end 9/30
 'us-announces-end-of-iranian-blockade-byptptpt-20260713152715080',     # 0.115
 'bab-el-mandeb-strait-effectively-closed-by',                          # 0.034
 'which-party-will-win-the-senate-in-2026',                             # D senate 0.595
 'brazil-presidential-election',                                        # Lula 0.425 / Flavio 0.546
 'netanyahu-out-before-2027',                                           # 0.475
]
for slug in slugs:
    ev = get(f'https://gamma-api.polymarket.com/events?slug={slug}')
    if not ev:
        print('MISSING', slug); continue
    ev = ev[0]
    print('==', ev['title'], '| end', ev.get('endDate'), '| vol24', ev.get('volume24hr'))
    print('DESC:', (ev.get('description') or '')[:800].replace('\n', ' '))
    for m in ev['markets']:
        try: op = json.loads(m.get('outcomePrices') or '[]')
        except Exception: op = []
        print('   M:', (m.get('question') or '')[:80], '| yes', op[:1], '| end', (m.get('endDate') or '')[:10], '| vol', m.get('volumeNum'))
    print()
