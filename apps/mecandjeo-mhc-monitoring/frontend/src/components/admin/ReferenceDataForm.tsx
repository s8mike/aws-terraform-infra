// Form for adding a reference value or editing one; the code is locked after creation because past records use it.
// Clicking, tabbing into or typing in the locked code field shows a red explanation.
import { useState, type FormEvent } from 'react'
import { createReferenceData, updateReferenceData, type ReferenceDataPatch } from '../../api/admin'
import type { ReferenceData } from '../../api/types'
import { errorMessage } from '../../utils/errors'

interface ReferenceDataFormProps {
  category: string
  item: ReferenceData | null // null means "add a new value"
  onSaved: () => void
  onCancel: () => void
}

export default function ReferenceDataForm({ category, item, onSaved, onCancel }: ReferenceDataFormProps) {
  const [code, setCode] = useState(item?.code ?? '')
  const [label, setLabel] = useState(item?.label ?? '')
  const [shortKey, setShortKey] = useState(item?.short_key ?? '')
  const [description, setDescription] = useState(item?.description ?? '')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)
  // True while the user is interacting with the locked code field.
  const [showCodeLock, setShowCodeLock] = useState(false)

  // Validate, then create or update; the parent reloads the list through onSaved.
  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)

    const nextLabel = label.trim()
    const nextShortKey = shortKey.trim() || null
    const nextDescription = description.trim() || null

    // New codes are stored in lowercase with underscores, matching the existing values.
    const normalizedCode = code.trim().toLowerCase().replace(/\s+/g, '_')
    if (item === null && !/^[a-z0-9_]+$/.test(normalizedCode)) {
      setError('Code may only contain letters, numbers and underscores.')
      return
    }

    // When editing, send only what changed; an emptied optional field is sent as null to clear it.
    const patch: ReferenceDataPatch = {}
    if (item !== null) {
      if (nextLabel !== item.label) patch.label = nextLabel
      if (nextShortKey !== item.short_key) patch.short_key = nextShortKey
      if (nextDescription !== item.description) patch.description = nextDescription
      if (Object.keys(patch).length === 0) {
        setError('Nothing has changed.')
        return
      }
    }

    setSubmitting(true)
    try {
      if (item === null) {
        await createReferenceData({
          category,
          code: normalizedCode,
          label: nextLabel,
          short_key: nextShortKey ?? undefined,
          description: nextDescription ?? undefined,
          is_active: true,
        })
      } else {
        await updateReferenceData(item.id, patch)
      }
      onSaved()
    } catch (caught) {
      setError(errorMessage(caught))
    } finally {
      setSubmitting(false)
    }
  }

  // Props that make the locked field react to any attempt to use it (editing only).
  const lockedHandlers =
    item === null
      ? {}
      : {
          onFocus: () => setShowCodeLock(true),
          onClick: () => setShowCodeLock(true),
          onKeyDown: () => setShowCodeLock(true),
          onBlur: () => setShowCodeLock(false),
        }

  return (
    <form className="edit-panel" onSubmit={handleSubmit}>
      <h3>{item ? `Edit ${item.label}` : 'Add value'}</h3>
      {error && (
        <p className="error-message" role="alert">
          {error}
        </p>
      )}

      <div className="form-grid">
        <div className="form-field">
          <label htmlFor="ref-code">Code{item ? ' (locked)' : ''}</label>
          <input
            id="ref-code"
            type="text"
            required
            maxLength={100}
            readOnly={item !== null}
            value={code}
            onChange={(event) => setCode(event.target.value)}
            {...lockedHandlers}
          />
          {item !== null && showCodeLock && (
            <p className="blocked-notice" role="alert">
              The code cannot be changed because past records use it.
            </p>
          )}
        </div>
        <div className="form-field">
          <label htmlFor="ref-label">Label shown to operators</label>
          <input id="ref-label" type="text" required maxLength={255} value={label} onChange={(event) => setLabel(event.target.value)} />
        </div>
        <div className="form-field">
          <label htmlFor="ref-short">Short key (optional)</label>
          <input id="ref-short" type="text" maxLength={30} value={shortKey} onChange={(event) => setShortKey(event.target.value)} />
        </div>
        <div className="form-field">
          <label htmlFor="ref-description">Description (optional)</label>
          <input id="ref-description" type="text" value={description} onChange={(event) => setDescription(event.target.value)} />
        </div>
      </div>

      {item === null && <p className="hint">Use a short code such as quay_side. It cannot be changed later.</p>}

      <div className="form-actions">
        <button type="submit" className="primary-button retry-button" disabled={submitting}>
          {submitting ? 'Saving…' : item ? 'Save changes' : 'Add value'}
        </button>
        <button type="button" className="secondary-button" onClick={onCancel}>
          Cancel
        </button>
      </div>
    </form>
  )
}