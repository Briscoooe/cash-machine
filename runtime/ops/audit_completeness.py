#!/usr/bin/env python3
"""Trade-record completeness audit: any open/closed trade missing thesis, key_figures,
council verdicts, or sources is a failure. Exit 1 on failure."""
import json, subprocess, sys

def d1(sql, params=None):
    body = {"sql": sql, "params": params or []}
    cmd = ["bash","-c",
        'set -a && source /root/.secrets/cloudflare.env && set +a && curl -s -X POST '
        '"https://api.cloudflare.com/client/v4/accounts/${CLOUDFLARE_ACCOUNT_ID}/d1/database/'
        'eeb98259-0e2f-44a0-8683-470f3d614e3c/query" -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" '
        '-H "Content-Type: application/json" --data-binary @- <<EOF\n' + json.dumps(body) + '\nEOF']
    return json.loads(subprocess.run(cmd, capture_output=True, text=True, timeout=60).stdout)

rows = d1("SELECT id, status, thesis, key_figures FROM trades WHERE status IN ('open','closed') AND ts_utc >= '2026-09-13T14:00' ORDER BY ts_utc DESC LIMIT 50  -- completeness gate live from 2026-09-13T14:00; older = legacy")["result"][0]["results"]
bad = []
for t in rows:
    tid = t["id"]
    nv = d1("SELECT COUNT(*) c FROM council_verdicts WHERE rejected_id=?", [tid])["result"][0]["results"][0]["c"]
    ns = d1("SELECT COUNT(*) c FROM sources WHERE rejected_id=?", [tid])["result"][0]["results"][0]["c"]
    kf_ok = t["key_figures"] and str(t["key_figures"]).strip().startswith("[{")
    missing = []
    if not t["thesis"]: missing.append("thesis")
    if not kf_ok: missing.append("key_figures")
    if nv == 0: missing.append(f"council_verdicts({nv})")
    if ns == 0: missing.append(f"sources({ns})")
    if missing:
        bad.append((tid, t["status"], ", ".join(missing)))
if bad:
    print("INCOMPLETE TRADE RECORDS:")
    for tid, st, m in bad: print(f"  {tid} [{st}]: missing {m}")
    sys.exit(1)
print(f"OK: all {len(rows)} live trades have thesis, figures, verdicts, sources")
