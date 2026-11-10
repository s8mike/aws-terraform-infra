// Form an operator uses to begin work: pick an MHC, pick shift A, B or C, and optionally add a note.
import { useState, type FormEvent } from 'react'
import { ApiError, nowUtcIso } from '../../api/client'
import { startShift } from '../../api/operator'
import type { LookupCrane, LookupValue } from '../../api/types'

interface StartShiftFormProps {
  cranes: LookupCrane[]
  shiftCodes: LookupValue[]
  onStarted: () => void
}

export default function StartShiftForm({ cranes, shiftCodes, onStarted }: StartShiftFormProps) {
  const [mhcNumber, setMhcNumber] = useState('')
  const [shiftCode, setShiftCode] = useState('')
  const [notes, setNotes] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  // Send the shift to the API with the current UTC time as the start; the parent reloads on success.
  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)
    setSubmitting(true)
    try {
      await startShift({
        mhc_number: mhcNumber,
        shift_code: shiftCode,
        started_at: nowUtcIso(),
        notes: notes.trim() || undefined,
      })
      onStarted()
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : 'Could not reach the server.')
    } finally {
      setSubmitting(false)
    }
  }

  // Nothing to choose from: tell the operator who can fix it.
  if (cranes.length === 0) {
    return (
      <section className="panel">
        <h2>Start shift</h2>
        <p className="hint">No active MHC is available. Ask an admin to add one.</p>
      </section>
    )
  }

  return (
    <section className="panel">
      <h2>Start shift</h2>
      <form className="form-stack" onSubmit={handleSubmit}>
        {error && (
          <p className="error-message" role="alert">
            {error}
          </p>
        )}

        <div className="form-field">
          <label htmlFor="mhc">MHC</label>
          <select id="mhc" required value={mhcNumber} onChange={(event) => setMhcNumber(event.target.value)}>
            <option value="">Select an MHC</option>
            {cranes.map((crane) => (
              <option key={crane.id} value={crane.mhc_number}>
                {crane.mhc_number}
              </option>
            ))}
          </select>
        </div>

        <div className="form-field">
          <label htmlFor="shift-code">Shift</label>
          <select id="shift-code" required value={shiftCode} onChange={(event) => setShiftCode(event.target.value)}>
            <option value="">Select a shift</option>
            {shiftCodes.map((shift) => (
              <option key={shift.code} value={shift.code}>
                {shift.label}
              </option>
            ))}
          </select>
        </div>

        <div className="form-field">
          <label htmlFor="shift-notes">Notes (optional)</label>
          <input id="shift-notes" type="text" value={notes} onChange={(event) => setNotes(event.target.value)} />
        </div>

        <button type="submit" className="primary-button" disabled={submitting}>
          {submitting ? 'Starting…' : 'Start shift'}
        </button>
      </form>
    </section>
  )
}