import { keepPreviousData, useQuery } from '@tanstack/react-query'
import {
  getInstruments,
  getNews,
  getPrices,
  getWatchlist,
  getWatchlists,
} from '@/services/api'
import type { PriceTimeRange } from '@/services/types'

export const marketDataQueryKeys = {
  instruments: ['instruments'] as const,
  prices: (symbol: string, timeRange: PriceTimeRange = '1M') => ['prices', symbol, timeRange] as const,
  news: (symbol: string | null = null, limit = 20) => ['news', symbol ?? 'market', limit] as const,
  watchlists: ['watchlists'] as const,
  watchlist: (id: number) => ['watchlists', id] as const,
}

export const useInstruments = () => {
  return useQuery({
    queryKey: marketDataQueryKeys.instruments,
    queryFn: getInstruments,
  })
}

export const usePrices = (symbol: string, timeRange: PriceTimeRange = '1M') => {
  const normalizedSymbol = symbol.trim().toUpperCase()

  return useQuery({
    queryKey: marketDataQueryKeys.prices(normalizedSymbol, timeRange),
    queryFn: () => getPrices(normalizedSymbol, timeRange),
    enabled: normalizedSymbol.length > 0,
    placeholderData: keepPreviousData,
  })
}

export const useNews = (symbol: string | null = null, limit = 20) => {
  const normalizedSymbol = symbol?.trim().toUpperCase() ?? null

  return useQuery({
    queryKey: marketDataQueryKeys.news(normalizedSymbol, limit),
    queryFn: () => getNews({ symbol: normalizedSymbol, limit }),
    placeholderData: keepPreviousData,
  })
}

export const useWatchlists = () => {
  return useQuery({
    queryKey: marketDataQueryKeys.watchlists,
    queryFn: getWatchlists,
  })
}

export const useWatchlist = (id: number | null) => {
  return useQuery({
    queryKey: marketDataQueryKeys.watchlist(id ?? 0),
    queryFn: () => getWatchlist(id ?? 0),
    enabled: typeof id === 'number' && id > 0,
  })
}
