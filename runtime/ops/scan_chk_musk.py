import json, os, sys, datetime
sys.path.insert(0,'/root/cash-machine/runtime/db')
import d1cli
d1 = d1cli.d1

# Existing watch rows for Musk tweet markets?
for r in d1("SELECT id, question, status FROM watchlist WHERE question LIKE '%Musk%'")["result"][0]["results"]:
    print(json.dumps(r))
