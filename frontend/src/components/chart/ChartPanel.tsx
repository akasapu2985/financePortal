import { useMemo, useState } from 'react'
import { PanelFrame } from '@/components/shell/PanelFrame'
import { TradingViewChart } from '@/components/chart/TradingViewChart'
import { usePrices, useInstruments } from '@/hooks/queries/useMarketData'
import { useSelectedSymbol } from '@/hooks/useSelectedSymbol'
import type { PriceTimeRange } from '@/services/types'
import { formatPercent, formatPrice, formatSignedPrice, getQuoteSummary } from '@/utils/marketData'

const timeRangeOptions: PriceTimeRange[] = ['1D', '1W', '1M', '3M']

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

export const ChartPanel = () => {
  const { selectedSymbol } = useSelectedSymbol()
  const { data: instruments = [] } = useInstruments()
  const [timeRange, setTimeRange] = useState<PriceTimeRange>('1M')
  const normalizedSymbol = selectedSymbol?.trim().toUpperCase() ?? ''
  const { data, isLoading, isFetching } = usePrices(normalizedSymbol, timeRange)
  const priceSeries = data?.symbol === normalizedSymbol ? data : undefined

  const quoteSummary = useMemo(() => {
    return priceSeries ? getQuoteSummary(priceSeries) : { currentPrice: null, change: null, changePercent: null }
  }, [priceSeries])

  const companyName = useMemo(() => {
    return instruments.find((instrument) => instrument.symbol.trim().toUpperCase() === normalizedSymbol)?.name ?? 'Market overview'
  }, [instruments, normalizedSymbol])

  const changeClassName = getChangeClassName(quoteSummary.changePercent)
  const isPriceLoading = isLoading || (!priceSeries && isFetching)

  return (
    <PanelFrame
      title="Chart"
      eyebrow="Center canvas"
      variant="canvas"
      actions={<span className="rounded-full bg-accent/16 px-2 py-1 text-xs font-medium text-accent">{normalizedSymbol || 'Awaiting symbol'}</span>}
      contentClassName="gap-3 p-3"
    >
      {!normalizedSymbol ? (
        <div className="flex h-full min-h-[28rem] items-center justify-center rounded-xl border border-dashed border-border-strong bg-canvas px-4 text-center text-sm text-text-secondary">
          Select a stock to view chart
        </div>
      ) : (
        <>
          <section className="panel-surface rounded-xl border border-border-subtle px-3 py-3">
            <p className="data-label">Chart header</p>
            {isPriceLoading ? (
              <div className="mt-3 space-y-2">
                <div className="h-5 w-28 animate-pulse rounded bg-surface-3" />
                <div className="h-4 w-48 animate-pulse rounded bg-surface-3" />
              </div>
            ) : (
              <div className="mt-2 flex flex-wrap items-end justify-between gap-3">
                <div className="min-w-0">
                  <div className="flex flex-wrap items-baseline gap-3">
                    <h3 className="text-base font-semibold text-text-primary">{normalizedSymbol}</h3>
                    <span className="truncate text-xs text-text-secondary">{companyName}</span>
                  </div>
                  <div className="mt-2 flex flex-wrap items-center gap-3">
                    <span className="data-value text-xl">{formatPrice(quoteSummary.currentPrice)}</span>
                    <span className={changeClassName}>{formatSignedPrice(quoteSummary.change)}</span>
                    <span className={changeClassName}>{formatPercent(quoteSummary.changePercent)}</span>
                  </div>
                </div>
                {isFetching && priceSeries ? (
                  <span className="rounded-full bg-surface-3 px-2 py-1 text-xs text-text-secondary">Updating</span>
                ) : null}
              </div>
            )}
          </section>

          <section className="flex flex-wrap gap-2 rounded-xl border border-border-subtle bg-surface-1 px-3 py-2">
            {timeRangeOptions.map((option) => {
              const isActive = option === timeRange

              return (
                <button
                  key={option}
                  type="button"
                  onClick={() => setTimeRange(option)}
                  className={[
                    'rounded-md px-3 py-1.5 text-sm transition-colors',
                    isActive
                      ? 'bg-accent/16 text-accent'
                      : 'bg-surface-2 text-text-secondary hover:bg-surface-hover hover:text-text-primary',
                  ].join(' ')}
                >
                  {option}
                </button>
              )
            })}
          </section>

          <TradingViewChart symbol={normalizedSymbol} timeRange={timeRange} />

          <section className="panel-surface rounded-xl border border-border-subtle px-3 py-3 text-sm text-text-secondary">
            Lower module slot reserved for follow-on issues like alerts, indicators, or AI context.
          </section>
        </>
      )}
    </PanelFrame>
  )
}
