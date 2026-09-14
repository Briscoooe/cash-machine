import json, urllib.request

def d1(sql):
    import os
    acc=os.environ["CLOUDFLARE_ACCOUNT_ID"]; tok=os.environ["CLOUDFLARE_API_TOKEN"]
    req=urllib.request.Request(f"https://api.cloudflare.com/client/v4/accounts/{acc}/d1/database/eeb98259-0e2f-44a0-8683-470f3d614e3c/query",
        data=json.dumps({"sql":sql}).encode(), headers={"Authorization":f"Bearer {tok}","Content-Type":"application/json"})
    return json.loads(urllib.request.urlopen(req,timeout=30).read())

if __name__=="__main__":
    import sys
    for sql in sys.argv[1:]:
        print(json.dumps(d1(sql)))
