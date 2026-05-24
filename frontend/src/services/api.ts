import axios from 'axios'
import type {
  ApiErrorShape,
  HealthResponse,
  Instrument,
  NewsArticle,
  NewsSentiment,
  PriceSeriesResponse,
  PriceTimeRange,
  Watchlist,
  WatchlistInstrumentPayload,
  WatchlistWritePayload,
} from '@/services/types'

interface BackendInstrumentResponse {
  symbol: string
  name: string
  type: string
  sector: string | null
  is_owned: boolean
  created_at: string
}

interface BackendNewsArticleResponse {
  symbol: string
  source: string | null
  title: string
  summary: string | null
  url: string
  published_at: string | null
  fetched_at: string
}

interface BackendWatchlistResponse {
  id: number
  name: string
  description: string | null
  created_at: string
  updated_at: string
  instrument_count: number
  instruments?: BackendWatchlistInstrumentResponse[]
}

interface BackendWatchlistInstrumentResponse extends BackendInstrumentResponse {
  added_at: string
}

interface ApiErrorResponse {
  detail?: string
  message?: string
  code?: string
}

interface GetNewsParams {
  symbol?: string | null
  limit?: number
}

const DEFAULT_API_BASE_URL = '/api'
const DEFAULT_API_TIMEOUT_MS = 10_000
const DEFAULT_NEWS_LIMIT = 20
const POSITIVE_NEWS_TERMS = ['beat', 'bullish', 'gain', 'growth', 'record', 'rally', 'surge', 'upgrade']
const NEGATIVE_NEWS_TERMS = ['bearish', 'cut', 'decline', 'downgrade', 'drop', 'fall', 'lawsuit', 'loss', 'miss', 'slump']

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL?.trim() || DEFAULT_API_BASE_URL
const parsedTimeout = Number(import.meta.env.VITE_API_TIMEOUT_MS)
const API_TIMEOUT_MS = Number.isFinite(parsedTimeout) && parsedTimeout > 0 ? parsedTimeout : DEFAULT_API_TIMEOUT_MS

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT_MS,
  headers: {
    Accept: 'application/json',
    'Content-Type': 'application/json',
  },
})

const priceRangeConfig: Record<PriceTimeRange, { intraday_limit: number; daily_limit: number }> = {
  '1D': { intraday_limit: 78, daily_limit: 1 },
  '1W': { intraday_limit: 390, daily_limit: 5 },
  '1M': { intraday_limit: 500, daily_limit: 30 },
  '3M': { intraday_limit: 500, daily_limit: 90 },
  '6M': { intraday_limit: 500, daily_limit: 180 },
  '1Y': { intraday_limit: 500, daily_limit: 365 },
  ALL: { intraday_limit: 500, daily_limit: 5000 },
}

export class ApiClientError extends Error implements ApiErrorShape {
  status: number | null
  detail: string | null
  code: string | null

  constructor({ message, status, detail, code }: ApiErrorShape) {
    super(message)
    this.name = 'ApiClientError'
    this.status = status
    this.detail = detail
    this.code = code
  }
}

const getErrorPayload = (payload: unknown): ApiErrorResponse => {
  if (!payload || typeof payload !== 'object') {
    return {}
  }

  const candidate = payload as ApiErrorResponse

  return {
    detail: typeof candidate.detail === 'string' ? candidate.detail : undefined,
    message: typeof candidate.message === 'string' ? candidate.message : undefined,
    code: typeof candidate.code === 'string' ? candidate.code : undefined,
  }
}

const normalizeApiError = (error: unknown) => {
  if (!axios.isAxiosError(error)) {
    return new ApiClientError({
      message: 'Unexpected request failure',
      status: null,
      detail: null,
      code: null,
    })
  }

  const payload = getErrorPayload(error.response?.data)
  const detail = payload.detail ?? payload.message ?? error.message

  return new ApiClientError({
    message: detail || 'Request failed',
    status: error.response?.status ?? null,
    detail: detail || null,
    code: payload.code ?? error.code ?? null,
  })
}

apiClient.interceptors.response.use(
  (response) => response,
  (error: unknown) => Promise.reject(normalizeApiError(error)),
)

const mapInstrument = (instrument: BackendInstrumentResponse): Instrument => ({
  id: null,
  symbol: instrument.symbol,
  name: instrument.name,
  sector: instrument.sector,
  exchange: null,
  is_active: true,
  instrument_type: instrument.type,
  is_owned: instrument.is_owned,
  created_at: instrument.created_at,
})

const mapWatchlistInstrument = (instrument: BackendWatchlistInstrumentResponse): Instrument => ({
  ...mapInstrument(instrument),
  added_at: instrument.added_at,
})

