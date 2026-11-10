// Manager home: loads the lookup values once and shows one of four tabs (overview, delays, performance, reports).
import { useState } from 'react'
import { fetchLookups } from '../api/operator'
import DelaysTab from '../components/manager/DelaysTab'
import OverviewTab from '../components/manager/OverviewTab'
import PerformanceTab from '../components/manager/PerformanceTab'
import ReportsTab from '../components/manager/ReportsTab'
import { useLoader } from '../hooks/useLoader'

type TabId = 'overview' | 'delays' | 'performance' | 'reports'

const TABS: { id: TabId; label: string }[] = [
  { id: 'overview', label: 'Overview' },
  { id: 'delays', label: 'Delays' },
  { id: 'performance', label: 'Performance' },
  { id: 'reports', label: 'Reports' },
]

export default function ManagerPage() {
  const [tab, setTab] = useState<TabId>('overview')
  const { data: lookups, error } = useLoader(fetchLookups)

  if (error) {
    return (
      <p className="error-message" role="alert">
        {error}
      </p>
    )
  }
  if (!lookups) return <p className="status-message">Loading…</p>

  return (
    <section>
      <h1>Manager</h1>
      <div className="tab-bar" role="tablist">
        {TABS.map((item) => (
          <button
            key={item.id}
            type="button"
            role="tab"
            aria-selected={tab === item.id}
            className={tab === item.id ? 'tab tab-active' : 'tab'}
            onClick={() => setTab(item.id)}
          >
            {item.label}
          </button>
        ))}
      </div>

      {tab === 'overview' && <OverviewTab lookups={lookups} />}
      {tab === 'delays' && <DelaysTab lookups={lookups} />}
      {tab === 'performance' && <PerformanceTab lookups={lookups} />}
      {tab === 'reports' && <ReportsTab lookups={lookups} />}
    </section>
  )
}