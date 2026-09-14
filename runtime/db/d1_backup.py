#!/usr/bin/env python3
"""Nightly local backup of D1 'cash-machine' (source of truth) → JSON on this server.
Cron: daily 6am UTC (after housekeeping job)."""
import requests, json, os, datetime, gzip, hashlib

SECRETS = "/root/.secrets/cloudflare.env"
D1META = "/root/.secrets/cashmachine_d1.json"
BACKUP_DIR = "/root/polymarket/backups"

env = {}
for line in open(SECRETS):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, _, v = line.partition("="); env[k] = v
cf, acct = env["CLOUDFLARE_API_TOKEN"], env["CLOUDFLARE_ACCOUNT_ID"]
uuid = json.load(open(D1META))["database_uuid"]
H = {"Authorization": f"Bearer {cf}", "Content-Type": "application/json"}

def q(sql):
    r = requests.post(f"https://api.cloudflare.com/client/v4/accounts/{acct}/d1/database/{uuid}/query",
        headers=H, json={"sql": sql}, timeout=60).json()
    if not r.get("success"):
        raise RuntimeError(f"D1 error: {r.get('errors')}")
    return r["result"][0]["results"]

import os, datetime
os.makedirs(BACKUP_DIR, exist_ok=True)
dump = {}
for table in ["state", "trades", "rejected", "sources", "council_verdicts", "council_runs", "daily_totals", "market_snapshots"]:
    dump[table] = q(f"SELECT * FROM {table}")
today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
payload = json.dumps({"dumped_utc": datetime.datetime.utcnow().isoformat(), "tables": dump})
# write compressed
path = f"{BACKUP_DIR}/{today}.json.gz"
with gzip.open(path, "wt") as f:
    f.write(payload)
# keep only last 30 days
for f in sorted(os.listdir(BACKUP_DIR))[:-30]:
    os.remove(os.path.join(BACKUP_DIR, f))
print(f"backup written: {path} ({os.path.getsize(path)} bytes, {sum(len(v) for v in dump.values())} rows)")