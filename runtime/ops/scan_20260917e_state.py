import sys, json
sys.path.insert(0, "/root/cash-machine/runtime/db")
import d1p
def q(sql):
    r = d1p.q(sql)
    if "HTTP_ERROR" in r:
        print("HTTP_ERR", r["HTTP_ERROR"], r.get("body", "")[:200]); raise SystemExit(1)
    return r["result"][0]["results"]

print("=== SCHEMAS")
for row in q("SELECT name, sql FROM sqlite_master WHERE type='table' AND name IN ('rejected','trades','watchlist','trade_intents','council_verdicts','sources')"):
    print(row["sql"], "\n")

print("=== RECENT REJECTED")
for r in q("SELECT * FROM rejected ORDER BY rowid DESC LIMIT 8"):
    print(json.dumps({k: str(v)[:55] for k, v in r.items()}))

print("\n=== OPEN TRADES")
for r in q("SELECT * FROM trades WHERE status='open'"):
    print(json.dumps({k: str(v)[:55] for k, v in r.items()}))

print("\n=== WATCHLIST")
for r in q("SELECT * FROM watchlist WHERE status='watching'"):
    print(json.dumps({k: str(v)[:55] for k, v in r.items()}))

print("\n=== INTENTS")
for r in q("SELECT * FROM trade_intents ORDER BY rowid DESC LIMIT 8"):
    print(json.dumps({k: str(v)[:80] for k, v in r.items()}))
