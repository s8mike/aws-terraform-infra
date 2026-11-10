// Reusable labelled dropdown: lists options by their label and reports the chosen code.
import type { LookupValue } from '../api/types'

interface LookupSelectProps {
  id: string
  label: string
  options: Pick<LookupValue, 'code' | 'label'>[]
  value: string
  onChange: (value: string) => void
  required?: boolean
  placeholder?: string
}

export default function LookupSelect({
  id,
  label,
  options,
  value,
  onChange,
  required = false,
  placeholder = 'Select…',
}: LookupSelectProps) {
  return (
    <div className="form-field">
      <label htmlFor={id}>{label}</label>
      <select id={id} required={required} value={value} onChange={(event) => onChange(event.target.value)}>
        <option value="">{placeholder}</option>
        {options.map((option) => (
          <option key={option.code} value={option.code}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  )
}