import { useMutation, useQueryClient } from '@tanstack/react-query'
import { marketDataQueryKeys } from '@/hooks/queries/useMarketData'
import { addInstrumentToWatchlist as addInstrumentToWatchlistRequest, removeInstrumentFromWatchlist as removeInstrumentFromWatchlistRequest } from '@/services/api'
import type { Watchlist } from '@/services/types'

interface WatchlistInstrumentMutationInput {
  watchlistId: number
  symbol: string
}

const normalizeSymbol = (symbol: string) => symbol.trim().toUpperCase()

const toWatchlistSummary = (watchlist: Watchlist): Watchlist => ({
  ...watchlist,
  instruments: [],
  instrument_count: watchlist.instrument_count ?? watchlist.instruments.length,
})

const updateWatchlistsCache = (watchlists: Watchlist[] | undefined, updatedWatchlist: Watchlist) => {
  if (!watchlists) {
    return watchlists
  }

  return watchlists.map((watchlist) => {
    if (watchlist.id !== updatedWatchlist.id) {
      return watchlist
    }

    return {
      ...watchlist,
      ...toWatchlistSummary(updatedWatchlist),
    }
  })
}

export const useWatchlistMutations = () => {
  const queryClient = useQueryClient()

  const syncWatchlistCache = (watchlist: Watchlist) => {
    queryClient.setQueryData(marketDataQueryKeys.watchlist(watchlist.id), watchlist)
    queryClient.setQueryData<Watchlist[] | undefined>(marketDataQueryKeys.watchlists, (currentWatchlists) => {
      return updateWatchlistsCache(currentWatchlists, watchlist)
    })
  }

  const addInstrumentMutation = useMutation({
    mutationFn: ({ watchlistId, symbol }: WatchlistInstrumentMutationInput) => {
      return addInstrumentToWatchlistRequest(watchlistId, symbol)
    },
    onSuccess: syncWatchlistCache,
  })

  const removeInstrumentMutation = useMutation({
    mutationFn: ({ watchlistId, symbol }: WatchlistInstrumentMutationInput) => {
      return removeInstrumentFromWatchlistRequest(watchlistId, symbol)
    },
    onSuccess: syncWatchlistCache,
  })

  return {
    addInstrumentToWatchlist: addInstrumentMutation.mutateAsync,
    isAddingInstrument: addInstrumentMutation.isPending,
    pendingAddSymbol: addInstrumentMutation.isPending ? normalizeSymbol(addInstrumentMutation.variables?.symbol ?? '') : null,
    removeInstrumentFromWatchlist: removeInstrumentMutation.mutateAsync,
    isRemovingInstrument: removeInstrumentMutation.isPending,
    pendingRemoveSymbol: removeInstrumentMutation.isPending
      ? normalizeSymbol(removeInstrumentMutation.variables?.symbol ?? '')
      : null,
  }
}