const mapWatchlist = (watchlist: BackendWatchlistResponse): Watchlist => ({
  id: watchlist.id,
  name: watchlist.name,
  description: watchlist.description,
  is_default: false,
  instruments: watchlist.instruments?.map(mapWatchlistInstrument) ?? [],
  instrument_count: watchlist.instrument_count,
  created_at: watchlist.created_at,
  updated_at: watchlist.updated_at,
})

const getSentimentScore = (content: string, sentimentTerms: string[]) => {
  return sentimentTerms.reduce((score, sentimentTerm) => {
    return content.includes(sentimentTerm) ? score + 1 : score
  }, 0)
}

const determineNewsSentiment = (article: BackendNewsArticleResponse): NewsSentiment => {
  const content = `${article.title} ${article.summary ?? ''}`.toLowerCase()
  const positiveScore = getSentimentScore(content, POSITIVE_NEWS_TERMS)
  const negativeScore = getSentimentScore(content, NEGATIVE_NEWS_TERMS)

  if (positiveScore > negativeScore) {
    return 'positive'
  }

  if (negativeScore > positiveScore) {
    return 'negative'
  }

  return 'neutral'
}

const mapNewsArticle = (article: BackendNewsArticleResponse): NewsArticle => {
  const sentiment = determineNewsSentiment(article)

  return {
    id: null,
    headline: article.title,
    summary: article.summary,
    source: article.source,
    url: article.url,
    sentiment,
    sentiment_score: sentiment === 'positive' ? 1 : sentiment === 'negative' ? -1 : 0,
    published_at: article.published_at,
    symbol: article.symbol,
    collected_at: article.fetched_at,
  }
}

const toWatchlistWritePayload = (name: string, description?: string | null): WatchlistWritePayload => ({
  name,
  description: description?.trim() ? description : null,
})

const toWatchlistInstrumentPayload = (symbol: string): WatchlistInstrumentPayload => ({
  symbol: symbol.trim().toUpperCase(),
})

export const getHealth = async () => {
  const response = await apiClient.get<HealthResponse>('/health')

  return response.data
}

export const getInstruments = async () => {
  const response = await apiClient.get<BackendInstrumentResponse[]>('/instruments')

  return response.data.map(mapInstrument)
}

export const getPrices = async (symbol: string, timeRange: PriceTimeRange = '1M') => {
  const normalizedSymbol = symbol.trim().toUpperCase()
  const response = await apiClient.get<PriceSeriesResponse>(`/prices/${normalizedSymbol}`, {
    params: {
      ...priceRangeConfig[timeRange],
      time_range: timeRange,
    },
  })

  return response.data
}

export const getNews = async ({ symbol, limit = DEFAULT_NEWS_LIMIT }: GetNewsParams = {}) => {
  const normalizedSymbol = symbol?.trim().toUpperCase() ?? ''
  const safeLimit = Math.max(1, limit)
  const response = await apiClient.get<BackendNewsArticleResponse[]>('/news', {
    params: {
      limit: safeLimit,
      ...(normalizedSymbol ? { symbol: normalizedSymbol } : {}),
    },
  })

  return response.data.map(mapNewsArticle)
}

export const getWatchlists = async () => {
  const response = await apiClient.get<BackendWatchlistResponse[]>('/watchlists')

  return response.data.map(mapWatchlist)
}

export const getWatchlist = async (id: number) => {
  const response = await apiClient.get<BackendWatchlistResponse>(`/watchlists/${id}`)

  return mapWatchlist(response.data)
}

export const createWatchlist = async (name: string, description?: string) => {
  const response = await apiClient.post<BackendWatchlistResponse>('/watchlists', toWatchlistWritePayload(name, description))

  return mapWatchlist(response.data)
}

export const updateWatchlist = async (id: number, name: string, description?: string) => {
  const response = await apiClient.put<BackendWatchlistResponse>(`/watchlists/${id}`, toWatchlistWritePayload(name, description))

  return mapWatchlist(response.data)
}

export const deleteWatchlist = async (id: number) => {
  await apiClient.delete(`/watchlists/${id}`)
}

export const addInstrumentToWatchlist = async (watchlistId: number, symbol: string) => {
  const response = await apiClient.post<BackendWatchlistResponse>(
    `/watchlists/${watchlistId}/instruments`,
    toWatchlistInstrumentPayload(symbol),
  )

  return mapWatchlist(response.data)
}

export const removeInstrumentFromWatchlist = async (watchlistId: number, symbol: string) => {
  const response = await apiClient.delete<BackendWatchlistResponse>(`/watchlists/${watchlistId}/instruments`, {
    data: toWatchlistInstrumentPayload(symbol),
  })

  return mapWatchlist(response.data)
}

export { apiClient, normalizeApiError }
