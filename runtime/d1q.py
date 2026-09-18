import json, os, sys, urllib.request
env = {}
for line in open('/root/.secrets/cloudflare.env'):
    line=line.strip()
    if '=' in line and not line.startswith('#'):
        k,v=line.split('=',1); env[k]=v.strip().strip('"')
acct=env['CLOUDFLARE_ACCOUNT_ID']; tok=env['CLOUDFLARE_API_TOKEN']
def d1(sql):
    req=urllib.request.Request(
        f"https://api.cloudflare.com/client/v4/accounts/{acct}/d1/database/eeb98259-0e2f-44a0-8683-470f3d614e3c/query",
        data=json.dumps({"sql":sql}).encode(),
        headers={'Authorization':f'Bearer {tok}','Content-Type':'application/json'})
    return json.load(urllib.request.urlopen(req,timeout=30))
if __name__=='__main__':
    r=d1(sys.argv[1])
    res=r.get('result')
    if isinstance(res,list): res=res[0]
    print(json.dumps(res.get('results',[]),indent=1)[:3000])
