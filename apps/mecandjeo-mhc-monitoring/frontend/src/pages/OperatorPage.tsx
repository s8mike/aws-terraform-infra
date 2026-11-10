// Operator home: "this shift" and "all time" numbers, then the start-shift form or the full working view.
import DelayPanel from '../components/operator/DelayPanel'
import ShiftPanel from '../components/operator/ShiftPanel'
import StartShiftForm from '../components/operator/StartShiftForm'
import SummaryCards from '../components/operator/SummaryCards'
import TaskPanel from '../components/operator/TaskPanel'
import WorkingConditionForm from '../components/operator/WorkingConditionForm'
import { useOperatorData } from '../hooks/useOperatorData'
import { formatMinutes } from '../utils/format'

export default function OperatorPage() {
  const { lookups, active, summary, shiftSummary, error, loading, reload } = useOperatorData()

  if (loading) return <p className="status-message">Loading…</p>

  // Something failed to load: show the reason and a retry button instead of a half-empty page.
  if (error || !lookups || !active || !summary) {
    return (
      <section>
        <p className="error-message" role="alert">
          {error ?? 'Could not load data.'}
        </p>
        <button type="button" className="primary-button retry-button" onClick={reload}>
          Retry
        </button>
      </section>
    )
  }

  // Lifetime figures across every shift the operator has worked.
  const allTimeItems = [
    { label: 'Shifts', value: String(summary.total_shifts) },
    { label: 'Completed tasks', value: String(summary.completed_tasks) },
    { label: 'Containers moved', value: String(summary.total_container_count) },
    { label: 'Delay time', value: formatMinutes(summary.total_delay_minutes) },
  ]

  return (
    <section>
      <h1>Operator</h1>

      {/* Figures for the open shift only; they start at zero for every new shift. */}
      {shiftSummary && (
        <SummaryCards
          title={`This shift - ${shiftSummary.mhc_number}`}
          items={[
            { label: 'Completed tasks', value: String(shiftSummary.completed_tasks) },
            { label: 'Containers moved', value: String(shiftSummary.total_container_count) },
            { label: 'Delay time', value: formatMinutes(shiftSummary.total_delay_minutes) },
          ]}
        />
      )}
      <SummaryCards title="All time" items={allTimeItems} />

      {active.shift === null ? (
        <StartShiftForm cranes={lookups.cranes} shiftCodes={lookups.shift_code} onStarted={reload} />
      ) : (
        <>
          <ShiftPanel shift={active.shift} hasActiveTask={active.task !== null} onChanged={reload} />
          <TaskPanel
            shiftId={active.shift.id}
            task={active.task}
            workTypes={lookups.nature_of_work}
            areas={lookups.working_area}
            hasActiveDelay={active.delay !== null}
            onChanged={reload}
          />

          {/* Delays are recorded against a running task; without one, show a hint instead of hiding the panel. */}
          {active.task !== null ? (
            <DelayPanel task={active.task} delay={active.delay} delayTypes={lookups.delay_type} onChanged={reload} />
          ) : (
            <section className="panel panel-muted">
              <h2>Log a delay</h2>
              <p className="hint">
                Delays are recorded against a running task. Start a task above and the delay form appears here.
              </p>
            </section>
          )}

          <WorkingConditionForm shiftId={active.shift.id} />
        </>
      )}
    </section>
  )
}