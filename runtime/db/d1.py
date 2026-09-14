import json, os, urllib.request

DB = "eeb98259-0e2f-44a0-8683-470f3d614e3c"
ACC = os.environ["CLOUDFLARE_ACCOUNT_ID"]
TOK = os.environ["CLOUDFLARE_API_TOKEN"]

def d1(sql):
    req = urllib.request.Request(
        f"https://api.cloudflare.com/client/v4/accounts/{ACC}/d1/database/{DB}/query",
        data=json.dumps({"sql": sql}).encode(),
        headers={"Authorization": f"Bearer {TOK}", "Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

if __name__ == "__main__":
    import sys
    for sql in sys.argv[1:]:
        print(json.dumps(d1(sql)))
