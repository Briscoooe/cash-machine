import json, urllib.request, time

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
    return json.load(urllib.request.urlopen(req, timeout=30))

cid = "0xdf8e2dc5860027decbe6164555c3c1c9645c3bd33e16b9dc57ca87125047d4a8"
for qs in ["interval=max&fidelity=604800", "interval=1w&fidelity=3600", "fidelity=1440"]:
    try:
        h = get("https://clob.polymarket.com/prices-history?market=%s&%s" % (cid, qs))
        pts = h.get('history', [])
        print(qs, "->", len(pts), "pts; last 10:", [(p['t'], round(p['p'],3)) for p in pts][-10:])
    except Exception as ex:
        print(qs, "ERR", ex)
