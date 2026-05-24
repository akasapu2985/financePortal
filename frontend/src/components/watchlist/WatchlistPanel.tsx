import { useEffect, useMemo, useState } from 'react'
import { PanelFrame } from '@/components/shell/PanelFrame'
import { WatchlistActions } from '@/components/watchlist/WatchlistActions'
import { WatchlistItem } from '@/components/watchlist/WatchlistItem'
import { useWatchlistMutations } from '@/hooks/mutations/useWatchlistMutations'
import { useInstruments, useWatchlist, useWatchlists } from '@/hooks/queries/useMarketData'
import { useSelectedSymbol } from '@/hooks/useSelectedSymbol'
import type { Instrument } from '@/services/types'

interface WatchlistPanelProps {
  searchQuery: string
}

interface WatchlistFeedback {
  tone: 'success' | 'error' | 'info'
  message: string
}

const MAX_VISIBLE_TABS = 5
const FEEDBACK_RESET_DELAY_MS = 4000
const loadingSkeletonRows = Array.from({ length: 6 }, (_, index) => index)
const normalizeSymbol = (symbol: string) => symbol.trim().toUpperCase()

const getMutationErrorMessage = (error: unknown, fallbackMessage: string) => {
  return error instanceof Error && error.message ? error.message : fallbackMessage
}

