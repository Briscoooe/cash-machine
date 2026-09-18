#!/usr/bin/env python3
"""Cron scan: write REJ-20260916-CHONGQING-NOEDGE rejected row + 2 sources rows to D1."""
import json, subprocess, datetime

def d1file(sql_obj, path):
    json.dump(sql_obj, open(path, 'w'))
    out = subprocess.run(['bash', 'runtime/db/d1x.sh', path], capture_output=True, text=True, cwd='/root/cash-machine')
    print(out.stdout[:400])

ts = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
thesis = ("BUY YES '20C' bracket of Highest temperature in Chongqing on September 16 @ 0.14-0.16. "
          "Resolution source is NOAA METAR at ZUCK. Live METAR 2026-09-16 09:00 UTC reads 20C, 100% humidity, "
          "heavy overcast. Forecast sources cap the day at 20-24C with no warming signal. Prior 06:00 UTC reading was 19C "
          "with cooling trend. Probability of max reaching 21C+ is roughly 0.20-0.25. YES at 0.16 carries a real edge.")
kf = [
    {"market": "20C bracket YES price", "note": "0.14-0.16"},
    {"market": "21C bracket YES price", "note": "0.22-0.24"},
    {"market": "22C bracket YES price", "note": "0.25-0.27"},
    {"market": "ZUCK METAR 2026-09-16 09:00 UTC", "note": "20C, dew 20C, RH 100%, overcast, wind 1 m/s"},
    {"market": "ZUCK METAR 2026-09-16 ~06:00 UTC", "note": "19C"},
    {"market": "Exa library Chongqing 16 Sep obs", "note": "high 21.7C city, hourly peak 71F late afternoon, rain"},
    {"market": "tianqi.com Chongqing 16 Sep forecast", "note": "high 24C, light rain"},
    {"market": "weathercrave ZUCK airport 16 Sep", "note": "range 19-20C"},
]
srcs = [
    {"url": "https://tgftp.nws.noaa.gov/data/observations/metar/decoded/ZUCK.TXT", "fact": "Live NOAA METAR ZUCK 2026-09-16 09:00 UTC: 20C, dew 20C, RH 100%, mostly cloudy, wind variable 2 MPH."},
    {"url": "https://polymarket.com/event/highest-temperature-in-chongqing-on-september-16-2026/highest-temperature-in-chongqing-on-september-16-2026-21c", "fact": "Bracket YES prices: 20C 16c, 21C 24c, 22C 27c, 23C 14c; NOAA ZUCK is the resolution source."},
    {"url": "https://m.tianqi.com/tianqi/chongqing/20260916.html", "fact": "Chongqing 16 Sep forecast: light rain, high 24C, low 22C."},
]
rej_sql = {
    "sql": (
        "INSERT INTO rejected (id, ts_utc, thesis, decision, my_est_yes, proposed_price, market_price_yes, reason, "
        "side, category, market_url, key_figures) VALUES "
        f"('REJ-20260916-CHONGQING-NOEDGE', '{ts}', '{thesis.replace(chr(39), chr(39)*2)}', 'rejected-pre-council', 0.24, 0.16, 0.16, "
        "'Re-derived from live NOAA METAR at ZUCK and three independent forecast sources: day max likely 20-21C, "
        "fair value for 20C bracket about 0.24 vs ask 0.16. Skipped: market is thin (single-digit dollars per bracket), "
        "$10 stake would consume more than the visible book; slippage destroys the 8pt edge. No stake-able edge at size.', "
        "'YES', 'no-edge', 'https://polymarket.com/event/highest-temperature-in-chongqing-on-september-16-2026', "
        f"'{json.dumps(kf).replace(chr(39), chr(39)*2)}')"
    )
}
d1file(rej_sql, '/tmp/rej_cq.json')
src_sql = {"sql": "INSERT INTO sources (rejected_id, url, fact) VALUES "
    + ", ".join(f"('REJ-20260916-CHONGQING-NOEDGE', '{s['url']}', \"{s['fact']}\")" for s in srcs)}
d1file(src_sql, '/tmp/src_cq.json')
