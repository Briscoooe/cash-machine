import json, urllib.request, datetime

def get(url):
    req=urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

data = get("https://xtracker.polymarket.com/api/users/elonmusk/posts?startDate=2026-09-14&endDate=2026-09-16&timezone=EST")
posts = data.get('data') or []
# window: Sept 14 12:00 ET (=16:00Z) to Sept 16 12:00 ET (16:00Z)
lo = datetime.datetime(2026,9,14,12,0, tzinfo=datetime.timezone(datetime.timedelta(hours=-4)))
hi = datetime.datetime(2026,9,16,12,0, tzinfo=datetime.timezone(datetime.timedelta(hours=-4)))
n=0
for p in posts:
    ts=p.get('createdAt') or ''
    try: t=datetime.datetime.fromisoformat(ts.replace('Z','+00:00'))
    except: continue
    if lo <= t.astimezone(lo.tzinfo) < hi: n+=1
print("count in window so far:", n)
# pace: hours elapsed in window vs remaining
now = datetime.datetime.now(lo.tzinfo)
elapsed = (min(now,hi)-lo).total_seconds()/3600
total = (hi-lo).total_seconds()/3600
print("elapsed hours: %.1f of %.0f" % (elapsed, total))
