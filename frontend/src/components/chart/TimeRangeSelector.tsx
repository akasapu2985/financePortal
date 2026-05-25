import { SlidersHorizontal } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import type { PriceTimeRange } from '@/services/types'

interface TimeRangeSelectorProps {
  value: PriceTimeRange
  onChange: (timeRange: PriceTimeRange) => void
}

const timeRangeOptions: PriceTimeRange[] = ['1D', '1W', '1M', '3M', '6M', '1Y', 'ALL']

export const TimeRangeSelector = ({ value, onChange }: TimeRangeSelectorProps) => {
  return (
    <Card className="border-border-subtle/70 bg-surface-2/70">
      <CardContent className="flex flex-wrap items-center justify-between gap-3 px-3 py-3">
        <div className="flex items-center gap-2 text-text-secondary">
          <div className="rounded-xl border border-border-subtle/70 bg-app/60 p-2">
            <SlidersHorizontal className="size-4" />
          </div>
          <div>
            <p className="data-label">Time range</p>
            <p className="text-xs text-text-secondary">Switch the visible market horizon without leaving the chart.</p>
          </div>
        </div>

        <div className="flex flex-wrap gap-2">
          {timeRangeOptions.map((option) => {
            const isActive = option === value

            return (
              <Button key={option} type="button" onClick={() => onChange(option)} variant={isActive ? 'default' : 'outline'} size="sm" aria-pressed={isActive}>
                {option}
              </Button>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}
