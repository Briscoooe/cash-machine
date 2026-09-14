#!/bin/bash
source /root/.secrets/cloudflare.env
URL="https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_ACCOUNT_ID/d1/database/eeb98259-0e2f-44a0-8683-470f3d614e3c/query"
JSON=$(python3 - "$1" <<'EOF'
import json,sys
print(json.dumps({"sql": sys.argv[1]}))
EOF
)
curl -s "$URL" -X POST -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" -H "Content-Type: application/json" --data "$JSON"
