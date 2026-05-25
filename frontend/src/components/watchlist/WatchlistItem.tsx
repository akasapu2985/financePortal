import { useMemo } from 'react'
import { Trash2, TrendingDown, TrendingUp } from 'lucide-react'
import { Button } from '@/components/ui/button'
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
  const ChangeIcon = (quoteSummary.changePercent ?? 0) >= 0 ? TrendingUp : TrendingDown

  return (
    <div className="grid grid-cols-[minmax(0,1fr)_40px] gap-2">
      <button
        type="button"
        onClick={() => onSelect(normalizedSymbol)}
        className={[
          'group relative grid min-h-[4.5rem] grid-cols-[minmax(0,1.4fr)_minmax(88px,0.9fr)_minmax(82px,0.8fr)_74px] items-center gap-3 overflow-hidden rounded-2xl border px-3 py-3 text-left transition-all',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/35',
          isSelected
            ? 'border-accent/40 bg-surface-selected/90 shadow-[0_12px_32px_rgba(6,21,38,0.45)]'
            : 'border-border-subtle/70 bg-surface-2/70 hover:border-border-strong hover:bg-surface-hover/80',
        ].join(' ')}
        aria-pressed={isSelected}
      >
        {isSelected ? <span className="absolute inset-y-3 left-0 w-0.5 rounded-full bg-accent" aria-hidden="true" /> : null}

        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <p className="truncate text-sm font-semibold text-text-primary">{normalizedSymbol}</p>
            <span className="rounded-full border border-border-subtle/70 bg-app/60 px-1.5 py-0.5 font-mono text-[0.625rem] text-text-muted">
              EQ
            </span>
          </div>
          <p className="mt-1 truncate text-xs text-text-muted">{instrument.name}</p>
        </div>

        <div className="text-right">
          {isLoading && !quoteData ? (
            <div className="ml-auto h-4 w-16 animate-pulse rounded bg-surface-3" aria-hidden="true" />
          ) : (
            <span className="font-mono text-sm font-semibold text-text-primary">{formatPrice(quoteSummary.currentPrice)}</span>
          )}
        </div>

        <div className="text-right">
          {isLoading && !quoteData ? (
            <div className="ml-auto h-4 w-14 animate-pulse rounded bg-surface-3" aria-hidden="true" />
          ) : (
            <div className="flex items-center justify-end gap-1">
              <ChangeIcon className={`size-3 ${changeClassName}`} />
              <span className={changeClassName}>{formatPercent(quoteSummary.changePercent)}</span>
            </div>
          )}
        </div>

        <div className="flex justify-end">
          <div className="w-full max-w-[4.5rem] rounded-full border border-border-subtle/70 bg-app/60 p-1">
            {isLoading && !quoteData ? (
              <div className="h-1.5 w-full animate-pulse rounded-full bg-surface-hover" aria-hidden="true" />
            ) : (
              <div className="h-1.5 w-full rounded-full bg-surface-3">
                <div className={`h-full rounded-full ${sparkBarClassName}`} style={{ width: `${sparklineWidth}%` }} aria-hidden="true" />
              </div>
            )}
          </div>
        </div>
      </button>

      <Button
        type="button"
        variant="ghost"
        size="icon-sm"
        onClick={() => onRemove(normalizedSymbol)}
        disabled={isRemoving}
        className="self-center border border-border-subtle/70 bg-surface-2/80 text-text-secondary hover:bg-market-loss/10 hover:text-market-loss"
        aria-label={`Remove ${normalizedSymbol} from watchlist`}
      >
        {isRemoving ? '…' : <Trash2 className="size-3.5" />}
      </Button>
    </div>
  )
}
