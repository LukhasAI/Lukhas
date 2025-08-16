import * as React from 'react';

/**
 * useSSE — resilient SSE hook with debounce + backoff + jitter.
 */
export function useSSE<T = any>(
  url: string,
  options?: {
    debounceMs?: number
    minMs?: number
    maxMs?: number
    paused?: boolean
    parse?: (e: MessageEvent) => T
  }
) {
  const { debounceMs = 300, minMs = 500, maxMs = 30000, paused = false, parse } = options || {}
  const [data, setData] = React.useState<T | null>(null)
  const [connected, setConnected] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)
  const retryRef = React.useRef(0)
  const esRef = React.useRef<EventSource | null>(null)
  const cancelRef = React.useRef(false)
  const debounceTimer = React.useRef<number | null>(null)

  const close = React.useCallback(() => {
    if (esRef.current) { esRef.current.close(); esRef.current = null }
    setConnected(false)
  }, [])

  const open = React.useCallback(() => {
    if (paused) return
    close()
    setError(null)
    const es = new EventSource(url)
    esRef.current = es

    es.onopen = () => { setConnected(true); retryRef.current = 0 }
    es.onmessage = (e: MessageEvent) => {
      try {
        const payload = parse ? parse(e) : JSON.parse((e as MessageEvent).data as any)
        if (debounceTimer.current) window.clearTimeout(debounceTimer.current)
        debounceTimer.current = window.setTimeout(() => { setData(payload as T) }, debounceMs) as any
      } catch (err: any) { setError(err?.message ?? 'parse-error') }
    }
    es.onerror = () => {
      setConnected(false)
      if (esRef.current) esRef.current.close()
      if (cancelRef.current || paused) return
      const delay = Math.min(maxMs, minMs * Math.pow(2, retryRef.current++)) * (0.85 + Math.random() * 0.3)
      window.setTimeout(() => { if (!cancelRef.current && !paused) open() }, delay)
    }
  }, [url, debounceMs, minMs, maxMs, paused, close, parse])

  React.useEffect(() => {
    cancelRef.current = false
    if (!paused) open()
    return () => {
      cancelRef.current = true
      close()
      if (debounceTimer.current) window.clearTimeout(debounceTimer.current)
    }
  }, [open, paused, close])

  return { data, connected, error, reopen: open, close }
}

export type DreamPhase = 'seed'|'awakening'|'exploration'|'creation'|'resonance'|'integration'|'crystallization'
export interface DreamEvent { type: string; phase?: DreamPhase; awareness?: number; coherence?: number; [key: string]: any }
