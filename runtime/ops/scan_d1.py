import json, os, urllib.request

env = {}
with open('/root/.secrets/cloudflare.env') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            env[k] = v.strip().strip('"')

acct = env.get('CLOUDFLARE_ACCOUNT_ID')
tok = env.get('CLOUDFLARE_API_TOKEN')
db = 'eeb98259-0e2f-44a0-8683-470f3d614e3c'

def d1(sql, params=None):
    body = {'sql': sql}
    if params:
        body['params'] = params
    req = urllib.request.Request(
        'https://api.cloudflare.com/client/v4/accounts/%s/d1/database/%s/query' % (acct, db),
        data=json.dumps(body).encode(),
        headers={'Authorization': 'Bearer ' + tok, 'Content-Type': 'application/json'})
    return json.load(urllib.request.urlopen(req, timeout=30))

def q(sql):
    r = d1(sql)
    return r['result'][0]['results']

for lbl, s in [
    ("rejected_cols", "SELECT * FROM rejected LIMIT 1"),
    ("rejected", "SELECT id, thesis, category FROM rejected ORDER BY rowid DESC LIMIT 8"),
]:
    try:
        print(lbl + ":", q(s))
    except Exception as ex:
        print(lbl, "ERR:", ex)
