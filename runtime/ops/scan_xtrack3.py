import json, urllib.request, datetime
from collections import Counter

def get(url):
    req=urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

ET=datetime.timezone(datetime.timedelta(hours=-4))
data = get("https://xtracker.polymarket.com/api/users/elonmusk/posts?startDate=2026-09-10&endDate=2026-09-16&timezone=EST")
posts = data.get('data') or []
# bucket by (EST date, hour)
byday=Counter(); byhour=Counter(); block=Counter()
for p in posts:
    ts=p.get('createdAt') or ''
    try: t=datetime.datetime.fromisoformat(ts.replace('Z','+00:00')).astimezone(ET)
    except: continue
    byday[t.date()]+=1
    byhour[t.hour]+=1
    # block 02:00-12:00 ET counts (the remaining window shape)
    if 2 <= t.hour < 12:
        block[t.date()]+=1
print("posts per EST day:", {str(k):v for k,v in sorted(byday.items())})
print("posts per hour-of-day ET (Sep10-16):", dict(sorted(byhour.items())))
print("posts in 02:00-11:59 ET block by day:", {str(k):v for k,v in sorted(block.items())})
