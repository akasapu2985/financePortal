const marketCards = [
  {
    label: 'S&P 500',
    value: '5,214.36',
    change: '+1.24%',
    statusClassName: 'status-gain',
  },
  {
    label: 'NASDAQ',
    value: '18,101.42',
    change: '+0.82%',
    statusClassName: 'status-gain',
  },
  {
    label: 'Watchlist Alerts',
    value: '3 active',
    change: 'Latency 120ms',
    statusClassName: 'status-warning',
  },
] as const

const watchlistRows = [
  {
    symbol: 'MSFT',
    price: '$429.18',
    change: '+1.12%',
    statusClassName: 'status-gain',
  },
  {
    symbol: 'NVDA',
    price: '$1,021.77',
    change: '+2.43%',
    statusClassName: 'status-gain',
  },
  {
    symbol: 'TSLA',
    price: '$176.03',
    change: '-0.94%',
    statusClassName: 'status-loss',
  },
] as const

export const App = () => {
  return (
    <main className="app-shell min-h-screen bg-app text-text-primary">
      <div className="mx-auto flex min-h-screen max-w-7xl flex-col gap-4 px-4 py-5 lg:px-6">
        <header className="panel-surface flex flex-col gap-4 rounded-2xl px-5 py-4 lg:flex-row lg:items-center lg:justify-between">
          <div className="space-y-1">
            <p className="data-label">financePortal</p>
            <h1 className="text-2xl font-semibold tracking-tight text-text-primary">Market dashboard shell</h1>
            <p className="text-sm text-text-secondary">
              Tailwind token plumbing now mirrors Renarin&apos;s dark theme spec.
            </p>
          </div>
          <div className="grid gap-3 sm:grid-cols-3">
            {marketCards.map((card) => (
              <section key={card.label} className="panel-surface-elevated min-w-40 rounded-xl px-4 py-3">
                <p className="data-label">{card.label}</p>
                <p className="mt-2 text-xl font-semibold text-text-primary">{card.value}</p>
                <p className={`mt-1 ${card.statusClassName}`}>{card.change}</p>
              </section>
            ))}
          </div>
        </header>

        <section className="grid flex-1 gap-4 lg:grid-cols-[18rem_minmax(0,1fr)_20rem]">
          <aside className="panel-surface rounded-2xl p-4">
            <div className="mb-3 flex items-center justify-between">
              <h2 className="text-sm font-semibold text-text-primary">Watchlist</h2>
              <span className="rounded-full bg-surface-3 px-2 py-1 text-xs text-text-secondary">Tech</span>
            </div>
            <div className="divide-y divide-border-subtle overflow-hidden rounded-xl border border-border-subtle bg-canvas">
              {watchlistRows.map((row) => (
                <article key={row.symbol} className="flex items-center justify-between px-3 py-3 hover:bg-surface-hover">
                  <div>
                    <p className="text-sm font-semibold text-text-primary">{row.symbol}</p>
                    <p className="text-xs text-text-muted">US Equity</p>
                  </div>
                  <div className="text-right">
                    <p className="data-value">{row.price}</p>
                    <p className={row.statusClassName}>{row.change}</p>
                  </div>
                </article>
              ))}
            </div>
          </aside>

          <section className="panel-muted rounded-2xl border border-border-grid p-4">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <p className="data-label">Chart canvas</p>
                <h2 className="text-lg font-semibold text-text-primary">AAPL · 1D</h2>
              </div>
              <div className="rounded-full bg-accent/16 px-3 py-1 text-xs font-medium text-accent">Live</div>
            </div>
            <div className="flex h-full min-h-72 items-center justify-center rounded-xl border border-dashed border-text-muted/40 bg-surface-1 text-sm text-text-secondary">
              Shared surface, border, and semantic status tokens are ready for chart, watchlist, and alert views.
            </div>
          </section>

          <aside className="panel-surface rounded-2xl p-4">
            <div className="mb-3 flex items-center justify-between">
              <h2 className="text-sm font-semibold text-text-primary">Signals</h2>
              <span className="status-info">3 new</span>
            </div>
            <div className="space-y-3">
              <article className="panel-surface-elevated rounded-xl px-4 py-3">
                <p className="data-label">Breaking news</p>
                <p className="mt-2 text-sm text-text-primary">NVDA suppliers raise guidance after AI demand spike.</p>
                <p className="mt-2 status-gain">Positive sentiment</p>
              </article>
              <article className="panel-surface-elevated rounded-xl px-4 py-3">
                <p className="data-label">Alert queue</p>
                <p className="mt-2 text-sm text-text-primary">Three rules triggered in the last 15 minutes.</p>
                <p className="mt-2 status-warning">Review recommended</p>
              </article>
            </div>
          </aside>
        </section>
      </div>
    </main>
  )
}
