-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Instruments (stocks we track)
CREATE TABLE IF NOT EXISTS instruments (
  id SERIAL PRIMARY KEY,
  symbol VARCHAR(10) NOT NULL UNIQUE,
  name VARCHAR(255),
  sector VARCHAR(100),
  exchange VARCHAR(50),
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Watchlists
CREATE TABLE IF NOT EXISTS watchlists (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  description TEXT,
  is_default BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Watchlist items (many-to-many)
CREATE TABLE IF NOT EXISTS watchlist_items (
  watchlist_id INTEGER REFERENCES watchlists(id) ON DELETE CASCADE,
  instrument_id INTEGER REFERENCES instruments(id) ON DELETE CASCADE,
  added_at TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (watchlist_id, instrument_id)
);

-- Intraday prices (TimescaleDB hypertable)
CREATE TABLE IF NOT EXISTS prices_intraday (
  time TIMESTAMPTZ NOT NULL,
  instrument_id INTEGER NOT NULL REFERENCES instruments(id),
  open NUMERIC(12,4),
  high NUMERIC(12,4),
  low NUMERIC(12,4),
  close NUMERIC(12,4),
  volume BIGINT,
  PRIMARY KEY (time, instrument_id)
);
SELECT create_hypertable('prices_intraday', 'time', if_not_exists => true);

-- Daily prices (TimescaleDB hypertable)
CREATE TABLE IF NOT EXISTS prices_daily (
  time TIMESTAMPTZ NOT NULL,
  instrument_id INTEGER NOT NULL REFERENCES instruments(id),
  open NUMERIC(12,4),
  high NUMERIC(12,4),
  low NUMERIC(12,4),
  close NUMERIC(12,4),
  volume BIGINT,
  adj_close NUMERIC(12,4),
  PRIMARY KEY (time, instrument_id)
);
SELECT create_hypertable('prices_daily', 'time', if_not_exists => true);

-- Indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_prices_intraday_instrument ON prices_intraday(instrument_id, time DESC);
CREATE INDEX IF NOT EXISTS idx_prices_daily_instrument ON prices_daily(instrument_id, time DESC);
