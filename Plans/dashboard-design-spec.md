# Dashboard Design Specification

**Owner:** Renarin  
**Requested by:** Giakas  
**Date:** 2026-05-24T12:26:16-07:00  
**Scope:** Phase 2 dashboard MVP, with forward-compatible guidance for Phase 3 alerts and Phase 5 AI insights

## Design Intent

Build a desktop-first financial command center that combines Bloomberg-level information density with TradingView-level chart usability. The dashboard should feel fast, serious, and operational. Every area should support scan-first behavior: prices, deltas, sentiment, and alerts should be readable in under 2 seconds.

Core principles:

- Dense, not cramped
- Dark by default, with layered surfaces instead of flat black
- Monospace numerics everywhere prices, percentages, time, or counts matter
- Color used semantically, never decoratively
- The chart is the focal point, but the watchlist and news rails stay visible at all times on desktop
- Interactions should reward power users: keyboard support, predictable focus, low-friction switching

---

## 1. Layout Architecture

### Primary Layout Model

Use a **3-column command-center layout** with a persistent top bar.

- **Left rail:** Watchlists and portfolio instruments
- **Center canvas:** Chart workspace and symbol detail
- **Right rail:** News feed by default, with room for alerts and AI insights in later phases
- **Top bar:** Search, market pulse, portfolio summary, market clock/status

This is the default desktop arrangement because it preserves the two critical side contexts around the chart:

- left side answers **what should I look at?**
- center answers **what is the market doing?**
- right side answers **why is it moving?**

### Desktop Panel Widths

For a 1440px-wide viewport:

- **Top bar height:** 56px
- **Left panel width:** 280px default, resizable from 240px to 340px
- **Center panel width:** fluid, minimum 640px
- **Right panel width:** 360px default, resizable from 320px to 420px
- **Panel gutters:** 8px
- **Outer app padding:** 8px
- **Inner panel padding:** 12px

For a 1920px-wide viewport:

- Left panel remains 280px to 320px
- Right panel remains 360px to 400px
- Extra space goes to chart canvas first

### Vertical Structure

Within the center column:

- **Chart header:** 56px
- **Time range and control row:** 36px
- **Chart area:** flexible, target 480px to 640px visible height
- **Optional lower module slot:** 160px to 220px reserved for future order flow, indicator table, or AI insight strip

Within the left column:

- **Watchlist tab row:** 36px
- **Watchlist table header:** 28px
- **Watchlist rows:** scrollable, fixed row height

Within the right column:

- **Panel header with tabs/filters:** 40px
- **Scrollable content feed:** remaining height

### Resizability

Support resizable left and right rails on desktop.

- Resize handles: 4px hit target rendered inside an 8px gutter
- Handle default color: `var(--color-border-subtle)`
- Handle hover color: `var(--color-accent)`
- Save widths to local storage per user session
- Double-click handle resets to default width

### Panel Relationships

Selection state should be single-source and global.

**Primary relationship model:**

- Selecting a symbol in the watchlist updates:
  - chart header
  - main chart series
  - chart tooltip symbol context
  - right-side news filter
  - alert badges and sentiment markers where present
  - AI insight panel context when that phase ships
- Search selection behaves exactly like watchlist selection
- Clicking a news item with a symbol tag switches selected symbol if different, then opens article detail
- Alert click jumps focus to associated symbol and relevant panel

### Header / Toolbar Design

Top bar is a dense utility strip, not a marketing navbar.

- Height: 56px
- Horizontal padding: 12px
- Item gap: 12px
- Background: elevated surface
- Bottom border: 1px solid subtle border

Top bar zones:

1. **Left:** global symbol search
2. **Center-left:** market indices mini-tickers
3. **Center-right:** portfolio value and day P/L
4. **Right:** market status, time, settings/profile affordance later