export const WatchlistPanel = ({ searchQuery }: WatchlistPanelProps) => {
  const { data: watchlists = [], isLoading: isLoadingWatchlists } = useWatchlists()
  const { data: instruments = [] } = useInstruments()
  const { selectedSymbol, setSelectedSymbol } = useSelectedSymbol()
  const {
    addInstrumentToWatchlist,
    isAddingInstrument,
    isRemovingInstrument,
    pendingRemoveSymbol,
    removeInstrumentFromWatchlist,
  } = useWatchlistMutations()
  const [feedback, setFeedback] = useState<WatchlistFeedback | null>(null)
  const [requestedWatchlistId, setRequestedWatchlistId] = useState<number | null>(null)

  const visibleWatchlists = useMemo(() => watchlists.slice(0, MAX_VISIBLE_TABS), [watchlists])
  const activeWatchlistId = useMemo(() => {
    if (requestedWatchlistId !== null && visibleWatchlists.some((watchlist) => watchlist.id === requestedWatchlistId)) {
      return requestedWatchlistId
    }

    return visibleWatchlists[0]?.id ?? null
  }, [requestedWatchlistId, visibleWatchlists])

  const { data: activeWatchlist, isLoading: isLoadingActiveWatchlist } = useWatchlist(activeWatchlistId)

  useEffect(() => {
    if (!feedback) {
      return
    }

    const timeoutId = window.setTimeout(() => {
      setFeedback(null)
    }, FEEDBACK_RESET_DELAY_MS)

    return () => {
      window.clearTimeout(timeoutId)
    }
  }, [feedback])

  const instrumentBySymbol = useMemo(() => {
    return new Map(
      instruments.map((instrument) => {
        const normalizedSymbol = normalizeSymbol(instrument.symbol)

        return [normalizedSymbol, { ...instrument, symbol: normalizedSymbol }]
      }),
    )
  }, [instruments])

  const watchlistInstruments = useMemo(() => {
    return (activeWatchlist?.instruments ?? []).map((instrument) => {
      const normalizedSymbol = normalizeSymbol(instrument.symbol)
      const matchingInstrument = instrumentBySymbol.get(normalizedSymbol)

      return {
        ...instrument,
        symbol: normalizedSymbol,
        name: matchingInstrument?.name ?? instrument.name,
      }
    })
  }, [activeWatchlist?.instruments, instrumentBySymbol])

  const normalizedSearchQuery = searchQuery.trim().toUpperCase()
  const activeWatchlistSymbols = useMemo(() => {
    return new Set(watchlistInstruments.map((instrument) => normalizeSymbol(instrument.symbol)))
  }, [watchlistInstruments])

  const filteredWatchlistInstruments = useMemo(() => {
    if (!normalizedSearchQuery) {
      return watchlistInstruments
    }

    return watchlistInstruments.filter((instrument) => {
      return normalizeSymbol(instrument.symbol).includes(normalizedSearchQuery)
    })
  }, [normalizedSearchQuery, watchlistInstruments])

  const exactSearchInstrument = normalizedSearchQuery ? instrumentBySymbol.get(normalizedSearchQuery) ?? null : null
  const selectedInstrument = useMemo(() => {
    if (!selectedSymbol) {
      return null
    }

    return instrumentBySymbol.get(normalizeSymbol(selectedSymbol)) ?? ({
      name: selectedSymbol,
      symbol: normalizeSymbol(selectedSymbol),
    } as Instrument)
  }, [instrumentBySymbol, selectedSymbol])
  const addCandidate = useMemo(() => {
    if (exactSearchInstrument && !activeWatchlistSymbols.has(exactSearchInstrument.symbol)) {
      return exactSearchInstrument
    }

    if (!normalizedSearchQuery && selectedInstrument && !activeWatchlistSymbols.has(selectedInstrument.symbol)) {
      return selectedInstrument
    }

    return null
  }, [activeWatchlistSymbols, exactSearchInstrument, normalizedSearchQuery, selectedInstrument])

  const helperMessage = useMemo(() => {
    if (!activeWatchlist) {
      return null
    }

    if (exactSearchInstrument && activeWatchlistSymbols.has(exactSearchInstrument.symbol)) {
      return `${exactSearchInstrument.symbol} is already in ${activeWatchlist.name}.`
    }

    if (normalizedSearchQuery && !exactSearchInstrument) {
      return `No exact symbol match for “${normalizedSearchQuery}”.`
    }

    if (!normalizedSearchQuery && selectedInstrument && !activeWatchlistSymbols.has(selectedInstrument.symbol)) {
      return `Add the selected symbol back to ${activeWatchlist.name}.`
    }

    return null
  }, [activeWatchlist, activeWatchlistSymbols, exactSearchInstrument, normalizedSearchQuery, selectedInstrument])

  useEffect(() => {
    if (selectedSymbol || filteredWatchlistInstruments.length === 0) {
      return
    }

    setSelectedSymbol(filteredWatchlistInstruments[0].symbol)
  }, [filteredWatchlistInstruments, selectedSymbol, setSelectedSymbol])

  const handleAddSymbol = async (symbol: string) => {
    if (!activeWatchlistId) {
      return
    }

    try {
      const updatedWatchlist = await addInstrumentToWatchlist({ watchlistId: activeWatchlistId, symbol })
      const normalizedSymbol = normalizeSymbol(symbol)

      setSelectedSymbol(normalizedSymbol)
      setFeedback({
        tone: 'success',
        message: `Added ${normalizedSymbol} to ${updatedWatchlist.name}.`,
      })
    } catch (error) {
      setFeedback({
        tone: 'error',
        message: getMutationErrorMessage(error, `Unable to add ${normalizeSymbol(symbol)} right now.`),
      })
    }
  }

  const handleRemoveSymbol = async (symbol: string) => {
    if (!activeWatchlistId || !activeWatchlist) {
      return
    }

    const normalizedSymbol = normalizeSymbol(symbol)

    try {
      const updatedWatchlist = await removeInstrumentFromWatchlist({ watchlistId: activeWatchlistId, symbol: normalizedSymbol })

      if (selectedSymbol === normalizedSymbol) {
        setSelectedSymbol(null)
      }

      setFeedback({
        tone: 'success',
        message: `Removed ${normalizedSymbol} from ${updatedWatchlist.name}.`,
      })
    } catch (error) {
      setFeedback({
        tone: 'error',
        message: getMutationErrorMessage(error, `Unable to remove ${normalizedSymbol} right now.`),
      })
    }
  }

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

      <WatchlistActions
        activeWatchlistName={activeWatchlist?.name ?? null}
        candidateName={addCandidate?.name ?? null}
        candidateSymbol={addCandidate?.symbol ?? null}
        feedback={feedback}
        helperMessage={helperMessage}
        isAddingSymbol={isAddingInstrument}
        onAddSymbol={handleAddSymbol}
      />

      <div className="grid grid-cols-[minmax(0,1.4fr)_minmax(84px,0.9fr)_minmax(72px,0.8fr)_56px_44px] gap-3 border-b border-border-subtle px-3 pb-2 text-xs uppercase tracking-[0.08em] text-text-secondary">
        <span>Symbol</span>
        <span className="text-right">Last</span>
        <span className="text-right">Chg %</span>
        <span className="text-right">Trend</span>
        <span className="text-right">Edit</span>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto pr-1">
        {isLoadingPanel ? (
          <div className="space-y-2">
            {loadingSkeletonRows.map((row) => (
              <div key={row} className="grid min-h-14 grid-cols-[minmax(0,1.4fr)_minmax(84px,0.9fr)_minmax(72px,0.8fr)_56px_44px] gap-3 rounded-xl px-3 py-2">
                <div className="space-y-2">
                  <div className="h-4 w-14 animate-pulse rounded bg-surface-3" />
                  <div className="h-3 w-24 animate-pulse rounded bg-surface-3" />
                </div>
                <div className="ml-auto h-4 w-16 animate-pulse self-center rounded bg-surface-3" />
                <div className="ml-auto h-4 w-14 animate-pulse self-center rounded bg-surface-3" />
                <div className="ml-auto h-4 w-12 animate-pulse self-center rounded bg-surface-3" />
                <div className="ml-auto h-8 w-8 animate-pulse self-center rounded-full bg-surface-3" />
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
            {filteredWatchlistInstruments.map((instrument) => {
              const normalizedInstrumentSymbol = normalizeSymbol(instrument.symbol)

              return (
                <WatchlistItem
                  key={`${activeWatchlistId ?? 'watchlist'}-${normalizedInstrumentSymbol}`}
                  instrument={instrument}
                  isRemoving={isRemovingInstrument && pendingRemoveSymbol === normalizedInstrumentSymbol}
                  isSelected={selectedSymbol === normalizedInstrumentSymbol}
                  onRemove={handleRemoveSymbol}
                  onSelect={setSelectedSymbol}
                />
              )
            })}
          </div>
        )}
      </div>
    </PanelFrame>
  )
}
