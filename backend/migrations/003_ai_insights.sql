-- AI-generated insights (for Phase 5, schema ready)
CREATE TABLE IF NOT EXISTS ai_insights (
  id SERIAL PRIMARY KEY,
  insight_type VARCHAR(50) NOT NULL,  -- 'morning_brief', 'evening_recap', 'stock_analysis', 'alert_tuning'
  instrument_id INTEGER REFERENCES instruments(id),  -- NULL for portfolio-wide insights
  title TEXT,
  content TEXT NOT NULL,
  model VARCHAR(100),
  tokens_used INTEGER,
  generated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_ai_insights_type ON ai_insights(insight_type, generated_at DESC);
