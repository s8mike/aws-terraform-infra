// Reports tab: a historical performance report with filters, delay context, and a CSV download.
import { useCallback, useMemo, useState } from 'react'
import { fetchPerformanceReport, reportCsvPath } from '../../api/manager'
import type { ReportFilters } from '../../api/manager'
import { downloadCsv } from '../../api/client'
import type { Lookups } from '../../api/types'
import { useLoader } from '../../hooks/useLoader'
import { endOfLocalDayUtc, startOfLocalDayUtc } from '../../utils/dates'
import { errorMessage } from '../../utils/errors'
import { formatDateTime, formatMinutes, labelFor } from '../../utils/format'
import DateRangeFilter from '../DateRangeFilter'
import LookupSelect from '../LookupSelect'
import SimpleTable from '../SimpleTable'
import SummaryCards from '../operator/SummaryCards'

export default function ReportsTab({ lookups }: { lookups: Lookups }) {
  const [from, setFrom] = useState('')
  const [to, setTo] = useState('')
  const [craneId, setCraneId] = useState('')
  const [natureOfWork, setNatureOfWork] = useState('')
  const [downloadError, setDownloadError] = useState<string | null>(null)

  // The filters in the shape the API expects; rebuilt only when an input changes.
  const filters = useMemo<ReportFilters>(
    () => ({
      date_from: startOfLocalDayUtc(from),
      date_to: endOfLocalDayUtc(to),
      crane_id: craneId ? Number(craneId) : undefined,
      nature_of_work: natureOfWork || undefined,
    }),
    [from, to, craneId, natureOfWork],
  )

  // Reload the report whenever a filter changes.
  const load = useCallback(() => fetchPerformanceReport(filters), [filters])
  const { data, error } = useLoader(load)

  // Download the same report as a CSV file (also recorded in the export history).
  async function handleDownload() {
    setDownloadError(null)
    try {
      await downloadCsv(reportCsvPath(filters), 'historical-performance.csv')
    } catch (caught) {
      setDownloadError(errorMessage(caught))
    }
  }

  const craneOptions = lookups.cranes.map((crane) => ({ code: String(crane.id), label: crane.mhc_number }))

  return (
    <section className="panel">
      <h2>Performance report</h2>
      <DateRangeFilter from={from} to={to} onFromChange={setFrom} onToChange={setTo}>
        <LookupSelect id="report-crane" label="MHC" options={craneOptions} value={craneId} onChange={setCraneId} placeholder="All MHCs" />
        <LookupSelect
          id="report-work"
          label="Nature of work"
          options={lookups.nature_of_work}
          value={natureOfWork}
          onChange={setNatureOfWork}
          placeholder="All types"
        />
      </DateRangeFilter>

      {(error || downloadError) && (
        <p className="error-message" role="alert">
          {error ?? downloadError}
        </p>
      )}

      {data && (
        <>
          <SummaryCards
            title="Summary"
            items={[
              { label: 'Completed tasks', value: String(data.summary.completed_tasks) },
              { label: 'Containers moved', value: String(data.summary.total_container_count) },
              { label: 'Task time', value: formatMinutes(data.summary.total_task_minutes) },
              { label: 'Delay time', value: formatMinutes(data.summary.total_delay_minutes) },
              { label: 'Effective time', value: formatMinutes(data.summary.effective_work_minutes) },
              { label: 'Moves per hour', value: data.summary.moves_per_hour === null ? '-' : String(data.summary.moves_per_hour) },
            ]}
          />

          <button type="button" className="primary-button retry-button" onClick={() => void handleDownload()}>
            Download CSV
          </button>

          <h3>Tasks</h3>
          <SimpleTable
            rows={data.tasks}
            rowKey={(row) => row.task_log_id}
            columns={[
              { header: 'Started', render: (row) => formatDateTime(row.started_at) },
              { header: 'Operator', render: (row) => row.operator_name },
              { header: 'MHC', render: (row) => row.mhc_number },
              { header: 'Work', render: (row) => labelFor(lookups.nature_of_work, row.nature_of_work) },
              { header: 'Area', render: (row) => labelFor(lookups.working_area, row.working_area) },
              { header: 'Vessel', render: (row) => row.vessel_name ?? '-' },
              { header: 'Task time', render: (row) => formatMinutes(row.task_minutes) },
              { header: 'Delay', render: (row) => formatMinutes(row.delay_minutes) },
              { header: 'Effective', render: (row) => formatMinutes(row.effective_work_minutes) },
              { header: 'Containers', render: (row) => row.container_count },
              { header: 'Moves per hour', render: (row) => row.moves_per_hour ?? '-' },
              { header: 'Delay reasons', render: (row) => row.delay_reasons.join(', ') || '-' },
            ]}
          />

          <h3>Delay breakdown</h3>
          <SimpleTable
            rows={data.delay_breakdown}
            rowKey={(row) => `${row.delay_type}|${row.custom_delay_type ?? ''}`}
            emptyMessage="No delays in this selection."
            columns={[
              {
                header: 'Reason',
                render: (row) =>
                  `${labelFor(lookups.delay_type, row.delay_type)}${row.custom_delay_type ? ` (${row.custom_delay_type})` : ''}`,
              },
              { header: 'Count', render: (row) => row.delay_count },
              { header: 'Total delay', render: (row) => formatMinutes(row.total_delay_minutes) },
            ]}
          />
        </>
      )}
    </section>
  )
}