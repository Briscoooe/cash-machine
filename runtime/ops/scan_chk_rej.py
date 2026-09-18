import json, os, sys
sys.path.insert(0,'/root/cash-machine/runtime/db')
import d1cli
d1 = d1cli.d1
for r in d1("SELECT id, thesis, category, ts_utc FROM rejected ORDER BY ts_utc DESC LIMIT 20")["result"][0]["results"]:
    print(json.dumps(r))
