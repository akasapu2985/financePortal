import type { ReactNode } from 'react'
import { TopBar } from '@/components/shell/TopBar'

interface DashboardLayoutProps {
  leftPanel: ReactNode
  centerPanel: ReactNode
  rightPanel: ReactNode
}

export const DashboardLayout = ({ leftPanel, centerPanel, rightPanel }: DashboardLayoutProps) => {
  return (
    <main className="app-shell min-h-screen bg-app text-text-primary">
      <div className="mx-auto grid min-h-screen w-full max-w-[1600px] grid-rows-[auto_1fr] gap-2 px-2 py-2">
        <TopBar />
        <section className="grid min-h-0 gap-2 lg:grid-cols-[240px_minmax(0,1fr)] xl:grid-cols-[280px_minmax(640px,1fr)_320px] 2xl:grid-cols-[280px_minmax(640px,1fr)_360px]">
          <div className="min-h-[18rem] min-w-0 lg:min-h-0">{leftPanel}</div>
          <div className="min-h-[24rem] min-w-0 lg:min-h-0">{centerPanel}</div>
          <div className="min-h-[18rem] min-w-0 lg:col-span-2 xl:col-span-1 xl:min-h-0">{rightPanel}</div>
        </section>
      </div>
    </main>
  )
}
