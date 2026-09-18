import json, urllib.request

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
    return json.load(urllib.request.urlopen(req, timeout=30))

cid = "0xdf8e2dc5860027decbe6164555c3c1c9645c3bd33e16b9dc57ca87125047d4a8"
try:
    h = get("https://clob.polymarket.com/prices-history?market=%s&startTs=%d&endTs=%d&fidelity=86400" % (
        cid, 1757808000, 1758153600))
    print("LULA daily YES:", [(p['t'], round(p['p'],3)) for p in h.get('history', [])])
except Exception as ex:
    print("hist ERR", ex)
