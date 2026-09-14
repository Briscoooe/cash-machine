#!/usr/bin/env python3
"""Audit D1 trades against on-chain truth. Reverts false closes."""
import json, gzip, datetime, requests

import json, os
WALLET = json.load(open("/root/.secrets/wallet_address.json"))["wallet"] if not os.environ.get("WALLET_ADDRESS") else os.environ["WALLET_ADDRESS"]
RPC = "https://polygon-bor-rpc.publicnode.com"
env = {}
for line in open("/root/.secrets/cloudflare.env"):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, _, v = line.partition("="); env[k] = v
ACC, TOK, DB = env["CLOUDFLARE_ACCOUNT_ID"], env["CLOUDFLARE_API_TOKEN"], "eeb98259-0e2f-44a0-8683-470f3d614e3c"
HEAD = {"Authorization": f"Bearer {TOK}"}

def q(sql, params=None):
    body = {"sql": sql}
    if params: body["params"] = params
    r = requests.post(f"https://api.cloudflare.com/client/v4/accounts/{ACC}/d1/database/{DB}/query",
                      headers=HEAD, json=body, timeout=30).json()
    if not r.get("success"):
        print("D1 ERR", r.get("errors"), sql[:80]); return None
    return (r.get("result") or [{}])[0].get("results")

def main():
    trades = q("SELECT * FROM trades") or []
    if not trades:
        print("no trades"); return
    acts = requests.get(f"https://data-api.polymarket.com/activity?user={WALLET}&limit=200", timeout=20).json()
    if isinstance(acts, dict):
        print("activity API error:", acts); return
    sells_by_cond = {}
    for a in acts:
        if isinstance(a, str):
            print("unexpected activity entry:", a); continue
        if a.get("type") == "TRADE" and a.get("side") == "SELL":
            sells_by_cond.setdefault(a.get("conditionId"), []).append(a)
    fake = []
    for t in trades:
        if t.get("status") != "closed":
            continue
        has_sell = t.get("condition_id") in sells_by_cond
        # market resolved + redeemed also counts; treat activity 'REDEEM' as proof
        redeemed = any(a.get("type") == "REDEEM" and a.get("conditionId") == t.get("condition_id") for a in acts)
        if not (has_sell or redeemed):
            print(f"FAKE CLOSE: {t['id']} — no SELL/REDEEM on-chain. Reverting to open.")
            q("UPDATE trades SET status='open', exit_price=NULL, realized_pl=NULL WHERE id=?", [t["id"]])
    print(f"audited {len(trades)} trades, sells on-chain: {sum(len(v) for v in sells_by_cond.values())}")

if __name__ == "__main__":
    main()