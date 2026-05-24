import { ChartPanel } from '@/components/chart/ChartPanel'
import { PanelFrame } from '@/components/shell/PanelFrame'
import { WatchlistPanel } from '@/components/watchlist/WatchlistPanel'
import { useSelectedSymbol, SelectedSymbolProvider } from '@/hooks/useSelectedSymbol'
import { DashboardLayout } from '@/layouts/DashboardLayout'

const newsFeedItems = ['Macro headlines', 'Company updates', 'Analyst notes'] as const

const DashboardContent = () => {
  const { selectedSymbol } = useSelectedSymbol()

  return (
    <DashboardLayout
      leftPanel={<WatchlistPanel />}
      centerPanel={<ChartPanel />}
      rightPanel={
        <PanelFrame
          as="aside"
          title="News Feed"
          eyebrow="Right rail"
          actions={
            <span className="rounded-full bg-surface-3 px-2 py-1 text-xs text-text-secondary">
              {selectedSymbol ?? 'Market feed'}
            </span>
          }
        >
          <div className="space-y-3">
            <div className="rounded-xl border border-dashed border-border-strong bg-canvas px-3 py-3 text-sm text-text-secondary">
              News and alerts stay visible here without overpowering the chart canvas.
            </div>
            {newsFeedItems.map((item) => (
              <article key={item} className="panel-surface-elevated rounded-xl border border-border-subtle px-3 py-3">
                <p className="data-label">News Feed</p>
                <p className="mt-2 text-sm font-medium text-text-primary">{item}</p>
                <p className="mt-1 text-xs text-text-muted">
                  Placeholder card for headlines, source metadata, and sentiment tags.
                </p>
              </article>
            ))}
          </div>
        </PanelFrame>
      }
    />
  )
}

export const App = () => {
  return (
    <SelectedSymbolProvider>
      <DashboardContent />
    </SelectedSymbolProvider>
  )
}
