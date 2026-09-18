#!/usr/bin/env python3
"""Check trades schema and the Oman Sep-14 market outcome."""
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

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

print(d1("PRAGMA table_info(trades)"))
ev = get("https://gamma-api.polymarket.com/events?slug=iran-oman-hormuz-management-agreement-byptptpt-20260804222725871")
for e in ev:
    for m in e.get('markets', []):
        print(m.get('question'), json.loads(m.get('outcomePrices') or '[]'), 'closed:', m.get('closed'), 'uma:', m.get('umaResolutionStatus'))
