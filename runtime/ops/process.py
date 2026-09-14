#!/usr/bin/env python3
"""Calibration + counterfactual + price-watch jobs for Polymarket dry run.

Usage:
  python3 process.py calibrate     # score resolved markets (Brier), update calibration table
  python3 process.py counterfactuals  # update counterfactual_pnl on rejected theses (live prices)
  python3 process.py postmortems   # write postmortem notes for resolved markets
  python3 process.py watch         # intraday price watch on open positions, alert on >15% moves
All read/write D1 directly. Designed to be called by cron, exit silently on nothing-to-do.
"""
import requests, json, datetime, sys, os, subprocess

SECRETS = "/root/.secrets/cloudflare.env"
D1META = "/root/.secrets/cashmachine_d1.json"
TELEGRAM = "/root/cash-machine/runtime/notify/cash_bubble.py"

env = {}
for line in open(SECRETS):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, _, v = line.partition("="); env[k] = v
cf, acct = env["CLOUDFLARE_API_TOKEN"], env["CLOUDFLARE_ACCOUNT_ID"]
uuid = json.load(open(D1META))["database_uuid"]
H = {"Authorization": f"Bearer {cf}", "Content-Type": "application/json"}

def q(sql, params=None):
    body = {"sql": sql}
    if params: body["params"] = params
    r = requests.post(f"https://api.cloudflare.com/client/v4/accounts/{acct}/d1/database/{uuid}/query",
        headers=H, json=body, timeout=60).json()
    if not r.get("success"): raise RuntimeError(f"D1: {r.get('errors')}")
    return r["result"][0]["results"]

def gamma_price(cid):
    r = requests.get(f"https://gamma-api.polymarket.com/markets?condition_ids={cid}", timeout=20).json()
    if not r: return None
    m = r[0]
    try: return float(json.loads(m["outcomePrices"])[0])
    except Exception: return None

def notify(msg):
    env = dict(os.environ, HERMES_CHAT_ID=os.environ.get("CASH_CHAT_ID", "-5339752056"))
    subprocess.run(["python3", TELEGRAM, msg], env=env, capture_output=True)

# ---------- calibration: score resolved markets ----------
def cmd_calibration():
    now = datetime.datetime.utcnow().isoformat()
    # unresolved calibration entries whose markets may have resolved
    rows = q("SELECT id, market, my_est, market_price, side, condition_id FROM calibration WHERE outcome IS NULL")
    if not rows: return print("calibration: nothing pending")
    # condition_id is embedded in rejected/trades rows; calibration rows carry it via market text for now
    done = 0
    for row in rows:
        cid = row.get("condition_id")
        if not cid: continue
        r = requests.get(f"https://gamma-api.polymarket.com/markets?condition_ids={cid}", timeout=20).json()
        if not r or not r[0].get("closed"): continue
        try: outcome = json.loads(r[0]["outcomePrices"])[0]
        except Exception: continue
        resolved_yes = float(outcome) > 0.5
        my = row["my_est"]; mp = row["market_price"]
        # Brier for the side I was estimating (YES prob)
        p = my if (my := (float(my) if isinstance(my := row["my_est"], (int, float)) else None)) else mp
        y = 1.0 if resolved_yes > 0.5 else 0.0
        brier = (p - y) ** 2
        q("UPDATE calibration SET outcome=?, brier=?, resolved_at=? WHERE id=?",
          ["YES" if y else "NO", brier, now, row["id"]])
    n = q("SELECT COUNT(*) c, AVG(brier) avg_b FROM calibration WHERE brier IS NOT NULL")
    print(f"calibration: scored; avg brier so far: {n}")

