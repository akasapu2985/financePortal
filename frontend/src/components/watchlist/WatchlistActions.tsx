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
  success: 'status-gain',
  error: 'status-loss',
  info: 'status-info',
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
    <section className="rounded-xl border border-border-subtle bg-surface-1 px-3 py-3">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="min-w-0">
          {feedback ? (
            <p className={feedbackToneClassName[feedback.tone]} role={feedback.tone === 'error' ? 'alert' : 'status'}>
              {feedback.message}
            </p>
          ) : helperMessage ? (
            <p className="text-sm text-text-secondary">{helperMessage}</p>
          ) : candidateSymbol ? (
            <div>
              <p className="text-sm font-medium text-text-primary">Add {candidateSymbol} to {activeWatchlistName ?? 'watchlist'}</p>
              {candidateName ? <p className="mt-1 text-xs text-text-secondary">{candidateName}</p> : null}
            </div>
          ) : null}
        </div>

        {candidateSymbol ? (
          <button
            type="button"
            onClick={() => onAddSymbol(candidateSymbol)}
            disabled={isAddingSymbol}
            className="rounded-lg border border-accent/40 bg-accent/12 px-3 py-2 text-sm font-medium text-accent transition-colors hover:bg-accent/18 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isAddingSymbol ? 'Adding…' : `Add ${candidateSymbol}`}
          </button>
        ) : null}
      </div>
    </section>
  )
}