### Layout ASCII Reference

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Search / Command     S&P 500   NASDAQ   DOW        Portfolio Value / Day P&L        Market Open  09:41 ET │ 56
├──────────────────────┬───────────────────────────────────────────────────────────────┬───────────────────────┤
│ Watchlists           │ Chart Header: AAPL  189.42  +2.14 (+1.14%)                   │ News / Alerts / AI    │
│ Tabs                 ├───────────────────────────────────────────────────────────────┤ Tabs + Filters        │
│ Symbol  Last  Chg %  │ 1D  1W  1M  3M  1Y  ALL   Candles  Volume  Compare  Indicators│                       │
│ ───────────────────  │                                                               │ Article card          │
│ AAPL   189.42 +1.14  │                                                               │ Headline              │
│ MSFT   418.20 -0.42  │                                                               │ Source  12m  Positive │
│ NVDA  1028.44 +3.62  │                     Main chart canvas                          │                       │
│ TSLA   176.10 -4.90  │                candlestick + volume subplot                    │ Article card          │
│ AMD    161.88 +2.07  │                                                               │                       │
│ ...                  │                                                               │                       │
│                      │                                                               │                       │
│                      ├───────────────────────────────────────────────────────────────┤                       │
│                      │ Optional lower module slot                                     │                       │
└──────────────────────┴───────────────────────────────────────────────────────────────┴───────────────────────┘
 280px                                      fluid center / min 640px                          360px
```

### Breakpoints and Collapse Order

- **≥ 1366px:** full 3-column layout
- **1200px to 1365px:** keep 3 columns, shrink left rail to 240px and right rail to 320px
- **992px to 1199px:** convert right panel to slide-over drawer; keep left watchlist visible
- **768px to 991px:** watchlist becomes collapsible drawer, chart remains primary
- **< 768px:** not optimized first, but stack top bar, chart, contextual drawer

The right panel collapses before the left panel because symbol navigation is more core than passive news browsing.

---

## 2. Color System

Reference mood: TradingView dark theme for chart clarity, Bloomberg dark for disciplined density, with slightly cleaner contrast separation.

### Core Dark Palette

```css
:root {
  --color-bg-app: #070b11;
  --color-bg-canvas: #0b1118;
  --color-surface-1: #0f1722;
  --color-surface-2: #131d2a;
  --color-surface-3: #182434;
  --color-surface-hover: #1d2b3d;
  --color-surface-selected: #1a3048;

  --color-border-subtle: #213247;
  --color-border-strong: #2b425b;
  --color-gridline: #1b2837;

  --color-text-primary: #e6edf5;
  --color-text-secondary: #a9b7c6;
  --color-text-muted: #6f8297;
  --color-text-disabled: #516172;

  --color-accent: #4da3ff;
  --color-accent-hover: #6ab2ff;
  --color-accent-soft: rgba(77, 163, 255, 0.16);

  --color-gain: #22c55e;
  --color-gain-strong: #16a34a;
  --color-loss: #ef4444;
  --color-loss-strong: #dc2626;
  --color-neutral: #94a3b8;
  --color-warning: #f59e0b;
  --color-info: #38bdf8;

  --color-alert-critical: #ef4444;
  --color-alert-important: #f59e0b;
  --color-alert-info: #38bdf8;
}
```

### Surface Usage Rules

- `--color-bg-app`: entire application background
- `--color-bg-canvas`: chart area background and deep recess surfaces
- `--color-surface-1`: default panel background
- `--color-surface-2`: elevated rows, cards, tabs
- `--color-surface-3`: selected modules, sticky headers
- `--color-surface-hover`: hover feedback on rows/cards
- `--color-surface-selected`: selected watchlist row, selected tab, focused state backing

### Semantic Usage

- **Gain:** `#22c55e`
- **Loss:** `#ef4444`
- **Neutral:** `#94a3b8`
- **Warning:** `#f59e0b`
- **Info:** `#38bdf8`

Rules:

- Gains/losses should always affect **value text first**, then optional icon/background tint second
- Never use green/red for non-market meaning unless it is truly success/error
- Warning is for watch conditions, latency, stale data, or batched alerts
- Info is for neutral tags, selected filters, and dashboard-only alerts

