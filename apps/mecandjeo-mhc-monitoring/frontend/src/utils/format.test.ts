// Tests for the display helpers: minutes as text, friendly labels with a fallback, and UTC timestamps shown in local time.
import { describe, expect, it } from 'vitest'
import type { LookupValue } from '../api/types'
import { formatDateTime, formatMinutes, labelFor } from './format'

describe('formatMinutes', () => {
  it.each([
    [0, '0 min'],
    [45, '45 min'],
    [60, '1 h 0 min'],
    [125, '2 h 5 min'],
  ])('shows %i minutes as "%s"', (minutes, text) => {
    expect(formatMinutes(minutes)).toBe(text)
  })
})

describe('labelFor', () => {
  const options: LookupValue[] = [
    { code: 'discharging', label: 'Discharging', short_key: null },
    { code: 'loading', label: 'Loading', short_key: null },
  ]

  it('returns the friendly label for a known code', () => {
    expect(labelFor(options, 'loading')).toBe('Loading')
  })

  it('falls back to the raw code when the value has been retired or is unknown', () => {
    expect(labelFor(options, 'deck_free_bay')).toBe('deck_free_bay')
  })
})

describe('formatDateTime', () => {
  it('treats the server timestamp as UTC and shows it in local time', () => {
    const expected = new Date(Date.UTC(2026, 9, 7, 6, 30, 0)).toLocaleString()
    expect(formatDateTime('2026-10-07T06:30:00')).toBe(expected)
  })
})