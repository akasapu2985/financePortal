import type { PropsWithChildren } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ApiClientError } from '@/services/api'

const FIVE_MINUTES = 5 * 60 * 1000
const ONE_MINUTE = 60 * 1000
const THIRTY_SECONDS = 30 * 1000
const MAX_RETRY_DELAY_MS = 30 * 1000

const shouldRetryQuery = (failureCount: number, error: unknown) => {
  if (error instanceof ApiClientError && error.status === 404) {
    return false
  }

  return failureCount < 3
}

const createQueryClient = () => {
  const client = new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: FIVE_MINUTES,
        gcTime: 15 * 60 * 1000,
        retry: shouldRetryQuery,
        retryDelay: (attemptIndex) => Math.min(1_000 * 2 ** attemptIndex, MAX_RETRY_DELAY_MS),
        refetchOnWindowFocus: true,
      },
    },
  })

  client.setQueryDefaults(['instruments'], {
    staleTime: FIVE_MINUTES,
  })

  client.setQueryDefaults(['prices'], {
    staleTime: THIRTY_SECONDS,
    refetchInterval: THIRTY_SECONDS,
  })

  client.setQueryDefaults(['news'], {
    staleTime: THIRTY_SECONDS,
    refetchInterval: ONE_MINUTE,
  })

  client.setQueryDefaults(['watchlists'], {
    staleTime: ONE_MINUTE,
  })

  return client
}

const queryClient = createQueryClient()

export const QueryProvider = ({ children }: PropsWithChildren) => {
  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
}
