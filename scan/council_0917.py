import json, urllib.request, time
KEY=[l.split("=",1)[1].strip() for l in open("/root/.hermes/.env") if l.startswith("OPENROUTER_API_KEY=")][0]
MODELS=["openai/gpt-6-astra","anthropic/claude-fable-5.1"]
PAYLOAD=open("/tmp/council_payload.txt").read()
PROMPT=("You are reviewing a proposed prediction-market trade for correctness. Given the evidence below "
        "(verify the reasoning, not just plausibility), respond with: VERDICT: APPROVE or REJECT, "
        "CONFIDENCE: 1-10, and 2-3 sentences of reasoning. Flag any source that does not support the claim.\n\n"+PAYLOAD)
out={}
for m in MODELS:
    body={"model":m,"messages":[{"role":"user","content":PROMPT}],"max_tokens":2000}
    req=urllib.request.Request("https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(body).encode(),
        headers={"Authorization":"Bearer "+KEY,"Content-Type":"application/json"})
    try:
        r=json.loads(urllib.request.urlopen(req,timeout=120).read())
        out[m]={"content":r["choices"][0]["message"]["content"],"id":r.get("id"),"usage":r.get("usage")}
    except Exception as e:
        out[m]={"error":str(e)}
    time.sleep(1)
json.dump(out,open("/tmp/council_out.json","w"),indent=1)
for m,v in out.items():
    print("==",m)
    print(v.get("content") or v.get("error"))
    print("id:",v.get("id"))
