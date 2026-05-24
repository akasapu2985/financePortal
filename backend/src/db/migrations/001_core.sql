CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE IF NOT EXISTS instruments (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(16) NOT NULL UNIQUE,
    name TEXT NOT NULL,
    type VARCHAR(16) NOT NULL DEFAULT 'stock',
    sector TEXT,
    is_owned BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS prices_intraday (
    time TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(16) NOT NULL,
    open NUMERIC(12, 4),
    high NUMERIC(12, 4),
    low NUMERIC(12, 4),
    close NUMERIC(12, 4),
    volume BIGINT,
    PRIMARY KEY (symbol, time)
);
SELECT create_hypertable('prices_intraday', 'time', if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS idx_prices_intraday_symbol_time_desc
    ON prices_intraday (symbol, time DESC);

CREATE TABLE IF NOT EXISTS prices_daily (
    time TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(16) NOT NULL,
    open NUMERIC(12, 4),
    high NUMERIC(12, 4),
    low NUMERIC(12, 4),
    close NUMERIC(12, 4),
    volume BIGINT,
    PRIMARY KEY (symbol, time)
);
SELECT create_hypertable('prices_daily', 'time', if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS idx_prices_daily_symbol_time_desc
    ON prices_daily (symbol, time DESC);
