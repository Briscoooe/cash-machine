import json
cands = json.load(open("/root/polymarket/scan_20260916.json"))
bad2 = ["spread", "innings", "map ", "set 1", "set 2", "total rounds", "o/u",
        "moneyline", "handicap", "match:", "completed match", "rounds",
        "1st 5", "total sets", "prop", "goals", "corners", "cards", "winner:",
        "vs.", " vs ", "series score", "grand slam", "ace", "strokes",
        "each way", "top 5", "top 10", "podium", "stage winner", "points",
        "laliga", "la liga", "tournament winner", "outright", "to win",
        "next prime", "next fifa", "division", "relegation", "promoted",
        "title race", "group stage"]
filt = []
for c in cands:
    low = c["q"].lower()
    if any(b in low for b in bad2):
        continue
    end = c["end"][:10]
    if end and (end < "2026-09-17" or end > "2027-01-15"):
        continue
    filt.append(c)
print(len(filt), "after filter")
for c in filt[:60]:
    print(round(c["yes"], 3), "|", c["end"][:10], "|", (c["vol24"] or 0) and round(c["vol24"]), "|", c["q"][:120])
