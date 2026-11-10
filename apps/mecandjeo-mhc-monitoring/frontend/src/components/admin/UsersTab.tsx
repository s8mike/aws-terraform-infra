// Users tab: list every account, add a user, edit one, or activate/deactivate it.
import { useState } from 'react'
import { listUsers, updateUser } from '../../api/admin'
import type { User } from '../../api/types'
import { useAuth } from '../../auth/useAuth'
import { useLoader } from '../../hooks/useLoader'
import { errorMessage } from '../../utils/errors'
import { formatDateTime } from '../../utils/format'
import SimpleTable from '../SimpleTable'
import UserForm from './UserForm'

export default function UsersTab() {
  const { user: me } = useAuth()
  const { data, error, reload } = useLoader(listUsers)
  // null = no form open, 'new' = the add form, a User = editing that user.
  const [editing, setEditing] = useState<User | 'new' | null>(null)
  const [actionError, setActionError] = useState<string | null>(null)

  // Activate or deactivate an account after a confirmation.
  async function toggleActive(target: User) {
    const verb = target.is_active ? 'Deactivate' : 'Activate'
    if (!window.confirm(`${verb} ${target.full_name}?`)) return
    setActionError(null)
    try {
      await updateUser(target.id, { is_active: !target.is_active })
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
        <h2>Users</h2>
        <button type="button" className="primary-button retry-button" onClick={() => setEditing('new')}>
          Add user
        </button>
      </div>

      {editing !== null && (
        <UserForm
          key={editing === 'new' ? 'new' : editing.id}
          user={editing === 'new' ? null : editing}
          isSelf={editing !== 'new' && editing.id === me?.id}
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
            { header: 'Name', render: (row) => row.full_name },
            { header: 'Email', render: (row) => row.email },
            { header: 'Role', render: (row) => <span className="badge">{row.role}</span> },
            {
              header: 'Status',
              render: (row) => <span className={row.is_active ? 'badge' : 'badge badge-off'}>{row.is_active ? 'Active' : 'Inactive'}</span>,
            },
            { header: 'Created', render: (row) => formatDateTime(row.created_at) },
            {
              header: 'Actions',
              render: (row) => (
                <>
                  <button type="button" className="small-button" onClick={() => setEditing(row)}>
                    Edit
                  </button>
                  {/* The API refuses self-deactivation, so the button is hidden on your own row. */}
                  {row.id !== me?.id && (
                    <button
                      type="button"
                      className={row.is_active ? 'small-button small-button-danger' : 'small-button'}
                      onClick={() => void toggleActive(row)}
                    >
                      {row.is_active ? 'Deactivate' : 'Activate'}
                    </button>
                  )}
                </>
              ),
            },
          ]}
        />
      )}
    </section>
  )
}