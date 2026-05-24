import type { PricePoint, PriceSeriesResponse, PriceTimeRange } from '@/services/types'

export interface QuoteSummary {
  currentPrice: number | null
  change: number | null
  changePercent: number | null
}

const PRICE_DIGITS_ABOVE_ONE = 2
const PRICE_DIGITS_BELOW_ONE = 4

const isFiniteNumber = (value: number | null | undefined): value is number => typeof value === 'number' && Number.isFinite(value)

export const sortPricePoints = (points: PricePoint[]) => {
  return [...points].sort((leftPoint, rightPoint) => {
    return new Date(leftPoint.time).getTime() - new Date(rightPoint.time).getTime()
  })
}

export const getSeriesForRange = (priceSeries: PriceSeriesResponse, timeRange: PriceTimeRange) => {
  const prefersIntraday = timeRange === '1D' || timeRange === '1W'
  const preferredSeries = prefersIntraday ? priceSeries.intraday : priceSeries.daily
  const fallbackSeries = prefersIntraday ? priceSeries.daily : priceSeries.intraday

  return sortPricePoints(preferredSeries.length > 0 ? preferredSeries : fallbackSeries)
}

export const getSparklineSeries = (priceSeries: PriceSeriesResponse) => {
  const preferredSeries = priceSeries.intraday.length > 0 ? priceSeries.intraday : priceSeries.daily

  return sortPricePoints(preferredSeries)
}

export const getQuoteSummary = (priceSeries: PriceSeriesResponse): QuoteSummary => {
  const intradaySeries = sortPricePoints(priceSeries.intraday)
  const dailySeries = sortPricePoints(priceSeries.daily)
  const latestIntraday = intradaySeries.at(-1)
  const latestDaily = dailySeries.at(-1)
  const previousDailyClose = dailySeries.at(-2)?.close ?? null
  const fallbackReferencePrice = latestDaily?.open ?? intradaySeries.at(-2)?.close ?? null
  const currentPrice = latestIntraday?.close ?? latestDaily?.close ?? null
  const referencePrice = previousDailyClose ?? fallbackReferencePrice

  if (!isFiniteNumber(currentPrice) || !isFiniteNumber(referencePrice) || referencePrice === 0) {
    return {
      currentPrice: isFiniteNumber(currentPrice) ? currentPrice : null,
      change: null,
      changePercent: null,
    }
  }

  const change = currentPrice - referencePrice

  return {
    currentPrice,
    change,
    changePercent: (change / referencePrice) * 100,
  }
}

export const formatPrice = (value: number | null) => {
  if (!isFiniteNumber(value)) {
    return '—'
  }

  const digits = Math.abs(value) >= 1 ? PRICE_DIGITS_ABOVE_ONE : PRICE_DIGITS_BELOW_ONE

  return value.toFixed(digits)
}

export const formatSignedPrice = (value: number | null) => {
  if (!isFiniteNumber(value)) {
    return '—'
  }

  const digits = Math.abs(value) >= 1 ? PRICE_DIGITS_ABOVE_ONE : PRICE_DIGITS_BELOW_ONE
  const prefix = value >= 0 ? '+' : ''

  return `${prefix}${value.toFixed(digits)}`
}

export const formatPercent = (value: number | null) => {
  if (!isFiniteNumber(value)) {
    return '—'
  }

  const prefix = value >= 0 ? '+' : ''

  return `${prefix}${value.toFixed(2)}%`
}
