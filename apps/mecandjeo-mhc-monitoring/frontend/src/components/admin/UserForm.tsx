// Form for creating a user or editing one; when editing, only the fields that changed are sent.
import { useState, type FormEvent } from 'react'
import { createUser, updateUser, type UserPatch } from '../../api/admin'
import type { Role, User } from '../../api/types'
import { errorMessage } from '../../utils/errors'
import { passwordProblem } from '../../utils/validation'
import PasswordInput from '../PasswordInput'
import PasswordRules from './PasswordRules'

const ROLE_OPTIONS: { code: Role; label: string }[] = [
  { code: 'operator', label: 'Operator' },
  { code: 'manager', label: 'Manager' },
  { code: 'admin', label: 'Admin' },
]

interface UserFormProps {
  user: User | null // null means "create a new user"
  isSelf: boolean // true when the admin is editing their own account
  onSaved: () => void
  onCancel: () => void
}

export default function UserForm({ user, isSelf, onSaved, onCancel }: UserFormProps) {
  const [fullName, setFullName] = useState(user?.full_name ?? '')
  const [email, setEmail] = useState(user?.email ?? '')
  const [role, setRole] = useState<Role>(user?.role ?? 'operator')
  const [isActive, setIsActive] = useState(user?.is_active ?? true)
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  // Validate, then create or update; the parent reloads the list through onSaved.
  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)

    const trimmedName = fullName.trim()
    const trimmedEmail = email.trim()

    // A password is required for new users and optional (a reset) when editing.
    if (user === null || password !== '') {
      const problem = passwordProblem(password)
      if (problem) {
        setError(problem)
        return
      }
    }

    // When editing, send only what changed.
    const patch: UserPatch = {}
    if (user !== null) {
      if (trimmedName !== user.full_name) patch.full_name = trimmedName
      if (trimmedEmail.toLowerCase() !== user.email.toLowerCase()) patch.email = trimmedEmail
      if (role !== user.role) patch.role = role
      if (isActive !== user.is_active) patch.is_active = isActive
      if (password !== '') patch.password = password
      if (Object.keys(patch).length === 0) {
        setError('Nothing has changed.')
        return
      }
    }

    setSubmitting(true)
    try {
      if (user === null) {
        await createUser({ email: trimmedEmail, full_name: trimmedName, password, role, is_active: isActive })
      } else {
        await updateUser(user.id, patch)
      }
      onSaved()
    } catch (caught) {
      setError(errorMessage(caught))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form className="edit-panel" onSubmit={handleSubmit}>
      <h3>{user ? `Edit ${user.full_name}` : 'Add user'}</h3>
      {error && (
        <p className="error-message" role="alert">
          {error}
        </p>
      )}

      <div className="form-grid">
        <div className="form-field">
          <label htmlFor="user-name">Full name</label>
          <input id="user-name" type="text" required maxLength={255} value={fullName} onChange={(event) => setFullName(event.target.value)} />
        </div>
        <div className="form-field">
          <label htmlFor="user-email">Email</label>
          <input id="user-email" type="email" required value={email} onChange={(event) => setEmail(event.target.value)} />
        </div>
        <div className="form-field">
          <label htmlFor="user-role">Role</label>
          <select id="user-role" value={role} disabled={isSelf} onChange={(event) => setRole(event.target.value as Role)}>
            {ROLE_OPTIONS.map((option) => (
              <option key={option.code} value={option.code}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
        <PasswordInput
          id="user-password"
          label={user ? 'New password (leave blank to keep)' : 'Password'}
          value={password}
          onChange={setPassword}
          autoComplete="new-password"
          required={user === null}
        />
      </div>

      <div className="checkbox-field">
        <input id="user-active" type="checkbox" checked={isActive} disabled={isSelf} onChange={(event) => setIsActive(event.target.checked)} />
        <label htmlFor="user-active">Account is active</label>
      </div>

      {isSelf && <p className="hint">You cannot change your own role or deactivate your own account.</p>}
      <PasswordRules password={password} required={user === null} />

      <div className="form-actions">
        <button type="submit" className="primary-button retry-button" disabled={submitting}>
          {submitting ? 'Saving…' : user ? 'Save changes' : 'Create user'}
        </button>
        <button type="button" className="secondary-button" onClick={onCancel}>
          Cancel
        </button>
      </div>
    </form>
  )
}