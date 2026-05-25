import { useMemo, useState } from 'react'
import { Activity, BarChart3, CandlestickChart, ScanSearch } from 'lucide-react'
import { TimeRangeSelector } from '@/components/chart/TimeRangeSelector'
import { TradingViewChart } from '@/components/chart/TradingViewChart'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { PanelFrame } from '@/components/shell/PanelFrame'
import { useInstruments, usePrices } from '@/hooks/queries/useMarketData'
import { useSelectedSymbol } from '@/hooks/useSelectedSymbol'
import type { PriceTimeRange } from '@/services/types'
import { formatPercent, formatPrice, formatSignedPrice, getQuoteSummary, getSeriesForRange } from '@/utils/marketData'

const formatCompactNumber = (value: number | null) => {
  if (typeof value !== 'number' || !Number.isFinite(value)) {
    return '—'
  }

  return new Intl.NumberFormat('en-US', {
    notation: 'compact',
    maximumFractionDigits: value >= 1000 ? 1 : 2,
  }).format(value)
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

  const chartMetrics = useMemo(() => {
    if (!priceSeries) {
      return { latestHigh: null, latestLow: null, latestVolume: null, pointCount: 0 }
    }

    const activeSeries = getSeriesForRange(priceSeries, timeRange)
    const latestPoint = activeSeries.at(-1)

    return {
      latestHigh: latestPoint?.high ?? null,
      latestLow: latestPoint?.low ?? null,
      latestVolume: latestPoint?.volume ?? null,
      pointCount: activeSeries.length,
    }
  }, [priceSeries, timeRange])

  const changeClassName = getChangeClassName(quoteSummary.changePercent)
  const isPriceLoading = isLoading || (!priceSeries && isFetching)

  return (
    <PanelFrame
      title={normalizedSymbol ? `${normalizedSymbol} chart workspace` : 'Chart workspace'}
      description={normalizedSymbol ? companyName : 'Select a symbol from the watchlist to load the active chart.'}
      variant="canvas"
      actions={<Badge variant="outline">{normalizedSymbol || 'Awaiting symbol'}</Badge>}
      contentClassName="gap-3 p-3"
    >
      {!normalizedSymbol ? (
        <Card className="flex h-full min-h-[32rem] items-center justify-center border-dashed border-border-strong bg-canvas/80">
          <CardContent className="max-w-md px-6 py-8 text-center">
            <div className="mx-auto mb-4 flex size-14 items-center justify-center rounded-2xl border border-border-subtle bg-surface-2/80 text-accent">
              <ScanSearch className="size-6" />
            </div>
            <h3 className="text-base font-semibold text-text-primary">Select a stock to open the chart</h3>
            <p className="mt-2 text-sm text-text-secondary">The center workspace updates from the selected watchlist symbol and keeps the news rail in sync.</p>
          </CardContent>
        </Card>
      ) : (
        <>
          <Card className="border-border-subtle/70 bg-surface-2/76">
            <CardContent className="px-4 py-4">
              {isPriceLoading ? (
                <div className="space-y-3">
                  <div className="h-5 w-32 animate-pulse rounded bg-surface-3" />
                  <div className="h-10 w-56 animate-pulse rounded bg-surface-3" />
                </div>
              ) : (
                <div className="flex flex-wrap items-end justify-between gap-4">
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <Badge className="border-border-subtle/70 bg-app/60 text-text-secondary">Equity</Badge>
                      <h3 className="text-lg font-semibold tracking-tight text-text-primary">{normalizedSymbol}</h3>
                      <span className="truncate text-sm text-text-secondary">{companyName}</span>
                    </div>
                    <div className="mt-3 flex flex-wrap items-end gap-3">
                      <span className="font-mono text-3xl font-semibold text-text-primary">{formatPrice(quoteSummary.currentPrice)}</span>
                      <span className={changeClassName}>{formatSignedPrice(quoteSummary.change)}</span>
                      <span className={changeClassName}>{formatPercent(quoteSummary.changePercent)}</span>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {isFetching && priceSeries ? <Badge className="border-market-info/25 bg-market-info/10 text-market-info">Updating</Badge> : null}
                    <Badge className="border-border-subtle/70 bg-app/60 text-text-secondary">{timeRange} view</Badge>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          <TimeRangeSelector value={timeRange} onChange={setTimeRange} />

          <TradingViewChart symbol={normalizedSymbol} timeRange={timeRange} />

          <div className="grid gap-3 xl:grid-cols-3">
            <Card className="border-border-subtle/70 bg-surface-2/72">
              <CardContent className="px-4 py-4">
                <p className="data-label">Session range</p>
                <div className="mt-3 flex items-center gap-3 text-text-primary">
                  <CandlestickChart className="size-4 text-accent" />
                  <div className="min-w-0">
                    <p className="font-mono text-sm font-semibold">{formatPrice(chartMetrics.latestLow)} — {formatPrice(chartMetrics.latestHigh)}</p>
                    <p className="mt-1 text-xs text-text-secondary">Latest visible high/low in the selected range.</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="border-border-subtle/70 bg-surface-2/72">
              <CardContent className="px-4 py-4">
                <p className="data-label">Volume</p>
                <div className="mt-3 flex items-center gap-3 text-text-primary">
                  <BarChart3 className="size-4 text-market-info" />
                  <div>
                    <p className="font-mono text-sm font-semibold">{formatCompactNumber(chartMetrics.latestVolume)}</p>
                    <p className="mt-1 text-xs text-text-secondary">Most recent bar volume for the active view.</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="border-border-subtle/70 bg-surface-2/72">
              <CardContent className="px-4 py-4">
                <p className="data-label">Coverage</p>
                <div className="mt-3 flex items-center gap-3 text-text-primary">
                  <Activity className="size-4 text-market-gain" />
                  <div>
                    <p className="font-mono text-sm font-semibold">{chartMetrics.pointCount} data points</p>
                    <p className="mt-1 text-xs text-text-secondary">Loaded for the current symbol and time range.</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </>
      )}
    </PanelFrame>
  )
}
