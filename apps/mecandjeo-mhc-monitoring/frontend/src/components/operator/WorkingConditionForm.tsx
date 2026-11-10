// Form for recording weather and deck conditions against the open shift; each submission is a new record.
import { useState, type FormEvent } from 'react'
import { recordWorkingCondition } from '../../api/operator'
import {
  CONGESTION_OPTIONS,
  DECK_OPTIONS,
  VISIBILITY_OPTIONS,
  WEATHER_OPTIONS,
  WIND_OPTIONS,
} from '../../constants/workingConditions'
import { errorMessage } from '../../utils/errors'
import LookupSelect from '../LookupSelect'

export default function WorkingConditionForm({ shiftId }: { shiftId: number }) {
  const [weather, setWeather] = useState('')
  const [visibility, setVisibility] = useState('')
  const [wind, setWind] = useState('')
  const [deck, setDeck] = useState('')
  const [congestion, setCongestion] = useState('')
  const [notes, setNotes] = useState('')
  const [error, setError] = useState<string | null>(null)
  // Time of the last successful save, shown as confirmation (there is no endpoint to list past records).
  const [savedAt, setSavedAt] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  // Save the conditions. Only filled-in fields are sent; an entirely empty form is rejected here.
  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)
    setSavedAt(null)

    if (!weather && !visibility && !wind && !deck && !congestion && !notes.trim()) {
      setError('Choose at least one condition or add a note.')
      return
    }

    setSubmitting(true)
    try {
      await recordWorkingCondition({
        shift_id: shiftId,
        weather_condition: weather || undefined,
        visibility: visibility || undefined,
        wind_condition: wind || undefined,
        deck_condition: deck || undefined,
        congestion_level: congestion || undefined,
        notes: notes.trim() || undefined,
      })
      setSavedAt(new Date().toLocaleTimeString())
      setWeather('')
      setVisibility('')
      setWind('')
      setDeck('')
      setCongestion('')
      setNotes('')
    } catch (caught) {
      setError(errorMessage(caught))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <section className="panel">
      <h2>Working conditions</h2>
      <form onSubmit={handleSubmit}>
        {error && (
          <p className="error-message" role="alert">
            {error}
          </p>
        )}
        {savedAt && <p className="success-message">Conditions recorded at {savedAt}.</p>}

        <div className="form-grid">
          <LookupSelect id="cond-weather" label="Weather" options={WEATHER_OPTIONS} value={weather} onChange={setWeather} placeholder="Not recorded" />
          <LookupSelect id="cond-visibility" label="Visibility" options={VISIBILITY_OPTIONS} value={visibility} onChange={setVisibility} placeholder="Not recorded" />
          <LookupSelect id="cond-wind" label="Wind" options={WIND_OPTIONS} value={wind} onChange={setWind} placeholder="Not recorded" />
          <LookupSelect id="cond-deck" label="Deck" options={DECK_OPTIONS} value={deck} onChange={setDeck} placeholder="Not recorded" />
          <LookupSelect id="cond-congestion" label="Congestion" options={CONGESTION_OPTIONS} value={congestion} onChange={setCongestion} placeholder="Not recorded" />
        </div>

        <div className="form-field form-stack">
          <label htmlFor="cond-notes">Notes (optional)</label>
          <input id="cond-notes" type="text" value={notes} onChange={(event) => setNotes(event.target.value)} />
        </div>

        <button type="submit" className="primary-button retry-button" disabled={submitting}>
          {submitting ? 'Saving…' : 'Record conditions'}
        </button>
      </form>
    </section>
  )
}