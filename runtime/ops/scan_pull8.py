import json, urllib.request, time

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
    return json.load(urllib.request.urlopen(req, timeout=30))

cid = "0xdf8e2dc5860027decbe6164555c3c1c9645c3bd33e16b9dc57ca87125047d4a8"
now = int(time.time())
for qs in ["interval=6m", "interval=1m&fidelity=6h", "interval=1d"]:
    try:
        h = get("https://clob.polymarket.com/prices-history?market=%s&%s" % (cid, qs))
        pts = h.get('history', [])
        print(qs, len(pts), [(time.strftime('%m-%d %H:%M', time.gmtime(p['t'])), round(p['p'],3)) for p in pts][-15:])
    except Exception as ex:
        print(qs, "ERR", ex)
