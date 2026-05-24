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
  news: (page = 1, limit = 20) => ['news', page, limit] as const,
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

export const useNews = (page = 1, limit = 20) => {
  return useQuery({
    queryKey: marketDataQueryKeys.news(page, limit),
    queryFn: () => getNews(page, limit),
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
