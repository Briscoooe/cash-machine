#!/usr/bin/env python3
"""PortWatch chokepoint4 (Bab el-Mandeb) daily transit calls, recent 40 days."""
import json, urllib.request, datetime

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

url = ("https://services9.arcgis.com/weJ1QsnbMYJlCHdG/arcgis/rest/services/"
       "Daily_Chokepoints_Data/FeatureServer/0/query"
       "?where=portid%3D%20'CHOKEPOINT4'%20&outFields=*&outSR=4326"
       "&orderByFields=date%20DESC&f=json&resultRecordCount=40")
data = get(url)
feats = data.get('features', [])
print("rows:", len(feats))
for f in feats:
    a = f['attributes']
    d = str(a.get('date'))[:10]
    print(d, '| n_total:', a.get('n_total'), '| tanker:', a.get('n_tanker'),
          '| container:', a.get('n_container'), '| dry_bulk:', a.get('n_dry_bulk'),
          '| cargo:', a.get('n_cargo'), '| roro:', a.get('n_roro'), '| general:', a.get('n_general_cargo'))
