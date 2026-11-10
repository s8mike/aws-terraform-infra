// Form for adding a crane (MHC) or editing one; when editing, only changed fields are sent and blanks clear optional fields.
import { useState, type FormEvent } from 'react'
import { createCrane, updateCrane, type CranePatch } from '../../api/admin'
import type { Crane } from '../../api/types'
import { errorMessage } from '../../utils/errors'

interface CraneFormProps {
  crane: Crane | null // null means "add a new crane"
  onSaved: () => void
  onCancel: () => void
}

export default function CraneForm({ crane, onSaved, onCancel }: CraneFormProps) {
  const [mhcNumber, setMhcNumber] = useState(crane?.mhc_number ?? '')
  const [code, setCode] = useState(crane?.code ?? '')
  const [name, setName] = useState(crane?.name ?? '')
  const [manufacturer, setManufacturer] = useState(crane?.manufacturer ?? '')
  const [model, setModel] = useState(crane?.model ?? '')
  const [capacity, setCapacity] = useState(crane?.capacity_tonnes === null || crane === null ? '' : String(crane.capacity_tonnes))
  const [location, setLocation] = useState(crane?.location ?? '')
  const [isActive, setIsActive] = useState(crane?.is_active ?? true)
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  // Validate, then create or update; the parent reloads the list through onSaved.
  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)

    const nextMhc = mhcNumber.trim()
    const nextCode = code.trim()
    const nextName = name.trim()

    let capacityValue: number | null = null
    if (capacity.trim() !== '') {
      capacityValue = Number(capacity)
      if (!Number.isFinite(capacityValue) || capacityValue < 0) {
        setError('Capacity must be a number, 0 or more.')
        return
      }
    }

    // When editing, send only what changed; an emptied optional field is sent as null to clear it.
    const patch: CranePatch = {}
    if (crane !== null) {
      if (nextMhc !== crane.mhc_number) patch.mhc_number = nextMhc
      if (nextCode !== crane.code) patch.code = nextCode
      if (nextName !== crane.name) patch.name = nextName
      const nextManufacturer = manufacturer.trim() || null
      if (nextManufacturer !== crane.manufacturer) patch.manufacturer = nextManufacturer
      const nextModel = model.trim() || null
      if (nextModel !== crane.model) patch.model = nextModel
      if (capacityValue !== crane.capacity_tonnes) patch.capacity_tonnes = capacityValue
      const nextLocation = location.trim() || null
      if (nextLocation !== crane.location) patch.location = nextLocation
      if (isActive !== crane.is_active) patch.is_active = isActive
      if (Object.keys(patch).length === 0) {
        setError('Nothing has changed.')
        return
      }
    }

    setSubmitting(true)
    try {
      if (crane === null) {
        await createCrane({
          mhc_number: nextMhc,
          code: nextCode,
          name: nextName,
          manufacturer: manufacturer.trim() || undefined,
          model: model.trim() || undefined,
          capacity_tonnes: capacityValue ?? undefined,
          location: location.trim() || undefined,
          is_active: isActive,
        })
      } else {
        await updateCrane(crane.id, patch)
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
      <h3>{crane ? `Edit ${crane.mhc_number}` : 'Add crane'}</h3>
      {error && (
        <p className="error-message" role="alert">
          {error}
        </p>
      )}

      <div className="form-grid">
        <div className="form-field">
          <label htmlFor="crane-mhc">MHC number</label>
          <input id="crane-mhc" type="text" required maxLength={100} value={mhcNumber} onChange={(event) => setMhcNumber(event.target.value)} />
        </div>
        <div className="form-field">
          <label htmlFor="crane-code">Code</label>
          <input id="crane-code" type="text" required maxLength={100} value={code} onChange={(event) => setCode(event.target.value)} />
        </div>
        <div className="form-field">
          <label htmlFor="crane-name">Name</label>
          <input id="crane-name" type="text" required maxLength={255} value={name} onChange={(event) => setName(event.target.value)} />
        </div>
        <div className="form-field">
          <label htmlFor="crane-manufacturer">Manufacturer (optional)</label>
          <input id="crane-manufacturer" type="text" value={manufacturer} onChange={(event) => setManufacturer(event.target.value)} />
        </div>
        <div className="form-field">
          <label htmlFor="crane-model">Model (optional)</label>
          <input id="crane-model" type="text" value={model} onChange={(event) => setModel(event.target.value)} />
        </div>
        <div className="form-field">
          <label htmlFor="crane-capacity">Capacity in tonnes (optional)</label>
          <input id="crane-capacity" type="number" min={0} step="any" value={capacity} onChange={(event) => setCapacity(event.target.value)} />
        </div>
        <div className="form-field">
          <label htmlFor="crane-location">Location (optional)</label>
          <input id="crane-location" type="text" value={location} onChange={(event) => setLocation(event.target.value)} />
        </div>
      </div>

      <div className="checkbox-field">
        <input id="crane-active" type="checkbox" checked={isActive} onChange={(event) => setIsActive(event.target.checked)} />
        <label htmlFor="crane-active">Available to operators</label>
      </div>

      <div className="form-actions">
        <button type="submit" className="primary-button retry-button" disabled={submitting}>
          {submitting ? 'Saving…' : crane ? 'Save changes' : 'Add crane'}
        </button>
        <button type="button" className="secondary-button" onClick={onCancel}>
          Cancel
        </button>
      </div>
    </form>
  )
}