# ---------- counterfactuals: what rejected theses would be worth now ----------
def cmd_counterfactuals():
    rows = q("SELECT id, condition_id FROM rejected WHERE condition_id IS NOT NULL AND counterfactual_pnl IS NULL")
    if not rows: return print("counterfactuals: nothing to update")
    for row in rows:
        cid = row["condition_id"]
        r = requests.get(f"https://gamma-api.polymarket.com/markets?condition_ids={cid}", timeout=20).json()
        if not r: continue
        m = r[0]
        try: yes = float(json.loads(m["outcomePrices"])[0])
        except Exception: continue
        closed = m.get("closed")
        # counterfactual: $10 on the proposed side at market_price_yes at rejection time
        mp = q("SELECT market_price_yes, side FROM rejected WHERE id=?", [row["id"]])
        if not mp or mp[0]["market_price_yes"] is None: continue
        entry = float(mp[0]["market_price_yes"]); side = mp[0]["side"] or "YES"
        if not closed:
            # mark-to-market
            pnl = (yes - entry) / entry * 10 if (entry := entry if (entry := entry) else None) else None
        else:
            final = yes if side == "YES" else 1 - yes
            pnl = (final - entry) / entry * 10 if entry else None
            q("UPDATE rejected SET resolved_outcome=? WHERE id=?", ["YES" if yes > 0.5 else "NO", row["id"]])
        if pnl is not None:
            q("UPDATE rejected SET counterfactual_pnl=? WHERE id=?", [round(pnl, 2), row["id"]])
    print("counterfactuals updated")

# ---------- postmortems: note on resolved markets ----------
def cmd_postmortems():
    rows = q("SELECT id, thesis, resolved_outcome, my_est_yes FROM rejected WHERE resolved_outcome IS NOT NULL AND postmortem IS NULL")
    if not rows: return print("postmortems: nothing pending")
    for row in rows:
        est = row.get("my_est_yes") or "?"
        note = (f"Market resolved {row['resolved_outcome']}. My estimate at rejection: {est}. "
                f"Thesis: {row['thesis'][:150]}. "
                f"Lesson: compare resolved outcome vs my estimate to calibrate future calls.")
        q("UPDATE rejected SET postmortem=? WHERE id=?", [note, row["id"]])
    print("postmortems written")

# ---------- price watch: intraday alert on open positions ----------
def cmd_watch():
    rows = q("SELECT t.id, t.condition_id, t.side, t.entry_price, w.last_price, w.intraday_open, w.alert_sent "
             "FROM trades t LEFT JOIN price_watch w ON w.condition_id = t.condition_id "
             "WHERE t.status = 'open'")
    if not rows: return print("watch: no open positions")
    now = datetime.datetime.utcnow().isoformat()
    for row in rows:
        cid = row["condition_id"]
        r = requests.get(f"https://gamma-api.polymarket.com/markets?condition_ids={cid}", timeout=20).json()
        if not r: continue
        try: yes = float(json.loads(r[0]["outcomePrices"])[0])
        except Exception: continue
        open_px = row["intraday_open"] if row["intraday_open"] is not None else yes
        move = abs(yes - open_px) / max(open_px, 0.01)
        alert = move >= 0.15 and not row["alert_sent"]
        q("INSERT OR REPLACE INTO price_watch (condition_id, trade_id, last_price, last_check, intraday_open, alert_sent) VALUES (?,?,?,?,?,?)",
          [cid, row["id"], yes, now, open_px, 1 if alert else row["alert_sent"] or 0])
        if alert:
            notify(f"Polymarket price alert: {row['side']} position moved {move*100:.0f}% intraday — {yes:.0%} now vs {open_px:.0%} at last check. Market: {r[0].get('question','')[:80]}")
            print("ALERT:", cid[:12], move)
    print("watch complete")


