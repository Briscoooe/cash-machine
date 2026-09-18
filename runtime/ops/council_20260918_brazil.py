import json, time, urllib.request, subprocess

key = None
for line in open('/root/.hermes/.env'):
    if line.startswith('OPENROUTER_API_KEY='):
        key = line.strip().split('=',1)[1]
assert key

PROMPT = """You are reviewing a proposed prediction-market trade for correctness. Given the evidence below (verify the reasoning, not just plausibility), respond with: VERDICT: APPROVE or REJECT, CONFIDENCE: 1-10, and 2-3 sentences of reasoning. Flag any source that does not support the claim.

MARKET (deadline in bold): **Brazil presidential election first round, October 4, 2026.**
Side: BUY NO on "Will Lula win the most votes in the first round of the 2026 Brazil presidential election?" — NO price 0.235. Equivalently YES on Flavio Bolsonaro finishing 2nd (also 0.235; the two markets are consistent mirrors).
Market implied P(Lula 1st) = 0.765. My estimate P(Lula 1st) = 0.60-0.65. Claimed edge ~12-16 points.

RESOLUTION: Most VALID votes in the first round, official results. Winner needs >50% valid votes or a runoff. No candidate reaches 50% in any poll, so this is purely Lula-vs-Flavio for first place.

EVIDENCE (all fetched 2026-09-17/18):
1. AtlasIntel/Bloomberg, field Sep 11-16, n=5018, MOE 1pt, TSE-registered BR-06221/2026 — https://www.gazetadopovo.com.br/eleicoes/2026/pesquisa-eleitoral-2026/atlasintel-presidente-setembro-2026-2/ : Lula 44.1, Flavio 41.7 (totals); valid votes Lula 45, Flavio 42.6. Flavio GREW +4.5 pts in one week; Lula -0.5. Runoff: Flavio 47.2 vs Lula 46.8 (tie).
2. Gerp, field Sep 14-16, n=2400, MOE 2pts — https://www.gazetadopovo.com.br/eleicoes/2026/pesquisa-eleitoral-2026/gerp-presidente-setembro-2026-2/ : valid votes FLAVIO 44 vs Lula 40 (Flavio leads); totals Flavio 40 vs Lula 37. Runoff Flavio 50 vs Lula 43.
3. MDA/CNT, field Sep 9-13, n=2002, MOE 2.2pts — https://mais.opovo.com.br/jornal/politica/2026/09/16/pesquisa-mda-lula-lidera-contra-flavio-bolsonaro-no-1-e-2-turnos.html : Lula 40.6, Flavio 30.4 (Lula +10.2). This is the outlier; field ended BEFORE the two above.
4. Prior rejection context (D1): 2026-09-16 "BUY YES Lula most-votes @ 0.445" was rejected as no-edge when polls led by 4-8 and market was 0.445. The market has SINCE repriced to 0.765 — the market has already absorbed the pro-Lula poll wave; price now sits ABOVE what the freshest polls support.

DECOMPOSITION: Poll mean gap (latest 2 institutes, freshest field): Lula +2.7pts on totals, but Gerp shows Flavio +3-4. Institute spread ~13pts => true gap highly uncertain. Historical 2022 first-round polling error ~5pts toward the Bolsonaro side. If Lula's true lead is ~0-3pts, P(Lula 1st) ~0.55-0.65; only if MDA-style +10 is real does 0.765 hold. Pace check: Flavio +4.5pts/week in Atlas would put him level or ahead by Oct 4.
Fair value NO = 0.35-0.40 vs price 0.235 => edge ~12-15pts. Under pace-continuation weighting (Flavio momentum continues), P(Lula 1st) drops below 0.55 and NO fair value exceeds 0.45.

COUNTERARGUMENTS: (a) MDA outlier supports 0.765 — but it is the OLDEST field and the only +10 result. (b) Market may know something polls do not — yet the reprice followed public polls, and Atlas shows momentum toward Flavio. (c) Undecideds/late deciders may break to the incumbent Lula."""
    
results = {}
for model in ["openai/gpt-6-astra", "anthropic/claude-fable-5.1"]:
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": PROMPT}],
        "max_tokens": 500,
    }).encode()
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    try:
        r = json.load(urllib.request.urlopen(req, timeout=120))
        results[model] = r
        print("=== ", model)
        print("gen id:", r.get("id"))
        print(r["choices"][0]["message"]["content"][:800])
        print("usage:", r.get("usage"))
    except Exception as e:
        print(model, "ERROR", e)
        results[model] = {"error": str(e)}
    time.sleep(2)
json.dump(results, open('/tmp/council_brazil.json','w'))
