import sys, json
sys.path.insert(0, "/root/cash-machine/runtime/db")
import d1p
r = d1p.q("SELECT name FROM sqlite_master WHERE type='table'")
print(json.dumps(r)[:2000])
