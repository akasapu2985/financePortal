import { PanelFrame } from '@/components/shell/PanelFrame'
import { DashboardLayout } from '@/layouts/DashboardLayout'

const watchlistItems = ['Core names', 'Portfolio movers', 'Earnings radar'] as const
const newsFeedItems = ['Macro headlines', 'Company updates', 'Analyst notes'] as const

export const App = () => {
  return (
    <DashboardLayout
      leftPanel={
        <PanelFrame
          as="aside"
          title="Watchlist"
          eyebrow="Left rail"
          actions={<span className="rounded-full bg-surface-3 px-2 py-1 text-xs text-text-secondary">~280px</span>}
        >
          <div className="space-y-3">
            <div className="rounded-xl border border-dashed border-border-strong bg-canvas px-3 py-3 text-sm text-text-secondary">
              Watchlist widgets land here next. The shell keeps navigation visible while feature work catches up.
            </div>
            <div className="space-y-2">
              {watchlistItems.map((item) => (
                <article key={item} className="panel-surface-elevated rounded-xl border border-border-subtle px-3 py-3">
                  <p className="text-sm font-medium text-text-primary">{item}</p>
                  <p className="mt-1 text-xs text-text-muted">Placeholder row group for instruments, last price, and change.</p>
                </article>
              ))}
            </div>
          </div>
        </PanelFrame>
      }
      centerPanel={
        <PanelFrame
          title="Chart"
          eyebrow="Center canvas"
          variant="canvas"
          actions={<span className="rounded-full bg-accent/16 px-2 py-1 text-xs font-medium text-accent">Flex grow</span>}
        >
          <div className="flex h-full min-h-[28rem] flex-col gap-3">
            <section className="panel-surface rounded-xl border border-border-subtle px-3 py-3">
              <p className="data-label">Chart header</p>
              <div className="mt-2 flex flex-wrap items-center justify-between gap-2">
                <h3 className="text-base font-semibold text-text-primary">Chart workspace placeholder</h3>
                <div className="flex flex-wrap gap-2 text-xs text-text-secondary">
                  <span className="rounded-full bg-surface-3 px-2 py-1">1D</span>
                  <span className="rounded-full bg-surface-3 px-2 py-1">1W</span>
                  <span className="rounded-full bg-surface-3 px-2 py-1">1M</span>
                </div>
              </div>
            </section>
            <section className="flex min-h-[22rem] flex-1 items-center justify-center rounded-xl border border-dashed border-border-strong bg-surface-1 px-4 text-center text-sm text-text-secondary">
              Chart
            </section>
            <section className="panel-surface rounded-xl border border-border-subtle px-3 py-3 text-sm text-text-secondary">
              Lower module slot reserved for follow-on issues like alerts, indicators, or AI context.
            </section>
          </div>
        </PanelFrame>
      }
      rightPanel={
        <PanelFrame
          as="aside"
          title="News Feed"
          eyebrow="Right rail"
          actions={<span className="rounded-full bg-surface-3 px-2 py-1 text-xs text-text-secondary">~320px</span>}
        >
          <div className="space-y-3">
            <div className="rounded-xl border border-dashed border-border-strong bg-canvas px-3 py-3 text-sm text-text-secondary">
              News and alerts stay visible here without overpowering the chart canvas.
            </div>
            {newsFeedItems.map((item) => (
              <article key={item} className="panel-surface-elevated rounded-xl border border-border-subtle px-3 py-3">
                <p className="data-label">News Feed</p>
                <p className="mt-2 text-sm font-medium text-text-primary">{item}</p>
                <p className="mt-1 text-xs text-text-muted">Placeholder card for headlines, source metadata, and sentiment tags.</p>
              </article>
            ))}
          </div>
        </PanelFrame>
      }
    />
  )
}
