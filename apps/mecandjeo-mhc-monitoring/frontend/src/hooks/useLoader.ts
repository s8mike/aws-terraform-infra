// Generic data loader: runs a fetch function, tracks loading and errors, and can re-run on a timer or on demand.
// Pass a stable function (defined outside the component or wrapped in useCallback).
import { useCallback, useEffect, useState } from 'react'
import { ApiError } from '../api/client'

export function useLoader<T>(load: () => Promise<T>, pollMs = 0) {
  const [data, setData] = useState<T | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  // Bumping this number makes the effect below fetch again.
  const [refreshKey, setRefreshKey] = useState(0)

  // Fetch whenever the loader, the poll interval or refreshKey changes; set state only after data arrives.
  useEffect(() => {
    let cancelled = false
    load()
      .then((result) => {
        if (cancelled) return
        setData(result)
        setError(null)
        setLoading(false)
      })
      .catch((caught: unknown) => {
        if (cancelled) return
        setError(caught instanceof ApiError ? caught.message : 'Could not load data from the server.')
        setLoading(false)
      })
    // Optional auto-refresh for live views.
    const timer = pollMs > 0 ? window.setInterval(() => setRefreshKey((key) => key + 1), pollMs) : undefined
    return () => {
      cancelled = true
      if (timer !== undefined) window.clearInterval(timer)
    }
  }, [load, pollMs, refreshKey])

  // Fetch again right now.
  const reload = useCallback(() => setRefreshKey((key) => key + 1), [])

  return { data, error, loading, reload }
}