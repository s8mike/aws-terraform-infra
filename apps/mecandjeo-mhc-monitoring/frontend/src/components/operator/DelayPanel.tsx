// Delay section: while a task is open, start a delay with its reason, or end the delay that is running.
import { useState, type FormEvent } from 'react'
import { nowUtcIso } from '../../api/client'
import { endDelay, startDelay } from '../../api/operator'
import type { DelayLog, LookupValue, TaskLog } from '../../api/types'
import { errorMessage } from '../../utils/errors'
import { formatDateTime, labelFor } from '../../utils/format'
import LookupSelect from '../LookupSelect'

interface DelayPanelProps {
  task: TaskLog
  delay: DelayLog | null
  delayTypes: LookupValue[]
  onChanged: () => void
}

export default function DelayPanel({ task, delay, delayTypes, onChanged }: DelayPanelProps) {
  const [delayType, setDelayType] = useState('')
  const [customLabel, setCustomLabel] = useState('')
  const [controllable, setControllable] = useState(false)
  const [notes, setNotes] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  // Start a delay now (UTC). The free-text label is only sent for the standard "Other Delay" type.
  async function handleStart(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)
    setSubmitting(true)
    try {
      await startDelay({
        task_log_id: task.id,
        delay_type: delayType,
        custom_delay_type: delayType === 'other_delay' ? customLabel.trim() || undefined : undefined,
        started_at: nowUtcIso(),
        is_operator_controllable: controllable,
        notes: notes.trim() || undefined,
      })
      setDelayType('')
      setCustomLabel('')
      setControllable(false)
      setNotes('')
      onChanged()
    } catch (caught) {
      setError(errorMessage(caught))
    } finally {
      setSubmitting(false)
    }
  }

  // End the running delay now (UTC); the API works out the minutes.
  async function handleEnd() {
    if (!delay) return
    setError(null)
    setSubmitting(true)
    try {
      await endDelay(delay.id, { ended_at: nowUtcIso() })
      onChanged()
    } catch (caught) {
      setError(errorMessage(caught))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <section className="panel">
      <h2>{delay ? 'Active delay' : 'Log a delay'}</h2>

      {error && (
        <p className="error-message" role="alert">
          {error}
        </p>
      )}

      {delay ? (
        <>
          <dl className="detail-list">
            <div>
              <dt>Reason</dt>
              <dd>
                {labelFor(delayTypes, delay.delay_type)}
                {delay.custom_delay_type ? ` (${delay.custom_delay_type})` : ''}
              </dd>
            </div>
            <div>
              <dt>Started</dt>
              <dd>{formatDateTime(delay.started_at)}</dd>
            </div>
          </dl>
          <button type="button" className="danger-button" onClick={handleEnd} disabled={submitting}>
            {submitting ? 'Ending…' : 'End delay'}
          </button>
        </>
      ) : (
        <form onSubmit={handleStart}>
          <div className="form-grid">
            <LookupSelect id="delay-type" label="Delay reason" options={delayTypes} value={delayType} onChange={setDelayType} required />
            {delayType === 'other_delay' && (
              <div className="form-field">
                <label htmlFor="delay-custom">Describe the delay (optional)</label>
                <input id="delay-custom" type="text" maxLength={150} value={customLabel} onChange={(event) => setCustomLabel(event.target.value)} />
              </div>
            )}
          </div>

          <div className="checkbox-field">
            <input id="delay-controllable" type="checkbox" checked={controllable} onChange={(event) => setControllable(event.target.checked)} />
            <label htmlFor="delay-controllable">Within the operator's control</label>
          </div>

          <div className="form-field form-stack">
            <label htmlFor="delay-notes">Notes (optional)</label>
            <input id="delay-notes" type="text" value={notes} onChange={(event) => setNotes(event.target.value)} />
          </div>

          <button type="submit" className="primary-button retry-button" disabled={submitting}>
            {submitting ? 'Starting…' : 'Start delay'}
          </button>
        </form>
      )}
    </section>
  )
}