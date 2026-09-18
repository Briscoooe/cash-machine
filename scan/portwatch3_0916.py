#!/usr/bin/env python3
"""PortWatch Bab el-Mandeb: query correct layer with portid filter."""
import json, urllib.request

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

svc = ("https://services9.arcgis.com/weJ1QsnbMYJlCHdG/arcgis/rest/services/"
       "Daily_Chokepoints_Data/FeatureServer")
info = get(svc + "?f=json")
print("layers:", [(l['id'], l['name']) for l in info.get('layers', [])])
