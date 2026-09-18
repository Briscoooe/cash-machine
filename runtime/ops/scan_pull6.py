import json, urllib.request, time

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
    return json.load(urllib.request.urlopen(req, timeout=30))

cid = "0xdf8e2dc5860027decbe6164555c3c1c9645c3bd33e16b9dc57ca87125047d4a8"
now = int(time.time())
print("now:", now, time.strftime('%Y-%m-%d', time.gmtime(now)))
h = get("https://clob.polymarket.com/prices-history?market=%s&startTs=%d&endTs=%d&fidelity=1440" % (cid, now-30*86400, now))
pts = h.get('history', [])
print(len(pts), [(time.strftime('%m-%d', time.gmtime(p['t'])), round(p['p'],3)) for p in pts])
