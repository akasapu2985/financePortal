import { useEffect, useMemo, useRef } from 'react'
import {
  CandlestickSeries,
  ColorType,
  CrosshairMode,
  HistogramSeries,
  createChart,
  type CandlestickData,
  type HistogramData,
  type UTCTimestamp,
} from 'lightweight-charts'
import { usePrices } from '@/hooks/queries/useMarketData'
import type { PriceTimeRange } from '@/services/types'
import { getSeriesForRange } from '@/utils/marketData'

interface TradingViewChartProps {
  symbol: string
  timeRange: PriceTimeRange
}

const toTimestamp = (value: string) => Math.floor(new Date(value).getTime() / 1000) as UTCTimestamp

export const TradingViewChart = ({ symbol, timeRange }: TradingViewChartProps) => {
  const containerRef = useRef<HTMLDivElement | null>(null)
  const normalizedSymbol = symbol.trim().toUpperCase()
  const { data, isLoading, isFetching, isError } = usePrices(normalizedSymbol, timeRange)
  const priceSeries = data?.symbol === normalizedSymbol ? data : undefined

  const chartSeries = useMemo(() => {
    const selectedSeries = priceSeries ? getSeriesForRange(priceSeries, timeRange) : []

    return selectedSeries.reduce<{
      candles: CandlestickData<UTCTimestamp>[]
      volumes: HistogramData<UTCTimestamp>[]
    }>(
      (accumulator, point) => {
        if (
          typeof point.open !== 'number' ||
          typeof point.high !== 'number' ||
          typeof point.low !== 'number' ||
          typeof point.close !== 'number'
        ) {
          return accumulator
        }

        const timestamp = toTimestamp(point.time)
        const isGain = point.close >= point.open

        accumulator.candles.push({
          time: timestamp,
          open: point.open,
          high: point.high,
          low: point.low,
          close: point.close,
        })

        if (typeof point.volume === 'number') {
          accumulator.volumes.push({
            time: timestamp,
            value: point.volume,
            color: isGain ? 'rgba(34, 197, 94, 0.42)' : 'rgba(239, 68, 68, 0.42)',
          })
        }

        return accumulator
      },
      { candles: [], volumes: [] },
    )
  }, [priceSeries, timeRange])

  useEffect(() => {
    if (!containerRef.current || chartSeries.candles.length === 0) {
      return
    }

    const chartContainer = containerRef.current
    const chart = createChart(chartContainer, {
      width: chartContainer.clientWidth,
      height: chartContainer.clientHeight,
      layout: {
        background: { color: '#0b1118', type: ColorType.Solid },
        textColor: '#a9b7c6',
        fontFamily: 'Inter, Segoe UI, system-ui, sans-serif',
      },
      grid: {
        vertLines: { color: '#1b2837' },
        horzLines: { color: '#1b2837' },
      },
      crosshair: {
        mode: CrosshairMode.Normal,
        vertLine: {
          color: '#6f8297',
          labelBackgroundColor: '#182434',
        },
        horzLine: {
          color: '#6f8297',
          labelBackgroundColor: '#182434',
        },
      },
      rightPriceScale: {
        borderColor: '#213247',
      },
      timeScale: {
        borderColor: '#213247',
        timeVisible: timeRange === '1D' || timeRange === '1W',
        secondsVisible: false,
      },
      handleScroll: {
        mouseWheel: true,
        pressedMouseMove: true,
        horzTouchDrag: true,
        vertTouchDrag: false,
      },
      handleScale: {
        mouseWheel: true,
        pinch: true,
        axisPressedMouseMove: true,
      },
    })

    const candlestickSeries = chart.addSeries(CandlestickSeries, {
      upColor: '#22c55e',
      downColor: '#ef4444',
      borderUpColor: '#22c55e',
      borderDownColor: '#ef4444',
      wickUpColor: '#4ade80',
      wickDownColor: '#f87171',
      priceLineVisible: true,
      lastValueVisible: true,
      priceLineColor: '#8fb8ff',
    })

    const volumeSeries = chart.addSeries(HistogramSeries, {
      priceFormat: { type: 'volume' },
      priceScaleId: '',
      lastValueVisible: false,
      priceLineVisible: false,
    })

    candlestickSeries.priceScale().applyOptions({
      scaleMargins: {
        top: 0.08,
        bottom: 0.26,
      },
    })

    chart.priceScale('').applyOptions({
      scaleMargins: {
        top: 0.8,
        bottom: 0,
      },
    })

    candlestickSeries.setData(chartSeries.candles)
    volumeSeries.setData(chartSeries.volumes)
    chart.timeScale().fitContent()

    const resizeObserver = new ResizeObserver(() => {
      chart.applyOptions({
        width: chartContainer.clientWidth,
        height: chartContainer.clientHeight,
      })
    })

    resizeObserver.observe(chartContainer)

    return () => {
      resizeObserver.disconnect()
      chart.remove()
    }
  }, [chartSeries.candles, chartSeries.volumes, timeRange])

  const isChartLoading = isLoading || !priceSeries
  const hasNoData = !isChartLoading && !isError && chartSeries.candles.length === 0

  return (
    <div className="relative h-full min-h-[22rem] rounded-xl border border-border-subtle bg-canvas">
      <div ref={containerRef} className="h-full min-h-[22rem] w-full" />

      {isChartLoading ? (
        <div className="absolute inset-0 flex items-center justify-center bg-canvas/85 text-sm text-text-secondary">
          Loading chart...
        </div>
      ) : null}

      {hasNoData ? (
        <div className="absolute inset-0 flex items-center justify-center bg-canvas/85 px-4 text-center text-sm text-text-secondary">
          No price history available for {normalizedSymbol}
        </div>
      ) : null}

      {isFetching && priceSeries ? (
        <div className="absolute right-3 top-3 rounded-full bg-surface-3 px-2 py-1 text-xs text-text-secondary">Refreshing</div>
      ) : null}

      {isError && !priceSeries ? (
        <div className="absolute inset-0 flex items-center justify-center bg-canvas/85 px-4 text-center text-sm text-text-secondary">
          Unable to load chart data right now.
        </div>
      ) : null}
    </div>
  )
}