### Chart Colors

Use chart colors that match financial tool expectations, not generic product colors.

```css
:root {
  --chart-candle-up: #22c55e;
  --chart-candle-down: #ef4444;
  --chart-candle-border-up: #22c55e;
  --chart-candle-border-down: #ef4444;
  --chart-wick-up: #4ade80;
  --chart-wick-down: #f87171;
  --chart-volume-up: rgba(34, 197, 94, 0.42);
  --chart-volume-down: rgba(239, 68, 68, 0.42);
  --chart-grid: #1b2837;
  --chart-crosshair: #6f8297;
  --chart-price-line: #8fb8ff;
  --chart-overlay-1: #fbbf24;
  --chart-overlay-2: #a78bfa;
  --chart-overlay-3: #22d3ee;
}
```

Guidance:

- Up candles should be filled green, not hollow, to match modern trading UI expectations
- Volume bars should be visibly lower contrast than candles
- Overlay colors must remain distinguishable over dark background and across red/green candle states

### Text Hierarchy

- **Primary text:** `#e6edf5` for active prices, headlines, selected labels
- **Secondary text:** `#a9b7c6` for metadata, column headers, source labels
- **Muted text:** `#6f8297` for timestamps, disabled states, placeholder labels

### Tailwind Token Mapping

```ts
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
    market: {
      gain: '#22c55e',
      loss: '#ef4444',
      neutral: '#94a3b8',
      warning: '#f59e0b',
      info: '#38bdf8',
    },
    accent: {
      DEFAULT: '#4da3ff',
      hover: '#6ab2ff',
      soft: 'rgba(77, 163, 255, 0.16)',
    },
  },
};
```

---

## 3. Typography

### Font Families

Use two families only.

- **UI labels and prose:** `Inter, Segoe UI, system-ui, sans-serif`
- **Numerics and market data:** `IBM Plex Mono, Cascadia Code, ui-monospace, monospace`

Rules:

- All prices, percentages, timestamps, volumes, alert counts, and index values should use the monospace stack
- Headlines and navigation labels stay on the sans stack
- Avoid more than two font families in the app

### Type Scale

This dashboard should run smaller than a typical SaaS app.

| Token | Size / Line Height | Use |
| --- | --- | --- |
| `text-2xs` | 10px / 14px | dense timestamps, micro labels, badge counts |
| `text-xs` | 11px / 16px | table headers, metadata, source labels |
| `text-sm` | 12px / 18px | default row text, filters, tabs |
| `text-md` | 13px / 18px | primary body size for dense cards |
| `text-lg` | 14px / 20px | chart header secondary metrics |
| `text-xl` | 16px / 22px | symbol price in header, prominent summary numbers |
| `text-2xl` | 20px / 24px | portfolio total, large KPI callouts |

### Weight Usage

- **600 / Semibold:** selected symbol, current price, active tab, major section labels
- **500 / Medium:** table rows, filter pills, metadata that needs clarity
- **400 / Regular:** supporting body copy, non-selected items

Avoid heavy bolding across the board. Weight should mark importance, not compensate for low contrast.

### Numeric Formatting Guidance

- Right-align numeric table columns
- Use tabular/monospace digits for all market values
- Prefer 2 decimal places for prices over $1 and 3 to 4 decimals for sub-$1 assets if introduced later
- Percentages should always include sign: `+1.24%`, `-0.81%`

---

## 4. Component Specifications

### A. Watchlist Panel (Left)

#### Purpose

Fast symbol scanning and fast context switching. This should feel closer to a market terminal table than a consumer stock app.

#### Structure

Top to bottom:

1. Watchlist panel title
2. Watchlist tabs
3. Table header row
4. Scrollable rows
5. Optional footer actions

#### Dimensions

- Panel padding: 12px
- Tab row height: 36px
- Table header height: 28px
- **Row height:** 40px default
- Dense mode row height: 34px optional later
- Row horizontal padding: 10px
- Sparkline width: 56px
- Sparkline height: 18px

