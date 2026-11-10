// Shows the operator's open shift and lets them end it; ending is blocked while a task is still open.
import { useState } from 'react'
import { ApiError, nowUtcIso } from '../../api/client'
import { endShift } from '../../api/operator'
import type { Shift } from '../../api/types'
import { formatDateTime } from '../../utils/format'

interface ShiftPanelProps {
  shift: Shift
  hasActiveTask: boolean
  onChanged: () => void
}

export default function ShiftPanel({ shift, hasActiveTask, onChanged }: ShiftPanelProps) {
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  // Ask for confirmation, then close the shift with the current UTC time.
  async function handleEnd() {
    if (!window.confirm('End this shift?')) return
    setError(null)
    setSubmitting(true)
    try {
      await endShift(shift.id, { ended_at: nowUtcIso() })
      onChanged()
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : 'Could not reach the server.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <section className="panel">
      <h2>Active shift</h2>
      <dl className="detail-list">
        <div>
          <dt>MHC</dt>
          <dd>{shift.mhc_number}</dd>
        </div>
        <div>
          <dt>Shift</dt>
          <dd>{shift.shift_code ?? '-'}</dd>
        </div>
        <div>
          <dt>Started</dt>
          <dd>{formatDateTime(shift.started_at)}</dd>
        </div>
      </dl>

      {hasActiveTask && <p className="blocked-notice" role="status">End the active task before ending the shift.</p>}
      {error && (
        <p className="error-message" role="alert">
          {error}
        </p>
      )}

      <button type="button" className="danger-button" onClick={handleEnd} disabled={submitting || hasActiveTask}>
        {submitting ? 'Ending…' : 'End shift'}
      </button>
    </section>
  )
}