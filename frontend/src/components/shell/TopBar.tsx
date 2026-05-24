const indices = [
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
    label: 'DOW',
    value: '39,487.12',
    change: '-0.13%',
    statusClassName: 'status-loss',
  },
] as const

export const TopBar = () => {
  return (
    <header className="panel-surface sticky top-2 z-20 flex min-h-14 flex-col gap-3 rounded-2xl border border-border-subtle px-3 py-3 backdrop-blur xl:flex-row xl:items-center xl:justify-between">
      <div className="flex flex-1 flex-col gap-3 xl:flex-row xl:items-center xl:gap-4">
        <div className="min-w-0 xl:w-64">
          <p className="data-label">financePortal</p>
          <h1 className="truncate text-base font-semibold tracking-tight text-text-primary">Market operations dashboard</h1>
        </div>

        <div className="panel-surface-elevated flex min-h-10 flex-1 items-center rounded-xl border border-border-subtle px-3 text-sm text-text-muted">
          Search symbols, watchlists, or headlines
        </div>

        <div className="grid gap-2 sm:grid-cols-3 xl:min-w-[26rem] xl:flex-1">
          {indices.map((index) => (
            <section key={index.label} className="panel-surface-elevated rounded-xl border border-border-subtle px-3 py-2">
              <p className="data-label">{index.label}</p>
              <div className="mt-1 flex items-center justify-between gap-2">
                <span className="data-value text-sm">{index.value}</span>
                <span className={index.statusClassName}>{index.change}</span>
              </div>
            </section>
          ))}
        </div>
      </div>

      <div className="grid gap-2 sm:grid-cols-2 xl:w-auto xl:min-w-[20rem]">
        <section className="panel-surface-elevated rounded-xl border border-border-subtle px-3 py-2">
          <p className="data-label">Portfolio value</p>
          <div className="mt-1 flex items-center justify-between gap-2">
            <span className="data-value text-sm">$124,880.42</span>
            <span className="status-gain">+$1,482.13</span>
          </div>
        </section>

        <section className="panel-surface-elevated rounded-xl border border-border-subtle px-3 py-2">
          <p className="data-label">Market status</p>
          <div className="mt-1 flex items-center justify-between gap-2">
            <span className="status-info">Open</span>
            <span className="data-value text-sm">09:41 ET</span>
          </div>
        </section>
      </div>
    </header>
  )
}