# ---------- balance history: daily snapshot for time series ----------
def cmd_balance_history():
    today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    bal = q("SELECT k, v FROM state WHERE k IN ('paper_balance','wallet_cash','real_balance')")
    vals = {r["k"]: r["v"] for r in bal}
    if "wallet_cash" in vals:
        balance = float(vals.get("wallet_cash") or 0) + float(vals.get("real_balance") or 0)
    else:
        balance = float(vals["paper_balance"]) if "paper_balance" in vals else None
    open_rows = q("SELECT id, condition_id, side, entry_price, size_usd FROM trades WHERE status='open'")
    unreal = 0.0
    for row in open_rows:
        r = requests.get(f"https://gamma-api.polymarket.com/markets?condition_ids={row['condition_id']}", timeout=20).json()
        if not r: continue
        try: yes = float(json.loads(r[0]["outcomePrices"])[0])
        except Exception: continue
        px = yes if row["side"].upper().startswith("YES") else 1-yes
        unreal += (px - float(row["entry_price"])) * float(row["size_usd"])
    n_open = len(open_rows)
    total = (balance or 0) + unreal
    q("INSERT OR REPLACE INTO balance_history (date_utc, balance, unrealized_pl, total_value, open_positions) VALUES (?,?,?,?,?)",
      [today, balance, round(unreal,2), round(total,2), n_open])
    print(f"balance_history: {today} bal={balance} unreal={unreal:.2f} total={total:.2f} open={n_open}")



def cmd_watchlist():
    """Check watchlist entries: price moved to trigger level, or catalyst date arrived."""
    import requests, ast
    env = {}
    for line in open("/root/.secrets/cloudflare.env"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("="); env[k] = v
    H = {"Authorization": f"Bearer {env['CLOUDFLARE_API_TOKEN']}"}
    uuid = "eeb98259-0e2f-44a0-8683-470f3d614e3c"
    def q(sql, params=None):
        body = {"sql": sql}
        if params: body["params"] = params
        r = requests.post(f"https://api.cloudflare.com/client/v4/accounts/{env['CLOUDFLARE_ACCOUNT_ID']}/d1/database/{uuid}/query",
                          headers=H, json=body, timeout=30).json()
        return r["result"][0]["results"] if r.get("success") else None
    rows = q("SELECT * FROM watchlist WHERE status='watching'") or []
    from datetime import datetime, timezone; today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    def _nw(s):
        import unicodedata
        s = unicodedata.normalize("NFKD", s or "")
        s = "".join(c for c in s if c.isascii() and (c.isalnum() or c.isspace()))
        return set(t for t in s.lower().split() if len(t) > 3)
    for w in rows:
        try:
            g = requests.get(f"https://gamma-api.polymarket.com/events?slug={w['slug']}", timeout=20).json()
            m = {}
            if g:
                # multi-candidate events: match the watchlist question, never trust markets[0]
                qw = _nw(w.get("question") or "")
                best, bs = None, -1.0
                for cand in (g[0].get("markets") or []):
                    cw = _nw(cand.get("question") or "")
                    if not cw:
                        continue
                    sc = len(qw & cw) / max(1, len(qw | cw))
                    if sc > bs:
                        best, bs = cand, sc
                m = best if best is not None else (g[0].get("markets") or [{}])[0]
            yp = float(ast.literal_eval(m.get("outcomePrices", "[0,0]"))[0]) if m else None
        except Exception:
            yp = None
        trig = []
        if yp is not None and w["watch_price"] is not None:
            if w["direction"] == "YES" and yp <= w["watch_price"]: trig.append(f"price {yp} <= {w['watch_price']}")
            if w["direction"] == "NO" and yp >= w["watch_price"]: trig.append(f"price {yp} >= {w['watch_price']}")
        if w["catalyst_date"] and w["catalyst_date"] <= today:
            trig.append("catalyst date arrived")
        if trig:
            print(f"WATCHLIST TRIGGER {w['id']}: {', '.join(trig)} ({w['question']} @ {yp})")
            q("UPDATE watchlist SET status='triggered', current_price=? WHERE id=?", [yp, w["id"]])
        elif yp is not None and yp != w["current_price"]:
            q("UPDATE watchlist SET current_price=? WHERE id=?", [yp, w["id"]])
        else:
            print(f"watchlist {w['id']}: quiet @ {yp}")

if __name__ == "__main__":
    cmds = sys.argv[1:] or ["watch"]
    fns = {"calibration": cmd_calibration, "counterfactuals": cmd_counterfactuals,
           "postmortems": cmd_postmortems, "watch": cmd_watch, "balance_history": cmd_balance_history, "watchlist": cmd_watchlist}
    for c in cmds:
        fn = fns.get(c)
        if fn: fn()
        else: print(f"unknown subcommand: {c}")