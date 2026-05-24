import { useState } from 'react'
import { ChartPanel } from '@/components/chart/ChartPanel'
import { NewsFeed } from '@/components/news/NewsFeed'
import { WatchlistPanel } from '@/components/watchlist/WatchlistPanel'
import { SelectedSymbolProvider } from '@/hooks/useSelectedSymbol'
import { DashboardLayout } from '@/layouts/DashboardLayout'

const DashboardContent = () => {
  const [watchlistSearchQuery, setWatchlistSearchQuery] = useState('')

  return (
    <DashboardLayout
      leftPanel={<WatchlistPanel searchQuery={watchlistSearchQuery} />}
      centerPanel={<ChartPanel />}
      rightPanel={<NewsFeed />}
      onWatchlistSearchChange={setWatchlistSearchQuery}
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