#### Column Layout

- **Symbol:** 64px min width, left aligned
- **Last Price:** 72px to 88px, right aligned, monospace
- **Change %:** 64px, right aligned, monospace
- **Sparkline:** 56px, right aligned

Recommended grid:

```text
| Symbol (28%) | Last (28%) | Chg % (24%) | Spark (20%) |
```

#### Row Anatomy

- Symbol on top-left or left-center, semibold 12px
- Optional company name hidden by default to preserve density
- Last price 12px monospace medium
- Change % 12px monospace semibold
- Sparkline uses 1px stroke, no fill unless needed for contrast

#### States

**Default row**
- Background: transparent
- Border-bottom: 1px solid `--color-border-subtle`

**Hover**
- Background: `--color-surface-hover`
- Cursor: pointer

**Selected**
- Background: `--color-surface-selected`
- Left accent bar: 2px `--color-accent`
- Symbol text: primary + semibold

**Keyboard focus**
- Inset outline: 1px solid `--color-accent`
- No heavy glow

#### Gain/Loss Coding

- Positive row change value: `--color-gain`
- Negative row change value: `--color-loss`
- Neutral or unavailable: `--color-neutral`
- Do not color the full row background red/green; keep the signal focused on numeric fields and tiny sparkline tint

#### Alert Badges

Alert badges live on the symbol cell, top-right or trailing edge.

- Badge size: 14px height, min width 14px
- Text size: 10px monospace
- Critical: red fill with dark text or white text depending on contrast
- Important: amber fill
- Info: blue outline or blue dot

If multiple alert severities exist for a symbol:

- Show highest severity badge only in row
- Full alert breakdown appears in tooltip or detail panel later

#### Sorting Options

Provide sortable headers for:

- Symbol
- Last price
- Day change %
- Volume or custom metric later

Default sorting:

- Manual watchlist order by drag handle later
- Temporary MVP fallback: alphabetical within selected watchlist

#### Multiple Watchlist Tabs

Support horizontal tabs above the table.

- Height: 36px
- Active tab: surface-selected background, primary text, bottom border accent
- Inactive tab: secondary text, transparent background
- Max 5 visible tabs before overflow menu
- Include `+` action button for creating a watchlist

Examples:

```text
[ Core ] [ Momentum ] [ Earnings ] [ AI Radar ] [ + ]
```

---

### B. Chart Panel (Center)

#### Purpose

This is the primary decision surface. It should be visually calm, precise, and information rich without becoming noisy.

#### Overall Structure

1. Symbol header
2. Range/control row
3. Main chart canvas
4. Volume subplot
5. Future indicator stack or lower module slot

#### Chart Header

Height: 56px

Content order:

- Symbol ticker, semibold 16px
- Company name or market tag, secondary 11px
- Current price, monospace 16px
- Absolute change and percent change, monospace 13px
- Optional mini stats on the right: day high, day low, volume, market cap later

Example:

```text
AAPL   Apple Inc.        189.42   +2.14   +1.14%
```

#### Lightweight Charts Configuration

Recommended baseline configuration:

- Chart background: `#0b1118`
- Text color: `#a9b7c6`
- Grid vertical and horizontal lines: `#1b2837`
- Crosshair mode: normal, visible on both panes
- Right price scale visible
- Time scale visible with compact formatting
- Layout padding: minimal
- Last price line visible
- Price line color: `#8fb8ff`
- No animation-heavy transitions on range changes

Candlestick series:

- Up color: `#22c55e`
- Down color: `#ef4444`
- Wick colors slightly brighter than body
- Border same as body for crisp rendering on dark backgrounds

Volume subplot:

- Height: 96px to 120px
- Bars keyed to candle direction
- Low opacity fill to avoid competing with price action
- Shared crosshair with main chart

#### Time Range Selector Design

Ranges:

- `1D`
- `1W`
- `1M`
- `3M`
- `1Y`
- `ALL`

Control specs:

