# runtime/

Core Polymarket trading runtime scripts, moved from `/root/polymarket/` on 2026-09-14.

Only the core scripts live here. Data files and one-off scripts stay in `/root/polymarket/`
(`cash.db`, `costs.db`, `shadow_trades.json`, `executor_log.jsonl`, `backups/`, scan/rej/log one-offs, JSON dumps).
Scripts reach that data with absolute `/root/polymarket/...` paths, so they run from any cwd.

## Old → new

| Old (`/root/polymarket/`) | New (`/root/cash-machine/runtime/`) |
|---|---|
| `execute_intents.py` | `executor/execute_intents.py` |
| `d1.py` | `db/d1.py` |
| `d1_backup.py` | `db/d1_backup.py` |
| `d1cli.py` | `db/d1cli.py` |
| `d1p.py` | `db/d1p.py` |
| `d1q.sh` | `db/d1q.sh` |
| `d1x.sh` | `db/d1x.sh` |
| `/root/cash-machine/schema.sql` | `db/schema.sql` |
| `audit_trades.py` | `ops/audit_trades.py` |
| `audit_completeness.py` | `ops/audit_completeness.py` |
| `balance_update.py` | `ops/balance_update.py` |
| `process.py` | `ops/process.py` |
| `rearm.py` | `ops/rearm.py` |
| `housekeeping.sh` | `ops/housekeeping.sh` |
| `cash_bubble.py` | `notify/cash_bubble.py` |

The cron wrapper `~/.hermes/scripts/polymarket_housekeeping.sh` calls the `runtime/ops/` scripts.
The old copies in `/root/polymarket/` still exist for now but are not canonical.
