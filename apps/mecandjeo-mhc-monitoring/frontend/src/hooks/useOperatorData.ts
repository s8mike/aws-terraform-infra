// Loads everything the operator screen needs (lookups, active state, summaries) and can reload it after any action.
import { useCallback, useEffect, useState } from 'react'
import { ApiError } from '../api/client'
import { fetchActiveState, fetchLookups, fetchOperatorSummary, fetchShiftSummary } from '../api/operator'
import type { Lookups, OperatorActiveState, OperatorSummary, ShiftSummary } from '../api/types'

export function useOperatorData() {
  const [lookups, setLookups] = useState<Lookups | null>(null)
  const [active, setActive] = useState<OperatorActiveState | null>(null)
  const [summary, setSummary] = useState<OperatorSummary | null>(null)
  const [shiftSummary, setShiftSummary] = useState<ShiftSummary | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  // Bumping this number makes the effect below fetch everything again.
  const [refreshKey, setRefreshKey] = useState(0)

  // Fetch the sources on first load and whenever refreshKey changes.
  // State is set only after all the data has arrived.
  useEffect(() => {
    let cancelled = false
    Promise.all([fetchLookups(), fetchActiveState(), fetchOperatorSummary()])
      .then(async ([nextLookups, nextActive, nextSummary]) => {
        // The open shift's totals need its id, so they load after the active state.
        const nextShiftSummary = nextActive.shift ? await fetchShiftSummary(nextActive.shift.id) : null
        return { nextLookups, nextActive, nextSummary, nextShiftSummary }
      })
      .then((data) => {
        if (cancelled) return
        setLookups(data.nextLookups)
        setActive(data.nextActive)
        setSummary(data.nextSummary)
        setShiftSummary(data.nextShiftSummary)
        setError(null)
        setLoading(false)
      })
      .catch((caught: unknown) => {
        if (cancelled) return
        setError(caught instanceof ApiError ? caught.message : 'Could not load data from the server.')
        setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [refreshKey])

  // Call after any shift, task or delay change (or from a Retry button) to refresh the screen.
  const reload = useCallback(() => {
    setRefreshKey((current) => current + 1)
  }, [])

  return { lookups, active, summary, shiftSummary, error, loading, reload }
}