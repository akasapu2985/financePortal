import { useMutation, useQueryClient } from '@tanstack/react-query'
import { marketDataQueryKeys } from '@/hooks/queries/useMarketData'
import {
  addInstrumentToWatchlist as addInstrumentToWatchlistRequest,
  createWatchlist as createWatchlistRequest,
  removeInstrumentFromWatchlist as removeInstrumentFromWatchlistRequest,
} from '@/services/api'
import type { Watchlist } from '@/services/types'

interface WatchlistInstrumentMutationInput {
  watchlistId: number
  symbol: string
}

interface CreateWatchlistMutationInput {
  name: string
  description?: string
}

const normalizeSymbol = (symbol: string) => symbol.trim().toUpperCase()

const toWatchlistSummary = (watchlist: Watchlist): Watchlist => ({
  ...watchlist,
  instruments: [],
  instrument_count: watchlist.instrument_count ?? watchlist.instruments.length,
})

const sortWatchlists = (watchlists: Watchlist[]) => {
  return [...watchlists].sort((leftWatchlist, rightWatchlist) => {
    return leftWatchlist.name.localeCompare(rightWatchlist.name) || leftWatchlist.id - rightWatchlist.id
  })
}

const updateWatchlistsCache = (watchlists: Watchlist[] | undefined, updatedWatchlist: Watchlist) => {
  if (!watchlists) {
    return watchlists
  }

  const nextWatchlists = watchlists.map((watchlist) => {
    if (watchlist.id !== updatedWatchlist.id) {
      return watchlist
    }

    return {
      ...watchlist,
      ...toWatchlistSummary(updatedWatchlist),
    }
  })

  return sortWatchlists(nextWatchlists)
}

const appendWatchlistCache = (watchlists: Watchlist[] | undefined, createdWatchlist: Watchlist) => {
  const nextWatchlists = [...(watchlists ?? []).filter((watchlist) => watchlist.id !== createdWatchlist.id), toWatchlistSummary(createdWatchlist)]

  return sortWatchlists(nextWatchlists)
}

export const useWatchlistMutations = () => {
  const queryClient = useQueryClient()

  const syncWatchlistCache = (watchlist: Watchlist) => {
    queryClient.setQueryData(marketDataQueryKeys.watchlist(watchlist.id), watchlist)
    queryClient.setQueryData<Watchlist[] | undefined>(marketDataQueryKeys.watchlists, (currentWatchlists) => {
      return updateWatchlistsCache(currentWatchlists, watchlist)
    })
  }

  const createWatchlistMutation = useMutation({
    mutationFn: ({ name, description }: CreateWatchlistMutationInput) => {
      return createWatchlistRequest(name, description)
    },
    onSuccess: (watchlist) => {
      queryClient.setQueryData(marketDataQueryKeys.watchlist(watchlist.id), watchlist)
      queryClient.setQueryData<Watchlist[] | undefined>(marketDataQueryKeys.watchlists, (currentWatchlists) => {
        return appendWatchlistCache(currentWatchlists, watchlist)
      })
    },
  })

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
    createWatchlist: createWatchlistMutation.mutateAsync,
    isCreatingWatchlist: createWatchlistMutation.isPending,
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
