import json, os, urllib.request
DB="eeb98259-0e2f-44a0-8683-470f3d614e3c"
def q(sql, params=None):
    body={"sql":sql}
    if params: body["params"]=params
    req=urllib.request.Request(
        f"https://api.cloudflare.com/client/v4/accounts/{os.environ['CLOUDFLARE_ACCOUNT_ID']}/d1/database/{DB}/query",
        data=json.dumps(body).encode(),
        headers={"Authorization":f"Bearer {os.environ['CLOUDFLARE_API_TOKEN']}","Content-Type":"application/json"})
    try: return json.loads(urllib.request.urlopen(req,timeout=30).read())
    except urllib.error.HTTPError as e: return {"HTTP_ERROR":e.code,"body":e.read().decode()[:300]}
