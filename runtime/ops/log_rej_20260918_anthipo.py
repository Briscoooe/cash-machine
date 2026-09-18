import json, urllib.request

def d1(sql):
    env={}
    for line in open('/root/.secrets/cloudflare.env'):
        line=line.strip()
        if '=' in line and not line.startswith('#'):
            k,v=line.split('=',1); env[k]=v.strip().strip('"')
    req=urllib.request.Request(
        f"https://api.cloudflare.com/client/v4/accounts/{env['CLOUDFLARE_ACCOUNT_ID']}/d1/database/eeb98259-0e2f-44a0-8683-470f3d614e3c/query",
        data=json.dumps({"sql":sql}).encode(),
        headers={'Authorization':f"Bearer {env['CLOUDFLARE_API_TOKEN']}",'Content-Type':'application/json'})
    return json.load(urllib.request.urlopen(req,timeout=30))

rej_id="R-20260918-ANTHIPO-3T-NOEDGE"
market_url="https://polymarket.com/event/will-anthropics-valuation-hit-by-december-31"
reasoning=("Pre-council no-edge skip. Market: Anthropic valuation hit (HIGH) $3.0T by Dec 31, YES 0.285. "
           "Price flat 0.245-0.325 for 3 weeks through the Sep 14-17 $2T-IPO-target headlines (informed money). "
           "Decomposition: P(IPO by Dec 31) ~0.6 x P(val >= $3T | IPO incl. pop) ~0.3 + secondary path ~0.03 "
           "=> P(YES) ~0.22-0.30, brackets the 0.285 price. NO fair value within 5pts of 0.715. Skip.")
kf=json.dumps([
 {"market":"Anthropic valuation $3.0T by Dec 31","note":"YES 0.285, NO 0.715; YES range 0.245-0.325 over 3 weeks (CLOB history)"},
 {"market":"NPM Anthropic price","note":"$729.87/share as of Aug 19, 2026 (~$1.1T implied)"},
 {"market":"Secondary market reports","note":"$1.05-1.5T implied valuation Aug-Sep 2026; +25%/month pace"},
 {"market":"IPO status","note":"Confidential S-1 filed Jun 1 2026; Nasdaq chosen; mid-Oct target; $2T banker talk; not confirmed"}
])
def sq(s): return s.replace("'","''")
r=d1(f"INSERT INTO rejected (id, ts_utc, market_url, category, thesis, reason, key_figures, my_est_yes, market_price_yes, side) VALUES ('{rej_id}', datetime('now'), '{market_url}', 'no-edge', '{sq(reasoning)}', '{sq(reasoning)}', '{sq(kf)}', 0.27, 0.285, 'YES')")
print(r.get('success'), json.dumps(r.get('result'))[:200])
srcs=[
 ("https://www.nasdaqprivatemarket.com/company/anthropic/","NPM price $729.87 as of Aug 19, 2026; Anthropic not yet public; no IPO price."),
 ("https://www.techtimes.com/articles/327492/20260914/anthropic-picks-nasdaq-2-trillion-ipo-trump-linked-compute-deal-tests-safety-mission.htm","Nasdaq picked; mid-Oct listing target; bankers float ~$2T; secondary $1.05-1.15T; nothing confirmed."),
 ("https://www.businessinsider.com/anthropic-1-5-trillion-valuation-on-secondary-markets-2026-8","Secondary trades implied up to $1.5T, +25% in a month; shares extremely scarce."),
 ("https://www.cnbc.com/2026/09/14/anthropic-walks-tightrope-to-nasdaq-pushing-slowdown-and-pursuing-ipo.html","Pursuing $2T valuation; listed as soon as October; timing and valuation not confirmed.")
]
for u,f in srcs:
    d1(f"INSERT INTO sources (rejected_id, url, fact) VALUES ('{rej_id}','{u}','{sq(f)}')")
    print("src",u)
print("logged",rej_id)
