import sys, os, json
sys.path.insert(0, '/root/cash-machine/runtime/db')
for line in open('/root/.secrets/cloudflare.env'):
    line=line.strip()
    if '=' in line and not line.startswith('#'):
        k,v=line.split('=',1); os.environ[k]=v.strip().strip('"')
import importlib; d1p=importlib.import_module('d1p')

rows = [
 ('W26-USIRAN-SEP30','US x Iran diplomatic meeting by September 30, 2026?','next-round-of-us-iran-peace-talks-byptptpt-20260623022722982',0.095,0.40,'YES','Trump says open to talks; Iran publicly refuses until conditions met.','Gulf leaders meeting at UNGA could open a diplomatic channel','2026-09-22'),
 ('W26-USIRAN-DEC31','US x Iran diplomatic meeting by December 31, 2026?','next-round-of-us-iran-peace-talks-byptptpt-20260623022722982',0.42,0.30,'NO','No talks until Iran conditions met; MoU collapsed; strikes decision pending.','Trump announces resumed large-scale strikes after UNGA meeting','2026-09-22'),
 ('W27-ER-NL-GAIN','Will New People (NL) gain the most seats in the next Russian parliamentary election?','which-party-will-gain-most-seats-in-russian-parliamentary-election',0.203,0.35,'YES','NL at 0.203 vs KPRF 0.014 despite KPRF polling ahead; official results could mirror 2021 KPRF loss to NL.','Official Duma results published','2026-09-30'),
 ('W28-USIRAN-TRUMPDEC','Trump decides against renewed large-scale strikes after UNGA consultations','(catalyst-watch, no market)',0,0,'INFO','Trump told Axios he approaches a major decision; Gulf leaders prefer de-escalation.','Post-UNGA decision announcement','2026-09-25'),
]
for w in rows:
    wid, q, slug, cur, wp, direction, seed, cat, cdate = w
    if slug == '(catalyst-watch, no market)':
        continue
    r = d1p.q("INSERT OR IGNORE INTO watchlist (id, ts_utc, market, question, slug, current_price, watch_price, direction, thesis_seed, catalyst, catalyst_date, status) VALUES ('%s', datetime('now'), '%s', '%s', '%s', %s, %s, '%s', '%s', '%s', '%s', 'watching')" % (
        wid, q.replace("'","''"), q.replace("'","''"), slug, cur, wp, direction,
        seed.replace("'","''"), cat.replace("'","''"), cdate))
print('watchlist seeded')
r = d1p.q("SELECT id, question, status FROM watchlist WHERE id IN ('W26-USIRAN-SEP30','W26-USIRAN-DEC31','W27-ER-NL-GAIN')")
for row in r['result'][0]['results']:
    print('-', row['id'], row['status'], (row['question'] or '')[:60])
