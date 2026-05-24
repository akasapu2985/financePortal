import type { Config } from 'tailwindcss'

export const financeTheme = {
  colors: {
    app: '#070b11',
    canvas: '#0b1118',
    surface: {
      1: '#0f1722',
      2: '#131d2a',
      3: '#182434',
      hover: '#1d2b3d',
      selected: '#1a3048',
    },
    border: {
      subtle: '#213247',
      strong: '#2b425b',
      grid: '#1b2837',
    },
    text: {
      primary: '#e6edf5',
      secondary: '#a9b7c6',
      muted: '#6f8297',
      disabled: '#516172',
    },
    accent: {
      DEFAULT: '#4da3ff',
      hover: '#6ab2ff',
      soft: 'rgba(77, 163, 255, 0.16)',
    },
    market: {
      gain: '#22c55e',
      gainStrong: '#16a34a',
      loss: '#ef4444',
      lossStrong: '#dc2626',
      neutral: '#94a3b8',
      warning: '#f59e0b',
      info: '#38bdf8',
    },
    alert: {
      critical: '#ef4444',
      important: '#f59e0b',
      info: '#38bdf8',
    },
    chart: {
      candleUp: '#22c55e',
      candleDown: '#ef4444',
      wickUp: '#4ade80',
      wickDown: '#f87171',
      volumeUp: 'rgba(34, 197, 94, 0.42)',
      volumeDown: 'rgba(239, 68, 68, 0.42)',
      grid: '#1b2837',
      crosshair: '#6f8297',
      priceLine: '#8fb8ff',
      overlay1: '#fbbf24',
      overlay2: '#a78bfa',
      overlay3: '#22d3ee',
    },
  },
  fontFamily: {
    sans: ['Inter', 'Segoe UI', 'system-ui', 'sans-serif'],
    mono: ['IBM Plex Mono', 'Cascadia Code', 'ui-monospace', 'monospace'],
  },
  fontSize: {
    '2xs': ['0.625rem', { lineHeight: '0.875rem' }],
    xs: ['0.6875rem', { lineHeight: '1rem' }],
    sm: ['0.75rem', { lineHeight: '1.125rem' }],
    md: ['0.8125rem', { lineHeight: '1.125rem' }],
    lg: ['0.875rem', { lineHeight: '1.25rem' }],
    xl: ['1rem', { lineHeight: '1.375rem' }],
    '2xl': ['1.25rem', { lineHeight: '1.5rem' }],
  },
  spacing: {
    panel: '0.75rem',
    header: '1.75rem',
    tab: '2.25rem',
    row: '2.5rem',
    'row-dense': '2.125rem',
    spark: '3.5rem',
  },
} satisfies NonNullable<Config['theme']>['extend']

const config = {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  darkMode: 'class',
  theme: {
    extend: financeTheme,
  },
} satisfies Config

export default config
