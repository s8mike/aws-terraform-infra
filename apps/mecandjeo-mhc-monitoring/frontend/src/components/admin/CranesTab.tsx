// Cranes tab: list every MHC, add one, edit one, or retire/reactivate it (history is kept).
import { useState } from 'react'
import { listCranes, updateCrane } from '../../api/admin'
import type { Crane } from '../../api/types'
import { useLoader } from '../../hooks/useLoader'
import { errorMessage } from '../../utils/errors'
import SimpleTable from '../SimpleTable'
import CraneForm from './CraneForm'

export default function CranesTab() {
  const { data, error, reload } = useLoader(listCranes)
  // null = no form open, 'new' = the add form, a Crane = editing that crane.
  const [editing, setEditing] = useState<Crane | 'new' | null>(null)
  const [actionError, setActionError] = useState<string | null>(null)

  // Retire or reactivate a crane after a confirmation; retired cranes disappear from operators' shift form.
  async function toggleActive(target: Crane) {
    const message = target.is_active
      ? `Retire ${target.mhc_number}? Operators will no longer be able to start shifts on it. Past records are kept.`
      : `Make ${target.mhc_number} available to operators again?`
    if (!window.confirm(message)) return
    setActionError(null)
    try {
      await updateCrane(target.id, { is_active: !target.is_active })
      reload()
    } catch (caught) {
      setActionError(errorMessage(caught))
    }
  }

  // Close the form and refresh the list after a save.
  function handleSaved() {
    setEditing(null)
    reload()
  }

  return (
    <section className="panel">
      <div className="toolbar">
        <h2>Cranes (MHC)</h2>
        <button type="button" className="primary-button retry-button" onClick={() => setEditing('new')}>
          Add crane
        </button>
      </div>

      {editing !== null && (
        <CraneForm
          key={editing === 'new' ? 'new' : editing.id}
          crane={editing === 'new' ? null : editing}
          onSaved={handleSaved}
          onCancel={() => setEditing(null)}
        />
      )}

      {(error || actionError) && (
        <p className="error-message" role="alert">
          {error ?? actionError}
        </p>
      )}

      {data && (
        <SimpleTable
          rows={data}
          rowKey={(row) => row.id}
          columns={[
            { header: 'MHC', render: (row) => row.mhc_number },
            { header: 'Code', render: (row) => row.code },
            { header: 'Name', render: (row) => row.name },
            { header: 'Capacity (t)', render: (row) => row.capacity_tonnes ?? '-' },
            { header: 'Location', render: (row) => row.location ?? '-' },
            {
              header: 'Status',
              render: (row) => <span className={row.is_active ? 'badge' : 'badge badge-off'}>{row.is_active ? 'Active' : 'Retired'}</span>,
            },
            {
              header: 'Actions',
              render: (row) => (
                <>
                  <button type="button" className="small-button" onClick={() => setEditing(row)}>
                    Edit
                  </button>
                  <button
                    type="button"
                    className={row.is_active ? 'small-button small-button-danger' : 'small-button'}
                    onClick={() => void toggleActive(row)}
                  >
                    {row.is_active ? 'Retire' : 'Reactivate'}
                  </button>
                </>
              ),
            },
          ]}
        />
      )}
    </section>
  )
}