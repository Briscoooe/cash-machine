import json, urllib.request, datetime

def get(url):
    req=urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

# Market window: Sept 14 12:00 ET -> Sept 16 12:00 ET
# Fetch posts from tracker, count in-window
data = get("https://xtracker.polymarket.com/api/users/elonmusk/posts?startDate=2026-09-14&endDate=2026-09-16&timezone=EST")
posts = data.get('data') or data
if isinstance(posts, dict): posts = posts.get('posts', [])
print("total posts returned:", len(posts))
# posts may include timestamps; count per EST day
from collections import Counter
c=Counter()
sample=None
for p in posts:
    ts = p.get('createdAt') or p.get('timestamp') or p.get('postedAt')
    if sample is None: sample=json.dumps(p)[:300]
    if ts:
        d=str(ts)[:10]
        c[d]+=1
print("per-day:", dict(c))
print("sample:", sample)
