#!/usr/bin/env python3
"""Week-of-Sep-14 Bab el-Mandeb ship ladder: fetch PortWatch actuals vs market."""
import json, urllib.request

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

# IMF PortWatch chokepoint daily data (chokepoint 4 = Bab el-Mandeb)
url = ("https://services9.arcgis.com/weJ1QsnbMYJlCHdG/arcgis/rest/services/"
       "Daily_Chokepoints_Data/FeatureServer/0/query"
       "?where=1%3D1&outFields=*&orderByFields=dateRange_start%20DESC"
       "&f=json&resultRecordCount=40")
data = get(url)
for f in data.get('features', []):
    a = f['attributes']
    print(a.get('dateRange_start'), a.get('dateRange_end'), '| transit_calls:', a.get('transit_calls'), '| portcalls:', a.get('port_calls'))
