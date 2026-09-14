#!/usr/bin/env python3
"""Send one Telegram message bubble via the Hermes bot — cash-machine copy.

Usage:
  python3 cash_bubble.py "message text"
Env: HERMES_CHAT_ID (default: -5339752056, the Cash machine group)
"""
import re, sys, os, urllib.request, urllib.parse

def token():
    m = re.search(r'[0-9]{8,12}:AA[A-Za-z0-9_-]{30,}', open(os.path.expanduser('~/.hermes/.env')).read())
    if not m:
        raise SystemExit("no bot token found in ~/.hermes/.env")
    return m.group(0)

def send(text, chat_id=None):
    chat_id = chat_id or os.environ.get("HERMES_CHAT_ID", "-5339752056")
    data = urllib.parse.urlencode({"chat_id": chat_id, "text": text}).encode()
    r = urllib.request.urlopen(urllib.request.Request(
        f"https://api.telegram.org/bot{token()}/sendMessage", data=data))
    assert r.status == 200, r.status

if __name__ == "__main__":
    text = sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read()
    stripped = text.lstrip()
    # Chat carries ONLY buy/sell activity. Anything else is refused at the source.
    if not (stripped.startswith("BUY") or stripped.startswith("CLOSE")):
        raise SystemExit("REFUSED: chat bubbles are for BUY/CLOSE only — not for: " + text[:80])
    send(text)