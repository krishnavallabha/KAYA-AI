import { useCallback, useEffect, useRef, useState } from 'react'
import { onConnectionChange, isLive } from '../api/client'

/**
 * Generic data hook: runs `fetcher` on mount and (optionally) polls it,
 * giving the dashboard a live feel. Returns { data, loading, error, refresh }.
 */
export function useResource(fetcher, { pollMs = 0, deps = [] } = {}) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [refreshIndex, setRefreshIndex] = useState(0)

  const savedFetcher = useRef(fetcher)
  savedFetcher.current = fetcher

  const refresh = useCallback(() => setRefreshIndex((i) => i + 1), [])

  useEffect(() => {
    let alive = true
    let timer

    async function load(isInitial) {
      if (isInitial) setLoading(true)
      try {
        const result = await savedFetcher.current()
        if (alive) {
          setData(result)
          setError(null)
        }
      } catch (e) {
        if (alive) setError(e)
      } finally {
        if (alive && isInitial) setLoading(false)
      }
    }

    load(true)
    if (pollMs > 0) timer = setInterval(() => load(false), pollMs)

    return () => {
      alive = false
      if (timer) clearInterval(timer)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pollMs, refreshIndex, ...deps])

  return { data, loading, error, refresh }
}

/** Reactive backend connection status: null (unknown) | true (live) | false (demo). */
export function useConnection() {
  const [live, setLive] = useState(isLive())
  useEffect(() => onConnectionChange(setLive), [])
  return live
}
