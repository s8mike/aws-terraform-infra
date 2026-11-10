// Admin home: three tabs for managing users, cranes (MHC) and the choices operators pick from.
import { useState } from 'react'
import CranesTab from '../components/admin/CranesTab'
import ReferenceDataTab from '../components/admin/ReferenceDataTab'
import UsersTab from '../components/admin/UsersTab'

type TabId = 'users' | 'cranes' | 'reference'

const TABS: { id: TabId; label: string }[] = [
  { id: 'users', label: 'Users' },
  { id: 'cranes', label: 'Cranes' },
  { id: 'reference', label: 'Reference data' },
]

export default function AdminPage() {
  const [tab, setTab] = useState<TabId>('users')

  return (
    <section>
      <h1>Admin</h1>
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

      {tab === 'users' && <UsersTab />}
      {tab === 'cranes' && <CranesTab />}
      {tab === 'reference' && <ReferenceDataTab />}
    </section>
  )
}