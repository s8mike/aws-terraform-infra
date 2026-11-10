// Row of filter inputs: a "from" day, a "to" day, and any extra filters passed as children.
import type { ReactNode } from 'react'

interface DateRangeFilterProps {
  from: string
  to: string
  onFromChange: (value: string) => void
  onToChange: (value: string) => void
  children?: ReactNode
}

export default function DateRangeFilter({ from, to, onFromChange, onToChange, children }: DateRangeFilterProps) {
  return (
    <div className="filter-row">
      <div className="form-field">
        <label htmlFor="filter-from">From</label>
        <input id="filter-from" type="date" value={from} onChange={(event) => onFromChange(event.target.value)} />
      </div>
      <div className="form-field">
        <label htmlFor="filter-to">To</label>
        <input id="filter-to" type="date" value={to} onChange={(event) => onToChange(event.target.value)} />
      </div>
      {children}
    </div>
  )
}