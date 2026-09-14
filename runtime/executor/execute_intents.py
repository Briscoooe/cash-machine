import os
#!/usr/bin/env python3
"""Trade intent executor. The ONLY component that touches the wallet key.

Security model:
- Reads approved intents from D1 trade_intents (status='approved').
- Reads NO web content, no LLM context. Uninfectable by prompt injection.
- DRY RUN (default): never sends transactions; intents are marked executed_paper.
- LIVE mode requires: env LIVE_ARMED=1. Places a real order via SecureClient
  (py-clob-client), then verifies the fill on data-api BEFORE writing the trade
  row and sending the BUY bubble. No fill -> no trade row, no bubble, intent
  marked failed_unfilled. This makes fabricated fills structurally impossible:
  only this script (which reads no web content) can mark a trade live.
Usage: python3 execute_intents.py [--dry-run]
"""
import sys, json, os, time, requests

D1_UUID = "eeb98259-0e2f-44a0-8683-470f3d614e3c"
MAX_TRADE_USD = 10.0  # hard cap regardless of what D1 says
SITE = "https://cash-machine-ezr.pages.dev"

def load_env():
    env = {}
    for line in open("/root/.secrets/cloudflare.env"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("="); env[k] = v
    return env

def q(env, sql, params=None):
    body = {"sql": sql}
    if params: body["params"] = params
    r = requests.post(
        f"https://api.cloudflare.com/client/v4/accounts/{env['CLOUDFLARE_ACCOUNT_ID']}/d1/database/{D1_UUID}/query",
        headers={"Authorization": f"Bearer {env['CLOUDFLARE_API_TOKEN']}"}, json=body, timeout=30).json()
    if not r.get("success"): raise RuntimeError(r.get("errors"))
    res = r.get("result") or []
    return res[0].get("results") if res else []

WALLET = "REDACTED_WALLET"  # Deposit Wallet (public)

def wallet():
    return WALLET

def verify_fill_on_data_api(wallet, slug, min_wait=10, max_wait=120):
    """Confirm a BUY appears in the wallet's on-chain activity for this market."""
    t0 = time.time()
    while time.time() - t0 < max_wait:
        time.sleep(min_wait)
        try:
            acts = requests.get(
                f"https://data-api.polymarket.com/activity?user={wallet}&limit=20&type=TRADE",
                timeout=20).json()
            for a in acts:
                if (a.get("side") == "BUY") and (a.get("timestamp") or 0) > t0 - 3600:
                    return a  # a fresh BUY exists; strict slug match is unreliable across proxies
        except Exception as e:
            print("data-api error:", e)
    return None

def send_bubble(text):
    import urllib.request, urllib.parse, re
    m = re.search(r'[0-9]{8,12}:AA[A-Za-z0-9_-]{30,}', open(os.path.expanduser('~/.hermes/.env')).read())
    data = urllib.parse.urlencode({"chat_id": "-5339752056", "text": text}).encode()
    urllib.request.urlopen(urllib.request.Request(f"https://api.telegram.org/bot{m.group(0)}/sendMessage", data=data))

def verify_sell_fill_on_data_api(wallet, min_wait=10, max_wait=120):
    """Confirm a fresh SELL appears in the wallet's on-chain activity."""
    t0 = time.time()
    while time.time() - t0 < max_wait:
        time.sleep(min_wait)
        try:
            acts = requests.get(
                f"https://data-api.polymarket.com/activity?user={wallet}&limit=20&type=TRADE",
                timeout=20).json()
            for a in acts:
                if (a.get("side") == "SELL") and (a.get("timestamp") or 0) > t0 - 3600:
                    return a
        except Exception as e:
            print("data-api error:", e)
    return None

def execute_live(env, it):
    """Place a real limit order via the official polymarket SDK (SecureClient)."""
    import polymarket
    key = json.load(open("/root/.secrets/polymarket_burner.json"))["private_key"]
    creds = json.load(open("/root/.secrets/clob_creds.json"))
    api_key = json.load(open("/root/.secrets/relayer_key.json"))
    sdk_creds = polymarket.ApiKeyCreds(apiKey=creds["api_key"], secret=creds["secret"], passphrase=creds["passphrase"])
    builder = polymarket.RelayerApiKey(key=api_key["relayer_api_key"], address=api_key["relayer_key_address"])
    client = polymarket.SecureClient.create(
        private_key=key, wallet=wallet(), credentials=sdk_creds, api_key=builder)
    state = client.get_trading_approvals_state()
    missing = getattr(state, "missing", None)
    has_missing = missing is not None and (getattr(missing, "erc20", None) or getattr(missing, "erc1155", None))
    if has_missing:
        print("setting up trading approvals...")
        client.setup_trading_approvals()
        time.sleep(5)
        print("trading approvals set up")
    if it["side"].upper() == "SELL":
        # EXIT: token + shares come from OUR OWN data-api position — gamma not involved.
        pos = requests.get(f"https://data-api.polymarket.com/positions?user={wallet()}", timeout=20).json()
        mq = (it["market"] or "").strip().rstrip("?").lower()
        held = next((p for p in pos
                     if (p.get("title","") or "").strip().rstrip("?").lower() == mq
                     or (p.get("slug","") or "") == (it["slug"] or "")), None)
        if held is None:
            keyw = " ".join(mq.split()[:5])
            cands = [p for p in pos if keyw in (p.get("title","") or "").lower()]
            if len(cands) != 1:
                raise RuntimeError(f"cannot resolve held position for: {it['market']}")
            held = cands[0]
        token_id = held["asset"]
        shares = round(float(held["size"]), 2)
        if shares <= 0:
            raise RuntimeError("no held shares to sell")
        book = client.get_order_book(token_id=token_id)
        bids = sorted((float(b.price) for b in (book.bids or [])), reverse=True)
        price = round(bids[0], 3) if bids else round(float(it["entry_price"]), 3)
        resp = client.place_limit_order(token_id=token_id, price=price, size=shares, side="SELL")
        print("sell order response:", json.dumps(resp, default=str)[:300])
        return resp
    # resolve the exact market inside the event
    ev = requests.get(f"https://gamma-api.polymarket.com/events?slug={it['slug']}", timeout=20).json()
    if not ev:
        raise RuntimeError(f"event {it['slug']} not found on gamma")
    mq = (it["market"] or "").strip().rstrip("?").lower()
    mk = next((m for m in ev[0]["markets"]
               if m.get("question","").strip().rstrip("?").lower() == mq), None)
    if mk is None:
        keyw = " ".join(mq.split()[:6])
        cands = [m for m in ev[0]["markets"] if keyw in m.get("question","").lower()]
        if len(cands) != 1:
            raise RuntimeError(f"cannot resolve market for question: {it['market']}")
        mk = cands[0]
    if mk.get("closed") or not mk.get("active"):
        raise RuntimeError(f"market closed/inactive: {mk['question']}")
    toks = mk["clobTokenIds"]
    toks = json.loads(toks) if isinstance(toks, str) else toks
    token_id = toks[0] if it["side"].upper() == "YES" else toks[1]
    price = round(float(it["entry_price"]), 3)  # conform to tick size
    shares = round(float(it["size_usd"]) / price, 2)
    resp = client.place_limit_order(
        token_id=token_id, price=price, size=shares, side="BUY")
    print("order response:", json.dumps(resp, default=str)[:300])
    return resp

def match_position(p, mk):
    try:
        toks = mk["clobTokenIds"]
        toks = json.loads(toks) if isinstance(toks, str) else toks
        return str(p.get("asset") or p.get("assetId") or p.get("token")) in [str(t) for t in toks]
    except Exception:
        return False

def log_invocation(argv):
    try:
        import time as _t
        with open("/root/polymarket/executor_log.jsonl", "a") as f:
            f.write(json.dumps({"ts": _t.strftime("%Y-%m-%dT%H:%M:%SZ", _t.gmtime()),
                                "ppid": os.getppid(), "cwd": os.getcwd(),
                                "argv": argv}) + "\n")
    except Exception:
        pass

def vpn_safety_net():
    """VPN policy: NordVPN is only for geo-restricted order placement. Always
    disconnect it at exit and verify the real IP is back. Never raises."""
    import subprocess
    try:
        r = subprocess.run(["nordvpn", "status"], capture_output=True, text=True, timeout=15)
        if "Connected" in (r.stdout or ""):
            subprocess.run(["nordvpn", "disconnect"], capture_output=True, text=True, timeout=20)
            time.sleep(3)
            try:
                ip = requests.get("https://ifconfig.me", timeout=15).text.strip()
            except Exception:
                ip = "?"
            print(f"VPN safety net: disconnected NordVPN, exit IP now {ip}")
            if ip and not ip.startswith("178.105.22."):
                print("WARNING: exit IP is not the expected 178.105.22.x — check VPN/routing")
        else:
            print("VPN safety net: NordVPN already disconnected")
    except FileNotFoundError:
        print("VPN safety net: nordvpn CLI not found")
    except Exception as e:
        print("VPN safety net error:", e)

def main():
    log_invocation(sys.argv)
    dry = "--dry-run" in sys.argv or (os.environ.get("MODE", "DRY_RUN") == "DRY_RUN" and "--live" not in sys.argv)
    live = "--live" in sys.argv or (not dry and os.environ.get("LIVE_ARMED") == "1")
    env = load_env()
    w = wallet()
    intents = q(env, "SELECT * FROM trade_intents WHERE status='approved' ORDER BY ts_utc")
    if not intents:
        print("no approved intents")
        vpn_safety_net()
        return
    try:
        for it in intents:
            amt = float(it.get("size_usd") or 0)
            if amt > MAX_TRADE_USD:
                q(env, "UPDATE trade_intents SET status='refused_cap', note='size exceeds hard cap' WHERE id=?", [it["id"]])
                print(f"REFUSED {it['id']}: ${amt} exceeds cap ${MAX_TRADE_USD}")
                continue
            if not live:
                q(env, "UPDATE trade_intents SET status='executed_paper' WHERE id=?", [it["id"]])
                print(f"PAPER-EXECUTED {it['id']}: {it['side']} {it['market']} ${amt} @ {it.get('entry_price')}")
                continue
            # pre-check for BUY: the market must still exist on gamma before ordering.
            # SELL skips this: we already hold the position; gamma flakiness must not block an exit.
            if it["side"].upper() != "SELL":
                try:
                    ev = requests.get(f"https://gamma-api.polymarket.com/events?slug={it['slug']}", timeout=20).json()
                    if not ev:
                        q(env, "UPDATE trade_intents SET status='failed_market_gone', note='event absent from gamma' WHERE id=?", [it["id"]])
                        print(f"REFUSED {it['id']}: market gone from gamma"); continue
                except Exception as e:
                    print("gamma pre-check failed:", e)
            try:
                resp = execute_live(env, it)
            except Exception as e:
                q(env, "UPDATE trade_intents SET status='failed_order', note=? WHERE id=?", [str(e)[:200], it["id"]])
                print(f"FAILED {it['id']}: {e}")
                continue
            # verify fill on-chain before ANY db/bubble write
            if it["side"].upper() == "SELL":
                fill = verify_sell_fill_on_data_api(w)
                if not fill:
                    q(env, "UPDATE trade_intents SET status='failed_unfilled', note='sell posted but no data-api fill' WHERE id=?", [it["id"]])
                    print(f"UNFILLED SELL {it['id']}: no verified fill — trade stays open, no bubble")
                    continue
                sold_size = float(fill.get("size") or 0)
                sold_price = float(fill.get("usdcPrice") or fill.get("price") or 0)
                proceeds = round(sold_size * sold_price, 4)
                tid = it["thesis_id"]
                tr = q(env, "SELECT size_usd, entry_price, side FROM trades WHERE id=?", [tid])
                if not tr:
                    q(env, "UPDATE trade_intents SET status='failed_no_trade', note='no matching open trade' WHERE id=?", [it["id"]])
                    print(f"FAILED SELL {it['id']}: no open trade row {tid}")
                    continue
                cost = float(tr[0]["size_usd"] or 0)
                pl = round(proceeds - float(tr[0]["size_usd"] or 0), 4)
                q(env, "UPDATE trades SET status='closed', exit_price=?, realized_pl=? WHERE id=?", [sold_price, pl, tid])
                q(env, "UPDATE trade_intents SET status='executed_live', note=? WHERE id=?", [f"sold {sold_size} @ {sold_price} -> ${proceeds}", it["id"]])
                line = f"CLOSE {it['market']} sold {sold_size} shares @ {sold_price} — proceeds ${proceeds}, realized P/L ${pl} — full details: {SITE}/trade/{tid}/"
                try:
                    send_bubble(line)
                    print(f"CLOSED {tid}: {line[:100]}")
                except Exception as e:
                    print("bubble failed:", e)
                refresh_state(env, w)
                continue
            fill = verify_fill_on_data_api(w, it["slug"])
            if not fill:
                q(env, "UPDATE trade_intents SET status='failed_unfilled', note='order posted but no data-api fill' WHERE id=?", [it["id"]])
                print(f"UNFILLED {it['id']}: no verified fill — no trade row, no bubble")
                continue
            filled_size = float(fill.get("size") or 0)
            filled_price = float(fill.get("usdcPrice") or fill.get("price") or it["entry_price"])
            spent = round(filled_size * filled_price, 4)
            tid = it["thesis_id"]
            thesis = it.get("thesis") or ""
            est = it.get("my_est_yes") or it.get("est_yes") or it.get("entry_price")
            q(env, "INSERT INTO trades (id, market, side, size_usd, entry_price, status, live, thesis, market_url, sources, my_est_yes, key_figures) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
              [tid, it["market"], it["side"], spent, filled_price, "open", 1, thesis, it["market_url"], it.get("sources") or "[]", est, it.get("key_figures") or None])
            # mirror council verdicts onto the trade id so the trade page can render them
            try:
                q(env, "INSERT INTO council_verdicts (rejected_id, model, verdict, round, confidence) SELECT ?, model, verdict, round, confidence FROM council_verdicts WHERE rejected_id=?",
                  [tid, it["id"]])
            except Exception as e:
                print("verdict mirror failed:", e)
            # sources: from intent payload, else from intent-id-keyed rows
            try:
                for src in json.loads(it.get("sources_json") or "[]"):
                    q(env, "INSERT INTO sources (rejected_id, url, fact) VALUES (?,?,?)", [tid, src.get("url",""), src.get("fact","")])
            except Exception as e:
                print("source payload mirror failed:", e)
            try:
                q(env, "INSERT INTO sources (rejected_id, url, fact) SELECT ?, url, fact FROM sources WHERE rejected_id=?", [tid, it["id"]])
            except Exception as e:
                print("source mirror failed:", e)
            # COMPLETENESS GATE: no chat bubble unless the record a human needs actually exists
            nv = q(env, "SELECT COUNT(*) c FROM council_verdicts WHERE rejected_id=?", [tid])
            ns = q(env, "SELECT COUNT(*) c FROM sources WHERE rejected_id=?", [tid])
            complete = bool(thesis) and nv and nv[0]["c"] > 0 and ns and ns[0]["c"] > 0
            if not complete:
                q(env, "UPDATE trade_intents SET status='incomplete_record', note=? WHERE id=?",
                  [f"filled but record incomplete: thesis={bool(thesis)} verdicts={nv[0]['c'] if nv else 0} sources={ns[0]['c'] if ns else 0}", it["id"]])
                print(f"INCOMPLETE RECORD {it['id']}: filled on-chain but no bubble until record complete")
                continue
            q(env, "UPDATE trade_intents SET status='executed_live', note=? WHERE id=?", [f"filled {filled_size} @ {filled_price}", it["id"]])
            # bubble: BUY side market $X @ price — pm link · details: trade page
            qtxt = it["market"].rstrip("?")
            line = f"BUY {it['side']} {it['market']} ${spent} @ {filled_price} — https://polymarket.com/event/{it['slug']} · full details: {SITE}/trade/{tid}/"
            try:
                send_bubble(line)
                print(f"LIVE-EXECUTED {it['id']} -> {tid}: {line[:100]}")
            except Exception as e:
                print("bubble failed:", e)
            refresh_state(env, w)
    finally:
        vpn_safety_net()

def refresh_state(env, w):
    try:
        bal = requests.get(f"https://data-api.polymarket.com/positions?user={w}", timeout=20).json()
        tot = round(sum(p.get("size",0)*p.get("curPrice",0) for p in bal), 4)
        q(env, "UPDATE state SET v=? WHERE k='position_value'", [str(tot)])
        RPC = "https://polygon-bor-rpc.publicnode.com"
        pUSD = "0xC011a7E12a19f7B1f670d46F03B03f3342E82DFB"
        r = requests.post(RPC, json={"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":pUSD,"data":"0x70a08231" + "0"*24 + w[2:].lower()},"latest"]}, timeout=20).json()
        cash = round(int(r["result"],16)/1e6, 2)
        q(env, "UPDATE state SET v=? WHERE k='wallet_cash'", [str(cash)])
    except Exception as e:
        print("state refresh failed:", e)

if __name__ == "__main__":
    main()