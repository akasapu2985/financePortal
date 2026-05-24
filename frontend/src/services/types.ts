export interface Instrument {
  id: number | null
  symbol: string
  name: string
  sector: string | null
  exchange: string | null
  is_active: boolean
  instrument_type?: string | null
  is_owned?: boolean
  created_at?: string
  added_at?: string
}

export interface PricePoint {
  time: string
  open: number | null
  high: number | null
  low: number | null
  close: number | null
  volume: number | null
}

export interface PriceSeriesResponse {
  symbol: string
  intraday: PricePoint[]
  daily: PricePoint[]
}

export type NewsSentiment = 'positive' | 'negative' | 'neutral'

export interface NewsArticle {
  id: number | null
  headline: string
  summary: string | null
  source: string | null
  url: string
  sentiment: NewsSentiment
  sentiment_score: number | null
  published_at: string | null
  symbol?: string | null
  collected_at?: string
}

export interface Watchlist {
  id: number
  name: string
  description: string | null
  is_default: boolean
  instruments: Instrument[]
  instrument_count?: number
  created_at?: string
  updated_at?: string
}

export interface HealthResponse {
  status: string
  database: string
}

export interface ApiErrorShape {
  message: string
  status: number | null
  detail: string | null
  code: string | null
}

export interface WatchlistWritePayload {
  name: string
  description?: string | null
}

export interface WatchlistInstrumentPayload {
  symbol: string
}

export type PriceTimeRange = '1D' | '1W' | '1M' | '3M' | '6M' | '1Y' | 'ALL'
