import type { ElementType, ReactNode } from 'react'
import { cn } from '@/lib/utils'

interface PanelFrameProps {
  title: string
  children: ReactNode
  eyebrow?: string
  description?: string
  actions?: ReactNode
  className?: string
  contentClassName?: string
  as?: ElementType
  variant?: 'surface' | 'canvas'
}

export const PanelFrame = ({
  title,
  children,
  eyebrow,
  description,
  actions,
  className,
  contentClassName,
  as: Component = 'section',
  variant = 'surface',
}: PanelFrameProps) => {
  return (
    <Component
      className={cn(
        'relative flex h-full min-h-0 flex-col overflow-hidden rounded-[1.35rem] border shadow-[0_22px_70px_rgba(0,0,0,0.32)] backdrop-blur-sm',
        variant === 'canvas'
          ? 'border-border-strong/70 bg-canvas/95 ring-1 ring-white/4'
          : 'border-border-subtle/80 bg-surface-1/88 ring-1 ring-white/4',
        className,
      )}
    >
      <header className="flex items-start justify-between gap-3 border-b border-border-subtle/80 px-4 py-3">
        <div className="min-w-0">
          {eyebrow ? <p className="data-label mb-1">{eyebrow}</p> : null}
          <h2 className="truncate text-sm font-semibold tracking-tight text-text-primary">{title}</h2>
          {description ? <p className="mt-1 text-xs text-text-secondary">{description}</p> : null}
        </div>
        {actions ? <div className="shrink-0">{actions}</div> : null}
      </header>
      <div className={cn('flex min-h-0 flex-1 flex-col p-4', contentClassName)}>{children}</div>
    </Component>
  )
}
