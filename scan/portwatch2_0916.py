#!/usr/bin/env python3
"""PortWatch chokepoint layer: inspect available fields/rows."""
import json, urllib.request

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

base = ("https://services9.arcgis.com/weJ1QsnbMYJlCHdG/arcgis/rest/services/"
        "Daily_Chokepoints_Data/FeatureServer/0")
meta = get(base + "?f=json")
print("fields:", [f['name'] for f in meta.get('fields', [])])
url = (base + "/query?where=1%3D1&outFields=*"
       "&orderByFields=dateRange_start%20DESC&f=json&resultRecordCount=40")
data = get(url)
print("features:", len(data.get('features', [])))
for f in data.get('features', [])[:10]:
    print(json.dumps(f['attributes'])[:400])
