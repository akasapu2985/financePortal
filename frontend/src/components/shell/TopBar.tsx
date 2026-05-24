import { useEffect, useState } from 'react'

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
  {
    label: 'S&P 500',
    value: 5214.36,
    changePercent: 1.24,
  },
  {
    label: 'NASDAQ',
    value: 18101.42,
    changePercent: 0.82,
  },
  {
    label: 'DOW',
    value: 39487.12,
    changePercent: -0.13,
  },
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

const getChangeClassName = (changePercent: number) => {
  if (changePercent > 0) {
    return 'status-gain'
  }

  if (changePercent < 0) {
    return 'status-loss'
  }

  return 'status-neutral'
}

export const TopBar = ({ onWatchlistSearchChange }: TopBarProps) => {
  const [localSearchQuery, setLocalSearchQuery] = useState('')
  const [isMobileSearchOpen, setIsMobileSearchOpen] = useState(false)

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      onWatchlistSearchChange(localSearchQuery)
    }, 250)

    return () => {
      window.clearTimeout(timeoutId)
    }
  }, [localSearchQuery, onWatchlistSearchChange])

  return (
    <header className="panel-surface sticky top-2 z-20 rounded-2xl border border-border-subtle px-3 py-3 backdrop-blur">
      <div className="flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
        <div className="flex min-w-0 flex-1 flex-col gap-3 xl:flex-row xl:items-center xl:gap-4">
          <div className="min-w-0 xl:w-64">
            <p className="data-label">financePortal</p>
            <h1 className="truncate text-base font-semibold tracking-tight text-text-primary">Market operations dashboard</h1>
          </div>

          <div className="flex items-center gap-2 sm:hidden">
            <button
              type="button"
              onClick={() => setIsMobileSearchOpen((previousValue) => !previousValue)}
              className="rounded-lg border border-border-subtle bg-surface-2 px-3 py-2 text-sm text-text-secondary transition-colors hover:bg-surface-hover hover:text-text-primary"
            >
              {isMobileSearchOpen ? 'Hide search' : 'Search'}
            </button>
          </div>

          <label
            className={[
              'panel-surface-elevated w-full items-center gap-3 rounded-xl border border-border-subtle px-3 py-2 text-sm text-text-muted sm:flex sm:max-w-sm sm:flex-1',
              isMobileSearchOpen ? 'flex' : 'hidden',
            ].join(' ')}
          >
            <span aria-hidden="true" className="text-base text-text-secondary">
              ⌕
            </span>
            <input
              value={localSearchQuery}
              onChange={(event) => setLocalSearchQuery(event.target.value)}
              onFocus={() => setIsMobileSearchOpen(true)}
              placeholder="Filter watchlist symbols"
              className="min-w-0 flex-1 border-none bg-transparent text-sm text-text-primary outline-none placeholder:text-text-muted"
              aria-label="Filter watchlist symbols"
            />
            {localSearchQuery ? (
              <button
                type="button"
                onClick={() => setLocalSearchQuery('')}
                className="rounded-md px-2 py-1 text-xs text-text-secondary transition-colors hover:bg-surface-hover hover:text-text-primary"
              >
                Clear
              </button>
            ) : null}
          </label>

          <div className="grid gap-2 sm:grid-cols-3 xl:min-w-[26rem] xl:flex-1">
            {marketIndices.map((index) => {
              const changeClassName = getChangeClassName(index.changePercent)

              return (
                <section key={index.label} className="panel-surface-elevated rounded-xl border border-border-subtle px-3 py-2">
                  <p className="data-label">{index.label}</p>
                  <div className="mt-1 flex items-center justify-between gap-2">
                    <span className="data-value text-sm">{marketValueFormatter.format(index.value)}</span>
                    <span className={changeClassName}>{percentFormatter.format(index.changePercent)}%</span>
                  </div>
                </section>
              )
            })}
          </div>
        </div>

        <div className="grid gap-2 sm:grid-cols-2 xl:w-auto xl:min-w-[22rem]">
          <section className="panel-surface-elevated rounded-xl border border-border-subtle px-3 py-2">
            <p className="data-label">Portfolio summary</p>
            <div className="mt-1 flex items-center justify-between gap-2">
              <span className="data-value text-sm">{currencyFormatter.format(portfolioSummary.totalValue)}</span>
              <span className={getChangeClassName(portfolioSummary.dayChangePercent)}>
                {signedCurrencyFormatter.format(portfolioSummary.dayChangeValue)}
              </span>
            </div>
            <p className="mt-2 text-2xs text-text-muted">
              Day change {percentFormatter.format(portfolioSummary.dayChangePercent)}%
            </p>
          </section>

          <section className="panel-surface-elevated rounded-xl border border-border-subtle px-3 py-2">
            <p className="data-label">Market status</p>
            <div className="mt-1 flex items-center justify-between gap-2">
              <span className="status-info">Open</span>
              <span className="data-value text-sm">09:41 ET</span>
            </div>
            <p className="mt-2 text-2xs text-text-muted">Watchlist search is client-side for this release.</p>
          </section>
        </div>
      </div>
    </header>
  )
}
