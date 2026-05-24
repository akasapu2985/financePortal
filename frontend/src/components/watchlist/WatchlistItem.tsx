import { useMemo } from 'react'
import { usePrices } from '@/hooks/queries/useMarketData'
import type { Instrument } from '@/services/types'
import { formatPercent, formatPrice, getQuoteSummary, getSparklineSeries } from '@/utils/marketData'

interface WatchlistItemProps {
  instrument: Instrument
  isRemoving: boolean
  isSelected: boolean
  onRemove: (symbol: string) => void
  onSelect: (symbol: string) => void
}

const getChangeClassName = (changePercent: number | null) => {
  if (typeof changePercent !== 'number') {
    return 'status-neutral'
  }

  if (changePercent > 0) {
    return 'status-gain'
  }

  if (changePercent < 0) {
    return 'status-loss'
  }

  return 'status-neutral'
}

const getSparkBarClassName = (changePercent: number | null) => {
  if (typeof changePercent !== 'number') {
    return 'bg-market-neutral'
  }

  if (changePercent > 0) {
    return 'bg-market-gain'
  }

  if (changePercent < 0) {
    return 'bg-market-loss'
  }

  return 'bg-market-neutral'
}

export const WatchlistItem = ({ instrument, isRemoving, isSelected, onRemove, onSelect }: WatchlistItemProps) => {
  const normalizedSymbol = instrument.symbol.trim().toUpperCase()
  const { data, isLoading } = usePrices(normalizedSymbol, '1D')
  const quoteData = data?.symbol === normalizedSymbol ? data : undefined

  const quoteSummary = useMemo(() => {
    return quoteData ? getQuoteSummary(quoteData) : { currentPrice: null, change: null, changePercent: null }
  }, [quoteData])

  const sparklineWidth = useMemo(() => {
    const sparklineSeries = quoteData ? getSparklineSeries(quoteData) : []
    const firstPoint = sparklineSeries[0]?.close ?? null
    const lastPoint = sparklineSeries.at(-1)?.close ?? null

    if (typeof firstPoint !== 'number' || typeof lastPoint !== 'number' || firstPoint === 0) {
      return 24
    }

    const movementPercent = Math.abs(((lastPoint - firstPoint) / firstPoint) * 100)

    return Math.min(100, Math.max(24, movementPercent * 12))
  }, [quoteData])

  const changeClassName = getChangeClassName(quoteSummary.changePercent)
  const sparkBarClassName = getSparkBarClassName(quoteSummary.changePercent)

  return (
    <div className="grid min-h-14 grid-cols-[minmax(0,1.4fr)_minmax(84px,0.9fr)_minmax(72px,0.8fr)_56px_44px] items-center gap-3 rounded-xl">
      <button
        type="button"
        onClick={() => onSelect(normalizedSymbol)}
        className={[
          'group relative col-span-4 grid min-h-14 grid-cols-[minmax(0,1.4fr)_minmax(84px,0.9fr)_minmax(72px,0.8fr)_56px] items-center gap-3 overflow-hidden rounded-xl border border-transparent px-3 py-2 text-left transition-colors',
          'hover:bg-surface-hover focus-visible:outline focus-visible:outline-1 focus-visible:outline-accent',
          isSelected ? 'bg-surface-selected' : 'bg-transparent',
        ].join(' ')}
        aria-pressed={isSelected}
      >
        {isSelected ? <span className="absolute inset-y-2 left-0 w-0.5 rounded-full bg-accent" aria-hidden="true" /> : null}

        <div className="min-w-0">
          <p className="truncate text-sm font-semibold text-text-primary">{normalizedSymbol}</p>
          <p className="truncate text-2xs text-text-muted">{instrument.name}</p>
        </div>

        <div className="text-right">
          {isLoading && !quoteData ? (
            <div className="ml-auto h-4 w-16 animate-pulse rounded bg-surface-3" aria-hidden="true" />
          ) : (
            <span className="data-value text-sm">{formatPrice(quoteSummary.currentPrice)}</span>
          )}
        </div>

        <div className="text-right">
          {isLoading && !quoteData ? (
            <div className="ml-auto h-4 w-14 animate-pulse rounded bg-surface-3" aria-hidden="true" />
          ) : (
            <span className={changeClassName}>{formatPercent(quoteSummary.changePercent)}</span>
          )}
        </div>

        <div className="flex justify-end">
          <div className="flex h-5 w-14 items-center justify-end rounded-full bg-surface-3 px-1.5">
            {isLoading && !quoteData ? (
              <div className="h-1.5 w-full animate-pulse rounded-full bg-surface-hover" aria-hidden="true" />
            ) : (
              <div className="h-1.5 w-full rounded-full bg-app/70">
                <div
                  className={`h-full rounded-full ${sparkBarClassName}`}
                  style={{ width: `${sparklineWidth}%` }}
                  aria-hidden="true"
                />
              </div>
            )}
          </div>
        </div>
      </button>

      <button
        type="button"
        onClick={() => onRemove(normalizedSymbol)}
        disabled={isRemoving}
        className="flex h-8 w-8 items-center justify-center rounded-full border border-border-subtle bg-surface-2 text-sm text-text-secondary transition-colors hover:bg-surface-hover hover:text-text-primary disabled:cursor-not-allowed disabled:opacity-60"
        aria-label={`Remove ${normalizedSymbol} from watchlist`}
      >
        {isRemoving ? '…' : '×'}
      </button>
    </div>
  )
}
