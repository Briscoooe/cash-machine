#!/bin/bash
export $(grep -v '^#' /root/.secrets/cloudflare.env | xargs)
DB="https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_ACCOUNT_ID/d1/database/eeb98259-0e2f-44a0-8683-470f3d614e3c/query"
qs=(
"SELECT id,substr(market,1,70) m,status,entry_price FROM trade_intents ORDER BY rowid DESC LIMIT 5"
"SELECT id,substr(market,1,70) m,side,entry_price,status,live FROM trades ORDER BY rowid DESC LIMIT 10"
"SELECT id,substr(thesis,1,60) t,category,ts_utc FROM rejected ORDER BY ts_utc DESC LIMIT 5"
"SELECT id,substr(market,1,70) m,my_est_yes est,market_price_yes mp,side FROM rejected WHERE date(ts_utc)=date('now')"
)
for q in "${qs[@]}"; do
  echo "Q: $q"
  curl -s -X POST "$DB" -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" -H 'Content-Type: application/json' -d "{\"sql\":\"$q\"}"
  echo; echo ---
done
