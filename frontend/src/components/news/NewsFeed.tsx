import { useMemo } from 'react'
import { ArrowUpRight, Newspaper } from 'lucide-react'
import { PanelFrame } from '@/components/shell/PanelFrame'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
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
    return 'border-market-gain/25 bg-market-gain/10 text-market-gain'
  }

  if (sentiment === 'negative') {
    return 'border-market-loss/25 bg-market-loss/10 text-market-loss'
  }

  return 'border-border-subtle bg-surface-3 text-text-secondary'
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
  const { selectedSymbol, setSelectedSymbol } = useSelectedSymbol()
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
      title="News feed"
      description={normalizedSymbol ? `Catalysts and headlines for ${normalizedSymbol}.` : 'Market-wide headlines ranked by freshness and sentiment.'}
      actions={
        <div className="flex items-center gap-2">
          <Badge variant="secondary">{feedLabel}</Badge>
          {isFetching && sortedArticles.length > 0 ? <Badge className="border-market-info/25 bg-market-info/10 text-market-info">Refreshing</Badge> : null}
        </div>
      }
      contentClassName="gap-3 p-3"
    >
      <Card className="border-border-subtle/70 bg-surface-2/70">
        <CardContent className="flex items-start gap-3 px-3 py-3 text-sm text-text-secondary">
          <div className="rounded-xl border border-border-subtle/70 bg-surface-3/80 p-2 text-accent">
            <Newspaper className="size-4" />
          </div>
          <div>
            <p className="font-medium text-text-primary">{normalizedSymbol ? `${normalizedSymbol} catalyst stream` : 'Market catalyst stream'}</p>
            <p className="mt-1 text-xs text-text-secondary">
              Click a symbol tag to sync the chart. Open any headline for the full article.
            </p>
          </div>
        </CardContent>
      </Card>

      <div className="min-h-0 flex-1 overflow-y-auto pr-1">
        {isInitialLoad ? (
          <div className="space-y-3">
            {loadingSkeletonRows.map((row) => (
              <Card key={row} className="border-border-subtle/70 bg-surface-2/70">
                <CardContent className="px-3 py-3">
                  <div className="flex items-center justify-between gap-3">
                    <div className="h-3 w-20 animate-pulse rounded bg-surface-3" />
                    <div className="h-5 w-20 animate-pulse rounded-full bg-surface-3" />
                  </div>
                  <div className="mt-3 h-4 w-full animate-pulse rounded bg-surface-3" />
                  <div className="mt-2 h-4 w-4/5 animate-pulse rounded bg-surface-3" />
                  <div className="mt-3 h-3 w-2/3 animate-pulse rounded bg-surface-3" />
                </CardContent>
              </Card>
            ))}
          </div>
        ) : error ? (
          <Card className="border-dashed border-market-loss/40 bg-market-loss/10">
            <CardContent className="flex min-h-40 items-center justify-center px-4 py-5 text-center text-sm text-market-loss">
              {errorMessage}
            </CardContent>
          </Card>
        ) : sortedArticles.length === 0 ? (
          <Card className="border-dashed border-border-strong bg-canvas/70">
            <CardContent className="flex min-h-40 items-center justify-center px-4 py-5 text-center text-sm text-text-secondary">
              {normalizedSymbol ? `No news found for ${normalizedSymbol}.` : 'No market news available yet.'}
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-3">
            {sortedArticles.map((article) => (
              <Card
                key={`${article.url}-${article.collected_at ?? article.published_at ?? article.headline}`}
                className="border-border-subtle/70 bg-surface-2/72 transition-colors hover:border-border-strong hover:bg-surface-hover/75"
              >
                <CardContent className="px-4 py-4">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex min-w-0 items-center gap-2">
                      <Badge variant="secondary">{article.source ?? 'Unknown source'}</Badge>
                      <span className="text-xs text-text-muted">{formatArticleTimestamp(article)}</span>
                    </div>
                    <Badge className={getSentimentBadgeClassName(article.sentiment)}>{getSentimentLabel(article.sentiment)}</Badge>
                  </div>

                  <a
                    href={article.url}
                    target="_blank"
                    rel="noreferrer"
                    className="mt-3 block text-sm font-semibold leading-5 text-text-primary transition-colors hover:text-accent"
                  >
                    <span className="inline-flex items-center gap-1">
                      {article.headline}
                      <ArrowUpRight className="size-3.5" />
                    </span>
                  </a>

                  {article.summary ? <p className="mt-2 text-xs leading-5 text-text-secondary">{article.summary}</p> : null}

                  <div className="mt-3 flex flex-wrap items-center gap-2">
                    {article.symbol ? (
                      <Button
                        type="button"
                        variant="outline"
                        size="xs"
                        onClick={() => {
                          const articleSymbol = article.symbol?.trim().toUpperCase()

                          if (articleSymbol) {
                            setSelectedSymbol(articleSymbol)
                          }
                        }}
                        className="font-mono"
                      >
                        {article.symbol}
                      </Button>
                    ) : null}
                    <span className="text-[0.6875rem] text-text-muted">Opens in a new tab</span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </PanelFrame>
  )
}
