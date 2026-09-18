import json, subprocess, sys, os
sql=sys.argv[1]
import urllib.request
env=dict(os.environ)
for f in ('/root/.secrets/cloudflare.env',):
    for line in open(f):
        line=line.strip()
        if '=' in line and not line.startswith('#'):
            k,v=line.split('=',1); env[k]=v.strip().strip('"')
url=f"https://api.cloudflare.com/client/v4/accounts/{env['CLOUDFLARE_ACCOUNT_ID']}/d1/database/eeb98259-0e2f-44a0-8683-470f3d614e3c/query"
req=urllib.request.Request(url, data=json.dumps({"sql":sql}).encode(),
    headers={"Authorization":"Bearer "+env['CLOUDFLARE_API_TOKEN'],"Content-Type":"application/json"})
d=json.load(urllib.request.urlopen(req,timeout=30))
for r in d['result'][0]['results']: print(json.dumps(r, default=str))
