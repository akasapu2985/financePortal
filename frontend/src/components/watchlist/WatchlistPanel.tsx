import { useEffect, useMemo, useState } from 'react'
import { Layers3, ListFilter, Sparkles } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
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
const STARTER_WATCHLIST_NAME = 'Core Watchlist'
const STARTER_WATCHLIST_DESCRIPTION = 'Seeded market leaders for the default dashboard view.'
const STARTER_SYMBOL_COUNT = 6
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
    createWatchlist,
    isAddingInstrument,
    isCreatingWatchlist,
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

  const starterInstruments = useMemo(() => {
    return instruments.slice(0, STARTER_SYMBOL_COUNT).map((instrument) => ({
      ...instrument,
      symbol: normalizeSymbol(instrument.symbol),
    }))
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

  useEffect(() => {
    if (isLoadingWatchlists || watchlists.length > 0 || starterInstruments.length === 0 || isCreatingWatchlist) {
      return
    }

    const bootstrapStarterWatchlist = async () => {
      try {
        const createdWatchlist = await createWatchlist({
          name: STARTER_WATCHLIST_NAME,
          description: STARTER_WATCHLIST_DESCRIPTION,
        })

        let hydratedWatchlist = createdWatchlist

        for (const starterInstrument of starterInstruments) {
          hydratedWatchlist = await addInstrumentToWatchlist({
            watchlistId: hydratedWatchlist.id,
            symbol: starterInstrument.symbol,
          })
        }

        setRequestedWatchlistId(hydratedWatchlist.id)
        setFeedback({
          tone: 'info',
          message: `Loaded ${hydratedWatchlist.instrument_count ?? hydratedWatchlist.instruments.length} starter symbols into ${hydratedWatchlist.name}.`,
        })
      } catch (error) {
        setFeedback({
          tone: 'error',
          message: getMutationErrorMessage(error, 'Unable to load the starter watchlist right now.'),
        })
      }
    }

    void bootstrapStarterWatchlist()
  }, [
    addInstrumentToWatchlist,
    createWatchlist,
    isCreatingWatchlist,
    isLoadingWatchlists,
    starterInstruments,
    watchlists.length,
  ])

  const handleAddSymbol = async (symbol: string) => {
    if (!activeWatchlistId) {
      return
    }

    try {
      const updatedWatchlist = await addInstrumentToWatchlist({ watchlistId: activeWatchlistId, symbol })
      const normalizedSymbol = normalizeSymbol(symbol)

      setSelectedSymbol(normalizedSymbol)
      setFeedback({ tone: 'success', message: `Added ${normalizedSymbol} to ${updatedWatchlist.name}.` })
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

      setFeedback({ tone: 'success', message: `Removed ${normalizedSymbol} from ${updatedWatchlist.name}.` })
    } catch (error) {
      setFeedback({
        tone: 'error',
        message: getMutationErrorMessage(error, `Unable to remove ${normalizedSymbol} right now.`),
      })
    }
  }

  const isBootstrappingStarterWatchlist = watchlists.length === 0 && (isCreatingWatchlist || isAddingInstrument)
  const isLoadingPanel = isLoadingWatchlists || isBootstrappingStarterWatchlist || (activeWatchlistId !== null && isLoadingActiveWatchlist && !activeWatchlist)
  const activeWatchlistCount = activeWatchlist?.instrument_count ?? watchlistInstruments.length
  const watchlistCountLabel = isBootstrappingStarterWatchlist
    ? 'Loading…'
    : normalizedSearchQuery
      ? `${filteredWatchlistInstruments.length}/${activeWatchlistCount} symbols`
      : `${activeWatchlistCount} symbols`

  return (
    <PanelFrame
      as="aside"
      title="Watchlists"
      description="Track leadership, rotate fast, and keep active names one click away."
      actions={<Badge variant="secondary">{watchlistCountLabel}</Badge>}
      contentClassName="gap-3 p-3"
    >
      <Card className="border-border-subtle/70 bg-surface-2/70">
        <CardContent className="space-y-3 px-3 py-3">
          <div className="flex items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <div className="rounded-xl border border-border-subtle/70 bg-surface-3/80 p-2 text-accent">
                <Layers3 className="size-4" />
              </div>
              <div>
                <p className="data-label">Active list</p>
                <p className="text-sm font-semibold text-text-primary">{activeWatchlist?.name ?? 'Preparing watchlist'}</p>
              </div>
            </div>
            <Badge className="border-border-subtle/70 bg-app/60 text-text-secondary">
              <ListFilter className="size-3" />
              dense view
            </Badge>
          </div>

          <div className="flex flex-wrap gap-2">
            {visibleWatchlists.map((watchlist) => {
              const isActive = watchlist.id === activeWatchlistId

              return (
                <Button
                  key={watchlist.id}
                  type="button"
                  variant={isActive ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setRequestedWatchlistId(watchlist.id)}
                  className={isActive ? 'shadow-[0_8px_24px_rgba(77,163,255,0.18)]' : ''}
                >
                  {watchlist.name}
                </Button>
              )
            })}
          </div>

          <div className="grid grid-cols-2 gap-2">
            <div className="rounded-xl border border-border-subtle/70 bg-app/50 px-3 py-2">
              <p className="data-label">Selected</p>
              <p className="mt-1 font-mono text-sm font-semibold text-text-primary">{selectedSymbol ?? 'Awaiting symbol'}</p>
            </div>
            <div className="rounded-xl border border-border-subtle/70 bg-app/50 px-3 py-2">
              <p className="data-label">Coverage</p>
              <p className="mt-1 flex items-center gap-1 text-sm font-semibold text-text-primary">
                <Sparkles className="size-3.5 text-accent" />
                {activeWatchlistCount} names live
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      <WatchlistActions
        activeWatchlistName={activeWatchlist?.name ?? null}
        candidateName={addCandidate?.name ?? null}
        candidateSymbol={addCandidate?.symbol ?? null}
        feedback={feedback}
        helperMessage={helperMessage}
        isAddingSymbol={isAddingInstrument}
        onAddSymbol={handleAddSymbol}
      />

      <div className="grid grid-cols-[minmax(0,1.4fr)_minmax(88px,0.9fr)_minmax(82px,0.8fr)_74px_40px] gap-3 px-3 pb-1 text-[0.625rem] uppercase tracking-[0.12em] text-text-muted">
        <span>Symbol</span>
        <span className="text-right">Last</span>
        <span className="text-right">Change</span>
        <span className="text-right">Trend</span>
        <span className="text-right">&nbsp;</span>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto pr-1">
        {isLoadingPanel ? (
          <div className="space-y-2">
            {loadingSkeletonRows.map((row) => (
              <div key={row} className="grid grid-cols-[minmax(0,1fr)_40px] gap-2">
                <div className="grid min-h-[4.5rem] grid-cols-[minmax(0,1.4fr)_minmax(88px,0.9fr)_minmax(82px,0.8fr)_74px] gap-3 rounded-2xl border border-border-subtle/70 bg-surface-2/60 px-3 py-3">
                  <div className="space-y-2">
                    <div className="h-4 w-14 animate-pulse rounded bg-surface-3" />
                    <div className="h-3 w-24 animate-pulse rounded bg-surface-3" />
                  </div>
                  <div className="ml-auto h-4 w-16 animate-pulse self-center rounded bg-surface-3" />
                  <div className="ml-auto h-4 w-14 animate-pulse self-center rounded bg-surface-3" />
                  <div className="ml-auto h-4 w-12 animate-pulse self-center rounded bg-surface-3" />
                </div>
                <div className="ml-auto h-8 w-8 animate-pulse self-center rounded-xl bg-surface-3" />
              </div>
            ))}
          </div>
        ) : watchlistInstruments.length === 0 ? (
          <Card className="border-dashed border-border-strong bg-canvas/70">
            <CardContent className="px-4 py-5 text-sm text-text-secondary">
              <p className="font-medium text-text-primary">Starter watchlist is still empty.</p>
              <p className="mt-2">Seeded instruments are ready to load once the watchlist service responds.</p>
              {starterInstruments.length > 0 ? (
                <div className="mt-3 flex flex-wrap gap-2">
                  {starterInstruments.map((instrument) => (
                    <Badge key={instrument.symbol} variant="secondary">
                      {instrument.symbol}
                    </Badge>
                  ))}
                </div>
              ) : null}
            </CardContent>
          </Card>
        ) : filteredWatchlistInstruments.length === 0 ? (
          <Card className="border-dashed border-border-strong bg-canvas/70">
            <CardContent className="flex min-h-40 items-center justify-center px-4 py-5 text-center text-sm text-text-secondary">
              No symbols match “{normalizedSearchQuery}”
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-2">
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
