import sys, os, json
sys.path.insert(0, '/root/cash-machine/runtime/db')
for line in open('/root/.secrets/cloudflare.env'):
    line = line.strip()
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        os.environ[k] = v.strip().strip('"')
import importlib
d1p = importlib.import_module('d1p')

r = d1p.q("SELECT id, thesis, category, ts_utc FROM rejected ORDER BY ts_utc DESC LIMIT 60")
rows = r['result'][0]['results']
print('rejected rows:', len(rows))
for row in rows:
    print('-', row['id'], '|', (row['thesis'] or '')[:100].replace('\n', ' '), '|', row['category'])

w = d1p.q("SELECT id, question, watch_price, current_price, status FROM watchlist")
print('\nwatchlist:')
for row in w['result'][0]['results']:
    print('-', row['id'], '|', (row['question'] or '')[:80], '| watch', row['watch_price'], 'cur', row['current_price'], row['status'])

t = d1p.q("SELECT id, market, side, status, live FROM trades WHERE status='open' OR live=1")
print('\nopen trades:')
for row in t['result'][0]['results']:
    print('-', row['id'], '|', (row['market'] or '')[:80], row['side'], row['status'], 'live', row['live'])

i = d1p.q("SELECT id, status, market FROM trade_intents ORDER BY ts_utc DESC LIMIT 10")
print('\nrecent intents:')
for row in i['result'][0]['results']:
    print('-', row['id'], row['status'], (row['market'] or '')[:70])
