#!/usr/bin/env python3
"""Search gamma for Bab el-Mandeb October markets."""
import json, urllib.request

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

data = get("https://gamma-api.polymarket.com/public-search?q=bab+el-mandeb&limit_per_type=10")
print(json.dumps(data, indent=1)[:3000])
