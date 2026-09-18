import json, urllib.request, time

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
    return json.load(urllib.request.urlopen(req, timeout=30))

# gamma may serve history via its own endpoint; try gamma series/timeseries
cid = "0xdf8e2dc5860027decbe6164555c3c1c9645c3bd33e16b9dc57ca87125047d4a8"
urls = [
    "https://gamma-api.polymarket.com/prices-history?market=%s&interval=1m" % cid,
    "https://clob.polymarket.com/prices-history?market=%s&interval=1w&fidelity=1d" % cid,
]
for u in urls:
    try:
        h = get(u)
        pts = h.get('history', [])
        print(u.split('/')[2], len(pts), [(time.strftime('%m-%d', time.gmtime(p['t'])), round(p['p'],3)) for p in pts][-12:])
    except Exception as ex:
        print(u.split('/')[2], "ERR", ex)
