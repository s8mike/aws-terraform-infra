// Delays tab: where time is being lost, by reason, for an optional date range.
import { useCallback, useState } from 'react'
import { fetchDelayBreakdown } from '../../api/manager'
import type { Lookups } from '../../api/types'
import { useLoader } from '../../hooks/useLoader'
import { endOfLocalDayUtc, startOfLocalDayUtc } from '../../utils/dates'
import { formatMinutes, labelFor } from '../../utils/format'
import DateRangeFilter from '../DateRangeFilter'
import SimpleTable from '../SimpleTable'

export default function DelaysTab({ lookups }: { lookups: Lookups }) {
  const [from, setFrom] = useState('')
  const [to, setTo] = useState('')

  // Reload whenever a date changes.
  const load = useCallback(
    () => fetchDelayBreakdown({ date_from: startOfLocalDayUtc(from), date_to: endOfLocalDayUtc(to) }),
    [from, to],
  )
  const { data, error } = useLoader(load)

  return (
    <section className="panel">
      <h2>Delay breakdown</h2>
      <DateRangeFilter from={from} to={to} onFromChange={setFrom} onToChange={setTo} />
      {error && (
        <p className="error-message" role="alert">
          {error}
        </p>
      )}
      {data && (
        <SimpleTable
          rows={data}
          rowKey={(row) => `${row.delay_type}|${row.custom_delay_type ?? ''}`}
          columns={[
            {
              header: 'Reason',
              render: (row) =>
                `${labelFor(lookups.delay_type, row.delay_type)}${row.custom_delay_type ? ` (${row.custom_delay_type})` : ''}`,
            },
            { header: 'Count', render: (row) => row.delay_count },
            { header: 'Total delay', render: (row) => formatMinutes(row.total_delay_minutes) },
            { header: 'Operator-controllable', render: (row) => row.operator_controllable_count },
          ]}
        />
      )}
    </section>
  )
}