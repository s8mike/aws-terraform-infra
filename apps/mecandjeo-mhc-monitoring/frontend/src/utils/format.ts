// Small helpers that turn server values into text people can read.
import { parseServerDate } from '../api/client'
import type { LookupValue } from '../api/types'

// Show a server timestamp (naive UTC) in the viewer's local date and time.
export function formatDateTime(value: string): string {
  return parseServerDate(value).toLocaleString()
}

// Show a number of minutes as "45 min" or "2 h 5 min".
export function formatMinutes(total: number): string {
  const hours = Math.floor(total / 60)
  const minutes = total % 60
  return hours > 0 ? `${hours} h ${minutes} min` : `${minutes} min`
}

// Find the friendly label for a code (for example "deck_free_bay" shows as "Deck Free Bay").
// Falls back to the raw code if an admin has since retired that value.
export function labelFor(options: LookupValue[], code: string): string {
  return options.find((option) => option.code === code)?.label ?? code
}