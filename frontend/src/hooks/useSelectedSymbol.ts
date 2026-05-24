import { createContext, createElement, useCallback, useContext, useMemo, useState, type PropsWithChildren } from 'react'

interface SelectedSymbolContextValue {
  selectedSymbol: string | null
  setSelectedSymbol: (symbol: string | null) => void
}

const SelectedSymbolContext = createContext<SelectedSymbolContextValue | undefined>(undefined)

export const SelectedSymbolProvider = ({ children }: PropsWithChildren) => {
  const [selectedSymbol, setSelectedSymbolState] = useState<string | null>(null)

  const setSelectedSymbol = useCallback((symbol: string | null) => {
    const normalizedSymbol = symbol?.trim().toUpperCase() ?? ''

    setSelectedSymbolState(normalizedSymbol.length > 0 ? normalizedSymbol : null)
  }, [])

  const value = useMemo(
    () => ({
      selectedSymbol,
      setSelectedSymbol,
    }),
    [selectedSymbol, setSelectedSymbol],
  )

  return createElement(SelectedSymbolContext.Provider, { value }, children)
}

export const useSelectedSymbol = () => {
  const context = useContext(SelectedSymbolContext)

  if (!context) {
    throw new Error('useSelectedSymbol must be used within SelectedSymbolProvider')
  }

  return context
}
