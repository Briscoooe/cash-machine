import json
out = json.load(open("/root/cash-machine/scan_events.json"))
bad = ["lol","counter-strike","map ","rounds","odds","spread","o/u","moneyline","ballon","valencia",
       "lions vs","bills","tennis","atp","wta","darts","snooker","mbl","cs2","starladder","lpl",
       "league of legends","esports","world cup","copa","serie a","la liga","bundesliga","seria",
       "grand slam","wimbledon","us open","pga","nascar","premier","efl","mls","nhl","nba","nfl",
       "cfb","ncaa","fights","ufc","boxing","f1","gp","motogp","olympic","esl","valorant","dota",
       "pubg","rocket league","rlcs","fifa","uefa","concacaf","pitcher","quarterback","touchdown",
       "scores","points","yards","goals","strokes","winner (","beat ","vs."," vs ", " total ", "handicap"]
res = [o for o in out if not any(b in o["q"].lower() for b in bad) and o["end"] and o["end"] <= "2026-12-31"]
print(len(res))
for o in res:
    print(o["yes"], o["end"], o["q"][:110])
