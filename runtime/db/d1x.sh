#!/bin/bash
# usage: d1x.sh file-with-sql-json  -> runs statements from a JSON file {"sql": "..."}
source /root/.secrets/cloudflare.env
curl -s -X POST "https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_ACCOUNT_ID/d1/database/eeb98259-0e2f-44a0-8683-470f3d614e3c/query" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" -H "Content-Type: application/json" \
  --data-binary @"$1"
