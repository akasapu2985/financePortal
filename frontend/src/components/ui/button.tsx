import * as React from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { Slot } from 'radix-ui'

import { cn } from '@/lib/utils'

const buttonVariants = cva(
  'inline-flex shrink-0 items-center justify-center gap-2 whitespace-nowrap rounded-xl border text-xs font-medium tracking-[0.04em] transition-all outline-none select-none focus-visible:ring-2 focus-visible:ring-ring/40 disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*=\'size-\'])]:size-3.5',
  {
    variants: {
      variant: {
        default: 'border-accent/25 bg-accent/14 text-accent shadow-[inset_0_1px_0_rgba(255,255,255,0.05)] hover:bg-accent/22 hover:text-accent-hover',
        outline: 'border-border-subtle bg-surface-2/85 text-text-secondary hover:bg-surface-hover hover:text-text-primary',
        secondary: 'border-border-subtle bg-surface-3/80 text-text-primary hover:bg-surface-hover',
        ghost: 'border-transparent bg-transparent text-text-secondary hover:bg-surface-hover hover:text-text-primary',
        destructive: 'border-market-loss/25 bg-market-loss/10 text-market-loss hover:bg-market-loss/18',
        link: 'border-transparent bg-transparent px-0 text-accent hover:text-accent-hover',
      },
      size: {
        default: 'h-10 px-4',
        xs: 'h-7 rounded-lg px-2.5 text-[0.6875rem]',
        sm: 'h-8 rounded-lg px-3 text-[0.6875rem]',
        lg: 'h-11 px-5 text-sm',
        icon: 'size-10',
        'icon-xs': 'size-7 rounded-lg',
        'icon-sm': 'size-8 rounded-lg',
        'icon-lg': 'size-11',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  },
)

function Button({
  className,
  variant = 'default',
  size = 'default',
  asChild = false,
  ...props
}: React.ComponentProps<'button'> &
  VariantProps<typeof buttonVariants> & {
    asChild?: boolean
  }) {
  const Comp = asChild ? Slot.Root : 'button'

  return (
    <Comp
      data-slot="button"
      data-variant={variant}
      data-size={size}
      className={cn(buttonVariants({ variant, size, className }))}
      {...props}
    />
  )
}

export { Button }
