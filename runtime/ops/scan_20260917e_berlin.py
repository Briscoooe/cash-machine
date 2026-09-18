import json
d = json.load(open("/root/cash-machine/runtime/ops/scan_20260917e_cands.json"))
for c in d["cands"]:
    if c["slug"] == "berlin-state-election-winner":
        print("Q:", c["question"], "| yes", c["yes"], "| end", c["end"])
        print("DESC:", c["desc"])
        print("----")
