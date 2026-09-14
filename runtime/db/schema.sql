-- Schema of D1 database 'cash-machine' (uuid eeb98259-0e2f-44a0-8683-470f3d614e3c)
-- Generated from live DB 2026-09-12. Recreate with: wrangler d1 execute cash-machine --file=schema.sql --remote

CREATE TABLE IF NOT EXISTS state (
  k TEXT PRIMARY KEY,
  v TEXT
);

CREATE TABLE IF NOT EXISTS trades (
  id TEXT PRIMARY KEY,
  ts_utc TEXT,
  market TEXT,
  side TEXT,
  size_usd REAL,
  entry_price REAL,
  status TEXT,
  sources TEXT,
  my_est_yes REAL,
  exit_price REAL,
  realized_pl REAL,
  condition_id TEXT,
  kelly_size REAL,
  market_url TEXT,
  live INTEGER,
  thesis TEXT,
  lesson TEXT,
  key_figures TEXT,
  council_cost_usd REAL
);

CREATE TABLE IF NOT EXISTS rejected (
  id TEXT PRIMARY KEY,
  ts_utc TEXT,
  thesis TEXT,
  decision TEXT,
  council_cost_usd REAL,
  my_est_yes TEXT,
  proposed_price REAL,
  market_price_yes REAL,
  reason TEXT,
  lesson TEXT,
  side TEXT,
  category TEXT,
  counterfactual_pnl REAL,
  resolved_outcome TEXT,
  postmortem TEXT,
  condition_id TEXT,
  market_url TEXT,
  key_figures TEXT
);

CREATE TABLE IF NOT EXISTS council_runs (
  ts_utc TEXT,
  trigger TEXT,
  model TEXT,
  generation_id TEXT,
  cost_usd REAL
);

CREATE TABLE IF NOT EXISTS daily_totals (
  date_utc TEXT PRIMARY KEY,
  total_cost_usd REAL,
  run_count INTEGER
);

CREATE TABLE IF NOT EXISTS sources (
  id INTEGER PRIMARY KEY,
  rejected_id TEXT,
  url TEXT,
  fact TEXT
);

CREATE TABLE IF NOT EXISTS council_verdicts (
  id INTEGER PRIMARY KEY,
  rejected_id TEXT,
  model TEXT,
  verdict TEXT,
  confidence INTEGER,
  generation_id TEXT,
  cost_usd REAL,
  reasoning TEXT
);

CREATE TABLE IF NOT EXISTS market_snapshots (
  id INTEGER PRIMARY KEY,
  ts_utc TEXT,
  condition_id TEXT,
  question TEXT,
  yes_price REAL,
  volume REAL,
  end_date TEXT
);

CREATE TABLE IF NOT EXISTS calibration (
  id INTEGER PRIMARY KEY,
  ts_utc TEXT,
  market TEXT,
  my_est REAL,
  market_price REAL,
  side TEXT,
  outcome TEXT,
  brier REAL,
  resolved_at TEXT,
  condition_id TEXT
);

CREATE TABLE IF NOT EXISTS price_watch (
  condition_id TEXT PRIMARY KEY,
  trade_id TEXT,
  last_price REAL,
  last_check TEXT,
  intraday_open REAL,
  alert_sent INTEGER
);

CREATE TABLE IF NOT EXISTS balance_history (
  date_utc TEXT PRIMARY KEY,
  balance REAL,
  unrealized_pl REAL,
  total_value REAL,
  open_positions INTEGER
);

CREATE TABLE IF NOT EXISTS watchlist (
  id TEXT PRIMARY KEY,
  ts_utc TEXT,
  market TEXT,
  question TEXT,
  slug TEXT,
  current_price REAL,
  watch_price REAL,
  direction TEXT,
  thesis_seed TEXT,
  catalyst TEXT,
  catalyst_date TEXT,
  status TEXT,
  notes TEXT
);

CREATE TABLE IF NOT EXISTS trade_intents (
  id TEXT PRIMARY KEY,
  ts_utc TEXT,
  market TEXT,
  side TEXT,
  size_usd REAL,
  entry_price REAL,
  slug TEXT,
  market_url TEXT,
  thesis_id TEXT,
  council_run_id TEXT,
  user_approval_ref TEXT,
  status TEXT,
  note TEXT
);

CREATE TABLE IF NOT EXISTS injection_log (
  id TEXT PRIMARY KEY,
  ts_utc TEXT,
  url TEXT,
  excerpt TEXT
);
