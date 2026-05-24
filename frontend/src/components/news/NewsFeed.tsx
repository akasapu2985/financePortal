import { useMemo } from 'react'
import { PanelFrame } from '@/components/shell/PanelFrame'
import { useNews } from '@/hooks/queries/useMarketData'
import { useSelectedSymbol } from '@/hooks/useSelectedSymbol'
import type { NewsArticle, NewsSentiment } from '@/services/types'

const MAX_FEED_ITEMS = 10
const loadingSkeletonRows = Array.from({ length: 4 }, (_, index) => index)
const articleDateFormatter = new Intl.DateTimeFormat('en-US', {
  month: 'short',
  day: 'numeric',
  hour: 'numeric',
  minute: '2-digit',
})

const getSentimentBadgeClassName = (sentiment: NewsSentiment) => {
  if (sentiment === 'positive') {
    return 'border border-market-gain/30 bg-market-gain/10 text-market-gain'
  }

  if (sentiment === 'negative') {
    return 'border border-market-loss/30 bg-market-loss/10 text-market-loss'
  }

  return 'border border-border-strong bg-surface-3 text-text-secondary'
}

const getSentimentLabel = (sentiment: NewsSentiment) => {
  if (sentiment === 'positive') {
    return 'Positive'
  }

  if (sentiment === 'negative') {
    return 'Negative'
  }

  return 'Neutral'
}

const formatArticleTimestamp = (article: NewsArticle) => {
  const timestamp = article.published_at ?? article.collected_at ?? null

  if (!timestamp) {
    return 'Timestamp unavailable'
  }

  const articleDate = new Date(timestamp)

  if (Number.isNaN(articleDate.getTime())) {
    return 'Timestamp unavailable'
  }

  const elapsedMilliseconds = Date.now() - articleDate.getTime()
  const elapsedMinutes = Math.round(elapsedMilliseconds / (1000 * 60))

  if (elapsedMinutes < 60) {
    return `${Math.max(elapsedMinutes, 1)}m ago`
  }

  if (elapsedMinutes < 24 * 60) {
    return `${Math.round(elapsedMinutes / 60)}h ago`
  }

  if (elapsedMinutes < 7 * 24 * 60) {
    return `${Math.round(elapsedMinutes / (24 * 60))}d ago`
  }

  return articleDateFormatter.format(articleDate)
}

export const NewsFeed = () => {
  const { selectedSymbol } = useSelectedSymbol()
  const normalizedSymbol = selectedSymbol?.trim().toUpperCase() ?? null
  const { data: articles = [], error, isFetching, isLoading } = useNews(normalizedSymbol, MAX_FEED_ITEMS)

  const feedLabel = normalizedSymbol ?? 'Market wide'
  const sortedArticles = useMemo(() => {
    return [...articles].sort((leftArticle, rightArticle) => {
      const leftTimestamp = new Date(leftArticle.published_at ?? leftArticle.collected_at ?? 0).getTime()
      const rightTimestamp = new Date(rightArticle.published_at ?? rightArticle.collected_at ?? 0).getTime()

      return rightTimestamp - leftTimestamp
    })
  }, [articles])
  const isInitialLoad = isLoading || (isFetching && sortedArticles.length === 0)
  const errorMessage = error instanceof Error ? error.message : 'Unable to load news right now.'

  return (
    <PanelFrame
      as="aside"
      title="News Feed"
      eyebrow="Right rail"
      actions={
        <div className="flex items-center gap-2">
          <span className="rounded-full bg-surface-3 px-2 py-1 text-xs text-text-secondary">{feedLabel}</span>
          {isFetching && sortedArticles.length > 0 ? (
            <span className="rounded-full bg-accent/16 px-2 py-1 text-xs font-medium text-accent">Refreshing</span>
          ) : null}
        </div>
      }
      contentClassName="gap-3 p-3"
    >
      <div className="rounded-xl border border-border-subtle bg-surface-2 px-3 py-3 text-sm text-text-secondary">
        {normalizedSymbol
          ? `Tracking the latest ${normalizedSymbol} headlines from the backend feed.`
          : 'Tracking the latest market-wide headlines from the backend feed.'}
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto pr-1">
        {isInitialLoad ? (
          <div className="space-y-3">
            {loadingSkeletonRows.map((row) => (
              <div key={row} className="panel-surface-elevated rounded-xl border border-border-subtle px-3 py-3">
                <div className="flex items-center justify-between gap-3">
                  <div className="h-3 w-20 animate-pulse rounded bg-surface-3" />
                  <div className="h-5 w-20 animate-pulse rounded-full bg-surface-3" />
                </div>
                <div className="mt-3 h-4 w-full animate-pulse rounded bg-surface-3" />
                <div className="mt-2 h-4 w-4/5 animate-pulse rounded bg-surface-3" />
                <div className="mt-3 h-3 w-2/3 animate-pulse rounded bg-surface-3" />
              </div>
            ))}
          </div>
        ) : error ? (
          <div className="flex h-full min-h-40 items-center justify-center rounded-xl border border-dashed border-market-loss/40 bg-market-loss/10 px-4 text-center text-sm text-market-loss">
            {errorMessage}
          </div>
        ) : sortedArticles.length === 0 ? (
          <div className="flex h-full min-h-40 items-center justify-center rounded-xl border border-dashed border-border-strong bg-canvas px-4 text-center text-sm text-text-secondary">
            {normalizedSymbol ? `No news found for ${normalizedSymbol}.` : 'No market news available yet.'}
          </div>
        ) : (
          <div className="space-y-3">
            {sortedArticles.map((article) => (
              <article key={`${article.url}-${article.collected_at ?? article.published_at ?? article.headline}`} className="panel-surface-elevated rounded-xl border border-border-subtle px-3 py-3">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="min-w-0">
                    <p className="data-label">{article.source ?? 'Unknown source'}</p>
                    <p className="mt-1 text-2xs text-text-muted">{formatArticleTimestamp(article)}</p>
                  </div>
                  <span
                    className={[
                      'rounded-full px-2 py-1 text-2xs font-medium uppercase tracking-[0.08em]',
                      getSentimentBadgeClassName(article.sentiment),
                    ].join(' ')}
                  >
                    {getSentimentLabel(article.sentiment)}
                  </span>
                </div>

                <a
                  href={article.url}
                  target="_blank"
                  rel="noreferrer"
                  className="mt-3 block text-sm font-semibold leading-5 text-text-primary transition-colors hover:text-accent"
                >
                  {article.headline}
                </a>

                {article.summary ? <p className="mt-2 text-xs leading-5 text-text-secondary">{article.summary}</p> : null}

                <div className="mt-3 flex flex-wrap items-center gap-2">
                  {article.symbol ? (
                    <span className="rounded-full border border-border-strong bg-canvas px-2 py-1 text-2xs font-medium text-text-secondary">
                      {article.symbol}
                    </span>
                  ) : null}
                  <span className="text-2xs text-text-muted">Opens in a new tab</span>
                </div>
              </article>
            ))}
          </div>
        )}
      </div>
    </PanelFrame>
  )
}
