#!/usr/bin/env python3
"""Cron scan: query D1 via d1q.sh and print compact result lines."""
import json, subprocess, sys

def d1(sql):
    out = subprocess.run(['bash', 'runtime/db/d1q.sh', sql], capture_output=True, text=True, cwd='/root/cash-machine')
    return json.loads(out.stdout)['result'][0]['results']

what = sys.argv[1]
if what == 'schema':
    print([c['name'] for c in d1(f"PRAGMA table_info({sys.argv[2]})")])
elif what == 'sql':
    for x in d1(sys.argv[2]):
        print(x)
