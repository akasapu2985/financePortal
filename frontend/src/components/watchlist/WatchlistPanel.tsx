import { useEffect, useMemo, useState } from 'react'
import { PanelFrame } from '@/components/shell/PanelFrame'
import { WatchlistItem } from '@/components/watchlist/WatchlistItem'
import { useSelectedSymbol } from '@/hooks/useSelectedSymbol'
import { useInstruments, useWatchlist, useWatchlists } from '@/hooks/queries/useMarketData'

interface WatchlistPanelProps {
  searchQuery: string
}

const MAX_VISIBLE_TABS = 5
const loadingSkeletonRows = Array.from({ length: 6 }, (_, index) => index)

export const WatchlistPanel = ({ searchQuery }: WatchlistPanelProps) => {
  const { data: watchlists = [], isLoading: isLoadingWatchlists } = useWatchlists()
  const { data: instruments = [] } = useInstruments()
  const { selectedSymbol, setSelectedSymbol } = useSelectedSymbol()
  const [requestedWatchlistId, setRequestedWatchlistId] = useState<number | null>(null)

  const visibleWatchlists = useMemo(() => watchlists.slice(0, MAX_VISIBLE_TABS), [watchlists])
  const activeWatchlistId = useMemo(() => {
    if (requestedWatchlistId !== null && visibleWatchlists.some((watchlist) => watchlist.id === requestedWatchlistId)) {
      return requestedWatchlistId
    }

    return visibleWatchlists[0]?.id ?? null
  }, [requestedWatchlistId, visibleWatchlists])

  const { data: activeWatchlist, isLoading: isLoadingActiveWatchlist } = useWatchlist(activeWatchlistId)

  const instrumentNameBySymbol = useMemo(() => {
    return new Map(instruments.map((instrument) => [instrument.symbol.trim().toUpperCase(), instrument.name]))
  }, [instruments])

  const watchlistInstruments = useMemo(() => {
    return (activeWatchlist?.instruments ?? []).map((instrument) => ({
      ...instrument,
      name: instrumentNameBySymbol.get(instrument.symbol.trim().toUpperCase()) ?? instrument.name,
    }))
  }, [activeWatchlist?.instruments, instrumentNameBySymbol])

  const normalizedSearchQuery = searchQuery.trim().toUpperCase()
  const filteredWatchlistInstruments = useMemo(() => {
    if (!normalizedSearchQuery) {
      return watchlistInstruments
    }

    return watchlistInstruments.filter((instrument) => {
      return instrument.symbol.trim().toUpperCase().includes(normalizedSearchQuery)
    })
  }, [normalizedSearchQuery, watchlistInstruments])

  useEffect(() => {
    if (selectedSymbol || filteredWatchlistInstruments.length === 0) {
      return
    }

    setSelectedSymbol(filteredWatchlistInstruments[0].symbol)
  }, [filteredWatchlistInstruments, selectedSymbol, setSelectedSymbol])

  const isLoadingPanel = isLoadingWatchlists || (activeWatchlistId !== null && isLoadingActiveWatchlist && !activeWatchlist)
  const activeWatchlistCount = activeWatchlist?.instrument_count ?? watchlistInstruments.length
  const watchlistCountLabel = normalizedSearchQuery
    ? `${filteredWatchlistInstruments.length}/${activeWatchlistCount} symbols`
    : `${activeWatchlistCount} symbols`

  return (
    <PanelFrame
      as="aside"
      title="Watchlist"
      eyebrow="Left rail"
      actions={<span className="rounded-full bg-surface-3 px-2 py-1 text-xs text-text-secondary">{watchlistCountLabel}</span>}
      contentClassName="gap-3 p-3"
    >
      <div className="flex flex-wrap gap-2">
        {visibleWatchlists.map((watchlist) => {
          const isActive = watchlist.id === activeWatchlistId

          return (
            <button
              key={watchlist.id}
              type="button"
              onClick={() => setRequestedWatchlistId(watchlist.id)}
              className={[
                'rounded-lg border px-3 py-1.5 text-sm transition-colors',
                isActive
                  ? 'border-accent bg-surface-selected text-text-primary'
                  : 'border-border-subtle bg-transparent text-text-secondary hover:bg-surface-hover hover:text-text-primary',
              ].join(' ')}
            >
              {watchlist.name}
            </button>
          )
        })}
      </div>

      <div className="grid grid-cols-[minmax(0,1.4fr)_minmax(84px,0.9fr)_minmax(72px,0.8fr)_56px] gap-3 border-b border-border-subtle px-3 pb-2 text-xs uppercase tracking-[0.08em] text-text-secondary">
        <span>Symbol</span>
        <span className="text-right">Last</span>
        <span className="text-right">Chg %</span>
        <span className="text-right">Trend</span>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto pr-1">
        {isLoadingPanel ? (
          <div className="space-y-2">
            {loadingSkeletonRows.map((row) => (
              <div key={row} className="grid min-h-14 grid-cols-[minmax(0,1.4fr)_minmax(84px,0.9fr)_minmax(72px,0.8fr)_56px] gap-3 rounded-xl px-3 py-2">
                <div className="space-y-2">
                  <div className="h-4 w-14 animate-pulse rounded bg-surface-3" />
                  <div className="h-3 w-24 animate-pulse rounded bg-surface-3" />
                </div>
                <div className="ml-auto h-4 w-16 animate-pulse self-center rounded bg-surface-3" />
                <div className="ml-auto h-4 w-14 animate-pulse self-center rounded bg-surface-3" />
                <div className="ml-auto h-4 w-12 animate-pulse self-center rounded bg-surface-3" />
              </div>
            ))}
          </div>
        ) : watchlistInstruments.length === 0 ? (
          <div className="flex h-full min-h-40 items-center justify-center rounded-xl border border-dashed border-border-strong bg-canvas px-4 text-center text-sm text-text-secondary">
            No stocks in watchlist
          </div>
        ) : filteredWatchlistInstruments.length === 0 ? (
          <div className="flex h-full min-h-40 items-center justify-center rounded-xl border border-dashed border-border-strong bg-canvas px-4 text-center text-sm text-text-secondary">
            No symbols match “{normalizedSearchQuery}”
          </div>
        ) : (
          <div className="space-y-1">
            {filteredWatchlistInstruments.map((instrument) => (
              <WatchlistItem
                key={`${activeWatchlistId ?? 'watchlist'}-${instrument.symbol}`}
                instrument={instrument}
                isSelected={selectedSymbol === instrument.symbol.trim().toUpperCase()}
                onSelect={setSelectedSymbol}
              />
            ))}
          </div>
        )}
      </div>
    </PanelFrame>
  )
}
