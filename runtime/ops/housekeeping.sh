#!/bin/bash
# No-LLM housekeeping: audits, balance refresh, process.py subcommands.
# Prints full output only if something needs review; otherwise a single OK line.
# Scripts live in /root/cash-machine/runtime/ops; data files stay in /root/polymarket.
cd /root/cash-machine
OUT=$(python3 runtime/ops/audit_trades.py 2>&1
python3 runtime/ops/audit_completeness.py 2>&1
python3 runtime/ops/balance_update.py 2>&1
python3 runtime/ops/process.py watch counterfactuals calibration postmortems balance_history watchlist 2>&1)
if echo "$OUT" | grep -qiE 'FAIL|FAKE|missing|incomplete|ALERT|trigger|move>|threshold|exceed'; then
  echo "HOUSEKEEPING_CHANGES"
  echo "$OUT"
else
  echo "HOUSEKEEPING_OK"
fi
