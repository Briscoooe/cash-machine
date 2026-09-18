import json, urllib.request, os

def d1(sql):
    acc=os.environ["CLOUDFLARE_ACCOUNT_ID"]; tok=os.environ["CLOUDFLARE_API_TOKEN"]
    req=urllib.request.Request(f"https://api.cloudflare.com/client/v4/accounts/{acc}/d1/database/eeb98259-0e2f-44a0-8683-470f3d614e3c/query",
        data=json.dumps({"sql":sql}).encode(), headers={"Authorization":f"Bearer {tok}","Content-Type":"application/json"})
    return json.loads(urllib.request.urlopen(req,timeout=30).read())

def rows(sql):
    return d1(sql)["result"][0]["results"]

for r in rows("SELECT id, question, slug, current_price, watch_price, direction, thesis_seed, catalyst, catalyst_date FROM watchlist WHERE status='watching'"):
    print(json.dumps(r))
