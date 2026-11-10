// Reference data tab: manage the nature-of-work, working-area and delay-type choices operators see.
import { useCallback, useState } from 'react'
import { listReferenceData, updateReferenceData } from '../../api/admin'
import type { ReferenceData } from '../../api/types'
import { useLoader } from '../../hooks/useLoader'
import { errorMessage } from '../../utils/errors'
import SimpleTable from '../SimpleTable'
import ReferenceDataForm from './ReferenceDataForm'

// Shift codes are fixed to A, B and C in the backend, so they are not managed here.
const CATEGORIES = [
  { code: 'nature_of_work', label: 'Nature of work' },
  { code: 'working_area', label: 'Working areas' },
  { code: 'delay_type', label: 'Delay types' },
]

export default function ReferenceDataTab() {
  const [category, setCategory] = useState('nature_of_work')
  // null = no form open, 'new' = the add form, an item = editing that value.
  const [editing, setEditing] = useState<ReferenceData | 'new' | null>(null)
  const [actionError, setActionError] = useState<string | null>(null)

  // Reload whenever the category changes.
  const load = useCallback(() => listReferenceData(category), [category])
  const { data, error, reload } = useLoader(load)

  // Switch category and close any open form.
  function changeCategory(value: string) {
    setCategory(value)
    setEditing(null)
    setActionError(null)
  }

  // Retire or reactivate a value after a confirmation; retired values vanish from operator forms but stay in history.
  async function toggleActive(target: ReferenceData) {
    const message = target.is_active
      ? `Retire "${target.label}"? Operators will no longer be able to choose it. Past records are kept.`
      : `Make "${target.label}" available to operators again?`
    if (!window.confirm(message)) return
    setActionError(null)
    try {
      await updateReferenceData(target.id, { is_active: !target.is_active })
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
        <h2>Reference data</h2>
        <button type="button" className="primary-button retry-button" onClick={() => setEditing('new')}>
          Add value
        </button>
      </div>

      <div className="filter-row">
        <div className="form-field">
          <label htmlFor="ref-category">Category</label>
          <select id="ref-category" value={category} onChange={(event) => changeCategory(event.target.value)}>
            {CATEGORIES.map((option) => (
              <option key={option.code} value={option.code}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {editing !== null && (
        <ReferenceDataForm
          key={`${category}-${editing === 'new' ? 'new' : editing.id}`}
          category={category}
          item={editing === 'new' ? null : editing}
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
            { header: 'Code', render: (row) => row.code },
            { header: 'Label', render: (row) => row.label },
            { header: 'Short key', render: (row) => row.short_key ?? '-' },
            { header: 'Description', render: (row) => row.description ?? '-' },
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