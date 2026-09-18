#!/usr/bin/env python3
"""Read recent rejected thesis/market_url to avoid dupes."""
import json, urllib.request, os

for line in open('/root/.secrets/cloudflare.env'):
    line = line.strip()
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        os.environ.setdefault(k, v)
ACC = os.environ['CLOUDFLARE_ACCOUNT_ID']
TOK = os.environ['CLOUDFLARE_API_TOKEN']
DB = 'eeb98259-0e2f-44a0-8683-470f3d614e3c'

def d1(sql):
    body = json.dumps({"sql": sql}).encode()
    req = urllib.request.Request(
        f"https://api.cloudflare.com/client/v4/accounts/{ACC}/d1/database/{DB}/query",
        data=body, headers={'Authorization': f'Bearer {TOK}', 'Content-Type': 'application/json'})
    r = json.loads(urllib.request.urlopen(req, timeout=30).read())
    return r['result'][0]['results']

for r in d1("SELECT id, ts_utc, thesis, market_url, category, market_price_yes, my_est_yes FROM rejected ORDER BY rowid DESC LIMIT 30"):
    print(r['ts_utc'], '|', r['category'], '|', r['market_url'], '| mkt', r['market_price_yes'], 'est', r['my_est_yes'])
    print('   ', (r['thesis'] or '')[:150].replace('\n', ' '))
