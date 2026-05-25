import { useEffect, useState } from 'react'
import { Activity, Clock3, Search, TrendingDown, TrendingUp, WalletCards } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'

interface MarketIndexCard {
  label: string
  value: number
  changePercent: number
}

interface PortfolioSummary {
  totalValue: number
  dayChangeValue: number
  dayChangePercent: number
}

interface TopBarProps {
  onWatchlistSearchChange: (query: string) => void
}

const marketIndices: MarketIndexCard[] = [
  { label: 'S&P 500', value: 5214.36, changePercent: 1.24 },
  { label: 'NASDAQ', value: 18101.42, changePercent: 0.82 },
  { label: 'DOW', value: 39487.12, changePercent: -0.13 },
]

const portfolioSummary: PortfolioSummary = {
  totalValue: 124880.42,
  dayChangeValue: 1482.13,
  dayChangePercent: 1.2,
}

const marketValueFormatter = new Intl.NumberFormat('en-US', {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
})

const currencyFormatter = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
})

const percentFormatter = new Intl.NumberFormat('en-US', {
  signDisplay: 'always',
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
})

const signedCurrencyFormatter = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  signDisplay: 'always',
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
})

const getChangeTone = (changePercent: number) => {
  if (changePercent > 0) {
    return {
      badgeClassName: 'border-market-gain/25 bg-market-gain/10 text-market-gain',
      textClassName: 'status-gain',
      Icon: TrendingUp,
    }
  }

  if (changePercent < 0) {
    return {
      badgeClassName: 'border-market-loss/25 bg-market-loss/10 text-market-loss',
      textClassName: 'status-loss',
      Icon: TrendingDown,
    }
  }

  return {
    badgeClassName: 'border-border-strong bg-surface-3 text-text-secondary',
    textClassName: 'status-neutral',
    Icon: Activity,
  }
}

export const TopBar = ({ onWatchlistSearchChange }: TopBarProps) => {
  const [localSearchQuery, setLocalSearchQuery] = useState('')

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      onWatchlistSearchChange(localSearchQuery)
    }, 200)

    return () => {
      window.clearTimeout(timeoutId)
    }
  }, [localSearchQuery, onWatchlistSearchChange])

  return (
    <header className="sticky top-2 z-20 rounded-[1.35rem] border border-border-subtle/80 bg-surface-1/88 px-4 py-3 shadow-[0_18px_60px_rgba(0,0,0,0.34)] backdrop-blur-sm ring-1 ring-white/4">
      <div className="flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
        <div className="flex min-w-0 flex-1 flex-col gap-3 xl:flex-row xl:items-center xl:gap-4">
          <div className="min-w-0 xl:w-60">
            <p className="data-label">financePortal</p>
            <h1 className="truncate text-base font-semibold tracking-tight text-text-primary">Professional market dashboard</h1>
            <p className="mt-1 text-xs text-text-muted">Scan movers, chart price action, and read catalysts without leaving the workspace.</p>
          </div>

          <div className="flex min-w-0 flex-1 flex-col gap-3 lg:flex-row lg:items-center">
            <label className="relative block w-full lg:max-w-md">
              <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-text-muted" aria-hidden="true" />
              <Input
                value={localSearchQuery}
                onChange={(event) => setLocalSearchQuery(event.target.value)}
                placeholder="Search watchlist symbols"
                className="pl-9 pr-20"
                aria-label="Filter watchlist symbols"
              />
              {localSearchQuery ? (
                <Button
                  type="button"
                  variant="ghost"
                  size="xs"
                  onClick={() => setLocalSearchQuery('')}
                  className="absolute right-1.5 top-1/2 -translate-y-1/2"
                >
                  Clear
                </Button>
              ) : null}
            </label>

            <div className="flex min-w-0 flex-1 flex-wrap gap-2">
              {marketIndices.map((index) => {
                const tone = getChangeTone(index.changePercent)

                return (
                  <Card key={index.label} size="sm" className="min-w-[10rem] flex-1 border-border-subtle/70 bg-surface-2/78">
                    <CardContent className="flex items-center gap-3 px-3 py-3">
                      <div className="min-w-0 flex-1">
                        <p className="data-label">{index.label}</p>
                        <p className="mt-1 truncate font-mono text-sm font-semibold text-text-primary">{marketValueFormatter.format(index.value)}</p>
                      </div>
                      <Badge className={tone.badgeClassName}>
                        <tone.Icon className="size-3" />
                        {percentFormatter.format(index.changePercent)}%
                      </Badge>
                    </CardContent>
                  </Card>
                )
              })}
            </div>
          </div>
        </div>

        <div className="grid gap-3 lg:grid-cols-2 xl:min-w-[25rem]">
          <Card className="border-border-subtle/70 bg-surface-2/82">
            <CardContent className="px-4 py-4">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="data-label">Portfolio summary</p>
                  <p className="mt-2 font-mono text-xl font-semibold text-text-primary">
                    {currencyFormatter.format(portfolioSummary.totalValue)}
                  </p>
                </div>
                <div className="rounded-xl border border-accent/15 bg-accent/10 p-2 text-accent">
                  <WalletCards className="size-4" />
                </div>
              </div>
              <div className="mt-3 flex items-end justify-between gap-3">
                <div>
                  <p className={getChangeTone(portfolioSummary.dayChangePercent).textClassName}>
                    {signedCurrencyFormatter.format(portfolioSummary.dayChangeValue)}
                  </p>
                  <p className="mt-1 text-xs text-text-muted">Day P&amp;L {percentFormatter.format(portfolioSummary.dayChangePercent)}%</p>
                </div>
                <Badge className="border-market-gain/25 bg-market-gain/10 text-market-gain">In line with indices</Badge>
              </div>
            </CardContent>
          </Card>

          <Card className="border-border-subtle/70 bg-surface-2/82">
            <CardContent className="px-4 py-4">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="data-label">Market status</p>
                  <p className="mt-2 flex items-center gap-2 text-sm font-semibold text-text-primary">
                    <span className="inline-flex size-2 rounded-full bg-market-gain shadow-[0_0_12px_rgba(34,197,94,0.65)]" aria-hidden="true" />
                    U.S. equities open
                  </p>
                </div>
                <div className="rounded-xl border border-border-subtle bg-surface-3/80 p-2 text-text-secondary">
                  <Clock3 className="size-4" />
                </div>
              </div>
              <div className="mt-3 flex items-center justify-between gap-3">
                <div>
                  <p className="font-mono text-sm font-semibold text-text-primary">09:41 ET</p>
                  <p className="mt-1 text-xs text-text-muted">Search filters the active watchlist in real time.</p>
                </div>
                <Badge className="border-market-info/25 bg-market-info/10 text-market-info">Live</Badge>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </header>
  )
}