- Height: 28px
- Pill padding: 0 10px
- Gap: 6px
- Border radius: 6px
- Default background: surface-2
- Active background: accent-soft
- Active text: accent
- Hover background: surface-hover

Place directly below the chart header, left aligned.

#### Crosshair and Tooltip Design

Crosshair:

- 1px dashed or lightly solid line in `#6f8297`
- Visible on both price and volume panes

Tooltip:

- Floating panel in upper-left or upper-right based on available space
- Background: `--color-surface-3`
- Border: 1px solid `--color-border-strong`
- Padding: 8px 10px
- Radius: 6px
- Font: 11px labels, 12px numeric values

Tooltip fields:

- Date/time
- Open
- High
- Low
- Close
- Volume
- Change from previous bar optional later

Use monospace for every numeric value.

#### Overlays and Indicators Later

Reserve architecture for overlays without redesign.

Future controls:

- `Indicators` dropdown
- `Compare` symbol input
- Toggle chips for SMA, EMA, VWAP, RSI, MACD later

Overlay color order:

1. SMA 20: `--chart-overlay-1`
2. SMA 50: `--chart-overlay-2`
3. VWAP: `--chart-overlay-3`

Indicators should be detachable or toggleable and never auto-enable by default.

---

### C. News Panel (Right)

#### Purpose

Explain price movement and surface why the selected symbol matters now.

#### Layout

- Panel header: 40px
- Filter row: 32px if present
- Scrollable article list
- Default card spacing: 8px

#### Article Card Design

Card anatomy:

- Headline, 12px semibold, max 2 lines
- Meta row: source, time, symbol tag, sentiment dot
- Optional summary line in expanded mode
- Optional alert badge if article triggered rule

Card specs:

- Background: surface-2
- Border: 1px solid border-subtle
- Radius: 8px
- Padding: 10px
- Hover background: surface-hover
- Selected/open state: border-strong + subtle accent tint

#### Metadata

- Source: 11px secondary
- Time: 11px muted, monospace optional
- Sentiment indicator: 8px dot or small pill
- Sentiment label optional in expanded mode only

#### Category Tabs / Filters

Support tabs or segmented filters:

- `All`
- `Symbol`
- `Market`
- `Filings`
- `Sentiment`

Default behavior:

- When a stock is selected, open on `Symbol`
- User can switch back to `All`

#### Compact vs Expanded View

**Compact mode**
- Headline + one metadata row
- Card height target: 64px to 76px
- Default for desktop density

**Expanded mode**
- Adds 2-line summary excerpt
- Card height target: 96px to 112px
- User toggle persisted locally

#### Relationship to Selected Stock

- Selected symbol filters the right panel automatically
- If no symbol-specific articles exist, show market-wide feed with an empty-state note: `No fresh symbol-specific news. Showing market feed.`
- Clicking a different symbol tag inside an article updates global selection

#### Sentiment Color Coding

- Positive: green dot `#22c55e`
- Negative: red dot `#ef4444`
- Mixed/neutral: slate dot `#94a3b8`
- High-impact or breaking: amber border accent `#f59e0b`

---

### D. Top Bar

#### Search Behavior

Search is a command input, not just a decorative field.

- Input width: 280px default, expandable to 360px on focus
- Height: 34px
- Placeholder: `Search symbol or company`
- Icon left, 14px
- Clear button on input when populated

Typeahead behavior:

- Debounce: 150ms
- Results dropdown max height: 320px
- Show ticker, company name, exchange, asset type
- Up/down keyboard navigation
- Enter selects symbol and updates dashboard context
- Escape closes results without clearing current selection

#### Market Indices Display

Show 3 mini tickers:

- S&P 500
- NASDAQ
- DOW

Each ticker block:

- Width: auto, min 88px
- Index label 10px muted
- Value and percent change 11px monospace semibold
- Positive/negative color on delta only, label stays secondary

#### Portfolio Summary

Content:

- Total portfolio value
- Day change absolute
- Day change percent

Specs:

