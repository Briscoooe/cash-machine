import json, os, sys
sys.path.insert(0,'/root/cash-machine/runtime/db')
import d1cli
d1 = d1cli.d1

wid = "W21-MUSK-SEP15-22"
q = "Elon Musk tweets Sep 15 - Sep 22: expected bin 200-239"
sql = ("INSERT INTO watchlist (id, question, slug, current_price, watch_price, direction, thesis_seed, catalyst, catalyst_date, status) "
 "VALUES ('%s', '%s', 'elon-musk-of-tweets-september-15-september-22-2026', 0.39, 0.55, 'YES', "
 "'Tracker counts 56 Musk posts in the Sep 14-16 window by 06:23 UTC Sep 16. Six-day hourly history shows the 02:00-12:00 ET block averages 12 posts and 20:00-00:59 ET averages 15. Extrapolation puts the Sep 15-22 week near 220-240, but the bin edge is inside one day of noise. Historical resolution prices held fair; no edge to trade now.', "
 "'Check cumulative count on Sep 18 and Sep 20; revisit if the count runs 8 or more posts below the 220 pace line', '2026-09-22', 'watching')")
print(json.dumps(d1(sql)))
