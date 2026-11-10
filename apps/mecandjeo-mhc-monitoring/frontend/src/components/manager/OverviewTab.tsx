// Overview tab: headline numbers, who is working now, and open shifts; refreshes every 15 seconds.
import { fetchActiveShifts, fetchDashboard, fetchLiveStatus } from '../../api/manager'
import type { Lookups } from '../../api/types'
import { useLoader } from '../../hooks/useLoader'
import { formatDateTime, formatMinutes, labelFor } from '../../utils/format'
import SimpleTable from '../SimpleTable'
import SummaryCards from '../operator/SummaryCards'

const POLL_MS = 15000

export default function OverviewTab({ lookups }: { lookups: Lookups }) {
  const dashboard = useLoader(fetchDashboard, POLL_MS)
  const live = useLoader(fetchLiveStatus, POLL_MS)
  const shifts = useLoader(fetchActiveShifts, POLL_MS)

  const error = dashboard.error ?? live.error ?? shifts.error
  if (error) {
    return (
      <p className="error-message" role="alert">
        {error}
      </p>
    )
  }
  if (!dashboard.data || !live.data || !shifts.data) return <p className="status-message">Loading…</p>

  const totals = dashboard.data

  return (
    <>
      <SummaryCards
        title="Right now"
        items={[
          { label: 'Active shifts', value: String(totals.active_shifts) },
          { label: 'Active tasks', value: String(totals.active_tasks) },
          { label: 'Active delays', value: String(totals.active_delays) },
        ]}
      />
      <SummaryCards
        title="Totals"
        items={[
          { label: 'Operators', value: String(totals.total_operators) },
          { label: 'Cranes', value: String(totals.total_cranes) },
          { label: 'Completed tasks', value: String(totals.completed_tasks) },
          { label: 'Containers moved', value: String(totals.total_container_count) },
          { label: 'Delay time', value: formatMinutes(totals.total_delay_minutes) },
        ]}
      />

      <section className="panel">
        <h2>Operators on shift</h2>
        <SimpleTable
          rows={live.data}
          rowKey={(row) => row.shift_id}
          emptyMessage="Nobody is on shift right now."
          columns={[
            { header: 'Operator', render: (row) => row.operator_name },
            { header: 'MHC', render: (row) => row.mhc_number },
            { header: 'Shift', render: (row) => row.shift_code ?? '-' },
            { header: 'Status', render: (row) => <span className="badge">{row.status}</span> },
            {
              header: 'Current task',
              render: (row) =>
                row.active_task_nature_of_work ? labelFor(lookups.nature_of_work, row.active_task_nature_of_work) : '-',
            },
            {
              header: 'Current delay',
              render: (row) => (row.active_delay_type ? labelFor(lookups.delay_type, row.active_delay_type) : '-'),
            },
            { header: 'On shift since', render: (row) => formatDateTime(row.shift_started_at) },
          ]}
        />
      </section>

      <section className="panel">
        <h2>Open shifts</h2>
        <SimpleTable
          rows={shifts.data}
          rowKey={(row) => row.shift_id}
          emptyMessage="No open shifts."
          columns={[
            { header: 'Operator', render: (row) => row.operator_name },
            { header: 'MHC', render: (row) => row.mhc_number },
            { header: 'Shift', render: (row) => row.shift_code ?? '-' },
            { header: 'Started', render: (row) => formatDateTime(row.started_at) },
            { header: 'Active tasks', render: (row) => row.active_task_count },
            { header: 'Completed tasks', render: (row) => row.completed_task_count },
            { header: 'Active delays', render: (row) => row.active_delay_count },
            { header: 'Containers', render: (row) => row.total_container_count },
          ]}
        />
      </section>
    </>
  )
}