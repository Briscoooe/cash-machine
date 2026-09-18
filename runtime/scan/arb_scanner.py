#!/usr/bin/env python3
"""Orderbook-depth arbitrage scanner for Polymarket negRisk multi-outcome events.

Purely numeric: no council, no news verification. For each live negRisk event,
sum the REAL best ask across every outcome leg. Buying one share of every leg
costs sum_ask and pays exactly $1 (exactly one outcome wins in negRisk markets).

Alert when: sum_ask <= 1 - MIN_EDGE, with capacity (min top-of-book size) >= MIN_CAP.
Writes findings to D1 table arb_scans. Prints alert lines for the cron bubble rule.
"""
import json, os, sys, time, datetime, urllib.request, urllib.parse
from concurrent.futures import ThreadPoolExecutor

MIN_EDGE = float(os.environ.get('ARB_MIN_EDGE', '0.02'))    # net >= 2%
MIN_CAP = float(os.environ.get('ARB_MIN_CAP', '50'))         # >= 50 shares deep
MAX_EVENTS = int(os.environ.get('ARB_MAX_EVENTS', '400'))
UA = {'User-Agent': 'cash-machine-arb-scanner'}

def fetch(url, timeout=15):
    req = urllib.request.Request(url, headers=UA)
    return json.load(urllib.request.urlopen(req, timeout=timeout))

def best_ask(token_id):
    try:
        b = fetch('https://clob.polymarket.com/book?token_id=' + token_id, timeout=10)
        asks = sorted([(float(x['price']), float(x['size'])) for x in b.get('asks', [])])
        return asks[0] if asks else None
    except Exception:
        return None

def main():
    # 1. pull live negRisk events (volume-sorted)
    events = []
    off = 0
    while len(events) < MAX_EVENTS:
        batch = fetch('https://gamma-api.polymarket.com/events?closed=false&limit=100&offset=%d&order=volume24hr&ascending=false' % off)
        events += [e for e in batch if any(m.get('negRisk') for m in e.get('markets', []))]
        if len(batch) < 100:
            break
        off += 100
    events = events[:MAX_EVENTS]

    findings = []
    for ev in events:
        if ev.get('closed'):
            continue
        legs = []
        ok = True
        for m in ev.get('markets', []):
            if m.get('closed'):
                continue
            try:
                t = json.loads(m['clobTokenIds'])
                tok = t[0]  # YES token
            except Exception:
                ok = False
                break
            legs.append((m['question'], tok))
        if not ok or len(legs) < 3:
            continue
        with ThreadPoolExecutor(max_workers=8) as ex:
            results = list(ex.map(lambda lt: (lt[0], best_ask(lt[1])), legs))
        if any(r[1] is None for r in results):
            continue
        total = 0.0
        sizes = []
        leg_rows = []
        for qname, ba in results:
            price, size = ba
            total += price
            sizes.append(size)
            leg_rows.append({'q': qname, 'ask': price, 'size': size})
        if total <= 0:
            continue
        net = (1 - total) * 100
        if net >= MIN_EDGE and min(sizes) >= MIN_CAP:
            findings.append({
                'event': ev['title'], 'event_slug': ev.get('slug', ''),
                'legs': len(leg_rows), 'sum_ask': round(total, 4),
                'net_pct': round(net, 2), 'capacity_usd': round(min(sizes), 1),
                'legs_json': json.dumps(leg_rows),
            })

    # 2. write to D1
    env = {}
    for line in open('/root/.secrets/cloudflare.env'):
        if '=' in line and not line.strip().startswith('#'):
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip()
    import subprocess, shlex
    now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    for f in findings:
        fid = 'ARB-%s-%s' % (now[:10].replace('-', ''), abs(hash(f['event_slug'])) % 100000)
        sql = ("INSERT INTO arb_scans (id, ts_utc, event, event_slug, legs, sum_ask, net_pct, capacity_usd, legs_json) VALUES ('%s','%s','%s','%s',%d,%.4f,%.2f,%.1f,'%s')"
               % (fid, now, f['event'].replace("'", "''"), f['event_slug'], f['legs'], f['sum_ask'], f['net_pct'], f['capacity_usd'], f['legs_json'].replace("'", "''")))
        payload = json.dumps({"sql": sql})
        cmd = ('source /root/.secrets/cloudflare.env && curl -s -X POST "%s" '
               '-H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" -H "Content-Type: application/json" --data %s'
               % ('https://api.cloudflare.com/client/v4/accounts/%s/d1/database/eeb98259-0e2f-44a0-8683-470f3d614e3c/query' % env['CLOUDFLARE_ACCOUNT_ID'], shlex.quote(payload)))
        subprocess.run(['bash', '-c', cmd], capture_output=True, text=True)

    # 3. report — this is the whole stdout; the cron bubble rule decides delivery
    if findings:
        findings.sort(key=lambda f: -f['net_pct'])
        print('ARBITRAGE ALERT: %d live orderbook arbs found' % len(findings))
        for f in findings[:5]:
            print('- %s | %d legs | cost $%.3f per $1 | net +%.1f%% | capacity ~$%.0f'
                  % (f['event'][:60], f['legs'], f['sum_ask'], f['net_pct'], f['capacity_usd']))
    else:
        print('ARB_SCAN_CLEAN: %d negRisk events checked, no arb >= %.0f%% with >= %.0f share depth'
              % (len(events), MIN_EDGE * 100, MIN_CAP))

if __name__ == '__main__':
    main()
