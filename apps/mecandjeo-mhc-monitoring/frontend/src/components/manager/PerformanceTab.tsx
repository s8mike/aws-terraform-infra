// Performance tab: completed work grouped by operator, crane, nature of work or date, with delay context.
import { useCallback, useState } from 'react'
import { fetchPerformanceTrends } from '../../api/manager'
import type { Lookups } from '../../api/types'
import { useLoader } from '../../hooks/useLoader'
import { endOfLocalDayUtc, startOfLocalDayUtc } from '../../utils/dates'
import { formatMinutes, labelFor } from '../../utils/format'
import DateRangeFilter from '../DateRangeFilter'
import SimpleTable from '../SimpleTable'

// The four groupings the API accepts.
const GROUP_OPTIONS = [
  { code: 'operator', label: 'By operator' },
  { code: 'crane', label: 'By crane (MHC)' },
  { code: 'nature_of_work', label: 'By nature of work' },
  { code: 'date', label: 'By date (UTC)' },
]

export default function PerformanceTab({ lookups }: { lookups: Lookups }) {
  const [groupBy, setGroupBy] = useState('operator')
  const [from, setFrom] = useState('')
  const [to, setTo] = useState('')

  // Reload whenever the grouping or a date changes.
  const load = useCallback(
    () => fetchPerformanceTrends(groupBy, { date_from: startOfLocalDayUtc(from), date_to: endOfLocalDayUtc(to) }),
    [groupBy, from, to],
  )
  const { data, error } = useLoader(load)

  return (
    <section className="panel">
      <h2>Performance</h2>
      <DateRangeFilter from={from} to={to} onFromChange={setFrom} onToChange={setTo}>
        <div className="form-field">
          <label htmlFor="group-by">Group</label>
          <select id="group-by" value={groupBy} onChange={(event) => setGroupBy(event.target.value)}>
            {GROUP_OPTIONS.map((option) => (
              <option key={option.code} value={option.code}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      </DateRangeFilter>
      {error && (
        <p className="error-message" role="alert">
          {error}
        </p>
      )}
      {data && (
        <SimpleTable
          rows={data}
          rowKey={(row) => row.group_key}
          columns={[
            {
              header: 'Group',
              // The API returns the raw code for nature of work, so show its friendly label.
              render: (row) => (groupBy === 'nature_of_work' ? labelFor(lookups.nature_of_work, row.group_key) : row.label),
            },
            { header: 'Completed tasks', render: (row) => row.completed_tasks },
            { header: 'Task time', render: (row) => formatMinutes(row.total_task_minutes) },
            { header: 'Delay time', render: (row) => formatMinutes(row.total_delay_minutes) },
            { header: 'Effective time', render: (row) => formatMinutes(row.effective_work_minutes) },
            { header: 'Containers', render: (row) => row.total_container_count },
            { header: 'Moves per hour', render: (row) => row.moves_per_hour ?? '-' },
          ]}
        />
      )}
    </section>
  )
}