- Value: 16px monospace semibold
- Day change: 12px monospace semibold
- Align right of center cluster
- Positive/negative colors on day change only

#### Time / Market Status Indicator

Rightmost cluster:

- Market state pill: `OPEN`, `PRE`, `AFTER`, `CLOSED`
- Local or Eastern time display, monospace 11px
- Use a small status dot plus label

State colors:

- OPEN: green
- PRE / AFTER: amber
- CLOSED: muted slate

---

### E. Alerts Panel (Phase 3)

#### Role

Alerts need to feel triaged, not noisy. Severity and recency should be obvious before the user reads the body.

#### Alert Card Anatomy

- Left severity bar: 3px
- Icon column: 20px
- Content column: title + message + time
- Trailing actions: unread dot or dismiss affordance

#### Card Specs

- Min height: 64px
- Padding: 10px 12px
- Radius: 8px
- Background: surface-2
- Border: 1px solid border-subtle

Fields:

- Title: 12px semibold
- Message: 11px secondary, max 2 lines
- Time: 10px muted, monospace

#### Tier Color Rules

- Critical: left bar red, icon red
- Important: left bar amber, icon amber
- Informational: left bar blue, icon blue

#### Unread Indicator

- 8px filled dot at top-right of card
- Use accent blue by default, not red, to distinguish unread from severity

#### Dismiss / Mark Read

- Hover reveals trailing action icons
- Single click on card marks as read
- Dismiss icon only on hover or selected state
- Bulk mark-all-read can live in panel header later

#### Watchlist Alert Badge Relationship

- Watchlist badge count reflects unread alerts for that symbol
- Critical unread alert should override standard count and show critical marker first

---

### F. AI Insights Panel (Phase 5)

#### Design Goal

AI output must read like an analyst briefing, not a chat transcript.

#### Presentation Pattern

Default structure:

1. Brief header with generated time and scope
2. Summary bullets
3. Key risks
4. Watch items
5. Optional recommended actions or thresholds

#### Morning Brief Card Layout

- Card padding: 12px
- Section gaps: 10px
- Header line: title + generated time
- Summary bullets: compact list with 4px item gap
- Highlight callouts: use subtle tinted boxes, not loud gradients

Example sections:

- `Overnight movers`
- `What matters today`
- `Risk flags`
- `Symbols to watch`

#### Expand / Collapse

- Default collapsed to top summary plus first 3 bullets
- Expand reveals full analysis
- Each subsection can be independently collapsed later if insight volume increases

Rules:

- Preserve scannability first
- Never render long paragraphs by default
- Use bullet structure and labels over narrative blocks

---

## 5. Interaction Patterns

### Stock Selection Flow

Canonical flow:

1. User clicks or keyboard-selects symbol in watchlist
2. Selected row updates immediately
3. Chart header updates
4. Chart data refetch begins
5. Existing chart remains visible until new data loads
6. Right rail filters to selected-symbol news
7. Alert badges and AI context update to same symbol

Loading guidance:

- Keep previous chart frame visible while next series loads
- Use subtle loading bar or skeleton in header, not a full-panel spinner
- Response should feel continuous, not blanked out

### Keyboard Navigation

Power-user shortcuts should be first-class.

Recommended shortcuts:

- `/` focuses global search
- `↑` / `↓` moves watchlist selection
- `Enter` confirms current highlighted search result
- `[` and `]` cycle watchlist tabs
- `1` to `6` switches chart ranges if no text input is focused
- `N` focuses news panel
- `W` focuses watchlist panel
- `C` focuses chart panel
- `A` opens alerts panel later

Focus behavior:

- Focus state must be clearly visible with 1px accent outline
- Keyboard interactions must not depend on mouse hover state

### Time Range Switching

- Range chips update selected state instantly
- Chart transitions should avoid flashy animation
- Preserve crosshair if feasible, otherwise reset cleanly
- Active range remains visible in header/control row at all times

### Responsive Behavior

Collapse order on smaller screens:

