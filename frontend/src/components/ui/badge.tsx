import * as React from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { Slot } from 'radix-ui'

import { cn } from '@/lib/utils'

const badgeVariants = cva(
  'inline-flex w-fit shrink-0 items-center justify-center gap-1 rounded-full border px-2 py-1 text-[0.625rem] font-semibold uppercase tracking-[0.08em] transition-colors [&>svg]:pointer-events-none [&>svg]:size-3!',
  {
    variants: {
      variant: {
        default: 'border-border-subtle bg-surface-2 text-text-secondary',
        secondary: 'border-border-strong bg-surface-3 text-text-primary',
        destructive: 'border-market-loss/30 bg-market-loss/10 text-market-loss',
        outline: 'border-accent/25 bg-accent/10 text-accent',
        ghost: 'border-transparent bg-transparent text-text-secondary',
        link: 'border-transparent bg-transparent px-0 text-accent',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  },
)

function Badge({
  className,
  variant = 'default',
  asChild = false,
  ...props
}: React.ComponentProps<'span'> &
  VariantProps<typeof badgeVariants> & { asChild?: boolean }) {
  const Comp = asChild ? Slot.Root : 'span'

  return (
    <Comp
      data-slot="badge"
      data-variant={variant}
      className={cn(badgeVariants({ variant }), className)}
      {...props}
    />
  )
}

export { Badge }
