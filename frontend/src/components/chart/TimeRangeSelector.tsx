import type { PriceTimeRange } from '@/services/types'

interface TimeRangeSelectorProps {
  value: PriceTimeRange
  onChange: (timeRange: PriceTimeRange) => void
}

const timeRangeOptions: PriceTimeRange[] = ['1D', '1W', '1M', '3M', '6M', '1Y', 'ALL']

export const TimeRangeSelector = ({ value, onChange }: TimeRangeSelectorProps) => {
  return (
    <section className="flex flex-wrap gap-2 rounded-xl border border-border-subtle bg-surface-1 px-3 py-2">
      {timeRangeOptions.map((option) => {
        const isActive = option === value

        return (
          <button
            key={option}
            type="button"
            onClick={() => onChange(option)}
            className={[
              'rounded-md px-3 py-1.5 text-sm transition-colors',
              isActive
                ? 'bg-accent/16 text-accent'
                : 'bg-surface-2 text-text-secondary hover:bg-surface-hover hover:text-text-primary',
            ].join(' ')}
            aria-pressed={isActive}
          >
            {option}
          </button>
        )
      })}
    </section>
  )
}
