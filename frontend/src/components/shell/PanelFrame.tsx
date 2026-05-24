import type { ElementType, ReactNode } from 'react'

interface PanelFrameProps {
  title: string
  children: ReactNode
  eyebrow?: string
  actions?: ReactNode
  className?: string
  contentClassName?: string
  as?: ElementType
  variant?: 'surface' | 'canvas'
}

const joinClasses = (...classNames: Array<string | undefined>) => classNames.filter(Boolean).join(' ')

export const PanelFrame = ({
  title,
  children,
  eyebrow,
  actions,
  className,
  contentClassName,
  as: Component = 'section',
  variant = 'surface',
}: PanelFrameProps) => {
  const surfaceClassName = variant === 'canvas' ? 'panel-muted' : 'panel-surface'

  return (
    <Component
      className={joinClasses(
        surfaceClassName,
        'flex h-full min-h-0 flex-col overflow-hidden rounded-2xl border border-border-subtle',
        className,
      )}
    >
      <header className="flex items-center justify-between gap-3 border-b border-border-subtle px-3 py-3">
        <div className="min-w-0">
          {eyebrow ? <p className="data-label">{eyebrow}</p> : null}
          <h2 className="truncate text-sm font-semibold text-text-primary">{title}</h2>
        </div>
        {actions ? <div className="shrink-0">{actions}</div> : null}
      </header>
      <div className={joinClasses('flex min-h-0 flex-1 flex-col p-3', contentClassName)}>{children}</div>
    </Component>
  )
}
