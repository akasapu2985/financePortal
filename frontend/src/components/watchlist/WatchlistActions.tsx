import { Plus } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'

interface WatchlistFeedback {
  tone: 'success' | 'error' | 'info'
  message: string
}

interface WatchlistActionsProps {
  activeWatchlistName: string | null
  candidateName: string | null
  candidateSymbol: string | null
  feedback: WatchlistFeedback | null
  helperMessage: string | null
  isAddingSymbol: boolean
  onAddSymbol: (symbol: string) => void
}

const feedbackToneClassName: Record<WatchlistFeedback['tone'], string> = {
  success: 'border-market-gain/25 bg-market-gain/10 text-market-gain',
  error: 'border-market-loss/25 bg-market-loss/10 text-market-loss',
  info: 'border-market-info/25 bg-market-info/10 text-market-info',
}

export const WatchlistActions = ({
  activeWatchlistName,
  candidateName,
  candidateSymbol,
  feedback,
  helperMessage,
  isAddingSymbol,
  onAddSymbol,
}: WatchlistActionsProps) => {
  const shouldRender = Boolean(candidateSymbol || feedback || helperMessage)

  if (!shouldRender) {
    return null
  }

  return (
    <Card className="border-border-subtle/70 bg-surface-2/70">
      <CardContent className="px-3 py-3">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div className="min-w-0">
            {feedback ? (
              <div className="flex flex-wrap items-center gap-2" role={feedback.tone === 'error' ? 'alert' : 'status'}>
                <Badge className={feedbackToneClassName[feedback.tone]}>{feedback.tone}</Badge>
                <p className="text-sm text-text-primary">{feedback.message}</p>
              </div>
            ) : helperMessage ? (
              <p className="text-sm text-text-secondary">{helperMessage}</p>
            ) : candidateSymbol ? (
              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <Badge variant="outline">Candidate</Badge>
                  <p className="text-sm font-medium text-text-primary">
                    Add {candidateSymbol} to {activeWatchlistName ?? 'watchlist'}
                  </p>
                </div>
                {candidateName ? <p className="mt-1 text-xs text-text-secondary">{candidateName}</p> : null}
              </div>
            ) : null}
          </div>

          {candidateSymbol ? (
            <Button type="button" onClick={() => onAddSymbol(candidateSymbol)} disabled={isAddingSymbol} size="sm" className="shrink-0">
              <Plus className="size-3.5" />
              {isAddingSymbol ? 'Adding…' : `Add ${candidateSymbol}`}
            </Button>
          ) : null}
        </div>
      </CardContent>
    </Card>
  )
}
