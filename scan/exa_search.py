#!/usr/bin/env python3
"""Exa search helper: python3 exa_search.py 'query' [n]"""
import json, os, sys, urllib.request

KEY = [l.split("=",1)[1].strip() for l in open("/root/.hermes/.env") if l.startswith("EXA_API_KEY=")][0]

def exa(query, n=5):
    body = {"query": query, "numResults": n, "contents": {"text": {"maxCharacters": 3000}}}
    req = urllib.request.Request("https://api.exa.ai/search",
        data=json.dumps(body).encode(),
        headers={"x-api-key": KEY, "Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

if __name__ == "__main__":
    r = exa(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 5)
    for res in r.get("results", []):
        print("URL:", res.get("url"))
        print("TITLE:", res.get("title"))
        txt = (res.get("text") or "")[:1200].replace("\n", " ")
        print("TEXT:", txt)
        print("---")
