import sys, json
sys.path.insert(0, "/root/cash-machine/runtime/db")
import d1p
def run(sql, params=None):
    body = {"sql": sql}
    if params: body["params"] = params
    req = d1p.q.__globals__  # unused
def d1(sql, params=None):
    import urllib.request, os
    body = {"sql": sql}
    if params: body["params"] = params
    req = urllib.request.Request(
        "https://api.cloudflare.com/client/v4/accounts/%s/d1/database/eeb98259-0e2f-44a0-8683-470f3d614e3c/query" % os.environ["CLOUDFLARE_ACCOUNT_ID"],
        data=json.dumps(body).encode(),
        headers={"Authorization": "Bearer " + os.environ["CLOUDFLARE_API_TOKEN"], "Content-Type": "application/json"})
    resp = json.loads(urllib.request.urlopen(req, timeout=30).read())
    return resp["result"][0]["results"]

for r in d1("SELECT id, decision, category, proposed_price FROM rejected WHERE id LIKE 'R-20260917e-%'"):
    print(r)
print("sources:", d1("SELECT COUNT(*) n FROM sources WHERE rejected_id LIKE 'R-20260917e-%'")[0]["n"])
print("wl:", d1("SELECT id, current_price, notes FROM watchlist WHERE id='W-berlin-cdu-notfirst'")[0]["notes"][:80])
