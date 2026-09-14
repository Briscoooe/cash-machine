import json, urllib.request

def post(url, data, headers={}):
    req = urllib.request.Request(url, data=json.dumps(data).encode() if data else None,
                                 headers={'Content-Type': 'application/json',
                                          'User-Agent': 'Mozilla/5.0', **headers})
    return json.load(urllib.request.urlopen(req, timeout=30))

import json, os
WALLET = json.load(open("/root/.secrets/wallet_address.json"))["wallet"] if not os.environ.get("WALLET_ADDRESS") else os.environ["WALLET_ADDRESS"]
RPC = "https://polygon-bor-rpc.publicnode.com"

r = post(RPC, {"jsonrpc": "2.0", "method": "eth_call",
               "params": [{"to": "0xC011a7E12a19f7B1f670d46F03B03f3342E82DFB",
                           "data": "0x70a08231" + WALLET[2:].lower().zfill(64)}, "latest"], "id": 1})
cash = int(r["result"], 16) / 1e6
req = urllib.request.Request(f"https://data-api.polymarket.com/positions?user={WALLET}",
                             headers={"User-Agent": "Mozilla/5.0"})
positions = json.load(urllib.request.urlopen(req, timeout=30))
posval = round(sum(p.get("currentValue", 0) for p in positions), 2)
print("CASH", cash, "POS", posval)

env = {}
for line in open("/root/.secrets/cloudflare.env"):
    line = line.strip()
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        env[k] = v.strip().strip('"')
acct, tok = env["CLOUDFLARE_ACCOUNT_ID"], env["CLOUDFLARE_API_TOKEN"]
url = f"https://api.cloudflare.com/client/v4/accounts/{acct}/d1/database/eeb98259-0e2f-44a0-8683-470f3d614e3c/query"
for key, val in (("wallet_cash", cash), ("position_value", posval)):
    post(url, {"sql": "INSERT INTO state (k, v) VALUES (?, ?) ON CONFLICT(k) DO UPDATE SET v=excluded.v",
               "params": [key, str(val)]},
         {"Authorization": f"Bearer {tok}"})
print("D1 state updated")