1. Right panel becomes slide-over drawer
2. Right panel filters compress into icon menu
3. Top bar indices reduce to abbreviated single-line values
4. Left panel narrows
5. Left panel becomes drawer only after right panel has already collapsed

Reasoning: the watchlist remains the fastest way to pivot context, so it should survive longer than the news feed.

---

## 6. Data Density Guidelines

Target a density closer to professional terminals than mainstream consumer dashboards, but with cleaner grouping and contrast.

### Density Rules

- Default text should mostly live in the 11px to 13px range
- Avoid decorative hero spacing entirely
- Use 8px spacing grid, with 4px allowed inside compact rows/cards
- Minimize redundant labels when context already provides meaning
- Prefer tables, rows, and aligned numeric columns over oversized cards

### Numeric Presentation

- All prices, percent changes, volumes, timestamps, and counts use monospace
- Right-align numeric columns for vertical scan efficiency
- Preserve plus/minus sign and consistent decimals

### Conditional Formatting

Use conditional formatting aggressively but precisely:

- Green and red for deltas, candle direction, sentiment shift when relevant
- Amber for risk, premarket/after-hours, unusual conditions
- Blue for selection, informational status, AI/system context

### Sparklines

Use sparklines where a full chart would waste space.

Good sparkline placements:

- Watchlist rows
- Portfolio row summaries
- Alert context previews later

Sparkline rules:

- 1px to 1.5px stroke
- No axes
- Last point may use a subtle end dot if needed
- Color should reflect direction over selected range

### Whitespace Philosophy

Whitespace is a tool for grouping, not decoration.

- Every gap should separate meaningfully different information
- Prefer tighter vertical rhythm inside tables and feeds
- Give the chart breathing room, but compress repetitive list UI
- If a row can be understood at 40px height, do not make it 56px

---

## 7. Reference Analysis

### What TradingView Does Well

- Best-in-class chart clarity on dark backgrounds
- Crosshair behavior feels precise and useful
- Range selectors and chart controls stay compact
- The chart remains the star without losing utility chrome

We should borrow:

- chart calmness
- disciplined gridlines
- predictable crosshair tooltips
- compact range toggles

### What Bloomberg Does Well

- Extreme data density
- Efficient use of color as semantic signal
- Keyboard-first workflows
- Multiple contexts visible at the same time

We should borrow:

- scan-first layout logic
- terminal-like hierarchy for market data
- multi-panel persistence
- low-whitespace bias

### What Robinhood Does Well

- Clean hierarchy
- Simple card anatomy
- Good restraint in use of accent color
- Fast emotional readability for gain/loss

We should borrow:

- simplicity in card construction
- restraint around visual noise
- clean typography hierarchy for summaries

### What We Will Do Differently

This product should combine density and clarity rather than picking one side.

- More information visible at once than Robinhood
- Cleaner and more modern than Bloomberg
- Less tool-heavy and less intimidating than TradingView full terminal mode
- Stronger connection between watchlist, chart, news, alerts, and AI insight than any single reference

The result should feel like a **personal market operations console**:

- dense enough for a power user
- calm enough for daily use
- structured enough that Shallan can implement it consistently without reinterpretation

---

## Implementation Notes for Shallan

### Priority Order

1. Nail the 3-column shell and spacing system first
2. Implement tokens and typography before component styling
3. Build watchlist row density correctly before adding decorative detail
4. Get chart header + range controls aligned before deep chart polish
5. Keep the right rail compact by default

### Non-Negotiables

- Dark theme tokens must drive the entire UI
- Monospace numerics are mandatory
- Watchlist rows must remain compact
- Chart is the focal surface
- Selected symbol state must drive chart, news, alerts, and AI context
- Right panel should never overpower the chart visually

### Acceptance Criteria

The dashboard implementation is on spec when:

- a symbol can be scanned, selected, and understood in under 2 seconds
- the chart dominates without isolating the user from context
- gain/loss state is readable from peripheral vision
- the UI feels denser than a normal web app but still cleaner than a terminal
- panel proportions hold up at 1440px and 1920px widths
