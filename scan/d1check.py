#!/usr/bin/env python3
"""Read D1 history; capture raw error bodies."""
import json, urllib.request, os, urllib.error

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
    try:
        r = json.loads(urllib.request.urlopen(req, timeout=30).read())
    except urllib.error.HTTPError as e:
        return {'HTTP_ERROR': e.read().decode()[:300]}
    if not r.get('success'):
        return {'ERR': r.get('errors')}
    return r['result'][0]['results']

print('rejected:', d1("SELECT question, category FROM rejected ORDER BY rowid DESC LIMIT 25"))
print('watchlist:', d1("SELECT question, watch_price, direction, status FROM watchlist LIMIT 30"))
print('intents:', d1("SELECT * FROM trade_intents LIMIT 10"))
print('cols rejected:', d1("PRAGMA table_info(rejected)"))
print('cols watchlist:', d1("PRAGMA table_info(watchlist)"))
