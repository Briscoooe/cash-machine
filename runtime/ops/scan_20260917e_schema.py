import sys, json, os
# don't import d1 (env missing); read creds directly
ACC = TOK = None
for p in ("/root/.secrets/cloudflare.env", "/root/.hermes/.env"):
    if os.path.exists(p):
        for line in open(p):
            line = line.strip()
            if line.startswith("export "):
                line = line[7:]
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"'))
import urllib.request
ACC = os.environ["CLOUDFLARE_ACCOUNT_ID"]; TOK = os.environ["CLOUDFLARE_API_TOKEN"]
DB = "eeb98259-0e2f-44a0-8683-470f3d614e3c"

def d1(sql, params=None):
    body = {"sql": sql}
    if params: body["params"] = params
    req = urllib.request.Request(
        f"https://api.cloudflare.com/client/v4/accounts/{ACC}/d1/database/{DB}/query",
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {TOK}", "Content-Type": "application/json"})
    resp = json.loads(urllib.request.urlopen(req, timeout=30).read())
    if not resp.get("success"):
        raise RuntimeError(json.dumps(resp)[:300])
    return resp[0]["results"]

def q(sql):
    return d1(sql)

for t in ("rejected", "trades", "watchlist", "trade_intents", "council_verdicts", "sources"):
    print("=== SCHEMA", t)
    try:
        for row in q(f"SELECT sql FROM sqlite_master WHERE name='{t}'"):
            print(row["sql"])
    except Exception as e:
        print("ERR", e)

print("\n=== RECENT REJECTED")
try:
    for r in q("SELECT * FROM rejected ORDER BY rowid DESC LIMIT 8"):
        print(json.dumps({k: str(v)[:55] for k, v in r.items()}))
except Exception as e:
    print("ERR", e)
