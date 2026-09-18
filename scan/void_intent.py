#!/usr/bin/env python3
"""Clean stale OMAN-SEP14 intent; candidate candidates none -> finalize run without council."""
import json, urllib.request, os, datetime

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
    if not r.get('success'):
        raise Exception(json.dumps(r.get('errors')))
    return r['result'][0]['results']

now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
res = d1("UPDATE trade_intents SET status='voided', note='Scan 2026-09-16: market resolved NO by deadline (Sep 14 rung 0/1, Uma resolved). Intent stale; no execution.', ts_utc=ts_utc WHERE id='TI-20260913-OMAN-SEP14'")
print('void update:', res)
print(d1("SELECT id, status, note FROM trade_intents WHERE id='TI-20260913-OMAN-SEP14'"))
