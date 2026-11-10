// Tests for the filter-date helpers: a picked local day becomes a naive UTC timestamp covering that whole local day.
import { describe, expect, it } from 'vitest'
import { parseServerDate } from '../api/client'
import { endOfLocalDayUtc, startOfLocalDayUtc } from './dates'

describe('startOfLocalDayUtc and endOfLocalDayUtc', () => {
  it('return undefined when no day is chosen', () => {
    expect(startOfLocalDayUtc('')).toBeUndefined()
    expect(endOfLocalDayUtc('')).toBeUndefined()
  })

  it('return naive timestamps (no Z, no offset) as the API expects', () => {
    expect(startOfLocalDayUtc('2026-10-08')).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$/)
    expect(endOfLocalDayUtc('2026-10-08')).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$/)
  })

  it('start is local midnight and end is the last second of the same local day', () => {
    const start = startOfLocalDayUtc('2026-10-08') ?? ''
    const end = endOfLocalDayUtc('2026-10-08') ?? ''
    expect(parseServerDate(start).getTime()).toBe(new Date(2026, 9, 8, 0, 0, 0).getTime())
    expect(parseServerDate(end).getTime()).toBe(new Date(2026, 9, 8, 23, 59, 59).getTime())
  })
})