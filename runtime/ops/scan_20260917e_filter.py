import json
d = json.load(open("/root/cash-machine/runtime/ops/scan_20260917e_cands.json"))
cands = d["cands"]
skip = ["cs2","wta-","atp-","itf-","crint","nfl","nba","counter-strike"]
seen_slugs = ["hormuz","bab-el-mandeb","musk","brazil-presidential","los-angeles-mayoral","clarity-act","saudi-oil-pipeline","next-prime-minister-of-sweden","which-party-will-gain-most-seats","fed-decision","iranian-blockade","will-china-invade-taiwan","aliens-exist","wti","ballon"]
n=0
for c in cands:
    q = c["question"].lower(); s = c["slug"].lower()
    if any(k in s or k in q for k in skip): continue
    if any(k in s for k in seen_slugs): continue
    if c["vol24"] < 5000: continue
    n+=1
    if n>40: break
    print("%.3f | %s | %s | v24 %d | end %s" % (c["yes"], c["question"][:95], c["slug"][:55], c["vol24"], c["end"]))
