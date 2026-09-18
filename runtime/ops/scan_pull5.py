import json, urllib.request, time

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
    return json.load(urllib.request.urlopen(req, timeout=30))

cid = "0xdf8e2dc5860027decbe6164555c3c1c9645c3bd33e16b9dc57ca87125047d4a8"
now = int(time.time())
for qs in ["interval=1m", "interval=all", "startTs=%d&endTs=%d" % (now-30*86400, now)]:
    try:
        h = get("https://clob.polymarket.com/prices-history?market=%s&%s" % (cid, qs))
        pts = h.get('history', [])
        print(qs, "->", len(pts), "pts; tail:", [(p['t'], round(p['p'],3)) for p in pts][-8:])
    except Exception as ex:
        print(qs, "ERR", ex)
