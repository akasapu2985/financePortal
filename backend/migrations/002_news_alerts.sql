-- News articles
CREATE TABLE IF NOT EXISTS news (
  id SERIAL PRIMARY KEY,
  instrument_id INTEGER REFERENCES instruments(id),
  headline TEXT NOT NULL,
  summary TEXT,
  source VARCHAR(100),
  url TEXT UNIQUE,
  image_url TEXT,
  category VARCHAR(50),
  sentiment_score NUMERIC(5,4),  -- -1.0 to 1.0
  published_at TIMESTAMPTZ,
  collected_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_news_instrument ON news(instrument_id, published_at DESC);
CREATE INDEX IF NOT EXISTS idx_news_published ON news(published_at DESC);

-- SEC Filings (for Phase 4, schema ready)
CREATE TABLE IF NOT EXISTS filings (
  id SERIAL PRIMARY KEY,
  instrument_id INTEGER REFERENCES instruments(id),
  filing_type VARCHAR(20) NOT NULL,  -- '4', '8-K', '10-K', '10-Q'
  filer_name VARCHAR(255),
  title TEXT,
  url TEXT UNIQUE,
  filed_at TIMESTAMPTZ,
  collected_at TIMESTAMPTZ DEFAULT NOW()
);

-- Sentiment scores (aggregated from social media)
CREATE TABLE IF NOT EXISTS sentiment (
  id SERIAL PRIMARY KEY,
  instrument_id INTEGER REFERENCES instruments(id),
  source VARCHAR(50) NOT NULL,  -- 'reddit', 'twitter', 'news'
  score NUMERIC(5,4),  -- -1.0 to 1.0
  mention_count INTEGER DEFAULT 0,
  volume_change_pct NUMERIC(8,2),
  measured_at TIMESTAMPTZ NOT NULL,
  collected_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_sentiment_instrument ON sentiment(instrument_id, measured_at DESC);

-- Alert rules (user-configured)
CREATE TABLE IF NOT EXISTS alert_rules (
  id SERIAL PRIMARY KEY,
  instrument_id INTEGER REFERENCES instruments(id),
  rule_type VARCHAR(50) NOT NULL,  -- 'price_drop', 'volume_spike', 'stop_loss', 'news_keyword'
  params JSONB NOT NULL DEFAULT '{}',
  tier VARCHAR(20) DEFAULT 'important',  -- 'critical', 'important', 'info'
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Fired alerts (history)
CREATE TABLE IF NOT EXISTS alerts (
  id SERIAL PRIMARY KEY,
  alert_rule_id INTEGER REFERENCES alert_rules(id),
  instrument_id INTEGER REFERENCES instruments(id),
  title TEXT NOT NULL,
  message TEXT,
  tier VARCHAR(20) NOT NULL,
  is_read BOOLEAN DEFAULT false,
  fired_at TIMESTAMPTZ DEFAULT NOW(),
  read_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_alerts_instrument ON alerts(instrument_id, fired_at DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_unread ON alerts(is_read, fired_at DESC) WHERE is_read = false;
