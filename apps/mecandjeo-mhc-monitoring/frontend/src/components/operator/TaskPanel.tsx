// Task section: start a task (work type, area, vessel, bay) or end the open one with its container count.
import { useState, type FormEvent } from 'react'
import { nowUtcIso } from '../../api/client'
import { endTask, startTask } from '../../api/operator'
import type { LookupValue, TaskLog } from '../../api/types'
import { errorMessage } from '../../utils/errors'
import { formatDateTime, labelFor } from '../../utils/format'
import LookupSelect from '../LookupSelect'

interface TaskPanelProps {
  shiftId: number
  task: TaskLog | null
  workTypes: LookupValue[]
  areas: LookupValue[]
  hasActiveDelay: boolean
  onChanged: () => void
}

interface StartTaskFormProps {
  shiftId: number
  workTypes: LookupValue[]
  areas: LookupValue[]
  onChanged: () => void
}

// Form shown while no task is open.
function StartTaskForm({ shiftId, workTypes, areas, onChanged }: StartTaskFormProps) {
  const [natureOfWork, setNatureOfWork] = useState('')
  const [workingArea, setWorkingArea] = useState('')
  const [vesselName, setVesselName] = useState('')
  const [bayReference, setBayReference] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  // Start the task now (UTC) and let the parent reload so the open task appears.
  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)
    setSubmitting(true)
    try {
      await startTask({
        shift_id: shiftId,
        nature_of_work: natureOfWork,
        working_area: workingArea,
        vessel_name: vesselName.trim() || undefined,
        bay_reference: bayReference.trim() || undefined,
        started_at: nowUtcIso(),
      })
      onChanged()
    } catch (caught) {
      setError(errorMessage(caught))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      {error && (
        <p className="error-message" role="alert">
          {error}
        </p>
      )}

      <div className="form-grid">
        <LookupSelect id="task-work" label="Nature of work" options={workTypes} value={natureOfWork} onChange={setNatureOfWork} required />
        <LookupSelect id="task-area" label="Working area" options={areas} value={workingArea} onChange={setWorkingArea} required />
        <div className="form-field">
          <label htmlFor="task-vessel">Vessel (optional)</label>
          <input id="task-vessel" type="text" maxLength={255} value={vesselName} onChange={(event) => setVesselName(event.target.value)} />
        </div>
        <div className="form-field">
          <label htmlFor="task-bay">Bay reference (optional)</label>
          <input id="task-bay" type="text" maxLength={100} value={bayReference} onChange={(event) => setBayReference(event.target.value)} />
        </div>
      </div>

      <button type="submit" className="primary-button retry-button" disabled={submitting}>
        {submitting ? 'Starting…' : 'Start task'}
      </button>
    </form>
  )
}

interface EndTaskFormProps {
  task: TaskLog
  workTypes: LookupValue[]
  areas: LookupValue[]
  hasActiveDelay: boolean
  onChanged: () => void
}

// Details and end form shown while a task is open.
function EndTaskForm({ task, workTypes, areas, hasActiveDelay, onChanged }: EndTaskFormProps) {
  // Starts empty so the operator must type the real count; ending with a silent 0 would skew performance figures.
  const [containerCount, setContainerCount] = useState('')
  const [notes, setNotes] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  // Close the task with the final container count; the API refuses while a delay is open.
  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)

    const count = Number(containerCount)
    if (containerCount.trim() === '' || !Number.isInteger(count) || count < 0) {
      setError('Container count must be a whole number, 0 or more.')
      return
    }

    setSubmitting(true)
    try {
      await endTask(task.id, {
        ended_at: nowUtcIso(),
        container_count: count,
        notes: notes.trim() || undefined,
      })
      onChanged()
    } catch (caught) {
      setError(errorMessage(caught))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <>
      <dl className="detail-list">
        <div>
          <dt>Work</dt>
          <dd>{labelFor(workTypes, task.nature_of_work)}</dd>
        </div>
        <div>
          <dt>Area</dt>
          <dd>{labelFor(areas, task.working_area)}</dd>
        </div>
        {task.vessel_name && (
          <div>
            <dt>Vessel</dt>
            <dd>{task.vessel_name}</dd>
          </div>
        )}
        {task.bay_reference && (
          <div>
            <dt>Bay</dt>
            <dd>{task.bay_reference}</dd>
          </div>
        )}
        <div>
          <dt>Started</dt>
          <dd>{formatDateTime(task.started_at)}</dd>
        </div>
      </dl>

      <form onSubmit={handleSubmit}>
        {hasActiveDelay && <p className="blocked-notice" role="status">End the active delay before ending the task.</p>}
        {error && (
          <p className="error-message" role="alert">
            {error}
          </p>
        )}

        <div className="form-grid">
          <div className="form-field">
            <label htmlFor="task-count">Containers moved</label>
            <input id="task-count" type="number" min={0} step={1} required value={containerCount} onChange={(event) => setContainerCount(event.target.value)} />
          </div>
          <div className="form-field">
            <label htmlFor="task-notes">Notes (optional)</label>
            <input id="task-notes" type="text" value={notes} onChange={(event) => setNotes(event.target.value)} />
          </div>
        </div>

        <button type="submit" className="danger-button" disabled={submitting || hasActiveDelay}>
          {submitting ? 'Ending…' : 'End task'}
        </button>
      </form>
    </>
  )
}

export default function TaskPanel({ shiftId, task, workTypes, areas, hasActiveDelay, onChanged }: TaskPanelProps) {
  return (
    <section className="panel">
      <h2>{task ? 'Active task' : 'Start task'}</h2>
      {task ? (
        <EndTaskForm key={task.id} task={task} workTypes={workTypes} areas={areas} hasActiveDelay={hasActiveDelay} onChanged={onChanged} />
      ) : (
        <StartTaskForm shiftId={shiftId} workTypes={workTypes} areas={areas} onChanged={onChanged} />
      )}
    </section>
  )
}